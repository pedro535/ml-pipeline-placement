from server.estimators import EstimatorInterface


class PCA(EstimatorInterface):

    @staticmethod
    def estimate_train(params):
        n_samples = params["n_samples"]
        n_features = params["n_features"]

        complexity = n_samples * n_features**2 + n_features**3
        return complexity, None
    

    @staticmethod
    def estimate_pred(params):
        return None