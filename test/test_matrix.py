import unittest
import logging
import time
from itertools import product

import numpy as np
import gmsh

from block import Block
from boolean import boolean, boolean_with_bounding_boxes
from matrix import Matrix
from coordinate_system import Path
from registry import reset as reset_registry
from zone import BlockDirection, BlockSimple

logging.basicConfig(level=logging.INFO)


class TestMatrix(unittest.TestCase):

    def test_init(self):
        for factory in ['geo', 'occ']:
            reset_registry()
            gmsh.initialize()
            model_name = f'test_matrix_init_{factory}'
            logging.info(model_name)
            gmsh.model.add(model_name)
            ms = []
            m1 = Matrix(factory=factory, points=[
                [1, 2],
                ['360:6'],
                ['360:6'],
                [10, 20, 30, 40],
                [1.5, 1.5, 0.75, 0.75],
                [1.5, 0.75, 1.5, 0.75],
                'tokamak',
                'trace'
            ], transforms=['tok2car', [0, 0, -50]])
            ms.append(m1)
            m2 = Matrix(factory=factory, points=[
                [1, 2],
                ['360:6'],
                ['360:6'],
                [10, 20, 30],
                [0.75],
                [1.5],
                'tokamak',
                'product'
            ], transforms=['tok2car', [0, 0, 50]])
            ms.append(m2)
            m3 = Matrix(factory=factory, points=[
                [1, 2],
                ['360:6'],
                [0, 1],
                'cyl',
            ], transforms=['cyl2car', [-50, 0, 0]])
            ms.append(m3)
            m4 = Matrix(factory=factory, points=[
                [1, 2],
                ['360:6'],
                ['360:6'],
                [10],
                'tor'
            ], transforms=['tor2car', [0, -50, 0]])
            ms.append(m4)
            m5 = Matrix(factory=factory, points=[
                [1, 2, 3],
                ['360:6'],
                ['increment', 10, '160:10'],
                'sph'
            ], transforms=['sph2car', [50, 0, 0]])
            ms.append(m5)
            curves = [['line', [[10, 0, x], [10, 0, x + 10], 'sph']]
                      for x in np.linspace(0, 80, 9)]
            orientations = [[[1, 180, x], 'sph'] for x in np.linspace(90, 0, 10)]
            p = Path(factory=factory, curves=curves, orientations=orientations)
            points = [
                ['1:3'],
                ['1:3'],
                # ['1:21:1.5:1.5'],
                ['1:5'],
                p
                # 'trace' by default
            ]
            m6 = Matrix(factory=factory, points=points, transforms=['pat2car'])
            ms.append(m6)
            for i, m in enumerate(ms):
                t0 = time.perf_counter()
                m.transform()
                logging.info(f'Transform_{i + 1} {time.perf_counter() - t0}')
                t0 = time.perf_counter()
                m.register()
                logging.info(f'Register_{i + 1} {time.perf_counter() - t0}')
            if factory == 'geo':
                for m in ms:
                    m.quadrate()
                    m.structure()
                gmsh.model.geo.synchronize()
            elif factory == 'occ':
                gmsh.model.occ.synchronize()
                for m in ms:
                    m.quadrate()
                    m.structure()
            else:
                raise ValueError(factory)
            gmsh.write(f'{model_name}.geo_unrolled')
            gmsh.finalize()

    def test_map(self):
        for factory in ['geo', 'occ']:
            reset_registry()
            gmsh.initialize()
            use_register_tag = False
            model_name = f'test_matrix_map_{factory}'
            logging.info(model_name)
            gmsh.model.add(model_name)
            points = [
                [1, 2, 3],  # r - inner radius (r < r2)
                ['180:5', '360:5'],  # phi - inner angle [0, 2*pi)
                ['180:5', '360:5'],  # theta - outer angle [0, 2*pi)
                [12, 24, 36, 48],  # r2 - outer radius
                [1.5, 1.5, 0.75, 0.75],  # kxy - inner radius XY scale coefficient in positive outer radius direction
                [1.5, 0.75, 1.5, 0.75],  # kz - inner radius Z scale coefficient
                'tokamak',
                'trace'
            ]
            do_register_map = [
                # param 1: [12, 1.5, 1.5]
                # Z1
                1, 1,  # Y1, X1, X2
                1, 1,  # Y2, X1, X2
                # Z2
                0, 0,  # Y1, X1, X2
                0, 0,  # Y2, X1, X2
                # param 2: [24, 1.5, 0.75]
                # Z1
                1, 1,  # Y1, X1, X2
                0, 0,  # Y2, X1, X2
                # Z2
                1, 1,  # Y1, X1, X2
                0, 0,  # Y2, X1, X2
                # param 3: [36, 0.75, 1.5]
                # Z1
                1, 0,  # Y1, X1, X2
                1, 0,  # Y2, X1, X2
                # Z2
                1, 0,  # Y1, X1, X2
                1, 0,  # Y2, X1, X2
                # param 4: [48, 0.75, 0.75]
                # Z1
                1, 1,  # Y1, X1, X2
                1, 1,  # Y2, X1, X2
                # Z2
                1, 1,  # Y1, X1, X2
                1, 1,  # Y2, X1, X2
            ]
            m_trace = Matrix(factory=factory, points=points,
                             use_register_tag=use_register_tag,
                             transforms=['tok2car'],
                             do_register_map=do_register_map)
            points = [
                [1, 2, 3],  # r - inner radius (r < r2)
                ['180:5', '360:5'],  # phi - inner angle [0, 2*pi)
                ['180:5', '360:5'],  # theta - outer angle [0, 2*pi)
                [60, 72, 84],  # r2 - outer radius
                [0.75],  # kxy - inner radius XY scale coefficient in positive outer radius direction
                [1.5],  # kz - inner radius Z scale coefficient
                'tokamak',
                'product'
            ]
            do_register_map = [
                # param 1: [60, 0.75, 1.5]
                # Z1
                1, 1,  # Y1, X1, X2
                1, 1,  # Y2, X1, X2
                # Z2
                0, 0,  # Y1, X1, X2
                0, 0,  # Y2, X1, X2
                # param 2: [72, 0.75, 1.5]
                # Z1
                1, 1,  # Y1, X1, X2
                0, 0,  # Y2, X1, X2
                # Z2
                1, 1,  # Y1, X1, X2
                0, 0,  # Y2, X1, X2
                # param 3: [84, 0.75, 1.5]
                # Z1
                1, 0,  # Y1, X1, X2
                1, 0,  # Y2, X1, X2
                # Z2
                1, 0,  # Y1, X1, X2
                1, 0,  # Y2, X1, X2
            ]
            m_product = Matrix(factory=factory, points=points,
                               use_register_tag=use_register_tag,
                               transforms=['tok2car'],
                               do_register_map=do_register_map)
            t0 = time.perf_counter()
            m_trace.transform()
            m_product.transform()
            print(f'Transform {time.perf_counter() - t0}')
            t0 = time.perf_counter()
            m_trace.register()
            m_product.register()
            print(f'Register {time.perf_counter() - t0}')
            t0 = time.perf_counter()
            if factory == 'geo':
                m_trace.quadrate()
                m_product.quadrate()
                m_trace.structure()
                m_product.structure()
                gmsh.model.geo.synchronize()
            elif factory == 'occ':
                gmsh.model.occ.synchronize()
                m_trace.quadrate()
                m_product.quadrate()
                m_trace.structure()
                m_product.structure()
            else:
                raise ValueError(factory)
            print(f'Synchronize {time.perf_counter() - t0}')
            gmsh.write(f'{model_name}.geo_unrolled')
            # gmsh.model.mesh.generate(3)
            # gmsh.write(f'{model_name}.msh2')
            gmsh.finalize()

    def test_boolean(self):
        # default 0
        # sds = {0: 'none', 1: 'all quadrangles', 2: 'all hexahedra', 3: 'barycentric'}
        sds = {2: 'all hexahedra'}
        # default 6
        # m2ds = {1: 'MeshAdapt', 2: 'Automatic', 3: 'Initial mesh only',
        #         5: 'Delaunay', 6: 'Frontal-Delaunay', 7: 'BAMG',
        #         8: 'Frontal-Delaunay for Quads', 9: 'Packing of Parallelograms'}
        m2ds = {5: 'Delaunay', 6: 'Frontal-Delaunay', 8: 'Frontal-Delaunay for Quads'}
        # m2ds = {6: 'Frontal-Delaunay', 8: 'Frontal-Delaunay for Quads'}
        # default 1
        # m3ds = {1: 'Delaunay', 3: 'Initial mesh only', 4: 'Frontal', 7: 'MMG3D',
        #         9: 'R-tree', 10: 'HXT'}
        m3ds = {1: 'Delaunay', 4: 'Frontal'}
        params = list(product(sds.items(), m2ds.items(), m3ds.items()))
        for i, p in enumerate(params):
            try:
                sd, m2d, m3d = p
                reset_registry()
                gmsh.initialize()
                gmsh.option.setNumber("General.Terminal", 0)
                gmsh.option.setNumber("Mesh.SubdivisionAlgorithm", sd[0])
                gmsh.option.setNumber("Mesh.Algorithm", m2d[0])
                gmsh.option.setNumber("Mesh.Algorithm3D", m3d[0])
                # default 1 1: longest or 2: shortest surface edge length
                gmsh.option.setNumber("Mesh.MeshSizeExtendFromBoundary", 2)
                # default 1
                gmsh.option.setNumber("Mesh.MeshSizeFactor", 1)
                # default 0
                gmsh.option.setNumber("Mesh.MeshSizeMin", 0)
                # default 1e+22
                gmsh.option.setNumber("Mesh.MeshSizeMax", 1e+0)
                # target number of elements per 2 * Pi radians, default 0
                gmsh.option.setNumber("Mesh.MeshSizeFromCurvature", 0)
                # default 0
                gmsh.option.setNumber("Mesh.MeshSizeFromCurvatureIsotropic", 0)
                # default 1
                gmsh.option.setNumber("Mesh.MeshSizeFromPoints", 1)
                # default 0
                gmsh.option.setNumber("Mesh.MeshSizeFromParametricPoints", 0)
                #
                factory = 'occ'
                model_name = f'test_matrix_boolean_{i+1}_{factory}_{sd[1]}_{m2d[1]}_{m3d[1]}'
                boolean_with_bboxes = True
                structure_all = None
                quadrate_all = None
                logging.info(model_name)
                gmsh.model.add(model_name)
                b = Block(factory=factory, points=[
                    [10, 5, 0], [0, 5, 0], [0, -5, 0], [10, -5, 0],
                    [10, 5, 10], [0, 5, 10], [0, -5, 10], [10, -5, 10]],
                          boolean_level=0,
                          structure_all=structure_all,
                          quadrate_all=quadrate_all,
                          zone_all='Block1')
                # b2 = Block(factory=factory, parent=b, points=[
                #     [5, 1, 5], [4, 1, 5], [4, -1, 5], [5, -1, 5],
                #     [5, 1, 6], [4, 1, 6], [4, -1, 6], [5, -1, 6], 0.5],
                #            boolean_level=1,
                #            quadrate_all=quadrate_all,
                #            zone_all='Block2')
                # b.add_child(b2)
                curves = [['line', [[10, 0, x], [10, 0, x + 10], 'sph']]
                          for x in np.linspace(0, 80, 9)]
                orientations = [[[1, 180, x], 'sph'] for x in np.linspace(90, 0, 10)]
                points = [
                    ['1:3'],
                    ['1:3'],
                    ['1:3'],
                    Path(factory=factory, curves=curves, orientations=orientations)
                    # 'trace' by default
                ]
                m = Matrix(factory=factory, points=points,
                           parent=b,
                           transforms=['pat2car'],
                           structure_all_map=structure_all,
                           quadrate_all_map=quadrate_all,
                           boolean_level_map=1,
                           zone_all_map='Tunnel1')
                b.add_child(m)
                m = Matrix(factory=factory, points=points,
                           parent=b,
                           transforms=['pat2car', [5, 0, 0, 0, 0, 1, 45]],
                           structure_all_map=None,
                           quadrate_all_map=None,
                           boolean_level_map=1,
                           zone_all_map='Tunnel2')
                b.add_child(m)
                t0 = time.perf_counter()
                b.transform()
                logging.info(f'transform {time.perf_counter() - t0}')
                t0 = time.perf_counter()
                b.register()
                logging.info(f'register {time.perf_counter() - t0}')
                if factory == 'geo':
                    gmsh.model.geo.synchronize()
                    t0 = time.perf_counter()
                    b.quadrate()
                    logging.info(f'quadrate: {time.perf_counter() - t0}')
                    t0 = time.perf_counter()
                    b.structure()
                    logging.info(f'structure: {time.perf_counter() - t0}')
                elif factory == 'occ':
                    if boolean_with_bboxes:
                        t0 = time.perf_counter()
                        gmsh.model.occ.synchronize()  # for evaluation of bboxes
                        logging.info(f'synchronize: {time.perf_counter() - t0}')
                        t0 = time.perf_counter()
                        boolean_with_bounding_boxes(b)
                        logging.info(f'boolean_with_bounding_boxes: {time.perf_counter() - t0}')
                        # INFO:root:synchronize: 0.03
                        # INFO: root:boolean_with_bounding_boxes: 2121
                        # INFO:root:remove_all_duplicates: 409
                    else:
                        t0 = time.perf_counter()
                        boolean(b)
                        logging.info(f'boolean: {time.perf_counter() - t0}')
                        # INFO:root:boolean: 2394
                        # INFO:root:remove_all_duplicates: 409
                    try:
                        t0 = time.perf_counter()
                        gmsh.model.occ.remove_all_duplicates()
                        logging.info(f'remove_all_duplicates: {time.perf_counter() - t0}')
                    except Exception as e:
                        logging.warning(e)
                    t0 = time.perf_counter()
                    b.unregister()
                    logging.info(f'unregister: {time.perf_counter() - t0}')
                    t0 = time.perf_counter()
                    b.unregister_boolean()
                    logging.info(f'unregister_boolean: {time.perf_counter() - t0}')
                    t0 = time.perf_counter()
                    gmsh.model.occ.synchronize()
                    logging.info(f'synchronize: {time.perf_counter() - t0}')
                    t0 = time.perf_counter()
                    b.quadrate()
                    logging.info(f'quadrate: {time.perf_counter() - t0}')
                    t0 = time.perf_counter()
                    b.structure()
                    logging.info(f'structure: {time.perf_counter() - t0}')
                else:
                    raise ValueError(factory)
                t0 = time.perf_counter()
                # BlockSimple()(b)
                BlockDirection(dims=(2, 3), make_interface=False,
                               add_volume_tag=True, add_volume_zone=True,
                               add_surface_loop_tag=True,
                               add_in_out_boundary=False)(b)
                logging.info(f'zones: {time.perf_counter() - t0}')
                t0 = time.perf_counter()
                gmsh.model.mesh.generate(3)
                logging.info(f'mesh: {time.perf_counter() - t0}')
                t0 = time.perf_counter()
                gmsh.write(f'{model_name}.msh2')
                # gmsh.write(f'{model_name}.geo_unrolled')
                logging.info(f'write: {time.perf_counter() - t0}')
            except Exception as e:
                logging.warning(e)
            finally:
                gmsh.finalize()


if __name__ == '__main__':
    unittest.main()
