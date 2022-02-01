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

from src.ml.action.coaction import Coaction


class Feature(Coaction):
    """Feature - key-value object

     Args:
        key (str): name of the feature
        value (object): value of the feature
    """

    def __init__(self, key=None, value=None, **kwargs):
        super().__init__(**kwargs)
        self.key = key
        self.value = value
