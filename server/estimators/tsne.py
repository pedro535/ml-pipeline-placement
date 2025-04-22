from typing import Dict, Any

from server.estimators import EstimatorInterface


class Tsne(EstimatorInterface):

    @staticmethod
    def estimate_train(params: Dict[str, Any]):
        """
        Estimate the training complexity of a t-SNE model.
        """
        n_samples = params["n_samples"]
        n_features = params["n_features"]
        complexity = n_samples**2 * n_features
        return complexity, None
    

    @staticmethod
    def estimate_pred(params):
        return None