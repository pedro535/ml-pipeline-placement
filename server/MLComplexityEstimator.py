import math


class MLComplexityEstimator:
    """
    Estimates the training and inference complexity of different ML algorithms.
    """

    def __init__(self):
        self._estimators = {
            "LINEAR_REGRESSION": self._estimate_linear_regression,
            "LOGISTIC_REGRESSION": self._estimate_logistic_regression,
            "DECISION_TREE": self._estimate_decision_tree,
            "RANDOM_FOREST": self._estimate_random_forest,
            "SVM": self._estimate_svm,
            "PCA": self._estimate_pca,
            "TSNE": self._estimate_tsne
        }
        self._global_mandatory_params = ["n_samples, n_features"]


    def estimate(self, algorithm, params):
        """
        Estimate the training and inference complexity of the given ML algorithm.
        """
        if algorithm in self._estimators:
            return self._estimators[algorithm](params)
        raise ValueError(f"Unknown ML algorithm: {algorithm}")
        

    def _estimate_linear_regression(self, params):
        """
        Estimates the training and inference complexity of linear regression.
        """
        n_samples = params["n_samples"]
        n_features = params["n_features"]
        solver = params["solver"]

        if solver == 'normal_equation':
            train_complexity = n_samples * n_features**2 + n_features**3
        elif solver == 'gradient_descent':
            n_iter = params.get('n_iter', 1000)  # sklearn default
            train_complexity = n_iter * n_samples * n_features
        else:
            raise ValueError(f"Unknown solver for linear regression: {solver}")
        
        inference_complexity = n_features
        return train_complexity, inference_complexity


    def _estimate_logistic_regression(self, params):
        """
        Estimates the training and inference complexity of logistic regression.
        """
        n_samples = params["n_samples"]
        n_features = params["n_features"]
        n_classes = params["n_classes"]
        n_iter = params.get('n_iter', 100)  # sklearn default

        train_complexity = n_samples * n_features * n_iter * n_classes
        inference_complexity = n_features * n_classes
        return train_complexity, inference_complexity


    def _estimate_decision_tree(self, params):
        """
        Estimates the training and inference complexity of decision tree.
        """
        n_samples = params["n_samples"]
        n_features = params["n_features"]
        max_depth = params.get('max_depth', None)

        train_complexity = n_features * n_samples * (max_depth or math.log2(n_samples))
        inference_complexity = max_depth or math.log2(n_samples)
        return train_complexity, inference_complexity


    def _estimate_random_forest(self, params):
        """
        Estimates the training and inference complexity of random forest.
        """
        n_samples = params["n_samples"]
        n_features = params["n_features"]
        n_estimators = params.get('n_estimators', 100)  # sklearn default
        max_depth = params.get('max_depth', None)

        train_complexity = n_estimators * n_features * n_samples * (max_depth or math.log2(n_samples))
        inference_complexity = n_estimators * (max_depth or math.log2(n_samples))
        return train_complexity, inference_complexity


    def _estimate_svm(self, params):
        """
        Estimates the training and inference complexity of SVM.
        """
        n_samples = params["n_samples"]
        n_features = params["n_features"]
        kernel = params.get('kernel', 'linear')
        n_iter = params.get('n_iter', 100)
        support_vectors = params.get('support_vectors', n_samples)  # if not provided, worst case is n_samples

        if kernel == 'linear':
            train_complexity = n_samples * n_features * n_iter
            inference_complexity = n_features
        else:
            train_complexity = n_samples**2 * n_features * n_iter
            inference_complexity = support_vectors * n_features
        
        return train_complexity, inference_complexity
        

    def _estimate_pca(self, params):
        """"
        Estimates the complexity of PCA.
        """
        n_samples = params["n_samples"]
        n_features = params["n_features"]

        complexity = n_samples * n_features**2 + n_features**3
        return complexity, None


    def _estimate_tsne(self, params):
        """
        Estimates the complexity of t-SNE.
        """
        n_samples = params["n_samples"]
        n_features = params["n_features"]

        complexity = n_samples**2 * n_features
        return complexity, None
