from typing import Dict, Any

from server.estimators import EstimatorInterface


class LogisticRegression(EstimatorInterface):

    @staticmethod
    def estimate_train(params: Dict[str, Any]) -> int:
        """
        Estimate the training complexity of logistic regression.
        """
        n_samples = params["n_samples"]
        n_features = params["n_features"]
        n_iter = params.get('n_iter', 100)
        complexity = n_samples * n_features * n_iter
        return complexity
    

    @staticmethod
    def estimate_pred(params: Dict[str, Any]) -> int:
        """
        Estimate the prediction complexity of logistic regression.
        """
        n_samples = params["n_samples"]
        n_features = params["n_features"]
        complexity = n_samples * n_features
        return complexity
