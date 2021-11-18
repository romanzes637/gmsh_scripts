import json

from support import check_on_file


class Factory:
    def __init__(self, local_factories=None):
        if local_factories is None:
            local_factories = []
            from strategy import factory as strategy_factory
            local_factories.append({f'strategy.{k}': v
                                    for k, v in strategy_factory.items()})
            from transform import factory as transform_factory
            local_factories.append({f'transform.{k}': v
                                    for k, v in transform_factory.items()})

            from coordinate_system import factory as coordinate_system_factory
            local_factories.append({f'coordinate_system.{k}': v
                                    for k, v in coordinate_system_factory.items()})
            from point import factory as point_factory
            local_factories.append({f'point.{k}': v
                                    for k, v in point_factory.items()})
            from block import Block
            local_factories.append({f'block.Block': Block})
        global_factory = {}
        for f in local_factories:
            for k, v in f.items():
                if k in global_factory:
                    raise ValueError(f'Duplicate keys: {k}')
                else:
                    global_factory[k] = v
        self.global_factory = global_factory

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
        return self.global_factory[key](*args, **kwargs)


FACTORY = Factory()  # Global factory
