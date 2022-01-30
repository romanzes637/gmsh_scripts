import numpy as np

from src.ml.action.set.variable import Variable
from src.ml.action.feature.feature import Feature


class Discrete(Variable):
    def __init__(self, low, high, num, **kwargs):
        super().__init__(**kwargs)
        self.low = low
        self.high = high
        self.num = num

    def post_call(self, action=None, *args, **kwargs):
        if isinstance(action, Feature):
            v = np.random.choice(np.linspace(
                self.low, self.high, self.num, endpoint=True))
            if isinstance(self.low, int) and isinstance(self.high, int):
                v = int(v)
            action.value = v
        return self, action
