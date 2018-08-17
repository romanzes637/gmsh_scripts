import math
from complex import Complex
from primitive import Primitive


class Cylinder(Complex):
    def __init__(self, factory, radii, heights, layers_lcs, transform_data, layers_physical_names,
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
        :param str factory: see Primitive
        :param list of float radii: layers outer radii [r1, r2, ..., rN]
        :param list of float heights: layers heights [h1, h2, ..., hM]
        :param list of list of float layers_lcs: characteristic lengths of layers
        [[h1_r1, h1_r2, ..., h1_rN], [h2_r1, h2_r2, ..., h2_rN], ..., [hM_r1, hM_r2, ..., hM_rN]]
        :param list of float transform_data: relative to cylinder bottom (see Primitive)
        :param list of list of str layers_physical_names: physical names of layers
        [[h1_r1, h1_r2, ..., h1_rN], [h2_r1, h2_r2, ..., h2_rN], ..., [hM_r1, hM_r2, ..., hM_rN]]
        :param list of list of float transfinite_r_data: see Primitive
        [[number of r1 nodes, type, coefficient], [number of r2 nodes, type, coefficient], ...]
        :param list of list of float transfinite_h_data: see Primitive
        [[number of h1 nodes, type, coefficient], [number of h2 nodes, type, coefficient], ...]
        :param list of float transfinite_phi_data: see Primitive
        [number of circumferential nodes, type, coefficient]
        :return None
        """
        primitives = []
        k = 1 / 3.0  # inner quadrangle part of the first layer radius
        transfinite_types = [0, 0, 0, 1, 3]
        h_cnt = 0.0  # height counter
        for i, h in enumerate(heights):
            c = radii[0] / math.sqrt(2.0)
            kc = k * radii[0] / math.sqrt(2.0)
            bottom_h = h_cnt  # primitive bottom h
            top_h = h_cnt + h  # primitive top h
            h_cnt += h
            # Core center
            primitives.append(Primitive(
                factory,
                [
                    [kc, kc, bottom_h, layers_lcs[i][0]],
                    [-kc, kc, bottom_h, layers_lcs[i][0]],
                    [-kc, -kc, bottom_h, layers_lcs[i][0]],
                    [kc, -kc, bottom_h, layers_lcs[i][0]],
                    [kc, kc, top_h, layers_lcs[i][0]],
                    [-kc, kc, top_h, layers_lcs[i][0]],
                    [-kc, -kc, top_h, layers_lcs[i][0]],
                    [kc, -kc, top_h, layers_lcs[i][0]]
                ],
                transform_data,
                [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                [[], [], [], [], [], [], [], [], [], [], [], []],
                [
                    transfinite_phi_data,
                    transfinite_phi_data,
                    transfinite_h_data[i]
                ],
                transfinite_types[0],
                layers_physical_names[i][0]
            ))
            # Core X
            primitives.append(Primitive(
                factory,
                [
                    [c, c, bottom_h, layers_lcs[i][0]],
                    [kc, kc, bottom_h, layers_lcs[i][0]],
                    [kc, -kc, bottom_h, layers_lcs[i][0]],
                    [c, -c, bottom_h, layers_lcs[i][0]],
                    [c, c, top_h, layers_lcs[i][0]],
                    [kc, kc, top_h, layers_lcs[i][0]],
                    [kc, -kc, top_h, layers_lcs[i][0]],
                    [c, -c, top_h, layers_lcs[i][0]]
                ],
                transform_data,
                [0, 0, 0, 0, 1, 0, 0, 1, 0, 0, 0, 0],
                [
                    [], [], [], [],
                    [[0, 0, bottom_h, 1]], [], [], [[0, 0, top_h, 1]],
                    [], [], [], []
                ],
                [
                    transfinite_r_data[0],
                    transfinite_phi_data,
                    transfinite_h_data[i]
                ],
                transfinite_types[1],
                layers_physical_names[i][0]
            ))
            # Core Y
            primitives.append(Primitive(
                factory,
                [
                    [c, c, bottom_h, layers_lcs[i][0]],
                    [-c, c, bottom_h, layers_lcs[i][0]],
                    [-kc, kc, bottom_h, layers_lcs[i][0]],
                    [kc, kc, bottom_h, layers_lcs[i][0]],
                    [c, c, top_h, layers_lcs[i][0]],
                    [-c, c, top_h, layers_lcs[i][0]],
                    [-kc, kc, top_h, layers_lcs[i][0]],
                    [kc, kc, top_h, layers_lcs[i][0]]
                ],
                transform_data,
                [1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                [
                    [[0, 0, bottom_h, 1]], [[0, 0, top_h, 1]], [], [],
                    [], [], [], [],
                    [], [], [], []
                ],
                [
                    transfinite_phi_data,
                    transfinite_r_data[0],
                    transfinite_h_data[i],
                ],
                transfinite_types[2],
                layers_physical_names[i][0]
            ))
            # Core NX
            if transfinite_r_data[0][1] == 0:  # If type is Progression then reverse coefficient
                rc = 1.0 / transfinite_r_data[0][2]
            else:
                rc = transfinite_r_data[0][2]
            primitives.append(Primitive(
                factory,
                [
                    [-kc, kc, bottom_h, layers_lcs[i][0]],
                    [-c, c, bottom_h, layers_lcs[i][0]],
                    [-c, -c, bottom_h, layers_lcs[i][0]],
                    [-kc, -kc, bottom_h, layers_lcs[i][0]],
                    [-kc, kc, top_h, layers_lcs[i][0]],
                    [-c, c, top_h, layers_lcs[i][0]],
                    [-c, -c, top_h, layers_lcs[i][0]],
                    [-kc, -kc, top_h, layers_lcs[i][0]]
                ],
                transform_data,
                [0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0],
                [
                    [], [], [], [],
                    [], [[0, 0, bottom_h, 1]], [[0, 0, top_h, 1]], [],
                    [], [], [], []
                ],
                [
                    [transfinite_r_data[0][0], transfinite_r_data[0][1], rc],
                    transfinite_phi_data,
                    transfinite_h_data[i]
                ],
                transfinite_types[3],
                layers_physical_names[i][0]
            ))
            # Core NY
            if transfinite_r_data[0][1] == 0:  # If type is Progression then reverse coefficient
                rc = 1.0 / transfinite_r_data[0][2]
            else:
                rc = transfinite_r_data[0][2]
            primitives.append(Primitive(
                factory,
                [
                    [kc, -kc, bottom_h, layers_lcs[i][0]],
                    [-kc, -kc, bottom_h, layers_lcs[i][0]],
                    [-c, -c, bottom_h, layers_lcs[i][0]],
                    [c, -c, bottom_h, layers_lcs[i][0]],
                    [kc, -kc, top_h, layers_lcs[i][0]],
                    [-kc, -kc, top_h, layers_lcs[i][0]],
                    [-c, -c, top_h, layers_lcs[i][0]],
                    [c, -c, top_h, layers_lcs[i][0]]
                ],
                transform_data,
                [0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0],
                [
                    [], [], [[0, 0, top_h, 1]], [[0, 0, bottom_h, 1]],
                    [], [], [], [],
                    [], [], [], []
                ],
                [
                    transfinite_phi_data,
                    [transfinite_r_data[0][0], transfinite_r_data[0][1], rc],
                    transfinite_h_data[i],
                ],
                transfinite_types[4],
                layers_physical_names[i][0]
            ))
            # Layers
            for j in range(1, len(radii)):
                c1 = radii[j - 1] / math.sqrt(2.0)
                c2 = radii[j] / math.sqrt(2.0)
                # Layer X
                primitives.append(Primitive(
                    factory,
                    [
                        [c2, c2, bottom_h, layers_lcs[i][j]],
                        [c1, c1, bottom_h, layers_lcs[i][j]],
                        [c1, -c1, bottom_h, layers_lcs[i][j]],
                        [c2, -c2, bottom_h, layers_lcs[i][j]],
                        [c2, c2, top_h, layers_lcs[i][j]],
                        [c1, c1, top_h, layers_lcs[i][j]],
                        [c1, -c1, top_h, layers_lcs[i][j]],
                        [c2, -c2, top_h, layers_lcs[i][j]]
                    ],
                    transform_data,
                    [0, 0, 0, 0, 1, 1, 1, 1, 0, 0, 0, 0],
                    [
                        [], [], [], [],
                        [[0, 0, bottom_h, 1]],
                        [[0, 0, bottom_h, 1]],
                        [[0, 0, top_h, 1]],
                        [[0, 0, top_h, 1]],
                        [], [], [], []
                    ],
                    [
                        transfinite_r_data[j],
                        transfinite_phi_data,
                        transfinite_h_data[i]
                    ],
                    transfinite_types[1],
                    layers_physical_names[i][j]
                ))
                # Layer Y
                primitives.append(Primitive(
                    factory,
                    [
                        [c2, c2, bottom_h, layers_lcs[i][j]],
                        [-c2, c2, bottom_h, layers_lcs[i][j]],
                        [-c1, c1, bottom_h, layers_lcs[i][j]],
                        [c1, c1, bottom_h, layers_lcs[i][j]],
                        [c2, c2, top_h, layers_lcs[i][j]],
                        [-c2, c2, top_h, layers_lcs[i][j]],
                        [-c1, c1, top_h, layers_lcs[i][j]],
                        [c1, c1, top_h, layers_lcs[i][j]]
                    ],
                    transform_data,
                    [1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0],
                    [
                        [[0, 0, bottom_h, 1]],
                        [[0, 0, top_h, 1]],
                        [[0, 0, top_h, 1]],
                        [[0, 0, bottom_h, 1]],
                        [], [], [], [],
                        [], [], [], []
                    ],
                    [
                        transfinite_phi_data,
                        transfinite_r_data[j],
                        transfinite_h_data[i]
                    ],
                    transfinite_types[2],
                    layers_physical_names[i][j]
                ))
                # Layer NX
                if transfinite_r_data[j][1] == 0:  # If type is Progression then reverse coefficient
                    rc = 1.0 / transfinite_r_data[j][2]
                else:
                    rc = transfinite_r_data[j][2]
                primitives.append(Primitive(
                    factory,
                    [
                        [-c1, c1, bottom_h, layers_lcs[i][j]],
                        [-c2, c2, bottom_h, layers_lcs[i][j]],
                        [-c2, -c2, bottom_h, layers_lcs[i][j]],
                        [-c1, -c1, bottom_h, layers_lcs[i][j]],
                        [-c1, c1, top_h, layers_lcs[i][j]],
                        [-c2, c2, top_h, layers_lcs[i][j]],
                        [-c2, -c2, top_h, layers_lcs[i][j]],
                        [-c1, -c1, top_h, layers_lcs[i][j]]
                    ],
                    transform_data,
                    [0, 0, 0, 0, 1, 1, 1, 1, 0, 0, 0, 0],
                    [
                        [], [], [], [],
                        [[0, 0, bottom_h, 1]],
                        [[0, 0, bottom_h, 1]],
                        [[0, 0, top_h, 1]],
                        [[0, 0, top_h, 1]],
                        [], [], [], []
                    ],
                    [
                        [transfinite_r_data[j][0], transfinite_r_data[j][1], rc],
                        transfinite_phi_data,
                        transfinite_h_data[i]
                    ],
                    transfinite_types[3],
                    layers_physical_names[i][j]
                ))
                # Layer NY
                if transfinite_r_data[j][1] == 0:  # If type is Progression then reverse coefficient
                    rc = 1.0 / transfinite_r_data[j][2]
                else:
                    rc = transfinite_r_data[j][2]
                primitives.append(Primitive(
                    factory,
                    [
                        [c1, -c1, bottom_h, layers_lcs[i][j]],
                        [-c1, -c1, bottom_h, layers_lcs[i][j]],
                        [-c2, -c2, bottom_h, layers_lcs[i][j]],
                        [c2, -c2, bottom_h, layers_lcs[i][j]],
                        [c1, -c1, top_h, layers_lcs[i][j]],
                        [-c1, -c1, top_h, layers_lcs[i][j]],
                        [-c2, -c2, top_h, layers_lcs[i][j]],
                        [c2, -c2, top_h, layers_lcs[i][j]]
                    ],
                    transform_data,
                    [1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0],
                    [
                        [[0, 0, bottom_h, 1]],
                        [[0, 0, top_h, 1]],
                        [[0, 0, top_h, 1]],
                        [[0, 0, bottom_h, 1]],
                        [], [], [], [],
                        [], [], [], []
                    ],
                    [
                        transfinite_phi_data,
                        [transfinite_r_data[j][0], transfinite_r_data[j][1], rc],
                        transfinite_h_data[i]
                    ],
                    transfinite_types[4],
                    layers_physical_names[i][j]
                ))
        Complex.__init__(self, factory, primitives)
