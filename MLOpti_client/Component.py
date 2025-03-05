import inspect

class Component:

    def __init__(self, image, func, args):
        self.image = image
        self.func = func
        self.user_args = args
        self.name = func.__name__
        self.file = None
        self.filename = None
        self.volumes = []
        self._get_source_file()
        

    def _get_source_file(self):
        """
        Get the source file of the function
        """
        self.file = inspect.getfile(self.func)
        self.filename = self.file.split("/")[-1]
        
        if self.filename.split(".")[0] != self.name:
            raise ValueError("The file name must match the function name")


    def mount_volume(self, pvc, mount_path):
        """
        Mount a volume to a component
        """
        self.volumes.append((pvc, mount_path))