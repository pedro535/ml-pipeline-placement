import inspect
import ast
import astor

KFP_COMPONENT_DECORATOR = "dsl.component"
KFP_PIPELINE_DECORATOR = "dsl.pipeline"

imports_mapping = {
    "dsl.component": ("kfp", ["dsl"]),
    "dsl.pipeline": ("kfp", ["dsl"]),
    "OutputDataset": ("kfp.dsl", ["Output", "Dataset"]),
    "InputDataset": ("kfp.dsl", ["Input", "Dataset"]),
    "OutputModel": ("kfp.dsl", ["Output", "Model"]),
    "InputModel": ("kfp.dsl", ["Input", "Model"])
}

type_mapping = {
    "OutputDataset": "Output[Dataset]",
    "InputDataset": "Input[Dataset]",
    "OutputModel": "Output[Model]",
    "InputModel": "Input[Model]"
}


class Pipeline:

    def __init__(self):
        self.components = []


    def add(self, image, func, args):
        self.components.append((image, func, args))


    def add_imports(self, tree, func):

        # Remove marked types imports
        nodes_to_rm = []
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom) and node.module == "artifacts":
                nodes_to_rm.append(node)  
        for node in nodes_to_rm:
            tree.body.remove(node)

        # Extract argument types
        args = inspect.signature(func).parameters
        arg_types = set(arg.annotation.__name__ for arg in args.values())

        # Ignore standard types
        arg_types.intersection_update(imports_mapping.keys())
        
        # Determine modules and names
        imports = {}
        for arg_type in arg_types:
            module, names = imports_mapping[arg_type]
            if module not in imports:
                imports[module] = set()
            imports[module].update(names)
        
        # Add imports statements
        for module, names in imports.items():
            node = ast.ImportFrom(
                module=module,
                names=[ast.alias(name=name, asname=None) for name in names],
                level=0
            )
            tree.body.insert(0, node)

        # Import component decorator
        module, names = imports_mapping[KFP_COMPONENT_DECORATOR]
        node = ast.ImportFrom(
            module=module,
            names=[ast.alias(name=name, asname=None) for name in names],
            level=0
        )
        tree.body.insert(0, node)


    def add_decorator(self, tree, func, image):
        func_name = func.__name__

        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) and node.name == func_name:
                decorator_node = ast.Call(
                    func=ast.Name(id=KFP_COMPONENT_DECORATOR, ctx=ast.Load()),
                    args=[],
                    keywords=[
                        ast.keyword(arg="base_image", value=ast.Constant(s=image))
                    ],
                )

                node.decorator_list.append(decorator_node)


    def update_arg_types(self, tree, func):
        func_name = func.__name__

        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) and node.name == func_name:
                for a in node.args.args:
                    arg_type = a.annotation.id
                    if arg_type in type_mapping:
                        a.annotation.id = type_mapping[arg_type]


    def compile_components(self):
        for component in self.components:
            image, func, _ = component
            func_file = inspect.getfile(func)

            with open(func_file) as f:
                tree = ast.parse(f.read())

            # Apply transformations
            self.add_imports(tree, func)
            self.add_decorator(tree, func, image)
            self.update_arg_types(tree, func)
            
            # Parse modified code
            ast.fix_missing_locations(tree)
            modified_code = astor.to_source(tree)
            print(modified_code)


    def build_pipeline(self):
        pass


    def run(self, kfp_host):
        self.compile_components()
        self.build_pipeline()
