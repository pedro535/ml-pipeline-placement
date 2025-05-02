from kfp import dsl
from kfp.dsl import Model, Input, Dataset
from typing import Dict, Any


@dsl.component(base_image="registry.localhost/kfp_tf_base:kfp")
def model_evaluation(
    model_artifact: Input[Model], x_test_ds: Input[Dataset], y_test_ds: Input[Dataset]
) -> Dict[str, Any]:
    import numpy as np
    import tensorflow as tf
    import keras
    from sklearn.metrics import (
        accuracy_score,
        f1_score,
        precision_score,
        confusion_matrix,
    )

    device = "/GPU:0" if tf.config.list_physical_devices("GPU") else "/CPU:0"
    x_test = np.load(x_test_ds.path)
    y_test = np.load(y_test_ds.path)
    model = keras.models.load_model(model_artifact.path + "/model.h5")
    with tf.device(device):
        y_pred = model.predict(x_test)
        y_pred = np.argmax(y_pred, axis=1)
    metrics = {
        "accuracy": accuracy_score(y_test, y_pred),
        "f1_score": f1_score(y_test, y_pred, average="weighted"),
        "precision": precision_score(y_test, y_pred, average="weighted"),
        "confusion_matrix": confusion_matrix(y_test, y_pred).tolist(),
    }
    return metrics
