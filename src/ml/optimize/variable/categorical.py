from variable import Variable


class Categorical(Variable):
    def __init__(self, name=None, choices=None):
        super().__init__(name=name)
        self.choices = choices
