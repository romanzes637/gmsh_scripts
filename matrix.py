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
                 kws=None, kws_map=None):
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
        :param list of dict kws: keyword arguments for matrix items
        :param list of int kws_map: matrix item keyword arguments map
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
        elif not isinstance(inputs, list):
            inputs = [inputs]
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
        if kws is None:
            kws = [{}]
        elif not isinstance(kws, list):
            kws = [kws]
        if kws_map is None:
            kws_map = [0 for _ in range(ni)]
        elif not isinstance(kws_map, list):
            kws_map = [kws_map for _ in range(ni)]
        # x0, y0, z0 - item start X, Y, Z
        # x1, y1, z1 - item end X, Y, Z
        # xc, yc, zc - item center X, Y, Z
        gis = {}
        x0s, x1s, xcs = [], [], []
        y0s, y1s, ycs = [], [], []
        z0s, z1s, zcs = [], [], []
        for k in range(nz):
            for j in range(ny):
                for i in range(nx):
                    gis[(i, j, k)] = i + nx * j + ny * nx * k
                    x0s.append(sum(xs[:i]) + transform_data[0])
                    x1s.append(sum(xs[:i + 1]) + transform_data[0])
                    xcs.append(0.5 * (x0s[-1] + x1s[-1]))
                    y0s.append(sum(ys[:j]) + transform_data[1])
                    y1s.append(sum(ys[:j + 1]) + transform_data[1])
                    ycs.append(0.5 * (y0s[-1] + y1s[-1]))
                    z0s.append(sum(zs[:k]) + transform_data[2])
                    z1s.append(sum(zs[:k + 1]) + transform_data[2])
                    zcs.append(0.5 * (z0s[-1] + z1s[-1]))
        primitives = []
        for ci, gi in gis.items():
            type_factory[type_map[gi]](**locals())
        Complex.__init__(self, factory, primitives)


# Empty
def type_0(**kwargs):
    pass


# Primitive
def type_1(primitives, ci, gi, factory,
           x0s, x1s, y0s, y1s, z0s, z1s, lcs, txs, tys, tzs,
           volumes_names, volumes_map, surfaces_names, surfaces_map,
           recs_map, trans_map, **kwargs):
    i, j, k = ci
    primitives.append(Primitive(
        factory=factory,
        point_data=[
            [x1s[gi], y1s[gi], z0s[gi], lcs[gi]],
            [x0s[gi], y1s[gi], z0s[gi], lcs[gi]],
            [x0s[gi], y0s[gi], z0s[gi], lcs[gi]],
            [x1s[gi], y0s[gi], z0s[gi], lcs[gi]],
            [x1s[gi], y1s[gi], z1s[gi], lcs[gi]],
            [x0s[gi], y1s[gi], z1s[gi], lcs[gi]],
            [x0s[gi], y0s[gi], z1s[gi], lcs[gi]],
            [x1s[gi], y0s[gi], z1s[gi], lcs[gi]],
        ],
        transfinite_data=[txs[i], tys[j], tzs[k]],
        physical_name=volumes_names[volumes_map[gi]],
        surfaces_names=surfaces_names[surfaces_map[gi]],
        rec=recs_map[gi],
        trans=trans_map[gi]
    ))


# Complex at (xc, yc, zc)
def type_2(primitives, gi, factory,
           xcs, ycs, zcs, inputs_datas, inputs_map, **kwargs):
    input_data = inputs_datas[inputs_map[gi]]
    transform_data = input_data['arguments'].setdefault('transform_data',
                                                        [0, 0, 0])
    transform_data[0] += xcs[gi]
    transform_data[1] += ycs[gi]
    transform_data[2] += zcs[gi]
    input_data['arguments']['factory'] = factory
    from complex_factory import ComplexFactory
    c = ComplexFactory.new(input_data)
    primitives.extend(c.primitives)


# Complex at (xc, yc, z0)
def type_3(primitives, gi, factory,
           xcs, ycs, z0s, inputs_datas, inputs_map, **kwargs):
    input_data = inputs_datas[inputs_map[gi]]
    transform_data = input_data['arguments'].setdefault('transform_data',
                                                        [0, 0, 0])
    transform_data[0] += xcs[gi]
    transform_data[1] += ycs[gi]
    transform_data[2] += z0s[gi]
    input_data['arguments']['factory'] = factory
    from complex_factory import ComplexFactory
    c = ComplexFactory.new(input_data)
    primitives.extend(c.primitives)


