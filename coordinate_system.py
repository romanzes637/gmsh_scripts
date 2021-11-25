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
    """Cylindrical coordinate system

    r - radius [0, inf),
    phi - azimuthal angle [0, 2*pi) (counterclockwise from X to Y),
    z - height
    """

    def __init__(self, origin=np.zeros(3), **kwargs):
        super().__init__(dim=3, origin=origin, **kwargs)


class Spherical(CoordinateSystem):
    """Spherical coordinate system

    r - radius [0, inf),
    phi - azimuthal angle [0, 2*pi) (counterclockwise from X to Y),
    theta - polar angle [0, pi] (from top to bottom, i.e XY-plane is pi/2)
    """

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
                 transforms=None, weights=None, local_weights=None, **kwargs):
        """Path coordinate system

        # pitch, yaw, roll
        xi [-inf, inf]  # Transverse (Right) axis, pitch rotation
        eta [-inf, inf]  # Vertical (Down) axis, yaw rotation
        zeta [0, 1]  # Longitudinal (Front) axis, roll rotation

`       Beta distribution calculator https://keisan.casio.com/exec/system/1180573226

        Args:
            origin (np.ndarray or list): Origin of the coordinate system
            curves (list of dict, list of list, list, list of Curve): Curves
        """
        super().__init__(dim=3, origin=origin, **kwargs)
        curves = [] if curves is None else curves
        transforms = [[] for _ in curves] if transforms is None else transforms
        self.weights = [1 for _ in curves] if weights is None else weights
        self.local_weights = [[] for _ in curves] if local_weights is None else local_weights
        from block import Block as BlockObject
        self.curves = BlockObject.parse_curves(curves)
        self.transforms = [BlockObject.parse_transforms(x, None) for x in transforms]
        self.orientations = self.parse_orientations(
            orientations=orientations, do_deg2rad=True)
        self.is_registered = False

    def parse_orientations(self, orientations, do_deg2rad):
        if orientations is None:
            n_curves = len(self.curves)
            orientations = [np.eye(3, 3).tolist() for _ in range(n_curves + 1)]  # X - Pitch, Y - Yaw, Z - Roll
        from point import Point
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
        from transform import str2obj as transform_factory
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
        # TODO Do normalization? Do +1 0
        for i, o in enumerate(orientations):
            for j, v in enumerate(o):
                v.coordinates = v.coordinates / np.linalg.norm(v.coordinates)
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
                    from transform import str2obj as tr_factory, reduce_transforms
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
            from registry import FACTORY
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
                break
        return v, dv, ori, lu_rel

    def get_local_coordinate_system(self, u):
        if not self.is_registered:  # lazy init
            self.transform()
            self.register()
            from registry import FACTORY
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
        from point import Point
        ps = [Point(coordinates=x) for x in ori]
        if np.linalg.norm(d) > 0 and not np.isnan(a):
            d = d / np.linalg.norm(d)
            from transform import Rotate
            # ori_part = 2*abs(lu_rel - 0.5)
            # der_part = 1 - ori_part
            der_part = 0
            a = a * der_part
            rot = Rotate(origin=[0, 0, 0], direction=d, angle=a)
            ps = [rot(x) for x in ps]
        cs = Affine(origin=v, vs=[x.coordinates / np.linalg.norm(x.coordinates) for x in ps])
        # cs = Affine(origin=v, vs=[x.coordinates for x in ps])
        return cs


class LayerXY(CoordinateSystem):
    """Different layers by X and Y axes and same by Z axis

    Args:
        layers (list of list):
            [[c_x1, c_x2, ..., c_xN],
            [c_y1, c_y2, ..., c_yN],
            [c_nx1, c_nx2, ..., c_nxN],
            [c_ny1, c_ny2, ..., c_nyN]],
            where N - number of layers,
            l - coordinate of the layer by X, Y, NX, NY axis (0, inf).
            Parsed by py:method:`matrix.Matrix:parse_grid`
        layers_curves (list of list of str):
            [[name_x1, name_x2, ..., name_xN],
            [name_y1, name_y2, ..., name_yN],
            [name_nx1, name_nx2, ..., name_nxN],
            [name_ny1, name_ny2, ..., name_nyN]],
            where N - number of layers,
            name - curve name (see py:class:`curve.Curve` class)
        layers_types (list of str): [type_x, type_y, type_nx, type_ny],
            where type: 'in' (inscribe), 'out' (circumscribed).
    """
    def __init__(self, origin=np.zeros(3), layers=None, layers_curves=None,
                 layers_types=None, **kwargs):
        super().__init__(dim=3, origin=origin, **kwargs)
        layers = [[1], [1], [1], [1]] if layers is None else layers
        if len(layers) == 4:   # X, Y, NX, NZ
            pass
        elif len(layers) == 1:  # X = Y = NX = NY
            layers = [layers[0] for _ in range(4)]
            layers_curves = [layers_curves[0] for _ in range(4)]
            layers_types = [layers_types[0] for _ in range(4)]
        elif len(layers) == 2:  # X = NX and Y = NY
            layers = layers + layers
            layers_curves = layers_curves + layers_curves
            layers_types = layers_types + layers_types
        else:
            raise ValueError(layers)
        if layers_curves is None:
            layers_curves = [['line' for _ in x] for x in layers]
        if layers_types is None:
            layers_types = ['in' for _ in layers[0]]
        from point import parse_grid_row
        for i, layer in enumerate(layers):
            new_row, values, maps = parse_grid_row(layer)
            coordinates = values[0]
            if i in [2, 3]:  # NX, NY
                coordinates = [-x for x in coordinates]
            layers[i] = coordinates
            new2old_id2id = maps[-2]
            layers_curves[i] = [layers_curves[i][x] for x in new2old_id2id]
        self.layers = layers
        self.curves_names = layers_curves
        self.layers_types = layers_types


str2obj = {
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
    Tokamak.__name__.lower(): Tokamak,
    'tok': Tokamak,
    Block.__name__: Block,
    Block.__name__.lower(): Block,
    'blo': Block,
    Path.__name__: Path,
    Path.__name__.lower(): Path,
    'pth': Path,
    LayerXY.__name__: LayerXY,
    LayerXY.__name__.lower(): LayerXY,
    'lxy': Path
}
