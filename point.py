import logging

import numpy as np

from coordinate_system import factory as cs_factory
from coordinate_system import CoordinateSystem, Cartesian, Cylindrical, \
    Spherical, Toroidal, Tokamak


class Point:
    """Point
    Args:
        tag (int or None): unique id
        zone (str or None): zone
        coordinate_system (str or dict or CoordinateSystem or None): coordinate system
        coordinates (list of float or np.ndarray or None): coordinates values

    Attributes:
        tag (int or None): unique id
        zone (str or None): zone
        coordinate_system (CoordinateSystem): coordinate system
        coordinates (np.ndarray): coordinates values
        kwargs (dict or None): other keyword arguments (e.g. meshSize)
    """

    def __init__(self, *args, tag=None, zone=None, coordinate_system=None,
                 coordinates=None, **kwargs):
        if len(args) > 0:
            tag, zone, coordinate_system, coordinates, kwargs = self.parse_args(args)
        self.tag = tag
        self.zone = zone
        self.coordinate_system = self.parse_coordinate_system(coordinate_system)
        self.coordinates = self.parse_coordinates(coordinates, self.coordinate_system)
        self.kwargs = kwargs

    @staticmethod
    def parse_coordinate_system(coordinate_system, default=Cartesian(),
                                name_key='name'):
        if coordinate_system is None:
            coordinate_system = default
        elif isinstance(coordinate_system, CoordinateSystem):
            pass
        elif isinstance(coordinate_system, str):
            coordinate_system = cs_factory[coordinate_system]()
        elif isinstance(coordinate_system, dict):
            name = coordinate_system[name_key]
            coordinate_system = cs_factory[name](**coordinate_system)
        else:
            raise ValueError(coordinate_system)
        return coordinate_system

    @staticmethod
    def parse_coordinates(coordinates, coordinate_system):
        if coordinates is None:
            coordinates = np.zeros(coordinate_system.dim)
        elif isinstance(coordinates, np.ndarray):
            pass
        elif isinstance(coordinates, list):
            coordinates = np.array(coordinates)
        else:
            raise ValueError(coordinates)
        return coordinates

    @staticmethod
    def parse_args(args):
        tag, zone = None, None
        coordinate_system, coordinates, kwargs = None, None, {}
        if len(args) == 1 and isinstance(args[0], list):  # init by list
            a = args[0]
            n_nums = 0  # number of numerical items in a
            for x in a:
                if not isinstance(x, float) and not isinstance(x, int):
                    break
                else:
                    n_nums += 1
            nums, others = a[:n_nums], a[n_nums:]
            # Process others
            if len(others) == 0:
                coordinate_system = Point.parse_coordinate_system(coordinate_system)  # default
            elif len(others) == 1:  # coordinate system or zone
                o1 = others[0]
                if isinstance(o1, str):
                    if o1 in cs_factory:  # coordinate system
                        coordinate_system = Point.parse_coordinate_system(o1)
                        logging.warning(f'May be a name conflict between zone and coordinate system: {o1}')
                    else:  # zone
                        coordinate_system = Point.parse_coordinate_system(coordinate_system)  # default
                        zone = o1
                else:
                    coordinate_system = Point.parse_coordinate_system(o1)
            elif len(others) == 2:  # coordinate system and zone
                o1, o2 = others
                coordinate_system = Point.parse_coordinate_system(o1)
                zone = o2
            else:
                raise ValueError(a)
            # Split nums into coordinates and meshSize
            if n_nums == coordinate_system.dim:  # coordinates, ...
                coordinates = nums
            elif n_nums - 1 == coordinate_system.dim:  # coordinates, meshSize, ...
                coordinates = nums[:-1]
                kwargs['meshSize'] = nums[-1]
            else:
                raise ValueError(a)
        else:
            raise ValueError(args)
        return tag, zone, coordinate_system, coordinates, kwargs

    @staticmethod
    def parse_points(points):
        """Parse list of raw points
        Patterns
        1. [[], [], [], ...]
        2. [[], [], [], ..., coordinate_system]
        3. [{}, {}, {}, ...]
        4. [{}, {}, {}, ..., coordinate_system]

        Args:
            points (list of list or list of dict): raw points

        Returns:
            points (list of Point): points
        """
        points = [] if points is None else points
        if len(points) == 0:
            pass
        elif isinstance(points[-1], str):
            points, cs_name = points[:-1], points[-1]
            for i, p in enumerate(points):  # Add coordinate system if not
                if isinstance(p, dict):
                    points[i].setdefault('coordinate_system', cs_name)
                elif isinstance(p, list):
                    add_cs = True
                    for x in p:
                        if x in cs_factory:  # CS already exists
                            add_cs = False
                            break
                    if add_cs:
                        n_nums = 0
                        for x in p:
                            if not isinstance(x, float) and not isinstance(x, int):
                                break
                            else:
                                n_nums += 1
                        points[i] = p[:n_nums] + [cs_name] + p[n_nums:]
            points = Point.parse_points(points)
        else:
            for i, p in enumerate(points):
                if isinstance(p, dict):
                    p = Point(**p)
                elif isinstance(p, list):
                    p = Point(p)
                else:
                    raise ValueError(p)
                if isinstance(p.coordinate_system, Cylindrical):
                    p.coordinates[1] = np.deg2rad(p.coordinates[1])
                elif any([isinstance(p.coordinate_system, Spherical),
                          isinstance(p.coordinate_system, Toroidal),
                          isinstance(p.coordinate_system, Tokamak)]):
                    p.coordinates[1] = np.deg2rad(p.coordinates[1])
                    p.coordinates[2] = np.deg2rad(p.coordinates[2])
                points[i] = p
        return points


factory = {
    Point.__name__: Point,
    Point.__name__.lower(): Point
}
