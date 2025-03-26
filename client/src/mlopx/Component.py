import ast
import inspect
from typing import Callable, Dict

from mlopx import ComponentConverter


class Component:

    def __init__(self, image: str, func: Callable, args: Dict = None):
        self.image = image
        self.func = func
        self.name = func.__name__
        self.user_args = args
        self.arg_types = {}
        self.filename = None
        self.volumes = []

        self.get_source_file()
        self.get_tree()
        self.get_arg_types()


    def get_source_file(self) -> None:
        """
        Get the source file of the function
        """
        abs_path = inspect.getfile(self.func)
        self.filename = abs_path.split("/")[-1]

        if self.filename.split(".")[0] != self.name:
            raise ValueError("The file name must match the function name")


    def get_tree(self) -> None:
        """
        Parse the source file to an AST
        """
        with open(self.filename, "r") as f:
            self.tree = ast.parse(f.read())


    def get_arg_types(self) -> None:
        """
        Get all arguments of the function
        """
        for arg_name, arg_type in self.func.__annotations__.items():
            self.arg_types[arg_name] = arg_type.__name__


    def mount_volume(self, pvc: str, mount_path: str) -> None:
        """
        Mount a volume to a component
        """
        self.volumes.append((pvc, mount_path))


    def convert(self) -> None:
        """
        Compile the component to a kfp component
        """
        converter = ComponentConverter(self.tree)

        (
            converter.remove_type_imports()
            .add_imports(self.arg_types)
            .add_decorator(self.name, self.image)
            .update_arg_types(self.name)
            .save_component(self.filename)
        )
