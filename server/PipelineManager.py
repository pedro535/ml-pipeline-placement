from datetime import datetime
from dateutil import tz
from queue import Queue
from typing import List, Dict, Tuple
import subprocess
from kfp import Client
import json

from server import DecisionUnit, NodeManager
from server.settings import KFP_URL, ENABLE_CACHING, METADATA_FILENAME, pipelines_dir


class PipelineManager:

    def __init__(self, decision_unit: DecisionUnit, node_manager: NodeManager):
        self.decision_unit = decision_unit
        self.node_manager = node_manager
        self.kfp_url = KFP_URL
        self.enable_caching = ENABLE_CACHING
        self.dir = pipelines_dir
        self.kfp_client = Client(host=self.kfp_url)
        self.pipelines = {}
        self.submission_queue = Queue()
        self.waiting_list = []
        self.running_pipelines = []


    def add_pipeline(self, pipeline_id: str, components: List[Tuple[str, str]]):
        """
        Add pipeline to the submission queue
        """
        self.submission_queue.put(pipeline_id)
        
        self.pipelines[pipeline_id] = {
            "components": {},
            "total_effort": None,
            "state": "QUEUED",
            "kfp_id": None,
            "scheduled_at": None,
            "finished_at": None,
            "duration": None,
            "last_update": None
        }

        for filename, name in components:
            self.pipelines[pipeline_id]["components"][name] = {
                "file": filename,
                "node": None,
                "effort": None,
                "start_time": None,
                "end_time": None,
                "duration": None,
                "state": None
            }

    
    def build_pipeline(self, pipeline_id: str, mapping: Dict[str, Tuple[str, str]]):
        """
        Build the kfp pipeline
        """
        path = self.dir / pipeline_id / "pipeline.py"
        args = ["python3", path, "-u", self.kfp_url, "-m"]

        mapping_arg = []
        for component in self.pipelines[pipeline_id]["components"]:
            mapping_arg.append(mapping[component])
        mapping_arg_json = json.dumps(mapping_arg)
        args.append(mapping_arg_json)

        if self.enable_caching:
            args.append("-c")

        try:
            subprocess.run(
                args=args,
                capture_output=True,
                cwd=self.dir / pipeline_id
            )
        except Exception as e:
            print("Error while building pipeline:", e)
            self.pipelines[pipeline_id]["state"] = "FAILED"


    def run_pipeline(self, pipeline_id: str):
        """
        Run the built kfp pipeline
        """
        try:
            run = subprocess.run(
                args=["python3", self.dir / pipeline_id / "kfp_pipeline.py"],
                capture_output=True,
                cwd=self.dir / pipeline_id
            )
            output = run.stdout.decode("utf-8")
            kfp_id = output.split("Run ID:")[-1].strip()
            self.pipelines[pipeline_id]["kfp_id"] = kfp_id
            self.pipelines[pipeline_id]["state"] = "RUNNING"
        except Exception as e:
            print("Error while running pipeline:", e)
            self.pipelines[pipeline_id]["state"] = "FAILED"
        

    def process_pipelines(self):
        """
        Process submitted pipelines
        """
        if self.submission_queue.empty():
            return
        
        pipelines_to_place = []
        pipelines_metadata = {}
        while not self.submission_queue.empty():
            pipeline_id = self.submission_queue.get()
            pipelines_metadata[pipeline_id] = self.get_metadata(pipeline_id)
            components = list(self.pipelines[pipeline_id]["components"].keys())
            pipelines_to_place.append((pipeline_id, components))
    
        placements = self.decision_unit.get_placements(pipelines_to_place, pipelines_metadata)

        for placement in placements:
            pipeline_id = placement["pipeline_id"]
            mapping = placement["mapping"]
            efforts = placement["efforts"]

            for c, selected_node in mapping.items():
                node_name, _ = selected_node
                self.pipelines[pipeline_id]["components"][c]["node"] = node_name
                self.pipelines[pipeline_id]["components"][c]["effort"] = efforts[c]
            self.pipelines[pipeline_id]["effort"] = efforts["total"]

            self.build_pipeline(pipeline_id, mapping)
            self.waiting_list.append(pipeline_id)
        
        print(json.dumps(self.decision_unit.assignments, indent=4, default=str))


    def terminate_pipelines(self):
        """
        Remove completed pipelines from running pipelines list.
        """
        for pipeline_id in self.running_pipelines.copy():
            state = self.pipelines[pipeline_id]["state"]
            if state in ["SUCCEEDED", "FAILED"]:
                self.running_pipelines.remove(pipeline_id)


    def update_components(self, pipeline_id: str, task_details: List):
        """
        Update details of components
        """
        pipeline = self.pipelines[pipeline_id]
        epoch_date = datetime.fromtimestamp(0, tz=tz.tzutc())

        for task in task_details:
            task_name = task["display_name"]
            if task_name in pipeline["components"]:
                component = pipeline["components"][task_name]
                component["start_time"] = task["start_time"]
                component["end_time"] = task["end_time"] if task["end_time"] > epoch_date else None
                duration = (task["end_time"] - task["start_time"]).total_seconds()
                component["duration"] = round(duration, 2) if duration >= 0 else None
                component["state"] = task["state"]

                if component["state"] == "SUCCEEDED":
                    node = component["node"]
                    self.decision_unit.rm_assignment(node, pipeline_id, task_name)
                    if not self.decision_unit.is_node_needed(component["node"], pipeline_id):
                        self.node_manager.release_nodes([component["node"]])


    def update_pipeline(self, pipeline_id: str, run_details: Dict):
        """
        Update details of pipelines
        """
        pipeline = self.pipelines[pipeline_id]
        epoch_date = datetime.fromtimestamp(0, tz=tz.tzutc())
        pipeline["state"] = run_details["state"]
        pipeline["scheduled_at"] = run_details["scheduled_at"]
        pipeline["finished_at"] = run_details["finished_at"] if run_details["finished_at"] > epoch_date else None
        duration = (run_details["finished_at"] - run_details["scheduled_at"]).total_seconds()
        pipeline["duration"] = round(duration, 2) if duration >= 0 else None
        pipeline["last_update"] = datetime.now(tz=tz.tzutc())


    def update_pipelines(self):

        # FOR DEBUG
        print("Waiting list: ", self.waiting_list)
        print("Running pipelines: ", self.running_pipelines)

        # Update running pipelines
        for pipeline_id in self.running_pipelines:
            pipeline = self.pipelines[pipeline_id]
            run_details = self.kfp_client.get_run(pipeline["kfp_id"]).to_dict()

            self.update_components(pipeline_id, run_details["run_details"]["task_details"])
            self.update_pipeline(pipeline_id, run_details)
        
        # Terminate completed pipelines
        self.terminate_pipelines()

        # Check for new pipeline to be executed
        for pipeline_id in self.waiting_list.copy():
            pipeline = self.pipelines[pipeline_id]
            nodes = [c["node"] for c in pipeline["components"].values()]

            if self.node_manager.nodes_available(nodes):
                self.node_manager.reserve_nodes(nodes)
                self.run_pipeline(pipeline_id)
                self.running_pipelines.append(pipeline_id)
                self.waiting_list.remove(pipeline_id)

        print(json.dumps(self.decision_unit.assignments, indent=4, default=str))
        print(json.dumps(self.node_manager.availability, indent=4, default=str))
        pipelines_running = [p for p_id, p in self.pipelines.items() if p_id in self.running_pipelines]
        print(json.dumps(pipelines_running, indent=4, default=str))
        print("-" * 50)


    def get_metadata(self, pipeline_id: str) -> Dict:
        """
        Get the metadata content of the pipeline
        """
        with open(self.dir / pipeline_id / METADATA_FILENAME, "r") as f:
            metadata = json.load(f)
        
        return metadata


    def dump_pipelines(self):
        """
        Dump the pipeline details to a file
        """
        pipelines = dict(
            sorted(self.pipelines.items(), key=lambda item: item[1]["total_effort"])
        )
        
        with open(self.dir / "pipelines.json", "w") as f:
            json.dump(pipelines, f, indent=4, default=str)
        print("Pipeline details dumped to pipelines.json")