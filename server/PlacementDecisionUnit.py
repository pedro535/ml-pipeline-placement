from typing import Dict, List
import random
import json

from server import NodeManager


class PlacementDecisionUnit:
    
    def __init__(self, nmanager: NodeManager):
        self.nmanager = nmanager

    
    def get_placements(self, analyses: Dict) -> List:
        """
        Get placements for the submitted pipelines
        """
        nodes = self.nmanager.get_nodes()
        placements = []

        for pipeline_id, analysis in analyses.items():
            placement = {
                "pipeline_id": pipeline_id,
                "mapping": [(component, random.choice(list(nodes.keys()))) for component in analysis]
            }
            placements.append(placement)

        # print(json.dumps(placements, indent=4, default=str))
        return placements