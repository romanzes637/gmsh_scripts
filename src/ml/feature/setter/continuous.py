from src.ml.feature.setter.variable import Variable
import numpy as np


class Continuous(Variable):
    def __init__(self, low, high):
        super().__init__()
        self.low = low
        self.high = high

    def __call__(self, feature, *args, **kwargs):
        feature.value = np.random.uniform(self.low, self.high)
        return feature.value
