from primitive import Primitive
from primitive import Complex
import math


class Cylinder(Complex):
    def __init__(self, factory, radii, heights, primitives_lcs, transform_data, layers_physical_names,
                 transfinite_r_data, transfinite_h_data, transfinite_phi_data):
        """
        Multilayer cylinder
        Used for axisymmetric objects
        Layers structure:
        h - height
        c - radius
        hM_r1 hM_r2 ... hM_rN
        ...   ...   ... ...
        h2_r1 h2_r2 ... h2_rN
        h1_r1 h1_r2 ... h1_rN
        Bottom center of h1_r1 layer is an origin of the cylinder
        :param factory: gmsh factory (currently: gmsh.model.geo or gmsh.model.occ)
        :param radii: [c1, c2, ..., rN]
        :param heights: [h1, h2, ..., hM]
        :param primitives_lcs: characteristic lengths of layers [[h1_r1, h1_r2, ...], [h2_r1, h2_r2 ...], ...]
        :param transform_data: relative to Cylinder bottom (see Primitive transform_data)
        :param layers_physical_names: physical indices of layers [[h1_r1, h1_r2, ...], [h2_r1, h2_r2 ...], ...]
        :param transfinite_r_data: [[c1 number of nodes, type (0 - Progression, 1 - Bump), coefficient], [c2 ...], ...]
        :param transfinite_h_data: [[h1 number of nodes, type (0 - Progression, 1 - Bump), coefficient], [h2 ...], ...]
        :param transfinite_phi_data: [circumferential number of nodes, type, coefficient]
        """
        primitives = []
        k = 1 / float(3)
        transfinite_types = [0, 0, 0, 1, 3]
        h_cnt = 0
        for i in range(len(heights)):
            c = radii[0] / math.sqrt(2)
            kc = k * radii[0] / math.sqrt(2)
            h = float(heights[i])
            h_cnt += h / 2
            # Core center
            primitives.append(Primitive(
                factory,
                [
                    [kc, kc, h_cnt - h / 2, primitives_lcs[i][0]],
                    [-kc, kc, h_cnt - h / 2, primitives_lcs[i][0]],
                    [-kc, -kc, h_cnt - h / 2, primitives_lcs[i][0]],
                    [kc, -kc, h_cnt - h / 2, primitives_lcs[i][0]],
                    [kc, kc, h_cnt + h / 2, primitives_lcs[i][0]],
                    [-kc, kc, h_cnt + h / 2, primitives_lcs[i][0]],
                    [-kc, -kc, h_cnt + h / 2, primitives_lcs[i][0]],
                    [kc, -kc, h_cnt + h / 2, primitives_lcs[i][0]]
                ],
                transform_data,
                [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                [[], [], [], [], [], [], [], [], [], [], [], []],
                [
                    transfinite_phi_data,
                    transfinite_phi_data,
                    transfinite_phi_data,
                    transfinite_phi_data,
                    transfinite_phi_data,
                    transfinite_phi_data,
                    transfinite_phi_data,
                    transfinite_phi_data,
                    transfinite_h_data[i],
                    transfinite_h_data[i],
                    transfinite_h_data[i],
                    transfinite_h_data[i]
                ],
                transfinite_types[0],
                layers_physical_names[i][0]
            ))
            # Core X
            primitives.append(Primitive(
                factory,
                [
                    [c, c, h_cnt - h / 2, primitives_lcs[i][0]],
                    [kc, kc, h_cnt - h / 2, primitives_lcs[i][0]],
                    [kc, -kc, h_cnt - h / 2, primitives_lcs[i][0]],
                    [c, -c, h_cnt - h / 2, primitives_lcs[i][0]],
                    [c, c, h_cnt + h / 2, primitives_lcs[i][0]],
                    [kc, kc, h_cnt + h / 2, primitives_lcs[i][0]],
                    [kc, -kc, h_cnt + h / 2, primitives_lcs[i][0]],
                    [c, -c, h_cnt + h / 2, primitives_lcs[i][0]]
                ],
                transform_data,
                [0, 0, 0, 0, 1, 0, 0, 1, 0, 0, 0, 0],
                [
                    [], [], [], [],
                    [[0, 0, h_cnt - h / 2, 1]], [], [], [[0, 0, h_cnt + h / 2, 1]],
                    [], [], [], []
                ],
                [
                    transfinite_r_data[0],
                    transfinite_r_data[0],
                    transfinite_r_data[0],
                    transfinite_r_data[0],
                    transfinite_phi_data,
                    transfinite_phi_data,
                    transfinite_phi_data,
                    transfinite_phi_data,
                    transfinite_h_data[i],
                    transfinite_h_data[i],
                    transfinite_h_data[i],
                    transfinite_h_data[i]
                ],
                transfinite_types[1],
                layers_physical_names[i][0]
            ))
            # Core Y
            primitives.append(Primitive(
                factory,
                [
                    [c, c, h_cnt - h / 2, primitives_lcs[i][0]],
                    [-c, c, h_cnt - h / 2, primitives_lcs[i][0]],
                    [-kc, kc, h_cnt - h / 2, primitives_lcs[i][0]],
                    [kc, kc, h_cnt - h / 2, primitives_lcs[i][0]],
                    [c, c, h_cnt + h / 2, primitives_lcs[i][0]],
                    [-c, c, h_cnt + h / 2, primitives_lcs[i][0]],
                    [-kc, kc, h_cnt + h / 2, primitives_lcs[i][0]],
                    [kc, kc, h_cnt + h / 2, primitives_lcs[i][0]]
                ],
                transform_data,
                [1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                [
                    [[0, 0, h_cnt - h / 2, 1]], [[0, 0, h_cnt + h / 2, 1]], [], [],
                    [], [], [], [],
                    [], [], [], []
                ],
                [
                    transfinite_phi_data,
                    transfinite_phi_data,
                    transfinite_phi_data,
                    transfinite_phi_data,
                    transfinite_r_data[0],
                    transfinite_r_data[0],
                    transfinite_r_data[0],
                    transfinite_r_data[0],
                    transfinite_h_data[i],
                    transfinite_h_data[i],
                    transfinite_h_data[i],
                    transfinite_h_data[i]
                ],
                transfinite_types[2],
                layers_physical_names[i][0]
            ))
            # Core NX
            if transfinite_r_data[0][1] == 0:  # If Progression type => reverse
                kt = 1 / transfinite_r_data[0][2]
            else:
                kt = transfinite_r_data[0][2]
            primitives.append(Primitive(
                factory,
                [
                    [-kc, kc, h_cnt - h / 2, primitives_lcs[i][0]],
                    [-c, c, h_cnt - h / 2, primitives_lcs[i][0]],
                    [-c, -c, h_cnt - h / 2, primitives_lcs[i][0]],
                    [-kc, -kc, h_cnt - h / 2, primitives_lcs[i][0]],
                    [-kc, kc, h_cnt + h / 2, primitives_lcs[i][0]],
                    [-c, c, h_cnt + h / 2, primitives_lcs[i][0]],
                    [-c, -c, h_cnt + h / 2, primitives_lcs[i][0]],
                    [-kc, -kc, h_cnt + h / 2, primitives_lcs[i][0]]
                ],
                transform_data,
                [0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0],
                [
                    [], [], [], [],
                    [], [[0, 0, h_cnt - h / 2, 1]], [[0, 0, h_cnt + h / 2, 1]], [],
                    [], [], [], []
                ],
                [
                    [transfinite_r_data[0][0], transfinite_r_data[0][1], kt],
                    [transfinite_r_data[0][0], transfinite_r_data[0][1], kt],
                    [transfinite_r_data[0][0], transfinite_r_data[0][1], kt],
                    [transfinite_r_data[0][0], transfinite_r_data[0][1], kt],
                    transfinite_phi_data,
                    transfinite_phi_data,
                    transfinite_phi_data,
                    transfinite_phi_data,
                    transfinite_h_data[i],
                    transfinite_h_data[i],
                    transfinite_h_data[i],
                    transfinite_h_data[i]
                ],
                transfinite_types[3],
                layers_physical_names[i][0]
            ))
            # Core NY
            if transfinite_r_data[0][1] == 0:  # If Progression type => reverse
                kt = 1 / transfinite_r_data[0][2]
            else:
                kt = transfinite_r_data[0][2]
            primitives.append(Primitive(
                factory,
                [
                    [kc, -kc, h_cnt - h / 2, primitives_lcs[i][0]],
                    [-kc, -kc, h_cnt - h / 2, primitives_lcs[i][0]],
                    [-c, -c, h_cnt - h / 2, primitives_lcs[i][0]],
                    [c, -c, h_cnt - h / 2, primitives_lcs[i][0]],
                    [kc, -kc, h_cnt + h / 2, primitives_lcs[i][0]],
                    [-kc, -kc, h_cnt + h / 2, primitives_lcs[i][0]],
                    [-c, -c, h_cnt + h / 2, primitives_lcs[i][0]],
                    [c, -c, h_cnt + h / 2, primitives_lcs[i][0]]
                ],
                transform_data,
                [0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0],
                [
                    [], [], [[0, 0, h_cnt + h / 2, 1]], [[0, 0, h_cnt - h / 2, 1]],
                    [], [], [], [],
                    [], [], [], []
                ],
                [
                    transfinite_phi_data,
                    transfinite_phi_data,
                    transfinite_phi_data,
                    transfinite_phi_data,
                    [transfinite_r_data[0][0], transfinite_r_data[0][1], kt],
                    [transfinite_r_data[0][0], transfinite_r_data[0][1], kt],
                    [transfinite_r_data[0][0], transfinite_r_data[0][1], kt],
                    [transfinite_r_data[0][0], transfinite_r_data[0][1], kt],
                    transfinite_h_data[i],
                    transfinite_h_data[i],
                    transfinite_h_data[i],
                    transfinite_h_data[i]
                ],
                transfinite_types[4],
                layers_physical_names[i][0]
            ))
            # Layers
            for j in range(1, len(radii)):
                c1 = radii[j - 1] / math.sqrt(2)
                c2 = radii[j] / math.sqrt(2)
                # Layer X
                primitives.append(Primitive(
                    factory,
                    [
                        [c2, c2, h_cnt - h / 2, primitives_lcs[i][j]],
                        [c1, c1, h_cnt - h / 2, primitives_lcs[i][j]],
                        [c1, -c1, h_cnt - h / 2, primitives_lcs[i][j]],
                        [c2, -c2, h_cnt - h / 2, primitives_lcs[i][j]],
                        [c2, c2, h_cnt + h / 2, primitives_lcs[i][j]],
                        [c1, c1, h_cnt + h / 2, primitives_lcs[i][j]],
                        [c1, -c1, h_cnt + h / 2, primitives_lcs[i][j]],
                        [c2, -c2, h_cnt + h / 2, primitives_lcs[i][j]]
                    ],
                    transform_data,
                    [0, 0, 0, 0, 1, 1, 1, 1, 0, 0, 0, 0],
                    [
                        [], [], [], [],
                        [[0, 0, h_cnt - h / 2, 1]],
                        [[0, 0, h_cnt - h / 2, 1]],
                        [[0, 0, h_cnt + h / 2, 1]],
                        [[0, 0, h_cnt + h / 2, 1]],
                        [], [], [], []
                    ],
                    [
                        transfinite_r_data[j],
                        transfinite_r_data[j],
                        transfinite_r_data[j],
                        transfinite_r_data[j],
                        transfinite_phi_data,
                        transfinite_phi_data,
                        transfinite_phi_data,
                        transfinite_phi_data,
                        transfinite_h_data[i],
                        transfinite_h_data[i],
                        transfinite_h_data[i],
                        transfinite_h_data[i]
                    ],
                    transfinite_types[1],
                    layers_physical_names[i][j]
                ))
                # Layer Y
                primitives.append(Primitive(
                    factory,
                    [
                        [c2, c2, h_cnt - h / 2, primitives_lcs[i][j]],
                        [-c2, c2, h_cnt - h / 2, primitives_lcs[i][j]],
                        [-c1, c1, h_cnt - h / 2, primitives_lcs[i][j]],
                        [c1, c1, h_cnt - h / 2, primitives_lcs[i][j]],
                        [c2, c2, h_cnt + h / 2, primitives_lcs[i][j]],
                        [-c2, c2, h_cnt + h / 2, primitives_lcs[i][j]],
                        [-c1, c1, h_cnt + h / 2, primitives_lcs[i][j]],
                        [c1, c1, h_cnt + h / 2, primitives_lcs[i][j]]
                    ],
                    transform_data,
                    [1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0],
                    [
                        [[0, 0, h_cnt - h / 2, 1]],
                        [[0, 0, h_cnt + h / 2, 1]],
                        [[0, 0, h_cnt + h / 2, 1]],
                        [[0, 0, h_cnt - h / 2, 1]],
                        [], [], [], [],
                        [], [], [], []
                    ],
                    [
                        transfinite_phi_data,
                        transfinite_phi_data,
                        transfinite_phi_data,
                        transfinite_phi_data,
                        transfinite_r_data[j],
                        transfinite_r_data[j],
                        transfinite_r_data[j],
                        transfinite_r_data[j],
                        transfinite_h_data[i],
                        transfinite_h_data[i],
                        transfinite_h_data[i],
                        transfinite_h_data[i]
                    ],
                    transfinite_types[2],
                    layers_physical_names[i][j]
                ))
                # Layer NX
                if transfinite_r_data[j][1] == 0:  # If Progression type => reverse
                    kt = 1 / transfinite_r_data[j][2]
                else:
                    kt = transfinite_r_data[j][2]
                primitives.append(Primitive(
                    factory,
                    [
                        [-c1, c1, h_cnt - h / 2, primitives_lcs[i][j]],
                        [-c2, c2, h_cnt - h / 2, primitives_lcs[i][j]],
                        [-c2, -c2, h_cnt - h / 2, primitives_lcs[i][j]],
                        [-c1, -c1, h_cnt - h / 2, primitives_lcs[i][j]],
                        [-c1, c1, h_cnt + h / 2, primitives_lcs[i][j]],
                        [-c2, c2, h_cnt + h / 2, primitives_lcs[i][j]],
                        [-c2, -c2, h_cnt + h / 2, primitives_lcs[i][j]],
                        [-c1, -c1, h_cnt + h / 2, primitives_lcs[i][j]]
                    ],
                    transform_data,
                    [0, 0, 0, 0, 1, 1, 1, 1, 0, 0, 0, 0],
                    [
                        [], [], [], [],
                        [[0, 0, h_cnt - h / 2, 1]],
                        [[0, 0, h_cnt - h / 2, 1]],
                        [[0, 0, h_cnt + h / 2, 1]],
                        [[0, 0, h_cnt + h / 2, 1]],
                        [], [], [], []
                    ],
                    [
                        [transfinite_r_data[j][0], transfinite_r_data[j][1], kt],
                        [transfinite_r_data[j][0], transfinite_r_data[j][1], kt],
                        [transfinite_r_data[j][0], transfinite_r_data[j][1], kt],
                        [transfinite_r_data[j][0], transfinite_r_data[j][1], kt],
                        transfinite_phi_data,
                        transfinite_phi_data,
                        transfinite_phi_data,
                        transfinite_phi_data,
                        transfinite_h_data[i],
                        transfinite_h_data[i],
                        transfinite_h_data[i],
                        transfinite_h_data[i]
                    ],
                    transfinite_types[3],
                    layers_physical_names[i][j]
                ))
                # Layer NY
                if transfinite_r_data[j][1] == 0:  # If Progression type => reverse
                    kt = 1 / transfinite_r_data[j][2]
                else:
                    kt = transfinite_r_data[j][2]
                primitives.append(Primitive(
                    factory,
                    [
                        [c1, -c1, h_cnt - h / 2, primitives_lcs[i][j]],
                        [-c1, -c1, h_cnt - h / 2, primitives_lcs[i][j]],
                        [-c2, -c2, h_cnt - h / 2, primitives_lcs[i][j]],
                        [c2, -c2, h_cnt - h / 2, primitives_lcs[i][j]],
                        [c1, -c1, h_cnt + h / 2, primitives_lcs[i][j]],
                        [-c1, -c1, h_cnt + h / 2, primitives_lcs[i][j]],
                        [-c2, -c2, h_cnt + h / 2, primitives_lcs[i][j]],
                        [c2, -c2, h_cnt + h / 2, primitives_lcs[i][j]]
                    ],
                    transform_data,
                    [1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0],
                    [
                        [[0, 0, h_cnt - h / 2, 1]],
                        [[0, 0, h_cnt + h / 2, 1]],
                        [[0, 0, h_cnt + h / 2, 1]],
                        [[0, 0, h_cnt - h / 2, 1]],
                        [], [], [], [],
                        [], [], [], []
                    ],
                    [
                        transfinite_phi_data,
                        transfinite_phi_data,
                        transfinite_phi_data,
                        transfinite_phi_data,
                        [transfinite_r_data[j][0], transfinite_r_data[j][1], kt],
                        [transfinite_r_data[j][0], transfinite_r_data[j][1], kt],
                        [transfinite_r_data[j][0], transfinite_r_data[j][1], kt],
                        [transfinite_r_data[j][0], transfinite_r_data[j][1], kt],
                        transfinite_h_data[i],
                        transfinite_h_data[i],
                        transfinite_h_data[i],
                        transfinite_h_data[i]
                    ],
                    transfinite_types[4],
                    layers_physical_names[i][j]
                ))
            h_cnt += h / 2
            Complex.__init__(self, factory, primitives)
