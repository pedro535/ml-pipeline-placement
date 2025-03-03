from pathlib import Path
import uuid
import inspect
import ast
import astor
import black
from typing import List

from src.pipeline import Component
from src.pipeline.consts import (
    IMPORTS_MAPPING,
    KFP_PIPELINE_DECORATOR
)


class Pipeline:

    def __init__(self, name):
        self.name = name
        self.components = []
        self.artifacts = {}  # {output_artifact_name: producer_component_name}
        self.tree = None


    def add(self, components: List[Component]):
        """
        Add a list of components to the pipeline
        """
        self.components.extend(components)
        for component in components:
            for arg_name, arg_type in component.arg_types.items():
                if "Output" in arg_type:
                    self.artifacts[arg_name] = component.name


    def compile_components(self, pipeline_id):
        """
        Compile each component to equivalent kfp component
        """
        for component in self.components:
            kfp_component = component.compile()
            with open(f"{pipeline_id}/{component.name}.py", "w") as f:
                f.write(kfp_component)


    def add_imports(self):
        """
        Add imports to the pipeline file
        """
        # Compiled components
        for component in self.components:
            node = ast.ImportFrom(
                module=component.name,
                names=[ast.alias(name=component.name, asname=None)],
                level=0,
            )
            self.tree.body.append(node)

        # Pipeline decorator
        module, names = IMPORTS_MAPPING[KFP_PIPELINE_DECORATOR]
        node = ast.ImportFrom(
            module=module,
            names=[ast.alias(name=name, asname=None) for name in names],
            level=0,
        )
        self.tree.body.append(node)

        # Import mount_pvc and add_node_selector functions
        imports = ["mount_pvc", "add_node_selector"]
        node = ast.ImportFrom(
            module="kfp.kubernetes",
            names=[ast.alias(name=name, asname=None) for name in imports],
            level=0,
        )
        self.tree.body.append(node)


    def create_function(self):
        """
        Create the pipeline function
        """
        node = ast.FunctionDef(
            name="kfp_pipeline",
            args=ast.arguments(
                args=[],
                defaults=[],
            ),
            body=[]
        )
        return node


    def add_decorator(self, func_node: ast.FunctionDef):
        """
        Add the kfp pipeline decorator to the function
        """
        func_node.decorator_list = [
            ast.Call(
                func=ast.Name(id=KFP_PIPELINE_DECORATOR, ctx=ast.Load()),
                args=[],
                keywords=[
                    ast.keyword(arg="name", value=ast.Constant(s=self.name))
                ],
            )
        ]


    def mount_volumes(self, component, func_node):
        """
        Mount volumes to the component
        """
        for pvc, mount_path in component.volumes:
            invoke_node = ast.Call(
                func=ast.Name(id="mount_pvc", ctx=ast.Load()),
                args=[],
                keywords=[
                    ast.keyword(arg="task", value=ast.Name(id=f"{component.name}_task", ctx=ast.Load())),
                    ast.keyword(arg="pvc_name", value=ast.Constant(value=pvc)),
                    ast.keyword(arg="mount_path", value=ast.Constant(value=mount_path))
                ],
            )
            node = ast.Assign(
                targets=[ast.Name(id=f"{component.name}_task", ctx=ast.Store())],
                value=invoke_node,
            )
            func_node.body.append(node)


    def call_components(self, func_node):
        """
        Call the compiled components in the pipeline function
        """
        for component in self.components:
            args = {}
            for arg_name, arg_type in component.arg_types.items():
                if arg_name in component.user_args:
                    args[arg_name] = ast.Constant(component.user_args[arg_name])
                elif arg_type.startswith("Input"):
                    args[arg_name] = ast.Subscript(
                        value=ast.Attribute(
                            value=ast.Name(id=f"{self.artifacts[arg_name]}_task", ctx=ast.Load()),
                            attr="outputs",
                            ctx=ast.Load(),
                        ),
                        slice=ast.Constant(value=arg_name),
                        ctx=ast.Load(),
                    )
            
            node = ast.Assign(
                targets=[ast.Name(id=f"{component.name}_task", ctx=ast.Store())],
                value=ast.Call(
                    func=ast.Name(id=component.name, ctx=ast.Load()),
                    args=[],
                    keywords=[
                        ast.keyword(arg=k, value=v) for k, v in args.items()
                    ],
                ),
            )
            func_node.body.append(node)
            self.mount_volumes(component, func_node)         


    def build_pipeline(self, pipeline_id):
        """
        Build the kfp pipeline using the compiled components
        """
        self.tree = ast.Module(body=[])
        self.add_imports()
        func_node = self.create_function()
        self.add_decorator(func_node)
        self.call_components(func_node)
        self.tree.body.append(func_node)

        # Write pipeline to file
        with open(f"{pipeline_id}/pipeline.py", "w") as f:
            ast.fix_missing_locations(self.tree)
            kfp_pipeline = astor.to_source(self.tree)
            kfp_pipeline = black.format_str(kfp_pipeline, mode=black.Mode())
            f.write(kfp_pipeline)


    def run(self, kfp_host):
        """
        Run the pipeline using the kfp backend
        """
        pipeline_id = str(uuid.uuid4())
        p = Path(f"{pipeline_id}/")
        p.mkdir(parents=True, exist_ok=True)
        
        self.compile_components(pipeline_id)
        self.build_pipeline(pipeline_id)