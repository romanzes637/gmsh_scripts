import unittest

from support import GmshDecorator, LoggingDecorator, GmshOptionsDecorator
from strategy import Simple, Fast
from layer import Layer


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
