from src.ml.feature.setter.setter import Setter


class Value(Setter):
    def __init__(self, value):
        super().__init__()
        self.value = value

    def __call__(self, feature, *args, **kwargs):
        feature.value = self.value
        return self.value
