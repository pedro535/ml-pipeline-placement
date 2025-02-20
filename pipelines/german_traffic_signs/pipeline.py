from kfp import dsl, compiler
from kfp.kubernetes import mount_pvc
from typing import Dict

from components.data_collection import data_collection
from components.model_training import model_training
from components.model_evaluation import model_evaluation

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
    data_collection_op = data_collection(
        dataset_path = dataset_path
    )

    data_collection_op = mount_pvc(
        task = data_collection_op,
        pvc_name = PVC,
        mount_path = MOUNT_PATH
    )

    # 2. Model Training
    model_training_op = model_training(
        X_train_ds = data_collection_op.outputs["X_train_ds"],
        X_val_ds = data_collection_op.outputs["X_val_ds"],
        y_train_ds = data_collection_op.outputs["y_train_ds"],
        y_val_ds = data_collection_op.outputs["y_val_ds"],
        epochs = epochs,
        batch_size = batch_size
    )

    # 3. Model Evaluation
    model_evaluation_op = model_evaluation(
        model_artifact = model_training_op.outputs["model_artifact"],
        X_test_ds = data_collection_op.outputs["X_test_ds"],
        y_test_ds = data_collection_op.outputs["y_test_ds"]
    )

    return model_evaluation_op.output


compiler.Compiler().compile(gts_pipeline, "pipeline.yaml")