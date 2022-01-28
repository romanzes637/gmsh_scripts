from src.ml.feature.setter.setter import Setter


class Variable(Setter):
    def __init__(self):
        super().__init__()

    def __call__(self, feature, *args, **kwargs):
        feature.value = None
        return feature.value
