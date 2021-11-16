from functools import reduce
import logging

import numpy as np

from coordinate_system import CoordinateSystem, Cartesian, Cylindrical, \
    Spherical, Toroidal, Tokamak, Block, Path, Affine, LayerXY


def reduce_transforms(transforms, point):
    """Apply transformations on the point.

    Args:
        transforms (list): Transformations
        point (Point): Point

    Returns:
        Point: Transformed point.

    """
    return reduce(lambda x, y: y(x), transforms, point)


class Transform:
    """General transformation of Point coordinates.

    Args:
        cs_from (CoordinateSystem): CoordinateSystem from
        cs_to (CoordinateSystem): CoordinateSystem to
        cs_self (CoordinateSystem): CoordinateSystem self
    """

    def __init__(self, cs_from=None, cs_to=None, cs_self=None, **kwargs):
        self.cs_from = CoordinateSystem() if cs_from is None else cs_from
        self.cs_to = CoordinateSystem() if cs_to is None else cs_to
        self.cs_self = CoordinateSystem() if cs_self is None else cs_self

    def __call__(self, p):
        """

        Args:
            p (Point): Point to transform

        Returns:
            Point: Transformed point
        """
        return p


class Translate(Transform):
    """Translate coordinates of the Point by the displacement

    Args:
        delta (list or np.ndarray): displacement
    """

    def __init__(self, delta, **kwargs):
        super().__init__(**kwargs)
        self.delta = delta if isinstance(delta, np.ndarray) else np.array(delta)

    def __call__(self, p):
        p = super().__call__(p)
        p.coordinates += self.delta
        return p


class Rotate(Transform):
    """
    TODO only for 3D coordinate systems
    Args:
        origin (list or np.ndarray): origin of rotation
        direction (list or np.ndarray): rotation axis
        angle (float): counterclockwise angle of rotation in radians [0, 2*pi)
    """

    def __init__(self, origin, direction, angle, **kwargs):
        super().__init__(**kwargs)
        self.origin = origin if isinstance(origin, np.ndarray) else np.array(origin)
        self.direction = direction if isinstance(direction, np.ndarray) else np.array(direction)
        self.angle = angle
        a = np.cos(0.5 * self.angle)
        b, c, d = -self.direction * np.sin(0.5 * self.angle)
        aa, bb, cc, dd = a * a, b * b, c * c, d * d
        bc, ad, ac, ab, bd, cd = b * c, a * d, a * c, a * b, b * d, c * d
        self.rotation_matrix = np.array([
            [aa + bb - cc - dd, 2 * (bc + ad), 2 * (bd - ac)],
            [2 * (bc - ad), aa + cc - bb - dd, 2 * (cd + ab)],
            [2 * (bd + ac), 2 * (cd - ab), aa + dd - bb - cc]])

    def __call__(self, p):
        p = super().__call__(p)
        m = self.rotation_matrix
        cs = p.coordinates - self.origin
        cs = np.dot(cs, m.T)
        p.coordinates = cs + self.origin
        return p


# TODO Dilate, Reflect


class CartesianToCartesian(Transform):
    """Convert coordinates of the Point from Cartesian to Cartesian system.

    For compatibility.
    """

    def __init__(self, **kwargs):
        super().__init__(cs_from=Cartesian(), cs_to=Cartesian(), **kwargs)

    def __call__(self, p):
        p = super().__call__(p)
        if not isinstance(p.coordinate_system, type(self.cs_from)):
            raise ValueError(p, self)
        return p


class CylindricalToCartesian(Transform):
    """Convert coordinates of the Point from Cylindrical to Cartesian system.

    [r, phi, z] -> [x, y, z]
    r - radius [0, inf),
    phi - azimuthal angle [0, 2*pi) (counterclockwise from X to Y),
    z - height
    """

    def __init__(self, **kwargs):
        super().__init__(cs_from=Cylindrical(), cs_to=Cartesian(), **kwargs)

    def __call__(self, p):
        p = super().__call__(p)
        if isinstance(p.coordinate_system, Cartesian):  # FIXME workaround for double any_to_cartesian
            return p
        r, phi, z = p.coordinates
        p.coordinates = np.array([r * np.cos(phi), r * np.sin(phi), z])
        p.coordinate_system = self.cs_to
        return p


