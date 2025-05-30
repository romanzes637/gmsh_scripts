import numpy as np
import gmsh

from gmsh_scripts.registry import register_point, register_curve


class CoordinateSystem:
    """Abstract

    Args:
        dim (int): Dimension
        origin (np.ndarray or list): Origin
    """
    def __init__(self, dim=None, origin=None, **kwargs):
        self.dim = dim
        self.origin = origin if isinstance(origin, np.ndarray) else np.array(origin)


class Affine(CoordinateSystem):
    """Affine coordinate system

    Args:
        origin (np.ndarray or list): Origin
        vs (np.ndarray or list of list): Basis vectors
    """

    def __init__(self, origin=np.zeros(3), vs=np.eye(3, 3), **kwargs):
        vs = vs if isinstance(vs, np.ndarray) else np.array(vs)
        super().__init__(dim=vs.shape[0], origin=origin, **kwargs)
        self.vs = vs


class Cartesian(Affine):
    def __init__(self, **kwargs):
        super().__init__(origin=np.zeros(3), vs=np.eye(3, 3), **kwargs)


class Cylindrical(CoordinateSystem):
    """Cylindrical coordinate system

    * r - radius [0, inf)
    * phi - azimuthal angle or longitude [0, 2pi) (counterclockwise from X to Y)
    * z - height
    """

    def __init__(self, origin=np.zeros(3), **kwargs):
        super().__init__(dim=3, origin=origin, **kwargs)


class Spherical(CoordinateSystem):
    """Spherical coordinate system

    * r - radius [0, inf)
    * phi - azimuthal angle [0, 2pi) (counterclockwise from X to Y)
    * theta - polar (zenith) angle or colatitude = pi/2 - latitude [0, pi]
        (from Z to -Z, i.e XY-plane is pi/2)
    """

    def __init__(self, origin=np.zeros(3), **kwargs):
        super().__init__(dim=3, origin=origin, **kwargs)


class Toroidal(CoordinateSystem):
    def __init__(self, origin=np.zeros(4), **kwargs):
        super().__init__(dim=4, origin=origin, **kwargs)


class Tokamak(CoordinateSystem):
    def __init__(self, origin=np.zeros(6), **kwargs):
        super().__init__(dim=6, origin=origin, **kwargs)


class Hexahedral(CoordinateSystem):
    """Natural Hexahedral Coordinate System

    * xi [-1, 1]
    * eta [-1, 1]
    * zeta [-1, 1]

    Args:
        ps (np.ndarray or list of list): points coordinates of hexahedron
        order (np.ndarray or list of list): order of points
        origin (np.ndarray or list): Origin
    """

    def __init__(self, origin=np.zeros(3), ps=None, order=None, **kwargs):
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


