import yaml
import json


def load(path):
    with open(path) as f:
        if path.suffix == '.json':
            data = json.load(f)
        elif path.suffix in ['.yml', '.yaml']:
            data = yaml.safe_load(f)
        else:
            raise ValueError(f"Wrong file format {path.suffix}!")
    return data