class SphericalToCartesian(Transform):
    """Convert coordinates of the Point from Spherical to Cartesian system.

    [r, phi, theta] -> [x, y, z]

    * r - radius [0, inf)
    * phi - azimuthal angle [0, 2*pi) (counterclockwise from X to Y)
    * theta - polar angle [0, pi] [from top to bottom, i.e XY-plane is pi/2]
    """

    def __init__(self, **kwargs):
        super().__init__(cs_from=Spherical(), cs_to=Cartesian(), **kwargs)

    def __call__(self, p):
        p = super().__call__(p)
        if isinstance(p.coordinate_system, Cartesian):
            return p
        r, phi, theta = p.coordinates
        p.coordinates = np.array([r * np.cos(phi) * np.sin(theta),
                                  r * np.sin(phi) * np.sin(theta),
                                  r * np.cos(theta)])
        p.coordinate_system = self.cs_to
        return p


class ToroidalToCartesian(Transform):
    """Convert coordinates of the Point from Toroidal to Cartesian system.

    [r, phi, theta, r2] -> [x, y, z]

    r - inner radius (r < r2)

    phi - inner angle [0, 2*pi)

    theta - outer angle [0, 2*pi)

    r2 - outer radius
    """

    def __init__(self, **kwargs):
        super().__init__(cs_from=Toroidal(), cs_to=Cartesian(), **kwargs)

    def __call__(self, p):
        p = super().__call__(p)
        if isinstance(p.coordinate_system, Cartesian):
            return p
        r, phi, theta, r2 = p.coordinates
        p.coordinates = np.array([r2 * np.cos(theta) + r * np.cos(phi) * np.cos(theta),
                                  r2 * np.sin(theta) + r * np.cos(phi) * np.sin(theta),
                                  r * np.sin(phi)])
        p.coordinate_system = self.cs_to
        return p


class TokamakToCartesian(Transform):
    """Convert coordinates of the Point from Tokamak to Cartesian system.

    [r, phi, theta, r2, kxy, kz] -> [x, y, z]

    r - inner radius (r < r2)

    phi - inner angle [0, 2*pi)

    theta - outer angle [0, 2*pi)

    r2 - outer radius

    kxy - inner radius XY scale coefficient in positive outer radius direction

    kz - inner radius Z scale coefficient
    """

    def __init__(self, **kwargs):
        super().__init__(cs_from=Tokamak(), cs_to=Cartesian(), **kwargs)

    def __call__(self, p):
        p = super().__call__(p)
        if isinstance(p.coordinate_system, Cartesian):
            return p
        r, phi, theta, r2, kxy, kz = p.coordinates
        if 0 <= phi <= 0.5 * np.pi or 1.5 * np.pi <= phi <= 2 * np.pi:
            p.coordinates = np.array([
                r2 * np.cos(theta) + kxy * r * np.cos(phi) * np.cos(theta),
                r2 * np.sin(theta) + kxy * r * np.cos(phi) * np.sin(theta),
                kz * r * np.sin(phi)])
        else:
            p.coordinates = np.array([
                r2 * np.cos(theta) + r * np.cos(phi) * np.cos(theta),
                r2 * np.sin(theta) + r * np.cos(phi) * np.sin(theta),
                kz * r * np.sin(phi)])
        p.coordinate_system = self.cs_to
        return p


class BlockToCartesian(Transform):
    """Convert coordinates of the Point from Block to Cartesian system.

    [xi, eta, zeta] -> [x, y, z]

    xi, eta, zeta - local block coordinates

    Args:
        cs_from(Block): Block Coordinate System
    """

    def __init__(self, cs_from, **kwargs):
        super().__init__(cs_from=cs_from, cs_to=Cartesian(), **kwargs)

    def __call__(self, p):
        p = super().__call__(p)
        # if isinstance(self.cs_from, Cartesian):
        #     return p
        xi, eta, zeta = p.coordinates  # Point coordinates
        ps = self.cs_from.ps  # Block points coordinates
        order = self.cs_from.order  # Block points order
        n = np.array([0.125 * (1 + x * xi) * (1 + y * eta) * (1 + z * zeta)
                      for x, y, z in order])
        p.coordinates = n.dot(ps)
        p.coordinate_system = self.cs_to
        return p


