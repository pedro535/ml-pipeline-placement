import math


class MLEstimator:

    def __init__(self):
        self.estimators = {
            "linear_regression": (self.linr_train, self.linr_pred),
            "logistic_regression": (self.lr_train, self.lr_pred),
            "decision_tree": (self.dt_train, self.dt_pred),
            "random_forest": (self.rf_train, self.rf_pred),
            "svm": (self.svm_train, self.svm_pred),
            "nn": (self.nn_train, self.nn_pred),
            "cnn": (self.cnn_train, self.cnn_pred),
            "pca": (self.pca, None),
            "tsne": (self.tsne, None)
        }


    def estimate(self, algorithm, params, training=True):
        if algorithm not in self.estimators:
            raise ValueError(f"Unknown ML algorithm: {algorithm}")
        
        train_est, pred_est = self.estimators[algorithm]
        if training:
            complexity = train_est(params)
        elif pred_est is not None:
            complexity = pred_est(params)
        return complexity
        

    def linr_train(self, params):
        n_samples = params["n_samples"]
        n_features = params["n_features"]
        solver = params.get("solver", "ols")

        if solver == 'ols':
            # Ordinary Least Squares (OLS)
            complexity = n_samples * n_features**2 + n_features**3
        elif solver == 'sgd':
            # Stochastic Gradient Descent (SGD)
            n_iter = params.get('n_iter', 1000)
            complexity = n_iter * n_samples * n_features
        else:
            raise ValueError(f"Unknown solver for linear regression: {solver}")
        
        return complexity
    

    def linr_pred(self, params):
        n_samples = params["n_samples"]
        n_features = params["n_features"]

        complexity = n_samples * n_features
        return complexity


    def lr_train(self, params):
        n_samples = params["n_samples"]
        n_features = params["n_features"]
        n_classes = params["n_classes"]
        n_iter = params.get('n_iter', 100)

        complexity = n_samples * n_features * n_iter * n_classes
        return complexity
    

    def lr_pred(self, params):
        n_samples = params["n_samples"]
        n_features = params["n_features"]
        n_classes = params["n_classes"]

        complexity = n_samples * n_features * n_classes
        return complexity


    def dt_train(self, params):
        n_samples = params["n_samples"]
        n_features = params["n_features"]
        max_depth = params.get('max_depth', None)

        complexity = n_features * n_samples * (max_depth or math.log2(n_samples))
        return complexity
    

    def dt_pred(self, params):
        n_samples = params["n_samples"]
        max_depth = params.get('max_depth', None)

        complexity = n_samples * max_depth or math.log2(n_samples)
        return complexity


    def rf_train(self, params):
        n_samples = params["n_samples"]
        n_features = params["n_features"]
        n_estimators = params.get('n_estimators', 100)
        max_depth = params.get('max_depth', None)

        complexity = n_estimators * n_features * n_samples * (max_depth or math.log2(n_samples))
        return complexity
    

    def rf_pred(self, params):
        n_samples = params["n_samples"]
        n_estimators = params.get('n_estimators', 100)
        max_depth = params.get('max_depth', None)

        complexity = n_samples * n_estimators * (max_depth or math.log2(n_samples))
        return complexity


    def svm_train(self, params):
        n_samples = params["n_samples"]
        n_features = params["n_features"]
        kernel = params.get('kernel', 'linear')
        n_iter = params.get('n_iter', 100)

        if kernel == 'linear':
            complexity = n_samples * n_features * n_iter
        else:
            complexity = n_samples**2 * n_features * n_iter
        
        return complexity
    

    def svm_pred(self, params):
        n_samples = params["n_samples"]
        n_features = params["n_features"]
        kernel = params.get('kernel', 'linear')
        support_vectors = params.get('support_vectors', n_samples)  # if not provided, worst case is n_samples

        if kernel == 'linear':
            complexity = n_samples * n_features
        else:
            complexity = n_samples * support_vectors * n_features
        
        return complexity
    

    def nn_train(self, params):
        n_samples = params["n_samples"]
        n_epochs = params["n_epochs"]
        n_parameters = params["n_parameters"]

        # Assuming a simple feedforward neural network
        complexity = n_samples * n_parameters * n_epochs
        return complexity
    

    def nn_pred(self, params):
        n_samples = params["n_samples"]
        n_parameters = params["n_parameters"]

        # Assuming a simple feedforward neural network
        complexity = n_samples * n_parameters
        return complexity
    

    def cnn_train(self, params):
        n_samples = params["n_samples"]
        n_epochs = params["n_epochs"]
        n_parameters = params["n_parameters"]

        # TODO: Enhance this with actual CNN complexity estimation
        complexity = n_samples * n_parameters * n_epochs
        return complexity
    

    def cnn_pred(self, params):
        n_samples = params["n_samples"]
        n_parameters = params["n_parameters"]

        # TODO: Enhance this with actual CNN complexity estimation
        complexity = n_samples * n_parameters
        return complexity

        
    def pca(self, params):

        n_samples = params["n_samples"]
        n_features = params["n_features"]

        complexity = n_samples * n_features**2 + n_features**3
        return complexity, None


    def tsne(self, params):
        n_samples = params["n_samples"]
        n_features = params["n_features"]

        complexity = n_samples**2 * n_features
        return complexity, None