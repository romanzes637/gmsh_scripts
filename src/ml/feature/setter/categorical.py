from src.ml.feature.setter.variable import Variable
import numpy as np


class Categorical(Variable):
    def __init__(self, choices):
        super().__init__()
        self.choices = choices

    def __call__(self, feature, *args, **kwargs):
        feature.value = np.random.choice(self.choices)
        return feature.value
