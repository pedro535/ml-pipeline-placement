from server.estimators import EstimatorInterface


class LogisticRegression(EstimatorInterface):

    @staticmethod
    def estimate_train(params):
        n_samples = params["n_samples"]
        n_features = params["n_features"]
        n_classes = params["n_classes"]
        n_iter = params.get('n_iter', 100)

        # complexity = n_samples * n_features * n_iter * n_classes
        complexity = n_samples * n_features * n_iter
        return complexity
    

    @staticmethod
    def estimate_pred(params):
        n_samples = params["n_samples"]
        n_features = params["n_features"]
        n_classes = params["n_classes"]

        # complexity = n_samples * n_features * n_classes
        complexity = n_samples * n_features * n_classes
        return complexity
