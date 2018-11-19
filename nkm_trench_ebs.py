import argparse
import json
import socket
from pprint import pprint
import time
import itertools
import sys
import os

import gmsh
import occ_workarounds as occ_ws
from complex_factory import ComplexFactory
from io import read_complex_type_2_to_complex_primitives
from environment import Environment, NestedEnvironment
from boolean import complex_by_volumes, complex_by_complex, complex_self, \
    sort_object_only_shared_no_tool, sort_object_only_shared_tool_no_shared
from support import auto_complex_points_sizes_min_curve_in_volume, \
    auto_volumes_groups_surfaces, auto_points_sizes, \
    boundary_surfaces_to_six_side_groups, check_file, volumes_groups_surfaces


class TrenchEbsNKM:
    def __init__(
            self, factory, simple_boundary,
            env_input_path, env_name, env_point_data, env_transform_data,
            origin, n_levels, n_tunnels, n_trenches, n_boreholes,
            d_tunnel, d_level, d_trench, dx_borehole, dz_borehole,
            borehole_input_path,
    ):
        """
        NKM model with Intrusions, ILW and HLW Boreholes inside Environment
        :param str factory: see Primitive
        :param bool simple_boundary: Make only 6 boundary surfaces: NX, NY, NZ, X, Y, Z (mandatory True for geo factory)
        :param str env_input_path: Environment input path (Complex class child)
        :param str env_name: Environment physical name
        :param list of float env_point_data: Environment point data (see Primitive)
        :param list of float env_transform_data: Environment center transform (see Primitive)
        :param list of float origin: position [x, y, z] of first trench of first tunnel of first level 
        """
        print('Read Input')
        print('Boreholes')
        result = check_file(borehole_input_path)
        print(result['path'])
        with open(result['path']) as f:
            self.borehole_input = json.load(f)
        pprint(self.borehole_input)
        print('Environment')
        result = check_file(env_input_path)
        print(result['path'])
        with open(result['path']) as f:
            self.env_input = json.load(f)
        pprint(self.env_input)
        print('Initialize')
        self.spent_times = dict()
        self.factory_str = factory
        if factory == 'occ':
            self.factory = gmsh.model.occ
            self.borehole_input['arguments']['factory'] = 'occ'
            self.env_input['arguments']['factory'] = 'occ'
        else:
            self.factory = gmsh.model.geo
            self.borehole_input['arguments']['factory'] = 'geo'
            self.env_input['arguments']['factory'] = 'geo'
        self.env_name = env_name
        self.simple_boundary = simple_boundary
        print('Intrusions')
        print('EBS')
        self.nenvs = list()
        # start_time = time.time()
        # self.ints = []  # Array of ComplexPrimitive arrays
        # for i, fn in enumerate(int_filenames):
        #     print(fn)
        #     self.ints.append(read_complex_type_2_to_complex_primitives(
        #         factory,
        #         fn,
        #         int_divides[i],
        #         int_lcs[i],
        #         int_transforms[i],
        #         int_transfinites[i],
        #         int_names[i]
        #     ))
        # self.spent_times['Initialize Intrusions'] = time.time() - start_time
        print('Boreholes')
        start_time = time.time()
        self.boreholes = list()
        self.boreholes_coordinates = list()
        x0 = origin[0]
        y0 = origin[1]
        z0 = origin[2]
        for level in range(n_levels):
            z = z0 + level * d_level
            print('Level {0}'.format(z))
            for tunnel in range(n_tunnels):
                x = x0 + tunnel * d_tunnel
                for trench in range(n_trenches):
                    y = y0 + trench * d_trench
                    # Left side
                    lbs = list()
                    rbs = list()
                    for borehole in range(n_boreholes):
                        borehole_x = x - 2 * dx_borehole - borehole * dx_borehole
                        new_transform = self.borehole_input['arguments'][
                            'transform_data']
                        new_transform[0] = borehole_x
                        new_transform[1] = y
                        new_transform[2] = z + dz_borehole
                        print(new_transform)
                        self.borehole_input['arguments'][
                            'transform_data'] = new_transform
                        b = ComplexFactory.new(self.borehole_input)
                        self.boreholes.append(b)
                        lbs.append(b)
                        coordinate = [level, tunnel, trench, 0, borehole]
                        self.boreholes_coordinates.append(coordinate)
                    # Right side
                    for borehole in range(n_boreholes):
                        borehole_x = x + 2 * dx_borehole + borehole * dx_borehole
                        new_transform = self.borehole_input['arguments'][
                            'transform_data']
                        new_transform[0] = borehole_x
                        new_transform[1] = y
                        new_transform[2] = z + dz_borehole
                        self.borehole_input['arguments'][
                            'transform_data'] = new_transform
                        b = ComplexFactory.new(self.borehole_input)
                        self.boreholes.append(b)
                        rbs.append(b)
                        coordinate = [level, tunnel, trench, 1, borehole]
                        self.boreholes_coordinates.append(coordinate)

                    # # !!! FACTORY SYNC !!!
                    self.synchronize()
                    for b in lbs:
                        b.evaluate_coordinates()
                        b.evaluate_bounding_box()
                    for b in rbs:
                        b.evaluate_coordinates()
                        b.evaluate_bounding_box()
                    self.remove_duplicates()  # ERROR IF REMOVE
                    self.synchronize()  # ERROR IF REMOVE
                    # # !!! FACTORY SYNC !!!

                    # lengths = [
                    #     (26.700, 1.500, 4.300, 1),
                    #     (28.000, 2.800, 5.400, 1)]
                    lengths = [
                        (26.200, 1.500, 4.100, 1),
                        (27.500, 2.800, 5.400, 1)]
                    physical_names = [
                        'Concrete',
                        'Bentonite'
                    ]
                    # Left side
                    inner_volumes = list()
                    for b in lbs:
                        inner_volumes.extend(b.get_volumes())
                    transforms = [
                        (x - dx_borehole - 13.750, y, z - 2.700),
                        (x - dx_borehole - 13.750, y, z - 2.700)]

                    nenv = NestedEnvironment(self.factory_str, lengths,
                                             transforms, inner_volumes,
                                             physical_names)
                    self.nenvs.append(nenv)
                    # Right side
                    inner_volumes = list()
                    for b in rbs:
                        inner_volumes.extend(b.get_volumes())
                    transforms = [
                        (x + dx_borehole + 13.750, y, z - 2.700),
                        (x + dx_borehole + 13.750, y, z - 2.700)]
                    nenv = NestedEnvironment(self.factory_str, lengths,
                                             transforms, inner_volumes,
                                             physical_names)
                    self.nenvs.append(nenv)
        self.spent_times['Initialize Boreholes'] = time.time() - start_time
        # ilw_n = ilw_nx * ilw_ny
        # est_time = 0
        # times = []
        # time_spent = 0
        # for i in range(ilw_nx):
        #     for j in range(ilw_ny):
        #         start = time.time()
        #         cnt = i * ilw_ny + j + 1
        #         rem = ilw_n - cnt + 1
        #         rem_time = rem * est_time
        #         print('Borehole:{}/{} X:{}/{} Y:{}/{} SpentTime:{:.3f}s RemainingTime:{:.3f}s'.format(
        #             cnt, ilw_n, i + 1, ilw_nx, j + 1, ilw_ny, time_spent, rem_time))
        #         new_ilw_transform = list(ilw_transform)
        #         new_ilw_transform[0] += ilw_dx * i
        #         new_ilw_transform[1] += ilw_dy * j
        #         ilw_input['arguments']['transform_data'] = new_ilw_transform
        #         self.ilws.append(ComplexFactory.new(ilw_input))
        #         times.append(time.time() - start)
        #         print('{:.3f}s'.format(times[-1]))
        #         time_spent += times[-1]
        #         est_time = sum(times) / cnt
        # print('HLW')
        # start_time = time.time()
        # self.hlws = []
        # hlw_n = hlw_nx * hlw_ny
        # est_time = 0
        # times = []
        # time_spent = 0
        # for i in range(hlw_nx):
        #     for j in range(hlw_ny):
        #         start = time.time()
        #         cnt = i * hlw_ny + j + 1
        #         rem = hlw_n - cnt + 1
        #         rem_time = rem * est_time
        #         print('Borehole:{}/{} X:{}/{} Y:{}/{} SpentTime:{:.3f}s RemainingTime:{:.3f}s'.format(
        #             cnt, hlw_n, i + 1, hlw_nx, j + 1, hlw_ny, time_spent, rem_time))
        #         new_hlw_transform = list(hlw_transform)
        #         new_hlw_transform[0] += hlw_dx * i
        #         new_hlw_transform[1] += hlw_dy * j
        #         hlw_input['arguments']['transform_data'] = new_hlw_transform
        #         self.hlws.append(ComplexFactory.new(hlw_input))
        #         times.append(time.time() - start)
        #         print('{:.3f}s'.format(times[-1]))
        #         time_spent += times[-1]
        #         est_time = sum(times) / cnt
        # self.spent_times['Initialize HLW'] = time.time() - start_time
        print('Environment')
        start_time = time.time()
        self.env_point_data = env_point_data
        self.env_transform = env_transform_data
        if self.factory == gmsh.model.occ:
            self.env_input['arguments']['point_data'] = self.env_point_data
            self.env_input['arguments']['transform_data'] = self.env_transform
            self.env = ComplexFactory.new(self.env_input)
        self.spent_times['Initialize Environment'] = time.time() - start_time

    def environment(self):
        print('Environment')
        start_time = time.time()
        lx = self.env_point_data[0]
        ly = self.env_point_data[1]
        lz = self.env_point_data[2]
        lc = self.env_point_data[3]
        inner_surfaces = auto_volumes_groups_surfaces()
        self.env = Environment(self.factory_str, lx, ly, lz, lc,
                               self.env_transform, inner_surfaces,
                               self.env_name)
        self.spent_times['Environment'] = time.time() - start_time

    def evaluate(self):
        print('Evaluating')
        start_time = time.time()
        # print('Intrusions')
        # for intrusion in self.ints:
        #     for c in intrusion:
        #         c.evaluate_coordinates()
        #         c.evaluate_bounding_box()
        print('Boreholes')
        for b in self.boreholes:
            b.evaluate_coordinates()
            b.evaluate_bounding_box()
        if self.factory == gmsh.model.occ:
            print('Environment')
            self.env.evaluate_coordinates()
            self.env.evaluate_bounding_box()
        self.spent_times['Evaluating'] = time.time() - start_time

    def boolean_intrusions(self):
        print('Intrusions Inner')
        start_time = time.time()
        for intrusion in self.ints:
            for c in intrusion:
                complex_self(self.factory, c)
        self.spent_times['In Ints'] = time.time() - start_time
        print('Intrusions By Intrusions')
        start_time = time.time()
        combinations = list(itertools.combinations(range(len(self.ints)), 2))
        for combination in combinations:
            print('{} by {}'.format(combination[0], combination[1]))
            for c0 in self.ints[combination[0]]:
                for c1 in self.ints[combination[1]]:
                    complex_by_complex(self.factory, c0, c1)
        self.spent_times['Ints by Ints'] = time.time() - start_time

    def boolean_intrusions_by_boreholes(self):
        print('Cut')
        print('Intrusions By ILW Boreholes')
        start_time = time.time()
        for i, b in enumerate(self.ilws):
            for j, intrusion in enumerate(self.ints):
                for k, c in enumerate(intrusion):
                    print(
                        'Borehole:{}/{} Intrusion:{}/{} IntrusionPart:{}/{}'.format(
                            i + 1, len(self.ilws), j + 1, len(self.ints), k + 1,
                            len(intrusion)))
                    b_volumes = c.get_volumes()
                    complex_by_volumes(self.factory, c, b_volumes,
                                       remove_tool=False,
                                       sort_function=sort_object_only_shared_no_tool)
        self.spent_times['Ints By ILW Cut'] = time.time() - start_time
        print('Intrusions By HLW Boreholes')
        start_time = time.time()
        for i, b in enumerate(self.hlws):
            for j, intrusion in enumerate(self.ints):
                for k, c in enumerate(intrusion):
                    print(
                        'Borehole:{}/{} Intrusion:{}/{} IntrusionPart:{}/{}'.format(
                            i + 1, len(self.ilws), j + 1, len(self.ints), k + 1,
                            len(intrusion)))
                    b_volumes = c.get_volumes()
                    complex_by_volumes(self.factory, c, b_volumes,
                                       remove_tool=False,
                                       sort_function=sort_object_only_shared_no_tool)
        self.spent_times['Ints By HLW Cut'] = time.time() - start_time
        print('Bool')
        print('Intrusions By ILW Boreholes')
        start_time = time.time()
        for i, b in enumerate(self.ilws):
            for j, intrusion in enumerate(self.ints):
                for k, c in enumerate(intrusion):
                    print(
                        'Borehole:{}/{} Intrusion:{}/{} IntrusionPart:{}/{}'.format(
                            i + 1, len(self.ilws), j + 1, len(self.ints), k + 1,
                            len(intrusion)))
                    complex_by_complex(self.factory, c, b)
        self.spent_times['Ints By ILW'] = time.time() - start_time
        print('Intrusions By HLW Boreholes')
        start_time = time.time()
        for i, b in enumerate(self.hlws):
            for j, intrusion in enumerate(self.ints):
                for k, c in enumerate(intrusion):
                    print(
                        'Borehole:{}/{} Intrusion:{}/{} IntrusionPart:{}/{}'.format(
                            i + 1, len(self.ilws), j + 1, len(self.ints), k + 1,
                            len(intrusion)))
                    complex_by_complex(self.factory, c, b)
        self.spent_times['Ints By HLW'] = time.time() - start_time

    def boolean_environment(self):
        if len(self.env.primitives) == 1:
            print('Intrusions By Environment')
            start_time = time.time()
            for i, intrusion in enumerate(self.ints):
                print('Intrusion:{}/{}'.format(i + 1, len(self.ints)))
                for c in intrusion:
                    complex_by_complex(self.factory, c, self.env,
                                       sort_function=sort_object_only_shared_tool_no_shared,
                                       pre_boolean=False)
            self.spent_times['Ints By Env'] = time.time() - start_time
            print('ILW Boreholes By Environment')
            start_time = time.time()
            for i, b in enumerate(self.ilws):
                print('Borehole:{}/{}'.format(i + 1, len(self.ilws)))
                complex_by_complex(self.factory, b, self.env,
                                   sort_function=sort_object_only_shared_tool_no_shared,
                                   pre_boolean=False)
            self.spent_times['ILW By Env'] = time.time() - start_time
            print('HLW Boreholes By Environment')
            start_time = time.time()
            for i, b in enumerate(self.hlws):
                print('Borehole:{}/{}'.format(i + 1, len(self.hlws)))
                complex_by_complex(self.factory, b, self.env,
                                   sort_function=sort_object_only_shared_tool_no_shared,
                                   pre_boolean=False)
        else:
            print('Cut')
            e_volumes = self.env.get_volumes()
            print('Environment By Intrusions')
            start_time = time.time()
            for i, intrusion in enumerate(self.ints):
                print('Intrusion:{}/{}'.format(i + 1, len(self.ints)))
                for c in intrusion:
                    complex_by_volumes(self.factory, c, e_volumes,
                                       remove_tool=False,
                                       sort_function=sort_object_only_shared_no_tool)
            self.spent_times['Env By Ints Cut'] = time.time() - start_time
            print('Environment By ILW Boreholes')
            start_time = time.time()
            for i, b in enumerate(self.ilws):
                print('Borehole:{}/{}'.format(i + 1, len(self.ilws)))
                complex_by_volumes(self.factory, b, e_volumes,
                                   remove_tool=False,
                                   sort_function=sort_object_only_shared_no_tool)
            self.spent_times['Env By Ilw Cut'] = time.time() - start_time
            print('Environment By HLW Boreholes')
            start_time = time.time()
            for i, b in enumerate(self.hlws):
                print('Borehole:{}/{}'.format(i + 1, len(self.hlws)))
                complex_by_volumes(self.factory, b, e_volumes,
                                   remove_tool=False,
                                   sort_function=sort_object_only_shared_no_tool)
            self.spent_times['Env By Hlw Cut'] = time.time() - start_time
            print('Bool')
            print('Environment By Intrusions')
            start_time = time.time()
            for i, intrusion in enumerate(self.ints):
                print('Intrusion:{}/{}'.format(i + 1, len(self.ints)))
                for c in intrusion:
                    complex_by_complex(self.factory, self.env, c)
            self.spent_times['Env By Ints'] = time.time() - start_time
            print('Environment By ILW Boreholes')
            start_time = time.time()
            for i, b in enumerate(self.ilws):
                print('Borehole:{}/{}'.format(i + 1, len(self.ilws)))
                complex_by_complex(self.factory, self.env, b)
            self.spent_times['Env By Ilw'] = time.time() - start_time
            print('Environment By HLW Boreholes')
            start_time = time.time()
            for i, b in enumerate(self.hlws):
                print('Borehole:{}/{}'.format(i + 1, len(self.hlws)))
                complex_by_complex(self.factory, self.env, b)
            self.spent_times['Env By Hlw'] = time.time() - start_time

    def remove_duplicates(self):
        print('Remove Duplicates')
        start_time = time.time()
        self.factory.removeAllDuplicates()
        self.spent_times['Removing Duplicates'] = time.time() - start_time

    def synchronize(self):
        print('Synchronize')
        start_time = time.time()
        self.factory.synchronize()
        delta_time = time.time() - start_time
        self.spent_times.setdefault('Synchronize', delta_time) + delta_time

    def correct_and_transfinite(self):
        print('Correct and Transfinite')
        start_time = time.time()
        cs = set()
        ss = set()
        # print('Intrusions')
        # for i in self.ints:
        #     for c in i:
        #         occ_ws.correct_and_transfinite_complex(c, ss, cs)
        print('Boreholes')
        for b in self.boreholes:
            occ_ws.correct_and_transfinite_complex(b, ss, cs)
        # print('HLW Boreholes')
        # for b in self.hlws:
        #     occ_ws.correct_and_transfinite_complex(b, ss, cs)
        if self.factory == gmsh.model.occ:
            print('Environment')
            occ_ws.correct_and_transfinite_complex(self.env, ss, cs)
        self.spent_times['Correct And Transfinite'] = time.time() - start_time

    def set_sizes(self):
        print('Set Sizes')
        start_time = time.time()
        # pss = auto_points_sizes()  # Very small size of environment points
        pss = dict()
        print('Intrusions')
        for intrusion in self.ints:
            for c in intrusion:
                auto_complex_points_sizes_min_curve_in_volume(c, pss)
        print('ILW Boreholes')
        for b in self.ilws:
            auto_complex_points_sizes_min_curve_in_volume(b, pss)
        print('HLW Boreholes')
        for b in self.hlws:
            auto_complex_points_sizes_min_curve_in_volume(b, pss)
        print('Environment')
        # auto_complex_points_sizes_min_curve_in_volume(self.env, pss)  # Very small size of environment points
        # pprint(pss)
        if len(pss) > 0:
            max_size_key = max(pss.keys(), key=(lambda x: pss[x]))
            min_size_key = min(pss.keys(), key=(lambda x: pss[x]))
            print('Maximum Point: {0}, Value: {1}'.format(max_size_key,
                                                          pss[max_size_key]))
            print('Minimum Point: {0}, Value: {1}'.format(min_size_key,
                                                          pss[min_size_key]))
        self.spent_times['Set Sizes'] = time.time() - start_time

    def smooth(self, dim, n):
        print('Smooth')
        start_time = time.time()
        print('Intrusions')
        for i in self.ints:
            for c in i:
                c.smooth(dim, n)
        print('ILW Boreholes')
        for b in self.ilws:
            b.smooth(dim, n)
        print('HLW Boreholes')
        for b in self.hlws:
            b.smooth(dim, n)
        print('Environment')
        if self.factory == gmsh.model.occ:
            self.env.smooth(dim, n)
        self.spent_times['Smooth'] = time.time() - start_time

    def physical_volumes(self):
        print('Physical Volumes')
        start_time = time.time()
        print('Boreholes')
        if len(self.boreholes) > 0:
            local_names = self.boreholes[
                0].map_physical_name_to_primitives_indices.keys()
            levels_boreholes = dict()
            for i, c in enumerate(self.boreholes_coordinates):
                levels_boreholes.setdefault(c[0], list()).append(i)
            # print(levels_boreholes)
            for local_name in local_names:
                for level, bs in levels_boreholes.items():
                    vs = set()
                    for b in bs:
                        bvs = self.boreholes[b].get_volumes_by_physical_name(
                            local_name)
                        vs.update(bvs)
                    tag = gmsh.model.addPhysicalGroup(3, list(vs))
                    level_name = 'Level{0}'.format(level)
                    gmsh.model.setPhysicalName(3, tag, '_'.join(
                        [local_name, level_name]))
        print('Environment')
        if self.factory == gmsh.model.occ:
            for local_name in self.env.map_physical_name_to_primitives_indices.keys():
                vs = self.env.get_volumes_by_physical_name(local_name)
                tag = gmsh.model.addPhysicalGroup(3, vs)
                if local_name == '':
                    gmsh.model.setPhysicalName(3, tag, self.env_name)
                else:
                    gmsh.model.setPhysicalName(3, tag, '_'.join(
                        [self.env_name, local_name]))
        else:
            tag = gmsh.model.addPhysicalGroup(3, self.env.volumes)
            gmsh.model.setPhysicalName(3, tag, self.env_name)
        print('EBS')
        if self.factory == gmsh.model.occ:
            pass
        else:
            n = len(self.nenvs[0].envs)
            vs_i = dict()
            for nenv in self.nenvs:
                nvs = nenv.get_nested_volumes()
                nns = nenv.get_nested_physical_names()
                for i, vs in enumerate(nvs):
                    vs_i.setdefault(nns[i], []).extend(vs)
            for k, v in vs_i.items():
                tag = gmsh.model.addPhysicalGroup(3, v)
                gmsh.model.setPhysicalName(3, tag, k)
        self.spent_times['Physical Volumes'] = time.time() - start_time

    def physical_surfaces(self):
        print('Physical Surfaces')
        start_time = time.time()
        print("Evaluate Boundary Surfaces")
        boundary_surfaces_groups = boundary_surfaces_to_six_side_groups()
        if not self.simple_boundary:
            print("Evaluate Map From Surface To Physical Name")
            map_surface_to_physical_name = dict()
            print("Intrusions")
            for i in self.ints:
                for c in i:
                    for physical_name in c.map_physical_name_to_primitives_indices:
                        surfaces = c.get_surfaces_by_physical_name(
                            physical_name)
                        for s in surfaces:
                            map_surface_to_physical_name[s] = physical_name
            print("ILW Boreholes")
            for b in self.ilws:
                for physical_name in b.map_physical_name_to_primitives_indices:
                    surfaces = b.get_surfaces_by_physical_name(physical_name)
                    for s in surfaces:
                        map_surface_to_physical_name[s] = '_'.join(
                            [self.ilw_name, physical_name])
            print("HLW Boreholes")
            for b in self.hlws:
                for physical_name in b.map_physical_name_to_primitives_indices:
                    surfaces = b.get_surfaces_by_physical_name(physical_name)
                    for s in surfaces:
                        map_surface_to_physical_name[s] = '_'.join(
                            [self.hlw_name, physical_name])
            print("Environment")
            for physical_name in self.env.map_physical_name_to_primitives_indices:
                surfaces = self.env.get_surfaces_by_physical_name(physical_name)
                for s in surfaces:
                    if physical_name == '':
                        map_surface_to_physical_name[s] = self.env_name
                    else:
                        map_surface_to_physical_name[s] = '_'.join(
                            [self.env_name, physical_name])
            print('Make Physical Surfaces')
            for i, (name, ss) in enumerate(boundary_surfaces_groups.items()):
                map_expanded_physical_name_to_surfaces = dict()
                for s in ss:
                    physical_name = '_'.join(
                        [name, map_surface_to_physical_name[s]])
                    map_expanded_physical_name_to_surfaces.setdefault(
                        physical_name, list()).append(s)
                for j, (epn, ess) in enumerate(
                        map_expanded_physical_name_to_surfaces.items()):
                    tag = gmsh.model.addPhysicalGroup(2, ess)
                    gmsh.model.setPhysicalName(2, tag, epn)
        else:
            for i, (name, ss) in enumerate(boundary_surfaces_groups.items()):
                tag = gmsh.model.addPhysicalGroup(2, ss)
                gmsh.model.setPhysicalName(2, tag, name)
        self.spent_times['Physical Surfaces'] = time.time() - start_time


