from src.ml.variable.variable import Variable
import numpy as np


class Categorical(Variable):
    def __init__(self, name=None, choices=None):
        super().__init__(name=name)
        self.choices = choices

    def __call__(self, *args, **kwargs):
        return np.random.choice(self.choices)
