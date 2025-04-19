from server.estimators import EstimatorInterface


class NN(EstimatorInterface):

    @staticmethod
    def estimate_train(params):
        n_samples = params["n_samples"]
        n_epochs = params["n_epochs"]
        n_parameters = params["n_parameters"]
        complexity = n_samples * n_parameters * n_epochs
        return complexity
    

    @staticmethod
    def estimate_pred(params):
        n_samples = params["n_samples"]
        n_parameters = params["n_parameters"]
        complexity = n_samples * n_parameters
        return complexity