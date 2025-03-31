from typing import Dict, List, Tuple
import json

from server import NodeManager, DataManager, MLEstimator


class DecisionUnit:
    
    def __init__(self, node_manager: NodeManager, data_manager: DataManager):
        self.node_manager = node_manager
        self.data_manager = data_manager
        self.estimator = MLEstimator()


    def get_placements(self, pipelines: List[Tuple], pipelines_metadata: Dict) -> List[Dict]:
        
        # Calculate computational effort for each pipeline and its components
        computational_effort = self.calculate_computational_effort(pipelines, pipelines_metadata)

        placements = []
        for pipeline_id, components in pipelines:
            placements.append({
                "pipeline_id": pipeline_id,
                "mapping": {c: None for c in components},
                "efforts": computational_effort[pipeline_id]["total"]
            })

        # Scheduling (sort by total effort for now)
        placements = sorted(placements, key=lambda x: x["efforts"]["total"])

        # Placement
        # TODO
        
        return placements


    def calculate_computational_effort(self, pipelines: List[Tuple], pipelines_metadata: Dict) -> Dict:
        computational_effort = {}
        
        for pipeline_id, components in pipelines:
            metadata = pipelines_metadata[pipeline_id]
            
            efforts = {}
            total_effort = 0
            for component in components:
                component_effort = self.get_effort(component, metadata)
                efforts[component] = component_effort
                total_effort += component_effort
                
            efforts["total"] = total_effort
            computational_effort[pipeline_id] = efforts
            
        return computational_effort


    def get_effort(self, component: str, metadata: Dict) -> int:
        component_type = metadata["components_type"][component]
        
        effort_calculators = {
            "preprocessing": self.calculate_preprocessing_effort,
            "training": self.calculate_training_effort,
            "evaluation": self.calculate_evaluation_effort
        }
        
        if component_type in effort_calculators:
            return effort_calculators[component_type](metadata)
        else:
            print(f"Unknown component type: {component_type}")
            return 0


    def calculate_preprocessing_effort(self, metadata: Dict) -> int:
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


    def calculate_training_effort(self, metadata: Dict) -> int:
        return self.estimate_model_effort(
            metadata, 
            metadata["dataset"]["train_percentage"], 
            training=True
        )


    def calculate_evaluation_effort(self, metadata: Dict) -> int:
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