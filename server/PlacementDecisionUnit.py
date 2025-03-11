from typing import Dict

from server import NodeManager


class PlacementDecisionUnit:
    
    def __init__(self, nmanager: NodeManager):
        self.nmanager = nmanager

    
    def get_placement(self, analyses: Dict):
        print("Analyses:", analyses)