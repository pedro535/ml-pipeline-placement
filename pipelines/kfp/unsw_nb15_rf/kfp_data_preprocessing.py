from kfp import dsl
from kfp.dsl import Dataset, Output


@dsl.component(base_image="registry.localhost/kfp_python_base:kfp")
def data_preprocessing(
    dataset_path: str,
    x_train_ds: Output[Dataset],
    x_test_ds: Output[Dataset],
    y_train_ds: Output[Dataset],
    y_test_ds: Output[Dataset],
):
    import pandas as pd
    import numpy as np
    from sklearn.model_selection import train_test_split
    from sklearn.preprocessing import StandardScaler, LabelEncoder

    def npy_save(data, path):
        with open(path, "wb") as f:
            np.save(f, data)

    df = pd.read_csv(dataset_path)
    df = df.drop(labels=["id", "attack_cat"], axis=1)
    df = df.dropna()
    categorical_cols = df.select_dtypes(include=["object"]).columns
    numeric_cols = df.select_dtypes(include=["float64", "int64"]).columns
    numeric_cols = numeric_cols.drop(["label"])
    for col in categorical_cols:
        if col in df.columns:
            label_encoder = LabelEncoder()
            df[col] = label_encoder.fit_transform(df[col])
    x = df.drop(["label"], axis=1)
    y = df["label"]
    x_train, x_test, y_train, y_test = train_test_split(
        x, y, test_size=0.2, shuffle=True, random_state=42, stratify=y
    )
    scaler = StandardScaler()
    x_train[numeric_cols] = scaler.fit_transform(x_train[numeric_cols])
    x_test[numeric_cols] = scaler.transform(x_test[numeric_cols])
    npy_save(x_train, x_train_ds.path)
    npy_save(y_train, y_train_ds.path)
    npy_save(x_test, x_test_ds.path)
    npy_save(y_test, y_test_ds.path)
    print("Data saved as artifacts")
