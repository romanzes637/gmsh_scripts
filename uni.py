import json
import time
import copy  # for dict copy, items of dict are shallow copies
from functools import reduce
from itertools import product

import gmsh
import numpy as np

import registry
from complex import Complex
from primitive import Primitive
from support import check_file, transform, coordinates_to_coordinates, \
    transform_to_transform, parse_indexing


class Uni(Complex):
    def __init__(self, factory=None,
                 coordinate_system=None,
                 transform_data=None,
                 coordinates=None,
                 points=None,
                 grid_coordinates_type=None,
                 grid=None,
                 coordinate_systems=None,
                 coordinate_systems_transform_data=None,
                 css_map=None,
                 types=None, types_map=None,  # types
                 lcs=None, lcs_map=None,  # characteristic lengths
                 ts=None,  # transfinite
                 txs=None,
                 tys=None,
                 tzs=None,
                 trans_map=None,
                 trans_type_map=None,
                 recs_map=None
                 ):
        """
        Universal complex Point and Matrix
        :param str factory: see Primitive
        :param str coordinate_system: cartesian, cylindrical or spherical
        :param list of int css_map: coordinate systems map
        """
        print(locals())
        # Factory
        factory = 'geo' if factory is None else factory
        if factory == 'occ':
            factory_object = gmsh.model.occ
        elif factory == 'geo':
            factory_object = gmsh.model.geo
        else:
            raise ValueError(factory)
        # Indexing
        new_grid, new_grid_maps = [], []
        for x in grid:
            new_cs, n2o = parse_indexing(x, grid_coordinates_type)
            new_grid.append(new_cs)
            new_grid_maps.append(n2o)
        grid = new_grid
        print(new_grid)
        # TODO change the maps to new grid shape
        # if any((len(nxs) != len(xs), len(nys) != len(ys), len(nzs) != len(zs))):
        #     # Old
        #     if coordinates_type == 'delta':
        #         nx, ny, nz = len(xs), len(ys), len(zs)
        #     elif coordinates_type == 'direct':
        #         nx, ny, nz = len(xs) - 1, len(ys) - 1, len(zs) - 1
        #     else:
        #         raise ValueError(f'coordinates_type: {coordinates_type}')
        #     l2g = {}  # local index (xi, yj, zk) -> global index (gi) map
        #     g2l = {}  # global index (gi) map -> local index (xi, yj, zk)
        #     for zi in range(nz):
        #         for yi in range(ny):
        #             for xi in range(nx):
        #                 gi = xi + nx * yi + ny * nx * zi
        #                 l2g[(xi, yi, zi)] = gi
        #                 g2l[gi] = (xi, yi, zi)
        #     # New
        #     xs, ys, zs = nxs, nys, nzs
        #     if coordinates_type == 'delta':
        #         x0, y0, z0 = 0, 0, 0
        #     elif coordinates_type == 'direct':  # convert to delta
        #         x0, y0, z0 = xs[0], ys[0], zs[0]
        #         xs = [xs[i] - xs[i - 1] for i in range(1, len(xs))]
        #         ys = [ys[i] - ys[i - 1] for i in range(1, len(ys))]
        #         zs = [zs[i] - zs[i - 1] for i in range(1, len(zs))]
        #     else:
        #         raise ValueError(f'coordinates_type: {coordinates_type}')
        #     nx, ny, nz = len(xs), len(ys), len(zs)
        #     ni = nx * ny * nz  # number of matrix items
        #     n2o_gs = {}  # new global index (gi) to old global index (gi)
        #     for zi in range(len(zs)):
        #         for yi in range(len(ys)):
        #             for xi in range(len(xs)):
        #                 gi = xi + nx * yi + ny * nx * zi
        #                 n2o_gs[gi] = l2g[(n2o_xs[xi], n2o_ys[yi], n2o_zs[zi])]
        #     # Update maps
        #     if isinstance(txs, list):
        #         txs = [txs[n2o_xs[xi]] for xi in range(nx)]
        #     if isinstance(tys, list):
        #         tys = [tys[n2o_ys[yi]] for yi in range(ny)]
        #     if isinstance(tzs, list):
        #         tzs = [tzs[n2o_zs[zi]] for zi in range(nz)]
        #     if isinstance(lcs_map, list):
        #         lcs_map = [lcs_map[n2o_gs[gi]] for gi in range(ni)]
        #     if isinstance(transforms_map, list):
        #         transforms_map = [transforms_map[n2o_gs[gi]] for gi in range(ni)]
        #     if isinstance(type_map, list):
        #         type_map = [type_map[n2o_gs[gi]] for gi in range(ni)]
        #     if isinstance(transforms_map, list):
        #         transforms_map = [transforms_map[n2o_gs[gi]] for gi in range(ni)]
        #     if isinstance(volumes_map, list):
        #         volumes_map = [volumes_map[n2o_gs[gi]] for gi in range(ni)]
        #     if isinstance(surfaces_map, list):
        #         surfaces_map = [surfaces_map[n2o_gs[gi]] for gi in range(ni)]
        #     if isinstance(in_surfaces_map, list):
        #         in_surfaces_map = [in_surfaces_map[n2o_gs[gi]] for gi in range(ni)]
        #     if isinstance(inputs_map, list):
        #         inputs_map = [inputs_map[n2o_gs[gi]] for gi in range(ni)]
        #     if isinstance(kws_map, list):
        #         kws_map = [kws_map[n2o_gs[gi]] for gi in range(ni)]
        #     if isinstance(recs_map, list):
        #         recs_map = [recs_map[n2o_gs[gi]] for gi in range(ni)]
        #     if isinstance(trans_map, list):
        #         trans_map = [trans_map[n2o_gs[gi]] for gi in range(ni)]
        #     if isinstance(curve_types_map, list):
        #         curve_types_map = [curve_types_map[n2o_gs[gi]] for gi in range(ni)]
        #     if isinstance(curve_data_map, list):
        #         curve_data_map = [curve_data_map[n2o_gs[gi]] for gi in range(ni)]
        #     if isinstance(curve_data_coord_sys_map, list):
        #         curve_data_coord_sys_map = [curve_data_coord_sys_map[n2o_gs[gi]] for gi in range(ni)]
        #     if isinstance(inputs_transforms_coord_sys_map, list):
        #         inputs_transforms_coord_sys_map = [inputs_transforms_coord_sys_map[n2o_gs[gi]] for gi in range(ni)]
        #     if isinstance(boolean_level_map, list):
        #         boolean_level_map = [boolean_level_map[n2o_gs[gi]] for gi in range(ni)]
        # Coordinates map for points and grid
        if coordinates is not None:
            if points is not None:
                points = [[coordinates[y] for y in x] for x in points]
            if grid is not None:
                grid = [coordinates[y] for x in grid for y in x]
        if points is not None:
            ni = nx = ny = nz = len(points)  # number of matrix items
            l2g = {}  # local index (x1, x2, ..., xi) -> global index (gi) map
            g2l = {}  # global index (gi) map -> local index (x1, x2, ..., xi)
            for i in range(ni):
                gi = i
                l2g[(i, i, i)] = gi
                g2l[gi] = (i, i, i)
        if grid is not None:
            if grid_coordinates_type is None:
                grid_coordinates_type = 'delta'
            if grid_coordinates_type == 'delta':
                origin = [0 for x in grid]
            elif grid_coordinates_type == 'direct':  # convert to delta
                origin = [x[0] for x in grid]
                grid = [[x[i] - x[i - 1] for i in range(1, len(x))] for x in grid]
            else:
                raise ValueError(grid_coordinates_type)
            nx, ny, nz = [len(x) for x in grid][:3]
            print(nx, ny, nz)
            ni = reduce(lambda x, y: x * y, [len(x) for x in grid])  # number of matrix items
            l2g = {}  # local index (xi, ..., zi, yi, xi) -> global index (gi) map
            g2l = {}  # global index (gi) map -> local index (xi, ..., zi, yi, xi)
            indexes = [range(len(x)) for x in grid]
            for gi, li in enumerate(product(*reversed(indexes))):
                l2g[li] = gi
                g2l[gi] = li
        points = np.array(points) if points is not None else points
        grid = [np.array(x) for x in grid]
        # Coordinate system with transform
        if coordinate_system is None:
            coordinate_system = 'cartesian'
        elif coordinate_system not in ['cartesian', 'cylindrical', 'spherical']:
            raise ValueError(coordinate_system)
        if transform_data is None:
            transform_data = []
        # Global curvilinear to global cartesian
        for i, t in enumerate(transform_data):
            transform_data[i] = transform_to_transform(
                t, coordinate_system, 'cartesian')
        # Coordinate systems for point and grid
        if coordinate_systems is None:
            coordinate_systems = ['cartesian']
        if coordinate_systems_transform_data is None:  # In coordinate_system
            coordinate_systems_transform_data = [[] for _ in coordinate_systems]
        # Global curvilinear to global cartesian
        for i, td in enumerate(coordinate_systems_transform_data):
            for j, t in enumerate(td):
                coordinate_systems_transform_data[i][j] = transform_to_transform(
                    t, coordinate_system, 'cartesian')
        if css_map is None:
            css_map = [0 for _ in range(ni)]
        elif not isinstance(css_map, list):
            css_map = [css_map for _ in range(ni)]
        # point_datas = np.zeros((ni, 8, 3))
        point_datas = []
        # Points datas
        if points is not None:
            for gi in range(ni):
                zi, yi, xi = g2l[gi][-3:]
                x, y, z = points[gi]  # center
                dxs, dys, dzs = grid[0], grid[1], grid[2]
                dx, dy, dz = dxs[xi], dys[yi], dzs[zi]  # deltas
                ds = grid[3:]
                dsi = reversed(g2l[gi][:-3])
                ds = [x[i] for (i, x) in zip(dsi, ds)]
                point_datas.append([
                    [x + 0.5 * dx, y + 0.5 * dy, z - 0.5 * dz] + ds,
                    [x - 0.5 * dx, y + 0.5 * dy, z - 0.5 * dz] + ds,
                    [x - 0.5 * dx, y - 0.5 * dy, z - 0.5 * dz] + ds,
                    [x + 0.5 * dx, y - 0.5 * dy, z - 0.5 * dz] + ds,
                    [x + 0.5 * dx, y + 0.5 * dy, z + 0.5 * dz] + ds,
                    [x - 0.5 * dx, y + 0.5 * dy, z + 0.5 * dz] + ds,
                    [x - 0.5 * dx, y - 0.5 * dy, z + 0.5 * dz] + ds,
                    [x + 0.5 * dx, y - 0.5 * dy, z + 0.5 * dz] + ds])
        else:
            for gi in range(ni):
                zi, yi, xi = g2l[gi][-3:]
                x0, y0, z0 = origin[:3]
                dxs, dys, dzs = grid[0], grid[1], grid[2]
                ds = grid[3:]
                dsi = reversed(g2l[gi][:-3])
                ds = [x[i] for (i, x) in zip(dsi, ds)]
                x0i, x1i = x0 + sum(dxs[:xi]), x0 + sum(dxs[:xi + 1])
                y0i, y1i = y0 + sum(dys[:yi]), y0 + sum(dys[:yi + 1])
                z0i, z1i = z0 + sum(dzs[:zi]), z0 + sum(dzs[:zi + 1])
                point_datas.append([
                    [x1i, y1i, z0i] + ds,
                    [x0i, y1i, z0i] + ds,
                    [x0i, y0i, z0i] + ds,
                    [x1i, y0i, z0i] + ds,
                    [x1i, y1i, z1i] + ds,
                    [x0i, y1i, z1i] + ds,
                    [x0i, y0i, z1i] + ds,
                    [x1i, y0i, z1i] + ds])
        # Local curvilinear to global cartesian
        for gi in range(ni):
            cs = coordinate_systems[css_map[gi]]
            td = coordinate_systems_transform_data[css_map[gi]]
            # Local curvilinear to local cartesian
            point_datas[gi] = coordinates_to_coordinates(
                point_datas[gi], cs, 'cartesian')
            if points is not None:
                points[gi] = coordinates_to_coordinates(
                    [points[gi]], cs, 'cartesian')[0]
            # Local cartesian to global cartesian transform
            for t in td:
                point_datas[gi] = transform(point_datas[gi], t)
                if points is not None:
                    points[gi] = transform([points[gi]], t)[0]
        # Types
        if types is None:
            types = ['primitive']
        if types_map is None:
            types_map = [0 for _ in range(ni)]
        # Characteristic length (default 1)
        if lcs is None:
            lcs = [1 for _ in range(ni)]
        elif not isinstance(lcs, list):
            lcs = [lcs for _ in range(ni)]
        if lcs_map is None:
            lcs_map = [0 for _ in range(ni)]
        elif not isinstance(lcs_map, list):
            lcs_map = [lcs_map for _ in range(ni)]
        # Transfinite (default [3, 0, 1]) and Recombine
        if ts is None:
            ts = [[3, 0, 1]]
        if txs is None:
            txs = [0 for _ in range(nx)]
        elif not isinstance(txs, list):
            txs = [txs for _ in range(nx)]
        if tys is None:
            tys = [0 for _ in range(ny)]
        elif not isinstance(tys, list):
            tys = [tys for _ in range(ny)]
        if tzs is None:
            tzs = [0 for _ in range(nz)]
        elif not isinstance(tzs, list):
            tzs = [tzs for _ in range(nz)]
        if trans_map is None:
            trans_map = [1 for _ in range(ni)]
        if trans_type_map is None:
            trans_type_map = [0 for _ in range(ni)]
        elif not isinstance(trans_type_map, list):
            trans_type_map = [trans_type_map for _ in range(ni)]
        if recs_map is None:
            recs_map = [1 for _ in range(ni)]
        elif not isinstance(recs_map, list):
            recs_map = [recs_map for _ in range(ni)]
        # Process
        primitives = []
        for li, gi in l2g.items():
            globals()[types[types_map[gi]]](**locals())
        Complex.__init__(self, factory, primitives)


