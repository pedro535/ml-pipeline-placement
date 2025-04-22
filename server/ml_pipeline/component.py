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
        return self.__dict__
