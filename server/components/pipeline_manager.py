from queue import Queue
from typing import List, Dict, Tuple
import time
import subprocess
import requests
import json
import csv

from server.ml_pipeline import Pipeline, Component
from server.components import DecisionUnit, NodeManager
from server.settings import (
    KFP_URL,
    KFP_API_ENDPOINT,
    ENABLE_CACHING,
    PIPELINE_FILENAME,
    KFP_PREFIX,
    N_PIPELINES_CSV,
    pipelines_dir
)


class PipelineManager:

    def __init__(self, decision_unit: DecisionUnit, node_manager: NodeManager):
        self.decision_unit = decision_unit
        self.node_manager = node_manager
        self.kfp_url = KFP_URL
        self.pipelines: Dict[str, Pipeline] = {}
        self.submission_queue: Queue = Queue()
        self.waiting_list: List[str] = []
        self.running_pipelines: List[str] = []
        self.time_window = 0

        # Csv file to save total running and waiting pipelines
        self.csv_file = open(N_PIPELINES_CSV, "a", newline="")
        self.csv_writer = csv.writer(self.csv_file)
        self.csv_writer.writerow(["timestamp", "type", "running_pipelines", "waiting_pipelines"])


    def add_pipeline(self, pipeline_id: str, name: str, components: List[Tuple[str, str]]) -> None:
        """
        Register a new pipeline with its components.
        """
        self.submission_queue.put(pipeline_id)
        pipeline = Pipeline(pipeline_id, name)
        
        for filename, name in components:
            component = Component(name, filename)
            pipeline.add_component(component)

        self.pipelines[pipeline_id] = pipeline


    def dump_pipelines(self) -> None:
        """
        Dump the pipelines to a JSON file.
        """
        pipelines_as_dict = []
        for pipeline in self.pipelines.values():
            pipelines_as_dict.append(pipeline.dict_repr())

        with open(pipelines_dir / "pipelines.json", "w") as f:
            json.dump(pipelines_as_dict, f, indent=4, default=str)
        self.csv_file.close()


    def process_pipelines(self) -> None:
        """
        Place and then build the pipelines in the submission queue.
        """
        # DEBUG
        print("Assignments")
        print(json.dumps(self.decision_unit.assignments, indent=4, default=str))
        print("Nodes avilability")
        print(json.dumps(self.node_manager.occupation, indent=4, default=str))

        if self.submission_queue.empty():
            return
        self.time_window += 1
        self._add_csv_row(new_window=True)
        
        pipelines_recv = []
        while not self.submission_queue.empty():
            pipeline_id = self.submission_queue.get()
            pipeline = self.pipelines[pipeline_id]
            pipeline.update(time_window=self.time_window)
            pipelines_recv.append(pipeline_id)
    
        placements = self.decision_unit.get_placements(pipelines_recv)

        for placement in placements:
            pipeline_id = placement.get("pipeline_id")
            pipeline = self.pipelines[pipeline_id]
            mapping = placement.get("mapping")
            efforts = placement.get("efforts", {})
            pipeline.update(effort=efforts.get("total", 0))

            for c, node in mapping.items():
                name, platform = node
                pipeline.update_component(c, node=name, platform=platform, effort=efforts.get(c, 0))

            self._build_pipeline(pipeline_id, mapping)
            self.waiting_list.append(pipeline_id)


    def update_pipelines(self) -> None:
        """
        Update the status of running pipelines and check waiting pipelines.
        """
        # Update running pipelines
        kfp_runs = self._get_kfp_runs()
        for pipeline_id in self.running_pipelines:
            pipeline = self.pipelines[pipeline_id]
            if pipeline.kfp_id is None:
                self._update_kfp_id(pipeline)
            if pipeline.kfp_id is None:
                print("Kfp id still unavailable for pipeline: ", pipeline_id)
                continue
            
            run_details = kfp_runs.get(pipeline.kfp_id)
            if run_details is not None:
                self._update_components(pipeline_id, run_details)
                pipeline.update_kfp(run_details)
        
        self._terminate_pipelines()

        # Check for new pipeline to be executed
        for pipeline_id in self.waiting_list.copy():
            pipeline = self.pipelines[pipeline_id]
            nodes_required = [c.node for c in pipeline.get_components()]

            if self.node_manager.nodes_available(nodes_required):
                self.node_manager.reserve_nodes(nodes_required, pipeline_id)
                self._run_pipeline(pipeline_id)
                self.running_pipelines.append(pipeline_id)
                self.waiting_list.remove(pipeline_id)

        self._add_csv_row()

        # DEBUG
        print("Waiting list: ", self.waiting_list)
        print("Running pipelines: ", self.running_pipelines)
        self.print_running_pipelines()


    def _update_components(self, pipeline_id: str, run_details: Dict) -> None:
        """
        Update pipeline components with details from KFP API.
        """
        task_details = run_details["run_details"]["task_details"]
        pipeline = self.pipelines[pipeline_id]
        pipeline.update_components_kfp(task_details)

        for c in pipeline.get_components():
            if c.state == "SUCCEEDED":
                self.decision_unit.rm_assignment(c.node, pipeline_id, c.name)
                if not self.decision_unit.is_node_needed(c.node, pipeline_id):
                    self.node_manager.release_nodes([c.node], pipeline_id)


    def _terminate_pipelines(self) -> None:
        """
        Terminate pipelines that are completed.
        """
        for pipeline_id in self.running_pipelines.copy():
            pipeline = self.pipelines[pipeline_id]
            if pipeline.state in ["SUCCEEDED", "FAILED"]:
                self.running_pipelines.remove(pipeline_id)
                for c in pipeline.get_components():
                    self.decision_unit.rm_assignment(c.node, pipeline_id, c.name)
                    self.node_manager.release_nodes([c.node], pipeline_id)


    def _build_pipeline(self, pipeline_id: str, mapping: Dict[str, Tuple[str, str]]) -> None:
        """
        Build the pipeline using the provided mapping.
        """
        pipeline = self.pipelines[pipeline_id]
        path = pipelines_dir / pipeline_id / PIPELINE_FILENAME
        args = ["python3", path, "-u", self.kfp_url, "-m"]

        mapping_arg = []
        for component in pipeline.get_components():
            mapping_arg.append(mapping[component.name])
        mapping_arg_json = json.dumps(mapping_arg)
        args.append(mapping_arg_json)

        if ENABLE_CACHING:
            args.append("-c")

        try:
            subprocess.run(args=args, capture_output=True, cwd=pipelines_dir / pipeline_id)
        except Exception as e:
            print("Error while building pipeline:", e)
            pipeline.update(state="FAILED")


    def _run_pipeline(self, pipeline_id: str) -> None:
        """
        Trigger the execution of the pipeline.
        """
        pipeline = self.pipelines[pipeline_id]

        try:
            print("----- Running pipeline: ", pipeline_id)
            run = subprocess.run(
                args=["python3", pipelines_dir / pipeline_id / f"{KFP_PREFIX}{PIPELINE_FILENAME}"],
                capture_output=True,
                cwd=pipelines_dir / pipeline_id
            )
            output = run.stdout.decode("utf-8")
            print("----- Pipeline output:")
            print(output)
            kfp_id = output.split("Run ID:")[-1].strip()
            pipeline.update(kfp_id=kfp_id, state="RUNNING")

        except Exception as e:
            print("Error while running pipeline:", e)
            pipeline.update(state="FAILED")


    def _update_kfp_id(self, pipeline: Pipeline) -> None:
        """
        Extract the KFP ID of the pipeline from the KFP API.
        """
        url = f"{self.kfp_url}{KFP_API_ENDPOINT}/runs"
        name = pipeline.name.lower().replace("_", "-")
        try:
            response = requests.get(url).json()
            runs = response.get("runs", [])
            for run in runs:
                if run["display_name"].startswith(name):
                    pipeline.update(kfp_id=run["run_id"])
        except requests.exceptions.RequestException:
            print("Error fetching runs from KFP API")

    
    def _get_kfp_runs(self) -> Dict[str, Dict]:
        """
        Fetch the list of runs from the KFP API.
        """
        url = f"{self.kfp_url}{KFP_API_ENDPOINT}/runs"
        try:
            response = requests.get(url, timeout=6).json()
            runs = response.get("runs", [])
            runs_dict = {r["run_id"]: r for r in runs}
            return runs_dict
        except requests.exceptions.RequestException:
            print("Error fetching runs from KFP API")
            return {}
        

    def _add_csv_row(self, new_window: bool = False) -> None:
        """
        Add a new row to the CSV file.
        """
        self.csv_writer.writerow([
            time.time(),
            "new_window" if new_window else "update",
            len(self.running_pipelines),
            len(self.waiting_list)
        ])


    def print_running_pipelines(self) -> None:
        for pipeline_id in self.running_pipelines:
            pipeline = self.pipelines[pipeline_id]
            print(pipeline)
