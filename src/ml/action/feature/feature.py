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
import logging


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

    @staticmethod
    def update_context(context, a=None, prev_a=None, key='', sep='.'):
        if a is None:  # top end
            return
        k = '' if getattr(a, 'key', '') is None else getattr(a, 'key', '')
        if prev_a is None:  # root
            if isinstance(a, Feature):
                key = k
                if key in context:
                    logging.warning(f'Duplicate feature {key}: '
                                    f'{context[key]} replaced by {a.value}')
                context[key] = a.value
            Feature.update_context(context, a.sup_action, a, key, sep)
            for s in a.sub_actions:
                Feature.update_context(context, s, a, key, sep)
        else:
            if prev_a.sup_action == a:  # sup action
                key = sep.join([k, key])
                if isinstance(a, Feature):
                    if key in context:
                        logging.warning(f'Duplicate feature {key}: {context[key]} '
                                        f'replaced by {a.value}')
                    context[key] = a.value
                Feature.update_context(context, a.sup_action, a, key, sep)
                for s in a.sub_actions:
                    if s != prev_a:
                        Feature.update_context(context, s, a, key, sep)
            else:  # sub action
                key = sep.join([key, k])
                if isinstance(a, Feature):
                    if key in context:
                        logging.warning(f'Duplicate feature {key}: {context[key]} replaced by {a.value}')
                    context[key] = a.value
                for s in a.sub_actions:
                    Feature.update_context(context, s, a, key, sep)
