from variable import Variable


class Continuous(Variable):
    def __init__(self, name=None, low=None, high=None):
        super().__init__(name=name)
        self.low = low
        self.high = high
