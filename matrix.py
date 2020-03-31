import json
from pprint import pprint
import time

import gmsh

from complex import Complex
from primitive import Primitive
from support import check_file


class Matrix(Complex):
    def __init__(self, factory, xs, ys, zs, coordinates_type='direct',
                 lcs=None, transform_data=None, txs=None, tys=None, tzs=None,
                 type_map=None,
                 inputs=None, inputs_map=None,
                 volumes_names=None, volumes_map=None,
                 surfaces_names=None, surfaces_map=None,
                 recs_map=None, trans_map=None,
                 kwargs=None, kwargs_map=None):
        """
        Primitives, Complexes and Complex descendants
        as items of 3D matrix structure
        Items data structure (1D array):
        [Z0_Y0_X0, Z0_Y0_X1, ..., Z0_Y0_XN,
         Z0_Y1_X0, Z0_Y1_X1, ..., Z0_Y1_XN,
         ...
         Z0_YM_X0, Z0_YM_X1, ..., Z0_YM_XN,
         Z1_Y0_X0, Z1_Y0_X1, ..., Z1_Y0_XN,
         Z1_Y1_X0, Z1_Y1_X1, ..., Z1_Y1_XN,
         ...
         Z1_YM_X0, Z1_YM_X1, ..., Z1_YM_XN,
         ...
         ...
         ZP_YM_X0, Z0_YM_X1, ..., ZP_YM_XN]
        X0, X1, ..., XN - X layers, where N - number of X layers
        Y0, Y1, ..., YM - Y layers, where M - number of Y layers
        Z0, Z1, ..., ZP - Z layers, where P - number of Z layers
        :param str factory: see Primitive
        :param list of float xs: X axis coordinates
        :param list of float ys: Y axis coordinates
        :param list of float zs: Z axis coordinates
        :param str coordinates_type: 'direct' - exact coordinates or
        'delta' - coordinates differences
        :param list of float lcs: see Primitive
        :param list of float transform_data: see Primitive
        :param list of float txs: X axis transfinite_data (see Primitive)
        :param list of float tys: Y axis transfinite_data (see Primitive)
        :param list of float tzs: Z axis transfinite_data (see Primitive)
        :param list of int type_map: matrix item type (see type_factory below)
        :param list of str inputs: input files
        :param list of int inputs_map: item - input file map
        :param list of str volumes_names: names for items volumes
        :param list of int volumes_map: item - volume name map
        :param list of str surfaces_names: names for items surfaces
        :param list of int surfaces_map: item - surface names map
        :param list of int recs_map: see Primitive
        :param list of int trans_map: see Primitive
        """
        if factory == 'occ':
            factory_object = gmsh.model.occ
        else:
            factory_object = gmsh.model.geo
        if coordinates_type == 'delta':
            pass
        elif coordinates_type == 'direct':  # convert to delta
            xs = [xs[i] - xs[i - 1] for i in range(1, len(xs))]
            ys = [ys[i] - ys[i - 1] for i in range(1, len(ys))]
            zs = [zs[i] - zs[i - 1] for i in range(1, len(zs))]
        else:
            raise ValueError('coordinates_type: {}'.format(coordinates_type))
        nx = len(xs)
        ny = len(ys)
        nz = len(zs)
        ni = nx * ny * nz  # number of matrix items
        # print(nx, ny, nz, ni)
        if transform_data is None:
            transform_data = [0, 0, 0]
        if txs is None:
            txs = [[3, 0, 1] for _ in range(nx)]
        elif isinstance(txs, list) and not isinstance(txs[0], list):
            txs = [txs for _ in range(nx)]
        if tys is None:
            tys = [[3, 0, 1] for _ in range(ny)]
        elif isinstance(tys, list) and not isinstance(tys[0], list):
            tys = [tys for _ in range(ny)]
        if tzs is None:
            tzs = [[3, 0, 1] for _ in range(nz)]
        elif isinstance(tzs, list) and not isinstance(tzs[0], list):
            tzs = [tzs for _ in range(nz)]
        if lcs is None:
            lcs = [1 for _ in range(ni)]
        elif not isinstance(lcs, list):
            lcs = [lcs for _ in range(ni)]
        if type_map is None:
            type_map = [1 for _ in range(ni)]
        elif not isinstance(type_map, list):
            type_map = [type_map for _ in range(ni)]
        if inputs is None:
            inputs = ['input/test_matrix_item.json']
        if inputs_map is None:
            inputs_map = [0 for _ in range(ni)]
        if volumes_names is None:
            volumes_names = ['V']
        if volumes_map is None:
            volumes_map = [0 for _ in range(ni)]
        if surfaces_names is None:
            surfaces_names = [['NX', 'X', 'NY', 'Y', 'NZ', 'Z']]
        if surfaces_map is None:
            surfaces_map = [0 for _ in range(ni)]
        if recs_map is None:
            recs_map = [1 for _ in range(ni)]
        elif not isinstance(recs_map, list):
            recs_map = [recs_map for _ in range(ni)]
        if trans_map is None:
            trans_map = [1 for _ in range(ni)]
        elif not isinstance(trans_map, list):
            trans_map = [trans_map for _ in range(ni)]
        inputs_datas = []
        for inp in inputs:
            result = check_file(inp)
            with open(result['path']) as f:
                d = json.load(f)
            inputs_datas.append(d)
        # x0, y0, z0 - item start X, Y, Z
        # x1, y1, z1 - item end X, Y, Z
        # xc, yc, zc - item center X, Y, Z
        primitives = []
        for k in range(nz):
            for j in range(ny):
                for i in range(nx):
                    gi = i + nx * j + ny * nx * k
                    # print('{}/{}'.format(gi + 1, n))
                    x0 = sum(xs[:i]) + transform_data[0]
                    x1 = sum(xs[:i + 1]) + transform_data[0]
                    xc = 0.5 * (x0 + x1)
                    y0 = sum(ys[:j]) + transform_data[1]
                    y1 = sum(ys[:j + 1]) + transform_data[1]
                    yc = 0.5 * (y0 + y1)
                    z0 = sum(zs[:k]) + transform_data[2]
                    z1 = sum(zs[:k + 1]) + transform_data[2]
                    zc = 0.5 * (z0 + z1)
                    type_factory[type_map[gi]](**locals())
        Complex.__init__(self, factory, primitives)


