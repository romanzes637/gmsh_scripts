from primitive import Primitive
from primitive import Complex
import math


class Cylinder(Complex):
    def __init__(self, factory, radii, heights, lcs, transform_data, physical_data,
                 transfinite_r_data=None, transfinite_h_data=None, transfinite_phi_data=None):
        primitives = []
        primitive_physical_groups = []
        k = 1 / float(3)
        transfinite_types = [0, 0, 0, 1, 3]
        h_cnt = 0
        for i in range(len(heights)):
            # primitive_physical_groups.extend([physical_data[i][0]] * 5)
            primitive_physical_groups.append(1)
            r = radii[0] * math.sqrt(2)
            kr = k * radii[0] * math.sqrt(2)
            h = float(heights[i])
            h_cnt += h / 2
            h2 = h / 2
            # Core center
            primitives.append(Primitive(
                factory,
                [
                    5, 10, -15, 1,
                    -5, 10, -15, 1,
                    -5, -10, -15, 1,
                    # 5, -10, -15, 1,
                    kr, -kr, -14, 1,
                    # 5, 10, 15, 1,
                    # -5, 10, 15, 1,
                    # -5, -10, 15, 1,
                    # 5, -10, 15, 1
                    # kr, kr, -h / 2, lcs[i][0],
                    # -kr, kr, -h / 2, lcs[i][0],
                    # -kr, -kr, -h / 2, lcs[i][0],
                    # kr, -kr, -h / 2, lcs[i][0],
                    kr, kr, h / 2, lcs[i][0],
                    -kr, kr, h / 2, lcs[i][0],
                    -kr, -kr, h / 2, lcs[i][0],
                    kr, -kr, h / 2, lcs[i][0]
                ],
                [0, 0, 0, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                [[], [], [], [], [], [], [], [], [], [], [], []],
                [
                    [5, 0, 1],
                    [5, 0, 1],
                    [5, 0, 1],
                    [5, 0, 1],
                    [10, 0, 1],
                    [10, 0, 1],
                    [10, 0, 1],
                    [10, 0, 1],
                    [15, 0, 1],
                    [15, 0, 1],
                    [15, 0, 1],
                    [15, 0, 1]
                ],
                0
            ))
            # primitives.append(Primitive(
            #     factory,
            #     [
            #         kr, kr, -h / 2, lcs[i][0],
            #         -kr, kr, -h / 2, lcs[i][0],
            #         -kr, -kr, -h / 2, lcs[i][0],
            #         kr, -kr, -h / 2, lcs[i][0],
            #         kr, kr, h / 2, lcs[i][0],
            #         -kr, kr, h / 2, lcs[i][0],
            #         -kr, -kr, h / 2, lcs[i][0],
            #         kr, -kr, h / 2, lcs[i][0]
            #     ],
            #     [
            #         transform_data[0], transform_data[1], transform_data[2] + h_cnt,
            #         transform_data[3], transform_data[4], transform_data[5],
            #         transform_data[6], transform_data[7], transform_data[8]
            #     ],
            #     [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            #     [[], [], [], [], [], [], [], [], [], [], [], []],
            #     [
            #         transfinite_phi_data,
            #         transfinite_phi_data,
            #         transfinite_phi_data,
            #         transfinite_phi_data,
            #         transfinite_phi_data,
            #         transfinite_phi_data,
            #         transfinite_phi_data,
            #         transfinite_phi_data,
            #         transfinite_h_data[i],
            #         transfinite_h_data[i],
            #         transfinite_h_data[i],
            #         transfinite_h_data[i]
            #     ],
            #     transfinite_types[0]
            # ))
            # Core X
            # primitives.append(Primitive(
            #     factory,
            #     [
            #         r, r, -h / 2, lcs[i][0],
            #         kr, kr, -h / 2, lcs[i][0],
            #         kr, -kr, -h / 2, lcs[i][0],
            #         r, -r, -h / 2, lcs[i][0],
            #         r, r, h / 2, lcs[i][0],
            #         kr, kr, h / 2, lcs[i][0],
            #         kr, -kr, h / 2, lcs[i][0],
            #         r, -r, h / 2, lcs[i][0]
            #     ],
            #     [
            #         transform_data[0], transform_data[1], transform_data[2] + h_cnt,
            #         transform_data[3], transform_data[4], transform_data[5],
            #         transform_data[6], transform_data[7], transform_data[8],
            #     ],
            #     [0, 0, 0, 0, 1, 0, 0, 1, 0, 0, 0, 0],
            #     [
            #         [], [], [], [],
            #         [0, 0, -h / 2, 1], [], [], [0, 0, h / 2, 1],
            #         [], [], [], []
            #     ],
            #     [
            #         transfinite_r_data[0],
            #         transfinite_r_data[0],
            #         transfinite_r_data[0],
            #         transfinite_r_data[0],
            #         transfinite_phi_data,
            #         transfinite_phi_data,
            #         transfinite_phi_data,
            #         transfinite_phi_data,
            #         transfinite_h_data[i],
            #         transfinite_h_data[i],
            #         transfinite_h_data[i],
            #         transfinite_h_data[i]
            #     ],
            #     transfinite_types[1]
            # ))
            # # Core Y
            # primitives.append(Primitive(
            #     factory,
            #     [
            #         r, r, -h / 2, lcs[i][0],
            #         -r, r, -h / 2, lcs[i][0],
            #         -kr, kr, -h / 2, lcs[i][0],
            #         kr, kr, -h / 2, lcs[i][0],
            #         r, r, h / 2, lcs[i][0],
            #         -r, r, h / 2, lcs[i][0],
            #         -kr, kr, h / 2, lcs[i][0],
            #         kr, kr, h / 2, lcs[i][0]
            #     ],
            #     [
            #         transform_data[0], transform_data[1], transform_data[2] + h_cnt,
            #         transform_data[3], transform_data[4], transform_data[5],
            #         transform_data[6], transform_data[7], transform_data[8],
            #     ],
            #     [1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            #     [
            #         [0, 0, -h / 2, 1], [0, 0, h / 2, 1], [], [],
            #         [], [], [], [],
            #         [], [], [], []
            #     ],
            #     [
            #         transfinite_phi_data,
            #         transfinite_phi_data,
            #         transfinite_phi_data,
            #         transfinite_phi_data,
            #         transfinite_r_data[0],
            #         transfinite_r_data[0],
            #         transfinite_r_data[0],
            #         transfinite_r_data[0],
            #         transfinite_h_data[i],
            #         transfinite_h_data[i],
            #         transfinite_h_data[i],
            #         transfinite_h_data[i]
            #     ],
            #     transfinite_types[2]
            # ))
            # # Core NX
            # if transfinite_r_data[0][1] == 0:  # If Progression type => reverse
            #     kt = 1 / transfinite_r_data[0][2]
            # else:
            #     kt = transfinite_r_data[0][2]
            # primitives.append(Primitive(
            #     factory,
            #     [
            #         -kr, kr, -h / 2, lcs[i][0],
            #         -r, r, -h / 2, lcs[i][0],
            #         -r, -r, -h / 2, lcs[i][0],
            #         -kr, -kr, -h / 2, lcs[i][0],
            #         -kr, kr, h / 2, lcs[i][0],
            #         -r, r, h / 2, lcs[i][0],
            #         -r, -r, h / 2, lcs[i][0],
            #         -kr, -kr, h / 2, lcs[i][0]
            #     ],
            #     [
            #         transform_data[0], transform_data[1], transform_data[2] + h_cnt,
            #         transform_data[3], transform_data[4], transform_data[5],
            #         transform_data[6], transform_data[7], transform_data[8]
            #     ],
            #     [0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0],
            #     [
            #         [], [], [], [],
            #         [], [0, 0, -h / 2, 1], [0, 0, h / 2, 1], [],
            #         [], [], [], []
            #     ],
            #     [
            #         [transfinite_r_data[0][0], transfinite_r_data[0][1], kt],
            #         [transfinite_r_data[0][0], transfinite_r_data[0][1], kt],
            #         [transfinite_r_data[0][0], transfinite_r_data[0][1], kt],
            #         [transfinite_r_data[0][0], transfinite_r_data[0][1], kt],
            #         transfinite_phi_data,
            #         transfinite_phi_data,
            #         transfinite_phi_data,
            #         transfinite_phi_data,
            #         transfinite_h_data[i],
            #         transfinite_h_data[i],
            #         transfinite_h_data[i],
            #         transfinite_h_data[i]
            #     ],
            #     transfinite_types[3]
            # ))
            # # Core NY
            # if transfinite_r_data[0][1] == 0:  # If Progression type => reverse
            #     kt = 1 / transfinite_r_data[0][2]
            # else:
            #     kt = transfinite_r_data[0][2]
            # primitives.append(Primitive(
            #     factory,
            #     [
            #         kr, -kr, -h / 2, lcs[i][0],
            #         -kr, -kr, -h / 2, lcs[i][0],
            #         -r, -r, -h / 2, lcs[i][0],
            #         r, -r, -h / 2, lcs[i][0],
            #         kr, -kr, h / 2, lcs[i][0],
            #         -kr, -kr, h / 2, lcs[i][0],
            #         -r, -r, h / 2, lcs[i][0],
            #         r, -r, h / 2, lcs[i][0]
            #     ],
            #     [
            #         transform_data[0], transform_data[1], transform_data[2] + h_cnt,
            #         transform_data[3], transform_data[4], transform_data[5],
            #         transform_data[6], transform_data[7], transform_data[8]
            #     ],
            #     [0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0],
            #     [
            #         [], [], [0, 0, h / 2, 1], [0, 0, -h / 2, 1],
            #         [], [], [], [],
            #         [], [], [], []
            #     ],
            #     [
            #         transfinite_phi_data,
            #         transfinite_phi_data,
            #         transfinite_phi_data,
            #         transfinite_phi_data,
            #         [transfinite_r_data[0][0], transfinite_r_data[0][1], kt],
            #         [transfinite_r_data[0][0], transfinite_r_data[0][1], kt],
            #         [transfinite_r_data[0][0], transfinite_r_data[0][1], kt],
            #         [transfinite_r_data[0][0], transfinite_r_data[0][1], kt],
            #         transfinite_h_data[i],
            #         transfinite_h_data[i],
            #         transfinite_h_data[i],
            #         transfinite_h_data[i]
            #     ],
            #     transfinite_types[4]
            # ))
            # # Layers
            # for j in range(1, len(radii)):
            #     primitive_physical_groups.extend([physical_data[i][j]] * 4)
            #     r1 = radii[j - 1] * math.sqrt(2)
            #     r2 = radii[j] * math.sqrt(2)
            #     # Layer X
            #     primitives.append(Primitive(
            #         factory,
            #         [
            #             r2, r2, -h / 2, lcs[i][j],
            #             r1, r1, -h / 2, lcs[i][j],
            #             r1, -r1, -h / 2, lcs[i][j],
            #             r2, -r2, -h / 2, lcs[i][j],
            #             r2, r2, h / 2, lcs[i][j],
            #             r1, r1, h / 2, lcs[i][j],
            #             r1, -r1, h / 2, lcs[i][j],
            #             r2, -r2, h / 2, lcs[i][j]
            #         ],
            #         [
            #             transform_data[0], transform_data[1], transform_data[2] + h_cnt,
            #             transform_data[3], transform_data[4], transform_data[5],
            #             transform_data[6], transform_data[7], transform_data[8]
            #         ],
            #         [0, 0, 0, 0, 1, 1, 1, 1, 0, 0, 0, 0],
            #         [
            #             [], [], [], [],
            #             [0, 0, -h / 2, 1], [0, 0, -h / 2, 1], [0, 0, h / 2, 1], [0, 0, h / 2, 1],
            #             [], [], [], []
            #         ],
            #         [
            #             transfinite_r_data[j],
            #             transfinite_r_data[j],
            #             transfinite_r_data[j],
            #             transfinite_r_data[j],
            #             transfinite_phi_data,
            #             transfinite_phi_data,
            #             transfinite_phi_data,
            #             transfinite_phi_data,
            #             transfinite_h_data[i],
            #             transfinite_h_data[i],
            #             transfinite_h_data[i],
            #             transfinite_h_data[i]
            #         ],
            #         transfinite_types[1]
            #     ))
            #     # Layer Y
            #     primitives.append(Primitive(
            #         factory,
            #         [
            #             r2, r2, -h / 2, lcs[i][j],
            #             -r2, r2, -h / 2, lcs[i][j],
            #             -r1, r1, -h / 2, lcs[i][j],
            #             r1, r1, -h / 2, lcs[i][j],
            #             r2, r2, h / 2, lcs[i][j],
            #             -r2, r2, h / 2, lcs[i][j],
            #             -r1, r1, h / 2, lcs[i][j],
            #             r1, r1, h / 2, lcs[i][j]
            #         ],
            #         [
            #             transform_data[0], transform_data[1], transform_data[2] + h_cnt,
            #             transform_data[3], transform_data[4], transform_data[5],
            #             transform_data[6], transform_data[7], transform_data[8]
            #         ],
            #         [1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0],
            #         [
            #             [0, 0, -h / 2, 1], [0, 0, h / 2, 1], [0, 0, h / 2, 1], [0, 0, -h / 2, 1],
            #             [], [], [], [],
            #             [], [], [], []
            #         ],
            #         [
            #             transfinite_phi_data,
            #             transfinite_phi_data,
            #             transfinite_phi_data,
            #             transfinite_phi_data,
            #             transfinite_r_data[j],
            #             transfinite_r_data[j],
            #             transfinite_r_data[j],
            #             transfinite_r_data[j],
            #             transfinite_h_data[i],
            #             transfinite_h_data[i],
            #             transfinite_h_data[i],
            #             transfinite_h_data[i]
            #         ],
            #         transfinite_types[2]
            #     ))
            #     # Layer NX
            #     if transfinite_r_data[j][1] == 0:  # If Progression type => reverse
            #         kt = 1 / transfinite_r_data[j][2]
            #     else:
            #         kt = transfinite_r_data[j][2]
            #     primitives.append(Primitive(
            #         factory,
            #         [
            #             -r1, r1, -h / 2, lcs[i][j],
            #             -r2, r2, -h / 2, lcs[i][j],
            #             -r2, -r2, -h / 2, lcs[i][j],
            #             -r1, -r1, -h / 2, lcs[i][j],
            #             -r1, r1, h / 2, lcs[i][j],
            #             -r2, r2, h / 2, lcs[i][j],
            #             -r2, -r2, h / 2, lcs[i][j],
            #             -r1, -r1, h / 2, lcs[i][j]
            #         ],
            #         [
            #             transform_data[0], transform_data[1], transform_data[2] + h_cnt,
            #             transform_data[3], transform_data[4], transform_data[5],
            #             transform_data[6], transform_data[7], transform_data[8]
            #         ],
            #         [0, 0, 0, 0, 1, 1, 1, 1, 0, 0, 0, 0],
            #         [
            #             [], [], [], [],
            #             [0, 0, -h / 2, 1], [0, 0, -h / 2, 1], [0, 0, h / 2, 1], [0, 0, h / 2, 1],
            #             [], [], [], []
            #         ],
            #         [
            #             [transfinite_r_data[j][0], transfinite_r_data[j][1], kt],
            #             [transfinite_r_data[j][0], transfinite_r_data[j][1], kt],
            #             [transfinite_r_data[j][0], transfinite_r_data[j][1], kt],
            #             [transfinite_r_data[j][0], transfinite_r_data[j][1], kt],
            #             transfinite_phi_data,
            #             transfinite_phi_data,
            #             transfinite_phi_data,
            #             transfinite_phi_data,
            #             transfinite_h_data[i],
            #             transfinite_h_data[i],
            #             transfinite_h_data[i],
            #             transfinite_h_data[i]
            #         ],
            #         transfinite_types[3]
            #     ))
            #     # Layer NY
            #     if transfinite_r_data[j][1] == 0:  # If Progression type => reverse
            #         kt = 1 / transfinite_r_data[j][2]
            #     else:
            #         kt = transfinite_r_data[j][2]
            #     primitives.append(Primitive(
            #         factory,
            #         [
            #             r1, -r1, -h / 2, lcs[i][j],
            #             -r1, -r1, -h / 2, lcs[i][j],
            #             -r2, -r2, -h / 2, lcs[i][j],
            #             r2, -r2, -h / 2, lcs[i][j],
            #             r1, -r1, h / 2, lcs[i][j],
            #             -r1, -r1, h / 2, lcs[i][j],
            #             -r2, -r2, h / 2, lcs[i][j],
            #             r2, -r2, h / 2, lcs[i][j]
            #         ],
            #         [
            #             transform_data[0], transform_data[1], transform_data[2] + h_cnt,
            #             transform_data[3], transform_data[4], transform_data[5],
            #             transform_data[6], transform_data[7], transform_data[8]
            #         ],
            #         [1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0],
            #         [
            #             [0, 0, -h / 2, 1], [0, 0, h / 2, 1], [0, 0, h / 2, 1], [0, 0, -h / 2, 1],
            #             [], [], [], [],
            #             [], [], [], []
            #         ],
            #         [
            #             transfinite_phi_data,
            #             transfinite_phi_data,
            #             transfinite_phi_data,
            #             transfinite_phi_data,
            #             [transfinite_r_data[j][0], transfinite_r_data[j][1], kt],
            #             [transfinite_r_data[j][0], transfinite_r_data[j][1], kt],
            #             [transfinite_r_data[j][0], transfinite_r_data[j][1], kt],
            #             [transfinite_r_data[j][0], transfinite_r_data[j][1], kt],
            #             transfinite_h_data[i],
            #             transfinite_h_data[i],
            #             transfinite_h_data[i],
            #             transfinite_h_data[i]
            #         ],
            #         transfinite_types[4]
            #     ))
            # h_cnt += h / 2
            Complex.__init__(self, factory, primitives, primitive_physical_groups)

            # surface_names = {
            #     0: "Internal",
            #     1: "Lateral",
            #     2: "Bottom",
            #     3: "Up"
            # }

            # to_primitive_surface = [
            #         [0, 2, 1, 3, None],  # X, Y, NX, NY, Core
            #         [1, 3, 0, 2, None],  # X, Y, NX, NY, Core
            #         [4, 4, 4, 4, 4],  # X, Y, NX, NY, Core
            #         [5, 5, 5, 5, 5]  # X, Y, NX, NY, Core
            #     ]
            #
            #     def set_layer_volume_physical_group(self, height_idx, radius_idx, tag):
            #         start_idx = height_idx * (len(self.radii) * 4 + 1) + radius_idx * 4 + 1
            #         for i in range(start_idx, start_idx + 4):
            #             self.primitives[i].volumes_physical_groups[0] = tag
            #         if radius_idx == 0:
            #             self.primitives[start_idx - 1].volumes_physical_groups[0] = tag
            #
            #     def set_layer_surface_physical_group(self, height_idx, radius_idx, surface_idx, tag):
            #         start_idx = height_idx * (len(self.radii) * 4 + 1) + radius_idx * 4 + 1
            #         for i in range(start_idx, start_idx + 4):
            #             idx = self.to_primitive_surface[surface_idx][i - start_idx]
            #             self.primitives[i].surfaces_physical_groups[idx] = tag
            #         if radius_idx == 0:
            #             idx = self.to_primitive_surface[surface_idx][4]
            #             self.primitives[start_idx-1].surfaces_physical_groups[idx] = tag
