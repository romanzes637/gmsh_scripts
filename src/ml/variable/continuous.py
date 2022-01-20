from src.ml.variable.variable import Variable
import numpy as np


class Continuous(Variable):
    def __init__(self, name=None, low=None, high=None):
        super().__init__(name=name)
        self.low = low
        self.high = high

    def __call__(self, *args, **kwargs):
        return np.random.uniform(self.low, self.high)
