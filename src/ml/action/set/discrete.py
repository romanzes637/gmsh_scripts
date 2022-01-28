from src.ml.action.set.variable import Variable
import numpy as np


class Discrete(Variable):
    def __init__(self, low, high, num,
                 tag=None, subactions=None, executor=None,
                 episode=None, do_propagate_episode=None):
        super().__init__(tag=tag, subactions=subactions, executor=executor,
                         episode=episode, do_propagate_episode=do_propagate_episode)
        self.low = low
        self.high = high
        self.num = num

    def __call__(self, feature, *args, **kwargs):
        v = np.random.choice(np.linspace(
            self.low, self.high, self.num, endpoint=True))
        if isinstance(self.low, int) and isinstance(self.high, int):
            v = int(v)
        feature.value = v
        return feature
