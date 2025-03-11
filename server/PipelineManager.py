from datetime import datetime
from dateutil import tz
from pathlib import Path
from queue import Queue
from typing import List, Dict
import subprocess

from kfp import Client

# REMOVE LATER
import json


class PipelineManager:

    def __init__(self, kfp_url: str, enable_caching: bool, pipelines_dir: Path):
        self.kfp_url = kfp_url
        self.enable_caching = enable_caching
        self.dir = pipelines_dir
        self.pipelines = {}
        self.queue = Queue()
        self.kfp_client = Client(host=kfp_url)
        print(enable_caching)


    def add_pipeline(self, pipeline_id: str, component_files: List[str]):
        """
        Add pipeline to the queue
        """
        self.queue.put(pipeline_id)
        
        component_names = [c.split(".")[0].lower().replace("_", "-") for c in component_files]
        self.pipelines[pipeline_id] = {
            "components": {c: {} for c in component_names},
            "state": "QUEUED",
            "kfp_id": None,
            "scheduled_at": None,
            "finished_at": None,
            "duration": None,
            "last_update": None
        }

        for i, c in enumerate(component_names):
            self.pipelines[pipeline_id]["components"][c]["file"] = component_files[i]

    
    def analyze_pipeline(self, pipeline_id: str):
        pass

    
    def build_pipeline(self, pipeline_id: str):
        """
        Build the kfp pipeline
        """
        path = self.dir / pipeline_id / "pipeline.py"
        args = ["python3", path, "-u", self.kfp_url, "-p", "k3s-node3", "k3s-node2", "k3s-node1"]
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
        Process pipelines in the queue
        """
        print("Queue size:", self.queue.qsize())
        while not self.queue.empty():
            pipeline_id = self.queue.get()
            self.build_pipeline(pipeline_id)
            self.run_pipeline(pipeline_id)

    
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


    def update_active_pipelines(self):
        """
        Update the state of active pipelines
        """
        for pipeline in self.pipelines.values():
            if pipeline["state"] not in ["QUEUED", "SUCCEEDED", "FAILED"]:
                run_details = self.kfp_client.get_run(pipeline["kfp_id"]).to_dict()
                self.update_component_details(pipeline, run_details["run_details"]["task_details"])
                self.update_pipeline_details(pipeline, run_details)

                # REMOVE LATER
                print("---" * 10)
                print(json.dumps(pipeline, indent=4, default=str))