from typing import Dict, List, Tuple
import json

from server import NodeManager, DataManager, MLEstimator


class DecisionUnit:
    
    def __init__(self, node_manager: NodeManager, data_manager: DataManager):
        self.node_manager = node_manager
        self.data_manager = data_manager
        self.estimator = MLEstimator()
        self.assignments = {}
        self.assignments_counts = {}
        self.init_assignments()

        self.effort_calculators = {
            "preprocessing": self.preprocessing_effort,
            "training": self.training_effort,
            "evaluation": self.evaluation_effort
        }

        self.placement_strategies = {
            "preprocessing": self.preprocessing_node,
            "training": self.training_node,
            "evaluation": self.evaluation_node
        }


    def init_assignments(self):
        """
        Initialize assignments and counts for each node.
        """
        self.node_manager.update_nodes()
        for node in self.node_manager.get_nodes():
            name = node["name"]
            self.assignments[name] = set()
            self.assignments_counts[name] = 0

    
    def add_assignment(self, node: str, pipeline_id: str, component: str):
        """
        Add a new assignment to a node.
        """
        self.assignments[node].add(f"{pipeline_id}/{component}")
        self.assignments_counts[node] += 1

    
    def rm_assignment(self, node: str, pipeline_id: str, component: str):
        """
        Remove an assignment from a node.
        """
        self.assignments[node].remove(f"{pipeline_id}/{component}")
        self.assignments_counts[node] -= 1

    
    def less_overloaded_node(self, nodes: List[Dict]) -> Dict:
        """
        From the list of nodes, return the one with less components assigned.
        """
        overload = [(node, self.assignments_counts[node["name"]]) for node in nodes]
        overload = sorted(overload, key=lambda x: x[1])
        return overload[0][0]


    def get_placements(self, pipelines: List[Tuple[str, List]], pipelines_metadata: Dict) -> List[Dict]:
        
        # Calculate comp. effort for each pipeline and its components
        efforts = self.get_efforts(pipelines, pipelines_metadata)

        # Scheduling: SJF
        run_order = [(pipeline_id, efforts["total"]) for pipeline_id, efforts in efforts.items()]
        run_order = sorted(run_order, key=lambda x: x[1])

        # Placement
        self.node_manager.update_nodes()
        placements = []
        for pipeline_id, _ in run_order:
            metadata = pipelines_metadata[pipeline_id]
            components_type = metadata["components_type"]
            pipeline_efforts = efforts[pipeline_id]
            mapping = {}
            
            for component, c_type in components_type.items():
                if c_type in self.placement_strategies:
                    node, platform = self.placement_strategies[c_type](metadata, pipeline_efforts[component])
                    mapping[component] = (node, platform)
                    self.add_assignment(node, pipeline_id, component)
                else:
                    print(f"Unknown component type: {c_type}")
            
            placements.append({
                "pipeline_id": pipeline_id,
                "mapping": mapping,
                "efforts": efforts[pipeline_id]
            })
        
        return placements


    def get_efforts(self, pipelines: List[Tuple], pipelines_metadata: Dict) -> Dict:
        efforts = {}
        
        for pipeline_id, components in pipelines:
            metadata = pipelines_metadata[pipeline_id]
            
            pipeline_efforts = {}
            total_effort = 0
            for component in components:
                component_effort = self.calculate_effort(component, metadata)
                pipeline_efforts[component] = component_effort
                total_effort += component_effort
                
            pipeline_efforts["total"] = total_effort
            efforts[pipeline_id] = pipeline_efforts
            
        return efforts


    def calculate_effort(self, component: str, metadata: Dict) -> int:
        component_type = metadata["components_type"][component]
        
        if component_type in self.effort_calculators:
            return self.effort_calculators[component_type](metadata)
        else:
            print(f"Unknown component type: {component_type}")
            return 0


    def preprocessing_effort(self, metadata: Dict) -> int:
        n_samples = metadata["dataset"]["original"]["n_samples"]
        
        # Calculate the number of features based on dataset type
        if metadata["dataset"]["type"] == "tabular":
            n_features = metadata["dataset"]["original"]["n_features"]
        elif metadata["dataset"]["type"] == "image":
            shape = metadata["dataset"]["original"]["input_shape"]
            n_features = shape[0] * shape[1] * shape[2]
        else:
            n_features = 1
            
        # Simple effort model: samples × features
        effort = n_samples * n_features
        return effort


    def training_effort(self, metadata: Dict) -> int:
        return self.estimate_model_effort(
            metadata, 
            metadata["dataset"]["train_percentage"], 
            training=True
        )


    def evaluation_effort(self, metadata: Dict) -> int:
        return self.estimate_model_effort(
            metadata, 
            metadata["dataset"]["test_percentage"], 
            training=False
        )
    

    def estimate_model_effort(self, metadata: Dict, data_percentage: float, training: bool) -> int:
        model = metadata["model"]["type"]
        estimator_params = {}
        
        # Pass model parameters to estimator
        estimator_params.update(metadata["model"]["params"])
        
        # Pass dataset details to estimator
        for key, value in metadata["dataset"]["preprocessed"].items():
            if key == "n_samples":
                estimator_params[key] = int(value * data_percentage)
            elif key == "input_shape":
                weight, height, channels = value
                estimator_params["n_features"] = int(weight * height * channels * data_percentage)
            else:
                estimator_params[key] = value
                
        return self.estimator.estimate(model, estimator_params, training=training)


    def preprocessing_node(self, metadata: Dict, effort: int) -> Tuple[str, str]:
        dataset = metadata["dataset"]
        size = self.data_manager.size_in_memory(dataset)
        nodes = self.node_manager.get_nodes(node_types=["low", "med"], sort_params=["memory"])  # TODO: put types as constants

        candidates = []
        for node in nodes:
            memory = node["memory"]
            memory_usage = node["memory_usage"]
            memory_free = memory - (memory * memory_usage)
            memory_required = size * 1.5
            
            if memory_free > memory_required:
                candidates.append(node)
            
        node = self.less_overloaded_node(candidates)
        return node["name"], node["architecture"]

    
    def training_node(self, metadata: Dict, effort: int) -> Tuple[str, str]:
        print(f"Get node for training component with effort {effort}")
        return None, None


    def evaluation_node(self, metadata: Dict, effort: int) -> Tuple[str, str]:
        print(f"Get node for evaluation component with effort {effort}")
        return None, None
        