from server.estimators import (
    LinearRegression,
    LogisticRegression,
    DecisionTree,
    RandomForest,
    Svm,
    Nn,
    Cnn,
    Pca,
    Tsne
)

class MLEstimator:

    def __init__(self):
        self.estimators = {
            "linear_regression": LinearRegression,
            "logistic_regression": LogisticRegression,
            "decision_tree": DecisionTree,
            "random_forest": RandomForest,
            "svm": Svm,
            "nn": Nn,
            "cnn": Cnn,
            "pca": Pca,
            "tsne": Tsne
        }


    def estimate(self, algorithm, params, training=True):
        if algorithm not in self.estimators:
            raise ValueError(f"Unknown ML algorithm: {algorithm}")
        
        estimator = self.estimators[algorithm]
        if training:
            complexity = estimator.estimate_train(params)
        else:
            complexity = estimator.estimate_pred(params)
        return complexity
