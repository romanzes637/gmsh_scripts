from src.ml.variable.variable import Variable


class Fixed(Variable):
    def __init__(self, name=None, variable=None):
        super().__init__(name=name)
        self.variable = variable

    def __call__(self, *args, **kwargs):
        return self.variable
