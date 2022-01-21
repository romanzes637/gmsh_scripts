import re


class Regex:
    def __init__(self, name=None, regex=None, value_type='str'):
        self.name = name
        self.regex = regex
        self.value_type = value_type

    str_to_type = {'str': str, 'int': int, 'float': float, 'bool': bool}

    def __call__(self, line=None, *args, **kwargs):
        if line is None or self.regex is None:
            return None
        else:
            r = re.findall(self.regex, line)
            t = self.str_to_type[self.value_type]
            if len(r) == 0:
                return None
            elif len(r) == 1:
                return t(r[0].strip())
            else:
                return [t(x.strip()) for x in r]
