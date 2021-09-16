from support import affine, rotation
import unittest
import numpy as np
from itertools import product

import gmsh

from registry import reset as reset_registry
from block import Block


class TestBlock(unittest.TestCase):

    def test_init(self):
        kwargs = {
            'factory': ['geo', 'occ'],
            'register_tag': [True, False],
            'output_format': ['msh2', 'geo_unrolled'
                              # 'vtk', 'stl',
                              # 'brep', 'step'
                              ]
            # auto, msh1, msh2, msh22, msh3, msh4, msh40, msh41, msh, unv,
            # vtk, wrl, mail, stl, p3d, mesh, bdf, cgns, med, diff, ir3, inp,
            # ply2, celum, su2, x3d, dat, neu, m, key
        }
        not_allowed = [{'factory': 'geo',
                        'output_format': 'brep'},
                       {'factory': 'geo',
                        'output_format': 'step'}]
        cs = product(*kwargs.values())
        for c in cs:
            args = dict(zip(kwargs, c))
            print(args)
            is_na = False
            for na in not_allowed:
                is_na = all([args[k] == na[k] for k in na])
                if is_na:
                    break
            if is_na:
                continue
            name_suffix = '-'.join(f'{k}_{v}' for k, v in args.items())
            model_name = f'test_init-{name_suffix}'
            reset_registry()
            gmsh.initialize()
            gmsh.model.add(model_name)
            b = Block(factory=args['factory'],
                      register_tag=args['register_tag'],
                      points=[
                          # P0
                          {'coordinates': [0.5, 0.5, -0.5],
                           'coordinate_system': {'name': 'cartesian', 'origin': [0, 0, 0]},
                           'kwargs': {'meshSize': 0.1}
                           },
                          # P1
                          {'coordinates': [-0.5, 0.5, -0.5],
                           'coordinate_system': {'name': 'cartesian', 'origin': [0, 0, 0]},
                           'kwargs': {'meshSize': 0.1}
                           },
                          # P2
                          {'coordinates': [-0.5, -0.5, -0.5],
                           'coordinate_system': {'name': 'cartesian', 'origin': [0, 0, 0]},
                           'kwargs': {'meshSize': 0.1}
                           },
                          # P3
                          {'coordinates': [0.5, -0.5, -0.5],
                           'coordinate_system': {'name': 'cartesian', 'origin': [0, 0, 0]},
                           'kwargs': {'meshSize': 0.1}
                           },
                          # P4
                          {'coordinates': [0.5, 0.5, 0.5],
                           'coordinate_system': {'name': 'cartesian', 'origin': [0, 0, 0]},
                           'kwargs': {'meshSize': 0.1}
                           },
                          # P5
                          {'coordinates': [-0.5, 0.5, 0.5],
                           'coordinate_system': {'name': 'cartesian', 'origin': [0, 0, 0]},
                           'kwargs': {'meshSize': 0.1}
                           },
                          # P6
                          {'coordinates': [-0.5, -0.5, 0.5],
                           'coordinate_system': {'name': 'cartesian', 'origin': [0, 0, 0]},
                           'kwargs': {'meshSize': 0.1}
                           },
                          # P7
                          {'coordinates': [0.5, -0.75, 0.5],  # For ellipse arc
                           'coordinate_system': {'name': 'cartesian', 'origin': [0, 0, 0]},
                           'kwargs': {'meshSize': 0.1}
                           },
                      ],
                      curves=[
                          # X1
                          {'name': 'line'},
                          # X2
                          {'name': 'circle_arc',
                           'points': [
                               {'coordinates': [0., 0., 0.],
                                'coordinate_system': 'cartesian',
                                'kwargs': {'meshSize': 0.0}}]
                           },
                          # X3
                          {'name': 'ellipse_arc',  # X2
                           'points': [
                               {'coordinates': [0.5, -0.5, 0.5],
                                'coordinate_system': 'cartesian',
                                'kwargs': {'meshSize': 0.0}},
                               {'coordinates': [0.25, -0.5, 0.5],
                                'coordinate_system': 'cartesian',
                                'kwargs': {'meshSize': 0.0}}
                           ]
                           },
                          # X4
                          {'name': 'line'},
                          # Y1
                          {'name': 'line'},
                          # Y2
                          {'name': 'spline',
                           'points': [
                               {'coordinates': [-0.4, -0.25, -0.5],
                                'coordinate_system': 'cartesian',
                                'kwargs': {'meshSize': 0.0}},
                               {'coordinates': [-0.5, 0., -0.5],
                                'coordinate_system': 'cartesian',
                                'kwargs': {'meshSize': 0.0}},
                               {'coordinates': [-0.6, 0.25, -0.5],
                                'coordinate_system': 'cartesian',
                                'kwargs': {'meshSize': 0.0}}
                           ]
                           },
                          # Y3
                          {'name': 'bspline',
                           'points': [
                               {'coordinates': [-0.4, -0.25, 0.5],
                                'coordinate_system': 'cartesian',
                                'kwargs': {'meshSize': 0.0}},
                               {'coordinates': [-0.5, 0., 0.5],
                                'coordinate_system': 'cartesian',
                                'kwargs': {'meshSize': 0.0}},
                               {'coordinates': [-0.6, 0.25, 0.5],
                                'coordinate_system': 'cartesian',
                                'kwargs': {'meshSize': 0.0}}
                           ],
                           'kwargs': {'degree': 3,
                                      'weights': [],
                                      'knots': [],
                                      'multiplicities': []
                                      }
                           },
                          # Y4
                          {'name': 'line'},
                          # Z1
                          {'name': 'line'},
                          # Z2
                          {'name': 'bezier',
                           'points': [
                               {'coordinates': [-0.4, 0.5, -0.25],
                                'coordinate_system': 'cartesian',
                                'kwargs': {'meshSize': 0.}},
                               {'coordinates': [-0.5, 0.5, 0.],
                                'coordinate_system': 'cartesian',
                                'kwargs': {'meshSize': 0.}},
                               {'coordinates': [-0.6, 0.5, 0.25],
                                'coordinate_system': 'cartesian',
                                'kwargs': {'meshSize': 0.}}
                           ]
                           },
                          # Z3
                          {'name': 'polyline',
                           'points': [
                               {'coordinates': [-0.4, -0.5, -0.25],
                                'coordinate_system': 'cartesian',
                                'kwargs': {'meshSize': 0.01}},
                               {'coordinates': [-0.5, -0.5, 0.],
                                'coordinate_system': 'cartesian',
                                'kwargs': {'meshSize': 0.01}},
                               {'coordinates': [-0.6, -0.5, 0.25],
                                'coordinate_system': 'cartesian',
                                'kwargs': {'meshSize': 0.01}}
                           ]
                           },
                          # Z4
                          {'name': 'line'}
                      ],
                      transformations=[
                          {
                              'name': 'translation',
                              'vector': [0, 0, 0],
                              'coordinate_system': {'type': 'cartesian', 'origin': [0, 0, 0]}
                          },
                          {
                              'name': 'rotation',
                              'origin': [0, 0, 0],
                              'direction': [0, 0, 1],
                              'angle': np.pi / 3,
                              'coordinate_system': {'type': 'cartesian', 'origin': [0, 0, 0]},
                          },
                          # dilation (enlargement or reduction)
                          # reflection
                          {
                              'name': 'conversion',
                              'coordinate_system': {'type': 'cartesian', 'origin': [0, 0, 4]},
                          },
                      ]
                      )
            if args['factory'] == 'geo':
                gmsh.model.geo.synchronize()
            else:
                gmsh.model.occ.synchronize()
            gmsh.model.mesh.generate(3)
            gmsh.write(f'{model_name}.{args["output_format"]}')
            gmsh.finalize()


if __name__ == '__main__':
    unittest.main()
