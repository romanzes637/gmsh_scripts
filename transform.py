import numpy as np
from functools import reduce

from coordinate_system import factory as cs_factory


def reduce_transforms(transforms, point):
    return reduce(lambda x, y: y(x), transforms, point)


class Transform:
    def __init__(self, cs_from=None, cs_to=None, cs_self=None, **kwargs):
        """
        Args:
            cs_from (CoordinateSystem): CoordinateSystem from
            cs_to (CoordinateSystem): CoordinateSystem to
            cs_self (CoordinateSystem): CoordinateSystem self
        """
        self.cs_from = cs_factory['coordinate_system']() if cs_from is None else cs_from
        self.cs_to = cs_factory['coordinate_system']() if cs_to is None else cs_to
        self.cs_self = cs_factory['coordinate_system']() if cs_self is None else cs_self

    def __call__(self, p):
        """
        Args:
            p(Point): point to transform

        Returns:
            Point: transformed point
        """
        return p


# Translation, Rotation, Dilation, Reflection
class Translate(Transform):
    """
    Args:
        delta (np.array or list): displacement
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
        origin (np.array or list): origin of rotation
        direction (np.array or list): rotation axis
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
    def __init__(self, **kwargs):
        """
        [r, phi, z] -> [x, y, z]
        r - radius [0, inf),
        phi - azimuthal angle [0, 2*pi) (counterclockwise from X to Y),
        z - height
        """
        super().__init__(cs_factory['cylindrical'](), cs_factory['cartesian'](),
                         **kwargs)

    def __call__(self, p):
        p = super().__call__(p)
        if isinstance(p.coordinate_system, cs_factory['cartesian']):  # FIXME workaround for double any_to_cartesian
            return p
        r, phi, z = p.coordinates
        p.coordinates = np.array([r * np.cos(phi), r * np.sin(phi), z])
        p.coordinate_system = self.cs_to
        return p


class SphericalToCartesian(Transform):
    def __init__(self, **kwargs):
        """
        [r, phi, theta] -> [x, y, z]
        r - radius [0, inf),
        phi - azimuthal angle [0, 2*pi) (counterclockwise from X to Y),
        theta - polar angle [0, pi] [from top to bottom, i.e XY-plane is pi/2]
        """
        super().__init__(cs_factory['spherical'](), cs_factory['cartesian'](), 
                         **kwargs)

    def __call__(self, p):
        p = super().__call__(p)
        if isinstance(p.coordinate_system, cs_factory['cartesian']()):
            return p
        r, phi, theta = p.coordinates
        p.coordinates = np.array([r * np.cos(phi) * np.sin(theta),
                         r * np.sin(phi) * np.sin(theta),
                         r * np.cos(theta)])
        p.coordinate_system = self.cs_to
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
        super().__init__(cs_factory['toroidal'](), cs_factory['cartesian'](), 
                         **kwargs)

    def __call__(self, p):
        p = super().__call__(p)
        if isinstance(p.coordinate_system, cs_factory['cartesian']()):
            return p
        r, phi, theta, r2 = p.coordinates
        p.coordinates = np.array([r2 * np.cos(theta) + r * np.cos(phi) * np.cos(theta),
                         r2 * np.sin(theta) + r * np.cos(phi) * np.sin(theta),
                         r * np.sin(phi)])
        p.coordinate_system = self.cs_to
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
        super().__init__(cs_factory['tokamak'](), cs_factory['cartesian'](), 
                         **kwargs)

    def __call__(self, p):
        p = super().__call__(p)
        if isinstance(p.coordinate_system, cs_factory['cartesian']()):
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
    def __init__(self, cs_from, **kwargs):
        """
        [xi, eta, zeta] -> [x, y, z]
        xi, eta, zeta - local block coordinates
        Args:
            cs_from(Block): Block Coordinate System
        """
        super().__init__(cs_from=cs_from, cs_to=cs_factory['cartesian'](), 
                         **kwargs)

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
    'translate': Translate,
    'rotate': Rotate,
    'cylindrical_to_cartesian': CylindricalToCartesian,
    'Spherical_to_cartesian': SphericalToCartesian,
    'toroidal_to_cartesian': ToroidalToCartesian,
    'tokamak_to_cartesian': TokamakToCartesian,
    'block_to_cartesian': BlockToCartesian
}
