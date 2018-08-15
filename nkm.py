import argparse
import json
from pprint import pprint

import gmsh
import time
import itertools
import occ_workarounds as occ_ws
import os

from divided_cylinder import DividedCylinder
from io import read_complex_type_2_to_complex_primitives
from primitive import Primitive, complex_boolean, complex_cut_by_volume_boolean, primitive_complex_boolean, Environment
from support import auto_complex_points_sizes_min_curve_in_volume, auto_volumes_groups_surfaces, auto_points_sizes


class NKM:
    def __init__(
            self, factory,
            env_transform, env_volume_name, env_dx, env_dy, env_dz, env_lc, env_bool,
            int_filenames, int_transforms, int_volume_names, int_lcs, int_divides, int_transfinites,
            ilw_input_path, ilw_name, ilw_transform, ilw_nx, ilw_ny, ilw_dx, ilw_dy,
            hlw_input_path, hlw_name, hlw_transform, hlw_nx, hlw_ny, hlw_dx, hlw_dy):
        """
        NKM model with Intrusions, ILW and HLW Boreholes inside Environment
        :param str factory: see Primitive
        :param list of float env_transform: Environment center transform (see Primitive)
        :param str env_volume_name: Environment physical name
        :param float env_dx: Environment length x
        :param float env_dy: Environment length y
        :param float env_dz: Environment length z
        :param float env_lc: Environment nodes characteristic length
        :param bool env_bool: Boolean environment?
        :param list of str int_filenames: Intrusions filenames (Complex Type 2, see io.py)
        :param list of list of float int_transforms: Intrusions transforms (see Primitive)
        :param list of str int_volume_names: Intrusions physical names
        :param list of float int_lcs: Intrusions characteristic lengths (no effect, if set_sizes method has been called)
        :param list of list of int int_divides: Intrusions number of divide parts (see ComplexPrimitive)
        :param list of list of float int_transfinites: Intrusions transfinites (see ComplexPrimitive)
        :param str ilw_input_path: ILW Boreholes input path
        :param str ilw_name: ILW Boreholes physical name prefix
        :param list of float ilw_transform: ILW Boreholes transform (First ILW Borehole position) see Primitive
        :param int ilw_nx: Number of ILW Boreholes x
        :param int ilw_ny: Number of ILW Boreholes y
        :param float ilw_dx: Interval of ILW Boreholes x
        :param float ilw_dy: Interval of ILW Boreholes y
        :param str hlw_input_path: HLW Boreholes input path
        :param str hlw_name: HLW Boreholes physical name prefix
        :param list of float hlw_transform: HLW Boreholes transform (First HLW Borehole position) see Primitive
        :param int hlw_nx: Number of HLW Boreholes x
        :param int hlw_ny: Number of HLW Boreholes y
        :param float hlw_dx: Interval of HLW Boreholes x
        :param float hlw_dy: Interval of HLW Boreholes y
        """
        print('Arguments')
        print('NKM')
        pprint(locals())
        print('ILW')
        with open(ilw_input_path) as ilw_input_file:
            ilw_args = json.load(ilw_input_file)
        pprint(ilw_args)
        print('HLW')
        with open(hlw_input_path) as hlw_input_file:
            hlw_args = json.load(hlw_input_file)
        pprint(hlw_args)
        print('Initialization')
        self.spent_times = {}
        if factory == 'occ':
            self.factory = gmsh.model.occ
        else:
            self.factory = gmsh.model.geo
        self.int_volume_names = int_volume_names
        self.ilw_name = ilw_name
        self.hlw_name = hlw_name
        self.env_transform = env_transform
        self.env_volume_name = env_volume_name
        self.env_dx = env_dx
        self.env_dy = env_dy
        self.env_dz = env_dz
        self.env_lc = env_lc
        self.env_bool = env_bool
        if env_bool:
            print('Environment')
            start_time = time.time()
            self.env = Primitive(
                factory,
                [
                    [env_dx / 2, env_dy / 2, -env_dz, env_lc],
                    [-env_dx / 2, env_dy / 2, -env_dz, env_lc],
                    [-env_dx / 2, -env_dy / 2, -env_dz, env_lc],
                    [env_dx / 2, -env_dy / 2, -env_dz, env_lc],
                    [env_dx / 2, env_dy / 2, env_dz, env_lc],
                    [-env_dx / 2, env_dy / 2, env_dz, env_lc],
                    [-env_dx / 2, -env_dy / 2, env_dz, env_lc],
                    [env_dx / 2, -env_dy / 2, env_dz, env_lc]
                ],
                transform_data=env_transform,
                physical_name=env_volume_name
            )
            self.spent_times['Init Env'] = time.time() - start_time
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
                int_volume_names[i]
            ))
        self.spent_times['Init Ints'] = time.time() - start_time
        print('Boreholes')
        print('ILW')
        start_time = time.time()
        self.bs_ilw = []
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
                ilw_args['transform_data'] = new_ilw_transform
                self.bs_ilw.append(DividedCylinder(**ilw_args))
                times.append(time.time() - start)
                print('{:.3f}s'.format(times[-1]))
                time_spent += times[-1]
                est_time = sum(times) / cnt
        self.spent_times['Init ILW'] = time.time() - start_time
        print('HLW')
        start_time = time.time()
        self.bs_hlw = []
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
                hlw_args['transform_data'] = new_hlw_transform
                self.bs_hlw.append(DividedCylinder(**hlw_args))
                times.append(time.time() - start)
                print('{:.3f}s'.format(times[-1]))
                time_spent += times[-1]
                est_time = sum(times) / cnt
        self.spent_times['Init HLW'] = time.time() - start_time

    def evaluate(self):
        print('Evaluate')
        start_time = time.time()
        if self.env_bool:
            print('Environment')
            self.env.evaluate_coordinates()
            self.env.evaluate_bounding_box()
        print('Intrusions')
        for intrusion in self.ints:
            for c in intrusion:
                c.evaluate_coordinates()
                c.evaluate_bounding_box()
        print('ILW Boreholes')
        for b in self.bs_ilw:
            b.evaluate_coordinates()
            b.evaluate_bounding_box()
        print('HLW Boreholes')
        for b in self.bs_hlw:
            b.evaluate_coordinates()
            b.evaluate_bounding_box()
        self.spent_times['Evaluate'] = time.time() - start_time

    def boolean(self):
        print('Boolean')
        if len(self.ints) > 0:
            print('Intrusions Inner')
            start_time = time.time()
            for intrusion in self.ints:
                combinations = list(itertools.combinations(range(len(intrusion)), 2))
                for combination in combinations:
                    print('Boolean %s by %s' % combination)
                    complex_boolean(self.factory, intrusion[combination[0]], intrusion[combination[1]])
            self.spent_times['In Ints'] = time.time() - start_time

            print('Intrusions By Intrusions')
            start_time = time.time()
            combinations = list(itertools.combinations(range(len(self.ints)), 2))
            for combination in combinations:
                print('Boolean %s by %s' % combination)
                for c0 in self.ints[combination[0]]:
                    for c1 in self.ints[combination[1]]:
                        complex_boolean(self.factory, c0, c1)
            self.spent_times['Ints by Ints'] = time.time() - start_time

            print('ILW Unions')
            start_time = time.time()
            us = []
            times = []
            est_time = 0
            time_spent = 0
            n = len(self.bs_ilw)
            for i, b in enumerate(self.bs_ilw):
                start = time.time()
                cnt = i + 1
                rem = n - cnt + 1
                rem_time = rem * est_time
                print('Borehole:{}/{} SpentTime:{:.3f}s RemainingTime:{:.3f}s'.format(cnt, n, time_spent, rem_time))
                us.append(b.get_union_volume())
                times.append(time.time() - start)
                print('{:.3f}s'.format(times[-1]))
                time_spent += times[-1]
                est_time = sum(times) / cnt
            self.spent_times['ILW Unions'] = time.time() - start_time

            print('Intrusions By ILW Boreholes')
            start_time = time.time()
            for i, b in enumerate(self.bs_ilw):
                for j, intrusion in enumerate(self.ints):
                    for k, c in enumerate(intrusion):
                        print('Borehole:{}/{} Intrusion:{}/{} IntrusionPart:{}/{}'.format(
                            i + 1, len(self.bs_ilw), j + 1, len(self.ints), k + 1, len(intrusion)))
                        complex_cut_by_volume_boolean(self.factory, c, us[i][0][1])
                        complex_boolean(self.factory, c, b)
            self.spent_times['Ints By ILW'] = time.time() - start_time

            print('HLW Unions')
            start_time = time.time()
            us = []
            times = []
            est_time = 0
            time_spent = 0
            n = len(self.bs_hlw)
            for i, b in enumerate(self.bs_hlw):
                start = time.time()
                cnt = i + 1
                rem = n - cnt + 1
                rem_time = rem * est_time
                print('Borehole:{}/{} SpentTime:{:.3f}s RemainingTime:{:.3f}s'.format(cnt, n, time_spent, rem_time))
                us.append(b.get_union_volume())
                times.append(time.time() - start)
                print('{:.3f}s'.format(times[-1]))
                time_spent += times[-1]
                est_time = sum(times) / cnt
            self.spent_times['HLW Unions'] = time.time() - start_time

            print('Intrusions By HLW Boreholes')
            start_time = time.time()
            for i, b in enumerate(self.bs_hlw):
                for j, intrusion in enumerate(self.ints):
                    for k, c in enumerate(intrusion):
                        print('Borehole:{}/{} Intrusion:{}/{} IntrusionPart:{}/{}'.format(
                            i + 1, len(self.bs_hlw), j + 1, len(self.ints), k + 1, len(intrusion)))
                        complex_cut_by_volume_boolean(self.factory, c, us[i][0][1])
                        complex_boolean(self.factory, c, b)
            self.spent_times['Ints By HLW'] = time.time() - start_time

            if self.env_bool:
                print('Environment by Intrusions')
                start_time = time.time()
                for i, intrusion in enumerate(self.ints):
                    print('Intrusion:{}/{}'.format(i + 1, len(self.ints)))
                    for c in intrusion:
                        primitive_complex_boolean(self.factory, self.env, c)
                self.spent_times['Env By Ints'] = time.time() - start_time

        if self.env_bool:
            print('Environment By ILW Boreholes')
            start_time = time.time()
            for i, b in enumerate(self.bs_ilw):
                print('Borehole:{}/{}'.format(i + 1, len(self.bs_ilw)))
                primitive_complex_boolean(self.factory, self.env, b)
            self.spent_times['Env By ILW'] = time.time() - start_time

            print('Environment By HLW Boreholes')
            start_time = time.time()
            for i, b in enumerate(self.bs_hlw):
                print('Borehole:{}/{}'.format(i + 1, len(self.bs_hlw)))
                primitive_complex_boolean(self.factory, self.env, b)
            self.spent_times['Env By HLW'] = time.time() - start_time

    def remove_duplicates(self):
        print('Remove Duplicates')
        start_time = time.time()
        self.factory.removeAllDuplicates()
        self.spent_times['Remove Ds'] = time.time() - start_time

    def environment(self):
        if not self.env_bool:
            print('Environment')
            start_time = time.time()
            vgs_ss = auto_volumes_groups_surfaces()
            self.env = Environment(
                self.factory,
                self.env_dx,
                self.env_dy,
                self.env_dz,
                self.env_lc,
                self.env_transform,
                vgs_ss,
                self.env_volume_name
            )
            self.spent_times['Init Env'] = time.time() - start_time

    def correct_and_transfinite(self):
        print('Correct and Transfinite')
        start_time = time.time()
        ss = set()
        if self.env_bool:
            print('Environment')
            occ_ws.correct_and_transfinite_primitive(self.env, ss)
        print('Intrusions')
        for i in self.ints:
            for c in i:
                occ_ws.correct_and_transfinite_complex(c, ss)
        print('ILW Boreholes')
        for b in self.bs_ilw:
            occ_ws.correct_and_transfinite_complex(b, ss)
        print('HLW Boreholes')
        for b in self.bs_hlw:
            occ_ws.correct_and_transfinite_complex(b, ss)
        self.spent_times['C And T'] = time.time() - start_time

    def transfinite(self):
        if self.factory == gmsh.model.geo:
            ss = set()
            print('Intrusions')
            for i in self.ints:
                for c in i:
                    c.transfinite(ss)
            print('ILW Boreholes')
            for b in self.bs_ilw:
                rs = b.transfinite(ss)
                print(rs)
            print('HLW Boreholes')
            for b in self.bs_hlw:
                b.transfinite(b, ss)

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
        for b in self.bs_ilw:
            auto_complex_points_sizes_min_curve_in_volume(b, pss)
        print('HLW Boreholes')
        for b in self.bs_hlw:
            auto_complex_points_sizes_min_curve_in_volume(b, pss)
        # print(pss)
        if len(pss) > 0:
            max_size_key = max(pss.keys(), key=(lambda x: pss[x]))
            min_size_key = min(pss.keys(), key=(lambda x: pss[x]))
            print('Maximum Point, Value: {0}, {1}'.format(max_size_key, pss[max_size_key]))
            print('Minimum Point, Value: {0}, {1}'.format(min_size_key, pss[min_size_key]))
        self.spent_times['Set Sizes'] = time.time() - start_time

    def smooth(self, dim, n):
        print('Smooth')
        start_time = time.time()
        print('Environment')
        if self.env is not None:
            self.env.smooth(dim, n)
        print('Intrusions')
        for intrusion in self.ints:
            for c in intrusion:
                c.smooth(dim, n)
        print('ILW Boreholes')
        for b in self.bs_ilw:
            b.smooth(dim, n)
        print('HLW Boreholes')
        for b in self.bs_hlw:
            b.smooth(dim, n)
        self.spent_times['Smooth'] = time.time() - start_time

    def physical(self):
        print('Physical')
        start_time = time.time()
        print('Intrusions')
        if len(self.ints) > 0:
            for name in set(self.int_volume_names):  # For same names for different ints
                vs = list()
                for intrusion in self.ints:
                    for c in intrusion:
                        vs.extend(c.get_volumes_by_physical_name(name))
                tag = gmsh.model.addPhysicalGroup(3, vs)
                gmsh.model.setPhysicalName(3, tag, name)
        print('ILW Boreholes')
        if len(self.bs_ilw) > 0:
            for name in Borehole.volumes_names:
                vs = list()
                for b in self.bs_ilw:
                    vs.extend(b.get_volumes_by_physical_name(name))
                tag = gmsh.model.addPhysicalGroup(3, vs)
                gmsh.model.setPhysicalName(3, tag, self.ilw_name + name)
        print('HLW Boreholes')
        if len(self.bs_hlw) > 0:
            for name in Borehole.volumes_names:
                vs = list()
                for b in self.bs_hlw:
                    vs.extend(b.get_volumes_by_physical_name(name))
                tag = gmsh.model.addPhysicalGroup(3, vs)
                gmsh.model.setPhysicalName(3, tag, self.hlw_name + name)
        print('Environment')
        tag = gmsh.model.addPhysicalGroup(3, self.env.volumes)
        gmsh.model.setPhysicalName(3, tag, self.env.volume_name)
        volumes_dim_tags = map(lambda x: (3, x), self.env.volumes)
        surfaces_dim_tags = gmsh.model.getBoundary(volumes_dim_tags, combined=False)
        if self.factory != gmsh.model.geo:
            if self.env_bool:
                surfaces_names = ['X', 'Z', 'NY', 'NZ', 'Y', 'NX']
            else:
                surfaces_names = ['X', 'NY', 'NX', 'Y', 'NZ', 'Z']
        else:
            surfaces_names = ['NX', 'X', 'NY', 'Y', 'NZ', 'Z']
        for i, n in enumerate(surfaces_names):
            tag = gmsh.model.addPhysicalGroup(surfaces_dim_tags[i][0], [surfaces_dim_tags[i][1]])
            gmsh.model.setPhysicalName(2, tag, n)
        self.spent_times['Physical'] = time.time() - start_time


