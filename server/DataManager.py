import os
from pathlib import Path
import subprocess
import json
from datetime import datetime

from server.settings import DATASETS_PATH


class DataManager:

    def __init__(self):
        self.datasets_dir = Path(DATASETS_PATH)
        self.datasets = {}
        self.get_datasets()

        print(json.dumps(self.datasets, indent=4, default=str))


    def get_datasets(self):
        """
        Load details of all datasets in the datasets directory.
        """
        dataset_folders = [
            folder for folder in os.listdir(self.datasets_dir) if not folder.startswith(".")
        ]

        for folder in dataset_folders:
            folder_path = self.datasets_dir / folder
            self.datasets[folder] = {
                "name": folder,
                "size": self.get_folder_size(folder_path),
                "modified_at": self.get_last_modified_time(folder_path),
            }


    def get_folder_size(self, folder):
        """
        Get the size of a folder in KB.
        """
        result = subprocess.run(["du", "-sk", folder], capture_output=True, text=True)
        print(result.stdout)
        size_in_kb = int(result.stdout.split()[0])
        return size_in_kb


    def get_last_modified_time(self, folder):
        """
        Get the creation time of a folder.
        """
        created_at_timestamp = os.path.getmtime(folder)
        return datetime.fromtimestamp(created_at_timestamp)


    def update_datasets(self):
        """
        Update the datasets dictionary with details of new or modified datasets.
        """
        dataset_folders = [
            folder for folder in os.listdir(self.datasets_dir) if not folder.startswith(".")
        ]

        # Identify new or modified datasets
        new_datasets = []
        for folder in dataset_folders:
            folder_path = self.datasets_dir / folder
            if (
                folder not in self.datasets
                or self.datasets[folder]["modified_at"] < self.get_last_modified_time(folder_path)
            ):
                new_datasets.append(folder)

        # Update the datasets
        for folder in new_datasets:
            folder_path = self.datasets_dir / folder
            self.datasets[folder] = {
                "name": folder,
                "size": self.get_folder_size(folder_path),
                "modified_at": self.get_last_modified_time(folder_path),
            }