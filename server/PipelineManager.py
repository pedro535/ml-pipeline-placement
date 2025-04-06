from queue import Queue
from typing import List, Dict, Tuple
import subprocess
from kfp import Client
import json

from server import DecisionUnit, NodeManager, Pipeline, Component
from server.settings import (
    KFP_URL,
    ENABLE_CACHING,
    PIPELINE_FILENAME,
    KFP_PREFIX,
    pipelines_dir
)


class PipelineManager:

    def __init__(self, decision_unit: DecisionUnit, node_manager: NodeManager):
        self.decision_unit = decision_unit
        self.node_manager = node_manager
        self.kfp_url = KFP_URL
        self.kfp_client = Client(host=self.kfp_url)
        self.pipelines: Dict[str, Pipeline] = {}
        self.submission_queue = Queue()
        self.waiting_list = []
        self.running_pipelines = []


    def add_pipeline(self, pipeline_id: str, name: str, components: List[Tuple[str, str]]):
        self.submission_queue.put(pipeline_id)
        pipeline = Pipeline(pipeline_id, name)
        
        for filename, name in components:
            component = Component(name, filename)
            pipeline.add_component(component)

        self.pipelines[pipeline_id] = pipeline


    def process_pipelines(self):
        # DEBUG
        print("Assignments")
        print(json.dumps(self.decision_unit.assignments, indent=4, default=str))
        print("Nodes avilability")
        print(json.dumps(self.node_manager.availability, indent=4, default=str))

        if self.submission_queue.empty():
            return
        
        pipelines_recv = []
        while not self.submission_queue.empty():
            pipeline_id = self.submission_queue.get()
            pipelines_recv.append(self.pipelines[pipeline_id])
    
        placements = self.decision_unit.get_placements(pipelines_recv)

        for placement in placements:
            pipeline_id = placement["pipeline_id"]
            pipeline = self.pipelines[pipeline_id]
            mapping = placement["mapping"]
            efforts = placement["efforts"]
            pipeline.update(effort=efforts["total"])

            for c, node in mapping.items():
                name, platform = node
                pipeline.update_component(c, node=name, platform=platform, effort=efforts[c])

            self._build_pipeline(pipeline_id, mapping)
            self.waiting_list.append(pipeline_id)


    def update_pipelines(self):
        # Update running pipelines
        for pipeline_id in self.running_pipelines:
            pipeline = self.pipelines[pipeline_id]
            run_details = self.kfp_client.get_run(pipeline.kfp_id).to_dict()

            self._update_components(pipeline_id, run_details)
            pipeline.update_kfp(run_details)
        
        # Terminate completed pipelines
        self._terminate_pipelines()

        # Check for new pipeline to be executed
        for pipeline_id in self.waiting_list.copy():
            pipeline = self.pipelines[pipeline_id]
            nodes = [c.node for c in pipeline.get_components()]

            if self.node_manager.nodes_available(nodes):
                self.node_manager.reserve_nodes(nodes)
                self._run_pipeline(pipeline_id)
                self.running_pipelines.append(pipeline_id)
                self.waiting_list.remove(pipeline_id)

        # DEBUG
        print("Waiting list: ", self.waiting_list)
        print("Running pipelines: ", self.running_pipelines)
        self.print_running_pipelines()


    def _update_components(self, pipeline_id: str, run_details: Dict):
        task_details = run_details["run_details"]["task_details"]
        pipeline = self.pipelines[pipeline_id]
        pipeline.update_components_kfp(task_details)

        for c in pipeline.get_components():
            if c.state == "SUCCEEDED":
                self.decision_unit.rm_assignment(c.node, pipeline_id, c.name)
                if not self.decision_unit.is_node_needed(c.node, pipeline_id):
                    self.node_manager.release_nodes([c.node])


    def _terminate_pipelines(self):
        for pipeline_id in self.running_pipelines.copy():
            pipeline = self.pipelines[pipeline_id]
            if pipeline.state not in ["SUCCEEDED", "FAILED"]:
                continue
            
            self.running_pipelines.remove(pipeline_id)
            for c in pipeline.get_components():
                self.decision_unit.rm_assignment(c.node, pipeline_id, c.name)
                self.node_manager.release_nodes([c.node])


    def _build_pipeline(self, pipeline_id: str, mapping: Dict[str, Tuple[str, str]]):
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


    def _run_pipeline(self, pipeline_id: str):
        pipeline = self.pipelines[pipeline_id]

        try:
            run = subprocess.run(
                args=["python3", pipelines_dir / pipeline_id / f"{KFP_PREFIX}{PIPELINE_FILENAME}"],
                capture_output=True,
                cwd=pipelines_dir / pipeline_id
            )
            output = run.stdout.decode("utf-8")
            kfp_id = output.split("Run ID:")[-1].strip()
            pipeline.update(kfp_id=kfp_id, state="RUNNING")

        except Exception as e:
            print("Error while running pipeline:", e)
            pipeline.update(state="FAILED")

    
    def print_running_pipelines(self):
        for pipeline_id in self.running_pipelines:
            pipeline = self.pipelines[pipeline_id]
            print(pipeline)

    
    def dump_pipelines(self):
        pipelines_as_dict = []
        for pipeline in self.pipelines.values():
            pipelines_as_dict.append(pipeline.dict_repr())

        with open(pipelines_dir / "pipelines.json", "w") as f:
            json.dump(pipelines_as_dict, f, indent=4, default=str)