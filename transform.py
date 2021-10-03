import numpy as np
from functools import reduce


class Point:
    """
    Args:
        cs (CoordinateSystem): CoordinateSystem
        vs (np.array): coordinates (values
    """
    def __init__(self, cs, vs):
        self.cs = cs
        self.vs = vs


class CoordinateSystem:
    def __init__(self, name=None, dim=None, origin=None, **kwargs):
        self.name = name
        self.dim = dim
        self.origin = origin


class Cartesian(CoordinateSystem):
    def __init__(self, origin=np.zeros(3), **kwargs):
        super().__init__(name='cartesian', dim=3, origin=origin, **kwargs)


class Cylindrical(CoordinateSystem):
    def __init__(self, origin=np.zeros(3), **kwargs):
        super().__init__(name='cylindrical', dim=3, origin=origin, **kwargs)


class Spherical(CoordinateSystem):
    def __init__(self, origin=np.zeros(3), **kwargs):
        super().__init__(name='spherical', dim=3, origin=origin, **kwargs)


class Toroidal(CoordinateSystem):
    def __init__(self, origin=np.zeros(4), **kwargs):
        super().__init__(name='toroidal', dim=4, origin=origin, **kwargs)


class Tokamak(CoordinateSystem):
    def __init__(self, origin=np.zeros(6), **kwargs):
        super().__init__(name='tokamak', dim=6, origin=origin, **kwargs)


class Block(CoordinateSystem):
    def __init__(self, ps, origin=np.zeros(3), order=None, **kwargs):
        """Local Block Coordinate System

        xi [-1, 1]
        eta [-1, 1]
        zeta [-1, 1]

        Args:
            ps (np.array): points coordinates of the block
            order (np.array): order of points
        """
        super().__init__(name='block', dim=3, origin=origin, **kwargs)
        self.ps = ps
        if order is None:
            self.order = np.array(
                [[1, 1, -1], [-1, 1, -1], [-1, -1, -1], [1, -1, -1],
                 [1, 1, 1], [-1, 1, 1], [-1, -1, 1], [1, -1, 1]])
        else:
            self.order = order

    def shape_functions(self, p):
        xi, eta, zeta = p.vs
        return np.array([0.125 * (1 + x * xi) * (1 + y * eta) * (1 + z * zeta)
                         for x, y, z in self.order])


cs_factory = {
    'cartesian': Cartesian,
    'cylindrical': Cylindrical,
    'spherical': Spherical,
    'toroidal': Toroidal,
    'tokamak': Tokamak,
    'block': Block
}


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
        # Check coordinate system from
        if self.cs_from.name is not None and p.cs.name != self.cs_from.name:
            raise ValueError(p.cs.name)
        if self.cs_from.dim is not None and p.cs.dim != self.cs_from.dim:
            raise ValueError(p.cs.dim)
        return p


# Translation, Rotation, Dilation, Reflection
class Translate(Transform):
    """
    Args:
        delta (np.array): displacement
    """
    def __init__(self, delta, **kwargs):
        super().__init__(**kwargs)
        self.delta = delta if isinstance(delta, np.ndarray) else np.array(delta)

    def __call__(self, p):
        p = super().__call__(p)
        p.vs += self.delta
        return p


class RotateCartesian(Transform):
    """

    Args:
        origin (np.array): origin of rotation
        direction (np.array): rotation axis
        angle (float): counterclockwise angle of rotation in radians [0, 2*pi)
    """
    def __init__(self, origin, direction, angle, **kwargs):
        super().__init__(Cartesian(), Cartesian(), **kwargs)
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
        m = self.rotation_matrix
        vs = p.vs - self.origin
        vs = np.dot(vs, m.T)
        p.vs = vs + self.origin
        return p


class CylindricalToCartesian(Transform):
    def __init__(self, **kwargs):
        """
        [r, phi, z] -> [x, y, z]
        r - radius [0, inf),
        phi - azimuthal angle [0, 2*pi) (counterclockwise from X to Y),
        z - height
        """
        super().__init__(Cylindrical(), Cartesian(), **kwargs)

    def __call__(self, p):
        p = super().__call__(p)
        r, phi, z = p.vs
        p.vs = np.array([r * np.cos(phi), r * np.sin(phi), z])
        p.cs = self.cs_to
        return p


