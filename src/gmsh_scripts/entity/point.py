import numpy as np

from gmsh_scripts.coordinate_system.coordinate_system import str2obj as cs_factory
from gmsh_scripts.coordinate_system.coordinate_system import CoordinateSystem, Cartesian, Cylindrical, \
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
            coordinates = np.zeros(coordinate_system.dim, dtype=float)
        elif isinstance(coordinates, np.ndarray):
            if coordinates.dtype != float:
                coordinates = coordinates.astype(float)
        elif isinstance(coordinates, list):
            coordinates = np.array(coordinates, dtype=float)
        else:
            raise ValueError(coordinates)
        return coordinates

    @staticmethod
    def parse_args(args):
        """Parse list
        Patterns:
        1. [coordinates]
        2. [coordinates, meshSize]
        3. [coordinates, coordinate_system]
        4. [coordinates, zone]
        5. [coordinates, meshSize, coordinate_system]
        5. [coordinates, coordinate_system, zone]
        5. [coordinates, meshSize, zone]
        5. [coordinates, meshSize, coordinate_system, zone]

        Args:
            args (list):

        Returns:
            int or None, str or None, CoordinateSystem or None, list of float, dict:
        """
        tag, zone = None, None
        coordinate_system, coordinates, kwargs = None, None, {}
        if len(args) == 1 and isinstance(args[0], list):  # init by list
            a = args[0]
            n_nums = 0  # number of numerical items in a
            for x in a:
                if isinstance(x, float) or isinstance(x, int):
                    n_nums += 1
                else:
                    break
            nums, others = a[:n_nums], a[n_nums:]
            # Process others
            if len(others) == 0:
                pass  # default
            elif len(others) == 1:  # coordinate system or zone
                o1 = others[0]
                if isinstance(o1, str):
                    if o1 in cs_factory:  # coordinate system
                        coordinate_system = Point.parse_coordinate_system(o1)
                        # logging.warning(f'May be a name conflict between zone and coordinate system: {o1}')
                    else:  # zone
                        zone = o1
                else:  # coordinate system
                    coordinate_system = Point.parse_coordinate_system(o1)
            elif len(others) == 2:  # coordinate system and zone
                o1, o2 = others
                coordinate_system = Point.parse_coordinate_system(o1)
                zone = o2
            else:
                raise ValueError(a)
            # Split nums into coordinates and meshSize
            dim = coordinate_system.dim if coordinate_system is not None else Cartesian().dim
            if n_nums == dim:  # coordinates, ...
                coordinates = nums
            elif n_nums - 1 == dim:  # coordinates, meshSize, ...
                coordinates = nums[:-1]
                kwargs['meshSize'] = nums[-1]
            else:
                raise ValueError(a)
        else:
            raise ValueError(args)
        return tag, zone, coordinate_system, coordinates, kwargs

    @staticmethod
    def parse_points(points=None, do_deg2rad=False):
        """Parse list of raw points
        Patterns
        1. [[], [], [], ...]
        2. [[], [], [], ..., meshSize]
        3. [[], [], [], ..., coordinate_system]
        4. [[], [], [], ..., zone]
        5. [[], [], [], ..., meshSize, coordinate_system]
        6. [[], [], [], ..., coordinate_system, zone]
        7. [[], [], [], ..., meshSize, zone]
        8. [[], [], [], ..., meshSize, coordinate_system, zone]
        9. [{}, {}, {}, ...]
        10. [{}, {}, {}, ..., meshSize]
        11. [{}, {}, {}, ..., coordinate_system]
        12. [{}, {}, {}, ..., zone]
        13. [{}, {}, {}, ..., meshSize, coordinate_system]
        14. [{}, {}, {}, ..., coordinate_system, zone]
        15. [{}, {}, {}, ..., meshSize, zone]
        16. [{}, {}, {}, ..., meshSize, coordinate_system, zone]

        Args:
            points (list or None): raw points
            do_deg2rad (bool): do degrees to radians conversion

        Returns:
            list of Point: points objects
        """
        points = [] if points is None else points
        # Evaluate number of points
        n_points = 0
        for p in points:
            if isinstance(p, list) or isinstance(p, dict):
                n_points += 1
            else:
                break
        # Split points and others
        points, others = points[:n_points], points[n_points:]
        if len(others) > 0:
            ms, cs, z = None, None, None  # meshSize, coordinate_system, zone
            if len(others) == 1:
                o1 = others[0]
                if isinstance(o1, float) or isinstance(o1, int):
                    ms = o1
                elif isinstance(o1, str):
                    if o1 in cs_factory:  # coordinate system
                        cs = o1
                        # logging.warning(f'May be a name conflict between zone and coordinate system: {o1}')
                    else:  # zone
                        z = o1
                elif isinstance(o1, CoordinateSystem):
                    cs = o1
                else:
                    raise ValueError(others, o1)
            elif len(others) == 2:
                o1, o2 = others
                if isinstance(o1, str) and isinstance(o2, str):
                    cs, z = o1, o2
                elif isinstance(o1, float) or isinstance(o1, int):
                    ms = o1
                    if o2 in cs_factory:  # coordinate system
                        cs = o2
                        # logging.warning(f'May be a name conflict between zone and coordinate system: {o2}')
                    else:  # zone
                        z = o2
                else:
                    raise ValueError(others)
            elif len(others) == 3:
                ms, cs, z = others
            else:
                raise ValueError(others)
            for i, p in enumerate(points):
                if isinstance(p, dict):
                    p.setdefault('coordinate_system', cs)
                    p.setdefault('zone', z)
                    if ms is not None:
                        p.setdefault('meshSize', ms)
                elif isinstance(p, list):
                    if ms is not None:
                        p += [ms]
                    if cs is not None:
                        p += [cs]
                    if z is not None:
                        p += [z]
                    tag, zone, coordinate_system, coordinates, kwargs = Point.parse_args([p])
                    p = {'tag': tag, 'coordinates': coordinates}
                    p['coordinate_system'] = coordinate_system if coordinate_system is not None else cs
                    p['zone'] = zone if zone is not None else z
                    p.update(kwargs)
                    if ms is not None:
                        p.setdefault('meshSize', ms)
                else:
                    raise ValueError(p)
                points[i] = p
        # Make objects
        for i, p in enumerate(points):
            if isinstance(p, dict):
                points[i] = Point(**p)
            elif isinstance(p, list):
                points[i] = Point(p)
            else:
                raise ValueError(p)
        # Change degrees to radians
        if do_deg2rad:
            for p in points:
                if isinstance(p.coordinate_system, Cylindrical):
                    p.coordinates[1] = np.deg2rad(p.coordinates[1])
                elif any([isinstance(p.coordinate_system, Spherical),
                          isinstance(p.coordinate_system, Toroidal),
                          isinstance(p.coordinate_system, Tokamak)]):
                    p.coordinates[1] = np.deg2rad(p.coordinates[1])
                    p.coordinates[2] = np.deg2rad(p.coordinates[2])
        return points


str2obj = {
    Point.__name__: Point,
}
