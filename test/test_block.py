import unittest
import numpy as np
from itertools import product
import logging
import time
import logging

import gmsh

from registry import reset as reset_registry
from boolean import boolean, boolean_with_bounding_boxes
from block import Block
from zone import Block as BlockRule, BlockSimple

logging.basicConfig(level=logging.INFO)


def gmsh_decorator(f):
    def wrapper(*args, **kwargs):
        gmsh.initialize()
        # gmsh.option.setNumber('Geometry.AutoCoherence', 0)  # No effect at occ
        gmsh.option.setNumber('Mesh.Optimize', 0)  # resolving further
        gmsh.option.setNumber("General.Terminal", 0)
        out = f(*args, **kwargs)
        gmsh.finalize()
        return out

    return wrapper


def make_kwargs_combinations(kwargs, filter_kwargs):
    values_combs = product(*kwargs.values())
    kwargs_combs = [dict(zip(kwargs.keys(), x)) for x in values_combs]
    flt_kwargs_combs = []
    for cmb_kws in kwargs_combs:
        in_filter = False
        for flt_kws in filter_kwargs:
            in_filter = all([cmb_kws[k] == flt_kws[k] for k in flt_kws])
            if in_filter:
                break
        if not in_filter:
            flt_kwargs_combs.append(cmb_kws)
    return flt_kwargs_combs


