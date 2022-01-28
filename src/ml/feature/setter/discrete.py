from src.ml.feature.setter.variable import Variable
import numpy as np


class Discrete(Variable):
    def __init__(self, low, high, num):
        super().__init__()
        self.low = low
        self.high = high
        self.num = num

    def __call__(self, feature, *args, **kwargs):
        v = np.random.choice(np.linspace(
            self.low, self.high, self.num, endpoint=True))
        if isinstance(self.low, int) and isinstance(self.high, int):
            v = int(v)
        feature.value = v
        return feature.value