def main():
    spent_times = {}
    global_start_time = time.time()
    print('Start time: {}'.format(time.asctime(time.localtime(time.time()))))
    print('PID: {}'.format(os.getpid()))
    print('CMD Arguments')
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--input', help='input filename', default='input_nkm.json')
    parser.add_argument('-o', '--output', help='output filename')
    parser.add_argument('-v', '--verbose', help='verbose', action='store_true')
    parser.add_argument('-t', '--test', help='test mode', action='store_true')
    args = parser.parse_args()
    basename, extension = os.path.splitext(args.input)
    if args.output is None:
        print('Using default output')
        args.output = basename
    print(args)
    input_path = args.input
    model_name = basename
    is_test = args.test
    is_verbose = args.verbose
    if is_test:
        output_path = args.output + '.brep'
    else:
        output_path = args.output + '.msh'
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
    print('NKM')
    start_time = time.time()
    with open(input_path) as f:
        d = json.load(f)
    nkm = NKM(**d)
    nkm.factory.synchronize()
    if not is_test:
        nkm.evaluate()
        nkm.boolean()
        nkm.remove_duplicates()
        nkm.factory.synchronize()
        nkm.environment()
        nkm.factory.synchronize()
        nkm.set_sizes()
        nkm.correct_and_transfinite()
        nkm.physical()
        # nkm.smooth(2, 1)
        spent_times.update(nkm.spent_times)
        spent_times['NK'] = time.time() - start_time
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

if __name__ == '__main__':
    main()
