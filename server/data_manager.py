import os
from pathlib import Path
import subprocess
from datetime import datetime
from typing import Dict, Optional
import numpy as np

from server.settings import DATASETS_PATH


class DataManager:
    def __init__(self):
        self.datasets_dir = Path(DATASETS_PATH)
        self.datasets: Dict[str, Dict] = {}
        self._fetch_datasets()


    def _fetch_datasets(self):
        """
        Fetch and update datasets registry with details of new or modified datasets.
        """
        folder_names = [
            name for name in os.listdir(self.datasets_dir)
            if not name.startswith(".")
        ]

        for name in folder_names:
            folder_path = self.datasets_dir / name
            last_modified = self._get_last_modified_time(folder_path)

            if name not in self.datasets or self.datasets[name]["modified_at"] < last_modified:
                self.datasets[name] = {
                    "path": folder_path,
                    "size": self._get_folder_size_kb(folder_path),
                    "modified_at": last_modified
                }


    def _get_last_modified_time(self, path: Path) -> datetime:
        """
        Get the last modification time of a file/folder.
        """
        return datetime.fromtimestamp(os.path.getmtime(path))
    

    def _get_folder_size_kb(self, folder: Path) -> int:
        """
        Get folder size in kilobytes.
        """
        result = subprocess.run(["du", "-sk", str(folder)], capture_output=True, text=True)
        return int(result.stdout.split()[0])


    def _estimate_npy_array_size_kb(self, details: Dict) -> int:
        """
        Estimate the memory size of a NumPy array in kilobytes.
        """
        n_samples = details.get("n_samples")
        data_types = details.get("data_types")

        # Sample size
        sample_size = 0
        for type_name, count in data_types.items():
            size = np.dtype(type_name).itemsize
            sample_size += size * count

        # Total size
        total_size = sample_size * n_samples
        return total_size // 1024


    def update_datasets(self):
        """
        Update the dataset registry by re-fetching the datasets.
        """
        self._fetch_datasets()


    def get_dataset_size(self, dataset_name: str) -> Optional[int]:
        """
        Get the size of a dataset in kilobytes.
        Returns None if dataset is not found.
        """
        if dataset_name in self.datasets:
            return self.datasets[dataset_name]["size"]
        return None
    

    def size_in_memory(self, metadata: Dict, version_key: str) -> Optional[int]:
        """
        Estimate the dataset's memory size in kilobytes.

        :param metadata: Dataset metadata dictionary
        :param version_key: Key for the desired version ('original' or 'preprocessed')
        """
        dataset_type = metadata.get("type")
        name = metadata.get("name")
        version_details = metadata.get(version_key)

        if dataset_type == "image":
            size = self.get_dataset_size(name)
            if not metadata.get("normalized"):
                size *= 8  # from uint8 to float64
        elif dataset_type == "tabular":
            size = self._estimate_npy_array_size_kb(version_details)
        
        return size