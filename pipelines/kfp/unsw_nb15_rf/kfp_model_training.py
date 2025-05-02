from kfp import dsl
from kfp.dsl import Output, Dataset, Input, Model


@dsl.component(base_image="registry.localhost/kfp_python_base:kfp")
def model_training(
    x_train_ds: Input[Dataset],
    y_train_ds: Input[Dataset],
    model_artifact: Output[Model],
):
    import joblib
    import numpy as np
    from sklearn.ensemble import RandomForestClassifier

    x_train = np.load(x_train_ds.path)
    y_train = np.load(y_train_ds.path)
    model = RandomForestClassifier(
        n_estimators=100, max_depth=20, random_state=42, n_jobs=-1
    )
    model.fit(x_train, y_train)
    joblib.dump(model, model_artifact.path)
    print(f"Model saved to {model_artifact.path}")
