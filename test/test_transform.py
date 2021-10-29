import unittest
from functools import reduce
import logging

import gmsh
import numpy as np

from registry import register_point, register_curve
from point import Point
from curve import Curve
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
        gmsh.initialize()
        model_name = 'test_path2'
        factory = 'geo'
        gmsh.model.add(model_name)
        curves = [
            ['line', [[0, 0, 0], [0, 1, 0]]],
            ['polyline', [[0, 1, 0], [1, 1, 1], [1, 2, 1], [2, 2, 2]]],
            ['spline', [[2, 2, 2], [2, 3, 2], [2, 3, 3]]],
            ['circle_arc', [[2, 3, 3], [2, 2, 3], [3, 2, 3]]],
            ['ellipse_arc', [[3, 2, 3], [5, 2, 3], [3, 2, 3], [5, 1, 3]]],
            ['bspline', [[5, 1, 3], [3, 3, 2], [2, 0, 0]]],
            ['spline', [[2, 0., 0], [2, -10, 0.5], [2, -30, 1.],
                        [2, -60, 1.5], [2, -80, 2.0], [2, -110, 2.5],
                        [2, -130, 3.0], [2, -150, 3.5], [2, -180, 4],
                        'cyl']],
            ['bezier', [[2, 180, 90], [2, 135, 45], [2, 90, 0],
                        'sph']],
            ['spline', [
                [1, 0, 180, 3], [1, 45, 190, 3], [1, 90, 200, 3],
                [1, 135, 210, 3], [1, 180, 220, 3], [1, 225, 230, 3],
                [1, 270, 240, 3], [1, 315, 250, 3], [1, 360, 260, 3],
                [1, 0, 270, 3], [1, 45, 280, 3], [1, 90, 290, 3],
                [1, 135, 300, 3], [1, 180, 310, 3], [1, 225, 320, 3],
                [1, 270, 330, 3], [1, 315, 340, 3], [1, 360, 350, 3],
                [1, 0, 360, 3], [1, 45, 10, 3], [1, 90, 20, 3],
                [1, 135, 30, 3], [1, 180, 40, 3], [1, 225, 50, 3],
                'tor']]

        ]
        transforms = [
            [], [], [], [], [], [], [], [[0, 0, 4]], [[4, 0, 6]]
        ]
        orientations = [
                        [[1, 0, 0], [0, 0, -1], [0, 1, 0]],
                        [[1, -1, 0], [0, 0, -1], [1, 1, 0]],
                        [[1, 0, 0], [0, 0, -1], [0, 1, 0]],
                        [[0, -1, 0], [0, 0, -1], [1, 0, 0]],
                        [[-1, 0, 0], [0, 0, -1], [0, -1, 0]],
                        [[-1, 0, 0], [0, 0, -1], [0, -1, 0]],
                        [[-1, 0, 0], [0, 0, -1], [0, -1, 0]],
                        [[0, -1, 0], [0, 0, -1], [1, 0, 0]],
                        [[0, -1, 0], [0, 0, -1], [1, 0, 0]],
                        ]
        weights = [5, 15, 5, 5, 5, 5, 20, 10, 30]
        local_weights = [[1, 4], [], [], [], [], [], [3, 3], [], [0.5, 0.5]]
        cs = Path(curves=curves, orientations=orientations,
                  transforms=transforms, weights=weights,
                  local_weights=local_weights,
                  factory=factory)
        cs.transform()
        cs.register()
        if factory == 'geo':
            gmsh.model.geo.synchronize()
        elif factory == 'occ':
            gmsh.model.occ.synchronize()
        else:
            raise ValueError(factory)
        cs.evaluate_bounds()
        for u in np.linspace(0., 1., 101):
            print(u)
            v, dv, ori = cs.get_value_derivative_orientation(u)
            dv = dv / np.linalg.norm(dv)
            p0 = Point(coordinates=v)
            register_point(factory=factory, point=p0, register_tag=False)
            p1 = Point(coordinates=np.add(v, dv))
            register_point(factory=factory, point=p1, register_tag=False)
            c = Curve(points=[p0, p1], name='line')
            register_curve(factory=factory, curve=c, register_tag=False)
            lcs = cs.get_local_coordinate_system(u)
            for j, v2 in enumerate(lcs.vs):
                v2 = v2 / np.linalg.norm(v2) * 0.1 * (1 + j)
                p3 = Point(coordinates=lcs.origin)
                register_point(factory=factory, point=p3, register_tag=False)
                p4 = Point(coordinates=np.add(lcs.origin, v2))
                register_point(factory=factory, point=p4, register_tag=False)
                c2 = Curve(points=[p3, p4], name='line')
                register_curve(factory=factory, curve=c2, register_tag=False)
        if factory == 'geo':
            gmsh.model.geo.synchronize()
        elif factory == 'occ':
            gmsh.model.occ.synchronize()
        else:
            raise ValueError(factory)
        gmsh.write(f'{model_name}.geo_unrolled')
        gmsh.finalize()

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