class SphericalToCartesian(Transform):
    def __init__(self, **kwargs):
        """
        [r, phi, theta] -> [x, y, z]
        r - radius [0, inf),
        phi - azimuthal angle [0, 2*pi) (counterclockwise from X to Y),
        theta - polar angle [0, pi] [from top to bottom, i.e XY-plane is pi/2]
        """
        super().__init__(Spherical(), Cartesian(), **kwargs)

    def __call__(self, p):
        p = super().__call__(p)
        r, phi, theta = p.vs
        p.vs = [r * np.cos(phi) * np.sin(theta),
                r * np.sin(phi) * np.sin(theta),
                r * np.cos(theta)]
        p.cs = self.cs_to
        return p


class ToroidalToCartesian(Transform):
    def __init__(self, **kwargs):
        """
        [r, phi, theta, r2] -> [x, y, z]
        r - inner radius (r < r2)
        phi - inner angle [0, 2*pi)
        theta - outer angle [0, 2*pi)
        r2 - outer radius
        """
        super().__init__(Toroidal(), Cartesian(), **kwargs)

    def __call__(self, p):
        p = super().__call__(p)
        r, phi, theta, r2 = p.vs
        p.vs = np.array([r2 * np.cos(theta) + r * np.cos(phi) * np.cos(theta),
                         r2 * np.sin(theta) + r * np.cos(phi) * np.sin(theta),
                         r * np.sin(phi)])
        p.cs = self.cs_to
        return p


class TokamakToCartesian(Transform):
    def __init__(self, **kwargs):
        """
        [r, phi, theta, r2, kxy, kz] -> [x, y, z]
        r - inner radius (r < r2)
        phi - inner angle [0, 2*pi)
        theta - outer angle [0, 2*pi)
        r2 - outer radius
        kxy - inner radius XY scale coefficient in positive outer radius direction
        kz - inner radius Z scale coefficient
        """
        super().__init__(Toroidal(), Cartesian(), **kwargs)

    def __call__(self, p):
        p = super().__call__(p)
        r, phi, theta, r2, kxy, kz = p.vs[:6]
        if 0 <= phi <= 0.5 * np.pi or 1.5 * np.pi <= phi <= 2 * np.pi:
            p.vs = np.array([
                r2 * np.cos(theta) + kxy * r * np.cos(phi) * np.cos(theta),
                r2 * np.sin(theta) + kxy * r * np.cos(phi) * np.sin(theta),
                kz * r * np.sin(phi)])
        else:
            p.vs = np.array([
                r2 * np.cos(theta) + r * np.cos(phi) * np.cos(theta),
                r2 * np.sin(theta) + r * np.cos(phi) * np.sin(theta),
                kz * r * np.sin(phi)])
        p.cs = self.cs_to
        return p


class BlockToCartesian(Transform):
    """
    [xi, eta, zeta] -> [x, y, z]
    xi, eta, zeta - local block coordinates
    """
    def __init__(self, cs_from, **kwargs):
        super().__init__(cs_from=cs_from,
                         cs_to=Cartesian(),
                         **kwargs)

    def __call__(self, p):
        p = super().__call__(p)
        n = self.cs_from.shape_functions(p)  # Shape Functions
        ps = self.cs_from.ps  # Points coordinates
        p.vs = n.dot(ps)
        p.cs = self.cs_to
        return p


def reduce_transforms(transforms, point):
    return reduce(lambda x, y: y(x), transforms, point)


transform_factory = {
    'translate': Translate,
    'rotate': RotateCartesian,
    'cylindrical_to_cartesian': CylindricalToCartesian,
    'Spherical_to_cartesian': SphericalToCartesian,
    'toroidal_to_cartesian': ToroidalToCartesian,
    'tokamak_to_cartesian': TokamakToCartesian,
    'block_to_cartesian': BlockToCartesian
}
