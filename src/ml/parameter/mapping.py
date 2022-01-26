class Mapping:
    def __init__(self, name=None, variables=None, mapping=None):
        self.name = name
        self.variables = variables
        self.mapping = mapping

    def __call__(self, *args, **kwargs):
        arguments = [x() for x in self.variables]
        return arguments
