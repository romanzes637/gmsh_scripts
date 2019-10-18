import json
import time
from pprint import pprint
import itertools

import gmsh

from complex import Complex
from support import check_file


class NkmEleronTrench(Complex):
    def __init__(
            self, factory, env_input_path, trench_input_path,
            origin, n_levels, n_tunnels, n_trenches,
            d_tunnel, d_level, d_trench):
        """
        NKM Eleron 2 var 2 layout
        :param str factory: see Primitive
        :param str env_input_path: Environment input path
        :param str trench_input_path: Trench input path
        :param list of float origin: position [x, y, z] of the first borehole
        :param int n_levels: number of horizontal levels
        :param int n_tunnels: number of tunnels per level
        :param int n_trenches: number of trenches per tunnel
        :param float d_tunnel: tunnel step
        :param float d_level: level step
        :param float d_trench: trench step
        """
        from complex_factory import ComplexFactory
        if factory == 'occ':
            factory_object = gmsh.model.occ
        else:
            factory_object = gmsh.model.geo
        complexes = list()
        print('Boreholes')
        result = check_file(trench_input_path)
        with open(result['path']) as f:
            input_data = json.load(f)
        input_data['arguments']['factory'] = factory
        pprint(input_data)
        n_bs = n_levels * n_tunnels * n_trenches * 2
        cnt = 0
        x0, y0, z0 = origin
        for level in range(n_levels):
            z = z0 + level * d_level
            for tunnel in range(n_tunnels):
                x = x0 + tunnel * d_tunnel
                for trench in range(n_trenches):
                    y = y0 + trench * d_trench
                    # Right
                    cnt += 1
                    print('{0}/{1} Level {2} Tunnel {3} Trench {4} Right'.format(
                        cnt, n_bs, z, x, y))
                    new_transform = input_data['arguments']['transform_data']
                    new_transform[0] = x + 13.155 + 2.500
                    new_transform[1] = y
                    new_transform[2] = z - 4.400
                    input_data['arguments']['transform_data'] = new_transform
                    t = ComplexFactory.new(input_data)
                    complexes.append(t)
                    # t0 = time.time()
                    # print('Synchronize')
                    # factory_object.synchronize()
                    # print('Evaluate')
                    # for c in complexes:
                    #     c.evaluate_coordinates()
                    # print('Remove Duplicates')
                    # factory_object.removeAllDuplicates()
                    # print('Synchronize')
                    # factory_object.synchronize()
                    # print(time.time() - t0)
                    # Left
                    cnt += 1
                    print('{0}/{1} Level {2} Tunnel {3} Trench {4} Left'.format(
                        cnt, n_bs, z, x, y))
                    new_transform = input_data['arguments']['transform_data']
                    new_transform[0] = x - 13.155 - 2.500
                    new_transform[1] = y
                    new_transform[2] = z - 4.400
                    input_data['arguments']['transform_data'] = new_transform
                    t2 = ComplexFactory.new(input_data)
                    complexes.append(t2)
                    # t0 = time.time()
                    # print('Synchronize')
                    # factory_object.synchronize()
                    # print('Evaluate')
                    # for c in complexes:
                    #     c.evaluate_coordinates()
                    # print('Remove Duplicates')
                    # factory_object.removeAllDuplicates()
                    # print('Synchronize')
                    # factory_object.synchronize()
                    # print(time.time() - t0)
        # t0 = time.time()
        # print('Synchronize')
        # factory_object.synchronize()
        # print('Evaluate')
        # for c in complexes:
        #     c.evaluate_coordinates()
        # print('Remove Duplicates')
        # factory_object.removeAllDuplicates()
        # print('Synchronize')
        # factory_object.synchronize()
        # print(time.time() - t0)
        print('Environment')
        result = check_file(env_input_path)
        print(result)
        with open(result['path']) as f:
            input_data = json.load(f)
        input_data['arguments']['factory'] = factory
        input_data['arguments']['inner_volumes'] = list(
            itertools.chain.from_iterable([x.get_volumes() for x in complexes]))
        pprint(input_data)
        e = ComplexFactory.new(input_data)
        complexes.append(e)
        primitives = list(itertools.chain.from_iterable(
            [x.primitives for x in complexes]))
        Complex.__init__(self, factory, primitives)
