"""FOAM dictionary

TODO parse list, table, vector, tensor
"""
from pathlib import Path

from src.ml.action.get.get import Get
from src.ml.action.get.json import Json
from src.ml.action.feature.feature import Feature


class Dictionary(Get):
    def __init__(self, path, mapping, regex='\{[.A-Za-z0-9\-\_]*\}', dump_path=None,
                 **kwargs):
        super().__init__(**kwargs)
        self.path = path
        self.dump_path = path if dump_path is None else dump_path
        self.mapping = mapping
        for k in list(self.mapping.keys()):
            if k == '':
                self.mapping[None] = self.mapping.pop(k)
        self.regex = regex

    def post_call(self, stack_trace=None, *args, **kwargs):
        p = Path(self.path).resolve()
        d = self.load(p)
        features = Feature.get_features(stack_trace[-2])
        d = Json.update(d, self.mapping, features, self.regex)
        dp = Path(self.dump_path).resolve()
        dp.parent.mkdir(parents=True, exist_ok=True)
        self.dump(d, dp)

    @staticmethod
    def load(path):
        d = {}
        with open(path) as f:
            name, kvs = Dictionary.load_object(f)
            while name is not None or len(kvs) > 0:
                d[name] = kvs
                name, kvs = Dictionary.load_object(f)
        return d

    @staticmethod
    def load_object(f, name=None):
        kvs = {}  # key-values
        is_comment = False
        for line in f:
            line = line.strip()
            if line.startswith('/*'):
                is_comment = True
            if line.endswith('*/'):
                is_comment = False
                continue
            if line.startswith('//') or line == '':
                continue
            if not is_comment:
                line = line.split('//')[0].strip()  # remove inline comments
                line = line.replace(';', '')  # remove ending ;
                ts = line.split()  # tokens
                k, vs = ts[0], ts[1:]
                if len(vs) == 0:
                    if k == '{':
                        continue
                    elif k == '}':
                        break
                    elif name is None and len(kvs) == 0:
                        name = k
                    else:
                        sub_name, sub_kvs = Dictionary.load_object(f, k)
                        kvs[sub_name] = sub_kvs
                elif len(vs) == 1:
                    kvs[k] = vs[0]
                else:  # list
                    if vs[0] in ('uniform', 'nonuniform', 'constant'):  # Workaround
                        k += f' {vs[0]}'
                        vs = vs[1:]
                    new_vs = []
                    for v in vs:
                        v = v.replace('(', '').replace(')', '')
                        if v != '':
                            new_vs.append(v)
                    kvs[k] = new_vs
        return name, kvs

    @staticmethod
    def dump(dictionary, path):
        with open(path, 'w') as f:
            for name, kvs in dictionary.items():
                Dictionary.dump_object(name, kvs, f)

    @staticmethod
    def dump_object(name, kvs, f):
        if name is not None:
            f.write(f'{name}\n')
            f.write('{\n')
        for k, v in kvs.items():
            if isinstance(v, list):
                f.write(f'{k} ({" ".join([str(x) for x in v])});\n')
            elif isinstance(v, dict):
                Dictionary.dump_object(k, v, f)
            else:
                f.write(f'{k} {v};\n')
        if name is not None:
            f.write('}\n')
