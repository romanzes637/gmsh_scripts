import numpy as np

from src.ml.action.set.variable import Variable


class Continuous(Variable):
    def __init__(self, low, high, **kwargs):
        super().__init__(**kwargs)
        self.low = low
        self.high = high

    def post_call(self, stack_trace=None, *args, **kwargs):
        stack_trace[-2].value = np.random.uniform(self.low, self.high)
