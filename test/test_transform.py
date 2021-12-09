import unittest
from functools import reduce
import logging

import gmsh
import numpy as np

from block import Block as BlockObject
from registry import register_point, register_curve
from point import Point
from curve import Curve
from coordinate_system import Block, Cartesian, Cylindrical, Spherical, \
    Toroidal, Tokamak, Path, Affine, LayerXY
from transform import Translate, Rotate, CylindricalToCartesian, \
    ToroidalToCartesian, TokamakToCartesian, SphericalToCartesian, BlockToCartesian, \
    PathToCartesian, AffineToAffine, AffineToCartesian, LayerXYToCartesian
from zone import BlockDirection, BlockSimple
from matrix import Matrix
from registry import reset as reset_registry
from support import timeit
from strategy import Simple, Boolean
from boolean import boolean as boolean_all

from support import LoggingDecorator, GmshDecorator, GmshOptionsDecorator

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
        gmsh.option.setNumber("Mesh.SubdivisionAlgorithm",
                              2)  # (0: none, 1: all quadrangles, 2: all hexahedra, 3: barycentric)
        model_name = 'test_path'
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
            [[0, -1, 0], [1, 0, -1], [1, 0, 1]],
            [[1, 0, 0], [0, 0, -1], [0, 1, 0]],
            [[0, -1, 0], [0, 0, -1], [1, 0, 0]],
            [[-1, 0, 0], [0, 0, -1], [0, -1, 0]],
            [[-1, 0, 0], [0, 0, -1], [0, -1, 0]],
            [[-1, 0, 0], [0, 0, -1], [0, -1, 0]],
            [[0, -1, 0], [0, 0, -1], [1, 0, 0]],
            [[0, -1, 0], [0, 0, -1], [1, 0, 0]],
            [[0, -1, -1], [-1, 0, 0], [0, 1, -1]],
        ]  # number of curves + 1
        weights = [5, 15, 5, 5, 5, 5, 20, 10, 30]
        local_weights = [[1, 4], [], [], [], [], [], [3, 3], [], [0.5, 0.5]]
        cs = Path(curves=curves, orientations=orientations,
                  transforms=transforms, weights=weights,
                  local_weights=local_weights,
                  factory=factory)
        # cs.transform()
        # cs.register()
        # if factory == 'geo':
        #     gmsh.model.geo.synchronize()
        # elif factory == 'occ':
        #     gmsh.model.occ.synchronize()
        # else:
        #     raise ValueError(factory)
        # cs.evaluate_bounds()
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
        n = 100j
        points4 = np.dstack([
            np.column_stack([
                np.ravel(x) for x in np.mgrid[0.1:0.2, 0.1:0.2, 0.7:1:n]]),
            np.column_stack([
                np.ravel(x) for x in np.mgrid[-0.1:0, 0.1:0.2, 0.7:1:n]]),
            np.column_stack([
                np.ravel(x) for x in np.mgrid[-0.1:0, -0.1:0, 0.7:1:n]]),
            np.column_stack([
                np.ravel(x) for x in np.mgrid[0.1:0.2, -0.1:0, 0.7:1:n]])])
        prev_ps4 = None
        bs = []
        b0 = BlockObject(factory=factory,
                         quadrate_all=True,
                         zone_all=[['V'], ['NX', 'X', 'NY', 'Y', 'NZ', 'Z']],
                         points=[30, 30, 30])
        for ps4 in points4:
            if prev_ps4 is not None:
                points = np.vstack((prev_ps4.T, ps4.T)).tolist()
                points = points + [cs]
                b = BlockObject(factory=factory,
                                structure_all=[[3, 0, 1], [3, 0, 1], [3, 0, 1]],
                                quadrate_all=True,
                                points=points,
                                parent=b0,
                                zone_all=[['T']],
                                transforms=['pat2car'])
                bs.append(b)
            prev_ps4 = ps4
        for b in bs:
            b0.add_child(b)
        b0.transform()
        b0.register()
        #     # cs2 = Path(curves=[['spline', points + [cs]]])
        #     cs2.transform()
        #     cs2.register()
        #     if factory == 'geo':
        #         gmsh.model.geo.synchronize()
        #     elif factory == 'occ':
        #         gmsh.model.occ.synchronize()
        #     else:
        #         raise ValueError(factory)
        #     cs2.evaluate_bounds()
        # prev_p = None
        # for u in np.linspace(0., 1., 101):
        #     print(u)
        #     v, dv, ori = cs2.get_value_derivative_orientation(u)
        #     # if np.linalg.norm(dv) != 0:
        #     #     dv = dv / np.linalg.norm(dv)
        #     p0 = Point(coordinates=v)
        #     register_point(factory=factory, point=p0, register_tag=False)
        #     if prev_p is not None:
        #         print(prev_p.coordinates, p0.coordinates)
        #         c2 = Curve(points=[prev_p, p0], name='line')
        #         register_curve(factory=factory, curve=c2, register_tag=False)
        #     prev_p = p0
        # p1 = Point(coordinates=np.add(v, dv))
        # register_point(factory=factory, point=p1, register_tag=False)
        # c = Curve(points=[p0, p1], name='line')
        # register_curve(factory=factory, curve=c, register_tag=False)
        if factory == 'geo':
            gmsh.model.geo.synchronize()
        elif factory == 'occ':
            gmsh.model.occ.synchronize()
        else:
            raise ValueError(factory)
        # b0.quadrate()
        # b0.structure()
        # if factory == 'geo':
        #     gmsh.model.geo.synchronize()
        # elif factory == 'occ':
        #     gmsh.model.occ.synchronize()
        # else:
        #     raise ValueError(factory)
        for vs_dt in gmsh.model.getEntities(3):
            for s_dt in gmsh.model.getBoundary(dimTags=[vs_dt],
                                               combined=False,
                                               oriented=True,
                                               recursive=False):
                gmsh.model.geo.mesh.setRecombine(s_dt[0], s_dt[1])
        BlockSimple()(b0)
        gmsh.model.mesh.generate(3)
        # gmsh.write(f'{model_name}.msh2')
        gmsh.write(f'{model_name}.geo_unrolled')
        gmsh.finalize()

    def test_path_spherical(self):
        gmsh.initialize()
        model_name = 'test_path_spherical'
        factory = 'geo'
        gmsh.model.add(model_name)
        curves = [
            ['line', [[0, 0, 0], [1, 0, 1]]],
            ['line', [[1, 0, 1], [2, 0, 1]]],
            ['line', [[2, 0, 1], [3, 0, 0]]],
            ['line', [[3, 0, 0], [4, 1, 1]]],
            ['line', [[4, 1, 1], [5, 1, 1]]],
            ['line', [[5, 1, 1], [6, 1, 1]]],
        ]
        transforms = None
        orientations = [
            [[1, 270, 90], [1, 0, 90], [1, 0, 0], 'spherical'],
            [[1, 270, 90], [1, 0, 135], [1, 0, 45], 'spherical'],
            [[1, 0, 180], [1, 0, 135], 'spherical'],
            [[1, 0, 135], 'spherical'],
            [[1, 45, np.rad2deg(np.arccos(3 ** -0.5))], 'spherical'],
            [[0, -1, 0], [0, 0, -1], [1, 0, 0]],
            [[0, 0, -1], [1, 0, 0]],
        ]  # number of curves + 1
        weights = None
        local_weights = None
        cs = Path(curves=curves, orientations=orientations,
                  transforms=transforms, weights=weights,
                  local_weights=local_weights,
                  factory=factory)
        # cs.transform()
        # cs.register()
        # if factory == 'geo':
        #     gmsh.model.geo.synchronize()
        # elif factory == 'occ':
        #     gmsh.model.occ.synchronize()
        # else:
        #     raise ValueError(factory)
        # cs.evaluate_bounds()
        for u in np.linspace(0., 1., 21):
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
            for j, v2 in enumerate(ori):
                v2 = v2 / np.linalg.norm(v2) * 0.05
                p3 = Point(coordinates=v)
                register_point(factory=factory, point=p3, register_tag=False)
                p4 = Point(coordinates=np.add(v, v2))
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

    def test_layer_xy(self):
        lxy = LayerXY(layers=[
            [1, 2, 3, 4],
            [1, 2, 3, 4],
            [1, 2, 3, 4],
            [1, 2, 3, 4]])
        lxy2car = LayerXYToCartesian()
        css = [[2, 1, 1],  # I sector X
               [1, 2, 1],  # I sector Y
               [-1, 2, 1],  # II sector Y
               [-2, 1, 1],  # II sector X
               [-2, -1, 1],  # III sector X
               [-1, -2, 1],  # III sector Y
               [1, -2, 1],  # IV sector Y
               [2, -1, 1]]  # IV sector X
        true_css = [[2, 2, 1],  # I sector X
                    [2, 2, 1],  # I sector Y
                    [-2, 2, 1],  # II sector Y
                    [-2, 2, 1],  # II sector X
                    [-2, -2, 1],  # III sector X
                    [-2, -2, 1],  # III sector Y
                    [2, -2, 1],  # IV sector Y
                    [2, -2, 1]]
        for cs, tcs in zip(css, true_css):  # IV sector X
            p0 = Point(coordinates=cs, coordinate_system=lxy)
            logging.info(f'before: {p0.coordinates}')
            p1 = lxy2car(p0)
            logging.info(f'after: {p1.coordinates}')
            self.assertTrue(np.array_equal(p1.coordinates, tcs))

    @LoggingDecorator()
    @GmshDecorator()
    @GmshOptionsDecorator()
    def test_layer_xy_matrix(self):
        for factory in ['geo', 'occ']:
            model_name = f'test_layer_xy_matrix-{factory}'
            logging.info(model_name)
            lxy = LayerXY(
                layers=[
                    [1, 2, 3, 4],
                    [1, 2, 3, 4],
                    [1, 2, 3, 4],
                    [1, 2, 3, 4]],
                layers_curves=[
                    ['line', 'circle_arc', 'circle_arc', 'line'],
                    ['line', 'circle_arc', 'circle_arc', 'line'],
                    ['line', 'circle_arc', 'circle_arc', 'line'],
                    ['line', 'circle_arc', 'circle_arc', 'line']],
                layers_types=['in', 'out', 'in', 'out'])
            b = BlockObject(do_register=False)
            m = Matrix(
                matrix=[[-4, -3, -2, -1, 1, 2, 3, 4],
                        [-4, -3, -2, -1, 1, 2, 3, 4],
                        [0, 1, 2], lxy],
                items_curves=[
                    # 0 L1 Center
                    [['line'], ['line'], ['line'], ['line'],
                     ['line'], ['line'], ['line'], ['line'],
                     ['line'], ['line'], ['line'], ['line']],
                    # TODO Bug surface filling of all circle_arc with GEO factory
                    # [['circle_arc', [[0, 0, 0]]],
                    #  ['circle_arc', [[0, 0, 1]]],
                    #  ['circle_arc', [[0, 0, 1]]],
                    #  ['circle_arc', [[0, 0, 0]]],
                    #  ['circle_arc', [[0, 0, 0]]],
                    #  ['circle_arc', [[0, 0, 0]]],
                    #  ['circle_arc', [[0, 0, 1]]],
                    #  ['circle_arc', [[0, 0, 1]]],
                    #  ['line'], ['line'], ['line'], ['line']],
                    # 1 L2 X1
                    [['line'], ['line'], ['line'], ['line'],
                     ['circle_arc', [[0, 0, 0]]],
                     ['line'],
                     ['line'],
                     ['circle_arc', [[0, 0, 1]]],
                     ['line'], ['line'], ['line'], ['line']],
                    # 2 L2 X2
                    [['line'], ['line'], ['line'], ['line'],
                     ['circle_arc', [[0, 0, 1]]],
                     ['line'],
                     ['line'],
                     ['circle_arc', [[0, 0, 2]]],
                     ['line'], ['line'], ['line'], ['line']],
                    # 3 L2 Y1
                    [['circle_arc', [[0, 0, 0]]],
                     ['circle_arc', [[0, 0, 1]]],
                     ['line'],
                     ['line'],
                     ['line'], ['line'], ['line'], ['line'],
                     ['line'], ['line'], ['line'], ['line']],
                    # 4 L2 Y2
                    [['circle_arc', [[0, 0, 1]]],
                     ['circle_arc', [[0, 0, 2]]],
                     ['line'],
                     ['line'],
                     ['line'], ['line'], ['line'], ['line'],
                     ['line'], ['line'], ['line'], ['line']],
                    # 5 L2 NX1
                    [['line'], ['line'], ['line'], ['line'],
                     ['line'],
                     ['circle_arc', [[0, 0, 0]]],
                     ['circle_arc', [[0, 0, 1]]],
                     ['line'],
                     ['line'], ['line'], ['line'], ['line']],
                    # 6 L2 NX2
                    [['line'], ['line'], ['line'], ['line'],
                     ['line'],
                     ['circle_arc', [[0, 0, 1]]],
                     ['circle_arc', [[0, 0, 2]]],
                     ['line'],
                     ['line'], ['line'], ['line'], ['line']],
                    # 7 L2 NY1
                    [['line'],
                     ['line'],
                     ['circle_arc', [[0, 0, 1]]],
                     ['circle_arc', [[0, 0, 0]]],
                     ['line'], ['line'], ['line'], ['line'],
                     ['line'], ['line'], ['line'], ['line']],
                    # 8 L2 NY2
                    [['line'],
                     ['line'],
                     ['circle_arc', [[0, 0, 2]]],
                     ['circle_arc', [[0, 0, 1]]],
                     ['line'], ['line'], ['line'], ['line'],
                     ['line'], ['line'], ['line'], ['line']],
                    # 9 L3 X1
                    [['line'], ['line'], ['line'], ['line'],
                     ['circle_arc', [[0, 0, 0]]],
                     ['circle_arc', [[0, 0, 0]]],
                     ['circle_arc', [[0, 0, 1]]],
                     ['circle_arc', [[0, 0, 1]]],
                     ['line'], ['line'], ['line'], ['line']],
                    # 10 L3 X2
                    [['line'], ['line'], ['line'], ['line'],
                     ['circle_arc', [[0, 0, 1]]],
                     ['circle_arc', [[0, 0, 1]]],
                     ['circle_arc', [[0, 0, 2]]],
                     ['circle_arc', [[0, 0, 2]]],
                     ['line'], ['line'], ['line'], ['line']],
                    # 11 L3 Y1
                    [['circle_arc', [[0, 0, 0]]],
                     ['circle_arc', [[0, 0, 1]]],
                     ['circle_arc', [[0, 0, 1]]],
                     ['circle_arc', [[0, 0, 0]]],
                     ['line'], ['line'], ['line'], ['line'],
                     ['line'], ['line'], ['line'], ['line']],
                    # 12 L3 Y2
                    [['circle_arc', [[0, 0, 1]]],
                     ['circle_arc', [[0, 0, 2]]],
                     ['circle_arc', [[0, 0, 2]]],
                     ['circle_arc', [[0, 0, 1]]],
                     ['line'], ['line'], ['line'], ['line'],
                     ['line'], ['line'], ['line'], ['line']],
                    # 13 L3 NX1
                    [['line'], ['line'], ['line'], ['line'],
                     ['circle_arc', [[0, 0, 0]]],
                     ['circle_arc', [[0, 0, 0]]],
                     ['circle_arc', [[0, 0, 1]]],
                     ['circle_arc', [[0, 0, 1]]],
                     ['line'], ['line'], ['line'], ['line']],
                    # 14 L3 NX2
                    [['line'], ['line'], ['line'], ['line'],
                     ['circle_arc', [[0, 0, 1]]],
                     ['circle_arc', [[0, 0, 1]]],
                     ['circle_arc', [[0, 0, 2]]],
                     ['circle_arc', [[0, 0, 2]]],
                     ['line'], ['line'], ['line'], ['line']],
                    # 15 L3 NY1
                    [['circle_arc', [[0, 0, 0]]],
                     ['circle_arc', [[0, 0, 1]]],
                     ['circle_arc', [[0, 0, 1]]],
                     ['circle_arc', [[0, 0, 0]]],
                     ['line'], ['line'], ['line'], ['line'],
                     ['line'], ['line'], ['line'], ['line']],
                    # 16 L3 NY2
                    [['circle_arc', [[0, 0, 1]]],
                     ['circle_arc', [[0, 0, 2]]],
                     ['circle_arc', [[0, 0, 2]]],
                     ['circle_arc', [[0, 0, 1]]],
                     ['line'], ['line'], ['line'], ['line'],
                     ['line'], ['line'], ['line'], ['line']],
                    # 17 L4 X1
                    [['line'], ['line'], ['line'], ['line'],
                     ['line'],
                     ['circle_arc', [[0, 0, 0]]],
                     ['circle_arc', [[0, 0, 1]]],
                     ['line'],
                     ['line'], ['line'], ['line'], ['line']],
                    # 18 L4 X2
                    [['line'], ['line'], ['line'], ['line'],
                     ['line'],
                     ['circle_arc', [[0, 0, 1]]],
                     ['circle_arc', [[0, 0, 2]]],
                     ['line'],
                     ['line'], ['line'], ['line'], ['line']],
                    # 19 L4 Y1
                    [['line'],
                     ['line'],
                     ['circle_arc', [[0, 0, 1]]],
                     ['circle_arc', [[0, 0, 0]]],
                     ['line'], ['line'], ['line'], ['line'],
                     ['line'], ['line'], ['line'], ['line']],
                    # 20 L4 Y2
                    [['line'],
                     ['line'],
                     ['circle_arc', [[0, 0, 2]]],
                     ['circle_arc', [[0, 0, 1]]],
                     ['line'], ['line'], ['line'], ['line'],
                     ['line'], ['line'], ['line'], ['line']],
                    # 21 L4 NX1
                    [['line'], ['line'], ['line'], ['line'],
                     ['circle_arc', [[0, 0, 0]]],
                     ['line'],
                     ['line'],
                     ['circle_arc', [[0, 0, 1]]],
                     ['line'], ['line'], ['line'], ['line']],
                    # 22 L4 NX2
                    [['line'], ['line'], ['line'], ['line'],
                     ['circle_arc', [[0, 0, 1]]],
                     ['line'],
                     ['line'],
                     ['circle_arc', [[0, 0, 2]]],
                     ['line'], ['line'], ['line'], ['line']],
                    # 23 L4 NY1
                    [['circle_arc', [[0, 0, 0]]],
                     ['circle_arc', [[0, 0, 1]]],
                     ['line'],
                     ['line'],
                     ['line'], ['line'], ['line'], ['line'],
                     ['line'], ['line'], ['line'], ['line']],
                    # 24 L4 NY2
                    [['circle_arc', [[0, 0, 1]]],
                     ['circle_arc', [[0, 0, 2]]],
                     ['line'],
                     ['line'],
                     ['line'], ['line'], ['line'], ['line'],
                     ['line'], ['line'], ['line'], ['line']],
                ],
                items_curves_map=[
                    0,  0,  0, 23, 0, 0, 0,
                    0,  0,  0, 15, 0, 0, 0,
                    0,  0,  0, 7,  0, 0, 0,
                    21, 13, 5, 0,  1, 9, 17,
                    0,  0,  0, 3,  0, 0, 0,
                    0,  0,  0, 11, 0, 0, 0,
                    0,  0,  0, 19, 0, 0, 0,

                    0,  0,  0, 24, 0, 0,  0,
                    0,  0,  0, 16, 0, 0,  0,
                    0,  0,  0, 8,  0, 0,  0,
                    22, 14, 6, 0,  2, 10, 18,
                    0,  0,  0, 4,  0, 0,  0,
                    0,  0,  0, 12, 0, 0,  0,
                    0,  0,  0, 20, 0, 0,  0,
                ],
                transforms=['lxy2car'],
                items_do_register_map=[
                    0, 0, 0, 1, 0, 0, 0,
                    0, 0, 0, 1, 0, 0, 0,
                    0, 0, 0, 1, 0, 0, 0,
                    1, 1, 1, 1, 1, 1, 1,
                    0, 0, 0, 1, 0, 0, 0,
                    0, 0, 0, 1, 0, 0, 0,
                    0, 0, 0, 1, 0, 0, 0,

                    0, 0, 0, 1, 0, 0, 0,
                    0, 0, 0, 1, 0, 0, 0,
                    0, 0, 0, 1, 0, 0, 0,
                    1, 1, 1, 1, 1, 1, 1,
                    0, 0, 0, 1, 0, 0, 0,
                    0, 0, 0, 1, 0, 0, 0,
                    0, 0, 0, 1, 0, 0, 0,
                ],
                structure_type=['LLL', 'LRR', 'RLR', 'RRL'],
                items_structure_type_map=[
                    0, 0, 0, 2, 0, 0, 0,
                    0, 0, 0, 2, 0, 0, 0,
                    0, 0, 0, 2, 0, 0, 0,
                    1, 1, 1, 0, 0, 0, 0,
                    0, 0, 0, 0, 0, 0, 0,
                    0, 0, 0, 0, 0, 0, 0,
                    0, 0, 0, 0, 0, 0, 0,

                    0, 0, 0, 2, 0, 0, 0,
                    0, 0, 0, 2, 0, 0, 0,
                    0, 0, 0, 2, 0, 0, 0,
                    1, 1, 1, 0, 0, 0, 0,
                    0, 0, 0, 0, 0, 0, 0,
                    0, 0, 0, 0, 0, 0, 0,
                    0, 0, 0, 0, 0, 0, 0,
                ],
                structure_map=[[5, 0, 1], [5, 0, 1], [3, 0, 1]],
                parent=b,
                items_boolean_level_map=0,
                items_do_quadrate_map=0)
            b.add_child(m)
            b2 = BlockObject(parent=b,
                             zone='Cube',
                             points=4,
                             boolean_level=1,
                             transforms=[[0, 0, 0, 1, 0, 0, 45],
                                         [0, 0, 0, 0, 1, 0, 45]])
            b.add_child(b2)
            # Simple()(factory, model_name, m)
            Boolean(boolean_function=boolean_all)(factory, model_name, b)


if __name__ == '__main__':
    unittest.main()
