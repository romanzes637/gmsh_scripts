from src.ml.variable.variable import Variable
import numpy as np


class Discrete(Variable):
    def __init__(self, name=None, low=None, high=None, num=None):
        super().__init__(name=name)
        self.low = low
        self.high = high
        self.num = num

    def __call__(self, *args, **kwargs):
        s = np.random.choice(np.linspace(
            self.low, self.high, self.num, endpoint=True))
        if isinstance(self.low, int) and isinstance(self.high, int):
            s = int(s)
        return s
