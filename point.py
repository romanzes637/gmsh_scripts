import numpy as np

from coordinate_system import factory as cs_factory


class Point:
    def __init__(self, tag=None, name=None, zone=None, coordinate_system=None,
                 coordinates=None, **kwargs):
        """Point
        Args:
            tag(int): unique id
            name(str): type
            zone(str): zone
            coordinate_system (CoordinateSystem): CoordinateSystem
            coordinates (list of float, np.array): coordinates values
        """
        self.tag = tag
        self.name = name
        self.zone = zone
        if coordinate_system is None:
            self.coordinate_system = cs_factory['cartesian']()
        else:
            self.coordinate_system = coordinate_system
        if coordinates is None:
            self.coordinates = np.zeros(self.coordinate_system.dim)
        elif isinstance(coordinates, np.ndarray):
            self.coordinates = coordinates
        elif isinstance(coordinates, list):
            self.coordinates = np.array(coordinates)
        else:
            raise ValueError(coordinates)
        self.kwargs = kwargs
