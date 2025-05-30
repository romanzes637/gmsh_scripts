from pathlib import Path

from gmsh_scripts.load import load


class FactoryClassError(Exception):

    def __init__(self, value):
        self.value = value

    def __str__(self):
        return str(self.value)


class FactoryKeyError(Exception):

    def __init__(self, value):
        self.value = value

    def __str__(self):
        return str(self.value)


class FactoryValueError(Exception):

    def __init__(self, value):
        self.value = value

    def __str__(self):
        return str(self.value)


class Factory:
    def __init__(self):
        # Import str2objs
        str2objs = []
        from gmsh_scripts.block.block import str2obj
        str2objs.append({f'block.{k}': v for k, v in str2obj.items()})
        from gmsh_scripts.boolean.boolean import str2obj
        str2objs.append({f'boolean.{k}': v for k, v in str2obj.items()})
        from gmsh_scripts.coordinate_system.coordinate_system import str2obj
        str2objs.append({f'coordinate_system.{k}': v for k, v in str2obj.items()})
        from gmsh_scripts.entity.curve import str2obj
        str2objs.append({f'curve.{k}': v for k, v in str2obj.items()})
        from gmsh_scripts.entity.curve_loop import str2obj
        str2objs.append({f'curve_loop.{k}': v for k, v in str2obj.items()})
        from gmsh_scripts.block.layer import str2obj
        str2objs.append({f'block.{k}': v for k, v in str2obj.items()})
        from gmsh_scripts.block.matrix import str2obj
        str2objs.append({f'block.{k}': v for k, v in str2obj.items()})
        from gmsh_scripts.block.polyhedron import str2obj
        str2objs.append({f'block.{k}': v for k, v in str2obj.items()})
        from gmsh_scripts.block.quarter_layer import str2obj
        str2objs.append({f'block.{k}': v for k, v in str2obj.items()})
        from gmsh_scripts.block.half_layer import str2obj
        str2objs.append({f'block.{k}': v for k, v in str2obj.items()})
        from gmsh_scripts.entity.point import str2obj
        str2objs.append({f'point.{k}': v for k, v in str2obj.items()})
        from gmsh_scripts.quadrate.quadrate import str2obj
        str2objs.append({f'quadrate.{k}': v for k, v in str2obj.items()})
        from gmsh_scripts.size.size import str2obj
        str2objs.append({f'size.{k}': v for k, v in str2obj.items()})
        from gmsh_scripts.strategy.strategy import str2obj
        str2objs.append({f'strategy.{k}': v for k, v in str2obj.items()})
        from gmsh_scripts.structure.structure import str2obj
        str2objs.append({f'structure.{k}': v for k, v in str2obj.items()})
        from gmsh_scripts.entity.surface import str2obj
        str2objs.append({f'surface.{k}': v for k, v in str2obj.items()})
        from gmsh_scripts.entity.surface_loop import str2obj
        str2objs.append({f'surface_loop.{k}': v for k, v in str2obj.items()})
        from gmsh_scripts.transform.transform import str2obj
        str2objs.append({f'transform.{k}': v for k, v in str2obj.items()})
        from gmsh_scripts.entity.volume import str2obj
        str2objs.append({f'volume.{k}': v for k, v in str2obj.items()})
        from gmsh_scripts.zone.zone import str2obj
        str2objs.append({f'zone.{k}': v for k, v in str2obj.items()})
        from gmsh_scripts.optimize.optimize import str2obj
        str2objs.append({f'optimize.{k}': v for k, v in str2obj.items()})
        from gmsh_scripts.refine.refine import str2obj
        str2objs.append({f'refine.{k}': v for k, v in str2obj.items()})
        from gmsh_scripts.smooth.smooth import str2obj
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
            if 'class' in obj:
                key, args, kwargs = obj.pop('class'), [], obj
            else:
                raise FactoryClassError(obj)
        elif isinstance(obj, list) and len(obj) > 1:
            key, args, kwargs = obj[0], obj[1:], {}
        elif isinstance(obj, str):
            if obj.startswith('/'):
                p = Path(obj)
                data = load(p)
                if 'class' in data:
                    key, args, kwargs = data.pop('class'), [], data
                else:
                    raise FactoryClassError(obj)
            else:
                key, args, kwargs = obj, [], {}
        else:
            raise FactoryValueError(obj)
        if isinstance(key, str) and key in self.str2obj:
            return self.str2obj[key](*args, **kwargs)
        else:
            raise FactoryKeyError(key)


FACTORY = Factory()
