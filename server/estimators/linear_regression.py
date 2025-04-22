from typing import Dict, Any

from server.estimators import EstimatorInterface


class LinearRegression(EstimatorInterface):

    @staticmethod
    def estimate_train(params: Dict[str, Any]) -> int:
        """
        Estimate the training complexity of linear regression.
        """
        n_samples = params["n_samples"]
        n_features = params["n_features"]
        solver = params.get("solver", "ols")
        n_iter = params.get('n_iter', 1000)

        if solver == 'ols':
            # Ordinary Least Squares (OLS)
            complexity = n_samples * n_features**2 + n_features**3
        elif solver == 'sgd':
            # Stochastic Gradient Descent (SGD)
            complexity = n_iter * n_samples * n_features
        else:
            raise ValueError(f"Unknown solver for linear regression: {solver}")
        
        return complexity
    

    @staticmethod
    def estimate_pred(params: Dict[str, Any]) -> int:
        """
        Estimate the prediction complexity of linear regression.
        """
        n_samples = params["n_samples"]
        n_features = params["n_features"]

        complexity = n_samples * n_features
        return complexity