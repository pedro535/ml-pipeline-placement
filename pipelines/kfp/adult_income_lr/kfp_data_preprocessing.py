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
    import numpy as np
    import pandas as pd
    from sklearn.model_selection import train_test_split
    from sklearn.preprocessing import LabelEncoder, StandardScaler
    from imblearn.over_sampling import SMOTE

    def npy_save(data, path):
        with open(path, "wb") as f:
            np.save(f, data)

    def outliers_handler(df, col):
        q1 = df[col].quantile(0.25)
        q3 = df[col].quantile(0.75)
        iqr = q3 - q1
        lower_limit = q1 - 1.5 * iqr
        upper_limit = q3 + 1.5 * iqr
        df[col] = df[col].clip(lower=lower_limit, upper=upper_limit)
        return df

    df = pd.read_csv(dataset_path)
    columns_with_question_marks = []
    for column in df.columns:
        if df[column].isin(["?"]).any():
            columns_with_question_marks.append(column)
    print("Columns with question marks:", columns_with_question_marks)
    df[columns_with_question_marks] = df[columns_with_question_marks].replace(
        "?", np.nan
    )
    print("shape of data before drop duplicate", df.shape)
    df = df.drop_duplicates()
    print("shape of data after drop duplicate", df.shape)
    numeric_cols = df.select_dtypes(include=["float64", "int64"]).columns
    for i in numeric_cols:
        df = outliers_handler(df, i)
    le = LabelEncoder()
    workclass_mapping = {
        "Private": "private",
        "Self-emp-not-inc": "self-employed",
        "Local-gov": "government",
        "State-gov": "government",
        "Self-emp-inc": "self-employed",
        "Federal-gov": "government",
        "Without-pay": "other",
        "Never-worked": "other",
    }
    df["workclass"] = df["workclass"].map(workclass_mapping)
    df["workclass"] = le.fit_transform(df["workclass"])
    education_mapping = {
        "HS-grad": "learning",
        "Some-college": "learning",
        "Bachelors ": "graduate",
        "Masters": "graduate",
        "Assoc-voc": "assoc",
        "11th": "child",
        "Assoc-acdm": "assoc",
        "10th": "child",
        "7th-8th": "child",
        "Prof-school": "graduate",
        "9th": "child",
        "12th": "child",
        "Doctorate": "gruduate",
        "5th-6th ": "child",
        "1st-4th  ": "child",
        "Preschool": "child",
    }
    df["education"] = df["education"].map(education_mapping)
    df["education"] = le.fit_transform(df["education"])
    marital_status_mapping = {
        "Married-civ-spouse": "married",
        "Never-married": "single",
        "Divorced": "single",
        "Separated": "single",
        "Widowed": "single",
        "Married-spouse-absent": "married",
        "Married-AF-spouse": "married",
    }
    df["marital-status"] = df["marital-status"].map(marital_status_mapping)
    df["marital-status"] = le.fit_transform(df["marital-status"])
    occupation_mapping = {
        "Prof-specialty": "professional and executive",
        "Craft-repair": "labor and manufacturing",
        "Exec-managerial": "professional and executive",
        "Adm-clerical": "professional and executive",
        "Sales": "sales and services",
        "Other-service": "sales and services",
        "Machine-op-inspct": "labor and manufacturing",
        "Transport-moving": "labor and manufacturing",
        "Handlers-cleaners": "labor and manufacturing",
        "Farming-fishing ": "labor and manufacturing",
        "Tech-suppor": "sales and services",
        "Protective-serv": "sales and services",
        "Priv-house-serv": "sales and services",
        "Armed-Forces ": "sales and services",
    }
    df["occupation"] = df["occupation"].map(occupation_mapping)
    df["occupation"] = le.fit_transform(df["occupation"])
    relationship_mapping = {
        "Husband": "spouse",
        "Not-in-family": "others:",
        "Own-child": "immediate family",
        "Unmarried": "others:",
        "Wife": "spouse",
        "Other-relative": "immediate family",
    }
    df["relationship"] = df["relationship"].map(relationship_mapping)
    df["relationship"] = le.fit_transform(df["relationship"])
    df["race"] = df["race"].map(lambda x: "White" if x == "White" else "Other")
    df["race"] = le.fit_transform(df["race"])
    df["gender"] = le.fit_transform(df["gender"])
    df["native-country"] = df["native-country"].map(
        lambda x: "United-States" if x == "United-States" else "Other"
    )
    df["native-country"] = le.fit_transform(df["native-country"])
    df["income"] = le.fit_transform(df["income"])
    df.drop(["capital-gain", "capital-loss"], axis=1, inplace=True)
    x = df.drop(columns=["income"])
    y = df["income"]
    resampler = SMOTE()
    x, y = resampler.fit_resample(x, y)
    x_train, x_test, y_train, y_test = train_test_split(
        x, y, test_size=0.2, random_state=42
    )
    scaler = StandardScaler()
    x_train = scaler.fit_transform(x_train)
    x_test = scaler.transform(x_test)
    npy_save(x_train, x_train_ds.path)
    npy_save(y_train, y_train_ds.path)
    npy_save(x_test, x_test_ds.path)
    npy_save(y_test, y_test_ds.path)
    print("Data saved as artifacts")