if __name__ == '__main__':
    spent_times = {}
    global_start_time = time.time()
    print('Start time: {0}'.format(time.asctime(time.localtime(time.time()))))
    print('Python: {0}'.format(sys.executable))
    print('Python Version: {0}'.format(sys.version))
    print('Script: {0}'.format(__file__))
    print('Working Directory: {0}'.format(os.getcwd()))
    print('Host: {0}'.format(socket.gethostname()))
    print('PID: {0}'.format(os.getpid()))
    print('CMD Arguments')
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--input', help='input filename', required=True)
    parser.add_argument('-o', '--output', help='output filename')
    parser.add_argument('-v', '--verbose', help='verbose', action='store_true')
    parser.add_argument('-t', '--test', help='test mode', action='store_true')
    args = parser.parse_args()
    root, extension = os.path.splitext(args.input)
    basename = os.path.basename(root)
    print(args)
    if args.output is None:
        output_root = basename
    else:
        output_root = args.output
    is_test = args.test
    is_verbose = args.verbose
    input_path = args.input
    model_name = basename
    is_test = args.test
    is_verbose = args.verbose
    if is_test:
        output_path = output_root + '.brep'
    else:
        output_path = output_root + '.msh'
    print('Input path: ' + input_path)
    print('Output path: ' + output_path)
    gmsh.initialize()
    gmsh.model.add(model_name)
    print('Gmsh model name: ' + gmsh.model.__name__)
    print('Gmsh options')
    gmsh.option.setNumber('Geometry.AutoCoherence', 0)  # For geo factory
    print('Geometry.AutoCoherence: {}'.format(
        gmsh.option.getNumber('Geometry.AutoCoherence')))
    if is_verbose:
        gmsh.option.setNumber('General.Terminal', 1)
    else:
        gmsh.option.setNumber('General.Terminal', 0)
    print(
        'General.Terminal: {}'.format(
            gmsh.option.getNumber('General.Terminal')))
    # (1=Delaunay, 2=New Delaunay, 4=Frontal, 5=Frontal Delaunay, 6=Frontal Hex, 7=MMG3D, 9=R-tree)
    gmsh.option.setNumber('Mesh.Algorithm3D', 4)
    print(
        'Mesh.Algorithm3D: {}'.format(
            gmsh.option.getNumber('Mesh.Algorithm3D')))
    print('Input')
    with open(input_path) as f:
        input_nkm = json.load(f)
    pprint(input_nkm)
    factory_str = input_nkm['arguments']['factory']
    print('Initialize')
    nkm = TrenchEbsNKM(**input_nkm['arguments'])
    # nkm.synchronize()
    if not is_test:
        if factory_str == 'occ':
            nkm.evaluate()
            nkm.boolean_intrusions()
            nkm.boolean_intrusions_by_boreholes()
            nkm.boolean_environment()
            nkm.remove_duplicates()
            nkm.synchronize()
            nkm.set_sizes()
            nkm.correct_and_transfinite()
            nkm.physical_volumes()
            nkm.physical_surfaces()
        else:
            # nkm.evaluate()
            # nkm.remove_duplicates()
            # nkm.synchronize()
            nkm.environment()
            nkm.synchronize()
            nkm.correct_and_transfinite()
            nkm.physical_volumes()
            nkm.physical_surfaces()
        spent_times.update(nkm.spent_times)
        print('Mesh')
        start_time = time.time()
        gmsh.model.mesh.generate(3)
        gmsh.model.mesh.removeDuplicateNodes()
        spent_times['Mesh'] = time.time() - start_time
    print('Write')
    start_time = time.time()
    gmsh.write(output_path)
    spent_times['Write'] = time.time() - start_time
    gmsh.finalize()
    spent_times['Total'] = time.time() - global_start_time
    pprint(spent_times)
    print('End time: {}'.format(time.asctime(time.localtime(time.time()))))