class AffineToAffine(Transform):
    """Convert coordinates of the Point from Affine to Affine system.

   [x0, y0, z0] -> [x1, y1, z1]

   Args:
       cs_to (Affine): Affine coordinate system
   """

    def __init__(self, cs_to, **kwargs):
        super().__init__(cs_to=cs_to, **kwargs)

    def __call__(self, p):
        p = super().__call__(p)
        cs0, cs1 = p.coordinate_system, self.cs_to  # Coordinate systems
        if not isinstance(cs0, Affine):
            return p
        vs0, vs1 = p.coordinate_system.vs, self.cs_to.vs  # Basis vectors
        o0, o1 = p.coordinate_system.origin, self.cs_to.origin  # Origins
        cds0 = p.coordinates  # Coordinates at old coordinate system
        cds01 = np.dot(vs0.T, cds0)  # Cartesian coordinate system
        cds01 += o0  # Without origin of old coordinate system
        cds01 -= o1  # With origin of new coordinate system
        cds1 = np.linalg.solve(vs1.T, cds01)  # New coordinate system
        p.coordinates = cds1
        p.coordinate_system = cs1
        return p


class AffineToCartesian(Transform):
    """Convert coordinates of the Point from Affine to Cartesian system.

   [x0, y0, z0] -> [x, y, z]
   """

    def __init__(self, **kwargs):
        super().__init__(cs_to=Cartesian(), **kwargs)

    def __call__(self, p):
        p = super().__call__(p)
        cs0, cs1 = p.coordinate_system, self.cs_to  # Coordinate systems
        if isinstance(cs0, type(cs1)):
            return p
        if not isinstance(cs0, Affine):
            return p
        vs0 = p.coordinate_system.vs  # Affine basis vectors
        o0 = p.coordinate_system.origin  # Affine origin
        cds0 = p.coordinates  # Coordinates at Affine coordinate system
        cds01 = np.dot(vs0.T, cds0)  # Cartesian coordinate system
        cds01 += o0  # Without origin of Affine coordinate system
        p.coordinates = cds01
        p.coordinate_system = cs1
        return p


class PathToCartesian(Transform):
    """Convert coordinates of the Point from Path to Cartesian system.

    [x, y, u] -> [x, y, z]

    u - relative path coordinate [0, 1], where 0 - start of the path, 1 - end.

    x, y - Cartesian coordinates [-inf, inf] on the normal plane to direction
    of the path derivative at the point with relative path coordinate u.
    """

    def __init__(self, **kwargs):
        super().__init__(cs_to=Cartesian(), **kwargs)

    def __call__(self, p):
        p = super().__call__(p)
        if isinstance(p.coordinate_system, type(self.cs_to)):
            return p
        if not isinstance(p.coordinate_system, Path):
            return p
        u = p.coordinates[2]  # Curve local coordinate
        p.coordinates[2] = 0
        lcs = p.coordinate_system.get_local_coordinate_system(u)
        any2car = factory[lcs.__class__]()
        p.coordinate_system = lcs
        p = any2car(p)
        return p


