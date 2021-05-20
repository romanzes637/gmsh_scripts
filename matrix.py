import json
from pprint import pprint
import time
import copy  # for dict copy, items of dict are shallow copies

import gmsh
import numpy as np
import registry

from complex import Complex
from primitive import Primitive
from support import check_file


class Matrix(Complex):
    def __init__(self, factory, xs, ys, zs, coordinates_type='delta',
                 lcs=None, transform_data=None, txs=None, tys=None, tzs=None,
                 types=None, type_map=None,
                 volumes_names=None, volumes_map=None,
                 surfaces_names=None, surfaces_map=None,
                 in_surfaces_names=None, in_surfaces_map=None,
                 in_surfaces_masks=None, in_surfaces_masks_map=None,
                 transforms=None, transforms_map=None,
                 inputs=None, inputs_map=None,
                 kws=None, kws_map=None,
                 recs_map=None, trans_map=None, trans_type_map=None,
                 curve_types=None, curve_types_map=None,
                 curve_data=None, curve_data_map=None,
                 curve_data_coord_sys=None, curve_data_coord_sys_map=None,
                 inputs_transforms=None, inputs_transforms_map=None,
                 inputs_transforms_coord_sys=None,
                 inputs_transforms_coord_sys_map=None,
                 boolean_level_map=None
                 ):
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
        :param list of str types: matrix items types (See functions below)
        :param list of int type_map: matrix items types map
        :param list of str volumes_names: names for items volumes
        :param list of int volumes_map: item - volume name map
        :param list of list of str surfaces_names: names for items surfaces
        :param list of int surfaces_map: item - surface names map
        :param list of list of list of float transforms: transforms for matrix items
        :param list of int transforms_map: item - input file map
        :param list of str inputs: input files
        :param list of int inputs_map: item - input file map
        :param list of dict kws: keyword arguments for matrix items
        :param list of int kws_map: matrix item keyword arguments map
        :param list of int recs_map: see Primitive
        :param list of int trans_map: see Primitive
        :param list of list of int curve_types: see Primitive
        :param list of int curve_types_map: item - curve types map
        :param list of list of list of list of float curve_data : see Primitive
        :param list of int curve_data_map: item - curve data map
        :param list of str curve_data_coord_sys: "local" [0-1] or "global"
        :param list of int curve_data_coord_sys_map:
        :param list of list of float inputs_transforms:
            inputs transform in local coordinate system of the cell
        :param list of int inputs_transforms_map:
        :param list of str inputs_transforms_coord_sys: "local" [0-1] or "global"
        :param list of int curve_data_coord_sys_map:
        :param list of int boolean_level_map : See Primitive
        """
        if factory == 'occ':
            factory_object = gmsh.model.occ
        else:
            factory_object = gmsh.model.geo
        if coordinates_type == 'delta':
            x0, y0, z0 = 0, 0, 0
            pass
        elif coordinates_type == 'direct':  # convert to delta
            x0, y0, z0 = xs[0], ys[0], zs[0]
            xs = [xs[i] - xs[i - 1] for i in range(1, len(xs))]
            ys = [ys[i] - ys[i - 1] for i in range(1, len(ys))]
            zs = [zs[i] - zs[i - 1] for i in range(1, len(zs))]
        else:
            raise ValueError('coordinates_type: {}'.format(coordinates_type))
        nx, ny, nz = len(xs), len(ys), len(zs)
        ni = nx * ny * nz  # number of matrix items
        # print(nx, ny, nz, ni)
        # characteristic length
        if lcs is None:
            lcs = [1 for _ in range(ni)]
        elif not isinstance(lcs, list):
            lcs = [lcs for _ in range(ni)]
        # transform
        if transform_data is None:
            transform_data = []
        if transforms is None:
            transforms = [[]]
        if transforms_map is None:
            transforms_map = [0 for _ in range(ni)]
        # transfinite
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
        if trans_map is None:
            trans_map = [1 for _ in range(ni)]
        if trans_type_map is None:
            trans_type_map = [0 for _ in range(ni)]
        elif not isinstance(trans_type_map, list):
            trans_type_map = [trans_type_map for _ in range(ni)]
        # types
        if types is None:
            types = ['primitive']
        if type_map is None:
            type_map = [0 for _ in range(ni)]
        elif not isinstance(type_map, list):
            type_map = [type_map for _ in range(ni)]
        # volumes
        if volumes_names is None:
            volumes_names = [None]
        if volumes_map is None:
            volumes_map = [0 for _ in range(ni)]
        elif not isinstance(volumes_map, list):
            volumes_map = [volumes_map for _ in range(ni)]
        # surfaces
        if surfaces_names is None:
            surfaces_names = [None]
        elif isinstance(surfaces_names, str):
            surfaces_names = [[surfaces_names for _ in range(6)]]
        if surfaces_map is None:
            surfaces_map = [0 for _ in range(ni)]
        elif not isinstance(surfaces_map, list):
            surfaces_map = [surfaces_map for _ in range(ni)]
        if in_surfaces_names is None:
            in_surfaces_names = [None]
        elif isinstance(in_surfaces_names, str):
            in_surfaces_names = [[in_surfaces_names for _ in range(6)]]
        if in_surfaces_masks is None:
            in_surfaces_masks = [None]
        elif isinstance(in_surfaces_masks, str):
            in_surfaces_masks = [[in_surfaces_masks for _ in range(6)]]
        if in_surfaces_map is None:
            in_surfaces_map = [0 for _ in range(ni)]
        elif isinstance(in_surfaces_map, int):
            in_surfaces_map = [in_surfaces_map for _ in range(ni)]
        if in_surfaces_masks_map is None:
            in_surfaces_masks_map = [0 for _ in range(ni)]
        elif isinstance(in_surfaces_masks_map, int):
            in_surfaces_masks_map = [in_surfaces_masks_map for _ in range(ni)]
        # inputs
        if inputs is None:
            inputs = []
        elif not isinstance(inputs, list):
            inputs = [inputs]
        if inputs_map is None:
            inputs_map = [0 for _ in range(ni)]
        elif not isinstance(inputs_map, list):
            inputs_map = [inputs_map for _ in range(ni)]
        if inputs_transforms is None:
            inputs_transforms = [[[0.5, 0.5, 0.5]]]  # center of the cell
        if inputs_transforms_map is None:
            inputs_transforms_map = [0 for _ in range(ni)]
        elif not isinstance(inputs_transforms_map, list):
            inputs_transforms_map = [inputs_transforms_map for _ in range(ni)]
        if inputs_transforms_coord_sys is None:
            inputs_transforms_coord_sys = ['local']
        if inputs_transforms_coord_sys_map is None:
            inputs_transforms_coord_sys_map = [0 for _ in range(ni)]
        elif not isinstance(curve_data_coord_sys_map, list):
            inputs_transforms_coord_sys_map = [
                inputs_transforms_coord_sys_map for _ in range(ni)]
        # download inputs
        inputs_datas = []
        for i in inputs:
            result = check_file(i)
            with open(result['path']) as f:
                d = json.load(f)
            inputs_datas.append(d)
        # recombine
        if recs_map is None:
            recs_map = [1 for _ in range(ni)]
        elif not isinstance(recs_map, list):
            recs_map = [recs_map for _ in range(ni)]
        # kws
        if kws is None:
            kws = [{}]
        elif not isinstance(kws, list):
            kws = [kws]
        if kws_map is None:
            kws_map = [0 for _ in range(ni)]
        elif not isinstance(kws_map, list):
            kws_map = [kws_map for _ in range(ni)]
        # curve_types
        curve_types = [None] if curve_types is None else curve_types
        if curve_types_map is None:
            curve_types_map = [0 for _ in range(ni)]
        elif not isinstance(curve_types_map, list):
            curve_types_map = [curve_types_map for _ in range(ni)]
        # curve_data
        curve_data = [None] if curve_data is None else curve_data
        if curve_data_map is None:
            curve_data_map = [0 for _ in range(ni)]
        elif not isinstance(curve_data_map, list):
            curve_data_map = [curve_data_map for _ in range(ni)]
        if curve_data_coord_sys is None:
            curve_data_coord_sys = ['local']
        if curve_data_coord_sys_map is None:
            curve_data_coord_sys_map = [0 for _ in range(ni)]
        elif not isinstance(curve_data_coord_sys_map, list):
            curve_data_coord_sys_map = [curve_data_coord_sys_map for _ in range(ni)]
        # boolean
        if boolean_level_map is None:
            boolean_level_map = [0 for _ in range(ni)]
        elif not isinstance(boolean_level_map, list):
            boolean_level_map = [boolean_level_map for _ in range(ni)]
        # Process
        gis = {}  # local index (xi, yj, zk) -> global index (gi) map
        x0s, x1s, xcs = [], [], []  # items starts X, Y, Z
        y0s, y1s, ycs = [], [], []  # items ends X, Y, Z
        z0s, z1s, zcs = [], [], []  # items centers X, Y, Z
        for k in range(nz):
            for j in range(ny):
                for i in range(nx):
                    gis[(i, j, k)] = i + nx * j + ny * nx * k
                    x0s.append(x0 + sum(xs[:i]))
                    x1s.append(x0 + sum(xs[:i + 1]))
                    xcs.append(0.5 * (x0s[-1] + x1s[-1]))
                    y0s.append(y0 + sum(ys[:j]))
                    y1s.append(y0 + sum(ys[:j + 1]))
                    ycs.append(0.5 * (y0s[-1] + y1s[-1]))
                    z0s.append(z0 + sum(zs[:k]))
                    z1s.append(z0 + sum(zs[:k + 1]))
                    zcs.append(0.5 * (z0s[-1] + z1s[-1]))
        primitives = []
        for ci, gi in gis.items():
            t0 = time.time()
            globals()[types[type_map[gi]]](**locals())
            # print(f'type: {types[type_map[gi]]}, time {time.time() - t0}')
        Complex.__init__(self, factory, primitives)


# Empty
def empty(**kwargs):
    pass


# Primitive
def primitive(primitives, ci, gi, factory,
              x0s, x1s, y0s, y1s, z0s, z1s, lcs, txs, tys, tzs,
              volumes_names, volumes_map, surfaces_names, surfaces_map,
              transforms, transforms_map,
              in_surfaces_names, in_surfaces_map,
              in_surfaces_masks, in_surfaces_masks_map,
              recs_map, trans_map, trans_type_map, transform_data,
              curve_types, curve_types_map,
              curve_data, curve_data_map,
              curve_data_coord_sys, curve_data_coord_sys_map,
              boolean_level_map,
              **kwargs):
    xi, yi, zi = ci  # local coordinates by axes
    cd = copy.deepcopy(curve_data[curve_data_map[gi]])
    cd_cs = curve_data_coord_sys[curve_data_coord_sys_map[gi]]
    if cd is not None and cd_cs == 'local':
        for i, points in enumerate(cd):
            for j, p in enumerate(points):  # [xj, yj, zj, lcj]
                cd[i][j][0] = x0s[gi] + cd[i][j][0]*(x1s[gi] - x0s[gi])
                cd[i][j][1] = y0s[gi] + cd[i][j][1]*(y1s[gi] - y0s[gi])
                cd[i][j][2] = z0s[gi] + cd[i][j][2]*(z1s[gi] - z0s[gi])
    # TODO bug with cylinder curve_types [1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0]
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
        transform_data=transform_data + transforms[transforms_map[gi]],
        curve_types=curve_types[curve_types_map[gi]],
        curve_data=cd,
        transfinite_data=[txs[xi], tys[yi], tzs[zi]],
        volume_name=volumes_names[volumes_map[gi]],
        surfaces_names=surfaces_names[surfaces_map[gi]],
        in_surfaces_names=in_surfaces_names[in_surfaces_map[gi]],
        in_surfaces_mask=in_surfaces_masks[in_surfaces_masks_map[gi]],
        rec=recs_map[gi],
        trans=trans_map[gi],
        transfinite_type=trans_type_map[gi],
        boolean_level=boolean_level_map[gi]
    ))


# Complex
def complex(primitives, gi, factory, transform_data,
            x0s, x1s, y0s, y1s, z0s, z1s,
            inputs_datas, inputs_map,
            inputs_transforms, inputs_transforms_map,
            inputs_transforms_coord_sys, inputs_transforms_coord_sys_map,
            **kwargs):
    in_ts = copy.deepcopy(inputs_transforms[inputs_transforms_map[gi]])
    ts_cs = inputs_transforms_coord_sys[inputs_transforms_coord_sys_map[gi]]
    for i, t in enumerate(in_ts):
        if ts_cs == 'local':
            if len(t) == 3:  # Displacement
                in_ts[i][0] = x0s[gi] + t[0] * (x1s[gi] - x0s[gi])  # dx
                in_ts[i][1] = y0s[gi] + t[1] * (y1s[gi] - y0s[gi])  # dy
                in_ts[i][2] = z0s[gi] + t[2] * (z1s[gi] - z0s[gi])  # dz
            elif len(t) == 7:  # Rotation with origin and direction
                in_ts[i][0] = x0s[gi] + t[0] * (x1s[gi] - x0s[gi])  # origin x
                in_ts[i][1] = y0s[gi] + t[1] * (y1s[gi] - y0s[gi])  # origin y
                in_ts[i][2] = z0s[gi] + t[2] * (z1s[gi] - z0s[gi])  # origin z
            else:  # Rotation with direction only
                pass
    input_data = copy.deepcopy(inputs_datas[inputs_map[gi]])
    if input_data['arguments'].get('transform_data', None) is None:
        input_data['arguments']['transform_data'] = []
    input_data['arguments']['transform_data'].extend(in_ts)
    input_data['arguments']['transform_data'].extend(transform_data)
    input_data['arguments']['factory'] = factory
    from complex_factory import ComplexFactory
    c = ComplexFactory.new(input_data)
    primitives.extend(c.primitives)


# Complex in Primitive
def complex_in_primitive(primitives, ci, gi, factory, transform_data,
                         x0s, x1s, y0s, y1s, z0s, z1s, lcs, txs,
                         tys, tzs,
                         volumes_names, volumes_map, surfaces_names,
                         surfaces_map,
                         in_surfaces_names, in_surfaces_map,
                         in_surfaces_masks, in_surfaces_masks_map,
                         recs_map, trans_map, inputs_datas, inputs_map,
                         curve_types, curve_types_map,
                         curve_data, curve_data_map,
                         curve_data_coord_sys, curve_data_coord_sys_map,
                         inputs_transforms, inputs_transforms_map,
                         inputs_transforms_coord_sys,
                         inputs_transforms_coord_sys_map,
                         boolean_level_map,
                         **kwargs):
    xi, yi, zi = ci  # local coordinates by axes
    cd = copy.deepcopy(curve_data[curve_data_map[gi]])
    cd_cs = curve_data_coord_sys[curve_data_coord_sys_map[gi]]
    if cd is not None and cd_cs == 'local':
        for i, points in enumerate(cd):
            for j, p in enumerate(points):  # [xj, yj, zj, lcj]
                cd[i][j][0] = x0s[gi] + cd[i][j][0] * (x1s[gi] - x0s[gi])
                cd[i][j][1] = y0s[gi] + cd[i][j][1] * (y1s[gi] - y0s[gi])
                cd[i][j][2] = z0s[gi] + cd[i][j][2] * (z1s[gi] - z0s[gi])
    in_ts = copy.deepcopy(inputs_transforms[inputs_transforms_map[gi]])
    ts_cs = inputs_transforms_coord_sys[inputs_transforms_coord_sys_map[gi]]
    for i, t in enumerate(in_ts):
        if ts_cs == 'local':
            if len(t) == 3:  # Displacement
                in_ts[i][0] = x0s[gi] + t[0] * (x1s[gi] - x0s[gi])  # dx
                in_ts[i][1] = y0s[gi] + t[1] * (y1s[gi] - y0s[gi])  # dy
                in_ts[i][2] = z0s[gi] + t[2] * (z1s[gi] - z0s[gi])  # dz
            elif len(t) == 7:  # Rotation with origin and direction
                in_ts[i][0] = x0s[gi] + t[0] * (x1s[gi] - x0s[gi])  # origin x
                in_ts[i][1] = y0s[gi] + t[1] * (y1s[gi] - y0s[gi])  # origin y
                in_ts[i][2] = z0s[gi] + t[2] * (z1s[gi] - z0s[gi])  # origin z
            else:  # Rotation with direction only
                pass
    input_data = copy.deepcopy(inputs_datas[inputs_map[gi]])
    if input_data['arguments'].get('transform_data', None) is None:
        input_data['arguments']['transform_data'] = []
    input_data['arguments']['transform_data'].extend(in_ts)
    input_data['arguments']['transform_data'].extend(transform_data)
    input_data['arguments']['factory'] = factory
    print(input_data['arguments']['transform_data'])
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
        transform_data=transform_data,
        transfinite_data=[txs[xi], tys[yi], tzs[zi]],
        curve_types=curve_types[curve_types_map[gi]],
        curve_data=cd,
        volume_name=volumes_names[volumes_map[gi]],
        inner_volumes=c.get_volumes(),
        surfaces_names=surfaces_names[surfaces_map[gi]],
        in_surfaces_names=in_surfaces_names[in_surfaces_map[gi]],
        in_surfaces_mask=in_surfaces_masks[in_surfaces_masks_map[gi]],
        rec=recs_map[gi],
        trans=trans_map[gi],
        boolean_level=boolean_level_map[gi]
    ))


# Complex and Primitive (for OCC boolean)
def complex_and_primitive(primitives, ci, gi, factory, transform_data,
                          x0s, x1s, y0s, y1s, z0s, z1s, lcs, txs,
                          tys, tzs,
                          volumes_names, volumes_map, surfaces_names,
                          surfaces_map,
                          in_surfaces_names, in_surfaces_map,
                          in_surfaces_masks, in_surfaces_masks_map,
                          recs_map, trans_map, inputs_datas, inputs_map,
                          curve_types, curve_types_map,
                          curve_data, curve_data_map,
                          curve_data_coord_sys, curve_data_coord_sys_map,
                          inputs_transforms, inputs_transforms_map,
                          boolean_level_map,
                          **kwargs):
    xi, yi, zi = ci  # local coordinates by axes
    cd = copy.deepcopy(curve_data[curve_data_map[gi]])
    cd_cs = curve_data_coord_sys[curve_data_coord_sys_map[gi]]
    if cd is not None and cd_cs == 'local':
        for i, points in enumerate(cd):
            for j, p in enumerate(points):  # [xj, yj, zj, lcj]
                cd[i][j][0] = x0s[gi] + cd[i][j][0] * (x1s[gi] - x0s[gi])
                cd[i][j][1] = y0s[gi] + cd[i][j][1] * (y1s[gi] - y0s[gi])
                cd[i][j][2] = z0s[gi] + cd[i][j][2] * (z1s[gi] - z0s[gi])
    local_tr = inputs_transforms[inputs_transforms_map[gi]]
    global_tr = [x0s[gi] + local_tr[0] * (x1s[gi] - x0s[gi]),
                 y0s[gi] + local_tr[1] * (y1s[gi] - y0s[gi]),
                 z0s[gi] + local_tr[2] * (z1s[gi] - z0s[gi])]
    input_data = copy.deepcopy(inputs_datas[inputs_map[gi]])
    print(input_data['arguments'])
    if input_data['arguments'].get('transform_data', None) is None:
        input_data['arguments']['transform_data'] = []
    input_data['arguments']['transform_data'].append(global_tr)
    input_data['arguments']['transform_data'].extend(transform_data)
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
        transform_data=transform_data,
        transfinite_data=[txs[xi], tys[yi], tzs[zi]],
        curve_types=curve_types[curve_types_map[gi]],
        curve_data=cd,
        volume_name=volumes_names[volumes_map[gi]],
        surfaces_names=surfaces_names[surfaces_map[gi]],
        in_surfaces_names=in_surfaces_names[in_surfaces_map[gi]],
        in_surfaces_mask=in_surfaces_masks[in_surfaces_masks_map[gi]],
        rec=recs_map[gi],
        trans=trans_map[gi],
        boolean_level=boolean_level_map[gi]
    ))


def axisymmetric_core(primitives, ci, gi, gis, factory,
                      x0s, x1s, y0s, y1s, z0s, z1s, lcs, txs, tys, tzs,
                      volumes_names, volumes_map, surfaces_names, surfaces_map,
                      recs_map, trans_map, xs, ys, zs, transform_data,
                      in_surfaces_names, in_surfaces_map,
                      in_surfaces_masks, in_surfaces_masks_map,
                      kws, kws_map, **kwargs):
    # print(x0s)
    # print(x1s)
    i, j, k = ci
    cxi, cyj = len(xs) // 2, len(ys) // 2
    cx = sum(xs[:cxi]) + xs[cxi] / 2
    cy = sum(ys[:cyj]) + ys[cyj] / 2
    rx, rnx, ry, rny = x1s[gi] - cx, cx - x0s[gi], y1s[gi] - cy, cy - y0s[gi]
    ct0 = kws[kws_map[gi]].get('ct0', 0)
    # ct1 = kws[kws_map[gi]].get('ct1', 0)
    ct = kws[kws_map[gi]].get('ct', 3)
    # print(ct0)
    if not ct0:  # straight
        pd = [[x1s[gi], y1s[gi], z0s[gi], lcs[gi]],
              [x0s[gi], y1s[gi], z0s[gi], lcs[gi]],
              [x0s[gi], y0s[gi], z0s[gi], lcs[gi]],
              [x1s[gi], y0s[gi], z0s[gi], lcs[gi]],
              [x1s[gi], y1s[gi], z1s[gi], lcs[gi]],
              [x0s[gi], y1s[gi], z1s[gi], lcs[gi]],
              [x0s[gi], y0s[gi], z1s[gi], lcs[gi]],
              [x1s[gi], y0s[gi], z1s[gi], lcs[gi]]]
        cts = None
        cd = None
        # print(pd)
    else:  # curved
        dxrx = rx / 2 ** 0.5
        dyry = ry / 2 ** 0.5
        dxrnx = -rnx / 2 ** 0.5
        dyrny = -rny / 2 ** 0.5
        pd = [
            [cx + dxrx, cy + dyry, z0s[gi], lcs[gi]],
            [cx + dxrnx, cy + dyry, z0s[gi], lcs[gi]],
            [cx + dxrnx, cy + dyrny, z0s[gi], lcs[gi]],
            [cx + dxrx, cy + dyrny, z0s[gi], lcs[gi]],
            [cx + dxrx, cy + dyry, z1s[gi], lcs[gi]],
            [cx + dxrnx, cy + dyry, z1s[gi], lcs[gi]],
            [cx + dxrnx, cy + dyrny, z1s[gi], lcs[gi]],
            [cx + dxrx, cy + dyrny, z1s[gi], lcs[gi]],
        ]
        if np.allclose(rx, [ry, rnx, rny], atol=registry.point_tol, rtol=0):
            cts = [ct0, ct0, ct0, ct0, ct0, ct0, ct0, ct0, 0, 0, 0, 0]
            cd = [
                [[cx, cy, z0s[gi], lcs[gi]]],
                [[cx, cy, z1s[gi], lcs[gi]]],
                [[cx, cy, z1s[gi], lcs[gi]]],
                [[cx, cy, z0s[gi], lcs[gi]]],
                [[cx, cy, z0s[gi], lcs[gi]]],
                [[cx, cy, z0s[gi], lcs[gi]]],
                [[cx, cy, z1s[gi], lcs[gi]]],
                [[cx, cy, z1s[gi], lcs[gi]]],
                [], [], [], []
            ]
        else:
            cts = [ct, ct, ct, ct, ct, ct, ct, ct, 0, 0, 0, 0]
            cd = [
                [[cx, cy + ry, z0s[gi], lcs[gi]]],
                [[cx, cy + ry, z1s[gi], lcs[gi]]],
                [[cx, cy - rny, z1s[gi], lcs[gi]]],
                [[cx, cy - rny, z0s[gi], lcs[gi]]],
                [[cx + rx, cy, z0s[gi], lcs[gi]]],
                [[cx - rnx, cy, z0s[gi], lcs[gi]]],
                [[cx - rnx, cy, z1s[gi], lcs[gi]]],
                [[cx + rx, cy, z1s[gi], lcs[gi]]],
                [], [], [], []
            ]
    primitives.append(Primitive(
        factory=factory,
        point_data=pd,
        transform_data=transform_data,
        curve_types=cts,
        curve_data=cd,
        transfinite_data=[txs[i], tys[j], tzs[k]],
        transfinite_type=2,
        volume_name=volumes_names[volumes_map[gi]],
        surfaces_names=surfaces_names[surfaces_map[gi]],
        in_surfaces_names=in_surfaces_names[in_surfaces_map[gi]],
        in_surfaces_mask=in_surfaces_masks[in_surfaces_masks_map[gi]],
        rec=recs_map[gi],
        trans=trans_map[gi]
    ))


def axisymmetric_x(primitives, ci, gi, gis, factory,
                   x0s, x1s, y0s, y1s, z0s, z1s, lcs, txs, tys, tzs,
                   volumes_names, volumes_map, surfaces_names, surfaces_map,
                   in_surfaces_names, in_surfaces_map,
                   in_surfaces_masks, in_surfaces_masks_map,
                   recs_map, trans_map, xs, ys, zs, transform_data,
                   kws, kws_map, **kwargs):
    i, j, k = ci
    cxi, cyj = len(xs) // 2, len(ys) // 2  # center indices
    cx = sum(xs[:cxi]) + xs[cxi] / 2  # center x
    cy = sum(ys[:cyj]) + ys[cyj] / 2  # center y
    giy0, giy1 = gis[(i, j - (i - cxi), k)], gis[(i, j + (i - cxi), k)]
    r0, r1 = abs(x0s[gi] - cx), abs(x1s[gi] - cx)  # inner and outer radii
    r1y0, r1y1 = abs(y0s[giy0] - cy), abs(y1s[giy1] - cy)
    r0y0, r0y1 = abs(y1s[giy0] - cy), abs(y0s[giy1] - cy)
    ct0 = kws[kws_map[gi]].get('ct0', 0)
    ct1 = kws[kws_map[gi]].get('ct1', 0)
    ct = kws[kws_map[gi]].get('ct', 3)
    dr1_z0 = kws[kws_map[gi]].get('dr1_z0', 0)
    dxr1_z0 = dr1_z0 / 2 ** 0.5
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
        [cx + dxr1 + dxr1_z0, cy + dyr1y1 + dxr1_z0, z0s[gi], lcs[gi]],
        [cx + dxr0, cy + dyr0y1, z0s[gi], lcs[gi]],
        [cx + dxr0, cy + dyr0y0, z0s[gi], lcs[gi]],
        [cx + dxr1 + dxr1_z0, cy + dyr1y0 - dxr1_z0, z0s[gi], lcs[gi]],
        [cx + dxr1, cy + dyr1y1, z1s[gi], lcs[gi]],
        [cx + dxr0, cy + dyr0y1, z1s[gi], lcs[gi]],
        [cx + dxr0, cy + dyr0y0, z1s[gi], lcs[gi]],
        [cx + dxr1, cy + dyr1y0, z1s[gi], lcs[gi]]
    ]
    r0_equal = np.allclose(r0, [r0y1, r0y0], atol=registry.point_tol, rtol=0)
    r1_equal = np.allclose(r1, [r1y1, r1y0], atol=registry.point_tol, rtol=0)
    if r0_equal and r1_equal:
        cts = [0, 0, 0, 0, ct1, ct0, ct0, ct1,
               1 if dxr1_z0 != 0 else 0, 0, 0, 1 if dxr1_z0 != 0 else 0]
        cd = [
            [], [], [], [],
            [[cx, cy, z0s[gi], lcs[gi]]],
            [[cx, cy, z0s[gi], lcs[gi]]],
            [[cx, cy, z1s[gi], lcs[gi]]],
            [[cx, cy, z1s[gi], lcs[gi]]],
            [[cx + dxr1 + dxr1_z0, cy + dyr1y1 + dxr1_z0, z1s[gi], lcs[gi]]],
            [],
            [],
            [[cx + dxr1 + dxr1_z0, cy + dyr1y0 - dxr1_z0, z1s[gi], lcs[gi]]]
        ]
    elif r1_equal:
        cts = [0, 0, 0, 0, ct1, ct * ct0, ct * ct0, ct1, 0, 0, 0, 0]
        cd = [
            [], [], [], [],
            [[cx, cy, z0s[gi], lcs[gi]]],
            [[x0s[gi], cy, z0s[gi], lcs[gi]]],
            [[x0s[gi], cy, z1s[gi], lcs[gi]]],
            [[cx, cy, z1s[gi], lcs[gi]]],
            [], [], [], []
        ]
    elif r0_equal:
        cts = [0, 0, 0, 0, ct * ct1, ct0, ct0, ct * ct1, 0, 0, 0, 0]
        cd = [
            [], [], [], [],
            [[x1s[gi], cy, z0s[gi], lcs[gi]]],
            [[cx, cy, z0s[gi], lcs[gi]]],
            [[cx, cy, z1s[gi], lcs[gi]]],
            [[x1s[gi], cy, z1s[gi], lcs[gi]]],
            [], [], [], []
        ]
    else:
        cts = [0, 0, 0, 0, ct * ct1, ct * ct0, ct * ct0, ct * ct1, 0, 0, 0, 0]
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
        transform_data=transform_data,
        curve_types=cts,
        curve_data=cd,
        transfinite_data=[txs[i], tys[j], tzs[k]],
        transfinite_type=3,
        volume_name=volumes_names[volumes_map[gi]],
        surfaces_names=surfaces_names[surfaces_map[gi]],
        in_surfaces_names=in_surfaces_names[in_surfaces_map[gi]],
        in_surfaces_mask=in_surfaces_masks[in_surfaces_masks_map[gi]],
        rec=recs_map[gi],
        trans=trans_map[gi]
    ))


def axisymmetric_y(primitives, ci, gi, gis, factory,
           x0s, x1s, y0s, y1s, z0s, z1s, lcs, txs, tys, tzs,
           volumes_names, volumes_map, surfaces_names, surfaces_map,
           in_surfaces_names, in_surfaces_map,
           in_surfaces_masks, in_surfaces_masks_map,
           recs_map, trans_map, xs, ys, zs, transform_data,
           kws, kws_map, **kwargs):
    i, j, k = ci
    cxi, cyj = len(xs) // 2, len(ys) // 2
    cx = sum(xs[:cxi]) + xs[cxi] / 2
    cy = sum(ys[:cyj]) + ys[cyj] / 2
    gix0, gix1 = gis[(i - (j - cyj), j, k)], gis[(i + (j - cyj), j, k)]
    r0, r1 = abs(y0s[gi] - cy), abs(y1s[gi] - cy)
    r1x0, r1x1 = abs(x0s[gix0] - cx), abs(x1s[gix1] - cx)
    r0x0, r0x1 = abs(x1s[gix0] - cx), abs(x0s[gix1] - cx)
    ct0 = kws[kws_map[gi]].get('ct0', 0)
    ct1 = kws[kws_map[gi]].get('ct1', 0)
    ct = kws[kws_map[gi]].get('ct', 3)
    dr1_z0 = kws[kws_map[gi]].get('dr1_z0', 0)
    dyr1_z0 = dr1_z0 / 2 ** 0.5
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
        [cx + dxr1x1 + dyr1_z0, cy + dyr1 + dyr1_z0, z0s[gi], lcs[gi]],
        [cx + dxr1x0 - dyr1_z0, cy + dyr1 + dyr1_z0, z0s[gi], lcs[gi]],
        [cx + dxr0x0, cy + dyr0, z0s[gi], lcs[gi]],
        [cx + dxr0x1, cy + dyr0, z0s[gi], lcs[gi]],
        [cx + dxr1x1, cy + dyr1, z1s[gi], lcs[gi]],
        [cx + dxr1x0, cy + dyr1, z1s[gi], lcs[gi]],
        [cx + dxr0x0, cy + dyr0, z1s[gi], lcs[gi]],
        [cx + dxr0x1, cy + dyr0, z1s[gi], lcs[gi]]
    ]
    r0_equal = np.allclose(r0, [r0x1, r0x0], atol=registry.point_tol, rtol=0)
    r1_equal = np.allclose(r1, [r1x1, r1x0], atol=registry.point_tol, rtol=0)
    if r1_equal and r0_equal:
        cts = [ct1, ct1, ct0, ct0, 0, 0, 0, 0,
               1 if dyr1_z0 != 0 else 0, 1 if dyr1_z0 != 0 else 0, 0, 0]
        cd = [
            [[cx, cy, z0s[gi], lcs[gi]]],
            [[cx, cy, z1s[gi], lcs[gi]]],
            [[cx, cy, z1s[gi], lcs[gi]]],
            [[cx, cy, z0s[gi], lcs[gi]]],
            [], [], [], [],
            [[cx + dxr1x1 + dyr1_z0, cy + dyr1 + dyr1_z0, z1s[gi], lcs[gi]]],
            [[cx + dxr1x0 - dyr1_z0, cy + dyr1 + dyr1_z0, z1s[gi], lcs[gi]]],
            [], []
        ]
    elif r1_equal:
        cts = [ct1, ct1, ct * ct0, ct * ct0, 0, 0, 0, 0, 0, 0, 0, 0]
        cd = [
            [[cx, cy, z0s[gi], lcs[gi]]],
            [[cx, cy, z1s[gi], lcs[gi]]],
            [[cx, y0s[gi], z1s[gi], lcs[gi]]],
            [[cx, y0s[gi], z0s[gi], lcs[gi]]],
            [], [], [], []
        ]
    elif r0_equal:
        cts = [ct * ct1, ct * ct1, ct0, ct0, 0, 0, 0, 0, 0, 0, 0, 0]
        cd = [
            [[cx, y1s[gi], z0s[gi], lcs[gi]]],
            [[cx, y1s[gi], z1s[gi], lcs[gi]]],
            [[cx, cy, z1s[gi], lcs[gi]]],
            [[cx, cy, z0s[gi], lcs[gi]]],
            [], [], [], [],
            [], [], [], []
        ]
    else:
        cts = [ct * ct1, ct * ct1, ct * ct0, ct * ct0, 0, 0, 0, 0, 0, 0, 0, 0]
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
        transform_data=transform_data,
        curve_types=cts,
        curve_data=cd,
        transfinite_data=[txs[i], tys[j], tzs[k]],
        transfinite_type=1,
        volume_name=volumes_names[volumes_map[gi]],
        surfaces_names=surfaces_names[surfaces_map[gi]],
        in_surfaces_names=in_surfaces_names[in_surfaces_map[gi]],
        in_surfaces_mask=in_surfaces_masks[in_surfaces_masks_map[gi]],
        rec=recs_map[gi],
        trans=trans_map[gi]
    ))


def axisymmetric_nx(primitives, ci, gi, gis, factory,
                   x0s, x1s, y0s, y1s, z0s, z1s, lcs, txs, tys, tzs,
                   volumes_names, volumes_map, surfaces_names, surfaces_map,
                   in_surfaces_names, in_surfaces_map,
                   in_surfaces_masks, in_surfaces_masks_map,
                   recs_map, trans_map, xs, ys, zs, transform_data,
                   kws, kws_map, **kwargs):
    i, j, k = ci
    cxi, cyj = len(xs) // 2, len(ys) // 2
    cx = sum(xs[:cxi]) + xs[cxi] / 2
    cy = sum(ys[:cyj]) + ys[cyj] / 2
    giy0, giy1 = gis[(i, j - (cxi - i), k)], gis[(i, j + (cxi - i), k)]
    r0, r1 = abs(x1s[gi] - cx), abs(x0s[gi] - cx)
    r1y0, r1y1 = abs(y0s[giy0] - cy), abs(y1s[giy1] - cy)
    r0y0, r0y1 = abs(y1s[giy0] - cy), abs(y0s[giy1] - cy)
    ct0 = kws[kws_map[gi]].get('ct0', 0)
    ct1 = kws[kws_map[gi]].get('ct1', 0)
    ct = kws[kws_map[gi]].get('ct', 3)
    dr1_z0 = kws[kws_map[gi]].get('dr1_z0', 0)
    dxr1_z0 = dr1_z0 / 2 ** 0.5
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
        [cx + dxr1 - dxr1_z0, cy + dyr1y1 + dxr1_z0, z0s[gi], lcs[gi]],
        [cx + dxr1 - dxr1_z0, cy + dyr1y0 - dxr1_z0, z0s[gi], lcs[gi]],
        [cx + dxr0, cy + dyr0y0, z0s[gi], lcs[gi]],
        [cx + dxr0, cy + dyr0y1, z1s[gi], lcs[gi]],
        [cx + dxr1, cy + dyr1y1, z1s[gi], lcs[gi]],
        [cx + dxr1, cy + dyr1y0, z1s[gi], lcs[gi]],
        [cx + dxr0, cy + dyr0y0, z1s[gi], lcs[gi]]
    ]
    r0_equal = np.allclose(r0, [r0y1, r0y0], atol=registry.point_tol, rtol=0)
    r1_equal = np.allclose(r1, [r1y1, r1y0], atol=registry.point_tol, rtol=0)
    if r1_equal and r0_equal:
        cts = [0, 0, 0, 0, ct0, ct1, ct1, ct0,
               0, 1 if dxr1_z0 != 0 else 0, 1 if dxr1_z0 != 0 else 0, 0]
        cd = [
            [], [], [], [],
            [[cx, cy, z0s[gi], lcs[gi]]],
            [[cx, cy, z0s[gi], lcs[gi]]],
            [[cx, cy, z1s[gi], lcs[gi]]],
            [[cx, cy, z1s[gi], lcs[gi]]],
            [],
            [[cx + dxr1 - dxr1_z0, cy + dyr1y1 + dxr1_z0, z1s[gi], lcs[gi]]],
            [[cx + dxr1 - dxr1_z0, cy + dyr1y0 - dxr1_z0, z1s[gi], lcs[gi]]],
            []
        ]
    elif r1_equal:
        cts = [0, 0, 0, 0, ct * ct0, ct1, ct1, ct * ct0, 0, 0, 0, 0]
        cd = [
            [], [], [], [],
            [[x1s[gi], cy, z0s[gi], lcs[gi]]],
            [[cx, cy, z0s[gi], lcs[gi]]],
            [[cx, cy, z1s[gi], lcs[gi]]],
            [[x1s[gi], cy, z1s[gi], lcs[gi]]],
            [], [], [], []
        ]
    elif r0_equal:
        cts = [0, 0, 0, 0, ct0, ct * ct1, ct * ct1, ct0, 0, 0, 0, 0]
        cd = [
            [], [], [], [],
            [[cx, cy, z0s[gi], lcs[gi]]],
            [[x0s[gi], cy, z0s[gi], lcs[gi]]],
            [[x0s[gi], cy, z1s[gi], lcs[gi]]],
            [[cx, cy, z1s[gi], lcs[gi]]],
            [], [], [], []
        ]
    else:
        cts = [0, 0, 0, 0, ct * ct0, ct * ct1, ct * ct1, ct * ct0, 0, 0, 0, 0]
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
        transform_data=transform_data,
        curve_types=cts,
        curve_data=cd,
        transfinite_data=[txs[i], tys[j], tzs[k]],
        transfinite_type=2,
        volume_name=volumes_names[volumes_map[gi]],
        surfaces_names=surfaces_names[surfaces_map[gi]],
        in_surfaces_names=in_surfaces_names[in_surfaces_map[gi]],
        in_surfaces_mask=in_surfaces_masks[in_surfaces_masks_map[gi]],
        rec=recs_map[gi],
        trans=trans_map[gi]
    ))


def axisymmetric_ny(primitives, ci, gi, gis, factory,
                    x0s, x1s, y0s, y1s, z0s, z1s, lcs, txs, tys, tzs,
                    volumes_names, volumes_map, surfaces_names, surfaces_map,
                    in_surfaces_names, in_surfaces_map,
                    in_surfaces_masks, in_surfaces_masks_map,
                    recs_map, trans_map, xs, ys, zs, transform_data,
                    kws, kws_map, **kwargs):
    i, j, k = ci
    cxi, cyj = len(xs) // 2, len(ys) // 2
    cx = sum(xs[:cxi]) + xs[cxi] / 2
    cy = sum(ys[:cyj]) + ys[cyj] / 2
    gix0, gix1 = gis[(i - (cyj - j), j, k)], gis[(i + (cyj - j), j, k)]
    r0, r1 = abs(y1s[gi] - cy), abs(y0s[gi] - cy)
    r1x0, r1x1 = abs(x0s[gix0] - cx), abs(x1s[gix1] - cx)
    r0x0, r0x1 = abs(x1s[gix0] - cx), abs(x0s[gix1] - cx)
    ct0 = kws[kws_map[gi]].get('ct0', 0)
    ct1 = kws[kws_map[gi]].get('ct1', 0)
    ct = kws[kws_map[gi]].get('ct', 3)
    dr1_z0 = kws[kws_map[gi]].get('dr1_z0', 0)
    dyr1_z0 = dr1_z0 / 2 ** 0.5
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
        [cx + dxr1x0 - dyr1_z0, cy + dyr1 - dyr1_z0, z0s[gi], lcs[gi]],
        [cx + dxr1x1 + dyr1_z0, cy + dyr1 - dyr1_z0, z0s[gi], lcs[gi]],
        [cx + dxr0x1, cy + dyr0, z1s[gi], lcs[gi]],
        [cx + dxr0x0, cy + dyr0, z1s[gi], lcs[gi]],
        [cx + dxr1x0, cy + dyr1, z1s[gi], lcs[gi]],
        [cx + dxr1x1, cy + dyr1, z1s[gi], lcs[gi]]
    ]
    r0_equal = np.allclose(r0, [r0x1, r0x0], atol=registry.point_tol, rtol=0)
    r1_equal = np.allclose(r1, [r1x1, r1x0], atol=registry.point_tol, rtol=0)
    if r1_equal and r0_equal:
        cts = [ct0, ct0, ct1, ct1, 0, 0, 0, 0,
               0, 0, 1 if dyr1_z0 != 0 else 0, 1 if dyr1_z0 != 0 else 0]
        cd = [
            [[cx, cy, z0s[gi], lcs[gi]]],
            [[cx, cy, z1s[gi], lcs[gi]]],
            [[cx, cy, z1s[gi], lcs[gi]]],
            [[cx, cy, z0s[gi], lcs[gi]]],
            [], [], [], [],
            [], [],
            [[cx + dxr1x0 - dyr1_z0, cy + dyr1 - dyr1_z0, z1s[gi], lcs[gi]]],
            [[cx + dxr1x1 + dyr1_z0, cy + dyr1 - dyr1_z0, z1s[gi], lcs[gi]]]
        ]
    elif r1_equal:
        cts = [ct * ct0, ct * ct0, ct1, ct1, 0, 0, 0, 0, 0, 0, 0, 0]
        cd = [
            [[cx, y1s[gi], z0s[gi], lcs[gi]]],
            [[cx, y1s[gi], z1s[gi], lcs[gi]]],
            [[cx, cy, z1s[gi], lcs[gi]]],
            [[cx, cy, z0s[gi], lcs[gi]]],
            [], [], [], []
        ]
    elif r0_equal:
        cts = [ct0, ct0, ct * ct1, ct * ct1, 0, 0, 0, 0, 0, 0, 0, 0]
        cd = [
            [[cx, cy, z0s[gi], lcs[gi]]],
            [[cx, cy, z1s[gi], lcs[gi]]],
            [[cx, y0s[gi], z1s[gi], lcs[gi]]],
            [[cx, y0s[gi], z0s[gi], lcs[gi]]],
            [], [], [], [],
            [], [], [], []
        ]
    else:
        cts = [ct * ct0, ct * ct0, ct * ct1, ct * ct1, 0, 0, 0, 0, 0, 0, 0, 0]
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
        transform_data=transform_data,
        curve_types=cts,
        curve_data=cd,
        transfinite_data=[txs[i], tys[j], tzs[k]],
        transfinite_type=2,
        volume_name=volumes_names[volumes_map[gi]],
        surfaces_names=surfaces_names[surfaces_map[gi]],
        in_surfaces_names=in_surfaces_names[in_surfaces_map[gi]],
        in_surfaces_mask=in_surfaces_masks[in_surfaces_masks_map[gi]],
        rec=recs_map[gi],
        trans=trans_map[gi]
    ))


def curved_nz(primitives, ci, gi, gis, factory,
              x0s, x1s, y0s, y1s, z0s, z1s, lcs, txs, tys, tzs,
              volumes_names, volumes_map, surfaces_names, surfaces_map,
              transforms, transforms_map,
              in_surfaces_names, in_surfaces_map,
              in_surfaces_masks, in_surfaces_masks_map, xs, ys, zs,
              recs_map, trans_map, trans_type_map, transform_data, kws, kws_map,
              **kwargs):
    i, j, k = ci
    cxi, cyj = len(xs) // 2, len(ys) // 2
    cx = sum(xs[:cxi]) + xs[cxi] / 2
    cy = sum(ys[:cyj]) + ys[cyj] / 2
    # gix0, gix1 = gis[(i - (cyj - j), j, k)], gis[(i + (cyj - j), j, k)]
    r = kws[kws_map[gi]].get('r', 1)
    ct = kws[kws_map[gi]].get('ct', 3)
    cts = [0, 0, 0, 0, ct, ct, 0, 0, 0, 0, 0, 0]
    cd = [
        [], [], [], [],
        [[x1s[gi], cy, z0s[gi] + r, lcs[gi]]],
        [[x0s[gi], cy, z0s[gi] + r, lcs[gi]]],
        [],
        [],
        [], [], [], []
    ]
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
        curve_types=cts,
        curve_data=cd,
        transform_data=transform_data + transforms[transforms_map[gi]],
        transfinite_data=[txs[i], tys[j], tzs[k]],
        volume_name=volumes_names[volumes_map[gi]],
        surfaces_names=surfaces_names[surfaces_map[gi]],
        in_surfaces_names=in_surfaces_names[in_surfaces_map[gi]],
        in_surfaces_mask=in_surfaces_masks[in_surfaces_masks_map[gi]],
        rec=recs_map[gi],
        trans=trans_map[gi],
        transfinite_type=trans_type_map[gi],
    ))


def curved_z(primitives, ci, gi, gis, factory,
             x0s, x1s, y0s, y1s, z0s, z1s, lcs, txs, tys, tzs,
             volumes_names, volumes_map, surfaces_names, surfaces_map,
             transforms, transforms_map,
             in_surfaces_names, in_surfaces_map,
             in_surfaces_masks, in_surfaces_masks_map, xs, ys, zs,
             recs_map, trans_map, trans_type_map, transform_data, kws, kws_map,
             **kwargs):
    i, j, k = ci
    cxi, cyj = len(xs) // 2, len(ys) // 2
    cx = sum(xs[:cxi]) + xs[cxi] / 2
    cy = sum(ys[:cyj]) + ys[cyj] / 2
    # gix0, gix1 = gis[(i - (cyj - j), j, k)], gis[(i + (cyj - j), j, k)]
    r = kws[kws_map[gi]].get('r', 1)
    ct = kws[kws_map[gi]].get('ct', 3)
    cts = [0, 0, 0, 0, 0, 0, ct, ct, 0, 0, 0, 0]
    cd = [
        [], [], [], [],
        [],
        [],
        [[x0s[gi], cy, z1s[gi] + r, lcs[gi]]],
        [[x1s[gi], cy, z1s[gi] + r, lcs[gi]]],
        [], [], [], []
    ]
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
        curve_types=cts,
        curve_data=cd,
        transform_data=transform_data + transforms[transforms_map[gi]],
        transfinite_data=[txs[i], tys[j], tzs[k]],
        volume_name=volumes_names[volumes_map[gi]],
        surfaces_names=surfaces_names[surfaces_map[gi]],
        in_surfaces_names=in_surfaces_names[in_surfaces_map[gi]],
        in_surfaces_mask=in_surfaces_masks[in_surfaces_masks_map[gi]],
        rec=recs_map[gi],
        trans=trans_map[gi],
        transfinite_type=trans_type_map[gi],
    ))


def curved_nz_right(primitives, ci, gi, gis, factory,
              x0s, x1s, y0s, y1s, z0s, z1s, lcs, txs, tys, tzs,
              volumes_names, volumes_map, surfaces_names, surfaces_map,
              transforms, transforms_map,
              in_surfaces_names, in_surfaces_map,
              in_surfaces_masks, in_surfaces_masks_map, xs, ys, zs,
              recs_map, trans_map, trans_type_map, transform_data, kws, kws_map,
              **kwargs):
    i, j, k = ci
    cxi, cyj = len(xs) // 2, len(ys) // 2
    cx = sum(xs[:cxi]) + xs[cxi] / 2
    cy = sum(ys[:cyj]) + ys[cyj] / 2
    # gix0, gix1 = gis[(i - (cyj - j), j, k)], gis[(i + (cyj - j), j, k)]
    r = kws[kws_map[gi]].get('r', 1)
    a = kws[kws_map[gi]].get('a', r/2**0.5)
    b = kws[kws_map[gi]].get('b', 1)
    ct = kws[kws_map[gi]].get('ct', 3)
    cts = [0, 0, 0, 0, ct, ct, 0, 0, 0, 0, 0, 0]
    cd = [
        [], [], [], [],
        [[x1s[gi], y1s[gi], z0s[gi] - a, lcs[gi]]],
        [[x0s[gi], y1s[gi], z0s[gi] - a, lcs[gi]]],
        [],
        [],
        [], [], [], []
    ]
    primitives.append(Primitive(
        factory=factory,
        point_data=[
            [x1s[gi], y1s[gi], z0s[gi] + r - a, lcs[gi]],
            [x0s[gi], y1s[gi], z0s[gi] + r - a, lcs[gi]],
            [x0s[gi], y0s[gi] , z0s[gi], lcs[gi]],
            [x1s[gi], y0s[gi], z0s[gi], lcs[gi]],
            [x1s[gi], y1s[gi], z1s[gi], lcs[gi]],
            [x0s[gi], y1s[gi], z1s[gi], lcs[gi]],
            [x0s[gi], y1s[gi] - b, z1s[gi], lcs[gi]],
            [x1s[gi], y1s[gi] - b, z1s[gi], lcs[gi]],
        ],
        curve_types=cts,
        curve_data=cd,
        transform_data=transform_data + transforms[transforms_map[gi]],
        transfinite_data=[txs[i], tys[j], tzs[k]],
        volume_name=volumes_names[volumes_map[gi]],
        surfaces_names=surfaces_names[surfaces_map[gi]],
        in_surfaces_names=in_surfaces_names[in_surfaces_map[gi]],
        in_surfaces_mask=in_surfaces_masks[in_surfaces_masks_map[gi]],
        rec=recs_map[gi],
        trans=trans_map[gi],
        transfinite_type=trans_type_map[gi],
    ))


def curved_y_left(primitives, ci, gi, gis, factory,
              x0s, x1s, y0s, y1s, z0s, z1s, lcs, txs, tys, tzs,
              volumes_names, volumes_map, surfaces_names, surfaces_map,
              transforms, transforms_map,
              in_surfaces_names, in_surfaces_map,
              in_surfaces_masks, in_surfaces_masks_map, xs, ys, zs,
              recs_map, trans_map, trans_type_map, transform_data, kws, kws_map,
              **kwargs):
    i, j, k = ci
    cxi, cyj = len(xs) // 2, len(ys) // 2
    cx = sum(xs[:cxi]) + xs[cxi] / 2
    cy = sum(ys[:cyj]) + ys[cyj] / 2
    # gix0, gix1 = gis[(i - (cyj - j), j, k)], gis[(i + (cyj - j), j, k)]
    r = kws[kws_map[gi]].get('r', 1)
    a = kws[kws_map[gi]].get('a', r/2**0.5)
    b = kws[kws_map[gi]].get('b', 1)
    ct = kws[kws_map[gi]].get('ct', 3)
    cts = [0, 0, 0, 0, 0, 0, 0, 0, ct, ct, 0, 0]
    cd = [
        [], [], [], [],
        [], [], [], [],
        [[x1s[gi], y1s[gi] + a, z0s[gi], lcs[gi]]],
        [[x0s[gi], y1s[gi] + a, z0s[gi], lcs[gi]]],
        [],
        [],
    ]
    primitives.append(Primitive(
        factory=factory,
        point_data=[
            [x1s[gi], y1s[gi] - (r - a), z0s[gi], lcs[gi]],
            [x0s[gi], y1s[gi] - (r - a), z0s[gi], lcs[gi]],
            [x0s[gi], y0s[gi], z0s[gi], lcs[gi]],
            [x1s[gi], y0s[gi], z0s[gi], lcs[gi]],
            [x1s[gi], y1s[gi], z1s[gi], lcs[gi]],
            [x0s[gi], y1s[gi], z1s[gi], lcs[gi]],
            [x0s[gi], y0s[gi], z0s[gi] + b, lcs[gi]],
            [x1s[gi], y0s[gi], z0s[gi] + b, lcs[gi]],
        ],
        curve_types=cts,
        curve_data=cd,
        transform_data=transform_data + transforms[transforms_map[gi]],
        transfinite_data=[txs[i], tys[j], tzs[k]],
        volume_name=volumes_names[volumes_map[gi]],
        surfaces_names=surfaces_names[surfaces_map[gi]],
        in_surfaces_names=in_surfaces_names[in_surfaces_map[gi]],
        in_surfaces_mask=in_surfaces_masks[in_surfaces_masks_map[gi]],
        rec=recs_map[gi],
        trans=trans_map[gi]
    ))


def curved_nz_left(primitives, ci, gi, gis, factory,
              x0s, x1s, y0s, y1s, z0s, z1s, lcs, txs, tys, tzs,
              volumes_names, volumes_map, surfaces_names, surfaces_map,
              transforms, transforms_map,
              in_surfaces_names, in_surfaces_map,
              in_surfaces_masks, in_surfaces_masks_map, xs, ys, zs,
              recs_map, trans_map, trans_type_map, transform_data, kws, kws_map,
              **kwargs):
    i, j, k = ci
    cxi, cyj = len(xs) // 2, len(ys) // 2
    cx = sum(xs[:cxi]) + xs[cxi] / 2
    cy = sum(ys[:cyj]) + ys[cyj] / 2
    # gix0, gix1 = gis[(i - (cyj - j), j, k)], gis[(i + (cyj - j), j, k)]
    r = kws[kws_map[gi]].get('r', 1)
    a = kws[kws_map[gi]].get('a', r/2**0.5)
    b = kws[kws_map[gi]].get('b', 1)
    ct = kws[kws_map[gi]].get('ct', 3)
    cts = [0, 0, 0, 0, ct, ct, 0, 0, 0, 0, 0, 0]
    cd = [
        [], [], [], [],
        [[x1s[gi], y0s[gi], z0s[gi] - a, lcs[gi]]],
        [[x0s[gi], y0s[gi], z0s[gi] - a, lcs[gi]]],
        [],
        [],
        [], [], [], []
    ]
    primitives.append(Primitive(
        factory=factory,
        point_data=[
            [x1s[gi], y1s[gi], z0s[gi], lcs[gi]],
            [x0s[gi], y1s[gi], z0s[gi], lcs[gi]],
            [x0s[gi], y0s[gi], z0s[gi] + r - a, lcs[gi]],
            [x1s[gi], y0s[gi], z0s[gi] + r - a, lcs[gi]],
            [x1s[gi], y0s[gi] + b, z1s[gi], lcs[gi]],
            [x0s[gi], y0s[gi] + b, z1s[gi], lcs[gi]],
            [x0s[gi], y0s[gi], z1s[gi], lcs[gi]],
            [x1s[gi], y0s[gi], z1s[gi], lcs[gi]],
        ],
        curve_types=cts,
        curve_data=cd,
        transform_data=transform_data + transforms[transforms_map[gi]],
        transfinite_data=[txs[i], tys[j], tzs[k]],
        volume_name=volumes_names[volumes_map[gi]],
        surfaces_names=surfaces_names[surfaces_map[gi]],
        in_surfaces_names=in_surfaces_names[in_surfaces_map[gi]],
        in_surfaces_mask=in_surfaces_masks[in_surfaces_masks_map[gi]],
        rec=recs_map[gi],
        trans=trans_map[gi],
        transfinite_type=trans_type_map[gi],
    ))


def curved_ny_right(primitives, ci, gi, gis, factory,
              x0s, x1s, y0s, y1s, z0s, z1s, lcs, txs, tys, tzs,
              volumes_names, volumes_map, surfaces_names, surfaces_map,
              transforms, transforms_map,
              in_surfaces_names, in_surfaces_map,
              in_surfaces_masks, in_surfaces_masks_map, xs, ys, zs,
              recs_map, trans_map, trans_type_map, transform_data, kws, kws_map,
              **kwargs):
    i, j, k = ci
    cxi, cyj = len(xs) // 2, len(ys) // 2
    cx = sum(xs[:cxi]) + xs[cxi] / 2
    cy = sum(ys[:cyj]) + ys[cyj] / 2
    # gix0, gix1 = gis[(i - (cyj - j), j, k)], gis[(i + (cyj - j), j, k)]
    r = kws[kws_map[gi]].get('r', 1)
    a = kws[kws_map[gi]].get('a', r/2**0.5)
    b = kws[kws_map[gi]].get('b', 1)
    ct = kws[kws_map[gi]].get('ct', 3)
    cts = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, ct, ct]
    cd = [
        [], [], [], [],
        [], [], [], [],
        [],
        [],
        [[x0s[gi], y0s[gi] - a, z0s[gi], lcs[gi]]],
        [[x1s[gi], y0s[gi] - a, z0s[gi], lcs[gi]]]
    ]
    primitives.append(Primitive(
        factory=factory,
        point_data=[
            [x1s[gi], y1s[gi], z0s[gi], lcs[gi]],
            [x0s[gi], y1s[gi], z0s[gi], lcs[gi]],
            [x0s[gi], y0s[gi] + (r - a), z0s[gi], lcs[gi]],
            [x1s[gi], y0s[gi] + (r - a), z0s[gi] , lcs[gi]],
            [x1s[gi], y1s[gi], z0s[gi] + b, lcs[gi]],
            [x0s[gi], y1s[gi], z0s[gi] + b, lcs[gi]],
            [x0s[gi], y0s[gi], z1s[gi], lcs[gi]],
            [x1s[gi], y0s[gi], z1s[gi], lcs[gi]],
        ],
        curve_types=cts,
        curve_data=cd,
        transform_data=transform_data + transforms[transforms_map[gi]],
        transfinite_data=[txs[i], tys[j], tzs[k]],
        volume_name=volumes_names[volumes_map[gi]],
        surfaces_names=surfaces_names[surfaces_map[gi]],
        in_surfaces_names=in_surfaces_names[in_surfaces_map[gi]],
        in_surfaces_mask=in_surfaces_masks[in_surfaces_masks_map[gi]],
        rec=recs_map[gi],
        trans=trans_map[gi],
        transfinite_type=trans_type_map[gi],
    ))


# Complex at external
def external(primitives, gi, factory,
             x0s, x1s, y0s, y1s, z0s, z1s, xcs, ycs, zcs,
             inputs_datas, inputs_map, transform_data,
             kws, kws_map, **kwargs):
    input_data = copy.deepcopy(inputs_datas[inputs_map[gi]])
    if input_data['arguments'].get('transform_data', None) is None:
        input_data['arguments']['transform_data'] = []
    pos = kws[kws_map[gi]].get('pos', ('xc', 'yc', 'zc'))
    external_pos_map = {
        "xc": xcs, "yc": ycs, "zc": zcs,
        "x0": x0s, "y0": y0s, "z0": z0s,
        "x1": x1s, "y1": y1s, "z1": z1s,
    }
    input_data['arguments']['transform_data'].append(
        [external_pos_map[pos[0]][gi],
         external_pos_map[pos[1]][gi],
         external_pos_map[pos[2]][gi]])
    input_data['arguments']['transform_data'].extend(transform_data)
    input_data['arguments']['factory'] = factory
    from complex_factory import ComplexFactory
    c = ComplexFactory.new(input_data)
    primitives.extend(c.primitives)