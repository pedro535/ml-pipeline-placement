class Component:
    
    def __init__(self, name, filename):
        self.name = name
        self.filename = filename
        self.type = None
        self.state = None
        self.node = None
        self.platform = None
        self.effort = None
        self.start_time = None
        self.end_time = None
        self.duration = None


    def dict_repr(self):
        """
        Returns a dictionary representation of the component.
        """
        obj_dict = self.__dict__.copy()
        obj_dict.pop("effort", None)
        obj_dict.pop("filename", None)
        return obj_dict