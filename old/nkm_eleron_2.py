import json
from pprint import pprint
import itertools

import gmsh

from complex import Complex
from support import check_file


class NkmEleron2(Complex):
    def __init__(
            self, factory, env_input_path, borehole_input_path,
            origin, n_levels, n_tunnels, n_boreholes,
            d_tunnel, d_level, dy_borehole, dz_borehole):
        """
        NKM Eleron 2 var 2 layout
        :param str factory: see Primitive
        :param str env_input_path: Environment input path
        :param str borehole_input_path: Borehole input path
        :param list of float origin: position [x, y, z] of the first borehole
        :param int n_levels: number of horizontal levels
        :param int n_tunnels: number of tunnels per level
        :param int n_boreholes: number of n_boreholes per tunnel
        :param float d_tunnel: tunnel step
        :param float d_level: level step
        :param float dy_borehole: borehole Y step
        :param float dz_borehole: borehole Z step
        """
        from complex_factory import ComplexFactory
        if factory == 'occ':
            factory_object = gmsh.model.occ
        else:
            factory_object = gmsh.model.geo
        complexes = list()
        print('Boreholes')
        result = check_file(borehole_input_path)
        with open(result['path']) as f:
            input_data = json.load(f)
        input_data['arguments']['factory'] = factory
        pprint(input_data)
        n_bs = n_levels * n_tunnels * n_boreholes
        cnt = 0
        x0, y0, z0 = origin
        for level in range(n_levels):
            z = z0 + level * d_level
            for tunnel in range(n_tunnels):
                x = x0 + tunnel * d_tunnel
                for borehole in range(n_boreholes):
                    cnt += 1
                    y = y0 + borehole * dy_borehole
                    print('{0}/{1} Level {2} Tunnel {3} Borehole {4}'.format(
                        cnt, n_bs, z, x, y))
                    new_transform = input_data['arguments']['transform_data']
                    new_transform[0] = x
                    new_transform[1] = y
                    new_transform[2] = z + dz_borehole
                    input_data['arguments']['transform_data'] = new_transform
                    b = ComplexFactory.new(input_data)
                    complexes.append(b)
        print('Synchronize')
        factory_object.synchronize()
        print('Evaluate')
        for c in complexes:
            c.evaluate_coordinates()
        print('Remove Duplicates')
        factory_object.removeAllDuplicates()
        print('Synchronize')
        factory_object.synchronize()
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
