from typing import Dict
import random
import json

from server import NodeManager


class PlacementDecisionUnit:
    
    def __init__(self, nmanager: NodeManager):
        self.nmanager = nmanager

    
    def get_placement(self, analyses: Dict):
        """
        Get placement for the pipeline components
        """
        nodes = self.nmanager.get_nodes()
        placement = {}

        for pipeline_id, analysis in analyses.items():
            placement[pipeline_id] = {}
            for component in analysis:
                placement[pipeline_id][component] = random.choice(list(nodes.keys()))

        return placement