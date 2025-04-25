from mlopx.pipelines.artifacts import OutputDataset


def data_preprocessing(
    dataset_path: str,
    x_train_ds: OutputDataset,
    x_test_ds: OutputDataset,
    y_train_ds: OutputDataset,
    y_test_ds: OutputDataset
):
    
    import numpy as np
    import pandas as pd
    from sklearn.model_selection import train_test_split
    from sklearn.preprocessing import StandardScaler

    def npy_save(data, path):
        with open(path, "wb") as f:
            np.save(f, data)

    # Load dataset
    df = pd.read_csv(dataset_path, sep=';')
    df['quality'] = (df['quality'] >= 6).astype(int)

    # Split data
    x = df.drop("quality", axis=1)
    y = df["quality"]
    x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=0.2, random_state=42)

    # Sclaing
    scaler = StandardScaler()
    x_train = scaler.fit_transform(x_train)
    x_test = scaler.transform(x_test)

    # Save data as artifacts
    npy_save(x_train, x_train_ds.path)
    npy_save(y_train, y_train_ds.path)
    npy_save(x_test, x_test_ds.path)
    npy_save(y_test, y_test_ds.path)
    print("Data saved as artifacts")