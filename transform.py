import numpy as np
from functools import reduce

from coordinate_system import CoordinateSystem, Cartesian, Cylindrical, \
    Spherical, Toroidal, Tokamak, Block


def reduce_transforms(transforms, point):
    return reduce(lambda x, y: y(x), transforms, point)


class Transform:
    """
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
            p (Point): point to transform

        Returns:
            Point: transformed point
        """
        return p


# Translation, Rotation, Dilation, Reflection
class Translate(Transform):
    """
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


class CylindricalToCartesian(Transform):
    """
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
    """
    [r, phi, theta] -> [x, y, z]
    r - radius [0, inf),
    phi - azimuthal angle [0, 2*pi) (counterclockwise from X to Y),
    theta - polar angle [0, pi] [from top to bottom, i.e XY-plane is pi/2]
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
    """
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
    """
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
    """
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


factory = {
    Transform.__name__: Transform,
    Translate.__name__: Translate,
    Translate.__name__.lower(): Translate,
    'tra': Translate,
    Rotate.__name__: Rotate,
    Rotate.__name__.lower(): Rotate,
    'rot': Rotate,
    CylindricalToCartesian.__name__: CylindricalToCartesian,
    'cylindrical_to_cartesian': CylindricalToCartesian,
    'cyl2car': CylindricalToCartesian,
    SphericalToCartesian.__name__: SphericalToCartesian,
    'spherical_to_cartesian': SphericalToCartesian,
    'sph2car': SphericalToCartesian,
    ToroidalToCartesian.__name__: ToroidalToCartesian,
    'toroidal_to_cartesian': ToroidalToCartesian,
    'tor2car': ToroidalToCartesian,
    TokamakToCartesian.__name__: TokamakToCartesian,
    'tokamak_to_cartesian': TokamakToCartesian,
    'tok2car': TokamakToCartesian,
    BlockToCartesian.__name__: BlockToCartesian,
    'block_to_cartesian': BlockToCartesian,
    'blo2car': BlockToCartesian
}
