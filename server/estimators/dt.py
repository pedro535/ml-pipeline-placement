import math
from typing import Dict, Any

from server.estimators import EstimatorInterface


class DecisionTree(EstimatorInterface):

    @staticmethod
    def estimate_train(params: Dict[str, Any]) -> int:
        """
        Estimate the training complexity of a decision tree.
        """
        n_samples = params["n_samples"]
        n_features = params["n_features"]
        complexity = n_features * n_samples * math.log2(n_samples)
        return int(complexity)


    @staticmethod
    def estimate_pred(params: Dict[str, Any]) -> int:
        """
        Estimate the prediction complexity of a decision tree.
        """
        n_samples = params["n_samples"]
        max_depth = params.get('max_depth', None)

        complexity = n_samples * max_depth or math.log2(n_samples)
        return int(complexity)