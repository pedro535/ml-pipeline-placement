from typing import Dict, Any

from server.estimators import EstimatorInterface


class Svm(EstimatorInterface):

    @staticmethod
    def estimate_train(params: Dict[str, Any]) -> int:
        """
        Estimate the training complexity of a Support Vector Machine model.
        """
        n_samples = params["n_samples"]
        n_features = params["n_features"]
        kernel = params.get('kernel', 'linear')
        n_iter = params.get('n_iter', 100)

        if kernel == 'linear':
            complexity = n_samples * n_features * n_iter
        else:
            complexity = n_samples**2 * n_features * n_iter
        
        return complexity


    @staticmethod
    def estimate_pred(params: Dict[str, Any]) -> int:
        """
        Estimate the prediction complexity of a Support Vector Machine model.
        """
        n_samples = params["n_samples"]
        n_features = params["n_features"]
        kernel = params.get('kernel', 'linear')
        support_vectors = params.get('support_vectors', n_samples)  # if not provided, worst case is n_samples

        if kernel == 'linear':
            complexity = n_samples * n_features
        else:
            complexity = n_samples * support_vectors * n_features
        
        return complexity