# Complex at (x0, yc, z0)
def type_4(primitives, gi, factory,
           x0s, ycs, z0s, inputs_datas, inputs_map, **kwargs):
    input_data = inputs_datas[inputs_map[gi]]
    transform_data = input_data['arguments'].setdefault('transform_data',
                                                        [0, 0, 0])
    transform_data[0] += x0s[gi]
    transform_data[1] += ycs[gi]
    transform_data[2] += z0s[gi]
    input_data['arguments']['factory'] = factory
    from complex_factory import ComplexFactory
    c = ComplexFactory.new(input_data)
    primitives.extend(c.primitives)


# Complex in Primitive at (xc, yc, zc)
def type_5(primitives, ci, gi, factory,
           x0s, x1s, xcs, y0s, y1s, ycs, z0s, z1s, zcs, lcs, txs, tys, tzs,
           volumes_names, volumes_map, surfaces_names, surfaces_map,
           recs_map, trans_map, inputs_datas, inputs_map, **kwargs):
    i, j, k = ci
    input_data = inputs_datas[inputs_map[gi]]
    transform_data = input_data['arguments'].setdefault('transform_data',
                                                        [0, 0, 0])
    transform_data[0] += xcs[gi]
    transform_data[1] += ycs[gi]
    transform_data[2] += zcs[gi]
    input_data['arguments']['factory'] = factory
    from complex_factory import ComplexFactory
    c = ComplexFactory.new(input_data)
    primitives.extend(c.primitives)
    primitives.append(Primitive(
        factory=factory,
        point_data=[
            [x1s[gi], y1s[gi], z0s[gi], lcs[gi]],
            [x0s[gi], y1s[gi], z0s[gi], lcs[gi]],
            [x0s[gi], y0s[gi], z0s[gi], lcs[gi]],
            [x1s[gi], y0s[gi], z0s[gi], lcs[gi]],
            [x1s[gi], y1s[gi], z1s[gi], lcs[gi]],
            [x0s[gi], y1s[gi], z1s[gi], lcs[gi]],
            [x0s[gi], y0s[gi], z1s[gi], lcs[gi]],
            [x1s[gi], y0s[gi], z1s[gi], lcs[gi]],
        ],
        transfinite_data=[txs[i], tys[j], tzs[k]],
        physical_name=volumes_names[volumes_map[gi]],
        inner_volumes=c.get_volumes(),
        surfaces_names=surfaces_names[surfaces_map[gi]],
        rec=recs_map[gi],
        trans=trans_map[gi]
    ))


