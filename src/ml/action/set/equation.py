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
        context = {}
        feature = stack_trace[-2]
        Feature.update_context(context, feature)
        v = self.parse(self.equation, context, self.regex)
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

    @staticmethod
    def parse(v, c, r):
        p = re.compile(r)
        cnt = 0
        m = p.search(v)
        while m is not None:
            cnt += 1
            x = ''.join(x for x in m.group(0) if x.isalnum() or x in ['-', '_', '.'])
            fv = str(c.get(x, None))
            if fv is None:
                raise ValueError(x)
            v = v[:m.start()] + fv + v[m.end():]
            m = p.search(v)
        if cnt == 0:
            raise ValueError(f'No pattern in string "{v}"')
        return v
