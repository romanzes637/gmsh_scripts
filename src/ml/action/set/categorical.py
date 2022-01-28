from src.ml.action.set.variable import Variable
import numpy as np


class Categorical(Variable):
    def __init__(self, choices,
                 tag=None, subactions=None, executor=None,
                 episode=None, do_propagate_episode=None):
        super().__init__(tag=tag, subactions=subactions, executor=executor,
                         episode=episode, do_propagate_episode=do_propagate_episode)
        self.choices = choices

    def __call__(self, feature, *args, **kwargs):
        feature.value = np.random.choice(self.choices)
        return feature
