import unittest
from pprint import pprint
import logging

import numpy as np

from point import Point
from coordinate_system import str2obj as cs_factory

global_rng = np.random.default_rng()

logging.basicConfig(level=logging.INFO)


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


if __name__ == '__main__':
    unittest.main()
