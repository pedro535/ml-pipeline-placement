import ast
import astor
import inspect
import black

from MLOpti_client.consts import (
    IMPORTS_MAPPING,
    TYPES_MAPPING,
    KFP_COMPONENT_DECORATOR
)


class Component:

    def __init__(self, image, func, args):
        self.image = image
        self.func = func
        self.user_args = args
        self.name = func.__name__
        self.file = None
        self.tree = None
        self.arg_types = {}
        self.volumes = []

        self.get_source_file()
        self.get_tree()
        self.get_arg_types()
        

    def get_source_file(self):
        """
        Get the source file of the function
        """
        self.file = inspect.getfile(self.func)


    def get_tree(self):
        """
        Parse the source file to an AST
        """
        with open(self.file, "r") as f:
            tree = ast.parse(f.read())
        tree.body = tree.body[2:]         # Remove sys.path.append used for development
        self.tree = tree


    def get_arg_types(self):
        """
        Get all arguments of the function
        """
        for arg_name, arg_type in self.func.__annotations__.items():
            self.arg_types[arg_name] = arg_type.__name__


    def mount_volume(self, pvc, mount_path):
        """
        Mount a volume to a component
        """
        self.volumes.append((pvc, mount_path))

    
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

    
    def get_imports(self):
        """
        Get modules and names to import
        """
        imports = {}
        for arg_type in self.arg_types.values():
            if arg_type not in IMPORTS_MAPPING:
                continue
            module, names = IMPORTS_MAPPING[arg_type]
            if module not in imports:
                imports[module] = set()
            imports[module].update(names)
        return imports


    def add_imports(self):
        """
        Add import statements to the top of the file
        """
        imports = self.get_imports()
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


    def add_decorator(self):
        """
        Add the kfp component decorator to the function
        """
        for node in ast.walk(self.tree):
            if isinstance(node, ast.FunctionDef) and node.name == self.name:
                decorator_node = ast.Call(
                    func=ast.Name(id=KFP_COMPONENT_DECORATOR, ctx=ast.Load()),
                    args=[],
                    keywords=[
                        ast.keyword(arg="base_image", value=ast.Constant(s=self.image))
                    ],
                )
                node.decorator_list.append(decorator_node)
                break


    def update_arg_types(self):
        """
        Replace artifact marker types with kfp data types
        """
        for node in ast.walk(self.tree):
            if isinstance(node, ast.FunctionDef) and node.name == self.name:
                for arg in node.args.args:
                    arg_type = arg.annotation.id
                    if arg_type in TYPES_MAPPING:
                        arg.annotation.id = TYPES_MAPPING[arg_type]
                break


    def compile(self) -> str:
        """
        Compile the component to a kfp component
        """
        # Apply transformations
        self.remove_type_imports()
        self.add_imports()
        self.add_decorator()
        self.update_arg_types()

        # Parse and save modified code
        ast.fix_missing_locations(self.tree)
        kfp_component = astor.to_source(self.tree)
        kfp_component = black.format_str(kfp_component, mode=black.Mode())
        
        return kfp_component