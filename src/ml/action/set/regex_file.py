"""Set from file by regex expression

1. Regex groups and ranges https://developer.mozilla.org/en-US/docs/Web/JavaScript/Guide/Regular_Expressions/Groups_and_Ranges
"""

import re
from pathlib import Path

from src.ml.action.set.set import Set


class RegexFile(Set):
    def __init__(self, regex, path, value_type='str', read_type='line',
                 num='last', **kwargs):
        super().__init__(**kwargs)
        self.regex = regex
        self.path = path
        self.value_type = value_type
        self.read_type = read_type
        self.num = num

    str_to_type = {'str': str, 'int': int, 'float': float, 'bool': bool}

    def post_call(self, stack_trace=None, *args, **kwargs):
        p = Path(self.path).resolve()
        t = self.str_to_type[self.value_type]
        rs = []
        with open(p) as f:
            if self.read_type == 'line':
                for line in f:
                    r = re.findall(self.regex, line)
                    rs.extend(r)
            elif self.read_type == 'all':
                rs = re.findall(self.regex, f.read())
            else:
                raise ValueError(self.read_type)
        if len(rs) == 0:
            v = None
        elif len(rs) == 1:
            v = t(rs[0].strip())
        else:
            v = [t(x.strip()) for x in rs]
        if isinstance(v, list):
            if self.num == 'last':
                stack_trace[-2].value = v[-1]
            elif self.num == 'first':
                stack_trace[-2].value = v[0]
            elif self.num == 'all':
                stack_trace[-2].value = v
            else:
                raise ValueError(self.num)
        else:
            stack_trace[-2].value = v
