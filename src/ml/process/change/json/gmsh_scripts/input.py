import json
from copy import deepcopy

from src.ml.variable.variable import Variable
from src.ml.process.process import Process


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


class Input(Process):
    def __init__(self, path=None, new_path=None, variables_map=None):
        super().__init__()
        self.path = path
        self.new_path = new_path
        self.variables_map = {} if variables_map is None else variables_map

    def __call__(self, *args, **kwargs):
        with open(self.path) as f:
            d = json.load(f)
        u = sample(deepcopy(self.variables_map))
        update(d, u)
        with open(self.new_path, 'w') as f:
            json.dump(d, f, indent=2)
