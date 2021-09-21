import unittest
import numpy as np
from itertools import product
from pprint import pprint
import time

import gmsh

from registry import reset as reset_registry
from block import Block


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
            print(model_name)
            reset_registry()
            gmsh.model.add(model_name)
            # B1
            b = Block(
                factory=kws['factory'],
                register_tag=kws['register_tag'],
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
                register_tag=kws['register_tag'],
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
                recombine_all=True,
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
                transfinite_all={
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
                register_tag=kws['register_tag'],
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
            print(f'Register: {time.perf_counter() - t0}s')
            if kws['factory'] == 'geo':
                b.recombine()
                b2.recombine()
                b3.recombine()
                b.transfinite()
                b2.transfinite()
                b3.transfinite()
            if kws['factory'] == 'geo':
                gmsh.model.geo.synchronize()
            elif kws['factory'] == 'occ':
                gmsh.model.occ.synchronize()
            else:
                raise ValueError(kws['factory'])
            if kws['factory'] == 'occ':
                b.recombine()
                b2.recombine()
                b3.recombine()
                b.transfinite()
                b2.transfinite()
                b3.transfinite()
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
            print(model_name)
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
                       register_tag=register_tag
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
                       register_tag=register_tag,
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
                       register_tag=register_tag,
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
                       register_tag=register_tag,
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
                         register_tag=register_tag,
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
                         register_tag=register_tag,
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
                           register_tag=register_tag,
                           do_register=True,
                           do_unregister=True,
                           parent=b4_2)
            b4_2.children.append(b4_2_1)
            t0 = time.perf_counter()
            b1.register()
            print(f'Register: {time.perf_counter() - t0}s')
            if kws['factory'] == 'geo':
                gmsh.model.geo.synchronize()
            elif kws['factory'] == 'occ':
                gmsh.model.occ.synchronize()
            else:
                raise ValueError(kws['factory'])
            b1.unregister()
            gmsh.model.mesh.generate(3)
            gmsh.write(f'{model_name}.{kws["output_format"]}')


if __name__ == '__main__':
    unittest.main()
