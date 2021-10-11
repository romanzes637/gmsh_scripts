import numpy as np


class CoordinateSystem:
    def __init__(self, dim=None, origin=None, **kwargs):
        self.dim = dim
        self.origin = origin if isinstance(origin, np.ndarray) else np.array(origin)


class Cartesian(CoordinateSystem):
    def __init__(self, origin=np.zeros(3), **kwargs):
        super().__init__(dim=3, origin=origin, **kwargs)


class Cylindrical(CoordinateSystem):
    def __init__(self, origin=np.zeros(3), **kwargs):
        super().__init__(dim=3, origin=origin, **kwargs)


class Spherical(CoordinateSystem):
    def __init__(self, origin=np.zeros(3), **kwargs):
        super().__init__(dim=3, origin=origin, **kwargs)


class Toroidal(CoordinateSystem):
    def __init__(self, origin=np.zeros(4), **kwargs):
        super().__init__(dim=4, origin=origin, **kwargs)


class Tokamak(CoordinateSystem):
    def __init__(self, origin=np.zeros(6), **kwargs):
        super().__init__(dim=6, origin=origin, **kwargs)


class Block(CoordinateSystem):
    def __init__(self, ps=None, origin=np.zeros(3), order=None, **kwargs):
        """Local Block Coordinate System

        xi [-1, 1]
        eta [-1, 1]
        zeta [-1, 1]

        Args:
            ps (np.array or list of list): points coordinates of the block
            order (np.array or list of list): order of points
            origin (np.array or list): origin of coordinate system
        """
        super().__init__(dim=3, origin=origin, **kwargs)
        if ps is None:
            ps = [[1, 1, -1], [-1, 1, -1], [-1, -1, -1], [1, -1, -1],
                  [1, 1, 1], [-1, 1, 1], [-1, -1, 1], [1, -1, 1]]
        self.ps = ps if isinstance(ps, np.ndarray) else np.array(ps)
        if order is None:
            self.order = np.array(
                [[1, 1, -1], [-1, 1, -1], [-1, -1, -1], [1, -1, -1],
                 [1, 1, 1], [-1, 1, 1], [-1, -1, 1], [1, -1, 1]])
        else:
            self.order = order if isinstance(order, np.ndarray) else np.array(order)


factory = {
    'coordinate_system': CoordinateSystem,
    'cartesian': Cartesian,
    'cylindrical': Cylindrical,
    'spherical': Spherical,
    'toroidal': Toroidal,
    'tokamak': Tokamak,
    'block': Block
}
