from pathlib import Path
from queue import Queue
import subprocess


class PipelineManager:

    def __init__(self, kfp_url: str, enable_caching: bool, pipelines_dir: Path):
        self.kfp_url = kfp_url
        self.enable_caching = enable_caching
        self.dir = pipelines_dir
        self.pipelines = Queue()


    def add_pipeline(self, pipeline_id: str):
        """
        Add pipeline to the queue
        """
        self.pipelines.put(pipeline_id)

    
    def analyze_pipeline(self, pipeline_id: str):
        pass

    
    def build_pipeline(self, pipeline_id: str):
        result = subprocess.run(
            args=["python3", self.dir / pipeline_id / "pipeline.py", "-u", self.kfp_url, "-p", "k3s-node3", "k3s-node1"],
            capture_output=True,
            cwd=self.dir / pipeline_id
        )
        print(result.stdout.decode("utf-8"))


    def run_pipeline(self, pipeline_id: str):
        result = subprocess.run(
            args=["python3", self.dir / pipeline_id / "kfp_pipeline.py"],
            capture_output=True,
            cwd=self.dir / pipeline_id
        )
        print(result.stdout.decode("utf-8"))
        # TODO: capture output to get kfp details


    def process_pipelines(self):
        """
        Process pipelines in the queue
        """
        print("Queue size:", self.pipelines.qsize())
        while not self.pipelines.empty():
            pipeline_id = self.pipelines.get()
            # self.build_pipeline(pipeline_id)
            # self.run_pipeline(pipeline_id)