KFP_COMPONENT_DECORATOR = "dsl.component"
KFP_PIPELINE_DECORATOR = "dsl.pipeline"


IMPORTS_MAPPING = {
    "dsl.component": ("kfp", ["dsl"]),
    "dsl.pipeline": ("kfp", ["dsl"]),
    "OutputDataset": ("kfp.dsl", ["Output", "Dataset"]),
    "InputDataset": ("kfp.dsl", ["Input", "Dataset"]),
    "OutputModel": ("kfp.dsl", ["Output", "Model"]),
    "InputModel": ("kfp.dsl", ["Input", "Model"])
}

TYPES_MAPPING = {
    "OutputDataset": "Output[Dataset]",
    "InputDataset": "Input[Dataset]",
    "OutputModel": "Output[Model]",
    "InputModel": "Input[Model]"
}