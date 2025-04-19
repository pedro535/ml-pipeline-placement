import math

from server.estimators import EstimatorInterface


class RandomForest(EstimatorInterface):

    @staticmethod
    def estimate_train(params):
        n_samples = params["n_samples"]
        n_features = params["n_features"]
        n_estimators = params.get('n_estimators', 100)
        complexity = n_estimators * n_features * n_samples * int(math.log2(n_samples))
        return complexity


    @staticmethod
    def estimate_pred(params):
        n_samples = params["n_samples"]
        n_estimators = params.get('n_estimators', 100)
        max_depth = params.get('max_depth', None)
        complexity = n_samples * n_estimators * (max_depth or math.log2(n_samples))
        return complexity
