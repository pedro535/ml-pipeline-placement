from mlopx.artifacts import InputModel, InputDataset
from typing import Dict


def model_evaluation(
    model_artifact: InputModel,
    x_test_ds: InputDataset,
    y_test_ds: InputDataset
) -> Dict[str, float]:
    
    import joblib
    import numpy as np
    from sklearn.metrics import accuracy_score, f1_score, precision_score

    # Load data
    x_test = np.load(x_test_ds.path)
    y_test = np.load(y_test_ds.path)

    # Load model
    model = joblib.load(model_artifact.path)

    # Evaluate model
    y_pred = model.predict(x_test)
    
    metrics = {
        "accuracy": accuracy_score(y_test, y_pred),
        "f1_score": f1_score(y_test, y_pred),
        "precision": precision_score(y_test, y_pred)
    }
    return metrics