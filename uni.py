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
    transform_to_transform, parse_indexing, transforms_to_transforms, \
    transform_transforms


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
                 coordinate_systems_map=None,
                 types=None, types_map=None,
                 lcs=None, lcs_map=None,
                 trans=None,
                 trans_map_x=None, trans_map_y=None, trans_map_z=None,
                 trans_type_map=None, trans_map=None, recs_map=None,
                 volumes=None, volumes_map=None,
                 surfaces=None, surfaces_map=None,
                 inputs=None, inputs_map=None,
                 inputs_transforms=None, inputs_transforms_map=None,
                 inputs_coordinate_systems=None,
                 inputs_coordinate_systems_transform_data=None,
                 inputs_coordinate_systems_map=None,
                 curves_types=None, curves_types_map=None,
                 curves=None, curves_map=None,
                 curves_coordinate_systems=None,
                 curves_coordinate_systems_transform_data=None,
                 curves_coordinate_systems_map=None,
                 boolean_level_map=None
                 ):
        """
        Universal Complex Point and Matrix
        :param str factory: see Primitive
        :param str coordinate_system: cartesian, cylindrical or spherical
        :param list of int coordinate_systems_map: coordinate systems map
        """
        # print(locals())
        # Factory
        factory = 'geo' if factory is None else factory
        if factory == 'occ':
            factory_object = gmsh.model.occ
        elif factory == 'geo':
            factory_object = gmsh.model.geo
        else:
            raise ValueError(factory)
        # Coordinates map
        if coordinates is not None:
            if points is not None:
                points = [[coordinates[y] for y in x] for x in points]
            if grid is not None:
                grid = [coordinates[y] if not isinstance(y, str) else y
                        for x in grid for y in x]
        if grid_coordinates_type is None:
            grid_coordinates_type = 'direct'
        # Indexing
        new_grid, new2old_l = [], []
        for x in grid:
            new_cs, n2o = parse_indexing(x, grid_coordinates_type)
            new_grid.append(new_cs)
            new2old_l.append(n2o)
        new2old_l = list(reversed(new2old_l))
        # New maps
        new_l2g = {}  # local index (xi, ..., zi, yi, xi) -> global index (gi) map
        new_g2l = {}  # global index (gi) map -> local index (xi, ..., zi, yi, xi)
        if grid_coordinates_type == 'delta':
            new_ns = [len(x) for x in new_grid]
        elif grid_coordinates_type == 'direct':
            new_ns = [len(x) - 1 for x in new_grid]
        else:
            raise ValueError(grid_coordinates_type)
        new_ni = reduce(lambda x, y: x * y, new_ns)  # number of matrix items
        new_indexes = [range(x) for x in new_ns]
        for gi, li in enumerate(product(*reversed(new_indexes))):
            new_l2g[li] = gi
            new_g2l[gi] = li
        # Old maps
        old_l2g = {}  # local index (xi, ..., zi, yi, xi) -> global index (gi) map
        old_g2l = {}  # global index (gi) map -> local index (xi, ..., zi, yi, xi)
        if grid_coordinates_type == 'delta':
            old_ns = [len([y for y in x if not isinstance(y, str)]) for x in grid]
        elif grid_coordinates_type == 'direct':
            old_ns = [len([y for y in x if not isinstance(y, str)]) - 1 for x in grid]
        else:
            raise ValueError(grid_coordinates_type)
        old_ni = reduce(lambda x, y: x * y, old_ns)  # number of matrix items
        old_indexes = [range(x) for x in old_ns]
        for gi, li in enumerate(product(*reversed(old_indexes))):
            old_l2g[li] = gi
            old_g2l[gi] = li
        # New to old global index map
        new2old_g = {}
        for new_l, new_g in new_l2g.items():
            old_l = tuple(new2old_l[i][x] for i, x in enumerate(new_l))
            new2old_g[new_g] = old_l2g[old_l]
        if isinstance(types_map, list):
            types_map = [types_map[new2old_g[i]] for i in range(new_ni)]
        if isinstance(lcs_map, list):
            lcs_map = [lcs_map[new2old_g[i]] for i in range(new_ni)]
        if isinstance(trans_map_x, list):
            trans_map_x = [trans_map_x[new2old_l[-1][i]] for i in range(new_ns[0])]
        if isinstance(trans_map_y, list):
            trans_map_y = [trans_map_y[new2old_l[-2][i]] for i in range(new_ns[1])]
        if isinstance(trans_map_x, list):
            trans_map_z = [trans_map_z[new2old_l[-3][i]] for i in range(new_ns[2])]
        if isinstance(trans_type_map, list):
            trans_type_map = [trans_type_map[new2old_g[i]] for i in range(new_ni)]
        if isinstance(trans_map, list):
            trans_map = [trans_map[new2old_g[i]] for i in range(new_ni)]
        if isinstance(recs_map, list):
            recs_map = [recs_map[new2old_g[i]] for i in range(new_ni)]
        if isinstance(volumes_map, list):
            volumes_map = [volumes_map[new2old_g[i]] for i in range(new_ni)]
        if isinstance(surfaces_map, list):
            surfaces_map = [surfaces_map[new2old_g[i]] for i in range(new_ni)]
        grid = new_grid
        if points is not None:
            ni = nx = ny = nz = len(points)  # number of matrix items
            l2g = {}  # local index (x1, x2, ..., xi) -> global index (gi) map
            g2l = {}  # global index (gi) map -> local index (x1, x2, ..., xi)
            for i in range(ni):
                gi = i
                l2g[tuple(gi for _ in range(ni))] = gi
                g2l[gi] = tuple(gi for _ in range(ni))
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
        elif coordinate_system not in ['cartesian']:
            # TODO transform_data with various coordinate systems
            # Needs system convertion at complex, complex_in_primitive
            # and complex_and_primitive transform_data
            raise NotImplementedError(coordinate_system)
        if transform_data is None:
            transform_data = []
        # Global curvilinear to global cartesian
        for i, t in enumerate(transform_data):
            transform_data[i] = transform_to_transform(
                t, coordinate_system, 'cartesian')
        # Coordinate systems
        if coordinate_systems is None:
            coordinate_systems = ['cartesian']
        if coordinate_systems_transform_data is None:  # In coordinate_system
            coordinate_systems_transform_data = [[] for _ in coordinate_systems]
        if inputs_coordinate_systems is None:
            inputs_coordinate_systems = ['cell']
        if inputs_coordinate_systems_transform_data is None:
            inputs_coordinate_systems_transform_data = [
                [] for _ in inputs_coordinate_systems]
        if curves_coordinate_systems is None:
            curves_coordinate_systems = ['cell']
        if curves_coordinate_systems_transform_data is None:
            curves_coordinate_systems_transform_data = [
                [] for _ in curves_coordinate_systems]
        # Global curvilinear to global cartesian
        for i, td in enumerate(coordinate_systems_transform_data):
            for j, t in enumerate(td):
                coordinate_systems_transform_data[i][j] = transform_to_transform(
                    t, coordinate_system, 'cartesian')
        if coordinate_systems_map is None:
            coordinate_systems_map = [0 for _ in range(ni)]
        elif not isinstance(coordinate_systems_map, list):
            coordinate_systems_map = [coordinate_systems_map for _ in range(ni)]
        if inputs_coordinate_systems_map is None:
            inputs_coordinate_systems_map = [0 for _ in range(ni)]
        elif not isinstance(inputs_coordinate_systems_map, list):
            inputs_coordinate_systems_map = [inputs_coordinate_systems_map for _ in range(ni)]
        if curves_coordinate_systems_map is None:
            curves_coordinate_systems_map = [0 for _ in range(ni)]
        elif not isinstance(curves_coordinate_systems_map, list):
            curves_coordinate_systems_map = [curves_coordinate_systems_map for _ in range(ni)]
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
        curves_types = [None] if curves_types is None else curves_types
        if curves_types_map is None:
            curves_types_map = [0 for _ in range(ni)]
        elif not isinstance(curves_types_map, list):
            curves_types_map = [curves_types_map for _ in range(ni)]
        curves = [None] if curves is None else curves
        if curves_map is None:
            curves_map = [0 for _ in range(ni)]
        elif not isinstance(curves_map, list):
            curves_map = [curves_map for _ in range(ni)]
        # Data
        inputs_transforms_data = []
        inputs_transforms_data_cs = []
        inputs_transforms_data_ds = []
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
                inputs_transforms_data.append(
                    inputs_transforms[inputs_transforms_map[gi]])
                inputs_transforms_data_cs.append([
                    [x0, y0, z0] + [x0i, x1i, y0i, y1i, z0i, z1i] for _ in
                    inputs_transforms[inputs_transforms_map[gi]]])
                inputs_transforms_data_ds.append([ds for _ in
                    inputs_transforms[inputs_transforms_map[gi]]])
        # Local curvilinear to global cartesian
        for gi in range(ni):
            cs = coordinate_systems[coordinate_systems_map[gi]]
            td = coordinate_systems_transform_data[coordinate_systems_map[gi]]
            inputs_cs = inputs_coordinate_systems[inputs_coordinate_systems_map[gi]]
            # Local cell to local curvilinear
            inputs_transforms_data[gi] = transforms_to_transforms(
                inputs_transforms_data[gi], inputs_cs, 'local',
                inputs_transforms_data_cs[gi])
            # Local curvilinear to local cartesian
            point_datas[gi] = coordinates_to_coordinates(
                point_datas[gi], cs, 'cartesian')
            inputs_transforms_data[gi] = transforms_to_transforms(
                inputs_transforms_data[gi], cs, 'cartesian',
                inputs_transforms_data_ds[gi])
            if points is not None:
                points[gi] = coordinates_to_coordinates(
                    [points[gi]], cs, 'cartesian')[0]
            # Local cartesian to global cartesian transform
            for t in td:
                point_datas[gi] = transform(point_datas[gi], t)
                if points is not None:
                    points[gi] = transform([points[gi]], t)[0]
        # Arguments
        print(f'Number of items: {ni}')
        if types is None:
            types = ['primitive']
        if types_map is None:
            types_map = [0 for _ in range(ni)]
        if lcs is None:
            lcs = [1 for _ in range(ni)]
        elif not isinstance(lcs, list):
            lcs = [lcs for _ in range(ni)]
        if lcs_map is None:
            lcs_map = [0 for _ in range(ni)]
        elif not isinstance(lcs_map, list):
            lcs_map = [lcs_map for _ in range(ni)]
        if trans is None:
            trans = [[3, 0, 1]]
        if trans_map_x is None:
            trans_map_x = [0 for _ in range(nx)]
        elif not isinstance(trans_map_x, list):
            trans_map_x = [trans_map_x for _ in range(nx)]
        if trans_map_y is None:
            trans_map_y = [0 for _ in range(ny)]
        elif not isinstance(trans_map_y, list):
            trans_map_y = [trans_map_y for _ in range(ny)]
        if trans_map_z is None:
            trans_map_z = [0 for _ in range(nz)]
        elif not isinstance(trans_map_z, list):
            trans_map_z = [trans_map_z for _ in range(nz)]
        if trans_map is None:
            trans_map = [1 for _ in range(ni)]
        elif not isinstance(trans_map, list):
            trans_map = [trans_map for _ in range(ni)]
        if trans_type_map is None:
            trans_type_map = [0 for _ in range(ni)]
        elif not isinstance(trans_type_map, list):
            trans_type_map = [trans_type_map for _ in range(ni)]
        if recs_map is None:
            recs_map = [1 for _ in range(ni)]
        elif not isinstance(recs_map, list):
            recs_map = [recs_map for _ in range(ni)]
        # volumes
        if volumes is None:
            volumes = [None]
        elif isinstance(volumes, str):
            volumes = [volumes]
        if volumes_map is None:
            volumes_map = [0 for _ in range(ni)]
        elif not isinstance(volumes_map, list):
            volumes_map = [volumes_map for _ in range(ni)]
        if surfaces is None:
            surfaces = [None]
        elif isinstance(surfaces, str):
            surfaces = [[surfaces for _ in range(6)]]
        if surfaces_map is None:
            surfaces_map = [0 for _ in range(ni)]
        elif not isinstance(surfaces_map, list):
            surfaces_map = [surfaces_map for _ in range(ni)]
        # if in_surfaces_masks is None:
        #     in_surfaces_masks = [None]
        # elif isinstance(in_surfaces_masks, str):
        #     in_surfaces_masks = [[in_surfaces_masks for _ in range(6)]]
        # if in_surfaces_map is None:
        #     in_surfaces_map = [0 for _ in range(ni)]
        # elif isinstance(in_surfaces_map, int):
        #     in_surfaces_map = [in_surfaces_map for _ in range(ni)]
        # if in_surfaces_masks_map is None:
        #     in_surfaces_masks_map = [0 for _ in range(ni)]
        # elif isinstance(in_surfaces_masks_map, int):
        #     in_surfaces_masks_map = [in_surfaces_masks_map for _ in range(ni)]
        if boolean_level_map is None:
            boolean_level_map = [0 for _ in range(ni)]
        elif not isinstance(boolean_level_map, list):
            boolean_level_map = [boolean_level_map for _ in range(ni)]
        # download inputs
        inputs_datas = []
        for i in inputs:
            result = check_file(i)
            with open(result['path']) as f:
                d = json.load(f)
            inputs_datas.append(d)
        # Process
        primitives = []
        for li, gi in l2g.items():
            globals()[types[types_map[gi]]](**locals())
        Complex.__init__(self, factory, primitives)


