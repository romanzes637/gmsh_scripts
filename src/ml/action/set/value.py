from src.ml.action.set.set import Set
from src.ml.action.feature.feature import Feature


class Value(Set):
    def __init__(self, value, **kwargs):
        super().__init__(**kwargs)
        self.value = value

    def post_call(self, action=None, *args, **kwargs):
        if isinstance(action, Feature):
            action.value = self.value
        return self, action