# Cylinder X
def type_6(primitives, ci, gi, gis, factory,
            x0s, x1s, y0s, y1s, z0s, z1s, lcs, txs, tys, tzs,
            volumes_names, volumes_map, surfaces_names, surfaces_map,
            recs_map, trans_map, xs, ys, zs, transform_data,
            kws, kws_map, **kwargs):
    i, j, k = ci
    cxi, cyj = len(xs) // 2, len(ys) // 2
    cx = sum(xs[:cxi]) + xs[cxi] / 2 + transform_data[0]
    cy = sum(ys[:cyj]) + ys[cyj] / 2 + transform_data[1]
    giy0, giy1 = gis[(i, j - (i - cxi), k)], gis[(i, j + (i - cxi), k)]
    r0, r1 = abs(x0s[gi] - cx), abs(x1s[gi] - cx)
    r1y0, r1y1 = abs(y0s[giy0] - cy), abs(y1s[giy1] - cy)
    r0y0, r0y1 = abs(y1s[giy0] - cy), abs(y0s[giy1] - cy)
    ct0 = kws[kws_map[gi]].get('ct0', 0)
    ct1 = kws[kws_map[gi]].get('ct1', 0)
    ct = kws[kws_map[gi]].get('ct', 3)
    if ct1 and ct0:
        dxr1 = r1 / 2 ** 0.5
        dxr0 = r0 / 2 ** 0.5
        dyr1y1 = r1y1 / 2 ** 0.5
        dyr1y0 = -r1y0 / 2 ** 0.5
        dyr0y1 = r0y1 / 2 ** 0.5
        dyr0y0 = -r0y0 / 2 ** 0.5
    elif ct0:
        dxr1 = r1
        dxr0 = r0 / 2 ** 0.5
        dyr1y1 = r1y1
        dyr1y0 = -r1y0
        dyr0y1 = r0y1 / 2 ** 0.5
        dyr0y0 = -r0y0 / 2 ** 0.5
    elif ct1:
        dxr1 = r1 / 2 ** 0.5
        dxr0 = r0
        dyr1y1 = r1y1 / 2 ** 0.5
        dyr1y0 = -r1y0 / 2 ** 0.5
        dyr0y1 = r0y1
        dyr0y0 = -r0y0
    else:
        dxr1 = r1
        dxr0 = r0
        dyr1y1 = r1y1
        dyr1y0 = -r1y0
        dyr0y1 = r0y1
        dyr0y0 = -r0y0
    pd = [
        [cx + dxr1, cy + dyr1y1, z0s[gi], lcs[gi]],
        [cx + dxr0, cy + dyr0y1, z0s[gi], lcs[gi]],
        [cx + dxr0, cy + dyr0y0, z0s[gi], lcs[gi]],
        [cx + dxr1, cy + dyr1y0, z0s[gi], lcs[gi]],
        [cx + dxr1, cy + dyr1y1, z1s[gi], lcs[gi]],
        [cx + dxr0, cy + dyr0y1, z1s[gi], lcs[gi]],
        [cx + dxr0, cy + dyr0y0, z1s[gi], lcs[gi]],
        [cx + dxr1, cy + dyr1y0, z1s[gi], lcs[gi]]
    ]
    if r1 == r1y1 == r1y0 and r0 == r0y1 == r0y0:
        cts = [0, 0, 0, 0, ct1, ct0, ct0, ct1, 0, 0, 0, 0]
        cd = [
            [], [], [], [],
            [[cx, cy, z0s[gi], lcs[gi]]],
            [[cx, cy, z0s[gi], lcs[gi]]],
            [[cx, cy, z1s[gi], lcs[gi]]],
            [[cx, cy, z1s[gi], lcs[gi]]],
            [], [], [], []
        ]
    elif r1 == r1y1 == r1y0:
        cts = [0, 0, 0, 0, ct1, ct, ct, ct1, 0, 0, 0, 0]
        cd = [
            [], [], [], [],
            [[cx, cy, z0s[gi], lcs[gi]]],
            [[x0s[gi], cy, z0s[gi], lcs[gi]]],
            [[x0s[gi], cy, z1s[gi], lcs[gi]]],
            [[cx, cy, z1s[gi], lcs[gi]]],
            [], [], [], []
        ]
    elif r0 == r0y1 == r0y0:
        cts = [0, 0, 0, 0, ct, ct0, ct0, ct, 0, 0, 0, 0]
        cd = [
            [], [], [], [],
            [[x1s[gi], cy, z0s[gi], lcs[gi]]],
            [[cx, cy, z0s[gi], lcs[gi]]],
            [[cx, cy, z1s[gi], lcs[gi]]],
            [[x1s[gi], cy, z1s[gi], lcs[gi]]],
            [], [], [], []
        ]
    else:
        cts = [0, 0, 0, 0, ct, ct, ct, ct, 0, 0, 0, 0]
        cd = [
            [], [], [], [],
            [[x1s[gi], cy, z0s[gi], lcs[gi]]],
            [[x0s[gi], cy, z0s[gi], lcs[gi]]],
            [[x0s[gi], cy, z1s[gi], lcs[gi]]],
            [[x1s[gi], cy, z1s[gi], lcs[gi]]],
            [], [], [], []
        ]
    primitives.append(Primitive(
        factory=factory,
        point_data=pd,
        curve_types=cts,
        curve_data=cd,
        transfinite_data=[txs[i], tys[j], tzs[k]],
        transfinite_type=0,
        physical_name=volumes_names[volumes_map[gi]],
        surfaces_names=surfaces_names[surfaces_map[gi]],
        rec=recs_map[gi],
        trans=trans_map[gi]
    ))


