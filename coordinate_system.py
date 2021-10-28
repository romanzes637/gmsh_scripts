import numpy as np


class CoordinateSystem:
    def __init__(self, dim=None, origin=None, **kwargs):
        self.dim = dim
        self.origin = origin if isinstance(origin, np.ndarray) else np.array(origin)


class Affine(CoordinateSystem):
    def __init__(self, origin=np.zeros(3), vs=np.eye(3, 3), **kwargs):
        """Affine coordinate system

        Args:
            origin (np.ndarray or list): Origin
            vs (np.ndarray or list of list): Basis vectors
        """
        vs = vs if isinstance(vs, np.ndarray) else np.array(vs)
        super().__init__(dim=vs.shape[0], origin=origin, **kwargs)
        self.vs = vs


class Cartesian(Affine):
    def __init__(self, **kwargs):
        super().__init__(origin=np.zeros(3), vs=np.eye(3, 3), **kwargs)


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
            ps (np.ndarray or list of list): points coordinates of the block
            order (np.ndarray or list of list): order of points
            origin (np.ndarray or list): origin of coordinate system
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


class Path(CoordinateSystem):
    def __init__(self, ps=None, vs=None, ds=None, ns=None, t='polyline',
                 local_cs=None,
                 origin=np.zeros(3), **kwargs):
        """Path coordinate system

        xi [-inf, inf]  # Transverse (Right) axis, pitch rotation
        eta [-inf, inf]  # Vertical (Down) axis, yaw rotation
        zeta [0, 1]  # Longitudinal (Front) axis, roll rotation

        Args:
            ps (np.ndarray or list of list): Coordinates of points of the path
            vs (np.ndarray or list of list of list): Basis vectors of local coordinate system at points
            ds (np.ndarray or list of list): Directions of basis vectors of local coordinate system at points
            ns (np.ndarray or list of list): Norms of basis vectors of local coordinate system at points
            t (str): Type of curve interpolation: polyline, polynomial, spline, ...
            origin (np.ndarray or list): Origin of the coordinate system
        """
        super().__init__(dim=3, origin=origin, **kwargs)
        if ps is None:
            ps = []
        ps = ps if isinstance(ps, np.ndarray) else np.array(ps)
        if vs is None:
            if ds is not None and ns is not None:
                ds = ds
                ns = ns
                vs = np.multiply(ds, ns)
            elif ds is not None:
                ds = ds
                # self.ds = ds
                # self.ns =
            else:
                vs = [[[1, 0, 0], [0, -1, 0], [0, 0, -1]]]  # long, pitch, yaw
        else:
            vs = vs
            ns = np.linalg.norm(vs, axis=2)
            ds = vs / ns

        vs = vs if isinstance(vs, np.ndarray) else np.array(vs)
        self.ps = ps
        self.vs = vs
        if t == 'polyline':
            lines = ps[1:] - ps[:-1]
            print(lines)
            lengths = np.linalg.norm(lines, axis=1)
            print(lengths)

        def get_global_p(self, lp):
            return lp

        def get_local_v(self, long):
            v = 42
            return v


factory = {
    Affine.__name__: Affine,
    Affine.__name__.lower(): Affine,
    'aff': Affine,
    Cartesian.__name__: Cartesian,
    Cartesian.__name__.lower(): Cartesian,
    'car': Cartesian,
    Cylindrical.__name__: Cylindrical,
    Cylindrical.__name__.lower(): Cylindrical,
    'cyl': Cylindrical,
    Spherical.__name__: Spherical,
    Spherical.__name__.lower(): Spherical,
    'sph': Spherical,
    Toroidal.__name__: Toroidal,
    Toroidal.__name__.lower(): Toroidal,
    'tor': Toroidal,
    Tokamak.__name__: Tokamak,
    'tok': Tokamak,
    Block.__name__: Block,
    Block.__name__.lower(): Block,
    'blo': Block,
    Path.__name__: Path,
    Path.__name__.lower(): Path,
    'pth': Path
}
