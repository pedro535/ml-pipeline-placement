from mlopx.artifacts import OutputDataset

def data_preprocessing(
    dataset_path: str,
    x_train_ds: OutputDataset,
    x_test_ds: OutputDataset,
    y_train_ds: OutputDataset,
    y_test_ds: OutputDataset
):

    import pandas as pd
    import numpy as np
    from sklearn.model_selection import train_test_split
    from sklearn.preprocessing import StandardScaler, LabelEncoder

    def npy_save(data, path):
        with open(path, "wb") as f:
            np.save(f, data)


    # Load dataset
    df = pd.read_csv(dataset_path)

    # Extract categorical and numerical columns
    categorical_cols = df.select_dtypes(include=['object']).columns
    categorical_cols = categorical_cols.drop('attack_cat')
    numeric_cols = df.select_dtypes(include=['float64', 'int64']).columns
    numeric_cols = numeric_cols.drop(labels=['id', 'label'])

    # Drop id column
    df = df.drop(columns=['id'])

    # Encode categorical variables
    for col in categorical_cols:
        if col in df.columns:
            label_encoder = LabelEncoder()
            df[col] = label_encoder.fit_transform(df[col])

    # Drop label column
    x = df.drop(['attack_cat', 'label'], axis=1)
    y = df['label']

    # Split the dataset
    x_train, x_test, y_train, y_test = train_test_split(
        x, y, test_size=0.2, random_state=42, stratify=y
    )

    # Apply standard scaling to numeric columns
    scaler = StandardScaler()
    x_train[numeric_cols] = scaler.fit_transform(x_train[numeric_cols])
    x_test[numeric_cols] = scaler.transform(x_test[numeric_cols])

    # Save data as artifacts
    npy_save(x_train, x_train_ds.path)
    npy_save(y_train, y_train_ds.path)
    npy_save(x_test, x_test_ds.path)
    npy_save(y_test, y_test_ds.path)
    print("Data saved as artifacts")