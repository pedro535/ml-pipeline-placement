# Metadata file

# General structure

```json
{
    "components": {
        "my_component_1": "preprocessing | training| evaluation",
        "my_component_2": "preprocessing | training | evaluation",
        "my_component_3": "preprocessing | training | evaluation"
    },
    "dataset": {
        "name": "dataset_folder_name",
        "type": "tabular | image",
        "train_percentage": 0.8,
        "val_percentage": 0.1,
        "test_percentage": 0.1,
        "original": {
            "n_samples": 48842,
            "n_features": 14,
            "n_classes": 2
        },
        "preprocessed": {
            "n_samples": 48842,
            "n_features": 14,
            "n_classes": 2
        }
    },
    "model": {
        ...
    }
}
```

## ML models

### Linear regression

Linear model using OLS (Ordinary Least Squares)


```json
{
    "components": {...},
    "dataset": {...},
    "model" : {
        "type" : "linear_regression",
        "parameters" : {
            "solver" : "ols"
        }
    }
}
```

Linear model with SGD (Stochastic Gradient Descent)

```json
{
    "components": {...},
    "dataset": {...},
    "model" : {
        "type" : "linear_regression",
        "parameters" : {
            "solver" : "sgd",
            "n_iter" : 1,
        }
    }
}
```

### Logistic regression

The complexity estimator assumes the model is using OvR for multiclass classification.

```json
{
    "components": {...},
    "dataset": {...},
    "model" : {
        "type" : "logistic_regression",
        "parameters" : {
            "n_iter" : 1
        }
    }
}
```

### Decision tree

```json
{
    "components": {...},
    "dataset": {...},
    "model" : {
        "type" : "decision_tree",
        "parameters" : {
            "max_depth" : "int | null"
        }
    }
}
```

### Random forest

```json
{
    "components": {...},
    "dataset": {...},
    "model" : {
        "type" : "random_forest",
        "parameters" : {
            "n_estimators" : 123,
            "max_depth" : "int | null"
        }
    }
}
```

### SVM

```json
{
    "components": {...},
    "dataset": {...},
    "model" : {
        "type" : "svm",
        "parameters" : {
            "kernel" : "linear | nonlinear",
            "n_iter" : 123,
            "n_support_vectors" : 123
        }
    }
}
```

### NN

```json
{
    "components": {...},
    "dataset": {...},
    "model" : {
        "type" : "nn",
        "parameters" : {
            "n_parameters" : 123,
            "n_epochs" : 123,
            "batch_size" : 123
        }
    }
}
```

### CNN

```json
{
    "components": {...},
    "dataset": {...},
    "model" : {
        "type" : "cnn",
        "parameters" : {
            "n_parameters" : 123,
            "n_epochs" : 123,
            "batch_size" : 123
        }
    }
}
```

### Other

```json
{
    "components": {...},
    "dataset": {...},
    "model" : {
        "type" : "other",
        "parameters" : {}
    }
}
```