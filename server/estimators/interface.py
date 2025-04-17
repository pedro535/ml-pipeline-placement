from abc import ABC, abstractmethod


class EstimatorInterface(ABC):
    """Abstract base class for ML estimators."""

    @abstractmethod
    def estimate_train(self, params: dict) -> int:
        """Estimate the total number of operations for the training phase."""
        pass

    @abstractmethod
    def estimate_pred(self, params: dict) -> int:
        """Estimate the total number of operations for the prediction phase."""
        pass