class Block(CoordinateSystem):
    """Block Coordinate System

    * xi [-1, 1]
    * eta [-1, 1]
    * zeta [-1, 1]

    Args:
        ps (np.ndarray or list of list): points coordinates of the block
        order (np.ndarray or list of list): order of points
        origin (np.ndarray or list): Origin
    """

    def __init__(self, origin=np.zeros(3), ps=None, order=None, **kwargs):
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
    """Path coordinate system

    * xi - X, transverse, right axis, axis of pitch rotation (-inf, inf)
    * eta - Y, vertical, down axis, axis of yaw rotation (-inf, inf)
    * zeta - Z, longitudinal, front axis, axis of roll rotation [0, 1]

    Args:
        origin (np.ndarray or list): Origin
        curves (list of Curve or list of Curve): Curves
        orientations (list): Orientation in curves points (number of curves + 1)
        transforms (list of list): Curves points transforms
        weights (list of float): Curves weights in global path coordinate system
        local_weights (list of list): Curves weights in local curve coordinate system
    """
    def __init__(self, origin=np.zeros(3), curves=None, orientations=None,
                 transforms=None, weights=None, local_weights=None,
                 do_normalize=False, normalize_kind=1, normalize_local_kind=1,
                 **kwargs):
        super().__init__(dim=3, origin=origin, **kwargs)
        self.do_normalize = do_normalize
        self.normalize_kind = normalize_kind
        self.normalize_local_kind = normalize_local_kind
        curves = [] if curves is None else curves
        transforms = [[] for _ in curves] if transforms is None else transforms
        self.weights = [1 for _ in curves] if weights is None else weights
        self.local_weights = [[] for _ in curves] if local_weights is None else local_weights
        from gmsh_scripts.block.block import Block as BlockObject
        self.curves = BlockObject.parse_curves(curves)
        self.transforms = [BlockObject.parse_transforms(x, None) for x in transforms]
        self.orientations = self.parse_orientations(
            orientations=orientations, do_deg2rad=True)
        self.is_registered = False

    def parse_orientations(self, orientations, do_deg2rad):
        if orientations is None:
            n_curves = len(self.curves)
            orientations = [np.eye(3, 3).tolist() for _ in range(n_curves + 1)]  # X - Pitch, Y - Yaw, Z - Roll
        from gmsh_scripts.entity.point import Point
        orientations = [Point.parse_points(x, do_deg2rad=do_deg2rad)
                        for x in orientations]
        for i, o in enumerate(orientations):
            # tangential (roll) - add binormal (bitangent, pitch)
            if len(o) == 1 and isinstance(o[0].coordinate_system, Spherical):
                t = o[0].coordinates
                n = [t[0], t[1], t[2] + 0.5 * np.pi]
                orientations[i] = [Point(
                    coordinates=n, coordinate_system=Spherical()), o[0]]
            elif len(o) == 3 or len(o) == 2:
                pass
            else:
                raise ValueError(o)

        from gmsh_scripts.transform.transform import str2obj as transform_factory
        orientations = [[transform_factory[y.coordinate_system.__class__.__name__]()(y)
                         for y in x] for x in orientations]
        for i, o in enumerate(orientations):
            # normal (yaw) and tangential (roll) directions - add binormal (bitangent, pitch)
            if len(o) == 2:
                n, t = o[0].coordinates, o[1].coordinates
                b = np.cross(n / np.linalg.norm(n), t / np.linalg.norm(t))
                b = b / np.linalg.norm(b)
                orientations[i] = [Point(coordinates=b), o[0], o[1]]
            elif len(o) == 3:
                pass
            else:
                raise ValueError(o)
        if self.do_normalize:
            if self.normalize_kind == 0:  # skip
                pass
            elif self.normalize_kind == 1:  # self
                for i, o in enumerate(orientations):
                    for j, v in enumerate(o):
                        norm = np.linalg.norm(v.coordinates)
                        v.coordinates = v.coordinates / norm
            elif self.normalize_kind == 2:  # first
                first_norms = [np.linalg.norm(x.coordinates) for x in orientations[0]]
                for i, o in enumerate(orientations):
                    for j, v in enumerate(o):
                        norm = np.linalg.norm(v.coordinates)
                        v.coordinates = v.coordinates / norm * first_norms[j]
            elif self.normalize_kind == 3:  # last
                last_norms = [np.linalg.norm(x.coordinates) for x in orientations[-1]]
                for i, o in enumerate(orientations):
                    for j, v in enumerate(o):
                        norm = np.linalg.norm(v.coordinates)
                        v.coordinates = v.coordinates / norm * last_norms[j]
            elif self.normalize_kind == 4:  # first-last
                first_norms = [np.linalg.norm(x.coordinates) for x in orientations[0]]
                last_norms = [np.linalg.norm(x.coordinates) for x in orientations[-1]]
                for i, o in enumerate(orientations):
                    k = i / (len(orientations) - 1)
                    for j, v in enumerate(o):
                        norm = np.linalg.norm(v.coordinates)
                        norms = [k*y + (1 - k) * x
                                 for x, y in zip(first_norms, last_norms)]
                        v.coordinates = v.coordinates / norm * norms[j]
            else:
                raise NotImplementedError(self.normalize_kind)
        return orientations

    def register(self):
        for c in self.curves:
            for p in c.points:
                register_point(point=p)
            register_curve(curve=c)

    def transform(self):
        for i, c in enumerate(self.curves):
            for p in c.points:
                cs = p.coordinate_system
                if not isinstance(cs, Cartesian):
                    from gmsh_scripts.transform.transform import str2obj as tr_factory, reduce_transforms
                    any2car = tr_factory[cs.__class__.__name__]()
                    ts = [any2car] + self.transforms[i]
                    reduce_transforms(ts, p)

    def evaluate_bounds(self):
        self.curves_bounds = []
        for c in self.curves:
            bs = gmsh.model.get_parametrization_bounds(1, c.tag)
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
        if not self.is_registered:  # lazy init
            self.transform()
            self.register()
            from gmsh_scripts.registry import FACTORY
            if FACTORY == 'geo':
                gmsh.model.geo.synchronize()
            elif FACTORY == 'occ':
                gmsh.model.occ.synchronize()
            else:
                raise ValueError(FACTORY)
            self.evaluate_bounds()
            self.is_registered = True
        v, dv, ori, lu_rel = None, None, None, None
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
                        n = 10000
                        xs, dx = np.linspace(0, lu_rel, n, retstep=True)
                        ts, dt = np.linspace(0, 1, n, retstep=True, endpoint=False)
                        xs, ts = xs[1:], ts[1:]  # Exclude 0's
                        t = np.sum(ts ** (a - 1) * (1 - ts) ** (b - 1) * dt)
                        x = np.sum(xs ** (a - 1) * (1 - xs) ** (b - 1) * dx)
                        lu_rel = x / t
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
                ori0 = np.array([x.coordinates for x in self.orientations[i]])
                ori1 = np.array([x.coordinates for x in self.orientations[i + 1]])
                ori = lu_rel * ori1 + (1 - lu_rel) * ori0
                if self.do_normalize:
                    if self.normalize_local_kind == 0:  # skip
                        pass
                    elif self.normalize_local_kind == 1:  # self
                        norm = np.linalg.norm(ori, axis=1, keepdims=True)
                        ori /= norm
                    elif self.normalize_local_kind == 2:  # first
                        norm0 = np.linalg.norm(ori0, axis=1, keepdims=True)
                        norm = np.linalg.norm(ori, axis=1, keepdims=True)
                        ori = ori / norm * norm0
                    elif self.normalize_local_kind == 3:  # last
                        norm1 = np.linalg.norm(ori1, axis=1, keepdims=True)
                        norm = np.linalg.norm(ori, axis=1, keepdims=True)
                        ori = ori / norm * norm1
                    elif self.normalize_local_kind == 4:  # first-last
                        norm0 = np.linalg.norm(ori0, axis=1, keepdims=True)
                        norm1 = np.linalg.norm(ori1, axis=1, keepdims=True)
                        norm = np.linalg.norm(ori, axis=1, keepdims=True)
                        ori = ori / norm * (lu_rel * norm1 + (1 - lu_rel) * norm0)
                    else:
                        raise NotImplementedError(self.normalize_local_kind)
                break
        return v, dv, ori, lu_rel

    def get_local_coordinate_system(self, u):
        if not self.is_registered:  # lazy init
            self.transform()
            self.register()
            from gmsh_scripts.registry import FACTORY
            if FACTORY == 'geo':
                gmsh.model.geo.synchronize()
            elif FACTORY == 'occ':
                gmsh.model.occ.synchronize()
            else:
                raise ValueError(FACTORY)
            self.evaluate_bounds()
            self.is_registered = True
        v, dv, ori, lu_rel = self.get_value_derivative_orientation(u)
        z = ori[2]
        cos_a = np.dot(dv, z) / (np.linalg.norm(dv) * np.linalg.norm(z))
        cos_a = np.clip(cos_a, -1, 1)  # Fix integration error
        a = np.arccos(cos_a)
        d = np.cross(z / np.linalg.norm(z), dv / np.linalg.norm(dv))
        # d = np.cross(z, dv)
        from gmsh_scripts.entity.point import Point
        ps = [Point(coordinates=x) for x in ori]
        if np.linalg.norm(d) > 0 and not np.isnan(a):
            d = d / np.linalg.norm(d)
            from gmsh_scripts.transform.transform import Rotate
            # ori_part = 2*abs(lu_rel - 0.5)
            # der_part = 1 - ori_part
            der_part = 0
            a = a * der_part
            rot = Rotate(origin=[0, 0, 0], direction=d, angle=a)
            ps = [rot(x) for x in ps]
        vs = [x.coordinates for x in ps]
        cs = Affine(origin=v, vs=vs)
        return cs


