import unittest
from pprint import pprint
import logging

import numpy as np

from point import Point, parse_grid
from point import parse_grid_row
from coordinate_system import str2obj as cs_factory
from support import LoggingDecorator, flatten

global_rng = np.random.default_rng()


class TestPoint(unittest.TestCase):

    def test_one(self):
        seed = global_rng.integers(0, 100500)
        # seed = 725
        rng = np.random.default_rng(seed)
        logging.info(f'seed: {seed}')

        ms = rng.uniform(0.01, 100)  # mesh size
        cs = rng.choice(list(cs_factory.keys()))  # coordinate system
        z = '-'.join(rng.choice(list('abc'), rng.integers(1, 7)))  # zone
        dim = cs_factory[cs]().dim
        xs = rng.uniform(-100, 100, dim) if dim is not None else []
        logging.info(f'coordinate system: {cs}')
        logging.info(f'dim: {dim}')
        logging.info(f'coordinates: {xs}')
        logging.info(f'mesh size: {ms}')
        logging.info(f'zone: {z}')

        if dim == 3:  # Cartesian only
            a = [*xs]
            p = Point(a)
            self.assertTrue(np.allclose(p.coordinates, xs))

            a = [*xs, ms]
            p = Point(a)
            self.assertTrue(np.allclose(p.coordinates, xs))
            self.assertEqual(p.kwargs['meshSize'], ms)

            a = [*xs, z]
            p = Point(a)
            self.assertTrue(np.allclose(p.coordinates, xs))
            self.assertEqual(p.zone, z)

            a = [*xs, ms, z]
            p = Point(a)
            self.assertTrue(np.allclose(p.coordinates, xs))
            self.assertEqual(p.kwargs['meshSize'], ms)
            self.assertEqual(p.zone, z)

        a = [*xs, cs]
        p = Point(a)
        self.assertTrue(np.allclose(p.coordinates, xs))
        self.assertTrue(isinstance(p.coordinate_system, cs_factory[cs]))

        a = [*xs, ms, cs]
        p = Point(a)
        self.assertTrue(np.allclose(p.coordinates, xs))
        self.assertEqual(p.kwargs['meshSize'], ms)
        self.assertTrue(isinstance(p.coordinate_system, cs_factory[cs]))

        a = [*xs, cs, z]
        p = Point(a)
        self.assertTrue(np.allclose(p.coordinates, xs))
        self.assertTrue(isinstance(p.coordinate_system, cs_factory[cs]))
        self.assertEqual(p.zone, z)

        a = [*xs, ms, cs, z]
        p = Point(a)
        self.assertTrue(np.allclose(p.coordinates, xs))
        self.assertEqual(p.kwargs['meshSize'], ms)
        self.assertTrue(isinstance(p.coordinate_system, cs_factory[cs]))
        self.assertEqual(p.zone, z)

    def test_many(self):
        seed = global_rng.integers(0, 100500)
        # seed = 27102
        rng = np.random.default_rng(seed)
        logging.info(f'seed: {seed}')

        n_points = rng.integers(0, 1000)
        logging.info(f'n_points: {n_points}')
        g_ms = rng.uniform(0.01, 100)  # mesh size
        g_cs = rng.choice(list(cs_factory.keys()))  # coordinate system
        g_z = '-'.join(rng.choice(list('abc'), rng.integers(1, 7)))  # zone
        g_dim = cs_factory[g_cs]().dim
        logging.info(f'coordinate system: {g_cs}')
        logging.info(f'dim: {g_dim}')
        logging.info(f'mesh size: {g_ms}')
        logging.info(f'zone: {g_z}')
        raw_points = []
        for _ in range(n_points):
            ms = rng.uniform(0.01, 100)  # mesh size
            cs = rng.choice(list(cs_factory.keys()))  # coordinate system
            z = '-'.join(rng.choice(list('abc'), rng.integers(1, 7)))  # zone
            dim = cs_factory[cs]().dim
            xs = rng.uniform(-100, 100, dim) if dim is not None else []
            do_list = rng.integers(0, 2)
            if do_list:
                if dim == 3:  # Cartesian only
                    if g_dim == dim:
                        p = rng.choice([[*xs],
                                        [*xs, ms],
                                        [*xs, z],
                                        [*xs, ms, z]])
                    else:
                        p = rng.choice([[*xs, cs],
                                        [*xs, ms, cs],
                                        [*xs, cs, z],
                                        [*xs, ms, cs, z]])
                else:
                    p = rng.choice([[*xs, cs],
                                    [*xs, ms, cs],
                                    [*xs, cs, z],
                                    [*xs, ms, cs, z]])
            else:  # do dict
                if dim == 3:  # Cartesian only
                    if g_dim == dim:
                        p = rng.choice([{'coordinates': xs},
                                        {'coordinates': xs,
                                         'meshSize': ms},
                                        {'coordinates': xs,
                                         'zone': z},
                                        {'coordinates': xs,
                                         'zone': z,
                                         'meshSize': ms}])
                    else:
                        p = rng.choice([{'coordinates': xs,
                                         'coordinate_system': cs},
                                        {'coordinates': xs,
                                         'meshSize': ms,
                                         'coordinate_system': cs},
                                        {'coordinates': xs,
                                         'coordinate_system': cs,
                                         'zone': z},
                                        {'coordinates': xs,
                                         'meshSize': ms,
                                         'coordinate_system': cs,
                                         'zone': z}])
                else:
                    p = rng.choice([{'coordinates': xs,
                                     'coordinate_system': cs},
                                    {'coordinates': xs,
                                     'meshSize': ms,
                                     'coordinate_system': cs},
                                    {'coordinates': xs,
                                     'coordinate_system': cs,
                                     'zone': z},
                                    {'coordinates': xs,
                                     'meshSize': ms,
                                     'coordinate_system': cs,
                                     'zone': z}])
            raw_points.append(p)
        raw_points = rng.choice([raw_points,
                                 raw_points + [g_ms],
                                 raw_points + [g_cs],
                                 raw_points + [g_z],
                                 raw_points + [g_ms, g_cs],
                                 raw_points + [g_cs, g_z],
                                 raw_points + [g_ms, g_z],
                                 raw_points + [g_ms, g_cs, g_z]])
        points = Point.parse_points(raw_points)
        self.assertEqual(len(points), n_points)
        for i, p in enumerate(points):
            print(i, p.coordinate_system, p.coordinates)
            self.assertEqual(p.coordinate_system.dim, len(p.coordinates))

    def test_random(self):
        n_tests = 42
        for _ in range(n_tests):
            self.test_one()
            self.test_many()

    @LoggingDecorator()
    def test_parse_grid_row(self):
        logging.info('1')
        row = ['v;p', -3.3, -1, 0, 1.1, 4]
        logging.info(f'row: {row}')
        bs = [0, 1, 2, 3]
        new_bs_true = [0, 1, 2, 3]
        logging.info(f'blocks: {bs}')
        rs = parse_grid_row(row)
        new2old_b2b = rs[-1]
        new_bs = [bs[x] for x in new2old_b2b]
        self.assertListEqual(new_bs_true, new_bs)

        logging.info('2')
        row = ['i;p', -3.3, -1, 0, 1.1, 4]
        logging.info(f'row: {row}')
        bs = [0, 1, 2, 3]
        new_bs_true = [0, 1, 2, 3]
        logging.info(f'blocks: {bs}')
        rs = parse_grid_row(row)
        new2old_b2b = rs[-1]
        new_bs = [bs[x] for x in new2old_b2b]
        self.assertListEqual(new_bs_true, new_bs)

        logging.info('3')
        row = ['v;s', -3.3, '-1:2', 0, 1.1, 4]
        logging.info(f'row: {row}')
        bs = [0, 1, 2, 3]
        new_bs_true = [0, 1, 2, 3]
        logging.info(f'blocks: {bs}')
        rs = parse_grid_row(row)
        new2old_b2b = rs[-1]
        new_bs = [bs[x] for x in new2old_b2b]
        self.assertListEqual(new_bs_true, new_bs)

        logging.info('4')
        row = ['v;s', -3.3, '-1:3', 0, 1.1, 4]
        logging.info(f'row: {row}')
        bs = [0, 1, 2, 3]
        new_bs_true = [0, 0, 1, 2, 3]
        cs_true = [-3.3, -2.15, -1, 0, 1.1, 4]
        logging.info(f'blocks: {bs}')
        rs = parse_grid_row(row)
        new2old_b2b = rs[-1]
        new_bs = [bs[x] for x in new2old_b2b]
        self.assertListEqual(new_bs_true, new_bs)
        cs = rs[1]
        self.assertListEqual(cs_true, cs)

        logging.info('5')
        row = ['v;s', -3.3, '-1:3;3.', 0, 1.1, 4]
        logging.info(f'row: {row}')
        bs = [0, 1, 2, 3]
        new_bs_true = [0, 0, 1, 2, 3]
        ms_true = [None, 3, 3, None, None, None]
        logging.info(f'blocks: {bs}')
        rs = parse_grid_row(row)
        new2old_b2b = rs[-1]
        new_bs = [bs[x] for x in new2old_b2b]
        self.assertListEqual(new_bs_true, new_bs)
        ms = rs[2]
        self.assertListEqual(ms_true, ms)

        logging.info('6')
        row = ['v;s', -3.3, '-1:3;3.;4', 0, 1.1, 4]
        logging.info(f'row: {row}')
        bs = [0, 1, 2, 3]
        new_bs_true = [0, 0, 1, 2, 3]
        ms_true = [None, 3, 3, None, None, None]
        ss_true = [None, [4, 0, 1], [4, 0, 1], None, None, None]
        logging.info(f'blocks: {bs}')
        rs = parse_grid_row(row)
        new2old_b2b = rs[-1]
        new_bs = [bs[x] for x in new2old_b2b]
        self.assertListEqual(new_bs_true, new_bs)
        ms = rs[2]
        self.assertListEqual(ms_true, ms)
        ss = rs[3]
        self.assertListEqual(ss_true, ss)

        logging.info('7')
        row = ['v;s', -3.3, '-1:3;3.;4', 0, '1.1:3;4.;5:1:1.2', 4]
        logging.info(f'row: {row}')
        bs = [0, 1, 2, 3]
        new_bs_true = [0, 0, 1, 2, 2, 3]
        ms_true = [None, 3., 3., None, 4., 4., None]
        ss_true = [None, [4, 0, 1], [4, 0, 1], None, [5, 1, 1.2], [5, 1, 1.2], None]
        logging.info(f'blocks: {bs}')
        rs = parse_grid_row(row)
        new2old_b2b = rs[-1]
        new_bs = [bs[x] for x in new2old_b2b]
        self.assertListEqual(new_bs_true, new_bs)
        ms = rs[2]
        self.assertListEqual(ms_true, ms)
        ss = rs[3]
        self.assertListEqual(ss_true, ss)

        logging.info('8')
        row = ['v;s', -3.3, '-1:4:0.5:0.5', 0, 1.1, 4]
        logging.info(f'row: {row}')
        bs = [0, 1, 2, 3]
        new_bs_true = [0, 0, 0, 1, 2, 3]
        cs_true = [-3.3, -2.4010554433227367, -1.8987877789497376,
                   -1, 0, 1.1, 4]
        logging.info(f'blocks: {bs}')
        rs = parse_grid_row(row)
        new2old_b2b = rs[-1]
        new_bs = [bs[x] for x in new2old_b2b]
        self.assertListEqual(new_bs_true, new_bs)
        new_cs = rs[1]
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
        rs = parse_grid_row(row)
        new2old_b2b = rs[-1]
        new_bs = [bs[x] for x in new2old_b2b]
        self.assertListEqual(new_bs_true, new_bs)
        cs = rs[1]
        self.assertListEqual(cs_true, cs)
        ms = rs[2]
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
        new_b_nd_true = [[[0,  1,  1,  2],
                          [3,  4,  4,  5],
                          [6,  7,  7,  8]],
                         [[9,  10, 10, 11],
                          [12, 13, 13, 14],
                          [15, 16, 16, 17]],
                         [[9,  10, 10, 11],
                          [12, 13, 13, 14],
                          [15, 16, 16, 17]]]
        new_b_1d_true = list(flatten(new_b_nd_true))
        grid = [[-3.3, -1, '1.1:3', 4],
                ['i;p', -3.3, -1, 0, 4],
                ['v;s', -3.3, '-1:3'],
                ['i;s', -3.3, '4:3'],
                'cartesian',
                0.7]
        new_grid, values, maps = parse_grid(grid)
        n2o_b2b = maps[-1]
        new_b_1d = [old_b_1d[x] for x in n2o_b2b]
        self.assertListEqual(new_b_1d, new_b_1d_true)
        n_b2b_g2l = maps[-2]
        shape = np.array([list(x) for x in n_b2b_g2l]).max(axis=0)
        shape = [x + 1 for x in shape]
        new_b_nd = np.array(new_b_1d).reshape(shape).tolist()
        self.assertListEqual(new_b_nd, new_b_nd_true)


if __name__ == '__main__':
    unittest.main()
