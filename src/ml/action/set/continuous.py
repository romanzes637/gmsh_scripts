import numpy as np

from src.ml.action.set.variable import Variable


class Continuous(Variable):
    def __init__(self, low, high, **kwargs):
        super().__init__(**kwargs)
        self.low = low
        self.high = high

    def post_call(self, actions=None, *args, **kwargs):
        actions[-2].value = np.random.uniform(self.low, self.high)
