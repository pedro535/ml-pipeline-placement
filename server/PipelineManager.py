from queue import Queue

class PipelineManager:

    def __init__(self, kfp_url: str, enable_caching: bool, pipelines_dir: str):
        self.kfp_url = kfp_url
        self.enable_caching = enable_caching
        self.dir = pipelines_dir
        self.pipelines = Queue()


    def add_pipeline(self, pipeline_id: str):
        """
        Add pipeline to the queue
        """
        self.pipelines.put(pipeline_id)


    def process_pipelines(self):
        """
        Process pipelines in the queue
        """
        print("Queue size:", self.pipelines.qsize())
        while not self.pipelines.empty():
            pipeline_id = self.pipelines.get()
            print(pipeline_id)