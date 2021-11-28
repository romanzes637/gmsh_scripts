import unittest
import logging

import numpy as np

from support import LoggingDecorator, flatten
import parse


class TestParser(unittest.TestCase):

    @LoggingDecorator()
    def test_parse_grid_row(self):
        logging.info('1')
        row = ['v;p', -3.3, -1, 0, 1.1, 4]
        logging.info(f'row: {row}')
        bs = [0, 1, 2, 3]
        new_bs_true = [0, 1, 2, 3]
        logging.info(f'blocks: {bs}')
        row, values, maps = parse.parse_row(row)
        new2old_b2b = maps[-1]
        new_bs = [bs[x] for x in new2old_b2b]
        self.assertListEqual(new_bs_true, new_bs)

        logging.info('2')
        row = ['i;p', -3.3, -1, 0, 1.1, 4]
        logging.info(f'row: {row}')
        bs = [0, 1, 2, 3]
        new_bs_true = [0, 1, 2, 3]
        logging.info(f'blocks: {bs}')
        row, values, maps = parse.parse_row(row)
        new2old_b2b = maps[-1]
        new_bs = [bs[x] for x in new2old_b2b]
        self.assertListEqual(new_bs_true, new_bs)

        logging.info('3')
        row = ['v;s', -3.3, '-1:2', 0, 1.1, 4]
        logging.info(f'row: {row}')
        bs = [0, 1, 2, 3]
        new_bs_true = [0, 1, 2, 3]
        logging.info(f'blocks: {bs}')
        row, values, maps = parse.parse_row(row)
        new2old_b2b = maps[-1]
        new_bs = [bs[x] for x in new2old_b2b]
        self.assertListEqual(new_bs_true, new_bs)

        logging.info('4')
        row = ['v;s', -3.3, '-1:3', 0, 1.1, 4]
        logging.info(f'row: {row}')
        bs = [0, 1, 2, 3]
        new_bs_true = [0, 0, 1, 2, 3]
        cs_true = [-3.3, -2.15, -1, 0, 1.1, 4]
        logging.info(f'blocks: {bs}')
        row, values, maps = parse.parse_row(row)
        new2old_b2b = maps[-1]
        new_bs = [bs[x] for x in new2old_b2b]
        self.assertListEqual(new_bs_true, new_bs)
        cs = values[0]
        self.assertListEqual(cs_true, cs)

        logging.info('5')
        row = ['v;s', -3.3, '-1:3;3.', 0, 1.1, 4]
        logging.info(f'row: {row}')
        bs = [0, 1, 2, 3]
        new_bs_true = [0, 0, 1, 2, 3]
        ms_true = [None, 3, 3, None, None, None]
        logging.info(f'blocks: {bs}')
        row, values, maps = parse.parse_row(row)
        new2old_b2b = maps[-1]
        new_bs = [bs[x] for x in new2old_b2b]
        self.assertListEqual(new_bs_true, new_bs)
        ms = values[1]
        self.assertListEqual(ms_true, ms)

        logging.info('6')
        row = ['v;s', -3.3, '-1:3;3.;4', 0, 1.1, 4]
        logging.info(f'row: {row}')
        bs = [0, 1, 2, 3]
        new_bs_true = [0, 0, 1, 2, 3]
        ms_true = [None, 3, 3, None, None, None]
        ss_true = [None, [4, 0, 1], [4, 0, 1], None, None, None]
        logging.info(f'blocks: {bs}')
        row, values, maps = parse.parse_row(row)
        new2old_b2b = maps[-1]
        new_bs = [bs[x] for x in new2old_b2b]
        self.assertListEqual(new_bs_true, new_bs)
        ms = values[1]
        self.assertListEqual(ms_true, ms)
        ss = values[2]
        self.assertListEqual(ss_true, ss)

        logging.info('7')
        row = ['v;s', -3.3, '-1:3;3.;4', 0, '1.1:3;4.;5:1:1.2', 4]
        logging.info(f'row: {row}')
        bs = [0, 1, 2, 3]
        new_bs_true = [0, 0, 1, 2, 2, 3]
        ms_true = [None, 3., 3., None, 4., 4., None]
        ss_true = [None, [4, 0, 1], [4, 0, 1], None, [5, 1, 1.2], [5, 1, 1.2], None]
        logging.info(f'blocks: {bs}')
        row, values, maps = parse.parse_row(row)
        new2old_b2b = maps[-1]
        new_bs = [bs[x] for x in new2old_b2b]
        self.assertListEqual(new_bs_true, new_bs)
        ms = values[1]
        self.assertListEqual(ms_true, ms)
        ss = values[2]
        self.assertListEqual(ss_true, ss)

        logging.info('8')
        row = ['v;s', -3.3, '-1:4:0.5:0.5', 0, 1.1, 4]
        logging.info(f'row: {row}')
        bs = [0, 1, 2, 3]
        new_bs_true = [0, 0, 0, 1, 2, 3]
        cs_true = [-3.3, -2.4010554433227367, -1.8987877789497376,
                   -1, 0, 1.1, 4]
        logging.info(f'blocks: {bs}')
        row, values, maps = parse.parse_row(row)
        new2old_b2b = maps[-1]
        new_bs = [bs[x] for x in new2old_b2b]
        self.assertListEqual(new_bs_true, new_bs)
        new_cs = values[0]
        self.assertListEqual(cs_true, new_cs)

        logging.info('9')
        row = ['v;s', -3.3, '-1:4:0.5:0.5;3.:1.1:1.2:1.2', 0, 1.1, 4]
        logging.info(f'row: {row}')
        bs = [0, 1, 2, 3]
        new_bs_true = [0, 0, 0, 1, 2, 3]
        cs_true = [-3.3, -2.4010554433227367, -1.8987877789497376,
                   -1, 0, 1.1, 4]
        ms_true = [None, 6.649247709847758, 6.649202077211734, 3.0,
                   None, None, None]
        logging.info(f'blocks: {bs}')
        row, values, maps = parse.parse_row(row)
        new2old_b2b = maps[-1]
        new_bs = [bs[x] for x in new2old_b2b]
        self.assertListEqual(new_bs_true, new_bs)
        cs = values[0]
        self.assertListEqual(cs_true, cs)
        ms = values[1]
        self.assertListEqual(ms_true, ms)

    @LoggingDecorator()
    def test_parse_grid(self):
        old_b_nd = [[[0, 1, 2],
                     [3, 4, 5],
                     [6, 7, 8]],
                    [[9, 10, 11],
                     [12, 13, 14],
                     [15, 16, 17]]]
        old_b_1d = list(flatten(old_b_nd))
        new_b_nd_true = [[[0, 1, 1, 2],
                          [3, 4, 4, 5],
                          [6, 7, 7, 8]],
                         [[9, 10, 10, 11],
                          [12, 13, 13, 14],
                          [15, 16, 16, 17]],
                         [[9, 10, 10, 11],
                          [12, 13, 13, 14],
                          [15, 16, 16, 17]]]
        new_b_1d_true = list(flatten(new_b_nd_true))
        grid = [[-3.3, -1, '1.1:3', 4],
                ['i;p', -3.3, -1, 0, 4],
                ['v;s', -3.3, '-1:3'],
                ['i;s', -3.3, '4:3'],
                'cartesian',
                0.7]
        new_grid, values, maps = parse.parse_grid(grid)
        n2o_b2b = maps[-1]
        new_b_1d = [old_b_1d[x] for x in n2o_b2b]
        self.assertListEqual(new_b_1d, new_b_1d_true)
        n_b2b_g2l = maps[-2]
        shape = np.array([list(x) for x in n_b2b_g2l]).max(axis=0)
        shape = [x + 1 for x in shape]
        new_b_nd = np.array(new_b_1d).reshape(shape).tolist()
        self.assertListEqual(new_b_nd, new_b_nd_true)

    @LoggingDecorator()
    def test_layers(self):
        logging.info('layers_6')
        layers_6 = [
            [0, 1, 2, 3],  # X
            [4, 5, 6],  # Y
            [7, 8],  # NX
            [9],  # NY
            [10, 11],  # Z
            [12, 13],  # NZ
        ]
        block_map = [
            [
                [[0, 1, 2, 3],
                 [0, 1, 2, 3]],
                [[0, 1, 2, 3],
                 [0, 1, 2, 3]],
            ],
            [
                [[4, 5, 6],
                 [4, 5, 6]],
                [[4, 5, 6],
                 [4, 5, 6]]
            ],
            [
                [[7, 8],
                 [7, 8]],
                [[7, 8],
                 [7, 8]]
            ],
            [
                [[9],
                 [9]],
                [[9],
                 [9]]
            ]
        ]
        new_block_map_true = block_map
        grid, values, maps = parse.parse_layers2grid(layers_6)
        n2o_b2b_l2l, n2o_b2b_g2g = maps[2], maps[3]
        block_map_flat = list(flatten(block_map))
        new_block_map_flat = [block_map_flat[x] for x in n2o_b2b_g2g]
        self.assertListEqual(new_block_map_flat, list(flatten(new_block_map_true)))

        logging.info('layers_2')
        layers_2 = [
            [0, 1, 2, 3],  # X
            [4, 5]  # Z
        ]
        block_map = [
            [0, 1, 2, 3],
            [0, 1, 2, 3]
        ]
        new_block_map_true = [
            [
                [[0, 1, 2, 3],
                 [0, 1, 2, 3]]
            ],
            [
                [[0, 1, 2, 3],
                 [0, 1, 2, 3]]
            ],
            [
                [[0, 1, 2, 3],
                 [0, 1, 2, 3]]
            ],
            [
                [[0, 1, 2, 3],
                 [0, 1, 2, 3]]
            ]
        ]
        grid, values, maps = parse.parse_layers2grid(layers_2)
        n2o_b2b_l2l, n2o_b2b_g2g = maps[2], maps[3]
        block_map_flat = list(flatten(block_map))
        new_block_map_flat = [block_map_flat[x] for x in n2o_b2b_g2g]
        self.assertListEqual(new_block_map_flat, list(flatten(new_block_map_true)))
        logging.info('layers_3')
        layers_3 = [
            [0, 1, 2, 3],  # X
            [4, 5, 6],  # Y
            [7, 8]  # Z
        ]
        block_map = [
            [
                [[0, 1, 2, 3],
                 [0, 1, 2, 3]]
            ],
            [
                [[4, 5, 6],
                 [4, 5, 6]]
            ]
        ]
        new_block_map_true = [
            [
                [0, 1, 2, 3],
                [0, 1, 2, 3]
            ],
            [
                [4, 5, 6],
                [4, 5, 6]
            ],
            [
                [0, 1, 2, 3],
                [0, 1, 2, 3]
            ],
            [
                [4, 5, 6],
                [4, 5, 6]
            ]
        ]
        grid, values, maps = parse.parse_layers2grid(layers_3)
        n2o_b2b_l2l, n2o_b2b_g2g = maps[2], maps[3]
        block_map_flat = list(flatten(block_map))
        new_block_map_flat = [block_map_flat[x] for x in n2o_b2b_g2g]
        self.assertListEqual(new_block_map_flat, list(flatten(new_block_map_true)))

        logging.info('layers_2_ext')
        layers_2_ext = [
            ['0;1;', '1;;100', '3:3;30;300'],  # X
            [4, 5]  # Z
        ]
        block_map = [
            [0, 1, 2],
            [0, 1, 2]
        ]
        parsed_block_map_true = [
            [
                [[0, 1, 2, 2],
                 [0, 1, 2, 2]]
            ],
            [
                [[0, 1, 2, 2],
                 [0, 1, 2, 2]]
            ],
            [
                [[0, 1, 2, 2],
                 [0, 1, 2, 2]]
            ],
            [
                [[0, 1, 2, 2],
                 [0, 1, 2, 2]]
            ]
        ]
        grid_map_true = [
            [[None, None, None, 2, None, None, None],
             [None, None, None, 2, None, None, None],
             [None, None, None, 1, None, None, None],
             [2, 2, 1, 0, 1, 2, 2],
             [None, None, None, 1, None, None, None],
             [None, None, None, 2, None, None, None],
             [None, None, None, 2, None, None, None]],
            [[None, None, None, 2, None, None, None],
             [None, None, None, 2, None, None, None],
             [None, None, None, 1, None, None, None],
             [2, 2, 1, 0, 1, 2, 2],
             [None, None, None, 1, None, None, None],
             [None, None, None, 2, None, None, None],
             [None, None, None, 2, None, None, None]]
        ]
        grid, values, maps = parse.parse_layers2grid(layers_2_ext)
        # Parsed -> Corrected -> Original
        n2o_b2b_g2g = maps[11]
        # Grid -> Parsed -> Corrected -> Original
        g2o_b2b_g2g = maps[13]
        # Check
        block_map_flat = list(flatten(block_map))
        parsed_block_map_flat = [block_map_flat[x] for x in n2o_b2b_g2g]
        parsed_block_map_true_flat = list(flatten(parsed_block_map_true))
        self.assertListEqual(parsed_block_map_flat, parsed_block_map_true_flat)
        grid_map_true_flat = list(flatten(grid_map_true))
        grid_map_flat = [block_map_flat[x[0]] if x is not None else None
                         for x in g2o_b2b_g2g]  # Center from first (X) layer
        self.assertListEqual(grid_map_flat, grid_map_true_flat)


if __name__ == '__main__':
    unittest.main()
