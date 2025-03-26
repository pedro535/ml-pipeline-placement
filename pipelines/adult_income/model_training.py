from mlopx.artifacts import InputDataset, OutputModel


def model_training(
    model_type: str,
    x_train_ds: InputDataset,
    y_train_ds: InputDataset,
    model_artifact: OutputModel
):
    import joblib
    import numpy as np
    from sklearn.linear_model import LogisticRegression
    from sklearn.tree import DecisionTreeClassifier
    from sklearn.ensemble import RandomForestClassifier


    # Load data
    x_train = np.load(x_train_ds.path)
    y_train = np.load(y_train_ds.path)

    # Train model
    if model_type == "logistic_regression":
        model = LogisticRegression(
            C=0.1,
            solver="liblinear",
            max_iter=100,
            random_state=42
        )
        model.fit(x_train, y_train)
    
    elif model_type == "decision_tree":
        model = DecisionTreeClassifier(
            max_depth=10,
            min_samples_split=10,
            min_samples_leaf=4,
            criterion="entropy",
            ccp_alpha=0.0,
            random_state=42
        )
        model.fit(x_train, y_train)

    elif model_type == "random_forest":
        model = RandomForestClassifier(
            n_estimators=150,
            max_depth=20,
            min_samples_split=5,
            min_samples_leaf=3,
            criterion="entropy",
            max_features="sqrt",
            random_state=42
        )
        model.fit(x_train, y_train)

    # Save model
    joblib.dump(model, model_artifact.path)
    print(f"Model saved to {model_artifact.path}")