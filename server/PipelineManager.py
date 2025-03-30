from datetime import datetime
from dateutil import tz
from queue import Queue
from typing import List, Dict
import subprocess
from kfp import Client
import json

from server import DecisionUnit
from server.settings import KFP_URL, ENABLE_CACHING, METADATA_FILENAME, pipelines_dir


class PipelineManager:

    def __init__(self, decision_unit: DecisionUnit):
        self.kfp_url = KFP_URL
        self.enable_caching = ENABLE_CACHING
        self.dir = pipelines_dir
        self.kfp_client = Client(host=self.kfp_url)
        self.decision_unit = decision_unit
        self.pipelines = {}
        self.submission_queue = Queue()
        self.execution_queue = Queue()
        self.running_pipeline = None


    def add_pipeline(self, pipeline_id: str, component_files: List[str]):
        """
        Add pipeline to the queue
        """
        self.submission_queue.put(pipeline_id)
        
        component_names = [c.split(".")[0].lower().replace("_", "-") for c in component_files]
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

        for i, c in enumerate(component_names):
            self.pipelines[pipeline_id]["components"][c] = {
                "file": component_files[i],
                "node": None,
                "effort": None,
                "start_time": None,
                "end_time": None,
                "duration": None,
                "state": None
            }

    
    def build_pipeline(self, pipeline_id: str, mapping: Dict[str, str]):
        """
        Build the kfp pipeline
        """
        path = self.dir / pipeline_id / "pipeline.py"
        args = ["python3", path, "-u", self.kfp_url, "-p"]

        for component in self.pipelines[pipeline_id]["components"]:
            args.append(mapping[component])

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
        while not self.submission_queue.empty():
            pipeline_id = self.submission_queue.get()

            with open(self.dir / pipeline_id / METADATA_FILENAME, "r") as f:
                metadata = json.load(f)
                
            # Rename component names
            components = list(metadata["components_type"].keys())
            for c in components:
                metadata["components_type"][c.lower().replace("_", "-")] = metadata["components_type"][c]
                del metadata["components_type"][c]
            
            pipeline_details = {
                "pipeline": pipeline_id,
                "components": list(
                    self.pipelines[pipeline_id]["components"].keys()
                ),
                "metadata": metadata
            }
            pipelines_to_place.append(pipeline_details)
    
        placements = self.decision_unit.get_placements(pipelines_to_place)

        for placement in placements:
            pipeline_id = placement["pipeline_id"]
            mapping = placement["mapping"]
            efforts = placement["efforts"]

            for c, node in mapping.items():
                self.pipelines[pipeline_id]["components"][c]["node"] = node
                self.pipelines[pipeline_id]["components"][c]["effort"] = efforts[c]
            
            self.pipelines[pipeline_id]["total_effort"] = efforts["total"]  # DEBUG
            
            self.build_pipeline(pipeline_id, mapping)
            self.execution_queue.put(pipeline_id)

    
    def update_component_details(self, pipeline: Dict, task_details: List):
        """
        Update details of components
        """
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


    def update_pipeline_details(self, pipeline: Dict, run_details: Dict):
        """
        Update details of pipelines
        """
        epoch_date = datetime.fromtimestamp(0, tz=tz.tzutc())
        pipeline["state"] = run_details["state"]
        pipeline["scheduled_at"] = run_details["scheduled_at"]
        pipeline["finished_at"] = run_details["finished_at"] if run_details["finished_at"] > epoch_date else None
        duration = (run_details["finished_at"] - run_details["scheduled_at"]).total_seconds()
        pipeline["duration"] = round(duration, 2) if duration >= 0 else None
        pipeline["last_update"] = datetime.now(tz=tz.tzutc())


    def update_running_pipeline(self):
        """
        Update the state of the running pipeline or start the next one
        """
        if self.running_pipeline is not None:
            pipeline = self.pipelines[self.running_pipeline]
            run_details = self.kfp_client.get_run(pipeline["kfp_id"]).to_dict()

            self.update_component_details(pipeline, run_details["run_details"]["task_details"])
            self.update_pipeline_details(pipeline, run_details)
            
            if pipeline["state"] in ["SUCCEEDED", "FAILED"]:
                self.running_pipeline = None

        if self.running_pipeline is None and not self.execution_queue.empty():
            pipeline_id = self.execution_queue.get()
            self.run_pipeline(pipeline_id)
            self.running_pipeline = pipeline_id

        # DEBUG
        # for p in self.pipelines.values():
        #     print(json.dumps(p, indent=4, default=str))


    def dump_pipelines(self):
        """
        Dump the pipeline details to a file
        """
        # sort pipelines by total effort
        pipelines = dict(
            sorted(self.pipelines.items(), key=lambda item: item[1]["total_effort"])
        )
        
        with open(self.dir / "pipelines.json", "w") as f:
            json.dump(pipelines, f, indent=4, default=str)
        print("Pipeline details dumped to pipelines.json")