# Empty
def empty(**kwargs):
    pass


# Primitive
def primitive(primitives, li, gi, factory, transform_data, point_datas,
              lcs, lcs_map,
              trans, trans_map_x, trans_map_y, trans_map_z,
              trans_type_map, trans_map, recs_map,
              volumes, volumes_map,
              surfaces, surfaces_map,
              **kwargs):
    pd = point_datas[gi]
    lc = np.array([[lcs[lcs_map[gi]]] for _ in range(8)])
    pd = np.concatenate((pd, lc), axis=1)
    zi, yi, xi = li[-3:]
    primitives.append(Primitive(
        factory=factory,
        transform_data=transform_data,
        point_data=pd,
        transfinite_data=[trans[trans_map_x[xi]],
                          trans[trans_map_y[yi]],
                          trans[trans_map_z[zi]]],
        trans=trans_map[gi],
        transfinite_type=trans_type_map[gi],
        rec=recs_map[gi],
        volume_name=volumes[volumes_map[gi]],
        surfaces_names=surfaces[surfaces_map[gi]],
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
            inputs_datas, inputs_map,
            inputs_transforms_data,
            coordinate_systems_transform_data, coordinate_systems_map,
            **kwargs):
    # Complex input data
    input_data = copy.deepcopy(inputs_datas[inputs_map[gi]])
    if input_data['arguments'].get('transform_data', None) is None:
        input_data['arguments']['transform_data'] = []
    input_data['arguments']['transform_data'].extend(inputs_transforms_data[gi])
    input_data['arguments']['transform_data'].extend(
        coordinate_systems_transform_data[coordinate_systems_map[gi]])
    input_data['arguments']['transform_data'].extend(transform_data)
    print(input_data['arguments']['transform_data'])
    input_data['arguments']['factory'] = factory
    # Create Complex
    from complex_factory import ComplexFactory
    c = ComplexFactory.new(input_data)
    primitives.extend(c.primitives)


# Complex in Primitive
def complex_in_primitive(primitives, li, gi, factory,
                          transform_data, point_datas,
                          lcs, lcs_map, inputs_datas,
                          trans, trans_map_x, trans_map_y, trans_map_z,
                          trans_type_map, trans_map, recs_map,
                          volumes, volumes_map,
                          surfaces, surfaces_map,
                          inputs_map,
                          inputs_transforms_data,
                          coordinate_systems_transform_data,
                          coordinate_systems_map,
                         **kwargs):
    # Complex input data
    input_data = copy.deepcopy(inputs_datas[inputs_map[gi]])
    if input_data['arguments'].get('transform_data', None) is None:
        input_data['arguments']['transform_data'] = []
    input_data['arguments']['transform_data'].extend(inputs_transforms_data[gi])
    input_data['arguments']['transform_data'].extend(
        coordinate_systems_transform_data[coordinate_systems_map[gi]])
    input_data['arguments']['transform_data'].extend(transform_data)
    input_data['arguments']['factory'] = factory
    # Create Complex
    from complex_factory import ComplexFactory
    c = ComplexFactory.new(input_data)
    primitives.extend(c.primitives)
    # Create Primitive
    pd = point_datas[gi]
    lc = np.array([[lcs[lcs_map[gi]]] for _ in range(8)])
    pd = np.concatenate((pd, lc), axis=1)
    zi, yi, xi = li[-3:]
    primitives.append(Primitive(
        factory=factory,
        transform_data=transform_data,
        point_data=pd,
        transfinite_data=[trans[trans_map_x[xi]],
                          trans[trans_map_y[yi]],
                          trans[trans_map_z[zi]]],
        inner_volumes=c.get_volumes(),
        trans=trans_map[gi],
        transfinite_type=trans_type_map[gi],
        rec=recs_map[gi],
        volume_name=volumes[volumes_map[gi]],
        surfaces_names=surfaces[surfaces_map[gi]],
    ))

# Complex and Primitive (for boolean)
def complex_and_primitive(primitives, li, gi, factory,
                          transform_data, point_datas,
                          lcs, lcs_map, inputs_datas,
                          trans, trans_map_x, trans_map_y, trans_map_z,
                          trans_type_map, trans_map, recs_map,
                          volumes, volumes_map,
                          surfaces, surfaces_map,
                          inputs_map,
                          inputs_transforms_data,
                          coordinate_systems_transform_data,
                          coordinate_systems_map,
                          **kwargs):
    # Complex input data
    input_data = copy.deepcopy(inputs_datas[inputs_map[gi]])
    if input_data['arguments'].get('transform_data', None) is None:
        input_data['arguments']['transform_data'] = []
    input_data['arguments']['transform_data'].extend(inputs_transforms_data[gi])
    input_data['arguments']['transform_data'].extend(
        coordinate_systems_transform_data[coordinate_systems_map[gi]])
    input_data['arguments']['transform_data'].extend(transform_data)
    input_data['arguments']['factory'] = factory
    # Create Complex
    from complex_factory import ComplexFactory
    c = ComplexFactory.new(input_data)
    primitives.extend(c.primitives)
    # Create Primitive
    pd = point_datas[gi]
    lc = np.array([[lcs[lcs_map[gi]]] for _ in range(8)])
    pd = np.concatenate((pd, lc), axis=1)
    zi, yi, xi = li[-3:]
    primitives.append(Primitive(
        factory=factory,
        transform_data=transform_data,
        point_data=pd,
        transfinite_data=[trans[trans_map_x[xi]],
                          trans[trans_map_y[yi]],
                          trans[trans_map_z[zi]]],
        trans=trans_map[gi],
        transfinite_type=trans_type_map[gi],
        rec=recs_map[gi],
        volume_name=volumes[volumes_map[gi]],
        surfaces_names=surfaces[surfaces_map[gi]],
    ))
