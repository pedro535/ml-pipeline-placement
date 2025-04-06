from abc import ABC, abstractmethod

from server import NodeManager, DataManager


class PlacerInterface(ABC):
    """Abstract base class for pipeline placement strategies."""

    @abstractmethod
    def __init__(self, node_manager: NodeManager, data_manager: DataManager):
        pass

    @abstractmethod
    def place_pipelines(self):
        """Place pipelines on nodes using a specific strategy."""
        pass
