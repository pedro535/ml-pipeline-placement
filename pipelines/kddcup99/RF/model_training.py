from mlopx.pipelines.artifacts import InputDataset, OutputModel


def model_training(
    x_train_ds: InputDataset,
    y_train_ds: InputDataset,
    model_artifact: OutputModel
):
    
    import joblib
    import numpy as np
    from sklearn.ensemble import RandomForestClassifier


    # Load data
    x_train = np.load(x_train_ds.path)
    y_train = np.load(y_train_ds.path)

    # Train model
    model = RandomForestClassifier(
        n_estimators=100,
        random_state=42,
        min_samples_leaf=1,
        max_features="sqrt",
        n_jobs=-1
    )
    model.fit(x_train, y_train)

    # Save model
    joblib.dump(model, model_artifact.path)
    print(f"Model saved to {model_artifact.path}")