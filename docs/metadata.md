# Metadata file

# General structure

```json
{
    "components_type": {
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
    "components_type": {...},
    "dataset": {...},
    "model" : {
        "type" : "linear_regression",
        "params" : {
            "solver" : "ols"
        }
    }
}
```

Linear model with SGD (Stochastic Gradient Descent)

```json
{
    "components_type": {...},
    "dataset": {...},
    "model" : {
        "type" : "linear_regression",
        "params" : {
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
    "components_type": {...},
    "dataset": {...},
    "model" : {
        "type" : "logistic_regression",
        "params" : {
            "n_iter" : 1
        }
    }
}
```

### Decision tree

```json
{
    "components_type": {...},
    "dataset": {...},
    "model" : {
        "type" : "decision_tree",
        "params" : {
            "max_depth" : "int | null"
        }
    }
}
```

### Random forest

```json
{
    "components_type": {...},
    "dataset": {...},
    "model" : {
        "type" : "random_forest",
        "params" : {
            "n_estimators" : 123,
            "max_depth" : "int | null"
        }
    }
}
```

### SVM

```json
{
    "components_type": {...},
    "dataset": {...},
    "model" : {
        "type" : "svm",
        "params" : {
            "kernel" : "linear | nonlinear",
            "n_iter" : 123,
            "n_support_vectors" : 123
        }
    }
}
```

### NN

The `layers` are the output of `mlopx.utils.ModelDetails.tf_dnn_layers`.

```json
{
    "components_type": {...},
    "dataset": {...},
    "model" : {
        "type" : "nn",
        "params" : {
            "n_epochs" : 123,
            "batch_size" : 123,
            "layers": [...]
        }
    }
}
```

### CNN

The `layers` are the output of `mlopx.utils.ModelDetails.tf_dnn_layers`.

```json
{
    "components_type": {...},
    "dataset": {...},
    "model" : {
        "type" : "cnn",
        "params" : {
            "n_epochs" : 123,
            "batch_size" : 123,
            "layers": [...]
        }
    }
}
```

### Other

```json
{
    "components_type": {...},
    "dataset": {...},
    "model" : {
        "type" : "other",
        "params" : {}
    }
}
```