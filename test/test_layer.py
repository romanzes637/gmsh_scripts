import logging
import unittest

from support import GmshDecorator, LoggingDecorator, GmshOptionsDecorator
from strategy import Simple
from layer import Layer
from coordinate_system import LayerXY
from matrix import Matrix


class TestLayer(unittest.TestCase):

    @LoggingDecorator(level='DEBUG')
    @GmshDecorator()
    @GmshOptionsDecorator()
    def test_layer(self):
        for factory in ['geo', 'occ']:
            model_name = f'test_layer-{factory}'
            logging.info(model_name)
            lxy = LayerXY(
                layers=[
                    [1, 2, 3, 4],
                    [1, 2, 3, 4],
                    [1, 2, 3, 4],
                    [1, 2, 3, 4]],
                curves_names=[
                    ['line', 'circle_arc', 'circle_arc', 'line'],
                    ['line', 'circle_arc', 'circle_arc', 'line'],
                    ['line', 'circle_arc', 'circle_arc', 'line'],
                    ['line', 'circle_arc', 'circle_arc', 'line']],
                layers_types=['in', 'out', 'in', 'out'])
            # b = BlockObject(factory=factory, do_register=False)
            m = Matrix(
                points=[[-4, -3, -2, -1, 1, 2, 3, 4],
                        [-4, -3, -2, -1, 1, 2, 3, 4],
                        [0, 1, 2], lxy],
                curves=[
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
                curves_map=[
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
                do_register_map=[
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
                structure_type_map=[
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
                boolean_level_map=0,
                quadrate_map=0)
            Simple(factory, model_name)(m)
