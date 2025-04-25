from mlopx.pipelines import Pipeline, Component

from data_preprocessing import data_preprocessing
from model_training import model_training
from model_evaluation import model_evaluation


BASE_IMAGE = "registry.localhost/kfp_tf_base"

component_1 = Component(
    func=data_preprocessing,
    image=BASE_IMAGE,
    args={
        "dataset_path": "/mnt/datasets/FASHION_MNIST"
    }
)

component_1.mount_volume(
    pvc="datasets-pvc",
    mount_path="/mnt/datasets"
)

component_2 = Component(
    image=BASE_IMAGE, 
    func=model_training,
    args={}
)

component_3 = Component(
    image=BASE_IMAGE,
    func=model_evaluation,
    args={}
)

pipeline = Pipeline(name="fashion_mnist_cnn", metadata_file="metadata.json")
pipeline.add([component_1, component_2, component_3])
pipeline.submit("http://127.0.0.1:8000")
