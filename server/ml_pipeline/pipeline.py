from typing import Dict, List
from datetime import datetime
from dateutil import tz
import json

from server.ml_pipeline import Component
from server.settings import METADATA_FILENAME, EPOCH_DATE, pipelines_dir


class Pipeline:

    def __init__(self, id: str, name: str):
        self.id = id
        self.name = name
        self.kfp_id = None
        self.state = None
        self.effort = None
        self.components: Dict[str, Component] = {}
        self.metadata = {}
        self.submitted_at = datetime.now(tz=tz.tzutc())
        self.scheduled_at = None
        self.finished_at = None
        self.last_update = None
        self.duration = None
        self.time_window = None
        self._load_metadata()


    def __str__(self):
        obj_dict = self.dict_repr()
        return json.dumps(obj_dict, indent=4, default=str)
    

    def _load_metadata(self):
        """
        Load the metadata from the metadata file.
        """
        with open(pipelines_dir / self.id / METADATA_FILENAME, "r") as f:
            self.metadata = json.load(f)
    

    def dict_repr(self):
        """
        Return a dictionary representation of the object, excluding metadata and components.
        """
        obj_dict = self.__dict__.copy()
        obj_dict.pop("effort", None)
        obj_dict.pop("last_update", None)
        obj_dict.pop("time_window", None)
        obj_dict.pop("metadata", None)
        obj_dict.pop("components", None)
        obj_dict["components"] = {name: component.dict_repr() for name, component in self.components.items()}
        return obj_dict


    def get_metadata(self) -> Dict:
        """
        Return the metadata of the pipeline.
        """
        return self.metadata
    

    def update(self, **kwargs):
        """
        Update pipeline with the given keyword arguments.
        """
        for key, value in kwargs.items():
            setattr(self, key, value)

    
    def update_kfp(self, run_details: Dict):
        """
        Update pipeline with the given run details returned by KFP API.
        """
        self.state = run_details["state"]
        scheduled_at = datetime.fromisoformat(run_details["scheduled_at"])
        finished_at = datetime.fromisoformat(run_details["finished_at"])
        self.scheduled_at = scheduled_at
        self.finished_at = finished_at if finished_at > EPOCH_DATE else None
        duration = (finished_at - scheduled_at).total_seconds()
        self.duration = round(duration, 2) if duration >= 0 else None
        self.last_update = datetime.now(tz=tz.tzutc())

        
    def add_component(self, component: Component):
        """
        Add a component to the pipeline.
        """
        component.type = self.metadata["components_type"][component.name]
        self.components[component.name] = component


    def get_component(self, name) -> Component:
        """
        Get a component by name.
        """
        return self.components.get(name)

    
    def get_components(self) -> List[Component]:
        """
        Get all components in the pipeline.
        """
        return list(self.components.values())
        

    def update_component(self, component: str, **kwargs):
        """
        Update a component with the given keyword arguments.
        """
        if component in self.components:
            for key, value in kwargs.items():
                setattr(self.components[component], key, value)
        else:
            raise ValueError(f"Component {component} not found in pipeline {self.id}")
        
    
    def update_components_kfp(self, task_details: List[Dict]):
        """
        Update components with the given task details returned by KFP API.
        """
        for task in task_details:
            task_name = task["display_name"]
            if task_name in self.components:
                component = self.components[task_name]
                start_time = datetime.fromisoformat(task["start_time"])
                end_time = datetime.fromisoformat(task["end_time"])
                component.start_time = start_time
                component.end_time = end_time if end_time > EPOCH_DATE else None
                duration = (end_time - start_time).total_seconds()
                component.duration = round(duration, 2) if duration >= 0 else None
                component.state = task.get("state")