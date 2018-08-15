import json
from pprint import pprint

import os

from complex_primitive import ComplexPrimitive
from primitive import Primitive, Complex
from support import get_volumes_geometry, get_geometry, check_geometry, initialize_geometry


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
    points_coordinates = list()
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
                        points_coordinates.append(coordinates)
                        coordinates = []
    return n_primitives, origins, rotations, points_coordinates


def parse_complex_type_2_json(path):
    with open(path) as f:
        d = json.load(f)
    # pprint(d)
    n_primitives = len(d)
    origins = list()
    rotations = list()
    points_coordinates = list()
    for primitive, data in d.items():
        origins.append(data['origin'])
        rotations.append(data['rotation'])
        points_coordinates.append(data['points'])
    return n_primitives, origins, rotations, points_coordinates


def prepare_complex_type_2(n_primitives, origins, rotations, points_coordinates, lc, transform_data):
    point_datas = list()
    new_transform_datas = list()
    for i in range(n_primitives):
        point_data = list()
        for c in points_coordinates[i]:
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
    basename, extension = os.path.splitext(path)
    if extension == '.json':
        n_primitives, origins, rotations, points_coordinates = parse_complex_type_2_json(path)
    else:
        n_primitives, origins, rotations, points_coordinates = parse_complex_type_2(path)
    point_datas, new_transform_datas = prepare_complex_type_2(
        n_primitives, origins, rotations, points_coordinates, lc, transform_data)
    primitives = list()
    for i in range(n_primitives):
        primitives.append(Primitive(
            factory,
            point_datas[i],
            new_transform_datas[i],
            transfinite_data=transfinite_data,
            physical_name=volume_name
        ))
    return Complex(factory, primitives)


def read_complex_type_2_to_complex_primitives(factory, path, divide_data, lc,
                                              transform_data, transfinite_data, volume_name=None):
    basename, extension = os.path.splitext(path)
    if extension == '.json':
        n_primitives, origins, rotations, points_coordinates = parse_complex_type_2_json(path)
    else:
        n_primitives, origins, rotations, points_coordinates = parse_complex_type_2(path)
    point_datas, new_transform_datas = prepare_complex_type_2(
        n_primitives, origins, rotations, points_coordinates, lc, transform_data)
    complex_primitives = list()
    for i in range(n_primitives):
        complex_primitives.append(ComplexPrimitive(
            factory,
            divide_data,
            point_datas[i],
            lc,
            new_transform_datas[i],
            transfinite_data=transfinite_data,
            physical_name=volume_name
        ))
    return complex_primitives


def write_json(filename, only_volume_entities=True):
    if only_volume_entities:
        geo = get_volumes_geometry()
    else:
        geo = get_geometry()
    geo_to_write = dict()
    print('Points')
    points_coordinates_to_write = dict()
    for k, v in geo['points'].items():
        new_v = [float(x) for x in v]
        points_coordinates_to_write[str(k)] = new_v
    geo_to_write['points'] = points_coordinates_to_write
    print('Edges')
    edges_points_to_write = dict()
    for k, v in geo['edges'].items():
        new_v = [int(x) for x in v]
        edges_points_to_write[str(k)] = new_v
    geo_to_write['edges'] = edges_points_to_write
    print('Surfaces')
    surfaces_edges_to_write = dict()
    for k, v in geo['surfaces'].items():
        new_v = [int(x) for x in v]
        surfaces_edges_to_write[str(k)] = new_v
    geo_to_write['surfaces'] = surfaces_edges_to_write
    print('Volumes')
    volumes_surfaces_to_write = dict()
    for k, v in geo['volumes'].items():
        new_v = [int(x) for x in v]
        volumes_surfaces_to_write[str(k)] = new_v
    geo_to_write['volumes'] = volumes_surfaces_to_write
    print('Write {}'.format(filename))
    # pprint(geo_to_write)
    with open('{}'.format(filename), 'w') as f:
        json.dump(geo_to_write, f, indent=2)


def read_json(factory, filename):
    print('Read File {}'.format(filename))
    with open(filename) as f:
        geo_from_read = json.load(f)
    geo = dict()
    print('Points')
    points_coordinates = dict()
    for k, v in geo_from_read['points'].items():
        new_v = [float(x) for x in v]
        points_coordinates[int(k)] = new_v
    geo['points'] = points_coordinates
    print('Edges')
    edges_points = dict()
    for k, v in geo_from_read['edges'].items():
        new_v = [int(x) for x in v]
        edges_points[int(k)] = new_v
    geo['edges'] = edges_points
    print('Surfaces')
    surfaces_edges = dict()
    for k, v in geo_from_read['surfaces'].items():
        new_v = [int(x) for x in v]
        surfaces_edges[int(k)] = new_v
    geo['surfaces'] = surfaces_edges
    print('Volumes')
    volumes_surfaces = dict()
    for k, v in geo_from_read['volumes'].items():
        new_v = [int(x) for x in v]
        volumes_surfaces[int(k)] = new_v
    geo['volumes'] = volumes_surfaces
    # pprint(geo)
    print('Check')
    check = check_geometry(geo, True)
    # pprint(check)
    print('Initialize')
    new_geo = initialize_geometry(factory, geo)
    # pprint(new_geo)
    return new_geo


