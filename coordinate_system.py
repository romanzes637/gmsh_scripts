import numpy as np
import gmsh

from registry import register_point, register_curve


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
    def __init__(self, origin=np.zeros(3), ps=None, order=None, **kwargs):
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
    def __init__(self, origin=np.zeros(3), curves=None, orientations=None,
                 transforms=None, weights=None, local_weights=None,
                 factory='geo', use_register_tag=False, **kwargs):
        """Path coordinate system

        # pitch, yaw, roll
        xi [-inf, inf]  # Transverse (Right) axis, pitch rotation
        eta [-inf, inf]  # Vertical (Down) axis, yaw rotation
        zeta [0, 1]  # Longitudinal (Front) axis, roll rotation

`       Beta distribution calculator https://keisan.casio.com/exec/system/1180573226

        Args:
            origin (np.ndarray or list): Origin of the coordinate system
            curves (list of dict, list of list, list, list of Curve): Curves
            use_register_tag (bool): use tag from registry instead tag from gmsh
            factory (str): gmsh factory (geo or occ)
        """
        super().__init__(dim=3, origin=origin, **kwargs)
        curves = [] if curves is None else curves
        transforms = [[] for _ in curves] if transforms is None else transforms
        self.weights = [1 for _ in curves] if weights is None else weights
        self.local_weights = [[] for _ in curves] if local_weights is None else local_weights
        from block import Block as BlockObject
        self.curves = BlockObject.parse_curves(curves)
        self.factory = factory
        self.use_register_tag = use_register_tag
        self.transforms = [BlockObject.parse_transforms(x, None) for x in transforms]
        if orientations is None:
            np.array([np.eye(3, 3) for _ in range(len(curves) + 1)])
        if not isinstance(orientations, np.ndarray):
            self.orientations = np.array(orientations)
        else:
            self.orientations = orientations

    def register(self):
        for c in self.curves:
            for p in c.points:
                register_point(factory=self.factory, point=p,
                               register_tag=self.use_register_tag)
            register_curve(factory=self.factory, curve=c,
                           register_tag=self.use_register_tag)

    def transform(self):
        for i, c in enumerate(self.curves):
            for p in c.points:
                cs = p.coordinate_system
                if not isinstance(cs, Cartesian):
                    from transform import factory as tr_factory, reduce_transforms

                    any2car = tr_factory[type(cs)]()
                    ts = [any2car] + self.transforms[i]
                    reduce_transforms(ts, p)

    def evaluate_bounds(self):
        self.curves_bounds = []
        for c in self.curves:
            bs = gmsh.model.getParametrizationBounds(1, c.tag)
            self.curves_bounds.append([bs[0][0], bs[1][0]])
        cnt = 0
        self.global_curves_bounds = []
        for i, bs in enumerate(self.curves_bounds):
            w = self.weights[i]
            # du = w * (bs[1] - bs[0])  # TODO Use real bounds?
            du = w
            bs_g = [cnt, cnt + du]
            cnt = bs_g[1]
            self.global_curves_bounds.append(bs_g)
        self.global_normalized_curves_bounds = np.divide(
            self.global_curves_bounds, np.max(self.global_curves_bounds))

    def get_value_derivative_orientation(self, u):
        v, dv, ori = None, None, None
        for i, c in enumerate(self.curves):
            bs_gn = self.global_normalized_curves_bounds[i]
            if bs_gn[0] <= u <= bs_gn[1]:
                # Relative [0, 1] local coordinate
                lu_rel = (u - bs_gn[0]) / (bs_gn[1] - bs_gn[0])
                lws = self.local_weights[i]
                if len(lws) == 2:  # Beta distribution
                    if lu_rel == 0 or lu_rel == 1:
                        pass
                    else:
                        a, b = lws
                        n = 1000
                        xs, dx = np.linspace(0, lu_rel, n, retstep=True)
                        ts, dt = np.linspace(0, 1, n, retstep=True, endpoint=False)
                        xs, ts = xs[1:], ts[1:]  # Exclude 0's
                        t = np.sum(ts ** (a - 1) * (1 - ts) ** (b - 1) * dt)
                        x = np.sum(xs ** (a - 1) * (1 - xs) ** (b - 1) * dx)
                        lu_rel = x/t
                        # print(f'beta {a}, {b}, {x}, {t}, {lu_rel}')
                else:  # Linear
                    pass
                bs = self.curves_bounds[i]
                # Absolute local coordinate
                lu_abs = bs[0] + lu_rel * (bs[1] - bs[0])
                # Value (Cartesian coordinates)
                v = gmsh.model.getValue(1, c.tag, (lu_abs,))
                # Derivative (Cartesian)
                dv = gmsh.model.getDerivative(1, c.tag, (lu_abs,))
                ori0 = self.orientations[i]  # TODO orientation for each point?
                ori1 = self.orientations[i+1]
                ori = lu_rel * ori1 + (1 - lu_rel) * ori0
                break
        return v, dv, ori

    def get_local_coordinate_system(self, u):
        v, dv, ori = self.get_value_derivative_orientation(u)
        z = ori[2]
        a = np.arccos(np.dot(dv, z) / (np.linalg.norm(dv) * np.linalg.norm(z)))
        d = np.cross(z / np.linalg.norm(z), dv / np.linalg.norm(dv))
        from point import Point

        ps = [Point(coordinates=x) for x in ori]
        if np.linalg.norm(d) > 0:
            d = d / np.linalg.norm(d)

            from transform import Rotate, reduce_transforms
            rot = Rotate(origin=[0, 0, 0], direction=d, angle=a)
            for p in ps:
                reduce_transforms([rot], p)
        cs = Affine(origin=v, vs=[x.coordinates / np.linalg.norm(x.coordinates) for x in ps])
        return cs


factory = {
    CoordinateSystem.__name__: CoordinateSystem,
    'coo': CoordinateSystem,
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