class LayerXYToCartesian(Transform):
    def __init__(self, **kwargs):
        super().__init__(cs_to=Cartesian(), **kwargs)

    def __call__(self, p):
        p = super().__call__(p)
        if isinstance(p.coordinate_system, type(self.cs_to)):
            return p
        if not isinstance(p.coordinate_system, LayerXY):
            return p
        cs = p.coordinate_system
        px, py, pz = p.coordinates
        n_layers = len(cs.layers[0])
        lx0, ly0, lnx0, lny0 = (cs.layers[i][0] for i in range(4))
        for j in range(n_layers):
            lx, ly, lnx, lny = (cs.layers[i][j] for i in range(4))
            n_x, n_y, n_nx, n_ny = (cs.curves_names[i][j] for i in range(4))
            lt = cs.layers_types[j]
            if py == ly0 and px == lx:  # I sector X
                logging.debug('I sector X')
                py, px = self.update_coordinate(p0=py, pn=px,
                                                n0=n_y, nn=n_x,
                                                l00=ly0, l0n=ly,
                                                ln0=lx0, lnn=lx,
                                                lt=lt)
                break
            elif px == lx0 and py == ly:  # I sector Y
                logging.debug('I sector Y')
                px, py = self.update_coordinate(p0=px, pn=py,
                                                n0=n_x, nn=n_y,
                                                l00=lx0, l0n=lx,
                                                ln0=ly0, lnn=ly,
                                                lt=lt)
                break
            elif px == lnx0 and py == ly:  # II sector Y
                logging.debug('II sector Y')
                px, py = self.update_coordinate(p0=px, pn=py,
                                                n0=n_nx, nn=n_y,
                                                l00=lnx0, l0n=lnx,
                                                ln0=ly0, lnn=ly,
                                                lt=lt)
                break
            elif py == ly0 and px == lnx:  # II sector X
                logging.debug('II sector X')
                py, px = self.update_coordinate(p0=py, pn=px,
                                                n0=n_y, nn=n_nx,
                                                l00=ly0, l0n=ly,
                                                ln0=lnx0, lnn=lnx,
                                                lt=lt)
                break
            elif py == lny0 and px == lnx:  # III sector X
                logging.debug('III sector X')
                py, px = self.update_coordinate(p0=py, pn=px,
                                                n0=n_ny, nn=n_nx,
                                                l00=lny0, l0n=lny,
                                                ln0=lnx0, lnn=lnx,
                                                lt=lt)
                break
            elif px == lnx0 and py == lny:  # III sector Y
                logging.debug('III sector Y')
                px, py = self.update_coordinate(p0=px, pn=py,
                                                n0=n_nx, nn=n_ny,
                                                l00=lnx0, l0n=lnx,
                                                ln0=lny0, lnn=lny,
                                                lt=lt)
                break
            elif px == lx0 and py == lny:  # IV sector Y
                logging.debug('IV sector Y')
                px, py = self.update_coordinate(p0=px, pn=py,
                                                n0=n_x, nn=n_ny,
                                                l00=lx0, l0n=lx,
                                                ln0=lny0, lnn=lny,
                                                lt=lt)
                break
            elif py == lny0 and px == lx:  # IV sector X
                logging.debug('IV sector X')
                py, px = self.update_coordinate(p0=py, pn=px,
                                                n0=n_ny, nn=n_x,
                                                l00=lny0, l0n=lny,
                                                ln0=lx0, lnn=lx,
                                                lt=lt)
                break
            else:
                continue
        p.coordinates = np.array([px, py, pz]) + cs.origin
        p.coordinate_system = self.cs_to
        return p

    @staticmethod
    def update_coordinate(p0, pn, n0, nn, l00, l0n, ln0, lnn, lt):
        if n0 == 'line' and nn == 'line':
            p0 = l0n
        elif n0 == 'circle_arc' and nn == 'circle_arc':
            if lt == 'in':
                r = abs(pn)  # radius
                p0 = np.sign(p0) * r / 2 ** 0.5
                pn = np.sign(pn) * r / 2 ** 0.5
            else:
                p0 = l0n
        else:
            raise NotImplementedError(n0, nn)
        return p0, pn


factory = {
    Transform.__name__: Transform,
    Translate.__name__: Translate,
    Translate.__name__.lower(): Translate,
    'tra': Translate,
    Rotate.__name__: Rotate,
    Rotate.__name__.lower(): Rotate,
    'rot': Rotate,
    CartesianToCartesian.__name__: CartesianToCartesian,
    Cartesian: CartesianToCartesian,
    'cartesian_to_cartesian': CartesianToCartesian,
    'car2car': CartesianToCartesian,
    CylindricalToCartesian.__name__: CylindricalToCartesian,
    Cylindrical: CylindricalToCartesian,
    'cylindrical_to_cartesian': CylindricalToCartesian,
    'cyl2car': CylindricalToCartesian,
    SphericalToCartesian.__name__: SphericalToCartesian,
    Spherical: SphericalToCartesian,
    'spherical_to_cartesian': SphericalToCartesian,
    'sph2car': SphericalToCartesian,
    ToroidalToCartesian.__name__: ToroidalToCartesian,
    Toroidal: ToroidalToCartesian,
    'toroidal_to_cartesian': ToroidalToCartesian,
    'tor2car': ToroidalToCartesian,
    TokamakToCartesian.__name__: TokamakToCartesian,
    Tokamak: TokamakToCartesian,
    'tokamak_to_cartesian': TokamakToCartesian,
    'tok2car': TokamakToCartesian,
    BlockToCartesian.__name__: BlockToCartesian,
    Block: BlockToCartesian,
    'block_to_cartesian': BlockToCartesian,
    'blo2car': BlockToCartesian,
    AffineToCartesian.__name__: AffineToCartesian,
    Affine: AffineToCartesian,
    'affine_to_cartesian': AffineToCartesian,
    'aff2car': AffineToCartesian,
    AffineToAffine.__name__: AffineToAffine,
    'affine_to_affine': AffineToAffine,
    'aff2aff': AffineToAffine,
    PathToCartesian.__name__: PathToCartesian,
    Path: PathToCartesian,
    'path_to_cartesian': PathToCartesian,
    'pat2car': PathToCartesian,
    LayerXYToCartesian: LayerXYToCartesian,
    'lxy_to_cartesian': LayerXYToCartesian,
    'lxy2car': LayerXYToCartesian
}
