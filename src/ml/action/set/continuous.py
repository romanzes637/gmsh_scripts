from src.ml.action.set.variable import Variable
import numpy as np


class Continuous(Variable):
    def __init__(self, low, high,
                 tag=None, subactions=None, executor=None,
                 episode=None, do_propagate_episode=None):
        super().__init__(tag=tag, subactions=subactions, executor=executor,
                         episode=episode, do_propagate_episode=do_propagate_episode)
        self.low = low
        self.high = high

    def __call__(self, feature, *args, **kwargs):
        feature.value = np.random.uniform(self.low, self.high)
        return feature
