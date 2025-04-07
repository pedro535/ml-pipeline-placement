from typing import Dict, List, Tuple, Set

from server import PlacerInterface, NodeManager, DataManager, MLEstimator, Pipeline, Component


class CustomPlacer(PlacerInterface):

    def __init__(self, node_manager: NodeManager, data_manager: DataManager):
        self.node_manager = node_manager
        self.data_manager = data_manager
        self.estimator = MLEstimator()
        self.assignments = None          # attr from DecisionUnit
        self.assignments_counts = None   # attr from DecisionUnit

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

        # Calculate effort for each pipeline and its components
        efforts = self.get_efforts(pipelines)

        # Scheduling: SJF
        run_order = [(pipeline_id, efforts["total"]) for pipeline_id, efforts in efforts.items()]
        run_order = sorted(run_order, key=lambda x: x[1])

        # Placement
        self.node_manager.update_nodes()
        pipelines_dict = {pipeline.id: pipeline for pipeline in pipelines}
        placements = []
        
        for pipeline_id, _ in run_order:
            pipeline = pipelines_dict[pipeline_id]
            metadata = pipeline.get_metadata()
            mapping = {}

            for component in pipeline.get_components():
                if component.type in self.placement_strategies:
                    strategy_fn = self.placement_strategies[component.type]
                    node, platform = strategy_fn(pipeline_id, metadata)
                    mapping[component.name] = (node, platform)
                    self.add_assignment(node, pipeline_id, component.name)
                else:
                    print(f"Unknown component type: {component.type}")
            
            placements.append({
                "pipeline_id": pipeline_id,
                "mapping": mapping,
                "efforts": efforts[pipeline_id]
            })
        
        return placements


    def get_efforts(self, pipelines: List[Pipeline]) -> Dict[str, Dict]:
        efforts = {}
        
        for pipeline in pipelines:
            metadata = pipeline.get_metadata()
            pipeline_efforts = {}
            total_effort = 0

            for component in pipeline.get_components():
                effort = self.component_effort(component, metadata)
                pipeline_efforts[component.name] = effort
                total_effort += effort
                
            pipeline_efforts["total"] = total_effort
            efforts[pipeline.id] = pipeline_efforts
            
        return efforts


    def component_effort(self, component: Component, metadata: Dict) -> int:
        if component.type in self.effort_calculators:
            return self.effort_calculators[component.type](metadata)
        else:
            print(f"Unknown component type: {component.type}")
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


    def choose_node(self, candidates: List[Dict], pipeline_id: str) -> Dict:
        # Check if the pipeline already has an assignment(s)
        nodes = []
        for node, components in self.assignments.items():
            pipelines = [c.split("/")[0] for c in components]
            if pipeline_id in pipelines:
                nodes.append(node)

        if not nodes and not candidates:
            return self.fallback_node()

        common_nodes = [c for c in candidates if c["name"] in nodes]
        candidates = common_nodes if common_nodes else candidates

        overload = [(node, self.assignments_counts[node["name"]]) for node in candidates]
        overload = sorted(overload, key=lambda x: x[1])
        return overload[0][0]
    
    
    def preprocessing_node(self, pipeline_id: str, metadata: Dict) -> Tuple[str, str]:
        dataset = metadata["dataset"]
        size = max(
            self.data_manager.size_in_memory(dataset, "original"),
            self.data_manager.size_in_memory(dataset, "preprocessed")
        )

        candidates = self.node_manager.get_nodes(node_types=["low", "med"], sort_params=["memory"])
        candidates = [node for node in candidates if self.size_fits_in_node(size, node)]
        node = self.choose_node(candidates, pipeline_id)
        return node["name"], node["architecture"]

    
    def training_node(self, pipeline_id: str, metadata: Dict) -> Tuple[str, str]:
        # Dataset
        dataset = metadata["dataset"]
        size = self.data_manager.size_in_memory(dataset, "preprocessed")
        size = int(size * metadata["dataset"]["train_percentage"])

        # Model
        model = metadata["model"]["type"]
        if model in ["logistic_regression", "linear_regression", "decision_tree"]:
            node_types = ["low", "med"]
        elif model in ["random_forest", "svm"]:
            node_types = ["med"]
        elif model in ["nn", "cnn"]:
            node_types = ["high-cpu"]
        else:
            print(f"Unknown model type: {model}")
            node_types = ["med"]

        # Get nodes
        candidates = self.node_manager.get_nodes(node_types=node_types, sort_params=["cpu_cores", "memory"])
        candidates = [node for node in candidates if self.size_fits_in_node(size, node)]
        node = self.choose_node(candidates, pipeline_id)
        return node["name"], node["architecture"]


    def evaluation_node(self, pipeline_id: str, metadata: Dict) -> Tuple[str, str]:
        # Dataset
        dataset = metadata["dataset"]
        size = self.data_manager.size_in_memory(dataset, "preprocessed")
        size = int(size * metadata["dataset"]["test_percentage"])

        # Model
        model = metadata["model"]["type"]
        if model in ["logistic_regression", "linear_regression", "decision_tree"]:
            node_types = ["low", "med"]
        elif model in ["random_forest", "svm"]:
            node_types = ["low", "med"]
        elif model in ["nn", "cnn"]:
            node_types = ["med", "high-cpu"]
        else:
            print(f"Unknown model type: {model}")
            node_types = ["med"]

        # Get nodes
        candidates = self.node_manager.get_nodes(node_types=node_types, sort_params=["cpu_cores", "memory"])
        candidates = [node for node in candidates if self.size_fits_in_node(size, node)]
        node = self.choose_node(candidates, pipeline_id)
        return node["name"], node["architecture"]
    
    
    def size_fits_in_node(self, size: int, node: Dict) -> bool:
        memory = node["memory"]
        memory_usage = node["memory_usage"]
        memory_free = memory - (memory * memory_usage)
        memory_required = size * 1.5
        return memory_free > memory_required
    

    def fallback_node(self) -> Dict:
        # Fallback to high-cpu nodes
        nodes = self.node_manager.get_nodes(node_types=["high-cpu"], sort_params=["cpu_cores", "memory"])
        overload = [(node, self.assignments_counts[node["name"]]) for node in nodes]
        overload = sorted(overload, key=lambda x: x[1])
        return overload[0][0]