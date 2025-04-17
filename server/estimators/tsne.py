from server.estimators import EstimatorInterface


class TSNE(EstimatorInterface):

    @staticmethod
    def estimate_train(params):
        n_samples = params["n_samples"]
        n_features = params["n_features"]

        complexity = n_samples**2 * n_features
        return complexity, None
    

    @staticmethod
    def estimate_pred(params):
        return None