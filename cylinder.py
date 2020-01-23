import math
from complex import Complex
from primitive import Primitive


class Cylinder(Complex):
    def __init__(self, factory, radii, heights, layers_lcs, transform_data,
                 layers_physical_names, transfinite_r_data, transfinite_h_data,
                 transfinite_phi_data, straight_boundary=None,
                 layers_surfaces_names=None, surfaces_names=None,
                 volumes_names=None, layers_recs=None, layers_trans=None,
                 k=None):
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
        :param list of list of float layers_lcs: characteristic lengths
        of layers
        [[h1_r1, h1_r2, ..., h1_rN], [h2_r1, h2_r2, ..., h2_rN], ...,
        [hM_r1, hM_r2, ..., hM_rN]]
        :param list of float transform_data: relative to cylinder bottom
        (see Primitive)
        :param list of list of str layers_physical_names: physical names
        of layers
        [[h1_r1, h1_r2, ..., h1_rN], [h2_r1, h2_r2, ..., h2_rN], ...,
        [hM_r1, hM_r2, ..., hM_rN]]
        :param list of list of float transfinite_r_data: see Primitive
        [[number of r1 nodes, type, coefficient], [number of r2 nodes, type,
        coefficient], ...]
        :param list of list of float transfinite_h_data: see Primitive
        [[number of h1 nodes, type, coefficient], [number of h2 nodes, type,
        coefficient], ...]
        :param list of float transfinite_phi_data: see Primitive
        [number of circumferential nodes, type, coefficient]
        :param list of int straight_boundary: radii layers form of curves:
        0 - ||
        1 - |)
        2 - )|
        3 - ))
        :param list of list of int layers_surfaces_names: Like as layers_physical_names for surfaces
        :param list of list of str surfaces_names:  Names for use in layers_surfaces_names
        :param list of str volumes_names: Names for use in layers_physical_names
        :param list if list of int layers_recs: Recombine primitives? 1 - yes, 0 - no
        :param list if list of int layers_trans: Transfinite primitives? 1 - yes, 0 - no
        :param float k: quadrangle part of first layer radius
        :return None
        """
        primitives = []
        if k is None:
            k = 1 / 3.0  # inner quadrangle part of the first layer radius
        transfinite_types = [0, 0, 0, 1, 3]
        h_cnt = 0.0  # height counter
        if layers_lcs is None:
            layers_lcs = [[1 for _ in radii] for _ in heights]
        if layers_recs is None:
            layers_recs = [[1 for _ in radii] for _ in heights]
        if layers_trans is None:
            layers_trans = [[1 for _ in radii] for _ in heights]
        if surfaces_names is None:
            surfaces_names = [['NX', 'X', 'NY', 'Y', 'NZ', 'Z']]
        if layers_surfaces_names is None:
            layers_surfaces_names = [[0 for _ in radii] for _ in heights]
        if volumes_names is not None:
            new_layers_physical_names = [[volumes_names[x] for x in y]
                                         for y in layers_physical_names]
            layers_physical_names = new_layers_physical_names
        for i, h in enumerate(heights):
            c = radii[0] / math.sqrt(2.0)
            kc = k * radii[0] / math.sqrt(2.0)
            bottom_h = h_cnt  # primitive bottom h
            top_h = h_cnt + h  # primitive top h
            h_cnt += h
            if straight_boundary is None:
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
                    layers_physical_names[i][0],
                    surfaces_names=surfaces_names[layers_surfaces_names[i][0]],
                    rec=layers_recs[i][0],
                    trans=layers_trans[i][0]
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
                    layers_physical_names[i][0],
                    surfaces_names=surfaces_names[layers_surfaces_names[i][0]],
                    rec=layers_recs[i][0],
                    trans=layers_trans[i][0]
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
                    layers_physical_names[i][0],
                    surfaces_names=surfaces_names[layers_surfaces_names[i][0]],
                    rec=layers_recs[i][0],
                    trans=layers_trans[i][0]
                ))
                # Core NX
                if transfinite_r_data[0][
                    1] == 0:  # If type is Progression then reverse coefficient
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
                        [transfinite_r_data[0][0], transfinite_r_data[0][1],
                         rc],
                        transfinite_phi_data,
                        transfinite_h_data[i]
                    ],
                    transfinite_types[3],
                    layers_physical_names[i][0],
                    surfaces_names=surfaces_names[layers_surfaces_names[i][0]],
                    rec=layers_recs[i][0],
                    trans=layers_trans[i][0]
                ))
                # Core NY
                if transfinite_r_data[0][
                    1] == 0:  # If type is Progression then reverse coefficient
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
                        [transfinite_r_data[0][0], transfinite_r_data[0][1],
                         rc],
                        transfinite_h_data[i],
                    ],
                    transfinite_types[4],
                    layers_physical_names[i][0],
                    surfaces_names=surfaces_names[layers_surfaces_names[i][0]],
                    rec=layers_recs[i][0],
                    trans=layers_trans[i][0]
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
                        layers_physical_names[i][j],
                        surfaces_names=surfaces_names[
                            layers_surfaces_names[i][j]],
                        rec=layers_recs[i][j],
                        trans=layers_trans[i][j]
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
                        layers_physical_names[i][j],
                        surfaces_names=surfaces_names[
                            layers_surfaces_names[i][j]],
                        rec=layers_recs[i][j],
                        trans=layers_trans[i][j]
                    ))
                    # Layer NX
                    if transfinite_r_data[j][
                        1] == 0:  # If type is Progression then reverse coefficient
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
                            [transfinite_r_data[j][0], transfinite_r_data[j][1],
                             rc],
                            transfinite_phi_data,
                            transfinite_h_data[i]
                        ],
                        transfinite_types[3],
                        layers_physical_names[i][j],
                        surfaces_names=surfaces_names[
                            layers_surfaces_names[i][j]],
                        rec=layers_recs[i][j],
                        trans=layers_trans[i][j]
                    ))
                    # Layer NY
                    if transfinite_r_data[j][
                        1] == 0:  # If type is Progression then reverse coefficient
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
                            [transfinite_r_data[j][0], transfinite_r_data[j][1],
                             rc],
                            transfinite_h_data[i]
                        ],
                        transfinite_types[4],
                        layers_physical_names[i][j],
                        surfaces_names=surfaces_names[
                            layers_surfaces_names[i][j]],
                        rec=layers_recs[i][j],
                        trans=layers_trans[i][j]
                    ))
            else:
                if straight_boundary[0] == 0:
                    curve_types = {
                        'C': [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                        'X': [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                        'Y': [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                        'NX': [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                        'NY': [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
                    }
                elif straight_boundary[0] == 1:
                    curve_types = {
                        'C': [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                        'X': [0, 0, 0, 0, 1, 0, 0, 1, 0, 0, 0, 0],
                        'Y': [1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                        'NX': [0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0],
                        'NY': [0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0]
                    }
                elif straight_boundary[0] == 2:
                    curve_types = {
                        'C': [1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0],
                        'X': [0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0],
                        'Y': [0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0],
                        'NX': [0, 0, 0, 0, 1, 0, 0, 1, 0, 0, 0, 0],
                        'NY': [1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
                    }
                else:
                    curve_types = {
                        'C': [1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0],
                        'X': [0, 0, 0, 0, 1, 1, 1, 1, 0, 0, 0, 0],
                        'Y': [1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0],
                        'NX': [0, 0, 0, 0, 1, 1, 1, 1, 0, 0, 0, 0],
                        'NY': [1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0]
                    }
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
                    curve_types['C'],
                    [
                        [[0, 0, bottom_h, 1]],
                        [[0, 0, top_h, 1]],
                        [[0, 0, top_h, 1]],
                        [[0, 0, bottom_h, 1]],
                        [[0, 0, bottom_h, 1]],
                        [[0, 0, bottom_h, 1]],
                        [[0, 0, top_h, 1]],
                        [[0, 0, top_h, 1]],
                        [], [], [], []],
                    [
                        transfinite_phi_data,
                        transfinite_phi_data,
                        transfinite_h_data[i]
                    ],
                    transfinite_types[0],
                    layers_physical_names[i][0],
                    surfaces_names=surfaces_names[layers_surfaces_names[i][0]],
                    rec=layers_recs[i][0],
                    trans=layers_trans[i][0]
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
                    curve_types['X'],
                    [
                        [], [], [], [],
                        [[0, 0, bottom_h, 1]],
                        [[0, 0, bottom_h, 1]],
                        [[0, 0, top_h, 1]],
                        [[0, 0, top_h, 1]],
                        [], [], [], []
                    ],
                    [
                        transfinite_r_data[0],
                        transfinite_phi_data,
                        transfinite_h_data[i]
                    ],
                    transfinite_types[1],
                    layers_physical_names[i][0],
                    surfaces_names=surfaces_names[
                        layers_surfaces_names[i][0]],
                    rec=layers_recs[i][0],
                    trans=layers_trans[i][0]
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
                    curve_types['Y'],
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
                        transfinite_r_data[0],
                        transfinite_h_data[i],
                    ],
                    transfinite_types[2],
                    layers_physical_names[i][0],
                    surfaces_names=surfaces_names[layers_surfaces_names[i][0]],
                    rec=layers_recs[i][0],
                    trans=layers_trans[i][0]
                ))
                # Core NX
                if transfinite_r_data[0][
                    1] == 0:  # If type is Progression then reverse coefficient
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
                    curve_types['NX'],
                    [
                        [], [], [], [],
                        [[0, 0, bottom_h, 1]],
                        [[0, 0, bottom_h, 1]],
                        [[0, 0, top_h, 1]],
                        [[0, 0, top_h, 1]],
                        [], [], [], []
                    ],
                    [
                        [transfinite_r_data[0][0], transfinite_r_data[0][1],
                         rc],
                        transfinite_phi_data,
                        transfinite_h_data[i]
                    ],
                    transfinite_types[3],
                    layers_physical_names[i][0],
                    surfaces_names=surfaces_names[layers_surfaces_names[i][0]],
                    rec=layers_recs[i][0],
                    trans=layers_trans[i][0]
                ))
                # Core NY
                if transfinite_r_data[0][
                    1] == 0:  # If type is Progression then reverse coefficient
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
                    curve_types['NY'],
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
                        [transfinite_r_data[0][0], transfinite_r_data[0][1],
                         rc],
                        transfinite_h_data[i],
                    ],
                    transfinite_types[4],
                    layers_physical_names[i][0],
                    surfaces_names=surfaces_names[layers_surfaces_names[i][0]],
                    rec=layers_recs[i][0],
                    trans=layers_trans[i][0]
                ))
                # Layers
                for j in range(1, len(radii)):
                    if straight_boundary[j] == 0:
                        curve_types = {
                            'X': [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                            'Y': [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                            'NX': [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                            'NY': [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
                        }
                    elif straight_boundary[j] == 1:
                        curve_types = {
                            'X': [0, 0, 0, 0, 1, 0, 0, 1, 0, 0, 0, 0],
                            'Y': [1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                            'NX': [0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0],
                            'NY': [0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0]
                        }
                    elif straight_boundary[j] == 2:
                        curve_types = {
                            'X': [0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0],
                            'Y': [0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0],
                            'NX': [0, 0, 0, 0, 1, 0, 0, 1, 0, 0, 0, 0],
                            'NY': [1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
                        }
                    else:
                        curve_types = {
                            'X': [0, 0, 0, 0, 1, 1, 1, 1, 0, 0, 0, 0],
                            'Y': [1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0],
                            'NX': [0, 0, 0, 0, 1, 1, 1, 1, 0, 0, 0, 0],
                            'NY': [1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0]
                        }
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
                        curve_types['X'],
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
                        layers_physical_names[i][j],
                        surfaces_names=surfaces_names[
                            layers_surfaces_names[i][j]],
                        rec=layers_recs[i][j],
                        trans=layers_trans[i][j]
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
                        curve_types['Y'],
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
                        layers_physical_names[i][j],
                        surfaces_names=surfaces_names[
                            layers_surfaces_names[i][j]],
                        rec=layers_recs[i][j],
                        trans=layers_trans[i][j]
                    ))
                    # Layer NX
                    if transfinite_r_data[j][
                        1] == 0:  # If type is Progression then reverse coefficient
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
                        curve_types['NX'],
                        [
                            [], [], [], [],
                            [[0, 0, bottom_h, 1]],
                            [[0, 0, bottom_h, 1]],
                            [[0, 0, top_h, 1]],
                            [[0, 0, top_h, 1]],
                            [], [], [], []
                        ],
                        [
                            [transfinite_r_data[j][0],
                             transfinite_r_data[j][1], rc],
                            transfinite_phi_data,
                            transfinite_h_data[i]
                        ],
                        transfinite_types[3],
                        layers_physical_names[i][j],
                        surfaces_names=surfaces_names[
                            layers_surfaces_names[i][j]],
                        rec=layers_recs[i][j],
                        trans=layers_trans[i][j]
                    ))
                    # Layer NY
                    if transfinite_r_data[j][
                        1] == 0:  # If type is Progression then reverse coefficient
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
                        curve_types['NY'],
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
                            [transfinite_r_data[j][0],
                             transfinite_r_data[j][1], rc],
                            transfinite_h_data[i]
                        ],
                        transfinite_types[4],
                        layers_physical_names[i][j],
                        surfaces_names=surfaces_names[
                            layers_surfaces_names[i][j]],
                        rec=layers_recs[i][j],
                        trans=layers_trans[i][j]
                    ))
        Complex.__init__(self, factory, primitives)
