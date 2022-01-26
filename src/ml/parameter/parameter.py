class Parameter:
    def __init__(self, name=None, variables=None):
        self.name = name
        self.variables = variables

    def __call__(self, *args, **kwargs):
        return (x() for x in self.variables)
