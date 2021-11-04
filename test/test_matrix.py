import unittest
import logging
import time

import numpy as np
import gmsh

from matrix import Matrix
from coordinate_system import Path
from registry import reset as reset_factory

logging.basicConfig(level=logging.INFO)


class TestMatrix(unittest.TestCase):

    def test_init(self):
        gmsh.initialize()
        factory = 'geo'
        model_name = 'test_matrix_init'
        gmsh.model.add(model_name)
        reset_factory()
        ms = []
        m1 = Matrix(factory=factory, points=[
            [1, 2],
            ['360:10'],
            ['360:10'],
            [10, 20, 30, 40],
            [1.5, 1.5, 0.75, 0.75],
            [1.5, 0.75, 1.5, 0.75],
            'tokamak',
            'trace'
        ], transforms=['tok2car', [0, 0, -50]])
        ms.append(m1)
        m2 = Matrix(factory=factory, points=[
            [1, 2],
            ['360:10'],
            ['360:10'],
            [10, 20, 30],
            [0.75],
            [1.5],
            'tokamak',
            'product'
        ], transforms=['tok2car', [0, 0, 50]])
        ms.append(m2)
        m3 = Matrix(factory=factory, points=[
            [1, 2],
            ['360:10'],
            [0, 1],
            'cyl'
        ], transforms=['cyl2car', [-50, 0, 0]])
        ms.append(m3)
        m4 = Matrix(factory=factory, points=[
            [1, 2],
            ['360:10'],
            ['360:10'],
            [10],
            'tor'
        ], transforms=['tor2car', [0, -50, 0]])
        ms.append(m4)
        m5 = Matrix(factory=factory, points=[
            [1, 2, 3],
            ['360:10'],
            ['increment', 10, '160:10'],
            'sph'
        ], transforms=['sph2car', [50, 0, 0]])
        ms.append(m5)
        curves = [['line', [[10, 0, x], [10, 0, x + 10], 'sph']]
                  for x in np.linspace(0, 80, 9)]
        orientations = [[[1, 180, x], 'sph'] for x in np.linspace(90, 0, 10)]
        points = [
            [-1, '1:4'],
            [-1, '1:4'],
            # ['1:21:1.5:1.5'],
            ['1:21'],
            Path(curves=curves, orientations=orientations)
            # 'trace' by default
        ]
        m = Matrix(factory=factory, points=points,
                   transforms=['pat2car'])
        ms.append(m)
        for m in ms:
            m.transform()
            m.register()
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
        gmsh.initialize()
        factory = 'geo'
        use_register_tag = False
        model_name = 'test_matrix_map'
        gmsh.model.add(model_name)
        reset_factory()
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


if __name__ == '__main__':
    unittest.main()
