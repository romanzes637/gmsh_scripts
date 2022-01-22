"""
Update json file by list of variables maps {}

"""

import json
from copy import deepcopy

from src.ml.variable.variable import Variable
from src.ml.action.action import Action


def sample(d):
    """Sample Variables in the nested dictionary d

    Args:
        d (dict): nested dictionary with Variables

    Returns:
        dict: nested dictionary with sampled Variables
    """
    if isinstance(d, dict):
        for k, v in d.items():
            if isinstance(v, Variable):
                d[k] = v()
            else:
                sample(v)
    elif isinstance(d, list):
        for i, v in enumerate(d):
            if isinstance(v, Variable):
                d[i] = v()
            else:
                sample(v)
    return d


def update(d, u):
    """Update nested dictionary d by nested dictionary u
    By https://stackoverflow.com/questions/3232943/update-value-of-a-nested-dictionary-of-varying-depth

    Args:
        d (dict): nested dictionary to update
        u (dict): nested dictionary update from

    Returns:
        dict: updated nested dictionary
    """
    for k, v in u.items():
        if isinstance(v, dict):
            d[k] = update(d.get(k, {}), v)
        else:
            d[k] = v
    return d


def features(var, s, fs=None):
    fs = {} if fs is None else fs
    for k, v in s.items():
        if isinstance(v, dict):
            features(var[k], s[k], fs)
        else:
            fs[var[k].name] = v
    return fs


class GmshScripts(Action):
    def __init__(self, tag=None, subactions=None, executor=None,
                 episode=None, do_propagate_episode=None,
                 path=None, new_path=None, variables=None):
        super().__init__(tag=tag, subactions=subactions, executor=executor,
                         episode=episode, do_propagate_episode=do_propagate_episode)
        self.path = path
        self.new_path = new_path
        self.variables = [] if variables is None else variables

    def __call__(self, *args, **kwargs):
        def call(self, *args, **kwargs):
            super().__call__(*args, **kwargs)
            with open(self.path) as f:
                d = json.load(f)
            samples = [sample(deepcopy(x)) for x in self.variables]
            for s in samples:
                update(d, s)
            with open(self.new_path, 'w') as f:
                json.dump(d, f, indent=2)
            fs = {}  # return features
            for v, s in zip(self.variables, samples):
                fs = features(v, s, fs)
            return fs

        if self.episode is not None:
            return self.episode(call)(self, *args, **kwargs)
        else:
            return call(self, *args, **kwargs)
