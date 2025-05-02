from kfp import dsl
from kfp.dsl import Dataset, Input, Model
from typing import Dict, Any


@dsl.component(base_image="registry.localhost/kfp_python_base:kfp")
def model_evaluation(
    model_artifact: Input[Model], x_test_ds: Input[Dataset], y_test_ds: Input[Dataset]
) -> Dict[str, Any]:
    import joblib
    import numpy as np
    from sklearn.metrics import (
        accuracy_score,
        f1_score,
        precision_score,
        confusion_matrix,
    )

    x_test = np.load(x_test_ds.path)
    y_test = np.load(y_test_ds.path)
    model = joblib.load(model_artifact.path)
    y_pred = model.predict(x_test)
    metrics = {
        "accuracy": accuracy_score(y_test, y_pred),
        "f1_score": f1_score(y_test, y_pred),
        "precision": precision_score(y_test, y_pred),
        "confusion_matrix": confusion_matrix(y_test, y_pred).tolist(),
    }
    return metrics
