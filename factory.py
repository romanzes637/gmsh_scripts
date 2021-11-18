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
        str2objs.append({f'layer.{k}': v for k, v in str2obj.items()})
        from matrix import str2obj
        str2objs.append({f'matrix.{k}': v for k, v in str2obj.items()})
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

    def __call__(self, string=None, args=None, kwargs=None):
        args = [] if args is None else args
        kwargs = {} if kwargs is None else kwargs
        if string is not None:
            result, path = check_on_file(string)  # Check on path to file
            if result is not None:  # string is a path
                with open(path) as f:
                    data = json.load(f)
                kwargs.update(data['data'])  # Update kwargs from file data
                key = kwargs.pop('class')  # key in the kwargs
            else:  # string is a key
                key = string
        else:  # string is None
            if 'class' in kwargs:  # key in the kwargs
                key = kwargs.pop('class')
            elif len(args) > 0:  # key is the first item in args
                key, args = args[0], args[1:]
            else:  # No key!
                raise ValueError(f'No key found in {string}, {args}, {kwargs}!')
        return self.str2obj[key](*args, **kwargs)


FACTORY = Factory()
