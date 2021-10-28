import unittest
from functools import reduce
import numpy as np
import logging

from point import Point
from coordinate_system import Block, Cartesian, Cylindrical, Spherical, \
    Toroidal, Tokamak, Path, Affine
from transform import Translate, Rotate, CylindricalToCartesian, \
    ToroidalToCartesian, TokamakToCartesian, SphericalToCartesian, BlockToCartesian, \
    PathToCartesian, AffineToAffine, AffineToCartesian

logging.basicConfig(level=logging.INFO)


class TestTransform(unittest.TestCase):

    def test_1(self):
        cs_car = Cartesian()
        cs_syl = Cylindrical()
        cs_sph = Spherical()
        cs_tor = Toroidal()
        cs_tok = Tokamak()
        cs_blo = Block(ps=[[1, 1, 0], [0, 1, 0], [0, 0, 0], [1, 0, 0],
                           [1, 1, 1], [0, 1, 1], [0, 0, 1], [1, 0, 1]])
        p_car = Point([0, 0, 1, cs_car])
        p_cyl = Point([0, np.deg2rad(45), 1, cs_syl])
        ps_sph = Point([1, np.deg2rad(45), np.deg2rad(60), cs_sph])
        p_tor = Point([1, np.deg2rad(30), np.deg2rad(45), 5, cs_tor])
        p_tok = Point([1, np.deg2rad(30), np.deg2rad(45), 5, 1.1, 1.2, cs_tok])
        p_blo = Point([0.5, -0.5, 0, cs_blo])
        t1 = Translate(delta=[0, 1, 2])
        t2 = Translate(delta=[0, 1, 2])
        cyl2car = CylindricalToCartesian()
        tor2car = ToroidalToCartesian()
        tok2car = TokamakToCartesian()
        sph2car = SphericalToCartesian()
        blo2car = BlockToCartesian(cs_from=cs_blo)
        r1 = Rotate(origin=[0, 0, 0], direction=[1, 0, 0], angle=np.deg2rad(30))
        p = reduce(lambda x, y: y(x), [r1, t1, t2], p_car)
        p = reduce(lambda x, y: y(x), [cyl2car, r1, t1, t2], p_cyl)
        p = reduce(lambda x, y: y(x), [sph2car, r1, t1, t2], ps_sph)
        p = reduce(lambda x, y: y(x), [tor2car, r1, t1, t2], p_tor)
        p = reduce(lambda x, y: y(x), [tok2car, r1, t1, t2], p_tok)
        p = reduce(lambda x, y: y(x), [blo2car, t1, r1, t1], p_blo)

    def test_path(self):
        ps = [[0, 0, 1], [0, 1, 1], [1, 2, 1]]
        vs = [[[1, 0, 0], [0, 0, -1], [0, 1, 0]]]  # right, down, front
        cs = Path(ps=ps, vs=vs)
        p = Point([0.25, 0.25, 0.25])  # right, down, front
        pth2car = PathToCartesian(cs_from=cs)
        print(p.coordinates)
        p = pth2car(p)
        print(p.coordinates)

    def test_affine(self):
        a0 = Affine(vs=[[0.5, 0.5, 0], [-0.5, 0.5, 0], [0, 0.2, 1]], origin=[-1, 0, 0])
        a1 = Affine(vs=[[-0.25, -0.25, 0.5], [-0.5, 0.5, 0], [0.1, 0, 1]], origin=[0, 1, 0])
        p = Point(coordinates=[0.5, 1, 1], coordinate_system=a0)
        print('a0')
        print(p.coordinates)
        to_a1 = AffineToAffine(cs_to=a1)
        to_a0 = AffineToAffine(cs_to=a0)
        to_c = AffineToCartesian()
        p1 = to_a1(p)
        print('a0 to a1')
        print(p1.coordinates, p1.coordinate_system)
        p0 = to_a0(p1)
        print('a1 to a0')
        print(p0.coordinates, p0.coordinate_system)
        pc = to_c(p0)
        print('a0 to c')
        print(pc.coordinates, pc.coordinate_system)
        pc = to_c(p1)
        print('a1 to c')
        print(pc.coordinates, pc.coordinate_system)
        print('c to a0')
        p0 = to_a0(pc)
        print(p0.coordinates, p0.coordinate_system)
        print('c to a1')
        p1 = to_a1(pc)
        print(p1.coordinates, p1.coordinate_system)


if __name__ == '__main__':
    unittest.main()
