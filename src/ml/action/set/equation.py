"""

TODO remove eval?
"""

import re
import numpy as np

from src.ml.action.set.variable import Variable
from src.ml.action.feature.feature import Feature


class Equation(Variable):
    def __init__(self, equation, regex='\{[.A-Za-z0-9\-\_]*\}', **kwargs):
        super().__init__(**kwargs)
        self.equation = equation
        self.regex = regex

    def post_call(self, stack_trace=None, *args, **kwargs):
        features = Feature.get_features(stack_trace[-2])
        v = self.parse(self.equation, features, self.regex)
        print(features)
        print(v)
        v = eval(v)
        print(v)
        if isinstance(v, str):
            if v.isdigit():
                v = int(v)
            else:
                try:
                    v = float(v)
                except ValueError:
                    pass
        stack_trace[-2].value = v

    @staticmethod
    def parse(v, fs, r):
        p = re.compile(r)
        cnt = 0
        m = p.search(v)
        while m is not None:
            cnt += 1
            x = ''.join(x for x in m.group(0) if x.isalnum() or x in ['-', '_', '.'])
            if x not in fs:
                ks = '"\n"'.join(fs.keys())
                raise ValueError(f'Key "{x}" is not in features keys:\n"{ks}"')
            value = str(fs[x])
            v = v[:m.start()] + value + v[m.end():]
            m = p.search(v)
        if cnt == 0:
            raise ValueError(f'No pattern in string "{v}"')
        return v
