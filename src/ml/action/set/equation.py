"""

TODO remove eval?
"""

import re
import numpy as np

from src.ml.action.set.variable import Variable


class Equation(Variable):
    def __init__(self, equation, features=None, regex='\{[A-Za-z0-9\-\_]*\}',
                 tag=None, subactions=None, executor=None,
                 episode=None, do_propagate_episode=None):
        super().__init__(tag=tag, subactions=subactions, executor=executor,
                         episode=episode, do_propagate_episode=do_propagate_episode)
        self.equation = equation
        self.regex = regex
        self.features = [] if features is None else features

    def __call__(self, feature, *args, **kwargs):
        for f in self.features:
            f.set()
        v = self.parse(self.equation, self.features, self.regex)
        v = eval(v)
        if isinstance(v, str):
            if v.isdigit():
                v = int(v)
            else:
                try:
                    v = float(v)
                except ValueError:
                    pass
        feature.value = v
        return feature

    @staticmethod
    def parse(v, fs, r):
        p = re.compile(r)
        cnt = 0
        m = p.search(v)
        while m is not None:
            cnt += 1
            x = ''.join(x for x in m.group(0) if x.isalnum() or x in ['-', '_'])
            if not x.isdigit():
                raise ValueError(f'Should be digit "{x}"')
            fv = str(fs[int(x)].value)
            v = v[:m.start()] + fv + v[m.end():]
            m = p.search(v)
        if cnt == 0:
            raise ValueError(f'No pattern in string "{v}"')
        return v
