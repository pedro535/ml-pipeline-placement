import requests
from typing import List
import inspect
from MLOpti_client import Component

class Pipeline:

    def __init__(self, name):
        self.name = name
        self.components = []


    def add(self, components: List[Component]):
        """
        Add a list of components to the pipeline
        """
        self.components.extend(components)


    def submit(self, server):
        """
        Submit the pipeline to the server
        """
        files = self._prepare_files()
        response = self._send_request(server, files)
        self._handle_response(response)


    def _prepare_files(self):
        """
        Prepare the files for submission
        """
        files = [("files", (c.filename, open(c.file, "rb"))) for c in self.components]
        files.append(("files", ("pipeline.py", open("pipeline.py", "rb"))))
        return files


    def _send_request(self, server, files):
        """
        Send the POST request to the server
        """
        try:
            response = requests.post(f"{server}/submit/", files=files)
            response.raise_for_status()
            return response
        except requests.RequestException as e:
            print(f"An error occurred: {e}")
            return None


    def _handle_response(self, response):
        """
        Handle the server response
        """
        if response:
            try:
                print(response.json())
            except ValueError:
                print("Failed to parse response JSON")