# Cylinder Y
def type_7(primitives, ci, gi, gis, factory,
            x0s, x1s, y0s, y1s, z0s, z1s, lcs, txs, tys, tzs,
            volumes_names, volumes_map, surfaces_names, surfaces_map,
            recs_map, trans_map, xs, ys, zs, transform_data,
            kws, kws_map, **kwargs):
    i, j, k = ci
    cxi, cyj = len(xs) // 2, len(ys) // 2
    cx = sum(xs[:cxi]) + xs[cxi] / 2 + transform_data[0]
    cy = sum(ys[:cyj]) + ys[cyj] / 2 + transform_data[1]
    gix0, gix1 = gis[(i - (j - cyj), j, k)], gis[(i + (j - cyj), j, k)]
    r0, r1 = abs(y0s[gi] - cy), abs(y1s[gi] - cy)
    r1x0, r1x1 = abs(x0s[gix0] - cx), abs(x1s[gix1] - cx)
    r0x0, r0x1 = abs(x1s[gix0] - cx), abs(x0s[gix1] - cx)
    ct0 = kws[kws_map[gi]].get('ct0', 0)
    ct1 = kws[kws_map[gi]].get('ct1', 0)
    ct = kws[kws_map[gi]].get('ct', 3)
    if ct1 and ct0:
        dyr1 = r1 / 2 ** 0.5
        dyr0 = r0 / 2 ** 0.5
        dxr1x1 = r1x1 / 2 ** 0.5
        dxr1x0 = -r1x0 / 2 ** 0.5
        dxr0x1 = r0x1 / 2 ** 0.5
        dxr0x0 = -r0x0 / 2 ** 0.5
    elif ct0:
        dyr1 = r1
        dyr0 = r0 / 2 ** 0.5
        dxr1x1 = r1x1
        dxr1x0 = -r1x0
        dxr0x1 = r0x1 / 2 ** 0.5
        dxr0x0 = -r0x0 / 2 ** 0.5
    elif ct1:
        dyr1 = r1 / 2 ** 0.5
        dyr0 = r0
        dxr1x1 = r1x1 / 2 ** 0.5
        dxr1x0 = -r1x0 / 2 ** 0.5
        dxr0x1 = r0x1
        dxr0x0 = -r0x0
    else:
        dyr1 = r1
        dyr0 = r0
        dxr1x1 = r1x1
        dxr1x0 = -r1x0
        dxr0x1 = r0x1
        dxr0x0 = -r0x0
    pd = [
        [cx + dxr1x1, cy + dyr1, z0s[gi], lcs[gi]],
        [cx + dxr1x0, cy + dyr1, z0s[gi], lcs[gi]],
        [cx + dxr0x0, cy + dyr0, z0s[gi], lcs[gi]],
        [cx + dxr0x1, cy + dyr0, z0s[gi], lcs[gi]],
        [cx + dxr1x1, cy + dyr1, z1s[gi], lcs[gi]],
        [cx + dxr1x0, cy + dyr1, z1s[gi], lcs[gi]],
        [cx + dxr0x0, cy + dyr0, z1s[gi], lcs[gi]],
        [cx + dxr0x1, cy + dyr0, z1s[gi], lcs[gi]]
    ]
    if r1 == r1x1 == r1x0 and r0 == r0x1 == r0x0:
        cts = [ct1, ct1, ct0, ct0, 0, 0, 0, 0, 0, 0, 0, 0]
        cd = [
            [[cx, cy, z0s[gi], lcs[gi]]],
            [[cx, cy, z1s[gi], lcs[gi]]],
            [[cx, cy, z1s[gi], lcs[gi]]],
            [[cx, cy, z0s[gi], lcs[gi]]],
            [], [], [], [],
            [], [], [], []
        ]
    elif r1 == r1x1 == r1x0:
        cts = [ct1, ct1, ct, ct, 0, 0, 0, 0, 0, 0, 0, 0]
        cd = [
            [[cx, cy, z0s[gi], lcs[gi]]],
            [[cx, cy, z1s[gi], lcs[gi]]],
            [[cx, y0s[gi], z1s[gi], lcs[gi]]],
            [[cx, y0s[gi], z0s[gi], lcs[gi]]],
            [], [], [], []
        ]
    elif r0 == r0x1 == r0x0:
        cts = [ct, ct, ct0, ct0, 0, 0, 0, 0, 0, 0, 0, 0]
        cd = [
            [[cx, y1s[gi], z0s[gi], lcs[gi]]],
            [[cx, y1s[gi], z1s[gi], lcs[gi]]],
            [[cx, cy, z1s[gi], lcs[gi]]],
            [[cx, cy, z0s[gi], lcs[gi]]],
            [], [], [], [],
            [], [], [], []
        ]
    else:
        cts = [ct, ct, ct, ct, 0, 0, 0, 0, 0, 0, 0, 0]
        cd = [
            [[cx, y1s[gi], z0s[gi], lcs[gi]]],
            [[cx, y1s[gi], z1s[gi], lcs[gi]]],
            [[cx, y0s[gi], z1s[gi], lcs[gi]]],
            [[cx, y0s[gi], z0s[gi], lcs[gi]]],
            [], [], [], [],
            [], [], [], []
        ]
    primitives.append(Primitive(
        factory=factory,
        point_data=pd,
        curve_types=cts,
        curve_data=cd,
        transfinite_data=[txs[i], tys[j], tzs[k]],
        transfinite_type=0,
        physical_name=volumes_names[volumes_map[gi]],
        surfaces_names=surfaces_names[surfaces_map[gi]],
        rec=recs_map[gi],
        trans=trans_map[gi]
    ))


