KFP_COMPONENT_DECORATOR = "dsl.component"
KFP_PIPELINE_DECORATOR = "dsl.pipeline"

PIPELINE_IMPORTS = ["dsl.pipeline", "mount_pvc", "add_node_selector", "client"]

IMPORTS_MAPPING = {
    "dsl.component": ("kfp", ["dsl"]),
    "dsl.pipeline": ("kfp", ["dsl"]),
    "mount_pvc": ("kfp.kubernetes", ["mount_pvc"]),
    "add_node_selector": ("kfp.kubernetes", ["add_node_selector"]),
    "client": ("kfp", ["Client"]),
    "OutputDataset": ("kfp.dsl", ["Output", "Dataset"]),
    "InputDataset": ("kfp.dsl", ["Input", "Dataset"]),
    "OutputModel": ("kfp.dsl", ["Output", "Model"]),
    "InputModel": ("kfp.dsl", ["Input", "Model"]),
}

TYPES_MAPPING = {
    "OutputDataset": "Output[Dataset]",
    "InputDataset": "Input[Dataset]",
    "OutputModel": "Output[Model]",
    "InputModel": "Input[Model]",
}

ARGPARSE_CODE = [
    "import argparse",
    "parser = argparse.ArgumentParser()",
    "parser.add_argument('-u', type=str, help='kfp URL', required=True)",
    "parser.add_argument('-c', help='Enable caching', action='store_true')",
    "parser.add_argument('-p', nargs='+', help='Placement', required=True)",
    "args = parser.parse_args()"
]