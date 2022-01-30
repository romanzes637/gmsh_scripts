"""

TODO remove eval?
"""

import re
import numpy as np

from src.ml.action.set.variable import Variable
from src.ml.action.feature.feature import Feature


class Equation(Variable):
    def __init__(self, equation, regex='\{[A-Za-z0-9\-\_]*\}', **kwargs):
        super().__init__(**kwargs)
        self.equation = equation
        self.regex = regex

    def post_call(self, action=None, *args, **kwargs):
        if isinstance(action, Feature):
            v = self.parse(self.equation, self.sub_actions, self.regex)
            v = eval(v)
            if isinstance(v, str):
                if v.isdigit():
                    v = int(v)
                else:
                    try:
                        v = float(v)
                    except ValueError:
                        pass
            action.value = v
            return action

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
