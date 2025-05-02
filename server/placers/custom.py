import json
from typing import Dict, List, Tuple, Set

from server.placers import PlacerInterface
from server.ml_pipeline import Pipeline, Component
from server.components import NodeManager, DataManager, MLEstimator


class CustomPlacer(PlacerInterface):

    def __init__(self, node_manager: NodeManager, data_manager: DataManager):
        self.node_manager = node_manager
        self.data_manager = data_manager
        self.estimator = MLEstimator()
        self.assignments = None          # attr from DecisionUnit
        self.assignments_counts = None   # attr from DecisionUnit
        self.accelerator_score = 3

        with open("placers/custom_heuristics.json", "r") as f:
            self.heuristics = json.load(f)

        self.effort_calculators = {
            "preprocessing": self._calc_preprocessing_effort,
            "training": self._calc_training_effort,
            "evaluation": self._calc_evaluation_effort
        }

        self.node_selectors = {
            "preprocessing": self._select_preprocessing_node,
            "training": self._select_training_node,
            "evaluation": self._select_evaluation_node
        }


    def place_pipelines(
        self,
        pipelines: List[Pipeline],
        assignments: Dict[str, Set[str]],
        assignments_counts: Dict[str, int]
    ) -> List[Dict]:
        """
        Place pipelines on nodes based on custom heuristics.
        """
        self.assignments = assignments
        self.assignments_counts = assignments_counts

        # Scheduling: SJF
        efforts = self._calc_pipeline_efforts(pipelines)
        run_order = sorted(
            list(efforts.keys()),
            key=lambda x: efforts[x]["total"]
        )

        # Placement: pipeline-aware heuristic
        self.node_manager.update_nodes()
        pipelines_dict = {pipeline.id: pipeline for pipeline in pipelines}
        placements = []
        
        for pipeline_id in run_order:
            pipeline = pipelines_dict[pipeline_id]
            metadata = pipeline.get_metadata()
            mapping = {}
            for component in pipeline.get_components():
                strategy_fn = self.node_selectors[component.type]
                node, platform = strategy_fn(pipeline_id, metadata)
                mapping[component.name] = (node, platform)
                self._add_assignment(node, pipeline_id, component.name)
            
            placements.append({
                "pipeline_id": pipeline_id,
                "mapping": mapping,
                "efforts": efforts[pipeline_id]
            })
        
        return placements


    def _calc_pipeline_efforts(self, pipelines: List[Pipeline]) -> Dict[str, Dict]:
        """
        Calculate the effort for each pipeline and its components.
        """
        efforts = {}
        for pipeline in pipelines:
            metadata = pipeline.get_metadata()
            pipeline_efforts = {}
            total_effort = 0
            for component in pipeline.get_components():
                effort = self._calc_component_effort(component, metadata)
                pipeline_efforts[component.name] = effort
                total_effort += effort
                
            pipeline_efforts["total"] = total_effort
            efforts[pipeline.id] = pipeline_efforts
            
        return efforts


    def _calc_component_effort(self, component: Component, metadata: Dict) -> int:
        """
        Calculate the effort for a specific component based on its type.
        """
        if component.type in self.effort_calculators:
            return self.effort_calculators[component.type](metadata)
        else:
            print(f"Unknown component type: {component.type}")
            return 0


    def _calc_preprocessing_effort(self, metadata: Dict) -> int:
        """
        Calculate the effort for a preprocessing component.
        """
        n_samples = metadata["dataset"]["original"]["n_samples"]
        
        # Calculate the number of features based on dataset type
        if metadata["dataset"]["type"] == "tabular":
            n_features = metadata["dataset"]["original"]["n_features"]
        elif metadata["dataset"]["type"] == "image":
            shape = metadata["dataset"]["original"]["input_shape"]
            n_features = shape[0] * shape[1] * shape[2]
            
        # Simple effort model: samples × features
        effort = n_samples * n_features
        return effort


    def _calc_training_effort(self, metadata: Dict) -> int:
        """
        Calculate the effort for a training component.
        """
        return self._estimate_model_effort(
            metadata, 
            metadata["dataset"]["train_percentage"], 
            training=True
        )


    def _calc_evaluation_effort(self, metadata: Dict) -> int:
        """
        Calculate the effort for an evaluation component.
        """
        return self._estimate_model_effort(
            metadata, 
            metadata["dataset"]["test_percentage"], 
            training=False
        )
    

    def _estimate_model_effort(self, metadata: Dict, data_percentage: float, training: bool) -> int:
        """
        Estimate the effort for a model based on its type and parameters.
        """
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

    
    def _select_preprocessing_node(self, pipeline_id: str, metadata: Dict) -> Tuple[str, str]:
        """
        Select a node for preprocessing.
        """
        dataset = metadata["dataset"]
        size = max(
            self.data_manager.size_in_memory(dataset, "original"),
            self.data_manager.size_in_memory(dataset, "preprocessed")
        )

        # Find nodes that fit the data
        filters = {"worker_type": ["low", "med", "high-cpu"]}
        candidates = self.node_manager.get_nodes(filters=filters, sort_params=["memory"])
        candidates = [node for node in candidates if self._has_sufficient_memory(size, node)]
        node = self._least_loaded_node(candidates)
        
        return (
            node["name"],
            self.node_manager.get_node_platform(node["name"])
        )
        
    
    def _select_training_node(self, pipeline_id: str, metadata: Dict) -> Tuple[str, str]:
        """
        Select a node for training.
        """
        # Dataset
        dataset = metadata["dataset"]
        size = self.data_manager.size_in_memory(dataset, "preprocessed")
        size = int(size * metadata["dataset"]["train_percentage"])

        # Model
        model = metadata["model"]["type"]
        heuristics = self.heuristics["training"][model]
        sorting = heuristics.get("sorting", [])
        filters = {
            "worker_type": heuristics["worker_type"],
            "architecture": heuristics["architecture"]
        }
        candidates = self.node_manager.get_nodes(filters=filters, sort_params=sorting)

        if model not in ["nn", "cnn"]:
            candidates = [node for node in candidates if self._has_sufficient_memory(size, node)]
            node = self._select_best_node(candidates, pipeline_id)
        else:
            scores = {}
            for node in candidates:
                has_accelerator = node["accelerator"] != "none"
                score = self.accelerator_score if has_accelerator else 0    # Prioritize nodes with accelerators
                score -= self.assignments_counts[node["name"]]              # But balance against current load
                scores[node["name"]] = score
            candidates = sorted(
                candidates,
                key=lambda x: (scores[x["name"]], -self.assignments_counts[x["name"]]),
                reverse=True
            )
            node = candidates[0]

        return (
            node["name"],
            self.node_manager.get_node_platform(node["name"])
        )


    def _select_evaluation_node(self, pipeline_id: str, metadata: Dict) -> Tuple[str, str]:
        """
        Select a node for evaluation.
        """
        # Dataset
        dataset = metadata["dataset"]
        size = self.data_manager.size_in_memory(dataset, "preprocessed")
        size = int(size * metadata["dataset"]["test_percentage"])

        # Model
        model = metadata["model"]["type"]
        heuristics = self.heuristics["evaluation"][model]
        sorting = heuristics["sorting"]
        filters = {
            "worker_type": heuristics["worker_type"],
            "architecture": heuristics["architecture"]
        }
        candidates = self.node_manager.get_nodes(filters=filters, sort_params=sorting)
        candidates = [node for node in candidates if self._has_sufficient_memory(size, node)]
        node = self._select_best_node(candidates, pipeline_id)

        return (
            node["name"],
            self.node_manager.get_node_platform(node["name"])
        )


    def _has_sufficient_memory(self, size: int, node: Dict) -> bool:
        """
        Check if the node has sufficient memory for the data plus overhead.
        """
        memory = node["memory"]
        memory_usage = node["memory_usage"]
        memory_free = memory - (memory * memory_usage)
        memory_required = size * 2
        return memory_free > memory_required


    def _least_loaded_node(self, nodes: List[Dict]) -> Dict:
        """
        Select the least loaded node based on the number of assignments.
        """
        overload = sorted(nodes, key=lambda x: self.assignments_counts[x["name"]])
        return overload[0]
    

    def _select_best_node(self, candidates: List[Dict], pipeline_id: str) -> Dict:
        """
        Select the best node from the candidates based on the pipeline ID.
        """
        # Check if the pipeline has assignment(s)
        nodes = []
        for node, components in self.assignments.items():
            pipelines = [c.split("/")[0] for c in components]
            if pipeline_id in pipelines:
                nodes.append(node)

        if not nodes and not candidates:
            return self._fallback_node()

        common_nodes = [c for c in candidates if c["name"] in nodes]
        candidates = common_nodes if common_nodes else candidates
        return self._least_loaded_node(candidates)
        

    def _fallback_node(self) -> Dict:
        """
        Fallback to a high-cpu node if no suitable candidates are found.
        """
        nodes = self.node_manager.get_nodes(filters={"worker_type": ["high-cpu"]})
        return self._least_loaded_node(nodes)


    def _add_assignment(self, node: str, pipeline_id: str, component: str):
        """
        Add an assignment to the node.
        """
        self.assignments[node].add(f"{pipeline_id}/{component}")
        self.assignments_counts[node] += 1
