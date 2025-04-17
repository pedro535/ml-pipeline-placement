from typing import Dict, List

from server.settings import PLACER
from server.ml_pipeline import Pipeline
from server import NodeManager, DataManager
from server.placers import (
    PlacerInterface,
    CustomPlacer,
    FifoRandomPlacer,
    FifoRoundRobinPlacer,
    FifoGreedyPlacer,
    RandomRandomPlacer
)


placers = {
    "custom": CustomPlacer,
    "fifo_random": FifoRandomPlacer,
    "fifo_round_robin": FifoRoundRobinPlacer,
    "fifo_greedy": FifoGreedyPlacer,
    "random_random": RandomRandomPlacer,
}


class DecisionUnit:
    
    def __init__(self, node_manager: NodeManager, data_manager: DataManager):
        self.node_manager = node_manager
        self.data_manager = data_manager
        self.placer: PlacerInterface = placers[PLACER](node_manager, data_manager)
        self.assignments = {}         # controlled by the placer
        self.assignments_counts = {}  # controlled by the placer
        self.init_assignments()


    def init_assignments(self):
        self.node_manager.update_nodes()
        for node in self.node_manager.get_nodes():
            name = node["name"]
            self.assignments[name] = set()
            self.assignments_counts[name] = 0

    
    def rm_assignment(self, node: str, pipeline_id: str, component: str):
        component_id = f"{pipeline_id}/{component}"
        if component_id in self.assignments[node]:
            self.assignments[node].remove(component_id)
            self.assignments_counts[node] -= 1


    def is_node_needed(self, node: str, pipeline_id: str) -> bool:
        for pipeline in self.assignments[node]:
            if pipeline.split("/")[0] == pipeline_id:
                return True
        return False


    def get_placements(self, pipelines: List[Pipeline]) -> List[Dict]:
        placements = self.placer.place_pipelines(
            pipelines, self.assignments, self.assignments_counts
        )
        
        return placements