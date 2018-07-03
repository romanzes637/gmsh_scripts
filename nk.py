import time
import itertools
import occ_workarounds as occ_ws

from borehole import Borehole
from import_text import read_complex_type_2_to_complex_primitives
from primitive import Primitive, complex_boolean, complex_cut_by_volume_boolean, primitive_complex_boolean
from support import auto_complex_points_sizes_min_curve_in_volume


class NK:
    def __init__(
            self, factory, model,
            env_transform, env_volume_name, env_dx, env_dy, env_dz, env_lc,
            int_filenames, int_transforms, int_volume_names, int_lcs, int_divides, int_transfinites,
            bor_lcs, bor_transfinite_r, bor_transfinite_h, bor_transfinite_phi, bor_nh,
            ilw_transform, ilw_name, ilw_nx, ilw_ny, ilw_dx, ilw_dy,
            hlw_transform, hlw_name, hlw_nx, hlw_ny, hlw_dx, hlw_dy):
        print("Initialization")
        self.spent_times = {
            "Init Env": 0,
            "Init Ints": 0,
            "Init ILW": 0,
            "Init HLW": 0,
            "In Ints": 0,
            "Ints By Ints": 0,
            "ILW Unions": 0,
            "Ints By ILW": 0,
            "HLW Unions": 0,
            "Ints By HLW": 0,
            "Env By Ints": 0,
            "Env By ILW": 0,
            "Remove Ds": 0,
            "C And T": 0,
            "Set Sizes": 0,
            "Physical": 0
        }
        self.factory = factory
        self.model = model
        self.int_volume_names = int_volume_names
        self.ilw_name = ilw_name
        self.hlw_name = hlw_name
        print("Environment")
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
            volume_name=env_volume_name
        )
        self.spent_times["Init Env"] = time.time() - start_time
        print("Intrusions")
        start_time = time.time()
        self.ints = []  # Array of ComplexPrimitives arrays
        for i, fn in enumerate(int_filenames):
            self.ints.append(read_complex_type_2_to_complex_primitives(
                factory,
                fn,
                int_divides[i],
                int_lcs[i],
                int_transforms[i],
                int_transfinites[i],
                int_volume_names[i]
            ))
        self.spent_times["Init Ints"] = time.time() - start_time
        print("Boreholes")
        print("ILW")
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
                self.bs_ilw.append(Borehole(
                    factory,
                    bor_lcs,  # No effect due to auto points' sizes algorithm
                    [ilw_transform[0] + ilw_dx * i, ilw_transform[1] + ilw_dy * j, ilw_transform[2] - 37.5,
                     0, 0, 0, 0, 0, 0],
                    bor_transfinite_r,  # [[3, 0, 1], [3, 0, 1], [3, 0, 1]]
                    bor_transfinite_h,  # [[10, 0, 1], [10, 0, 1], [10, 0, 1]]
                    bor_transfinite_phi,  # [5, 0, 1]
                    bor_nh  # 10
                ))
                times.append(time.time() - start)
                print('{:.3f}s'.format(times[-1]))
                time_spent += times[-1]
                est_time = sum(times) / cnt
        self.spent_times["Init ILW"] = time.time() - start_time
        print("HLW")
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
                self.bs_hlw.append(Borehole(
                    factory,
                    bor_lcs,  # No effect due to auto points' sizes algorithm
                    [hlw_transform[0] + hlw_dx * i, hlw_transform[1] + hlw_dy * j, hlw_transform[2] - 37.5,
                     0, 0, 0, 0, 0, 0],
                    bor_transfinite_r,  # [[3, 0, 1], [3, 0, 1], [3, 0, 1]]
                    bor_transfinite_h,  # [[10, 0, 1], [10, 0, 1], [10, 0, 1]]
                    bor_transfinite_phi,  # [5, 0, 1]
                    bor_nh  # 10
                ))
                times.append(time.time() - start)
                print('{:.3f}s'.format(times[-1]))
                time_spent += times[-1]
                est_time = sum(times) / cnt
        self.spent_times["Init HLW"] = time.time() - start_time

    def boolean(self):
        print("Boolean")
        print("Intrusions Inner")
        start_time = time.time()
        for intrusion in self.ints:
            combinations = list(itertools.combinations(range(len(intrusion)), 2))
            for combination in combinations:
                print("Boolean %s by %s" % combination)
                complex_boolean(self.factory, intrusion[combination[0]], intrusion[combination[1]])
        self.spent_times["In Ints"] = time.time() - start_time

        print("Intrusions By Intrusions")
        start_time = time.time()
        combinations = list(itertools.combinations(range(len(self.ints)), 2))
        for combination in combinations:
            print("Boolean %s by %s" % combination)
            for c0 in self.ints[combination[0]]:
                for c1 in self.ints[combination[1]]:
                    complex_boolean(self.factory, c0, c1)
        self.spent_times["Ints by Ints"] = time.time() - start_time

        print("ILW Boreholes Unions")
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
        self.spent_times["ILW Unions"] = time.time() - start_time

        print("Intrusions By ILW Boreholes Boolean")
        start_time = time.time()
        for i, b in enumerate(self.bs_ilw):
            for j, intrusion in enumerate(self.ints):
                for k, c in enumerate(intrusion):
                    print('Borehole:{}/{} Intrusion:{}/{} IntrusionPart:{}/{}'.format(
                        i, len(self.bs_ilw), j, len(self.ints), k, len(intrusion)))
                    complex_cut_by_volume_boolean(self.factory, c, us[i][0][1])
                    complex_boolean(self.factory, c, b)
        self.spent_times["Ints By ILW"] = time.time() - start_time

        print("Environment by Intrusions boolean")
        start_time = time.time()
        for intrusion in self.ints:
            for c in intrusion:
                primitive_complex_boolean(self.factory, self.env, c)
        self.spent_times["Env By Ints"] = time.time() - start_time

        print("Environment by ILW Boreholes boolean")
        start_time = time.time()
        for b in self.bs_ilw:
            primitive_complex_boolean(self.factory, self.env, b)
        self.spent_times["Env By ILW"] = time.time() - start_time

        print("Remove All Duplicates")
        start_time = time.time()
        self.factory.removeAllDuplicates()
        self.factory.synchronize()
        self.spent_times["Remove Ds"] = time.time() - start_time

        print("Correct and Transfinite")
        start_time = time.time()
        ss = set()
        print("Intrusions")
        for intrusion in self.ints:
            for c in intrusion:
                occ_ws.correct_and_transfinite_complex(c, ss)
        print("ILW Boreholes")
        for b in self.bs_ilw:
            occ_ws.correct_and_transfinite_complex(b, ss)
        self.spent_times["C And T"] = time.time() - start_time

        print("Set Sizes")
        start_time = time.time()
        pss = dict()
        print("Intrusions")
        for intrusion in self.ints:
            for c in intrusion:
                auto_complex_points_sizes_min_curve_in_volume(c, pss)
        print("ILW Boreholes")
        for b in self.bs_ilw:
            auto_complex_points_sizes_min_curve_in_volume(b, pss)
        print(pss)
        max_size_key = max(pss.keys(), key=(lambda k: pss[k]))
        min_size_key = min(pss.keys(), key=(lambda k: pss[k]))
        print('Maximum Point, Value: {0}, {1}'.format(max_size_key, pss[max_size_key]))
        print('Minimum Point, Value: {0}, {1}'.format(min_size_key, pss[min_size_key]))
        self.spent_times["Set Sizes"] = time.time() - start_time

    def physical(self):
        print("Physical")
        start_time = time.time()
        print("Intrusions Physical")
        for name in self.int_volume_names:
            vs = []
            for intrusion in self.ints:
                for c in intrusion:
                    vs.extend(c.get_volumes_by_name(name))
            tag = self.model.addPhysicalGroup(3, vs)
            self.model.setPhysicalName(3, tag, name)
        print("ILW Boreholes Physical")
        for name in Borehole.volumes_names:
            vs = []
            for b in self.bs_ilw:
                vs.extend(b.get_volumes_by_name(name))
            tag = self.model.addPhysicalGroup(3, vs)
            self.model.setPhysicalName(3, tag, self.ilw_name + name)
        print("Environment Physical")
        tag = self.model.addPhysicalGroup(3, self.env.volumes)
        self.model.setPhysicalName(3, tag, self.env.volume_name)
        volumes_dim_tags = map(lambda x: (3, x), self.env.volumes)
        surfaces_dim_tags = self.model.getBoundary(volumes_dim_tags, combined=False)
        surfaces_names = ["X", "Z", "NY", "NZ", "Y", "NX"]
        for i in range(len(surfaces_names)):
            tag = self.model.addPhysicalGroup(surfaces_dim_tags[i][0], [surfaces_dim_tags[i][1]])
            self.model.setPhysicalName(2, tag, surfaces_names[i])
            #     gmsh.model.setPhysicalName(2, tag, 'S%s' % i)
        self.spent_times["Physical"] = time.time() - start_time