# Empty
def type_0(**kwargs):
    pass


# Primitive
def type_1(primitives, i, j, k, gi, factory,
           x0, x1, y0, y1, z0, z1, lcs, txs, tys, tzs,
           volumes_names, volumes_map, surfaces_names, surfaces_map,
           recs_map, trans_map, **kwargs):
    primitives.append(Primitive(
        factory=factory,
        point_data=[
            [x1, y1, z0, lcs[gi]],
            [x0, y1, z0, lcs[gi]],
            [x0, y0, z0, lcs[gi]],
            [x1, y0, z0, lcs[gi]],
            [x1, y1, z1, lcs[gi]],
            [x0, y1, z1, lcs[gi]],
            [x0, y0, z1, lcs[gi]],
            [x1, y0, z1, lcs[gi]],
        ],
        transfinite_data=[txs[i], tys[j], tzs[k]],
        physical_name=volumes_names[volumes_map[gi]],
        surfaces_names=surfaces_names[surfaces_map[gi]],
        rec=recs_map[gi],
        trans=trans_map[gi]
    ))


# Complex at (xc, yc, zc)
def type_2(primitives, gi, factory,
           xc, yc, zc, inputs_datas, inputs_map, **kwargs):
    input_data = inputs_datas[inputs_map[gi]]
    transform_data = input_data['arguments'].setdefault('transform_data',
                                                        [0, 0, 0])
    transform_data[0] += xc
    transform_data[1] += yc
    transform_data[2] += zc
    input_data['arguments']['factory'] = factory
    from complex_factory import ComplexFactory
    c = ComplexFactory.new(input_data)
    primitives.extend(c.primitives)


# Complex at (xc, yc, z0)
def type_3(primitives, gi, factory,
           xc, yc, z0, inputs_datas, inputs_map, **kwargs):
    input_data = inputs_datas[inputs_map[gi]]
    transform_data = input_data['arguments'].setdefault('transform_data',
                                                        [0, 0, 0])
    transform_data[0] += xc
    transform_data[1] += yc
    transform_data[2] += z0
    input_data['arguments']['factory'] = factory
    from complex_factory import ComplexFactory
    c = ComplexFactory.new(input_data)
    primitives.extend(c.primitives)


