import ast
import astor
import black
from typing import List, Dict

from mlopx import Component
from mlopx.consts import (
    IMPORTS_MAPPING,
    KFP_PIPELINE_DECORATOR,
    PIPELINE_IMPORTS,
)


class PipelineBuilder:

    def __init__(self):
        self.tree = ast.Module(body=[])
        self.func_node = None


    def add_imports(self, components: List[Component]):
        """
        Add imports to the pipeline file
        """
        # KFP imports
        imports = {}
        for name in PIPELINE_IMPORTS:
            module, names = IMPORTS_MAPPING[name]
            imports[module] = imports.get(module, []) + names

        for module, names in imports.items():
            node = ast.ImportFrom(
                module=module,
                names=[ast.alias(name=name, asname=None) for name in names],
                level=0,
            )
            self.tree.body.append(node)

        # Component imports
        for component in components:
            node = ast.ImportFrom(
                module=f"kfp_{component.name}",
                names=[ast.alias(name=component.name, asname=None)],
                level=0,
            )
            self.tree.body.append(node)

        return self


    def create_function(self, func_name: str):
        """
        Create the pipeline function
        """
        self.func_node = ast.FunctionDef(
            name=func_name,
            args=ast.arguments(
                args=[],
                defaults=[],
            ),
            body=[],
        )
        return self


    def add_decorator(self, pipeline_name: str):
        """
        Add the kfp pipeline decorator to the function
        """
        self.func_node.decorator_list = [
            ast.Call(
                func=ast.Name(id=KFP_PIPELINE_DECORATOR, ctx=ast.Load()),
                args=[],
                keywords=[ast.keyword(arg="name", value=ast.Constant(s=pipeline_name))],
            )
        ]
        return self


    def call_components(self, components: List[Component], artifacts: Dict):
        """
        Call the compiled components in the pipeline function
        """
        for component in components:
            args = {}
            for arg_name, arg_type in component.arg_types.items():
                if arg_name in component.user_args:
                    args[arg_name] = ast.Constant(component.user_args[arg_name])
                elif arg_type.startswith("Input"):
                    args[arg_name] = ast.Subscript(
                        value=ast.Attribute(
                            value=ast.Name(
                                id=f"{artifacts[arg_name]}_task", ctx=ast.Load()
                            ),
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
                    keywords=[ast.keyword(arg=k, value=v) for k, v in args.items()],
                ),
            )
            self.func_node.body.append(node)

        self.tree.body.append(self.func_node)
        return self


    def mount_volumes(self, components: List[Component]):
        """
        Mount volumes to components
        """
        for component in components:
            for pvc, mount_path in component.volumes:
                invoke_node = ast.Call(
                    func=ast.Name(id="mount_pvc", ctx=ast.Load()),
                    args=[],
                    keywords=[
                        ast.keyword(
                            arg="task",
                            value=ast.Name(id=f"{component.name}_task", ctx=ast.Load()),
                        ),
                        ast.keyword(
                            arg="pvc_name",
                            value=ast.Constant(value=pvc)
                        ),
                        ast.keyword(
                            arg="mount_path",
                            value=ast.Constant(value=mount_path)
                        )
                    ],
                )
                node = ast.Assign(
                    targets=[ast.Name(id=f"{component.name}_task", ctx=ast.Store())],
                    value=invoke_node,
                )
                self.func_node.body.append(node)
        return self

        
    def add_node_selector(self, components: List[Component], node_selectors: List[str]):
        """
        Add node selectors to components
        """
        if not node_selectors:
            return self
        
        for i, component in enumerate(components):
            invoke_node = ast.Call(
                func=ast.Name(id="add_node_selector", ctx=ast.Load()),
                args=[],
                keywords=[
                    ast.keyword(
                        arg="task",
                        value=ast.Name(id=f"{component.name}_task", ctx=ast.Load()),
                    ),
                    ast.keyword(
                        arg="label_key",
                        value=ast.Constant(value="kubernetes.io/hostname")
                    ),
                    ast.keyword(
                        arg="label_value",
                        value=ast.Constant(value=node_selectors[i])
                    )
                ],
            )
            node = ast.Assign(
                targets=[ast.Name(id=f"{component.name}_task", ctx=ast.Store())],
                value=invoke_node,
            )
            self.func_node.body.append(node)
        return self


    def create_client(self, kfp_url: str):
        """
        Create the kfp client
        """
        node = ast.Assign(
            targets=[ast.Name(id="client", ctx=ast.Store())],
            value=ast.Call(
                func=ast.Name(id="Client", ctx=ast.Load()),
                args=[],
                keywords=[ast.keyword(arg="host", value=ast.Constant(value=kfp_url))],
            ),
        )
        self.tree.body.append(node)
        return self


    def add_create_run(self, func_name: str, enable_caching: bool):
        """
        Call the kfp create run function to run the created pipeline
        """
        node = ast.Assign(
            targets=[ast.Name(id="run", ctx=ast.Store())],
            value=ast.Call(
                func=ast.Attribute(
                    value=ast.Name(id="client", ctx=ast.Load()),
                    attr="create_run_from_pipeline_func",
                    ctx=ast.Load(),
                ),
                args=[],
                keywords=[
                    ast.keyword(
                        arg="pipeline_func",
                        value=ast.Name(id=func_name, ctx=ast.Load()),
                    ),
                    ast.keyword(
                        arg="enable_caching", value=ast.Constant(value=enable_caching)
                    ),
                ],
            ),
        )
        print_node = ast.Expr(
            value=ast.Call(
                func=ast.Name(id="print", ctx=ast.Load()),
                args=[
                    ast.Constant(value="Run ID: "),
                    ast.Attribute(
                        value=ast.Name(id="run", ctx=ast.Load()),
                        attr="run_id",
                        ctx=ast.Load(),
                    ),
                ],
                keywords=[],
            )
        )
        self.tree.body.extend([node, print_node])
        return self


    def save_pipeline(self) -> None:
        """
        Save the pipeline to a file
        """
        with open("kfp_pipeline.py", "w") as f:
            ast.fix_missing_locations(self.tree)
            kfp_pipeline = astor.to_source(self.tree)
            kfp_pipeline = black.format_str(kfp_pipeline, mode=black.Mode())
            f.write(kfp_pipeline)