# Empty
def empty(**kwargs):
    pass


# Primitive
def primitive(primitives, li, gi, factory, transform_data,
              point_datas, lcs, lcs_map, ts, txs, tys, tzs,
              trans_map, trans_type_map, recs_map,
              **kwargs):
    pd = point_datas[gi]
    lc = np.array([[lcs[lcs_map[gi]]] for _ in range(8)])
    pd = np.concatenate((pd, lc), axis=1)
    zi, yi, xi = li[-3:]
    primitives.append(Primitive(
        factory=factory,
        transform_data=transform_data,
        transfinite_data=[ts[txs[xi]], ts[tys[yi]], ts[tzs[zi]]],
        point_data=pd,
        rec=recs_map[gi],
        trans=trans_map[gi],
        transfinite_type=trans_type_map[gi],
    ))


# def primitive(primitives, li, gi, factory,
#               x0s, x1s, y0s, y1s, z0s, z1s, ts, txs, tys, tzs, lcs, lcs_map,
#               volumes_names, volumes_map, surfaces_names, surfaces_map,
#               transforms, transforms_map,
#               in_surfaces_names, in_surfaces_map,
#               in_surfaces_masks, in_surfaces_masks_map,
#               recs_map, trans_map, trans_type_map, transform_data,
#               curve_types, curve_types_map,
#               curve_data, curve_data_map,
#               curve_data_coord_sys, curve_data_coord_sys_map,
#               boolean_level_map,
#               **kwargs):
#     # Primitive curves data
#     cd = copy.deepcopy(curve_data[curve_data_map[gi]])
#     cd_cs = curve_data_coord_sys[curve_data_coord_sys_map[gi]]
#     if cd is not None and cd_cs == 'local':  # local to global coordinates
#         for i, points in enumerate(cd):
#             for j, p in enumerate(points):  # [xj, yj, zj, lcj]
#                 cd[i][j][0] = x0s[gi] + cd[i][j][0]*(x1s[gi] - x0s[gi])
#                 cd[i][j][1] = y0s[gi] + cd[i][j][1]*(y1s[gi] - y0s[gi])
#                 cd[i][j][2] = z0s[gi] + cd[i][j][2]*(z1s[gi] - z0s[gi])
#     # Create Primitive
#     # TODO bug with cylinder curve_types [1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0]
#     xi, yi, zi = li  # local coordinates by axes
#     primitives.append(Primitive(
#         factory=factory,
#         point_data=[
#             [x1s[gi], y1s[gi], z0s[gi], lcs[lcs_map[gi]]],
#             [x0s[gi], y1s[gi], z0s[gi], lcs[lcs_map[gi]]],
#             [x0s[gi], y0s[gi], z0s[gi], lcs[lcs_map[gi]]],
#             [x1s[gi], y0s[gi], z0s[gi], lcs[lcs_map[gi]]],
#             [x1s[gi], y1s[gi], z1s[gi], lcs[lcs_map[gi]]],
#             [x0s[gi], y1s[gi], z1s[gi], lcs[lcs_map[gi]]],
#             [x0s[gi], y0s[gi], z1s[gi], lcs[lcs_map[gi]]],
#             [x1s[gi], y0s[gi], z1s[gi], lcs[lcs_map[gi]]],
#         ],
#         transform_data=transform_data + transforms[transforms_map[gi]],
#         curve_types=curve_types[curve_types_map[gi]],
#         curve_data=cd,
#         transfinite_data=[ts[txs[xi]], ts[tys[yi]], ts[tzs[zi]]],
#         volume_name=volumes_names[volumes_map[gi]],
#         surfaces_names=surfaces_names[surfaces_map[gi]],
#         in_surfaces_names=in_surfaces_names[in_surfaces_map[gi]],
#         in_surfaces_mask=in_surfaces_masks[in_surfaces_masks_map[gi]],
#         rec=recs_map[gi],
#         trans=trans_map[gi],
#         transfinite_type=trans_type_map[gi],
#         boolean_level=boolean_level_map[gi]
#     ))


