import numpy as np

from src.ml.action.set.variable import Variable
from src.ml.action.feature.feature import Feature


class Categorical(Variable):
    def __init__(self, choices, **kwargs):
        super().__init__(**kwargs)
        self.choices = choices

    def post_call(self, action=None, *args, **kwargs):
        if isinstance(action, Feature):
            action.value = np.random.choice(self.choices)
        return self, action
