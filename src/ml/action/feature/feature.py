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
    def get_features(action=None, prev_action=None, sep='.', key='', features=None):
        features = {} if features is None else features
        if action is None:  # super end
            return features
        k = '' if getattr(action, 'key', '') is None else getattr(action, 'key', '')
        if prev_action is None:  # root
            key = k
            if isinstance(action, Feature):
                if key in features:
                    logging.warning(f'Duplicate feature {key}: '
                                    f'{features[key]} replaced by {action.value}')
                features[key] = action.value
            Feature.get_features(action.sup_action, action, sep, key, features)
            for s in action.sub_actions:
                Feature.get_features(s, action, sep, key, features)
        else:
            if prev_action.sup_action == action:  # sup action
                key = sep.join([k, key])
                if isinstance(action, Feature):
                    if key in features:
                        logging.warning(f'Duplicate feature {key}: {features[key]} '
                                        f'replaced by {action.value}')
                    features[key] = action.value
                Feature.get_features(action.sup_action, action, sep, key, features)
                for s in action.sub_actions:
                    if s != prev_action:
                        Feature.get_features(s, action, sep, key, features)
            else:  # sub action
                key = sep.join([key, k])
                if isinstance(action, Feature):
                    if key in features:
                        logging.warning(f'Duplicate feature {key}: {features[key]} replaced by {action.value}')
                    features[key] = action.value
                for s in action.sub_actions:
                    Feature.get_features(s, action, sep, key, features)
        return features
