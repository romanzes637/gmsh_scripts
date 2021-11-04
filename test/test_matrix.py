import unittest
import logging

import numpy as np
import gmsh

from matrix import Matrix
from coordinate_system import Path

logging.basicConfig(level=logging.INFO)


class TestMatrix(unittest.TestCase):

    def test_init(self):

        gmsh.initialize()
        factory = 'geo'
        model_name = 'test_matrix_init'
        gmsh.model.add(model_name)
        # [r, phi, theta, r2, kxy, kz] -> [x, y, z]
        # r - inner radius (r < r2)
        # phi - inner angle [0, 2*pi)
        # theta - outer angle [0, 2*pi)
        # r2 - outer radius
        # kxy - inner radius XY scale coefficient in positive outer radius direction
        # kz - inner radius Z scale coefficient
        # type, start, values or increments
        # points = [
        #     [1, 2],
        #     ['360:10'],
        #     ['360:10'],
        #     [10, 20, 30, 40],
        #     [1.5, 1.5, 0.75, 0.75],
        #     [1.5, 0.75, 1.5, 0.75],
        #     'tokamak',
        #     'trace'
        # ]
        # points = [
        #     [1, 2],
        #     ['360:10'],
        #     ['360:10'],
        #     [10, 20, 30],
        #     [0.75],
        #     [1.5],
        #     'tokamak',
        #     'product'
        # ]
        # m = Matrix(factory=factory, points=points, transforms=['tok2car'])
        # points = [
        #     [1, 2],
        #     ['360:10'],
        #     [0, 1],
        #     'cyl'
        # ]
        # m = Matrix(factory=factory, points=points, transforms=['cyl2car'])
        # points = [
        #     [1, 2],
        #     ['360:10'],
        #     ['360:10'],
        #     [10],
        #     'tor'
        # ]
        # m = Matrix(factory=factory, points=points, transforms=['tor2car'])
        # points = [
        #     [1, 2, 3],
        #     ['360:10'],
        #     ['increment', 10, '160:10'],
        #     'sph'
        # ]
        # m = Matrix(factory=factory, points=points, transforms=['sph2car'])
        # points = [
        #     [1, '2:2', 3, '4:10:0.8:0.8'],  # 'direct' by default
        #     ['increment', '1:4', 0.5],  # 0 by default
        #     ['1:10:1.3:1.3']  # 'direct', 0 by default
        #     # 'cartesian' by default
        #     # 'trace' by default
        # ]
        # m = Matrix(factory=factory, points=points)
        # points = [
        #     [-1, '1:4'],
        #     [-1, '1:4'],
        #     ['1:2'],
        #     Path(curves=[
        #         ['line', [[0, 0, 0], [1, 0, 0]]],
        #         # ['line', [[6, 0, 1], [9, 0, 3]]],
        #         # ['line', [[9, 0, 3], [12, 0, 6]]],
        #         # ['line', [[12, 0, 6], [15, 0, 10]]],
        #     ], orientations=[
        #         [[0, -1, 0], [0, 0, -1], [1, 0, 0]],
        #         [[0, -1, 0], [1, 0, -1], [1, 0, 1]],
        #         # [[0, -1, 0], [1, 0, -1], [1, 0, 1]],
        #         # [[0, -1, 0], [1, 0, -1], [1, 0, 1]],
        #         # [[0, -1, 0], [1, 0, -1], [1, 0, 1]],
        #     ]
        #     )
        #     # 'trace' by default
        # ]
        # points = [
        #     [-1, '1:4'],
        #     [-1, '1:4'],
        #     ['1:11'],
        #     Path(curves=[
        #         ['line', [[0, 0, 0], [3, 0, 0]]],
        #         ['line', [[3, 0, 0], [6, 0, 3]]],
        #         ['line', [[6, 0, 3], [6, 0, 6]]],
        #         # ['line', [[6, 0, 1], [9, 0, 3]]],
        #         # ['line', [[9, 0, 3], [12, 0, 6]]],
        #         # ['line', [[12, 0, 6], [15, 0, 10]]],
        #     ], orientations=[
        #         [[0, -1, 0], [0, 0, -1], [1, 0, 0]],
        #         [[0, -1, 0], [1, 0, -1], [1, 0, 1]],
        #         [[0, -1, 0], [1, 0, -1], [1, 0, 1]],
        #         [[0, -1, 0], [1, 0, 0], [0, 0, 1]],
        #         # [[0, -1, 0], [1, 0, -1], [1, 0, 1]],
        #         # [[0, -1, 0], [1, 0, -1], [1, 0, 1]],
        #         # [[0, -1, 0], [1, 0, -1], [1, 0, 1]],
        #     ]
        #     )
        #     # 'trace' by default
        # ]
        curves = [['line', [[10, 0, x], [10, 0, x+10], 'sph']]
                  for x in np.linspace(0, 80, 9)]
        orientations = [[[1, 180, x], 'sph'] for x in np.linspace(90, 0, 10)]
        print(curves)
        print(orientations)
        points = [
            [-1, '1:4'],
            [-1, '1:4'],
            ['1:21:1.5:1.5'],
            Path(curves=curves, orientations=orientations)
            # 'trace' by default
        ]
        m = Matrix(factory=factory, points=points, transforms=['pat2car'])
        m.transform()
        m.register()
        if factory == 'geo':
            gmsh.model.geo.synchronize()
        elif factory == 'occ':
            gmsh.model.occ.synchronize()
        else:
            raise ValueError(factory)
        gmsh.write(f'{model_name}.geo_unrolled')
        gmsh.finalize()


if __name__ == '__main__':
    unittest.main()
