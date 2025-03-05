#### For development purposes only ####
import sys
sys.path.append("../../")
#######################################

from MLOpti_client.artifacts import InputModel, InputDataset
from typing import Dict


def model_evaluation(
    model_artifact: InputModel,
    X_test_ds: InputDataset,
    y_test_ds: InputDataset
) -> Dict[str, float]:
    
    import numpy as np
    import pandas as pd
    from PIL import Image
    import tensorflow as tf
    from tensorflow import keras
    from sklearn.metrics import f1_score, accuracy_score

    device = "/GPU:0" if tf.config.list_physical_devices("GPU") else "/CPU:0"


    # Load data
    X_test = np.load(X_test_ds.path)
    y_test = np.load(y_test_ds.path)

    # Load model
    model = keras.models.load_model(model_artifact.path + "/model.h5")

    # Evaluate model
    with tf.device(device):
        preds = np.argmax(model.predict(X_test), axis=-1)

    metrics = {
        "accuracy": accuracy_score(y_test, preds),
        "f1_score": f1_score(y_test, preds, average="weighted")
    }

    print("=" * 20)
    print(f"Accuracy: {metrics["accuracy"]}")
    print(f"F1 Score: {metrics["f1_score"]}")
    print("=" * 20)

    return metrics