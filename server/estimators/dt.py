import math

from server.estimators import EstimatorInterface


class DecisionTree(EstimatorInterface):

    @staticmethod
    def estimate_train(params):
        n_samples = params["n_samples"]
        n_features = params["n_features"]
        max_depth = params.get('max_depth', None)

        # complexity = n_features * n_samples * (max_depth or math.log2(n_samples))
        complexity = n_features * n_samples * int(math.log2(n_samples))
        return complexity


    @staticmethod
    def estimate_pred(params):
        n_samples = params["n_samples"]
        max_depth = params.get('max_depth', None)

        complexity = n_samples * max_depth or math.log2(n_samples)
        return complexity