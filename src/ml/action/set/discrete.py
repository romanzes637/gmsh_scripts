import numpy as np

from src.ml.action.set.variable import Variable


class Discrete(Variable):
    def __init__(self, low, high, num=None, **kwargs):
        super().__init__(**kwargs)
        self.low = low
        self.high = high
        self.num = int(self.high - self.low) + 1 if num is None else num

    def post_call(self, stack_trace=None, *args, **kwargs):
        v = np.random.choice(np.linspace(
            self.low, self.high, self.num, endpoint=True))
        if isinstance(self.low, int) and isinstance(self.high, int):
            v = int(v)
        stack_trace[-2].value = v
