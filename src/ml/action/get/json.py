import json
from pathlib import Path
from copy import deepcopy
import re

from src.ml.action.get.get import Get
from src.ml.action.feature.feature import Feature


class Json(Get):
    def __init__(self, path, mapping, regex='\{[.A-Za-z0-9\-\_]*\}', **kwargs):
        super().__init__(**kwargs)
        self.path = path
        self.mapping = mapping
        self.regex = regex

    def post_call(self, stack_trace=None, *args, **kwargs):
        p = Path(self.path).resolve()
        with open(p) as f:
            d = json.load(f)
        features = Feature.get_features(stack_trace[-2])
        d = self.update(d, self.mapping, features, self.regex)
        with open(p, 'w') as f:
            json.dump(d, f, indent=2)

    @staticmethod
    def update(d, m, f, r):
        if isinstance(m, dict):
            if not isinstance(d, dict):
                raise ValueError(f'Bad mapping {d}, {m}')
            for k, v in m.items():
                if isinstance(v, dict):
                    d[k] = Json.update(d.get(k, {}), v, f, r)
                elif isinstance(v, list):
                    u = d.get(k, [])
                    if isinstance(u, list):
                        if len(u) != len(v):
                            d[k] = v
                        for i, x in enumerate(v):
                            if isinstance(x, dict):
                                d[k][i] = Json.update(d[k][i], x, f, r)
                            elif isinstance(x, list):
                                d[k][i] = Json.update(d[k][i], x, f, r)
                            elif x is not None:
                                d[k][i] = Json.parse(x, f, r)
                    else:
                        raise ValueError(f'Bad mapping {u}, {d}, {m}')
                else:
                    d[k] = Json.parse(v, f, r)
        elif isinstance(m, list):
            if not isinstance(d, list):
                raise ValueError(f'Bad mapping {d}, {m}')
            if len(m) != len(d):
                d = deepcopy(m)
            for i, x in enumerate(m):
                if isinstance(x, dict):
                    d[i] = Json.update(d[i], x, f, r)
                elif isinstance(x, list):
                    d[i] = Json.update(d[i], x, f, r)
                elif x is not None:
                    d[i] = Json.parse(x, f, r)
        return d

    @staticmethod
    def parse(v, fs, r):
        if isinstance(v, str):
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
                return v
            if v.isdigit():
                v = int(v)
            else:
                try:
                    v = float(v)
                except ValueError:
                    pass
            return v
        else:  # not str
            return v
