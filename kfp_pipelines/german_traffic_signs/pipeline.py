from kfp import dsl, Client
from kfp.kubernetes import mount_pvc, add_node_selector, add_toleration
from typing import Dict

from data_collection import data_collection
from model_training import model_training
from model_evaluation import model_evaluation


KFP_URL = "http://localhost:3000"
PVC = "datasets-pvc"
MOUNT_PATH = "/mnt/datasets"


@dsl.pipeline(
    name = "German Traffic Signs pipeline",
    description = "Pipeline that loads the German Traffic Signs dataset, trains a model, and evaluates it."
)
def gts_pipeline(
    dataset_path: str,
    epochs: int,
    batch_size: int
) -> Dict[str, float]:

    # 1. Data Collection
    data_collection_task = data_collection(
        dataset_path = dataset_path
    )

    # 2. Model Training
    model_training_task = model_training(
        X_train_ds=data_collection_task.outputs["X_train_ds"],
        X_val_ds=data_collection_task.outputs["X_val_ds"],
        y_train_ds=data_collection_task.outputs["y_train_ds"],
        y_val_ds=data_collection_task.outputs["y_val_ds"],
        epochs=epochs,
        batch_size = batch_size
    )

    # 3. Model Evaluation
    model_evaluation_task = model_evaluation(
        model_artifact=model_training_task.outputs["model_artifact"],
        X_test_ds=data_collection_task.outputs["X_test_ds"],
        y_test_ds=data_collection_task.outputs["y_test_ds"]
    )

    # Mount volumes
    data_collection_task = mount_pvc(
        task=data_collection_task,
        pvc_name=PVC,
        mount_path=MOUNT_PATH
    )

    # Add node selectors
    data_collection_task = add_node_selector(
        task=data_collection_task,
        label_key="kubernetes.io/hostname",
        label_value="k3s-node1"
    )

    model_training_task = add_node_selector(
        task=model_training_task,
        label_key="kubernetes.io/hostname",
        label_value="k3s-node2"
    )

    model_evaluation_task = add_node_selector(
        task=model_evaluation_task,
        label_key="kubernetes.io/hostname",
        label_value="k3s-node3"
    )

    # Add tolerations
    data_collection_task = add_toleration(
        task=data_collection_task,
        key="component-id",
        operator="Equal",
        value="data-collection",
        effect="NoSchedule"
    )

    model_training_task = add_toleration(
        task=model_training_task,
        key="component-id",
        operator="Equal",
        value="model-training",
        effect="NoSchedule"
    )

    model_evaluation_task = add_toleration(
        task=model_evaluation_task,
        key="component-id",
        operator="Equal",
        value="model-evaluation",
        effect="NoSchedule"
    )


    return model_evaluation_task.output



if __name__ == "__main__":
    client = Client(host=KFP_URL)

    client.create_run_from_pipeline_func(
        pipeline_func=gts_pipeline,
        arguments={
            "dataset_path": "/mnt/datasets/german_traffic_signs",
            "epochs": 1,
            "batch_size": 128
        }
    )