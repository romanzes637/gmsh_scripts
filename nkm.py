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
from environment import Environment
from boolean import complex_by_volumes, complex_by_complex, complex_self, \
    sort_object_only_shared_no_tool, sort_object_only_shared_tool_no_shared
from support import auto_complex_points_sizes_min_curve_in_volume, auto_volumes_groups_surfaces, auto_points_sizes, \
    boundary_surfaces_to_six_side_groups, check_file


class NKM:
    def __init__(
            self, factory,
            env_input_path, env_name, env_transform,
            int_filenames, int_transforms, int_names, int_lcs, int_divides, int_transfinites,
            ilw_input_path, ilw_name, ilw_transform, ilw_nx, ilw_ny, ilw_dx, ilw_dy,
            hlw_input_path, hlw_name, hlw_transform, hlw_nx, hlw_ny, hlw_dx, hlw_dy, simple_boundary):
        """
        NKM model with Intrusions, ILW and HLW Boreholes inside Environment
        :param str factory: see Primitive
        :param str env_input_path: Environment input path (Complex class child)
        :param str env_name: Environment physical name
        :param list of float env_transform: Environment center transform (see Primitive)
        :param list of str int_filenames: Intrusions filenames (Complex Type 2, see io.py)
        :param list of list of float int_transforms: Intrusions transforms (see Primitive)
        :param list of str int_names: Intrusions physical names
        :param list of float int_lcs: Intrusions characteristic lengths (no effect, if set_sizes method has been called)
        :param list of list of int int_divides: Intrusions number of divide parts (see ComplexPrimitive)
        :param list of list of float int_transfinites: Intrusions transfinites (see ComplexPrimitive)
        :param str ilw_input_path: ILW Boreholes input path (Complex class child)
        :param str ilw_name: ILW Boreholes physical name prefix
        :param list of float ilw_transform: ILW Boreholes transform (First ILW Borehole position) see Primitive
        :param int ilw_nx: Number of ILW Boreholes x
        :param int ilw_ny: Number of ILW Boreholes y
        :param float ilw_dx: Interval of ILW Boreholes x
        :param float ilw_dy: Interval of ILW Boreholes y
        :param str hlw_input_path: HLW Boreholes input path (Complex class child)
        :param str hlw_name: HLW Boreholes physical name prefix
        :param list of float hlw_transform: HLW Boreholes transform (First HLW Borehole position) see Primitive
        :param int hlw_nx: Number of HLW Boreholes x
        :param int hlw_ny: Number of HLW Boreholes y
        :param float hlw_dx: Interval of HLW Boreholes x
        :param float hlw_dy: Interval of HLW Boreholes y
        :param bool simple_boundary: Make only 6 boundary surfaces: NX, NY, NZ, X, Y, Z (mandatory True for geo factory)
        """
        print('Read Input')
        print('ILW')
        result = check_file(ilw_input_path)
        print(result['path'])
        with open(result['path']) as ilw_input_file:
            ilw_input = json.load(ilw_input_file)
        pprint(ilw_input)
        print('HLW')
        result = check_file(hlw_input_path)
        print(result['path'])
        with open(result['path']) as hlw_input_file:
            hlw_input = json.load(hlw_input_file)
        pprint(hlw_input)
        print('Environment')
        result = check_file(env_input_path)
        print(result['path'])
        with open(result['path']) as env_input_file:
            env_input = json.load(env_input_file)
        pprint(env_input)
        print('Initialize')
        self.spent_times = {}
        self.factory_str = factory
        if factory == 'occ':
            self.factory = gmsh.model.occ
            ilw_input['arguments']['factory'] = 'occ'
            hlw_input['arguments']['factory'] = 'occ'
            env_input['arguments']['factory'] = 'occ'
        else:
            self.factory = gmsh.model.geo
            ilw_input['arguments']['factory'] = 'geo'
            hlw_input['arguments']['factory'] = 'geo'
            env_input['arguments']['factory'] = 'geo'
        self.int_names = int_names
        self.ilw_name = ilw_name
        self.hlw_name = hlw_name
        self.env_name = env_name
        self.simple_boundary = simple_boundary
        print('Intrusions')
        start_time = time.time()
        self.ints = []  # Array of ComplexPrimitive arrays
        for i, fn in enumerate(int_filenames):
            print(fn)
            self.ints.append(read_complex_type_2_to_complex_primitives(
                factory,
                fn,
                int_divides[i],
                int_lcs[i],
                int_transforms[i],
                int_transfinites[i],
                int_names[i]
            ))
        self.spent_times['Initialize Intrusions'] = time.time() - start_time
        print('ILW')
        start_time = time.time()
        self.ilws = []
        ilw_n = ilw_nx * ilw_ny
        est_time = 0
        times = []
        time_spent = 0
        for i in range(ilw_nx):
            for j in range(ilw_ny):
                start = time.time()
                cnt = i * ilw_ny + j + 1
                rem = ilw_n - cnt + 1
                rem_time = rem * est_time
                print('Borehole:{}/{} X:{}/{} Y:{}/{} SpentTime:{:.3f}s RemainingTime:{:.3f}s'.format(
                    cnt, ilw_n, i + 1, ilw_nx, j + 1, ilw_ny, time_spent, rem_time))
                new_ilw_transform = list(ilw_transform)
                new_ilw_transform[0] += ilw_dx * i
                new_ilw_transform[1] += ilw_dy * j
                ilw_input['arguments']['transform_data'] = new_ilw_transform
                self.ilws.append(ComplexFactory.new(ilw_input))
                times.append(time.time() - start)
                print('{:.3f}s'.format(times[-1]))
                time_spent += times[-1]
                est_time = sum(times) / cnt
        self.spent_times['Initialize ILW'] = time.time() - start_time
        print('HLW')
        start_time = time.time()
        self.hlws = []
        hlw_n = hlw_nx * hlw_ny
        est_time = 0
        times = []
        time_spent = 0
        for i in range(hlw_nx):
            for j in range(hlw_ny):
                start = time.time()
                cnt = i * hlw_ny + j + 1
                rem = hlw_n - cnt + 1
                rem_time = rem * est_time
                print('Borehole:{}/{} X:{}/{} Y:{}/{} SpentTime:{:.3f}s RemainingTime:{:.3f}s'.format(
                    cnt, hlw_n, i + 1, hlw_nx, j + 1, hlw_ny, time_spent, rem_time))
                new_hlw_transform = list(hlw_transform)
                new_hlw_transform[0] += hlw_dx * i
                new_hlw_transform[1] += hlw_dy * j
                hlw_input['arguments']['transform_data'] = new_hlw_transform
                self.hlws.append(ComplexFactory.new(hlw_input))
                times.append(time.time() - start)
                print('{:.3f}s'.format(times[-1]))
                time_spent += times[-1]
                est_time = sum(times) / cnt
        self.spent_times['Initialize HLW'] = time.time() - start_time
        print('Environment')
        start_time = time.time()
        self.env_transform = env_transform
        self.env_point_data = env_input['arguments']['point_data']
        if self.factory == gmsh.model.occ:
            env_input['arguments']['transform_data'] = env_transform
            self.env = ComplexFactory.new(env_input)
        self.spent_times['Initialize Environment'] = time.time() - start_time

    def environment(self):
        print('Environment')
        start_time = time.time()
        lx = self.env_point_data[0]
        ly = self.env_point_data[1]
        lz = self.env_point_data[2]
        lc = self.env_point_data[3]
        inner_surfaces = auto_volumes_groups_surfaces()
        self.env = Environment(self.factory_str, lx, ly, lz, lc, self.env_transform, inner_surfaces, self.env_name)
        self.spent_times['Environment'] = time.time() - start_time

    def evaluate(self):
        print('Evaluating')
        start_time = time.time()
        print('Intrusions')
        for intrusion in self.ints:
            for c in intrusion:
                c.evaluate_coordinates()
                c.evaluate_bounding_box()
        print('ILW Boreholes')
        for b in self.ilws:
            b.evaluate_coordinates()
            b.evaluate_bounding_box()
        print('HLW Boreholes')
        for b in self.hlws:
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
                    print('Borehole:{}/{} Intrusion:{}/{} IntrusionPart:{}/{}'.format(
                        i + 1, len(self.ilws), j + 1, len(self.ints), k + 1, len(intrusion)))
                    b_volumes = c.get_volumes()
                    complex_by_volumes(self.factory, c, b_volumes, remove_tool=False,
                                       sort_function=sort_object_only_shared_no_tool)
        self.spent_times['Ints By ILW Cut'] = time.time() - start_time
        print('Intrusions By HLW Boreholes')
        start_time = time.time()
        for i, b in enumerate(self.hlws):
            for j, intrusion in enumerate(self.ints):
                for k, c in enumerate(intrusion):
                    print('Borehole:{}/{} Intrusion:{}/{} IntrusionPart:{}/{}'.format(
                        i + 1, len(self.ilws), j + 1, len(self.ints), k + 1, len(intrusion)))
                    b_volumes = c.get_volumes()
                    complex_by_volumes(self.factory, c, b_volumes, remove_tool=False,
                                       sort_function=sort_object_only_shared_no_tool)
        self.spent_times['Ints By HLW Cut'] = time.time() - start_time
        print('Bool')
        print('Intrusions By ILW Boreholes')
        start_time = time.time()
        for i, b in enumerate(self.ilws):
            for j, intrusion in enumerate(self.ints):
                for k, c in enumerate(intrusion):
                    print('Borehole:{}/{} Intrusion:{}/{} IntrusionPart:{}/{}'.format(
                        i + 1, len(self.ilws), j + 1, len(self.ints), k + 1, len(intrusion)))
                    complex_by_complex(self.factory, c, b)
        self.spent_times['Ints By ILW'] = time.time() - start_time
        print('Intrusions By HLW Boreholes')
        start_time = time.time()
        for i, b in enumerate(self.hlws):
            for j, intrusion in enumerate(self.ints):
                for k, c in enumerate(intrusion):
                    print('Borehole:{}/{} Intrusion:{}/{} IntrusionPart:{}/{}'.format(
                        i + 1, len(self.ilws), j + 1, len(self.ints), k + 1, len(intrusion)))
                    complex_by_complex(self.factory, c, b)
        self.spent_times['Ints By HLW'] = time.time() - start_time

    def boolean_environment(self):
        if len(self.env.primitives) == 1:
            print('Intrusions By Environment')
            start_time = time.time()
            for i, intrusion in enumerate(self.ints):
                print('Intrusion:{}/{}'.format(i + 1, len(self.ints)))
                for c in intrusion:
                    complex_by_complex(self.factory, c, self.env, sort_function=sort_object_only_shared_tool_no_shared,
                                       pre_boolean=False)
            self.spent_times['Ints By Env'] = time.time() - start_time
            print('ILW Boreholes By Environment')
            start_time = time.time()
            for i, b in enumerate(self.ilws):
                print('Borehole:{}/{}'.format(i + 1, len(self.ilws)))
                complex_by_complex(self.factory, b, self.env, sort_function=sort_object_only_shared_tool_no_shared,
                                   pre_boolean=False)
            self.spent_times['ILW By Env'] = time.time() - start_time
            print('HLW Boreholes By Environment')
            start_time = time.time()
            for i, b in enumerate(self.hlws):
                print('Borehole:{}/{}'.format(i + 1, len(self.hlws)))
                complex_by_complex(self.factory, b, self.env, sort_function=sort_object_only_shared_tool_no_shared,
                                   pre_boolean=False)
        else:
            print('Cut')
            e_volumes = self.env.get_volumes()
            print('Environment By Intrusions')
            start_time = time.time()
            for i, intrusion in enumerate(self.ints):
                print('Intrusion:{}/{}'.format(i + 1, len(self.ints)))
                for c in intrusion:
                    complex_by_volumes(self.factory, c, e_volumes, remove_tool=False,
                                       sort_function=sort_object_only_shared_no_tool)
            self.spent_times['Env By Ints Cut'] = time.time() - start_time
            print('Environment By ILW Boreholes')
            start_time = time.time()
            for i, b in enumerate(self.ilws):
                print('Borehole:{}/{}'.format(i + 1, len(self.ilws)))
                complex_by_volumes(self.factory, b, e_volumes, remove_tool=False,
                                   sort_function=sort_object_only_shared_no_tool)
            self.spent_times['Env By Ilw Cut'] = time.time() - start_time
            print('Environment By HLW Boreholes')
            start_time = time.time()
            for i, b in enumerate(self.hlws):
                print('Borehole:{}/{}'.format(i + 1, len(self.hlws)))
                complex_by_volumes(self.factory, b, e_volumes, remove_tool=False,
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
        print('Intrusions')
        for i in self.ints:
            for c in i:
                occ_ws.correct_and_transfinite_complex(c, ss, cs)
        print('ILW Boreholes')
        for b in self.ilws:
            occ_ws.correct_and_transfinite_complex(b, ss, cs)
        print('HLW Boreholes')
        for b in self.hlws:
            occ_ws.correct_and_transfinite_complex(b, ss, cs)
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
            print('Maximum Point: {0}, Value: {1}'.format(max_size_key, pss[max_size_key]))
            print('Minimum Point: {0}, Value: {1}'.format(min_size_key, pss[min_size_key]))
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
        print('Intrusions')
        if len(self.ints) > 0:
            for local_name in set(self.int_names):  # For same names for different ints
                vs = set()
                for intrusion in self.ints:
                    for c in intrusion:
                        cvs = c.get_volumes_by_physical_name(local_name)
                        vs.update(cvs)
                tag = gmsh.model.addPhysicalGroup(3, list(vs))
                gmsh.model.setPhysicalName(3, tag, local_name)
        print('ILW Boreholes')
        if len(self.ilws) > 0:
            local_names = self.ilws[0].map_physical_name_to_primitives_indices.keys()
            for local_name in local_names:
                vs = set()
                for b in self.ilws:
                    bvs = b.get_volumes_by_physical_name(local_name)
                    vs.update(bvs)
                tag = gmsh.model.addPhysicalGroup(3, list(vs))
                gmsh.model.setPhysicalName(3, tag, '_'.join([self.ilw_name, local_name]))
        print('HLW Boreholes')
        if len(self.hlws) > 0:
            local_names = self.hlws[0].map_physical_name_to_primitives_indices.keys()
            for local_name in local_names:
                vs = set()
                for b in self.hlws:
                    bvs = b.get_volumes_by_physical_name(local_name)
                    vs.update(bvs)
                tag = gmsh.model.addPhysicalGroup(3, list(vs))
                gmsh.model.setPhysicalName(3, tag, '_'.join([self.hlw_name, local_name]))
        print('Environment')
        if self.factory == gmsh.model.occ:
            for local_name in self.env.map_physical_name_to_primitives_indices.keys():
                vs = self.env.get_volumes_by_physical_name(local_name)
                tag = gmsh.model.addPhysicalGroup(3, vs)
                if local_name == '':
                    gmsh.model.setPhysicalName(3, tag, self.env_name)
                else:
                    gmsh.model.setPhysicalName(3, tag, '_'.join([self.env_name, local_name]))
        else:
            tag = gmsh.model.addPhysicalGroup(3, self.env.volumes)
            gmsh.model.setPhysicalName(3, tag, self.env_name)
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
                        surfaces = c.get_surfaces_by_physical_name(physical_name)
                        for s in surfaces:
                            map_surface_to_physical_name[s] = physical_name
            print("ILW Boreholes")
            for b in self.ilws:
                for physical_name in b.map_physical_name_to_primitives_indices:
                    surfaces = b.get_surfaces_by_physical_name(physical_name)
                    for s in surfaces:
                        map_surface_to_physical_name[s] = '_'.join([self.ilw_name, physical_name])
            print("HLW Boreholes")
            for b in self.hlws:
                for physical_name in b.map_physical_name_to_primitives_indices:
                    surfaces = b.get_surfaces_by_physical_name(physical_name)
                    for s in surfaces:
                        map_surface_to_physical_name[s] = '_'.join([self.hlw_name, physical_name])
            print("Environment")
            for physical_name in self.env.map_physical_name_to_primitives_indices:
                surfaces = self.env.get_surfaces_by_physical_name(physical_name)
                for s in surfaces:
                    if physical_name == '':
                        map_surface_to_physical_name[s] = self.env_name
                    else:
                        map_surface_to_physical_name[s] = '_'.join([self.env_name, physical_name])
            print('Make Physical Surfaces')
            for i, (name, ss) in enumerate(boundary_surfaces_groups.items()):
                map_expanded_physical_name_to_surfaces = dict()
                for s in ss:
                    physical_name = '_'.join([name, map_surface_to_physical_name[s]])
                    map_expanded_physical_name_to_surfaces.setdefault(physical_name, list()).append(s)
                for j, (epn, ess) in enumerate(map_expanded_physical_name_to_surfaces.items()):
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
    print('Geometry.AutoCoherence: {}'.format(gmsh.option.getNumber('Geometry.AutoCoherence')))
    if is_verbose:
        gmsh.option.setNumber('General.Terminal', 1)
    else:
        gmsh.option.setNumber('General.Terminal', 0)
    print('General.Terminal: {}'.format(gmsh.option.getNumber('General.Terminal')))
    # (1=Delaunay, 2=New Delaunay, 4=Frontal, 5=Frontal Delaunay, 6=Frontal Hex, 7=MMG3D, 9=R-tree)
    gmsh.option.setNumber('Mesh.Algorithm3D', 4)
    print('Mesh.Algorithm3D: {}'.format(gmsh.option.getNumber('Mesh.Algorithm3D')))
    print('Input')
    with open(input_path) as f:
        input_nkm = json.load(f)
    pprint(input_nkm)
    factory_str = input_nkm['arguments']['factory']
    print('Initialize')
    nkm = NKM(**input_nkm['arguments'])
    nkm.synchronize()
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
            nkm.evaluate()
            nkm.remove_duplicates()
            nkm.synchronize()
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
