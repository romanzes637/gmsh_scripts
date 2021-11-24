import unittest

import numpy as np

from support import GmshDecorator, LoggingDecorator, GmshOptionsDecorator
from strategy import Simple, Fast
from layer import Layer
from coordinate_system import Path


class TestLayer(unittest.TestCase):

    @LoggingDecorator(level='DEBUG')
    @GmshDecorator()
    @GmshOptionsDecorator()
    def test_layer(self):
        for factory in ['geo', 'occ']:
            model_name = f'test_layer-{factory}'
            layer = Layer(
                layers=[['1;.4;3', '2;.3', '3;.5'],
                        ['1;.3', '2;.3']],
                layers_curves_names=[['line', 'line', 'circle_arc'],
                                     ['line', 'line']],
                layers_types=[['in', 'in', 'in'],
                              ['in', 'in']],
                do_register_map=[[[1, 1, 1],
                                  [1, 1, 1]]],
                boolean_level_map=[[[0, 1, 2],
                                    [3, 4, 5]]]
                # transforms=[[3, 0, 1]]
            )
            Fast(factory, model_name)(layer)

    @LoggingDecorator(level='DEBUG')
    @GmshDecorator()
    @GmshOptionsDecorator()
    def test_layer_path(self):
        for factory in ['geo', 'occ']:
            model_name = f'test_layer_path-{factory}'
            curves = [['line', [[10, 0, x], [10, 0, x + 10], 'sph']]
                      for x in np.linspace(0, 80, 9)]
            orientations = [[[1, 180, x], 'sph'] for x in np.linspace(90, 0, 10)]
            cs = Path(factory=factory, curves=curves, orientations=orientations)
            layer = Layer(
                layers=[['1;1', '2;1', '3;1'],
                        ['.2;1', '.5;1', '.7;1', '1;1'],
                        cs],
                layers_curves_names=[['line', 'line', 'circle_arc'],
                                     ['line', 'line', 'line', 'line']]
            )
            Simple(factory, model_name)(layer)
