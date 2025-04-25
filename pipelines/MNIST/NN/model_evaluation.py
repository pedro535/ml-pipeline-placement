from mlopx.pipelines.artifacts import InputModel, InputDataset
from typing import Dict, Any


def model_evaluation(
    model_artifact: InputModel,
    x_test_ds: InputDataset,
    y_test_ds: InputDataset
) -> Dict[str, Any]:

    import numpy as np
    import tensorflow as tf
    import keras
    from sklearn.metrics import accuracy_score, f1_score, precision_score, confusion_matrix

    device = "/GPU:0" if tf.config.list_physical_devices("GPU") else "/CPU:0"

    # Load data
    x_test = np.load(x_test_ds.path)
    y_test = np.load(y_test_ds.path)

    # Load model
    model = keras.models.load_model(model_artifact.path + "/model.h5")

    # Evaluate model
    with tf.device(device):
        y_pred = model.predict(x_test)
        y_pred = np.argmax(y_pred, axis=1)
    
    metrics = {
        "accuracy": accuracy_score(y_test, y_pred),
        "f1_score": f1_score(y_test, y_pred, average="weighted"),
        "precision": precision_score(y_test, y_pred, average="weighted"),
        "confusion_matrix": confusion_matrix(y_test, y_pred).tolist()
    }
    return metrics