# Complex at (x0, yc, z0)
def type_4(primitives, gi, factory,
           x0, yc, z0, inputs_datas, inputs_map, **kwargs):
    input_data = inputs_datas[inputs_map[gi]]
    transform_data = input_data['arguments'].setdefault('transform_data',
                                                        [0, 0, 0])
    transform_data[0] += x0
    transform_data[1] += yc
    transform_data[2] += z0
    input_data['arguments']['factory'] = factory
    from complex_factory import ComplexFactory
    c = ComplexFactory.new(input_data)
    primitives.extend(c.primitives)


# Complex in Primitive at (xc, yc, zc)
def type_5(primitives, i, j, k, gi, factory,
           x0, x1, xc, y0, y1, yc, z0, z1, zc, lcs, txs, tys, tzs,
           volumes_names, volumes_map, surfaces_names, surfaces_map,
           recs_map, trans_map, inputs_datas, inputs_map, **kwargs):
    input_data = inputs_datas[inputs_map[gi]]
    transform_data = input_data['arguments'].setdefault('transform_data',
                                                        [0, 0, 0])
    transform_data[0] += xc
    transform_data[1] += yc
    transform_data[2] += zc
    input_data['arguments']['factory'] = factory
    from complex_factory import ComplexFactory
    c = ComplexFactory.new(input_data)
    primitives.extend(c.primitives)
    primitives.append(Primitive(
        factory=factory,
        point_data=[
            [x1, y1, z0, lcs[gi]],
            [x0, y1, z0, lcs[gi]],
            [x0, y0, z0, lcs[gi]],
            [x1, y0, z0, lcs[gi]],
            [x1, y1, z1, lcs[gi]],
            [x0, y1, z1, lcs[gi]],
            [x0, y0, z1, lcs[gi]],
            [x1, y0, z1, lcs[gi]],
        ],
        transfinite_data=[txs[i], tys[j], tzs[k]],
        physical_name=volumes_names[volumes_map[gi]],
        inner_volumes=c.get_volumes(),
        surfaces_names=surfaces_names[surfaces_map[gi]],
        rec=recs_map[gi],
        trans=trans_map[gi]
    ))


def type_20(primitives, i, j, k, gi, factory,
            x0, x1, xc, y0, y1, yc, z0, z1, zc, lcs, txs, tys, tzs,
            volumes_names, volumes_map, surfaces_names, surfaces_map,
            recs_map, trans_map, xs, ys, transform_data, **kwargs):
    cxi = len(xs) // 2
    cyi = len(ys) // 2
    cx = sum(xs[:cxi]) + xs[cxi] / 2 + transform_data[0]
    cy = sum(ys[:cyi]) + ys[cyi] / 2 + transform_data[1]
    r1 = abs(x1 - cx)
    r1y1 = sum(ys[cyi:j + 2]) - ys[cyi] / 2
    r1y0 = sum(ys[:cyi]) + ys[cyi] / 2
    k1y1 = r1y1 / r1
    k1y0 = r1y0 / r1
    print(r1, r1y1, k1y1)
    print(r1, r1y0, k1y0)
    if k1y1 == 0 and k1y0 == 0:
        cts = [0, 0, 0, 0, 1, 0, 0, 1, 0, 0, 0, 0]
        cd = [
            [], [], [], [],
            [[cx, cy, z0, lcs[gi]]],
            [], [],
            [[cx, cy, z1, lcs[gi]]],
            [], [], [], []
        ]
    else:
        cts = [0, 0, 0, 0, 3, 0, 0, 3, 0, 0, 0, 0]
        cd = [
            [], [], [], [],
            [[x1, cy, z0, lcs[gi]]],
            [], [],
            [[x1, cy, z1, lcs[gi]]],
            [], [], [], []
        ]
    primitives.append(Primitive(
        factory=factory,
        point_data=[
            [cx + r1 / 2 ** 0.5, cy + k1y1 * r1 / 2 ** 0.5, z0, lcs[gi]],
            [x0, y1, z0, lcs[gi]],
            [x0, y0, z0, lcs[gi]],
            [cx + r1 / 2 ** 0.5, cy - k1y0 * r1 / 2 ** 0.5, z0, lcs[gi]],
            [cx + r1 / 2 ** 0.5, cy + k1y1 * r1 / 2 ** 0.5, z1, lcs[gi]],
            [x0, y1, z1, lcs[gi]],
            [x0, y0, z1, lcs[gi]],
            [cx + r1 / 2 ** 0.5, cy - k1y0 * r1 / 2 ** 0.5, z1, lcs[gi]]
        ],
        curve_types=cts,
        curve_data=cd,
        transfinite_data=[txs[i], tys[j], tzs[k]],
        transfinite_type=0,
        physical_name=volumes_names[volumes_map[gi]],
        surfaces_names=surfaces_names[surfaces_map[gi]],
        rec=recs_map[gi],
        trans=trans_map[gi]
    ))


