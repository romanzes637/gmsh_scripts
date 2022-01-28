import re
from pathlib import Path

from src.ml.feature.setter.setter import Setter


class RegexFile(Setter):
    def __init__(self, regex, path, value_type='str'):
        super().__init__()
        self.regex = regex
        self.path = path
        self.value_type = value_type

    str_to_type = {'str': str, 'int': int, 'float': float, 'bool': bool}

    def __call__(self, feature, *args, **kwargs):
        if self.regex is None or self.path is None:
            v = None
        else:
            p = Path(self.path).resolve()
            if p.exists() and p.is_file():
                t = self.str_to_type[self.value_type]
                rs = []
                with open(p) as f:
                    for line in f:
                        r = re.findall(self.regex, line)
                        rs.extend(r)
                if len(rs) == 0:
                    v = None
                elif len(rs) == 1:
                    v = t(rs[0].strip())
                else:
                    v = [t(x.strip()) for x in rs]
            else:
                v = None
        feature.value = v
        return feature.value