# Complex
def complex(primitives, gi, factory, transform_data,
            x0s, x1s, y0s, y1s, z0s, z1s,
            inputs_datas, inputs_map,
            inputs_transforms, inputs_transforms_map,
            inputs_transforms_coord_sys, inputs_transforms_coord_sys_map,
            **kwargs):
    # Complex transforms
    in_ts = copy.deepcopy(inputs_transforms[inputs_transforms_map[gi]])
    ts_cs = inputs_transforms_coord_sys[inputs_transforms_coord_sys_map[gi]]
    for i, t in enumerate(in_ts):
        if ts_cs == 'local':  # local to global coordinates
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
    # Complex input data
    input_data = copy.deepcopy(inputs_datas[inputs_map[gi]])
    if input_data['arguments'].get('transform_data', None) is None:
        input_data['arguments']['transform_data'] = []
    input_data['arguments']['transform_data'].extend(in_ts)
    input_data['arguments']['transform_data'].extend(transform_data)
    input_data['arguments']['factory'] = factory
    # Create Complex
    from complex_factory import ComplexFactory
    c = ComplexFactory.new(input_data)
    primitives.extend(c.primitives)


# Complex in Primitive
def complex_in_primitive(primitives, li, gi, factory, transform_data,
                         x0s, x1s, y0s, y1s, z0s, z1s,
                         ts, txs, tys, tzs, lcs, lcs_map,
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
    # Primitive curves data
    cd = copy.deepcopy(curve_data[curve_data_map[gi]])
    cd_cs = curve_data_coord_sys[curve_data_coord_sys_map[gi]]
    if cd is not None and cd_cs == 'local':  # local to global coordinates
        for i, points in enumerate(cd):
            for j, p in enumerate(points):  # [xj, yj, zj, lcj]
                cd[i][j][0] = x0s[gi] + cd[i][j][0] * (x1s[gi] - x0s[gi])
                cd[i][j][1] = y0s[gi] + cd[i][j][1] * (y1s[gi] - y0s[gi])
                cd[i][j][2] = z0s[gi] + cd[i][j][2] * (z1s[gi] - z0s[gi])
    # Complex transforms
    c_ts = copy.deepcopy(inputs_transforms[inputs_transforms_map[gi]])
    c_cs = inputs_transforms_coord_sys[inputs_transforms_coord_sys_map[gi]]
    for i, t in enumerate(c_ts):
        if c_cs == 'local':  # local to global coordinates
            if len(t) == 3:  # Displacement
                c_ts[i][0] = x0s[gi] + t[0] * (x1s[gi] - x0s[gi])  # dx
                c_ts[i][1] = y0s[gi] + t[1] * (y1s[gi] - y0s[gi])  # dy
                c_ts[i][2] = z0s[gi] + t[2] * (z1s[gi] - z0s[gi])  # dz
            elif len(t) == 7:  # Rotation with origin and direction
                c_ts[i][0] = x0s[gi] + t[0] * (x1s[gi] - x0s[gi])  # origin x
                c_ts[i][1] = y0s[gi] + t[1] * (y1s[gi] - y0s[gi])  # origin y
                c_ts[i][2] = z0s[gi] + t[2] * (z1s[gi] - z0s[gi])  # origin z
            else:  # Rotation with direction only
                pass
    # Complex input data
    input_data = copy.deepcopy(inputs_datas[inputs_map[gi]])
    if input_data['arguments'].get('transform_data', None) is None:
        input_data['arguments']['transform_data'] = []
    input_data['arguments']['transform_data'].extend(c_ts)
    input_data['arguments']['transform_data'].extend(transform_data)
    input_data['arguments']['factory'] = factory
    # Create Complex
    from complex_factory import ComplexFactory
    c = ComplexFactory.new(input_data)
    primitives.extend(c.primitives)
    # Create Primitive
    xi, yi, zi = li  # local coordinates by axes
    primitives.append(Primitive(
        factory=factory,
        point_data=[
            [x1s[gi], y1s[gi], z0s[gi], lcs[lcs_map[gi]]],
            [x0s[gi], y1s[gi], z0s[gi], lcs[lcs_map[gi]]],
            [x0s[gi], y0s[gi], z0s[gi], lcs[lcs_map[gi]]],
            [x1s[gi], y0s[gi], z0s[gi], lcs[lcs_map[gi]]],
            [x1s[gi], y1s[gi], z1s[gi], lcs[lcs_map[gi]]],
            [x0s[gi], y1s[gi], z1s[gi], lcs[lcs_map[gi]]],
            [x0s[gi], y0s[gi], z1s[gi], lcs[lcs_map[gi]]],
            [x1s[gi], y0s[gi], z1s[gi], lcs[lcs_map[gi]]],
        ],
        transform_data=transform_data,
        transfinite_data=[ts[txs[xi]], ts[tys[yi]], ts[tzs[zi]]],
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


# Complex and Primitive (for boolean)
def complex_and_primitive(primitives, li, gi, factory, transform_data,
                          x0s, x1s, y0s, y1s, z0s, z1s,
                          ts, txs, tys, tzs, lcs, lcs_map,
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
    # Primitive curves data
    cd = copy.deepcopy(curve_data[curve_data_map[gi]])
    cd_cs = curve_data_coord_sys[curve_data_coord_sys_map[gi]]
    if cd is not None and cd_cs == 'local':  # local to global coordinates
        for i, points in enumerate(cd):
            for j, p in enumerate(points):  # [xj, yj, zj, lcj]
                cd[i][j][0] = x0s[gi] + cd[i][j][0] * (x1s[gi] - x0s[gi])
                cd[i][j][1] = y0s[gi] + cd[i][j][1] * (y1s[gi] - y0s[gi])
                cd[i][j][2] = z0s[gi] + cd[i][j][2] * (z1s[gi] - z0s[gi])
    # Complex transforms
    in_ts = copy.deepcopy(inputs_transforms[inputs_transforms_map[gi]])
    ts_cs = inputs_transforms_coord_sys[inputs_transforms_coord_sys_map[gi]]
    for i, t in enumerate(in_ts):
        if ts_cs == 'local':  # local to global coordinates
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
    # Complex input data
    input_data = copy.deepcopy(inputs_datas[inputs_map[gi]])
    if input_data['arguments'].get('transform_data', None) is None:
        input_data['arguments']['transform_data'] = []
    input_data['arguments']['transform_data'].extend(ts_cs)
    input_data['arguments']['transform_data'].extend(transform_data)
    input_data['arguments']['factory'] = factory
    # Create Complex
    from complex_factory import ComplexFactory
    c = ComplexFactory.new(input_data)
    primitives.extend(c.primitives)
    # Create Primitive
    xi, yi, zi = li  # local coordinates by axes
    primitives.append(Primitive(
        factory=factory,
        point_data=[
            [x1s[gi], y1s[gi], z0s[gi], lcs[lcs_map[gi]]],
            [x0s[gi], y1s[gi], z0s[gi], lcs[lcs_map[gi]]],
            [x0s[gi], y0s[gi], z0s[gi], lcs[lcs_map[gi]]],
            [x1s[gi], y0s[gi], z0s[gi], lcs[lcs_map[gi]]],
            [x1s[gi], y1s[gi], z1s[gi], lcs[lcs_map[gi]]],
            [x0s[gi], y1s[gi], z1s[gi], lcs[lcs_map[gi]]],
            [x0s[gi], y0s[gi], z1s[gi], lcs[lcs_map[gi]]],
            [x1s[gi], y0s[gi], z1s[gi], lcs[lcs_map[gi]]],
        ],
        transform_data=transform_data,
        transfinite_data=[ts[txs[xi]], ts[tys[yi]], ts[tzs[zi]]],
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
