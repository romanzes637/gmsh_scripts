class Feature:
    """Feature - key-value object

     Args:
        key (str): name of the feature
        value (object): value of the feature
        getter (collections.abc.Callable): callable that use feature
        setter (collections.abc.Callable): callable that update feature
    """
    def __init__(self, key=None, value=None, getter=None, setter=None):
        self.key = key
        self.value = value
        self.getter = getter
        self.setter = setter

    def get(self):
        return self.getter(self)

    def set(self):
        return self.setter(self)
