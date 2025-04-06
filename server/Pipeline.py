from typing import Dict, List
from datetime import datetime
from dateutil import tz
import json

from server import Component
from server.settings import METADATA_FILENAME, EPOCH_DATE, pipelines_dir


class Pipeline:

    def __init__(self, id: str):
        self.id = id
        self.kfp_id = None
        self.state = None
        self.effort = None
        self.scheduled_at = None
        self.finished_at = None
        self.duration = None
        self.last_update = None
        self.metadata = {}
        self.components: Dict[str, Component] = {}
        self.load_metadata()


    def __str__(self):
        obj_dict = self.__dict__.copy()
        obj_dict.pop("metadata", None)
        obj_dict.pop("components", None)
        obj_dict["components"] = {name: component.dict_repr() for name, component in self.components.items()}
        return json.dumps(obj_dict, indent=4, default=str)

    
    def load_metadata(self):
        with open(pipelines_dir / self.id / METADATA_FILENAME, "r") as f:
            self.metadata = json.load(f)


    def get_metadata(self) -> Dict:
        return self.metadata
    

    def update(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)

    
    def update_kfp(self, run_details: Dict):
        self.state = run_details["state"]
        self.scheduled_at = run_details["scheduled_at"]
        self.finished_at = run_details["finished_at"] if run_details["finished_at"] > EPOCH_DATE else None
        duration = (run_details["finished_at"] - run_details["scheduled_at"]).total_seconds()
        self.duration = round(duration, 2) if duration >= 0 else None
        self.last_update = datetime.now(tz=tz.tzutc())

        
    def add_component(self, component: Component):
        self.components[component.name] = component


    def get_component(self, name) -> Component:
        return self.components.get(name)

    
    def get_components(self) -> List[Component]:
        return list(self.components.values())
        

    def update_component(self, component: str, **kwargs):
        if component in self.components:
            for key, value in kwargs.items():
                setattr(self.components[component], key, value)
        else:
            raise ValueError(f"Component {component} not found in pipeline {self.id}")
        
    
    def update_components_kfp(self, task_details: List[Dict]):
        for task in task_details:
            task_name = task["display_name"]
            if task_name in self.components:
                component = self.components[task_name]
                component.start_time = task["start_time"]
                component.end_time = task["end_time"] if task["end_time"] > EPOCH_DATE else None
                duration = (task["end_time"] - task["start_time"]).total_seconds()
                component.duration = round(duration, 2) if duration >= 0 else None
                component.state = task["state"]