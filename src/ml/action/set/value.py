from src.ml.action.set.set import Set


class Value(Set):
    def __init__(self, value, **kwargs):
        super().__init__(**kwargs)
        self.value = value

    def post_call(self, stack_trace=None, *args, **kwargs):
        stack_trace[-2].value = self.value
