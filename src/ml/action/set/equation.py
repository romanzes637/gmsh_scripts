"""

TODO remove eval?
"""

import re
import numpy as np

from src.ml.action.set.variable import Variable
from src.ml.action.feature.feature import Feature


class Equation(Variable):
    def __init__(self, equation, regex='\{[.A-Za-z0-9\-\_]*\}', depth=-2,
                 **kwargs):
        super().__init__(**kwargs)
        self.equation = equation
        self.regex = regex
        self.depth = depth

    def post_call(self, stack_trace=None, *args, **kwargs):
        v = self.parse(self.equation, stack_trace[self.depth].sub_actions,
                       self.regex)
        v = eval(v)
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
    def parse(v, acs, r):
        p = re.compile(r)
        cnt = 0
        m = p.search(v)
        while m is not None:
            cnt += 1
            x = ''.join(x for x in m.group(0) if x.isalnum() or x in ['-', '_', '.'])
            if not x.isdigit():
                fv = None
                for f in acs:
                    if isinstance(f, Feature):
                        if x == f.key:
                            fv = str(f.value)
                if fv is None:
                    raise ValueError(x)
            else:
                fv = str(acs[int(x)].value)
            v = v[:m.start()] + fv + v[m.end():]
            m = p.search(v)
        if cnt == 0:
            raise ValueError(f'No pattern in string "{v}"')
        return v
