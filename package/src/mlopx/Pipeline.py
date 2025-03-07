import os
import requests
import ast
import astor
import black
from typing import List, Tuple

from mlopx import Component, PipelineBuilder
from mlopx.consts import ARGPARSE_CODE


class Pipeline:

    def __init__(self, name: str):
        self.name = name
        self.func_name = name.replace(" ", "_").lower()
        self.components = []
        self.artifacts = {}
        self.tree = None


    def add(self, components: List[Component]) -> None:
        """
        Add a list of components to the pipeline
        """
        self.components.extend(components)
        for component in components:
            for arg_name, arg_type in component.arg_types.items():
                if "Output" in arg_type:
                    self.artifacts[arg_name] = component.name

    
    def create_tmp_pipeline(self, tmp_filename: str) -> None:
        """
        Create a temporary pipeline file to be submitted
        """
        with open("pipeline.py", "r") as f:
            code = f.read()
            tree = ast.parse(code)

        argparse_nodes = [n for line in ARGPARSE_CODE for n in ast.parse(line).body]
        run_node = ast.parse("pipeline.build(args.u, args.c, args.p)").body

        for i, node in enumerate(tree.body):
            if not isinstance(node, ast.ImportFrom) and not isinstance(node, ast.Import):
                break
            
        tree.body = tree.body[:i] + argparse_nodes + tree.body[i:-1] + run_node
        with open(tmp_filename, "w") as f:
            ast.fix_missing_locations(tree)
            kfp_pipeline = astor.to_source(tree)
            kfp_pipeline = black.format_str(kfp_pipeline, mode=black.Mode())
            f.write(kfp_pipeline)


    def prepare_files(self) -> List[Tuple]:
        """
        Prepare the files for submission
        """
        files = [
            ("components", (c.filename, open(c.filename, "rb"))) for c in self.components
        ]

        tmp_file = "pipeline_tmp.py"
        self.create_tmp_pipeline(tmp_file)
        files.append(("pipeline", ("pipeline.py", open(tmp_file, "rb"))))
        os.remove(tmp_file)

        return files


    def send_pipeline(self, server_url: str, files: List[Tuple]) -> requests.Response:
        """
        Send the pipeline files to the server
        """
        try:
            response = requests.post(f"{server_url}/submit/", files=files)
            response.raise_for_status()
            return response
        except requests.RequestException as e:
            print(f"An error occurred: {e}")
            return None


    def handle_response(self, response: requests.Response) -> None:
        """
        Handle the server response
        """
        if response:
            try:
                print(response.json())
            except ValueError:
                print("Failed to parse response JSON")


    def submit(self, server_url: str) -> None:
        """
        Submit the pipeline to the server
        """
        files = self.prepare_files()
        response = self.send_pipeline(server_url, files)
        self.handle_response(response)


    def build(self, kfp_url: str, enable_caching: str, placement: List[str]):
        """
        Build the kfp pipeline
        """
        for component in self.components:
            component.convert()

        builder = PipelineBuilder()
        (
            builder.add_imports(self.components)
            .create_function(self.func_name)
            .add_decorator(self.name)
            .call_components(self.components, self.artifacts)
            .mount_volumes(self.components)
            .add_node_selector(self.components, placement)
            .create_client(kfp_url)
            .add_create_run(self.func_name, enable_caching)
            .save_pipeline()
        )