class Layer(CoordinateSystem):
    """Different layers by X, Y and Z axis

    Args:
        layers (list):
            [[c_x_1, c_x_2,  ..., c_x_NX],
            [c_y_1,  c_y_2,  ..., c_y_NY],
            [c_nx_1, c_nx_2, ..., c_nx_NNX],
            [c_ny_1, c_ny_2, ..., c_ny_NNY]],
            [c_z_1,  c_z_2,  ..., c_z_NZ]],
            [c_nz_1, c_nz_2, ..., c_nz_NNZ]],
            where N - number of layers, c (float): coordinate (0, inf).
        layers_curves (list):
            [[name_x_1, name_x_2,  ..., name_x_NX],
            [name_y_1,  name_y_2,  ..., name_y_NY],
            [name_nx_1, name_nx_2, ..., name_nx_NNX],
            [name_ny_1, name_ny_2, ..., name_ny_NNY]],
            [name_z_1,  name_z_2,  ..., name_z_NZ]],
            [name_nz_1, name_nz_2, ..., name_nz_NNZ]],
            where N - number of layers,
            name - curve name (see py:class:`curve.Curve` class)
        layers_types (list):
            [[type_x_1, type_x_2,  ..., type_x_NX],
             [type_y_1,  type_y_2,  ..., type_y_NY],
             [type_z_1,  type_z_2,  ..., type_z_NZ]],
             [type_nz_1, type_nz_2, ..., type_nz_NNZ]],
            where type (str): 'in' - inscribed, 'out' - circumscribed.
    """

    def __init__(self, origin=np.zeros(3), layers=None, layers_curves=None,
                 layers_types=None, **kwargs):
        super().__init__(dim=3, origin=origin, **kwargs)
        self.layers = [x for x in layers] if layers is not None else [[] for _ in range(6)]
        self.layers[2] = [-x for x in self.layers[2]]  # NX
        self.layers[3] = [-x for x in self.layers[3]]  # NY
        self.layers[5] = [-x for x in self.layers[5]]  # NZ
        self.layers_curves = layers_curves
        self.layers_types = layers_types