def type_21(primitives, i, j, k, gi, factory,
            x0, x1, xc, y0, y1, yc, z0, z1, zc, lcs, txs, tys, tzs,
            volumes_names, volumes_map, surfaces_names, surfaces_map,
            recs_map, trans_map, xs, ys, transform_data, **kwargs):
    cxi = len(xs) // 2
    cyi = len(ys) // 2
    cx = sum(xs[:cxi]) + xs[cxi] / 2 + transform_data[0]
    cy = sum(ys[:cyi]) + ys[cyi] / 2 + transform_data[1]
    r1 = abs(y1 - cy)
    r1x1 = sum(xs[i:i + 2]) - xs[i] / 2
    k1x1 = r1x1 / r1
    if r1 == r1x1:
        cts = [1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        cd = [
            [[cx, cy, z0, 1]], [[cx, cy, z1, 1]], [], [],
            [], [], [], [],
            [], [], [], []
        ]
    else:
        cts = [3, 3, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        cd = [
            [[cx, y1, z0, 1]], [[cx, y1, z1, 1]], [], [],
            [], [], [], [],
            [], [], [], []
        ]
    primitives.append(Primitive(
        factory=factory,
        point_data=[
            [xc + k1x1 * r1 / 2 ** 0.5, cy + r1 / 2 ** 0.5, z0, lcs[gi]],
            [xc - r1 / 2 ** 0.5, cy + r1 / 2 ** 0.5, z0, lcs[gi]],
            [x0, y0, z0, lcs[gi]],
            [x1, y0, z0, lcs[gi]],
            [xc + k1x1 * r1 / 2 ** 0.5, cy + r1 / 2 ** 0.5, z1, lcs[gi]],
            [xc - r1 / 2 ** 0.5, cy + r1 / 2 ** 0.5, z1, lcs[gi]],
            [x0, y0, z1, lcs[gi]],
            [x1, y0, z1, lcs[gi]]
        ],
        curve_types=cts,
        curve_data=cd,
        transfinite_data=[txs[i], tys[j], tzs[k]],
        transfinite_type=0,
        physical_name=volumes_names[volumes_map[gi]],
        surfaces_names=surfaces_names[surfaces_map[gi]],
        rec=recs_map[gi],
        trans=trans_map[gi]
    ))


def type_22(primitives, i, j, k, gi, factory,
            x0, x1, xc, y0, y1, yc, z0, z1, zc, lcs, txs, tys, tzs,
            volumes_names, volumes_map, surfaces_names, surfaces_map,
            recs_map, trans_map, xs, ys, transform_data, **kwargs):
    cxi = len(xs) // 2
    cyi = len(ys) // 2
    cx = sum(xs[:cxi]) + xs[cxi] / 2 + transform_data[0]
    cy = sum(ys[:cyi]) + ys[cyi] / 2 + transform_data[1]
    r1 = abs(x1 - cx)
    r1y1 = sum(ys[cyi:j + 2]) - ys[cyi] / 2
    r1y0 = sum(ys[:cyi]) + ys[cyi] / 2
    k1y1 = r1y1 / r1
    k1y0 = r1y0 / r1
    print(r1, r1y1, k1y1)
    print(r1, r1y0, k1y0)
    if k1y1 == 0 and k1y0 == 0:
        cts = [0, 0, 0, 0, 0, 2, 2, 0, 0, 0, 0, 0]
        cd = [
            [], [], [], [],
            [], [[0, 0, z0, 1], [0, 0, z0, 1]],
            [[0, 0, z1, 1], [0, 0, z1, 1]], [],
            [], [], [], []
        ]
    else:
        cts = [0, 0, 0, 0, 3, 0, 0, 3, 0, 0, 0, 0]
        cd = [
            [], [], [], [],
            [[x1, cy, z0, lcs[gi]]],
            [], [],
            [[x1, cy, z1, lcs[gi]]],
            [], [], [], []
        ]
    primitives.append(Primitive(
        factory=factory,
        point_data=[
            [x1, y1, z0, lcs[gi]],
            [x0 / 2 ** 0.5, -ky1 * x0 / 2 ** 0.5, z0, lcs[gi]],
            [x0 / 2 ** 0.5, ky0 * x0 / 2 ** 0.5, z0, lcs[gi]],
            [x1, y0, z0, lcs[gi]],
            [x1, y1, z1, lcs[gi]],
            [x0 / 2 ** 0.5, -ky1 * x0 / 2 ** 0.5, z1, lcs[gi]],
            [x0 / 2 ** 0.5, ky0 * x0 / 2 ** 0.5, z1, lcs[gi]],
            [x1, y0, z1, lcs[gi]]
        ],
        curve_types=cts,
        curve_data=cd,
        transfinite_data=[txs[i], tys[j], tzs[k]],
        transfinite_type=1,
        physical_name=volumes_names[volumes_map[gi]],
        surfaces_names=surfaces_names[surfaces_map[gi]],
        rec=recs_map[gi],
        trans=trans_map[gi]
    ))


def type_23(primitives, i, j, k, gi, factory,
            x0, x1, xc, y0, y1, yc, z0, z1, zc, lcs, txs, tys, tzs,
            volumes_names, volumes_map, surfaces_names, surfaces_map,
            recs_map, trans_map, xs, ys, transform_data, **kwargs):
    cxi = len(xs) // 2
    cyi = len(ys) // 2
    cx = sum(xs[:cxi]) + xs[cxi] / 2 + transform_data[0]
    cy = sum(ys[:cyi]) + ys[cyi] / 2 + transform_data[1]
    r1 = abs(y0 - cy)
    r1x1 = sum(xs[i:i + 2]) - xs[i] / 2
    k1x1 = r1x1 / r1
    print(r1, r1x1, k1x1)
    if k1x1 == 0:
        cts = [0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0]
        cd = [
            [], [], [[cx, cy, z1, 1]], [[cx, cy, z0, 1]],
            [], [], [], [],
            [], [], [], []
        ]
    else:
        cts = [0, 0, 3, 3, 0, 0, 0, 0, 0, 0, 0, 0]
        cd = [
            [], [], [[cx, y0, z1, 1]], [[cx, y0, z0, 1]],
            [], [], [], [],
            [], [], [], []
        ]
    primitives.append(Primitive(
        factory=factory,
        point_data=[
            [x1, y1, z0, lcs[gi]],
            [x0, y1, z0, lcs[gi]],
            [cx - r1 / 2 ** 0.5, cy - r1 / 2 ** 0.5, z0, lcs[gi]],
            [cx + k1x1 * r1 / 2 ** 0.5, cy - r1 / 2 ** 0.5, z0, lcs[gi]],
            [x1, y1, z1, lcs[gi]],
            [x0, y1, z1, lcs[gi]],
            [cx - r1 / 2 ** 0.5, cy - r1 / 2 ** 0.5, z1, lcs[gi]],
            [cx + k1x1 * r1 / 2 ** 0.5, cy - r1 / 2 ** 0.5, z1, lcs[gi]]
        ],
        curve_types=cts,
        curve_data=cd,
        transfinite_data=[txs[i], tys[j], tzs[k]],
        transfinite_type=3,
        physical_name=volumes_names[volumes_map[gi]],
        surfaces_names=surfaces_names[surfaces_map[gi]],
        rec=recs_map[gi],
        trans=trans_map[gi]
    ))


type_factory = {
    0: type_0,  # Empty
    1: type_1,  # Primitive
    2: type_2,  # Complex at (xc, yc, zc)
    3: type_3,  # Complex at (xc, yc, z0)
    4: type_4,  # Complex at (x0, yc, z0)
    5: type_5,  # Complex in Primitive at (xc, yc, zc)
    20: type_20,  # Cylinder X|)
    21: type_21,  # Cylinder Y|)
    22: type_22,  # Cylinder NX|)
    23: type_23  # Cylinder NY|)
}
