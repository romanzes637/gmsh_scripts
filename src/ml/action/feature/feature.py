"""Feature - key-value object

TODO return generator from get/set?
    yield from (x.get() for x in self.subfeatures)
    yield self.getter(self)
TODO concurrent get/set (ThreadPoolExecutor)?
    if self.executor == 'thread':
        executor = concurrent.futures.ThreadPoolExecutor()
    elif self.executor == 'process':
        executor = concurrent.futures.ProcessPoolExecutor()
    else:  # consecutive
        executor = None
    rs = []
    if executor is not None:
        for future in concurrent.futures.as_completed(executor.submit(
                x.get, *args, **kwargs) for x in self.subfeatures):
            rs.append(future.result())  # yield future.result()?
        executor.shutdown()
        rs.append(self.getter(self))  # yield self.getter(self)?
    else:
        rs = [x.get() for x in self.subfeatures] + [self.getter(self)]
    return rs
"""

from src.ml.action.action import Action


class Feature(Action):
    """Feature - key-value object

     Args:
        key (str): name of the feature
        value (object): value of the feature
        getter (collections.abc.Callable): callable that use feature
        setter (collections.abc.Callable): callable that update feature
    """

    def __init__(self, tag=None, subactions=None, executor=None,
                 episode=None, do_propagate_episode=None,
                 key=None, value=None, getter=None, setter=None):
        super().__init__(tag=tag, subactions=subactions, executor=executor,
                         episode=episode, do_propagate_episode=do_propagate_episode)
        self.key = key
        self.value = value
        self.getter = getter
        self.setter = setter

    def get(self):
        return self.getter(self) if self.getter is not None else self

    def set(self):
        return self.setter(self) if self.setter is not None else self

    def call(self, *args, **kwargs):
        self.set()
        self.get()
        return self

    def __call__(self, *args, **kwargs):
        super().__call__(*args, **kwargs)
        if self.episode is not None:
            return self.episode(self.call)(self, *args, **kwargs)
        else:
            return self.call(self, *args, **kwargs)
