#### For development purposes only ####
import sys
sys.path.append("../../")
#######################################

from MLOpti_client import Pipeline, Component

from data_collection import data_collection
from model_training import model_training
from model_evaluation import model_evaluation

SERVER_URL = "http://127.0.0.1:8000"
BASE_IMAGE = "registry.localhost/python_kfp:v3"

component_1 = Component(
    func=data_collection,
    image=BASE_IMAGE,
    args={
        "dataset_path": "/mnt/datasets/german_traffic_signs"
    }
)

component_1.mount_volume(
    pvc="datasets-pvc",
    mount_path="/mnt/datasets"
)

component_2 = Component(
    image=BASE_IMAGE, 
    func=model_training,
    args={
        "epochs": 1,
        "batch_size": 128
    }
)

component_3 = Component(
    image=BASE_IMAGE,
    func=model_evaluation,
    args={}
)

pipeline = Pipeline(name="german_traffic_signs")
pipeline.add([component_1, component_2, component_3])
pipeline.submit(SERVER_URL)