class QuarterLayer(CoordinateSystem):
    """Quarter of Layer by +X and +Y directions

    Args:
        layers (list):
            [[c_x_1, c_x_2,  ..., c_x_NX],
             [c_y_1,  c_y_2,  ..., c_y_NY],
             [c_z_1,  c_z_2,  ..., c_z_NZ]],
             [c_nz_1, c_nz_2, ..., c_nz_NNZ]],
            where N - number of layers, c (float): coordinate (0, inf).
        layers_curves (list):
            [[name_x_1, name_x_2,  ..., name_x_NX],
             [name_y_1,  name_y_2,  ..., name_y_NY],
             [name_z_1,  name_z_2,  ..., name_z_NZ]],
             [name_nz_1, name_nz_2, ..., name_nz_NNZ]],
            where N - number of layers,
            name - curve name (see py:class:`curve.Curve` class)
        layers_types (list):
            [[type_x_1, type_x_2,  ..., type_x_NX],
             [type_y_1,  type_y_2,  ..., type_y_NY],
             [type_z_1,  type_z_2,  ..., type_z_NZ]],
             [type_nz_1, type_nz_2, ..., type_nz_NNZ]],
            where type (str): 'in' - inscribed, 'out' - circumscribed.

    """
    def __init__(self, origin=np.zeros(3), layers=None, layers_curves=None,
                 layers_types=None, **kwargs):
        super().__init__(dim=3, origin=origin, **kwargs)
        self.layers = [x for x in layers] if layers is not None else [[] for _ in range(6)]
        self.layers[2] = [-x for x in self.layers[2]]  # NX
        self.layers[3] = [-x for x in self.layers[3]]  # NY
        self.layers[5] = [-x for x in self.layers[5]]  # NZ
        self.layers_curves = layers_curves
        self.layers_types = layers_types


class HalfLayer(CoordinateSystem):
    """Half of Layer

    Args:
        layers (list):
            [[c_x_1, c_x_2,  ..., c_x_NX],
             [c_y_1,  c_y_2,  ..., c_y_NY],
             [c_z_1,  c_z_2,  ..., c_z_NZ]],
             [c_nz_1, c_nz_2, ..., c_nz_NNZ]],
            where N - number of layers, c (float): coordinate (0, inf).
        layers_curves (list):
            [[name_x_1, name_x_2,  ..., name_x_NX],
             [name_y_1,  name_y_2,  ..., name_y_NY],
             [name_z_1,  name_z_2,  ..., name_z_NZ]],
             [name_nz_1, name_nz_2, ..., name_nz_NNZ]],
            where N - number of layers,
            name - curve name (see py:class:`curve.Curve` class)
        layers_types (list):
            [[type_x_1, type_x_2,  ..., type_x_NX],
             [type_y_1,  type_y_2,  ..., type_y_NY],
             [type_z_1,  type_z_2,  ..., type_z_NZ]],
             [type_nz_1, type_nz_2, ..., type_nz_NNZ]],
            where type (str): 'in' - inscribed, 'out' - circumscribed.

    """
    def __init__(self, origin=np.zeros(3), layers=None, layers_curves=None,
                 layers_types=None, **kwargs):
        super().__init__(dim=3, origin=origin, **kwargs)
        self.layers = [x for x in layers] if layers is not None else [[] for _ in range(6)]
        self.layers[2] = [-x for x in self.layers[2]]  # NX
        self.layers[3] = [-x for x in self.layers[3]]  # NY
        self.layers[5] = [-x for x in self.layers[5]]  # NZ
        self.layers_curves = layers_curves
        self.layers_types = layers_types


str2obj = {
    CoordinateSystem.__name__: CoordinateSystem,
    'coo': CoordinateSystem,
    Affine.__name__: Affine,
    'aff': Affine,
    Cartesian.__name__: Cartesian,
    'car': Cartesian,
    Cylindrical.__name__: Cylindrical,
    'cyl': Cylindrical,
    Spherical.__name__: Spherical,
    'sph': Spherical,
    Toroidal.__name__: Toroidal,
    'tor': Toroidal,
    Tokamak.__name__: Tokamak,
    'tok': Tokamak,
    Hexahedral.__name__: Hexahedral,
    'hex': Hexahedral,
    Block.__name__: Block,
    'blo': Block,
    Path.__name__: Path,
    'pth': Path,
    Layer.__name__: Layer,
    QuarterLayer.__name__: QuarterLayer,
    HalfLayer.__name__: HalfLayer,
}
