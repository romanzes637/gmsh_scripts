import numpy as np

from src.ml.action.set.variable import Variable


class Categorical(Variable):
    def __init__(self, choices, **kwargs):
        super().__init__(**kwargs)
        self.choices = choices

    def post_call(self, actions=None, *args, **kwargs):
        actions[-2].value = np.random.choice(self.choices)
