from src.ml.feature.setter.setter import Setter
import re


class Regex(Setter):
    def __init__(self, regex, text, value_type='str'):
        super().__init__()
        self.regex = regex
        self.text = text
        self.value_type = value_type

    str_to_type = {'str': str, 'int': int, 'float': float, 'bool': bool}

    def __call__(self, feature, *args, **kwargs):
        if self.regex is None or self.text is None:
            v = None
        else:
            r = re.findall(self.regex, self.text)
            t = self.str_to_type[self.value_type]
            if len(r) == 0:
                v = None
            elif len(r) == 1:
                v = t(r[0].strip())
            else:
                v = [t(x.strip()) for x in r]
        feature.value = v
        return feature.value
