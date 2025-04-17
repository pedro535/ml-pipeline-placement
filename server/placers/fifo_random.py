import random
from typing import Dict, List, Tuple, Set

from server.placers import PlacerInterface
from server.ml_pipeline import Pipeline, Component
from server import NodeManager, DataManager
from server.settings import SEED

random.seed(SEED)


class FifoRandomPlacer(PlacerInterface):

    def __init__(self, node_manager: NodeManager, data_manager: DataManager):
        self.node_manager = node_manager
        self.data_manager = data_manager
        self.assignments = None          # attr from DecisionUnit
        self.assignments_counts = None   # attr from DecisionUnit


    def add_assignment(self, node: str, pipeline_id: str, component: str):
        self.assignments[node].add(f"{pipeline_id}/{component}")
        self.assignments_counts[node] += 1


    def place_pipelines(
        self,
        pipelines: List[Pipeline],
        assignments: Dict[str, Set[str]],
        assignments_counts: Dict[str, int]
    ) -> List[Dict]:
        
        self.assignments = assignments
        self.assignments_counts = assignments_counts

        self.node_manager.update_nodes()
        placements = []
        for pipeline in pipelines:
            metadata = pipeline.get_metadata()
            mapping = {}
            for component in pipeline.get_components():
                node, platform = self.get_random_node(component, metadata)
                mapping[component.name] = (node, platform)
                self.add_assignment(node, pipeline.id, component.name)

            placements.append({
                "pipeline_id": pipeline.id,
                "mapping": mapping
            })
        
        return placements


    def get_random_node(self, component: Component, metadata: Dict) -> Tuple:
        dataset = metadata["dataset"]
        size = max(
            self.data_manager.size_in_memory(dataset, "original"),
            self.data_manager.size_in_memory(dataset, "preprocessed")
        )

        nodes = self.node_manager.get_nodes()
        random_node = random.choice(nodes)
        while not self.size_fits_in_node(size, random_node):
            random_node = random.choice(nodes)

        node_name = random_node["name"]
        node_platform = self.node_manager.get_node_platform(node_name)
        return node_name, node_platform


    def size_fits_in_node(self, size: int, node: Dict) -> bool:
        memory = node["memory"]
        memory_usage = node["memory_usage"]
        memory_free = memory - (memory * memory_usage)
        memory_required = size * 1.5
        return memory_free > memory_required