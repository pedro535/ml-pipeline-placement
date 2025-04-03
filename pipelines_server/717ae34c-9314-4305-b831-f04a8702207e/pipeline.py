from mlopx import Pipeline, Component
from data_preprocessing import data_preprocessing
from model_training import model_training
from model_evaluation import model_evaluation
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("-u", type=str, help="kfp URL", required=True)
parser.add_argument("-c", help="Enable caching", action="store_true")
parser.add_argument("-m", type=str, help="Mapping", required=True)
args = parser.parse_args()
BASE_IMAGE = "registry.localhost/kfp_python_base"
component_1 = Component(
    func=data_preprocessing,
    image=BASE_IMAGE,
    args={"dataset_path": "/mnt/datasets/adult_income/adult.csv"},
)
component_1.mount_volume(pvc="datasets-pvc", mount_path="/mnt/datasets")
component_2 = Component(image=BASE_IMAGE, func=model_training, args={})
component_3 = Component(image=BASE_IMAGE, func=model_evaluation, args={})
pipeline = Pipeline(name="adult_income_lr", metadata_file="metadata.json")
pipeline.add([component_1, component_2, component_3])
pipeline.build(args.u, args.c, args.m)