# Cylinder NX
def type_8(primitives, ci, gi, gis, factory,
            x0s, x1s, y0s, y1s, z0s, z1s, lcs, txs, tys, tzs,
            volumes_names, volumes_map, surfaces_names, surfaces_map,
            recs_map, trans_map, xs, ys, zs, transform_data,
            kws, kws_map, **kwargs):
    i, j, k = ci
    cxi, cyj = len(xs) // 2, len(ys) // 2
    cx = sum(xs[:cxi]) + xs[cxi] / 2 + transform_data[0]
    cy = sum(ys[:cyj]) + ys[cyj] / 2 + transform_data[1]
    giy0, giy1 = gis[(i, j - (cxi - i), k)], gis[(i, j + (cxi - i), k)]
    r0, r1 = abs(x1s[gi] - cx), abs(x0s[gi] - cx)
    r1y0, r1y1 = abs(y0s[giy0] - cy), abs(y1s[giy1] - cy)
    r0y0, r0y1 = abs(y1s[giy0] - cy), abs(y0s[giy1] - cy)
    ct0 = kws[kws_map[gi]].get('ct0', 0)
    ct1 = kws[kws_map[gi]].get('ct1', 0)
    ct = kws[kws_map[gi]].get('ct', 3)
    if ct1 and ct0:
        dxr1 = -r1 / 2 ** 0.5
        dxr0 = -r0 / 2 ** 0.5
        dyr1y1 = r1y1 / 2 ** 0.5
        dyr1y0 = -r1y0 / 2 ** 0.5
        dyr0y1 = r0y1 / 2 ** 0.5
        dyr0y0 = -r0y0 / 2 ** 0.5
    elif ct0:
        dxr1 = -r1
        dxr0 = -r0 / 2 ** 0.5
        dyr1y1 = r1y1
        dyr1y0 = -r1y0
        dyr0y1 = r0y1 / 2 ** 0.5
        dyr0y0 = -r0y0 / 2 ** 0.5
    elif ct1:
        dxr1 = -r1 / 2 ** 0.5
        dxr0 = -r0
        dyr1y1 = r1y1 / 2 ** 0.5
        dyr1y0 = -r1y0 / 2 ** 0.5
        dyr0y1 = r0y1
        dyr0y0 = -r0y0
    else:
        dxr1 = -r1
        dxr0 = -r0
        dyr1y1 = r1y1
        dyr1y0 = -r1y0
        dyr0y1 = r0y1
        dyr0y0 = -r0y0
    pd = [
        [cx + dxr0, cy + dyr0y1, z0s[gi], lcs[gi]],
        [cx + dxr1, cy + dyr1y1, z0s[gi], lcs[gi]],
        [cx + dxr1, cy + dyr1y0, z0s[gi], lcs[gi]],
        [cx + dxr0, cy + dyr0y0, z0s[gi], lcs[gi]],
        [cx + dxr0, cy + dyr0y1, z1s[gi], lcs[gi]],
        [cx + dxr1, cy + dyr1y1, z1s[gi], lcs[gi]],
        [cx + dxr1, cy + dyr1y0, z1s[gi], lcs[gi]],
        [cx + dxr0, cy + dyr0y0, z1s[gi], lcs[gi]]
    ]
    if r1 == r1y1 == r1y0 and r0 == r0y1 == r0y0:
        cts = [0, 0, 0, 0, ct0, ct1, ct1, ct0, 0, 0, 0, 0]
        cd = [
            [], [], [], [],
            [[cx, cy, z0s[gi], lcs[gi]]],
            [[cx, cy, z0s[gi], lcs[gi]]],
            [[cx, cy, z1s[gi], lcs[gi]]],
            [[cx, cy, z1s[gi], lcs[gi]]],
            [], [], [], []
        ]
    elif r1 == r1y1 == r1y0:
        cts = [0, 0, 0, 0, ct, ct1, ct1, ct, 0, 0, 0, 0]
        cd = [
            [], [], [], [],
            [[x1s[gi], cy, z0s[gi], lcs[gi]]],
            [[cx, cy, z0s[gi], lcs[gi]]],
            [[cx, cy, z1s[gi], lcs[gi]]],
            [[x1s[gi], cy, z1s[gi], lcs[gi]]],
            [], [], [], []
        ]
    elif r0 == r0y1 == r0y0:
        cts = [0, 0, 0, 0, ct0, ct, ct, ct0, 0, 0, 0, 0]
        cd = [
            [], [], [], [],
            [[cx, cy, z0s[gi], lcs[gi]]],
            [[x0s[gi], cy, z0s[gi], lcs[gi]]],
            [[x0s[gi], cy, z1s[gi], lcs[gi]]],
            [[cx, cy, z1s[gi], lcs[gi]]],
            [], [], [], []
        ]
    else:
        cts = [0, 0, 0, 0, ct, ct, ct, ct, 0, 0, 0, 0]
        cd = [
            [], [], [], [],
            [[x1s[gi], cy, z0s[gi], lcs[gi]]],
            [[x0s[gi], cy, z0s[gi], lcs[gi]]],
            [[x0s[gi], cy, z1s[gi], lcs[gi]]],
            [[x1s[gi], cy, z1s[gi], lcs[gi]]],
            [], [], [], []
        ]
    primitives.append(Primitive(
        factory=factory,
        point_data=pd,
        curve_types=cts,
        curve_data=cd,
        transfinite_data=[txs[i], tys[j], tzs[k]],
        transfinite_type=1,
        physical_name=volumes_names[volumes_map[gi]],
        surfaces_names=surfaces_names[surfaces_map[gi]],
        rec=recs_map[gi],
        trans=trans_map[gi]
    ))


