from Pipeline import Pipeline
from Steps import Steps

from data_collection import data_collection
from model_training import model_training

IMAGE = "registry.localhost/python_kfp:v3"

pipeline = Pipeline()

pipeline.add(
    image=IMAGE,
    func=data_collection,
    args={
        "dataset_path": "/mnt/datasets/german_traffic_signs"
    }
)

pipeline.add(
    image=IMAGE,
    func=model_training,
    args={
        "epochs": 2,
        "batch_size": 128
    }
)

pipeline.run("kfp_host")