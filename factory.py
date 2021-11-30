import json

from support import check_on_file


class Factory:
    def __init__(self):
        # Import str2objs
        str2objs = []
        from block import str2obj
        str2objs.append({f'block.{k}': v for k, v in str2obj.items()})
        from boolean import str2obj
        str2objs.append({f'boolean.{k}': v for k, v in str2obj.items()})
        from coordinate_system import str2obj
        str2objs.append({f'coordinate_system.{k}': v for k, v in str2obj.items()})
        from curve import str2obj
        str2objs.append({f'curve.{k}': v for k, v in str2obj.items()})
        from curve_loop import str2obj
        str2objs.append({f'curve_loop.{k}': v for k, v in str2obj.items()})
        from layer import str2obj
        str2objs.append({f'block.{k}': v for k, v in str2obj.items()})
        from matrix import str2obj
        str2objs.append({f'block.{k}': v for k, v in str2obj.items()})
        from point import str2obj
        str2objs.append({f'point.{k}': v for k, v in str2obj.items()})
        from quadrate import str2obj
        str2objs.append({f'quadrate.{k}': v for k, v in str2obj.items()})
        from size import str2obj
        str2objs.append({f'size.{k}': v for k, v in str2obj.items()})
        from strategy import str2obj
        str2objs.append({f'strategy.{k}': v for k, v in str2obj.items()})
        from structure import str2obj
        str2objs.append({f'structure.{k}': v for k, v in str2obj.items()})
        from surface import str2obj
        str2objs.append({f'surface.{k}': v for k, v in str2obj.items()})
        from surface_loop import str2obj
        str2objs.append({f'surface_loop.{k}': v for k, v in str2obj.items()})
        from transform import str2obj
        str2objs.append({f'transform.{k}': v for k, v in str2obj.items()})
        from volume import str2obj
        str2objs.append({f'volume.{k}': v for k, v in str2obj.items()})
        from zone import str2obj
        str2objs.append({f'zone.{k}': v for k, v in str2obj.items()})
        from optimize import str2obj
        str2objs.append({f'optimize.{k}': v for k, v in str2obj.items()})
        from refine import str2obj
        str2objs.append({f'refine.{k}': v for k, v in str2obj.items()})
        from smooth import str2obj
        str2objs.append({f'smooth.{k}': v for k, v in str2obj.items()})
        # Make global str2obj and obj2str(s)
        str2obj, obj2str = {}, {}
        for s2o in str2objs:
            for k, v in s2o.items():
                if k not in str2obj:
                    str2obj[k] = v
                    obj2str.setdefault(v, []).append(k)
                else:
                    raise ValueError(f'Duplicate keys: {k}')
        self.str2obj = str2obj
        self.obj2str = obj2str

    def __call__(self, obj):
        if isinstance(obj, dict):
            key, args, kwargs = obj.pop('class'), [], obj
        elif isinstance(obj, list) and len(obj) > 1:
            key, args, kwargs = obj[0], obj[1:], {}
        elif isinstance(obj, str):
            result, path = check_on_file(obj)  # Check on path to file
            if result is None:  # obj is a key
                key, args, kwargs = obj, [], {}
            else:  # obj is a path
                with open(path) as f:
                    data = json.load(f)
                key, args, kwargs = data.pop('class'), [], data
        else:
            raise ValueError(obj)
        if isinstance(key, str) and key in self.str2obj:
            return self.str2obj[key](*args, **kwargs)
        else:
            raise KeyError(key)


FACTORY = Factory()
