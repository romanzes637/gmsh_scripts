import numpy as np

from src.ml.action.set.variable import Variable
from src.ml.action.feature.feature import Feature


class Continuous(Variable):
    def __init__(self, low, high, **kwargs):
        super().__init__(**kwargs)
        self.low = low
        self.high = high

    def post_call(self, action=None, *args, **kwargs):
        if isinstance(action, Feature):
            action.value = np.random.uniform(self.low, self.high)
        return self, action