class TestBlock(unittest.TestCase):

    @gmsh_decorator
    def test_init(self):
        kwargs = {
            'factory': ['geo', 'occ'],
            # 'factory': ['geo'],
            # 'register_tag': [True, False],
            'register_tag': [True, False],
            # 'recombine_angle': [45.],
            'transfinite_curve_mesh_type': ['Progression', 'Bump', 'Beta'],
            'transfinite_curve_coef': [0.75, 1.0, 1.5],
            'output_format': ['msh2', 'geo_unrolled'
                              # 'vtk', 'stl',
                              # 'brep', 'step'
                              ]
            # auto, msh1, msh2, msh22, msh3, msh4, msh40, msh41, msh, unv,
            # vtk, wrl, mail, stl, p3d, mesh, bdf, cgns, med, diff, ir3, inp,
            # ply2, celum, su2, x3d, dat, neu, m, key
        }
        filter_kwargs = [{'factory': 'geo',
                          'output_format': 'brep'},
                         {'factory': 'geo',
                          'output_format': 'step'}]
        kwargs_combs = make_kwargs_combinations(kwargs, filter_kwargs)
        for kws in kwargs_combs:
            name_suffix = '-'.join(f'{k}_{v}' for k, v in kws.items())
            model_name = f'test_init-{name_suffix}'
            logging.info(model_name)
            reset_registry()
            gmsh.model.add(model_name)
            # B1
            b = Block(
                factory=kws['factory'],
                use_register_tag=kws['register_tag'],
                points=[
                    # P0
                    {'coordinates': [0.5, 0.5, -0.5],
                     'coordinate_system': {'name': 'cartesian',
                                           'origin': [0, 0, 0]},
                     'kwargs': {'meshSize': 0.}
                     },
                    # P1
                    {'coordinates': [-0.5, 0.5, -0.5],
                     'coordinate_system': {'name': 'cartesian',
                                           'origin': [0, 0, 0]},
                     'kwargs': {'meshSize': 0.1}
                     },
                    # P2
                    {'coordinates': [-0.5, -0.5, -0.5],
                     'coordinate_system': {'name': 'cartesian',
                                           'origin': [0, 0, 0]},
                     'kwargs': {'meshSize': 0.1}
                     },
                    # P3
                    {'coordinates': [0.5, -0.5, -0.5],
                     'coordinate_system': {'name': 'cartesian',
                                           'origin': [0, 0, 0]},
                     'kwargs': {'meshSize': 0.1}
                     },
                    # P4
                    {'coordinates': [0.5, 0.5, 0.5],
                     'coordinate_system': {'name': 'cartesian',
                                           'origin': [0, 0, 0]},
                     'kwargs': {'meshSize': 0.1}
                     },
                    # P5
                    {'coordinates': [-0.5, 0.5, 0.5],
                     'coordinate_system': {'name': 'cartesian',
                                           'origin': [0, 0, 0]},
                     'kwargs': {'meshSize': 0.1}
                     },
                    # P6
                    {'coordinates': [-0.5, -0.5, 0.5],
                     'coordinate_system': {'name': 'cartesian',
                                           'origin': [0, 0, 0]},
                     'kwargs': {'meshSize': 0.1}
                     },
                    # P7
                    {'coordinates': [0.5, -0.75, 0.5],  # For ellipse arc
                     'coordinate_system': {'name': 'cartesian',
                                           'origin': [0, 0, 0]},
                     'kwargs': {'meshSize': 0.}
                     },
                ],
                curves=[
                    # X1
                    {'name': 'line',
                     'transfinite': {
                         'nPoints': 15,
                         'kwargs': {
                             'meshType': kws.get('transfinite_curve_mesh_type',
                                                 'Progression'),
                             'coef': kws.get('transfinite_curve_coef', 1.),
                         }}
                     },
                    # X2
                    {'name': 'circle_arc',
                     'points': [
                         {'coordinates': [0., 0., 0.],
                          'coordinate_system': 'cartesian',
                          'kwargs': {'meshSize': 0.0}}],
                     'transfinite': {
                         'nPoints': 15,
                         'kwargs': {
                             'meshType': kws.get('transfinite_curve_mesh_type',
                                                 'Progression'),
                             'coef': kws.get('transfinite_curve_coef',
                                             1.)
                         }}
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
                     ],
                     'transfinite': {
                         'nPoints': 15,
                         'kwargs': {
                             'meshType': kws.get(
                                 'transfinite_curve_mesh_type',
                                 'Progression'),
                             'coef': kws.get('transfinite_curve_coef',
                                             1.)
                         }}
                     },
                    # X4
                    {'name': 'line',
                     'transfinite': {
                         'nPoints': 15,
                         'kwargs': {
                             'meshType': kws.get(
                                 'transfinite_curve_mesh_type',
                                 'Progression'),
                             'coef': kws.get('transfinite_curve_coef',
                                             1.)
                         }}
                     },
                    # Y1
                    {'name': 'line',
                     'transfinite': {
                         'nPoints': 15,
                         'kwargs': {
                             'meshType': kws.get('transfinite_curve_mesh_type',
                                                 'Progression'),
                             'coef': kws.get('transfinite_curve_coef', 1.)
                         }}
                     },
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
                     ],
                     'transfinite': {
                         'nPoints': 15,
                         'kwargs': {
                             'meshType': kws.get(
                                 'transfinite_curve_mesh_type',
                                 'Progression'),
                             'coef': kws.get('transfinite_curve_coef',
                                             1.)
                         }}
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
                                },
                     'transfinite': {
                         'nPoints': 15,
                         'kwargs': {
                             'meshType': kws.get(
                                 'transfinite_curve_mesh_type',
                                 'Progression'),
                             'coef': kws.get('transfinite_curve_coef',
                                             1.)
                         }}
                     },
                    # Y4
                    {'name': 'line',
                     'transfinite': {
                         'nPoints': 15,
                         'kwargs': {
                             'meshType': kws.get(
                                 'transfinite_curve_mesh_type',
                                 'Progression'),
                             'coef': kws.get('transfinite_curve_coef',
                                             1.)
                         }}
                     },
                    # Z1
                    {'name': 'line',
                     'transfinite': {
                         'nPoints': 15,
                         'kwargs': {
                             'meshType': kws.get(
                                 'transfinite_curve_mesh_type',
                                 'Progression'),
                             'coef': kws.get('transfinite_curve_coef',
                                             1.)
                         }}
                     },
                    # Z2
                    {'name': 'bezier',
                     'points': [
                         {'coordinates': [-0.4, 0.5, -0.25],
                          'coordinate_system': 'cartesian',
                          'kwargs': {'meshSize': 0.01}},
                         {'coordinates': [-0.5, 0.5, 0.],
                          'coordinate_system': 'cartesian',
                          'kwargs': {'meshSize': 0.01}},
                         {'coordinates': [-0.6, 0.5, 0.25],
                          'coordinate_system': 'cartesian',
                          'kwargs': {'meshSize': 0.01}}
                     ],
                     'transfinite': {
                         'nPoints': 15,
                         'kwargs': {
                             'meshType': kws.get(
                                 'transfinite_curve_mesh_type',
                                 'Progression'),
                             'coef': kws.get('transfinite_curve_coef',
                                             1.)
                         }}
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
                     ],
                     'transfinite': {
                         'nPoints': 15,
                         'kwargs': {
                             'meshType': kws.get(
                                 'transfinite_curve_mesh_type',
                                 'Progression'),
                             'coef': kws.get('transfinite_curve_coef',
                                             1.)
                         }}
                     },
                    # Z4
                    {'name': 'line',
                     'transfinite': {
                         'nPoints': 15,
                         'kwargs': {
                             'meshType': kws.get(
                                 'transfinite_curve_mesh_type',
                                 'Progression'),
                             'coef': kws.get('transfinite_curve_coef',
                                             1.)
                         }}
                     }
                ],
                surfaces=[
                    # NX
                    {'recombine': {}, 'transfinite': {}},
                    # X
                    {'recombine': {}, 'transfinite': {}},
                    # NY
                    {'recombine': {}, 'transfinite': {}},
                    # Y
                    {'recombine': {}, 'transfinite': {}},
                    # NZ
                    {'recombine': {}, 'transfinite': {}},
                    # Z
                    {'recombine': {'kwargs': {
                        'angle': kws.get('recombine_angle', 45.)}},
                        'transfinite': {}
                    },
                ],
                volumes=[
                    {'transfinite': {}}
                ]
            )
            # B2
            b2 = Block(
                factory=kws['factory'],
                use_register_tag=kws['register_tag'],
                points=[
                    # P0
                    {'coordinates': [-0.5, 0.5, -0.5],
                     'coordinate_system': {'name': 'cartesian',
                                           'origin': [0, 0, 0]},
                     'kwargs': {'meshSize': 0.}
                     },
                    # P1
                    {'coordinates': [-1.5, 0.5, -0.5],
                     'coordinate_system': {'name': 'cartesian',
                                           'origin': [0, 0, 0]},
                     'kwargs': {'meshSize': 0.1}
                     },
                    # P2
                    {'coordinates': [-1.5, -0.5, -0.5],
                     'coordinate_system': {'name': 'cartesian',
                                           'origin': [0, 0, 0]},
                     'kwargs': {'meshSize': 0.1}
                     },
                    # P3
                    {'coordinates': [-0.5, -0.5, -0.5],
                     'coordinate_system': {'name': 'cartesian',
                                           'origin': [0, 0, 0]},
                     'kwargs': {'meshSize': 0.1}
                     },
                    # P4
                    {'coordinates': [-0.5, 0.5, 0.5],
                     'coordinate_system': {'name': 'cartesian',
                                           'origin': [0, 0, 0]},
                     'kwargs': {'meshSize': 0.1}
                     },
                    # P5
                    {'coordinates': [-1.5, 0.5, 0.5],
                     'coordinate_system': {'name': 'cartesian',
                                           'origin': [0, 0, 0]},
                     'kwargs': {'meshSize': 0.1}
                     },
                    # P6
                    {'coordinates': [-1.5, -0.5, 0.5],
                     'coordinate_system': {'name': 'cartesian',
                                           'origin': [0, 0, 0]},
                     'kwargs': {'meshSize': 0.1}
                     },
                    # P7
                    {'coordinates': [-0.5, -0.5, 0.5],  # For ellipse arc
                     'coordinate_system': {'name': 'cartesian',
                                           'origin': [0, 0, 0]},
                     'kwargs': {'meshSize': 0.}
                     },
                ],
                curves=[
                    # X1
                    {'name': 'line'},
                    # X2
                    {'name': 'line',
                     'points': [
                         {'coordinates': [-0.75, 0., 0.],
                          'coordinate_system': 'cartesian',
                          'kwargs': {'meshSize': 0.0}}]
                     },
                    # X3
                    {'name': 'line',  # X2
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
                    # Y1
                    {'name': 'line'},
                    # Y2
                    {'name': 'line'},
                    # Y4
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
                    # Z1
                    {'name': 'bezier',
                     'points': [
                         {'coordinates': [-0.4, 0.5, -0.25],
                          'coordinate_system': 'cartesian',
                          'kwargs': {'meshSize': 0.01}},
                         {'coordinates': [-0.5, 0.5, 0.],
                          'coordinate_system': 'cartesian',
                          'kwargs': {'meshSize': 0.01}},
                         {'coordinates': [-0.6, 0.5, 0.25],
                          'coordinate_system': 'cartesian',
                          'kwargs': {'meshSize': 0.01}}
                     ]
                     },
                    # Z3
                    {'name': 'line'},
                    # Z4
                    {'name': 'line'},
                    # Z4
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
                ],
                quadrate_all=True,
                #   transfinite_all={
                #     'curves': {
                #       'nPoints': 15,
                #       'kwargs': {
                #         'meshType': args.get(
                #           'transfinite_curve_mesh_type',
                #           'Progression'),
                #         'coef': args.get('transfinite_curve_coef', 1.)
                #       }}}
                # ),
                structure_all={
                    'curves_x': {
                        'nPoints': 10,
                        'kwargs': {
                            'meshType': kws.get(
                                'transfinite_curve_mesh_type',
                                'Progression'),
                            'coef': kws.get('transfinite_curve_coef', 1.)
                        }},
                    'curves_y': {
                        'nPoints': 15,
                        'kwargs': {
                            'meshType': kws.get(
                                'transfinite_curve_mesh_type',
                                'Progression'),
                            'coef': kws.get('transfinite_curve_coef', 1.)
                        }},
                    'curves_z': {
                        'nPoints': 15,
                        'kwargs': {
                            'meshType': kws.get(
                                'transfinite_curve_mesh_type',
                                'Progression'),
                            'coef': kws.get('transfinite_curve_coef', 1.)
                        }}
                },
            )
            # B3 (B1 duplicate)
            b3 = Block(
                factory=kws['factory'],
                use_register_tag=kws['register_tag'],
                points=[
                    # P0
                    {'coordinates': [0.5, 0.5, -0.5],
                     'coordinate_system': {'name': 'cartesian',
                                           'origin': [0, 0, 0]},
                     'kwargs': {'meshSize': 0.}
                     },
                    # P1
                    {'coordinates': [-0.5, 0.5, -0.5],
                     'coordinate_system': {'name': 'cartesian',
                                           'origin': [0, 0, 0]},
                     'kwargs': {'meshSize': 0.1}
                     },
                    # P2
                    {'coordinates': [-0.5, -0.5, -0.5],
                     'coordinate_system': {'name': 'cartesian',
                                           'origin': [0, 0, 0]},
                     'kwargs': {'meshSize': 0.1}
                     },
                    # P3
                    {'coordinates': [0.5, -0.5, -0.5],
                     'coordinate_system': {'name': 'cartesian',
                                           'origin': [0, 0, 0]},
                     'kwargs': {'meshSize': 0.1}
                     },
                    # P4
                    {'coordinates': [0.5, 0.5, 0.5],
                     'coordinate_system': {'name': 'cartesian',
                                           'origin': [0, 0, 0]},
                     'kwargs': {'meshSize': 0.1}
                     },
                    # P5
                    {'coordinates': [-0.5, 0.5, 0.5],
                     'coordinate_system': {'name': 'cartesian',
                                           'origin': [0, 0, 0]},
                     'kwargs': {'meshSize': 0.1}
                     },
                    # P6
                    {'coordinates': [-0.5, -0.5, 0.5],
                     'coordinate_system': {'name': 'cartesian',
                                           'origin': [0, 0, 0]},
                     'kwargs': {'meshSize': 0.1}
                     },
                    # P7
                    {'coordinates': [0.5, -0.75, 0.5],  # For ellipse arc
                     'coordinate_system': {'name': 'cartesian',
                                           'origin': [0, 0, 0]},
                     'kwargs': {'meshSize': 0.}
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
                          'kwargs': {'meshSize': 0.01}},
                         {'coordinates': [-0.5, 0.5, 0.],
                          'coordinate_system': 'cartesian',
                          'kwargs': {'meshSize': 0.01}},
                         {'coordinates': [-0.6, 0.5, 0.25],
                          'coordinate_system': 'cartesian',
                          'kwargs': {'meshSize': 0.01}}
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
                ])
            t0 = time.perf_counter()
            b.register()
            b2.register()
            b3.register()
            logging.info(f'Register: {time.perf_counter() - t0}s')
            if kws['factory'] == 'geo':
                b.quadrate()
                b2.quadrate()
                b3.quadrate()
                b.structure()
                b2.structure()
                b3.structure()
            if kws['factory'] == 'geo':
                gmsh.model.geo.synchronize()
            elif kws['factory'] == 'occ':
                gmsh.model.occ.synchronize()
            else:
                raise ValueError(kws['factory'])
            if kws['factory'] == 'occ':
                b.quadrate()
                b2.quadrate()
                b3.quadrate()
                b.structure()
                b2.structure()
                b3.structure()
            gmsh.model.mesh.generate(3)
            gmsh.write(f'{model_name}.{kws["output_format"]}')
            # reset_registry()
            # gmsh.clear()

    @gmsh_decorator
    def test_children(self):
        kwargs = {
            'factory': ['geo', 'occ'],
            # 'factory': ['geo'],
            # 'register_tag': [True, False],
            'register_tag': [True, False],
            # 'recombine_angle': [45.],
            # 'transfinite_curve_mesh_type': ['Progression', 'Bump', 'Beta'],
            # 'transfinite_curve_coef': [0.75, 1.0, 1.5],
            'output_format': ['msh2', 'geo_unrolled'
                              # 'vtk', 'stl',
                              # 'brep', 'step'
                              ]
            # auto, msh1, msh2, msh22, msh3, msh4, msh40, msh41, msh, unv,
            # vtk, wrl, mail, stl, p3d, mesh, bdf, cgns, med, diff, ir3, inp,
            # ply2, celum, su2, x3d, dat, neu, m, key
        }
        filter_kwargs = [{'factory': 'geo',
                          'output_format': 'brep'},
                         {'factory': 'geo',
                          'output_format': 'step'}]
        kwargs_combs = make_kwargs_combinations(kwargs, filter_kwargs)
        for kws in kwargs_combs:
            name_suffix = '-'.join(f'{k}_{v}' for k, v in kws.items())
            model_name = f'test_children-{name_suffix}'
            gmsh.model.add(model_name)
            logging.info(model_name)
            reset_registry()
            factory = kws.get('factory', 'geo')
            register_tag = kws.get('register_tag', False)
            b1 = Block(factory=factory,
                       points=[[0.5, 0.5, -0.5],
                               [-0.5, 0.5, -0.5],
                               [-0.5, -0.5, -0.5],
                               [0.5, -0.5, -0.5],
                               [0.5, 0.5, 0.5],
                               [-0.5, 0.5, 0.5],
                               [-0.5, -0.5, 0.5],
                               [0.5, -0.5, 0.5]],
                       use_register_tag=register_tag
                       )
            b2 = Block(factory=factory,
                       points=[[0.25, 0.25, -0.4],
                               [-0.25, 0.25, -0.4],
                               [-0.25, -0.25, -0.4],
                               [0.25, -0.25, -0.4],
                               [0.25, 0.25, -0.3],
                               [-0.25, 0.25, -0.3],
                               [-0.25, -0.25, -0.3],
                               [0.25, -0.25, -0.3]],
                       use_register_tag=register_tag,
                       parent=b1)
            b1.children.append(b2)
            b3 = Block(factory=factory,
                       points=[[0.25, 0.25, -0.3],
                               [-0.25, 0.25, -0.3],
                               [-0.25, -0.25, -0.3],
                               [0.25, -0.25, -0.3],
                               [0.25, 0.25, -0.2],
                               [-0.25, 0.25, -0.2],
                               [-0.25, -0.25, -0.2],
                               [0.25, -0.25, -0.2]],
                       use_register_tag=register_tag,
                       parent=b1)
            b1.children.append(b3)
            b4 = Block(factory=factory,
                       points=[[0.25, 0.25, 0.1],
                               [-0.25, 0.25, 0.1],
                               [-0.25, -0.25, 0.1],
                               [0.25, -0.25, 0.1],
                               [0.25, 0.25, 0.3],
                               [-0.25, 0.25, 0.3],
                               [-0.25, -0.25, 0.3],
                               [0.25, -0.25, 0.3]],
                       use_register_tag=register_tag,
                       parent=b1)
            b1.children.append(b4)
            b4_1 = Block(factory=factory,
                         points=[[0.2, 0.2, 0.15],
                                 [-0.2, 0.2, 0.15],
                                 [-0.2, -0.2, 0.15],
                                 [0.2, -0.2, 0.15],
                                 [0.2, 0.2, 0.2],
                                 [-0.2, 0.2, 0.2],
                                 [-0.2, -0.2, 0.2],
                                 [0.2, -0.2, 0.2]],
                         use_register_tag=register_tag,
                         parent=b4)
            b4.children.append(b4_1)
            b4_2 = Block(factory=factory,
                         points=[[0.2, 0.2, 0.2],
                                 [-0.2, 0.2, 0.2],
                                 [-0.2, -0.2, 0.2],
                                 [0.2, -0.2, 0.2],
                                 [0.2, 0.2, 0.25],
                                 [-0.2, 0.2, 0.25],
                                 [-0.2, -0.2, 0.25],
                                 [0.2, -0.2, 0.25]],
                         use_register_tag=register_tag,
                         do_register=True,
                         do_unregister=True,
                         parent=b4)
            b4.children.append(b4_2)
            b4_2_1 = Block(factory=factory,
                           points=[[0.1, 0.1, 0.22],
                                   [-0.1, 0.1, 0.22],
                                   [-0.1, -0.1, 0.22],
                                   [0.1, -0.1, 0.22],
                                   [0.1, 0.1, 0.24],
                                   [-0.1, 0.1, 0.24],
                                   [-0.1, -0.1, 0.24],
                                   [0.1, -0.1, 0.24]],
                           use_register_tag=register_tag,
                           do_register=True,
                           do_unregister=True,
                           parent=b4_2)
            b4_2.children.append(b4_2_1)
            t0 = time.perf_counter()
            b1.register()
            logging.info(f'Register: {time.perf_counter() - t0}s')
            if kws['factory'] == 'geo':
                gmsh.model.geo.synchronize()
            elif kws['factory'] == 'occ':
                gmsh.model.occ.synchronize()
            else:
                raise ValueError(kws['factory'])
            b1.unregister()
            if kws['output_format'] != 'geo_unrolled':
                gmsh.model.mesh.generate(3)
            gmsh.write(f'{model_name}.{kws["output_format"]}')

    @gmsh_decorator
    def test_transform(self):
        kwargs = {
            'factory': ['geo', 'occ'],
            # 'factory': ['geo'],
            # 'register_tag': [True, False],
            # 'register_tag': [True, False],
            # 'recombine_angle': [45.],
            # 'transfinite_curve_mesh_type': ['Progression', 'Bump', 'Beta'],
            # 'transfinite_curve_coef': [0.75, 1.0, 1.5],
            'output_format': [
                'geo_unrolled',
                'msh2',
                # 'vtk', 'stl',
                # 'brep', 'step'
            ]
            # auto, msh1, msh2, msh22, msh3, msh4, msh40, msh41, msh, unv,
            # vtk, wrl, mail, stl, p3d, mesh, bdf, cgns, med, diff, ir3, inp,
            # ply2, celum, su2, x3d, dat, neu, m, key
        }
        filter_kwargs = [{'factory': 'geo',
                          'output_format': 'brep'},
                         {'factory': 'geo',
                          'output_format': 'step'}]
        kwargs_combs = make_kwargs_combinations(kwargs, filter_kwargs)
        for kws in kwargs_combs:
            name_suffix = '-'.join(f'{k}_{v}' for k, v in kws.items())
            model_name = f'test_transform-{name_suffix}'
            gmsh.model.add(model_name)
            logging.info(model_name)
            reset_registry()
            factory = kws.get('factory', 'geo')
            b1 = Block(factory=factory,
                       points=[[0.5, 0.5, -0.5],
                               [-0.5, 0.5, -0.5],
                               [-0.5, -0.5, -0.5],
                               [0.5, -0.5, -0.5],
                               [0.5, 0.5, 0.5],
                               [-0.5, 0.5, 0.5],
                               [-0.5, -0.5, 0.5],
                               [0.5, -0.5, 0.5]],
                       transforms=[{'name': 'translate', 'delta': [0, 1, 2]},
                                   {'name': 'translate', 'delta': [1, -1, 2]}]
                       )
            b2 = Block(factory=factory,
                       points=[[0.25, 0.25, -0.4],
                               [-0.25, 0.25, -0.4],
                               [-0.25, -0.25, -0.4],
                               [0.25, -0.25, -0.4],
                               [0.25, 0.25, -0.3],
                               [-0.25, 0.25, -0.3],
                               [-0.25, -0.25, -0.3],
                               [0.25, -0.25, -0.3]],
                       transforms=[{'name': 'translate',
                                    'delta': [0.01, 0.01, 0.04]},
                                   {'name': 'rotate',
                                    'origin': [0.01, 0.01, 0.04],
                                    'direction': [1, 0, 0],
                                    'angle': 10}],
                       parent=b1
                       )
            b1.add_child(b2)
            b3 = Block(factory=factory,
                       points=[[0.25, 0.25, -0.3],
                               [-0.25, 0.25, -0.3],
                               [-0.25, -0.25, -0.3],
                               [0.25, -0.25, -0.3],
                               [0.25, 0.25, -0.2],
                               [-0.25, 0.25, -0.2],
                               [-0.25, -0.25, -0.2],
                               [0.25, -0.25, -0.2],
                               'block'],
                       transforms=['block_to_cartesian',
                                   [0, 0, 0, 1, 0, 0, -15],
                                   [0, 0, 0.1],
                                   [0, 0, 1, 10]],
                       parent=b1)
            b1.add_child(child=b3, transforms=[[0, 0, -0.1]])
            b4 = Block(factory=factory,
                       points=[[0.25, 0.25, -0.3],
                               [-0.25, 0.25, -0.3],
                               [-0.25, -0.25, -0.3],
                               [0.25, -0.25, -0.3],
                               [0.25, 0.25, -0.2],
                               [-0.25, 0.25, -0.2],
                               [-0.25, -0.25, -0.2],
                               [0.25, -0.3, -0.2],
                               0.2,
                               'block'],
                       curves=[
                           [[-0.20, 0.24, -0.3], [-0.15, 0.26, -0.3], 'block'],  # polyline
                           ['circle_arc', [[0., 0., -0.2, 1.], 'block']],
                           ['ellipse_arc', [[0.1, -0.25, -0.2], [0.25, -0.25, -0.2], 'block']],
                           ['spline', [[-0.1, -0.22, -0.3], [0.1, -0.28, -0.3], 'block']],
                           ['bspline', [[0.27, -0.1, -0.3], [0.23, 0.1, -0.3], 'block']],
                           ['bezier', [[-0.27, -0.1, -0.3], [-0.23, 0.1, -0.3], 'block']],
                           ['polyline', [[-0.27, -0.1, -0.2], [-0.23, 0.1, -0.2], 'block']],
                           [],
                           [],
                           [],
                           [],  # line
                           {}  # line
                       ],
                       transforms=['block_to_cartesian',
                                   [0, 0, 0, 1, 0, 0, -15],
                                   [0, 0, 0.3],
                                   [0, 0, 1, 10]],
                       parent=b1)
            b1.add_child(b4)
            b5 = Block(factory=factory,
                       points=[[0.25, 0.25, -0.5, 0.05],
                               [-0.25, 0.25, -0.5, 0.05],
                               [-0.25, -0.25, -0.5, 0.05],
                               [0.25, -0.25, -0.5, 0.05],
                               [0.25, 0.25, -0.1, 0.05],
                               [-0.25, 0.25, -0.1, 0.05],
                               [-0.25, -0.25, -0.1, 0.05],
                               [0.25, -0.3, -0.1, 0.05],
                               'block'],
                       curves=[
                           [[-0.20, 0.24, -0.5], [-0.15, 0.26, -0.5], 'block'],  # polyline
                           [],  # ['circle_arc', [[0., 0., -0.5], 'block']], BUG because parent block is deformed
                           ['ellipse_arc', [[0.1, -0.25, -0.1], [0.25, -0.25, -0.1], 'block']],
                           ['spline', [[-0.1, -0.22, -0.5], [0.1, -0.28, -0.5], 'block']],
                           ['bspline', [[0.27, -0.1, -0.5], [0.23, 0.1, -0.5], 'block']],
                           ['bezier', [[-0.27, -0.1, -0.5], [-0.23, 0.1, -0.5], 'block']],
                           ['polyline', [[-0.27, -0.1, -0.1], [-0.23, 0.1, -0.1], 'block']],
                           [],
                           [],
                           [],
                           [],  # line
                           {}  # line
                       ],
                       transforms=['block_to_cartesian',
                                   [0, 0, 0, 1, 0, 0, -15],
                                   [0, 0, -0.01],
                                   [0, 0, 1, 10]
                                   ],
                       parent=b4)
            b4.add_child(b5)
            b6 = Block(factory=factory,
                       points=[[0.1, 20, 0.35],
                               [0.05, 20, 0.35],
                               [0.05, 5, 0.35],
                               [0.1, 5, 0.35],
                               [0.1, 20, 0.4],
                               [0.05, 20, 0.4],
                               [0.05, 5, 0.4],
                               [0.1, 5, 0.4],
                               0.03,
                               'cylindrical'],
                       parent=b1,
                       transforms=['cylindrical_to_cartesian', [0.01, 0.01, 0]])
            b1.add_child(b6)
            b7 = Block(factory=factory,
                       points=[[0.08, 10, 0.37],
                               [0.07, 10, 0.37],
                               [0.07, 15, 0.37],
                               [0.08, 15, 0.37],
                               [0.08, 10, 0.38],
                               [0.07, 10, 0.38],
                               [0.07, 15, 0.38],
                               [0.08, 15, 0.38],
                               0.05,
                               'cylindrical'],
                       parent=b6,
                       transforms=['cylindrical_to_cartesian', [0, 0, 0.01]])
            b6.add_child(b7)
            b1.plot_tree()
            b1.transform()
            b1.register()
            if factory == 'geo':
                gmsh.model.geo.synchronize()
            elif factory == 'occ':
                gmsh.model.occ.synchronize()
            else:
                raise ValueError(factory)
            if kws['output_format'] != 'geo_unrolled':
                gmsh.model.mesh.generate(3)
            gmsh.write(f'{model_name}.{kws["output_format"]}')

    @gmsh_decorator
    def test_boolean(self):
        kwargs = {
            'factory': ['occ'],
            'boolean_type': ['with_bboxes', 'without_bboxes'],
            # 'factory': ['geo'],
            'register_tag': [True, False],
            # 'register_tag': [True, False],
            # 'recombine_angle': [45.],
            # 'transfinite_curve_mesh_type': ['Progression', 'Bump', 'Beta'],
            # 'transfinite_curve_coef': [0.75, 1.0, 1.5],
            'output_format': [
                'geo_unrolled',
                'msh2',
                # 'vtk', 'stl',
                # 'brep', 'step'
            ]
            # auto, msh1, msh2, msh22, msh3, msh4, msh40, msh41, msh, unv,
            # vtk, wrl, mail, stl, p3d, mesh, bdf, cgns, med, diff, ir3, inp,
            # ply2, celum, su2, x3d, dat, neu, m, key
        }
        filter_kwargs = [{'factory': 'geo',
                          'output_format': 'brep'},
                         {'factory': 'geo',
                          'output_format': 'step'}]
        kwargs_combs = make_kwargs_combinations(kwargs, filter_kwargs)
        for kws in kwargs_combs:
            name_suffix = '-'.join(f'{k}_{v}' for k, v in kws.items())
            model_name = f'test_boolean-{name_suffix}'
            gmsh.model.add(model_name)
            logging.info(model_name)
            reset_registry()
            factory = kws.get('factory', 'geo')
            b1 = Block(factory=factory,
                       points=[[0.5, 0.5, -0.5],
                               [-0.5, 0.5, -0.5],
                               [-0.5, -0.5, -0.5],
                               [0.5, -0.5, -0.5],
                               [0.5, 0.5, 0.5],
                               [-0.5, 0.5, 0.5],
                               [-0.5, -0.5, 0.5],
                               [0.5, -0.5, 0.5]],
                       boolean_level=1,
                       volumes=[{'zone': 'a'}]
                       )
            b2 = Block(factory=factory,
                       points=[[0.5, 0.5, -0.5],
                               [-0.5, 0.5, -0.5],
                               [-0.5, -0.5, -0.5],
                               [0.5, -0.5, -0.5],
                               [0.5, 0.5, 0.5],
                               [-0.5, 0.5, 0.5],
                               [-0.5, -0.5, 0.5],
                               [0.5, -0.5, 0.5],
                               'block'],
                       transforms=['block_to_cartesian'],
                       parent=b1,
                       boolean_level=0,
                       volumes=[{'zone': 'ba'}]
                       )
            b1.add_child(b2)
            b3 = Block(factory=factory,
                       points=[[0.5, 0.5, -0.1],
                               [-0.5, 0.5, -0.1],
                               [-0.5, -0.5, -0.1],
                               [0.5, -0.5, -0.1],
                               [0.5, 0.5, 0.5],
                               [-0.5, 0.5, 0.5],
                               [-0.5, -0.5, 0.5],
                               [0.5, -0.5, 0.5],
                               'block'],
                       transforms=['block_to_cartesian'],
                       parent=b2,
                       boolean_level=2,
                       volumes=[{'zone': 'cb'}]
                       )
            b2.add_child(b3)
            b4 = Block(factory=factory,
                       points=[[0.5, 0.5, -0.5],
                               [-0.5, 0.5, -0.5],
                               [-0.5, -0.5, -0.5],
                               [0.5, -0.5, -0.5],
                               [0.5, 0.5, 0.1],
                               [-0.5, 0.5, 0.1],
                               [-0.5, -0.5, 0.1],
                               [0.5, -0.5, 0.1],
                               'block'],
                       transforms=['block_to_cartesian'],
                       parent=b2,
                       boolean_level=2,
                       do_unregister=True,
                       volumes=[{'zone': 'ca'}]
                       )
            b2.add_child(b4)
            b5 = Block(factory=factory,
                       points=[[0.95, 0.95, 0.1],
                               [0.90, 0.95, 0.1],
                               [0.90, 0.90, 0.1],
                               [0.95, 0.90, 0.1],
                               [0.95, 0.95, 0.2],
                               [0.90, 0.95, 0.2],
                               [0.90, 0.90, 0.2],
                               [0.95, 0.90, 0.2],
                               'block'],
                       transforms=['block_to_cartesian'],
                       parent=b1,
                       boolean_level=2,
                       do_unregister=True,
                       volumes=[{'zone': 'bb'}]
                       )
            b1.add_child(b5)
            t0 = time.perf_counter()
            b1.transform()
            logging.info(f'transform: {time.perf_counter() - t0}')
            t0 = time.perf_counter()
            b1.register()
            logging.info(f'register: {time.perf_counter() - t0}')
            if factory == 'occ':
                t0 = time.perf_counter()
                if kws['boolean_type'] == 'without_bboxes':
                    boolean(b1)
                elif kws['boolean_type'] == 'with_bboxes':
                    gmsh.model.occ.synchronize()  # for evaluation of bboxes
                    boolean_with_bounding_boxes(b1)
                gmsh.model.occ.removeAllDuplicates()
                logging.info(f'boolean: {time.perf_counter() - t0}')
            t0 = time.perf_counter()
            b1.unregister()
            logging.info(f'unregister: {time.perf_counter() - t0}')
            t0 = time.perf_counter()
            if factory == 'geo':
                gmsh.model.geo.synchronize()
            elif factory == 'occ':
                gmsh.model.occ.synchronize()
            else:
                raise ValueError(factory)
            logging.info(f'synchronize: {time.perf_counter() - t0}')
            if factory == 'occ':
                t0 = time.perf_counter()
                b1.quadrate()
                logging.info(f'quadrate: {time.perf_counter() - t0}')
                t0 = time.perf_counter()
                b1.structure()
                logging.info(f'structure: {time.perf_counter() - t0}')
            t0 = time.perf_counter()
            b1.plot_tree(file_name=model_name,
                         label_type='volume_zone', group_type='volume_zone')
            zone2tag = {}
            for i, b in enumerate(b1):
                for v in b.volumes:
                    if v.tag is not None:
                        zone2tag.setdefault(v.zone, []).append(v.tag)
            for zone, tags in zone2tag.items():
                tag = gmsh.model.addPhysicalGroup(3, tags)
                gmsh.model.setPhysicalName(3, tag, zone)
            logging.info(f'zones: {time.perf_counter() - t0}')
            t0 = time.perf_counter()
            if kws['output_format'] != 'geo_unrolled':
                gmsh.model.mesh.generate(3)
            logging.info(f'mesh: {time.perf_counter() - t0}')
            t0 = time.perf_counter()
            gmsh.write(f'{model_name}.{kws["output_format"]}')
            logging.info(f'write: {time.perf_counter() - t0}')

    @gmsh_decorator
    def test_zones(self):
        kwargs = {
            # 'factory': ['occ'],
            # 'boolean_type': ['with_bboxes', 'without_bboxes'],
            'factory': ['geo', 'occ'],
            # 'register_tag': [True, False],
            # 'register_tag': [True, False],
            # 'recombine_angle': [45.],
            # 'transfinite_curve_mesh_type': ['Progression', 'Bump', 'Beta'],
            # 'transfinite_curve_coef': [0.75, 1.0, 1.5],
            'output_format': [
                'geo_unrolled',
                'msh2',
                # 'vtk', 'stl',
                # 'brep', 'step'
            ]
            # auto, msh1, msh2, msh22, msh3, msh4, msh40, msh41, msh, unv,
            # vtk, wrl, mail, stl, p3d, mesh, bdf, cgns, med, diff, ir3, inp,
            # ply2, celum, su2, x3d, dat, neu, m, key
        }
        filter_kwargs = [{'factory': 'geo',
                          'output_format': 'brep'},
                         {'factory': 'geo',
                          'output_format': 'step'}]
        kwargs_combs = make_kwargs_combinations(kwargs, filter_kwargs)
        for kws in kwargs_combs:
            name_suffix = '-'.join(f'{k}_{v}' for k, v in kws.items())
            model_name = f'test_zones-{name_suffix}'
            gmsh.model.add(model_name)
            logging.info(model_name)
            reset_registry()
            factory = kws.get('factory', 'geo')
            b0 = Block(factory=factory, do_register=False)
            b1 = Block(factory=factory,
                       points=[{'coordinates': [0.5, 0.5, -0.5],
                                'zone': 'p1'},
                               # {'coordinates': [-0.5, 0.5, -0.5],
                               #  'zone': 'p2'},
                               [-0.5, 0.5, -0.5, 'p2'],
                               [-0.5, -0.5, -0.5],
                               {'coordinates': [0.5, -0.5, -0.5],
                                'zone': 'p4'},
                               {'coordinates': [0.5, 0.5, 0.5],
                                'zone': 'p5'},
                               {'coordinates': [-0.5, 0.5, 0.5],
                                'zone': 'p6'},
                               {'coordinates': [-0.5, -0.5, 0.5],
                                'zone': 'p7'},
                               {'coordinates': [0.5, -0.5, 0.5],
                                'zone': 'p8'}],
                       curves=[{'zone': 'x1'}, {'zone': 'x2'},
                               {'zone': 'x3'}, {'zone': 'x4'},
                               {'zone': 'y1'}, {'zone': 'y2'},
                               {'zone': 'y3'}, {'zone': 'y4'},
                               {'zone': 'z1'}, {'zone': 'z2'},
                               {'zone': 'z3'}, {'zone': 'z4'}],
                       surfaces=[{'zone': 'nx'}, {'zone': 'x'}, {'zone': 'ny'},
                                 {'zone': 'y'}, {'zone': 'nz'}, {'zone': 'z'}],
                       volumes=[{'zone': 'v'}],
                       parent=b0
                       )
            b0.add_child(b1)
            b2 = Block(factory=factory,
                       points=[{'coordinates': [0.5, 0.5, -0.5],
                                'zone': 'p1'},
                               # {'coordinates': [-0.5, 0.5, -0.5],
                               #  'zone': 'p2'},
                               [-0.5, 0.5, -0.5, 'p2'],
                               [-0.5, -0.5, -0.5],
                               {'coordinates': [0.5, -0.5, -0.5],
                                'zone': 'p4'},
                               {'coordinates': [0.5, 0.5, 0.5],
                                'zone': 'p5'},
                               {'coordinates': [-0.5, 0.5, 0.5],
                                'zone': 'p6'},
                               {'coordinates': [-0.5, -0.5, 0.5],
                                'zone': 'p7'},
                               {'coordinates': [0.5, -0.5, 0.5],
                                'zone': 'p8'}],
                       curves=[{'zone': 'x1'}, {'zone': 'x2'},
                               {'zone': 'x3'}, {'zone': 'x4'},
                               {'zone': 'y1'}, {'zone': 'y2'},
                               {'zone': 'y3'}, {'zone': 'y4'},
                               {'zone': 'z1'}, {'zone': 'z2'},
                               {'zone': 'z3'}, {'zone': 'z4'}],
                       surfaces=[{'zone': 'nx'}, {'zone': 'x'}, {'zone': 'ny'},
                                 {'zone': 'y'}, {'zone': 'nz'}, {'zone': 'z'}],
                       zone_all='v2',
                       parent=b0
                       )
            b0.add_child(b2, [[1, 0, 0]])
            b3 = Block(factory=factory,
                       points=[{'coordinates': [0.5, 0.5, -0.5],
                                'zone': 'p1'},
                               # {'coordinates': [-0.5, 0.5, -0.5],
                               #  'zone': 'p2'},
                               [-0.5, 0.5, -0.5, 'p2'],
                               [-0.5, -0.5, -0.5],
                               {'coordinates': [0.5, -0.5, -0.5],
                                'zone': 'p4'},
                               {'coordinates': [0.5, 0.5, 0.5],
                                'zone': 'p5'},
                               {'coordinates': [-0.5, 0.5, 0.5],
                                'zone': 'p6'},
                               {'coordinates': [-0.5, -0.5, 0.5],
                                'zone': 'p7'},
                               {'coordinates': [0.5, -0.5, 0.5],
                                'zone': 'p8'}],
                       curves=[{'zone': 'x1'}, {'zone': 'x2'},
                               {'zone': 'x3'}, {'zone': 'x4'},
                               {'zone': 'y1'}, {'zone': 'y2'},
                               {'zone': 'y3'}, {'zone': 'y4'},
                               {'zone': 'z1'}, {'zone': 'z2'},
                               {'zone': 'z3'}, {'zone': 'z4'}],
                       surfaces=[{'zone': 'nx'}, {'zone': 'x'}, {'zone': 'ny'},
                                 {'zone': 'y'}, {'zone': 'nz'}, {'zone': 'z'}],
                       zone_all=['v3'],
                       parent=b0
                       )
            b0.add_child(b3, [[-1, 0, 0]])
            b4 = Block(factory=factory,
                       points=[{'coordinates': [0.5, 0.5, -0.5],
                                'zone': 'p1'},
                               # {'coordinates': [-0.5, 0.5, -0.5],
                               #  'zone': 'p2'},
                               [-0.5, 0.5, -0.5, 'p2'],
                               [-0.5, -0.5, -0.5],
                               {'coordinates': [0.5, -0.5, -0.5],
                                'zone': 'p4'},
                               {'coordinates': [0.5, 0.5, 0.5],
                                'zone': 'p5'},
                               {'coordinates': [-0.5, 0.5, 0.5],
                                'zone': 'p6'},
                               {'coordinates': [-0.5, -0.5, 0.5],
                                'zone': 'p7'},
                               {'coordinates': [0.5, -0.5, 0.5],
                                'zone': 'p8'}],
                       curves=[{'zone': 'x1'}, {'zone': 'x2'},
                               {'zone': 'x3'}, {'zone': 'x4'},
                               {'zone': 'y1'}, {'zone': 'y2'},
                               {'zone': 'y3'}, {'zone': 'y4'},
                               {'zone': 'z1'}, {'zone': 'z2'},
                               {'zone': 'z3'}, {'zone': 'z4'}],
                       zone_all=[['v4'], ['nx', 'x', 'ny', 'y', 'nz', 'z']],
                       parent=b0
                       )
            b0.add_child(b4, [[0, 1, 0]])
            b5 = Block(factory=factory,
                       points=[{'coordinates': [0.5, 0.5, -0.5],
                                'zone': 'p1'},
                               # {'coordinates': [-0.5, 0.5, -0.5],
                               #  'zone': 'p2'},
                               [-0.5, 0.5, -0.5, 'p2'],
                               [-0.5, -0.5, -0.5],
                               {'coordinates': [0.5, -0.5, -0.5],
                                'zone': 'p4'},
                               {'coordinates': [0.5, 0.5, 0.5],
                                'zone': 'p5'},
                               {'coordinates': [-0.5, 0.5, 0.5],
                                'zone': 'p6'},
                               {'coordinates': [-0.5, -0.5, 0.5],
                                'zone': 'p7'},
                               {'coordinates': [0.5, -0.5, 0.5],
                                'zone': 'p8'}],
                       zone_all=[['v5'],
                                 ['nx', 'x', 'ny', 'y', 'nz', 'z'],
                                 ['x1', 'x2', 'x3', 'x4',
                                  'y1', 'y2', 'y3', 'y4',
                                  'z1', 'z2', 'z3', 'z4']],
                       parent=b0
                       )
            b0.add_child(b5, [[0, -1, 0]])
            b6 = Block(factory=factory,
                       points=[[0.5, 0.5, -0.5],
                               [-0.5, 0.5, -0.5],
                               [-0.5, -0.5, -0.5],
                               [0.5, -0.5, -0.5],
                               [0.5, 0.5, 0.5],
                               [-0.5, 0.5, 0.5],
                               [-0.5, -0.5, 0.5],
                               [0.5, -0.5, 0.5]],
                       zone_all=[['v6'],
                                 ['nx', 'x', 'ny', 'y', 'nz', 'z'],
                                 ['x1', 'x2', 'x3', 'x4',
                                  'y1', 'y2', 'y3', 'y4',
                                  'z1', 'z2', 'z3', 'z4'],
                                 ['p1', 'p2', 'p3', 'p4',
                                  'p5', 'p6', 'p7', 'p8']],
                       parent=b0
                       )
            b0.add_child(b6, [[0, 0, 1]])
            b7 = Block(factory=factory,
                       points=[{'coordinates': [0.5, 0.5, -0.5],
                                'zone': 'p1'},
                               # {'coordinates': [-0.5, 0.5, -0.5],
                               #  'zone': 'p2'},
                               [-0.5, 0.5, -0.5, 'p2'],
                               [-0.5, -0.5, -0.5],
                               {'coordinates': [0.5, -0.5, -0.5],
                                'zone': 'p4'},
                               {'coordinates': [0.5, 0.5, 0.5],
                                'zone': 'p5'},
                               {'coordinates': [-0.5, 0.5, 0.5],
                                'zone': 'p6'},
                               {'coordinates': [-0.5, -0.5, 0.5],
                                'zone': 'p7'},
                               {'coordinates': [0.5, -0.5, 0.5],
                                'zone': 'p8'}],
                       curves=[{'zone': 'x1'}, {'zone': 'x2'},
                               {'zone': 'x3'}, {'zone': 'x4'},
                               {'zone': 'y1'}, {'zone': 'y2'},
                               {'zone': 'y3'}, {'zone': 'y4'},
                               {'zone': 'z1'}, {'zone': 'z2'},
                               {'zone': 'z3'}, {'zone': 'z4'}],
                       surfaces=[{'zone': 'nx'}, {'zone': 'x'}, {'zone': 'ny'},
                                 {'zone': 'y'}, {'zone': 'nz'}, {'zone': 'z'}],
                       zone_all=[['v7']],
                       parent=b0
                       )
            b0.add_child(b7, [[0, 0, -1]])
            t0 = time.perf_counter()
            b0.transform()
            logging.info(f'transform: {time.perf_counter() - t0}')
            t0 = time.perf_counter()
            b0.register()
            logging.info(f'register: {time.perf_counter() - t0}')
            t0 = time.perf_counter()
            if factory == 'geo':
                gmsh.model.geo.synchronize()
            elif factory == 'occ':
                gmsh.model.occ.synchronize()
            else:
                raise ValueError(factory)
            logging.info(f'synchronize: {time.perf_counter() - t0}')
            if factory == 'occ':
                t0 = time.perf_counter()
                b0.quadrate()
                logging.info(f'quadrate: {time.perf_counter() - t0}')
                t0 = time.perf_counter()
                b0.structure()
                logging.info(f'structure: {time.perf_counter() - t0}')
            t0 = time.perf_counter()
            z2tg = BlockSimple()(b0)
            for zone, tags in z2tg.items():
                dims, tags = [x[0] for x in tags], [x[1] for x in tags]
                if len(set(dims)) == 1:
                    dim = dims[0]
                else:
                    raise ValueError(tags)
                tag = gmsh.model.addPhysicalGroup(dim, tags)
                gmsh.model.setPhysicalName(dim, tag, zone)
            logging.info(f'zones: {time.perf_counter() - t0}')
            t0 = time.perf_counter()
            if kws['output_format'] != 'geo_unrolled':
                gmsh.model.mesh.generate(3)
            logging.info(f'mesh: {time.perf_counter() - t0}')
            t0 = time.perf_counter()
            gmsh.write(f'{model_name}.{kws["output_format"]}')
            logging.info(f'write: {time.perf_counter() - t0}')


if __name__ == '__main__':
    unittest.main()
