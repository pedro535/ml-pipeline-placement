from kfp import dsl
from kfp.dsl import Model, Dataset, Input, Output


@dsl.component(base_image="registry.localhost/kfp_python_base:kfp")
def model_training(
    x_train_ds: Input[Dataset],
    y_train_ds: Input[Dataset],
    model_artifact: Output[Model],
):
    import joblib
    import numpy as np
    from sklearn.tree import DecisionTreeClassifier

    x_train = np.load(x_train_ds.path)
    y_train = np.load(y_train_ds.path)
    model = DecisionTreeClassifier(
        max_depth=10,
        min_samples_split=10,
        min_samples_leaf=4,
        criterion="entropy",
        ccp_alpha=0.0,
        random_state=42,
    )
    model.fit(x_train, y_train)
    joblib.dump(model, model_artifact.path)
    print(f"Model saved to {model_artifact.path}")