# Cylinder NY
def type_9(primitives, ci, gi, gis, factory,
            x0s, x1s, y0s, y1s, z0s, z1s, lcs, txs, tys, tzs,
            volumes_names, volumes_map, surfaces_names, surfaces_map,
            recs_map, trans_map, xs, ys, zs, transform_data,
            kws, kws_map, **kwargs):
    i, j, k = ci
    cxi, cyj = len(xs) // 2, len(ys) // 2
    cx = sum(xs[:cxi]) + xs[cxi] / 2 + transform_data[0]
    cy = sum(ys[:cyj]) + ys[cyj] / 2 + transform_data[1]
    gix0, gix1 = gis[(i - (cyj - j), j, k)], gis[(i + (cyj - j), j, k)]
    r0, r1 = abs(y1s[gi] - cy), abs(y0s[gi] - cy)
    r1x0, r1x1 = abs(x0s[gix0] - cx), abs(x1s[gix1] - cx)
    r0x0, r0x1 = abs(x1s[gix0] - cx), abs(x0s[gix1] - cx)
    ct0 = kws[kws_map[gi]].get('ct0', 0)
    ct1 = kws[kws_map[gi]].get('ct1', 0)
    ct = kws[kws_map[gi]].get('ct', 3)
    if ct1 and ct0:
        dyr1 = -r1 / 2 ** 0.5
        dyr0 = -r0 / 2 ** 0.5
        dxr1x1 = r1x1 / 2 ** 0.5
        dxr1x0 = -r1x0 / 2 ** 0.5
        dxr0x1 = r0x1 / 2 ** 0.5
        dxr0x0 = -r0x0 / 2 ** 0.5
    elif ct0:
        dyr1 = -r1
        dyr0 = -r0 / 2 ** 0.5
        dxr1x1 = r1x1
        dxr1x0 = -r1x0
        dxr0x1 = r0x1 / 2 ** 0.5
        dxr0x0 = -r0x0 / 2 ** 0.5
    elif ct1:
        dyr1 = -r1 / 2 ** 0.5
        dyr0 = -r0
        dxr1x1 = r1x1 / 2 ** 0.5
        dxr1x0 = -r1x0 / 2 ** 0.5
        dxr0x1 = r0x1
        dxr0x0 = -r0x0
    else:
        dyr1 = -r1
        dyr0 = -r0
        dxr1x1 = r1x1
        dxr1x0 = -r1x0
        dxr0x1 = r0x1
        dxr0x0 = -r0x0
    pd = [
        [cx + dxr0x1, cy + dyr0, z0s[gi], lcs[gi]],
        [cx + dxr0x0, cy + dyr0, z0s[gi], lcs[gi]],
        [cx + dxr1x0, cy + dyr1, z0s[gi], lcs[gi]],
        [cx + dxr1x1, cy + dyr1, z0s[gi], lcs[gi]],
        [cx + dxr0x1, cy + dyr0, z1s[gi], lcs[gi]],
        [cx + dxr0x0, cy + dyr0, z1s[gi], lcs[gi]],
        [cx + dxr1x0, cy + dyr1, z1s[gi], lcs[gi]],
        [cx + dxr1x1, cy + dyr1, z1s[gi], lcs[gi]]
    ]
    if r1 == r1x1 == r1x0 and r0 == r0x1 == r0x0:
        cts = [ct0, ct0, ct1, ct1, 0, 0, 0, 0, 0, 0, 0, 0]
        cd = [
            [[cx, cy, z0s[gi], lcs[gi]]],
            [[cx, cy, z1s[gi], lcs[gi]]],
            [[cx, cy, z1s[gi], lcs[gi]]],
            [[cx, cy, z0s[gi], lcs[gi]]],
            [], [], [], [],
            [], [], [], []
        ]
    elif r1 == r1x1 == r1x0:
        cts = [ct, ct, ct1, ct1, 0, 0, 0, 0, 0, 0, 0, 0]
        cd = [
            [[cx, y1s[gi], z0s[gi], lcs[gi]]],
            [[cx, y1s[gi], z1s[gi], lcs[gi]]],
            [[cx, cy, z1s[gi], lcs[gi]]],
            [[cx, cy, z0s[gi], lcs[gi]]],
            [], [], [], []
        ]
    elif r0 == r0x1 == r0x0:
        cts = [ct0, ct0, ct, ct, 0, 0, 0, 0, 0, 0, 0, 0]
        cd = [
            [[cx, cy, z0s[gi], lcs[gi]]],
            [[cx, cy, z1s[gi], lcs[gi]]],
            [[cx, y0s[gi], z1s[gi], lcs[gi]]],
            [[cx, y0s[gi], z0s[gi], lcs[gi]]],
            [], [], [], [],
            [], [], [], []
        ]
    else:
        cts = [ct, ct, ct, ct, 0, 0, 0, 0, 0, 0, 0, 0]
        cd = [
            [[cx, y1s[gi], z0s[gi], lcs[gi]]],
            [[cx, y1s[gi], z1s[gi], lcs[gi]]],
            [[cx, y0s[gi], z1s[gi], lcs[gi]]],
            [[cx, y0s[gi], z0s[gi], lcs[gi]]],
            [], [], [], [],
            [], [], [], []
        ]
    primitives.append(Primitive(
        factory=factory,
        point_data=pd,
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
    6: type_6,  # Cylinder X
    7: type_7,  # Cylinder Y
    8: type_8,  # Cylinder NX
    9: type_9   # Cylinder NY
}
