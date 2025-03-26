import ast
import astor
import black
from typing import Dict

from mlopx.consts import IMPORTS_MAPPING, TYPES_MAPPING, KFP_COMPONENT_DECORATOR


class ComponentConverter:

    def __init__(self, tree: ast.Module):
        self.tree = tree


    def remove_type_imports(self):
        """
        Remove marked types imports
        """
        import_nodes = []
        for node in ast.walk(self.tree):
            if isinstance(node, ast.ImportFrom) and "artifacts" in node.module:
                import_nodes.append(node)
        for node in import_nodes:
            self.tree.body.remove(node)
        return self


    def get_imports(self, arg_types: Dict) -> Dict:
        """
        Get modules and names to import
        """
        imports = {}
        for arg_type in arg_types.values():
            if arg_type not in IMPORTS_MAPPING:
                continue
            module, names = IMPORTS_MAPPING[arg_type]
            if module not in imports:
                imports[module] = set()
            imports[module].update(names)
        return imports


    def add_imports(self, arg_types):
        """
        Add import statements to the top of the file
        """
        imports = self.get_imports(arg_types)
        for module, names in imports.items():
            node = ast.ImportFrom(
                module=module,
                names=[ast.alias(name=name, asname=None) for name in names],
                level=0,
            )
            self.tree.body.insert(0, node)

        # Import @dsl.component decorator
        module, names = IMPORTS_MAPPING[KFP_COMPONENT_DECORATOR]
        node = ast.ImportFrom(
            module=module,
            names=[ast.alias(name=name, asname=None) for name in names],
            level=0,
        )
        self.tree.body.insert(0, node)
        return self


    def add_decorator(self, component_name: str, image: str):
        """
        Add the kfp component decorator to the function
        """
        for node in ast.walk(self.tree):
            if isinstance(node, ast.FunctionDef) and node.name == component_name:
                decorator_node = ast.Call(
                    func=ast.Name(id=KFP_COMPONENT_DECORATOR, ctx=ast.Load()),
                    args=[],
                    keywords=[
                        ast.keyword(arg="base_image", value=ast.Constant(s=image))
                    ],
                )
                node.decorator_list.append(decorator_node)
                break
        return self


    def update_arg_types(self, component_name: str):
        """
        Replace artifact marker types with kfp data types
        """
        for node in ast.walk(self.tree):
            if isinstance(node, ast.FunctionDef) and node.name == component_name:
                for arg in node.args.args:
                    arg_type = arg.annotation.id
                    if arg_type in TYPES_MAPPING:
                        arg.annotation.id = TYPES_MAPPING[arg_type]
                break
        return self


    def save_component(self, filename: str):
        """
        Save the converted component to a file
        """
        with open(f"kfp_{filename}", "w") as f:
            ast.fix_missing_locations(self.tree)
            kfp_component = astor.to_source(self.tree)
            kfp_component = black.format_str(kfp_component, mode=black.Mode())
            f.write(kfp_component)
