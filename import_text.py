from complex_primitive import ComplexPrimitive
from primitive import Primitive, Complex


def read_complex_type_1(factory, path, transform_data, curve_type, transfinite_data, physical_tag, lc):
    primitives_curves = []
    origins = []
    rotations = []
    curves = []
    cnt = 0
    with open(path) as f:
        for line in f:
            if not line.startswith("#" or "//"):
                tokens = line.split()
                # print(tokens)
                if len(tokens) > 0:
                    cnt += 1
                    if cnt == 1:
                        origins.append(map(lambda x: float(x), tokens))
                    elif cnt == 2:
                        rotations.append(map(lambda x: float(x), tokens))
                    else:
                        curve = []
                        cs = map(lambda x: float(x), tokens)
                        point_cs = []
                        cs_cnt = 0
                        for c in cs:
                            cs_cnt += 1
                            point_cs.append(c)
                            if cs_cnt == 3:
                                cs_cnt = 0
                                curve.append(point_cs)
                                point_cs = []
                        curves.append(curve)
                    if cnt == 14:
                        cnt = 0
                        primitives_curves.append(curves)
                        curves = []
    primitives = []
    physical_data = []
    lcs = []
    for i in range(len(origins)):
        p0 = list(primitives_curves[i][8][0])
        p1 = list(primitives_curves[i][0][0])
        p2 = list(primitives_curves[i][3][0])
        p3 = list(primitives_curves[i][4][0])
        p4 = list(primitives_curves[i][1][len(primitives_curves[i][1]) - 1])
        p5 = list(primitives_curves[i][1][0])
        p6 = list(primitives_curves[i][6][0])
        p7 = list(primitives_curves[i][7][0])
        p0.append(float(lc))
        p1.append(float(lc))
        p2.append(float(lc))
        p3.append(float(lc))
        p4.append(float(lc))
        p5.append(float(lc))
        p6.append(float(lc))
        p7.append(float(lc))
        point_data = [p0, p1, p2, p3, p4, p5, p6, p7]
        curve_data = []
        curve_types = []
        for j in range(len(primitives_curves[i])):
            points = []
            n_points = len(primitives_curves[i][j])
            if n_points > 2:
                for k in range(1, n_points - 1):
                    point_with_lc = list(primitives_curves[i][j][k])
                    point_with_lc.append(float(lc))
                    points.append(point_with_lc)
                curve_data.append(points)
                curve_types.append(curve_type)
            else:
                curve_data.append([])
                curve_types.append(0)
        t_form_data = []
        t_form_data.append(origins[i][0] + transform_data[0])
        t_form_data.append(origins[i][1] + transform_data[1])
        t_form_data.append(origins[i][2] + transform_data[2])
        if len(rotations[i]) == 3:
            t_form_data.append(t_form_data[0])
            t_form_data.append(t_form_data[1])
            t_form_data.append(t_form_data[2])
            t_form_data.append(rotations[i][0])
            t_form_data.append(rotations[i][1])
            t_form_data.append(rotations[i][2])
        elif len(rotations[i]) == 4:
            t_form_data.append(rotations[i][0])
            t_form_data.append(rotations[i][1])
            t_form_data.append(rotations[i][2])
            t_form_data.append(rotations[i][3])
        t_finite_data = [
            [transfinite_data[0], 0, 1],
            [transfinite_data[0], 0, 1],
            [transfinite_data[0], 0, 1],
            [transfinite_data[0], 0, 1],
            [transfinite_data[1], 0, 1],
            [transfinite_data[1], 0, 1],
            [transfinite_data[1], 0, 1],
            [transfinite_data[1], 0, 1],
            [transfinite_data[2], 0, 1],
            [transfinite_data[2], 0, 1],
            [transfinite_data[2], 0, 1],
            [transfinite_data[2], 0, 1],
        ]
        t_finite_type = 0
        primitives.append(Primitive(
            factory,
            point_data,
            t_form_data,
            curve_types,
            curve_data,
            t_finite_data,
            t_finite_type
        ))
        physical_data.append(physical_tag)
        lcs.append(lc)
    return Complex(factory, primitives, physical_data, lcs)


def parse_complex_type_2(path):
    n_primitives = 0
    origins = list()
    rotations = list()
    coordinates = list()
    primitives_cs = list()
    cnt = 0
    with open(path) as f:
        for line in f:
            if not line.startswith("#"):
                tokens = line.split()
                # print(tokens)
                if len(tokens) > 0:
                    cnt += 1
                    if cnt == 1:
                        origins.append(map(lambda x: float(x), tokens))
                    elif cnt == 2:
                        rotations.append(map(lambda x: float(x), tokens))
                    else:
                        coordinates.append(map(lambda x: float(x), tokens))
                    if cnt == 10:
                        cnt = 0
                        n_primitives += 1
                        primitives_cs.append(coordinates)
                        coordinates = []
    return n_primitives, origins, rotations, primitives_cs


def prepare_complex_type_2(n_primitives, origins, rotations, primitives_cs, lc, transform_data):
    point_datas = list()
    new_transform_datas = list()
    for i in range(n_primitives):
        point_data = list()
        for c in primitives_cs[i]:
            point = c
            point.append(lc)
            point_data.append(point)
        new_transform_data = map(lambda x, y: x + y, origins[i], transform_data)
        if len(rotations[i]) == 3:
            new_transform_data.extend(new_transform_data)
            new_transform_data.extend(rotations[i])
        elif len(rotations[i]) == 4:
            new_transform_data.extend(rotations[i])
        point_datas.append(point_data)
        new_transform_datas.append(new_transform_data)
    return point_datas, new_transform_datas


def read_complex_type_2(factory, path, lc, transform_data, transfinite_data, volume_name=None):
    n_primitives, origins, rotations, primitives_cs = parse_complex_type_2(path)
    point_datas, new_transform_datas = prepare_complex_type_2(
        n_primitives, origins, rotations, primitives_cs, lc, transform_data)
    primitives = list()
    for i in range(n_primitives):
        primitives.append(Primitive(
            factory,
            point_datas[i],
            new_transform_datas[i],
            transfinite_data=transfinite_data,
            volume_name=volume_name
        ))
    return Complex(factory, primitives)


def read_complex_type_2_to_complex_primitives(
        factory, path, divide_data, lc, transform_data, transfinite_data, volume_name=None):
    n_primitives, origins, rotations, primitives_cs = parse_complex_type_2(path)
    point_datas, new_transform_datas = prepare_complex_type_2(
        n_primitives, origins, rotations, primitives_cs, lc, transform_data)
    complex_primitives = list()
    for i in range(n_primitives):
        complex_primitives.append(ComplexPrimitive(
            factory,
            divide_data,
            point_datas[i],
            lc,
            new_transform_datas[i],
            transfinite_data=transfinite_data,
            volume_name=volume_name
        ))
    return complex_primitives
