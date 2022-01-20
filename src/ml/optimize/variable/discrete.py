from variable import Variable


class Discrete(Variable):
    def __init__(self, name=None, low=None, high=None, step=None):
        super().__init__(name=name)
        self.low = low
        self.high = high
        self.step = step
