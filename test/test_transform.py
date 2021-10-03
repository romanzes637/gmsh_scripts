import unittest
from functools import reduce
import numpy as np

from transform import CoordinateSystem, Point, Translate, RotateCartesian, \
    CylindricalToCartesian, ToroidalToCartesian, TokamakToCartesian, SphericalToCartesian, \
    BlockToCartesian, BlockCS


class TestTransform(unittest.TestCase):

    def test_1(self):
        cs_car = CoordinateSystem('cartesian', 3, np.array([0, 0, 0]))
        cs_syl = CoordinateSystem('cylindrical', 3, np.array([0, 0, 0]))
        cs_sph = CoordinateSystem('spherical', 3, np.array([0, 0, 0]))
        cs_tor = CoordinateSystem('toroidal', 4, np.array([0, 0, 0, 0]))
        cs_tok = CoordinateSystem('tokamak', 6, np.array([0, 0, 0, 0, 0, 0]))
        cs_blo = BlockCS(ps=np.array([
            [1, 1, 0], [0, 1, 0], [0, 0, 0], [1, 0, 0],
            [1, 1, 1], [0, 1, 1], [0, 0, 1], [1, 0, 1]
        ]))
        p_car = Point(cs_car, np.array([0, 0, 1]))
        p_cyl = Point(cs_syl, np.array([0, np.radians(45), 1]))
        ps_sph = Point(cs_sph, np.array([1, np.radians(45), np.radians(60)]))
        p_tor = Point(cs_tor, np.array([1, np.radians(30), np.radians(45), 5]))
        p_tok = Point(cs_tok, np.array([1, np.radians(30), np.radians(45),
                                        5, 1.1, 1.2]))
        p_blo = Point(cs_blo, np.array([0.5, -0.5, 0]))
        t1 = Translate(cs_car, cs_car, cs_car, delta=np.array([0, 1, 2]))
        t2 = Translate(cs_car, cs_car, cs_car, delta=np.array([0, 1, 2]))
        cyl2car = CylindricalToCartesian()
        tor2car = ToroidalToCartesian()
        tok2car = TokamakToCartesian()
        sph2car = SphericalToCartesian()
        blo2car = BlockToCartesian(cs_from=cs_blo)
        r1 = RotateCartesian(origin=np.array([0, 0, 0]),
                             direction=np.array([1, 0, 0]),
                             angle=np.radians(30))
        p = reduce(lambda x, y: y(x), [r1, t1, t2], p_car)
        print(p.vs)
        p = reduce(lambda x, y: y(x), [cyl2car, r1, t1, t2], p_cyl)
        print(p.vs)
        p = reduce(lambda x, y: y(x), [sph2car, r1, t1, t2], ps_sph)
        print(p.vs)
        p = reduce(lambda x, y: y(x), [tor2car, r1, t1, t2], p_tor)
        print(p.vs)
        p = reduce(lambda x, y: y(x), [tok2car, r1, t1, t2], p_tok)
        print(p.vs)
        print(p_blo.vs)
        p = reduce(lambda x, y: y(x), [blo2car, t1, r1, t1], p_blo)
        print(p.vs)


if __name__ == '__main__':
    unittest.main()
