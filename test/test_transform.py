import unittest
from functools import reduce
import numpy as np
import logging

from point import Point
from coordinate_system import Block, Cartesian, Cylindrical, Spherical, \
    Toroidal, Tokamak
from transform import Translate, Rotate, CylindricalToCartesian, \
    ToroidalToCartesian, TokamakToCartesian, SphericalToCartesian, BlockToCartesian

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


if __name__ == '__main__':
    unittest.main()
