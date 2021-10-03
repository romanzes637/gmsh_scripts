import logging
from pprint import pprint
import copy
import time
import numpy as np

from support import volumes_surfaces_to_volumes_groups_surfaces
from transform import Point, cs_factory, transform_factory, reduce_transforms
from registry import register_point, register_curve, register_curve_loop, \
    register_surface, register_surface_loop, register_volume, \
    register_recombine_surface, register_transfinite_curve, \
    register_transfinite_surface, register_transfinite_volume, unregister_volume


class Block:
    def __init__(self, factory='geo',
                 points=None, curves=None, surfaces=None, volumes=None,
                 register_tag=False, do_register=True, do_unregister=False,
                 do_register_children=True, do_unregister_children=True,
                 transforms=None,
                 recombine_all=None, transfinite_all=None,
                 parent=None, children=None):
        self.factory = factory
        if points is None:
            self.points = [
                {'coordinates': [0.5, 0.5, -0.5],
                 'coordinate_system': {'name': 'cartesian', 'origin': [0, 0, 0]},
                 'kwargs': {'meshSize': 0.1}},
                {'coordinates': [-0.5, 0.5, -0.5],
                 'coordinate_system': {'name': 'cartesian', 'origin': [0, 0, 0]},
                 'kwargs': {'meshSize': 0.1}},
                {'coordinates': [-0.5, -0.5, -0.5],
                 'coordinate_system': {'name': 'cartesian', 'origin': [0, 0, 0]},
                 'kwargs': {'meshSize': 0.1}},
                {'coordinates': [0.5, -0.5, -0.5],
                 'coordinate_system': {'name': 'cartesian', 'origin': [0, 0, 0]},
                 'kwargs': {'meshSize': 0.1}},
                {'coordinates': [0.5, 0.5, 0.5],
                 'coordinate_system': {'name': 'cartesian', 'origin': [0, 0, 0]},
                 'kwargs': {'meshSize': 0.1}},
                {'coordinates': [-0.5, 0.5, 0.5],
                 'coordinate_system': {'name': 'cartesian', 'origin': [0, 0, 0]},
                 'kwargs': {'meshSize': 0.1}},
                {'coordinates': [-0.5, -0.5, 0.5],
                 'coordinate_system': {'name': 'cartesian', 'origin': [0, 0, 0]},
                 'kwargs': {'meshSize': 0.1}},
                {'coordinates': [0.5, -0.5, 0.5],
                 'coordinate_system': {'name': 'cartesian', 'origin': [0, 0, 0]},
                 'kwargs': {'meshSize': 0.1}}]
        elif isinstance(points, list):
            self.points = self.parse_points(points)
        else:
            raise ValueError(points)
        self.curves = [{} for _ in range(12)] if curves is None else curves
        for i, c in enumerate(self.curves):
            if isinstance(c, dict):
                pass
            elif isinstance(c, list):
                new_c = {}
                if len(c) > 0:
                    if not isinstance(c[0], str):
                        new_c['name'] = 'polyline'
                        new_c['points'] = c
                    else:
                        if len(c) == 2:
                            new_c['name'] = c[0]
                            new_c['points'] = c[1]
                        elif len(c) == 3:
                            new_c['name'] = c[0]
                            new_c['points'] = c[1]
                            new_c['kwargs'] = c[2]
                        else:
                            raise ValueError(c)
                self.curves[i] = new_c
            else:
                raise ValueError(c)
            self.curves[i].setdefault('name', 'line')
            self.curves[i].setdefault('points', [])
            self.curves[i]['points'] = self.parse_points(self.curves[i]['points'])
        self.surfaces = [{} for _ in range(6)] if surfaces is None else surfaces
        self.volumes = [{}] if volumes is None else volumes
        self.register_tag = register_tag
        self.do_register = do_register
        self.do_unregister = do_unregister
        self.do_register_children = do_register_children
        self.do_unregister_children = do_unregister_children
        self.transforms = [] if transforms is None else transforms
        for i, t in enumerate(self.transforms):
            if isinstance(t, str):
                name, kwargs = t, {}
            elif isinstance(t, list):
                if len(t) == 3:
                    name, kwargs = 'translate', {'delta': t}
                elif len(t) == 4:
                    name = 'rotate'
                    kwargs = {'origin': [0, 0, 0],
                              'direction': t[:3],
                              'angle': t[3]}
                elif len(t) == 7:
                    name = 'rotate'
                    kwargs = {'origin': t[:3],
                              'direction': t[3:6],
                              'angle': t[6]}
                else:
                    raise ValueError(t)
            else:
                name = t.pop('name')
                kwargs = t
            if 'angle' in kwargs:
                kwargs['angle'] = np.deg2rad(kwargs['angle'])
            if name.startswith('block'):
                ps = np.array([p['coordinates'] for p in parent.points])
                kwargs['cs_from'] = cs_factory['block'](ps=ps)
            self.transforms[i] = transform_factory[name](**kwargs)
        self.recombine_all = recombine_all
        self.transfinite_all = transfinite_all
        self.parent = parent
        self.children = [] if children is None else children
        # Support
        self.curves_loops = [{} for _ in range(6)]
        self.surfaces_loops = [{}]
        self.is_registered = False
        self.is_recombined = False
        self.is_transfinited = False

    curves_points = [
        [1, 0], [5, 4], [6, 7], [2, 3],
        [3, 0], [2, 1], [6, 5], [7, 4],
        [0, 4], [1, 5], [2, 6], [3, 7]
    ]

    curves_directions = ['x', 'x', 'x', 'x',
                         'y', 'y', 'y', 'y',
                         'z', 'z', 'z', 'z']

    surfaces_points = [
        [2, 6, 5, 1],  # NX
        [3, 7, 4, 0],  # X
        [2, 6, 7, 3],  # NY
        [1, 5, 4, 0],  # Y
        [3, 2, 1, 0],  # NZ
        [7, 6, 5, 4],  # Z
    ]

    surfaces_curves = [
        [5, 9, 6, 10],  # NX
        [4, 11, 7, 8],  # X
        [11, 2, 10, 3],  # NY
        [0, 8, 1, 9],  # Y
        [0, 5, 3, 4],  # NZ
        [1, 7, 2, 6],  # Z
    ]

    surfaces_curves_signs = [
        [1, 1, -1, -1],  # NX
        [-1, 1, 1, -1],  # X
        [1, -1, -1, 1],  # NY
        [1, 1, -1, -1],  # Y
        [-1, -1, 1, 1],  # NZ
        [1, -1, -1, 1],  # Z
    ]

    def parse_points(self, points):
        new_points = []
        if len(points) == 0:
            return new_points
        cs_name = 'cartesian'
        if isinstance(points[-1], str):
            points, cs_name = points[:-1], points[-1]
        for p in points:
            if isinstance(p, dict):
                cs = p.get('coordinate_system', cs_name)
                if isinstance(cs, str):
                    p['coordinate_system'] = {'name': cs}
                new_p = p
            elif isinstance(p, list):
                if len(p) == 3 and not isinstance(p[0], list):
                    new_p = {'coordinates': p,
                             'coordinate_system':
                                 {'name': cs_name,
                                  'origin': [0, 0, 0]},
                             'kwargs': {'meshSize': 0.}}
                elif len(p) == 4 and not isinstance(p[0], list):
                    new_p = {'coordinates': p[:3],
                             'coordinate_system':
                                 {'name': cs_name,
                                  'origin': [0, 0, 0]},
                             'kwargs': {'meshSize': p[3]}}
                else:
                    raise ValueError(p)
            else:
                raise ValueError(p)
            new_points.append(new_p)
        return new_points

    def register(self):
        # Children
        if self.do_register_children:
            for i, c in enumerate(self.children):
                c.register()
        # Self
        if not self.do_register:
            return
        if self.is_registered:
            return
        # Points
        # t0 = time.perf_counter()
        self.register_points()
        # print(f'register_points: {time.perf_counter() - t0}s')
        # Curves Points
        # t0 = time.perf_counter()
        self.register_curve_points()
        # print(f'register_curve_points: {time.perf_counter() - t0}s')
        # Curves
        # t0 = time.perf_counter()
        self.register_curves()
        # print(f'register_curves: {time.perf_counter() - t0}s')
        # Curve Loops
        # t0 = time.perf_counter()
        self.register_curves_loops()
        # print(f'register_curves_loops: {time.perf_counter() - t0}s')
        # Surfaces
        # t0 = time.perf_counter()
        self.register_surfaces()
        # print(f'register_surfaces: {time.perf_counter() - t0}s')
        # Surfaces Loops
        # t0 = time.perf_counter()
        self.register_surfaces_loops()
        # print(f'register_surfaces_loops: {time.perf_counter() - t0}s')
        # Volume
        # t0 = time.perf_counter()
        self.register_volumes()
        # print(f'register_volumes: {time.perf_counter() - t0}s')

    def transform(self):
        for i, c in enumerate(self.children):
            c.transforms.extend(self.transforms)
            c.transform()
        for i, p in enumerate(self.points):
            cs_kwargs = copy.deepcopy(p.get('coordinate_system', {}))
            cs_name = cs_kwargs.pop('name', 'cartesian')
            if cs_name.startswith('block'):
                ps = np.array([p['coordinates'] for p in self.parent.points])
                cs_kwargs['ps'] = ps
            cs = cs_factory[cs_name](**cs_kwargs)
            vs = p.get('coordinates', np.zeros(3))
            point = Point(cs=cs, vs=vs)
            point = reduce_transforms(self.transforms, point)
            self.points[i]['coordinates'] = point.vs
        # Curve Points
        for i, c in enumerate(self.curves):
            for j, p in enumerate(c['points']):
                cs_kwargs = p.get('coordinate_system', {})
                cs_name = cs_kwargs.pop('name', 'cartesian')
                if cs_name.startswith('block'):
                    ps = np.array([p['coordinates'] for p in self.parent.points])
                    cs_kwargs['ps'] = ps
                cs = cs_factory[cs_name](**cs_kwargs)
                vs = p.get('coordinates', np.zeros(3))
                point = Point(cs=cs, vs=vs)
                point = reduce_transforms(self.transforms, point)
                self.curves[i]['points'][j]['coordinates'] = point.vs

    def register_points(self):
        for i, p in enumerate(self.points):
            self.points[i] = register_point(self.factory, p, self.register_tag)

    def register_curve_points(self):
        for i, c in enumerate(self.curves):
            for j, p in enumerate(c['points']):
                c['points'][j] = register_point(self.factory, p, self.register_tag)
            # Add start and end points to curves
            p0 = self.points[self.curves_points[i][0]]
            p1 = self.points[self.curves_points[i][1]]
            c['points'] = [p0] + c['points'] + [p1]

    def register_curves(self):
        for i, c in enumerate(self.curves):
            self.curves[i] = register_curve(self.factory, c, self.register_tag)

    def register_curves_loops(self):
        for i, cl in enumerate(self.curves_loops):
            cl.setdefault('curves_tags', [
                self.curves[x]['kwargs']['tag'] * y for (x, y) in zip(
                    self.surfaces_curves[i], self.surfaces_curves_signs[i])])
            self.curves_loops[i] = register_curve_loop(self.factory, cl, self.register_tag)

    def register_surfaces(self):
        for i, s in enumerate(self.surfaces):
            s.setdefault('name', 'fill')
            s.setdefault('curve_loops', [self.curves_loops[i]])
            self.surfaces[i] = register_surface(self.factory, s, self.register_tag)

    def register_surfaces_loops(self):
        # External
        sl = self.surfaces_loops[0]
        sl.setdefault('surfaces_tags', [x['kwargs']['tag'] for x in self.surfaces])
        self.surfaces_loops[0] = register_surface_loop(self.factory, sl, self.register_tag)
        # Internal
        internal_volumes = []
        for i, c in enumerate(self.children):
            if c.do_register:
                if not c.is_registered:
                    raise ValueError('Register children before parent!')
                internal_volumes.append(c.volumes)
        volumes_surfaces = [y['surfaces_loops'][0]['surfaces_tags']
                            for x in internal_volumes for y in x]
        surfaces_groups = volumes_surfaces_to_volumes_groups_surfaces(
            volumes_surfaces)
        for g in surfaces_groups:
            sl = {'surfaces_tags': g}
            sl = register_surface_loop(self.factory, sl, self.register_tag)
            self.surfaces_loops.append(sl)

    def register_volumes(self):
        v = self.volumes[0]
        v.setdefault('surfaces_loops', self.surfaces_loops)
        self.volumes[0] = register_volume(self.factory, v, self.register_tag)
        self.is_registered = True

    def unregister(self):
        # Children
        if self.do_unregister_children:
            for i, c in enumerate(self.children):
                c.unregister()
        # Self
        if not self.do_unregister:
            return
        if self.is_registered:
            for i, v in enumerate(self.volumes):
                self.volumes[i] = unregister_volume(self.factory, v,
                                                    self.register_tag)
        else:
            raise ValueError('Block is not registered')

    def recombine_surfaces(self):
        # Check all
        if self.recombine_all is not None:
            if isinstance(self.recombine_all, bool):
                self.recombine_all = {}
            elif isinstance(self.recombine_all, dict):
                pass
            else:
                raise ValueError(self.recombine_all)
            for i, s in enumerate(self.surfaces):
                self.surfaces[i]['recombine'] = copy.deepcopy(
                    self.recombine_all)
        # Recombine
        for i, s in enumerate(self.surfaces):
            if 'recombine' in s:
                self.surfaces[i] = register_recombine_surface(s, self.factory)

    def transfinite_curves(self):
        # Check all
        if self.transfinite_all is not None:
            if 'curves' in self.transfinite_all:
                value = copy.deepcopy(self.transfinite_all['curves'])
                for i, c in enumerate(self.curves):
                    self.curves[i]['transfinite'] = value
            elif 'curves_x' in self.transfinite_all \
                    and 'curves_y' in self.transfinite_all \
                    and 'curves_z' in self.transfinite_all:
                for i, c in enumerate(self.curves):
                    direction = self.curves_directions[i]
                    key = f'curves_{direction}'
                    value = copy.deepcopy(self.transfinite_all[key])
                    self.curves[i]['transfinite'] = value
            else:
                raise ValueError(self.transfinite_all)
        # Transfinite
        for i, c in enumerate(self.curves):
            if 'transfinite' in c:
                self.curves[i] = register_transfinite_curve(c, self.factory)

    def transfinite_surfaces(self):
        # Check all
        if self.transfinite_all is not None:
            key = 'surfaces'
            value = copy.deepcopy(self.transfinite_all.get(key, {}))
            for i, s in enumerate(self.surfaces):
                self.surfaces[i]['transfinite'] = value
        # Transfinite
        for i, s in enumerate(self.surfaces):
            all_tr_curves = all('transfinite' in self.curves[x] for x in
                                self.surfaces_curves[i])
            if all_tr_curves and 'transfinite' in s:
                s['transfinite']['cornerTags'] = [
                    self.points[x]['kwargs']['tag']
                    for x in self.surfaces_points[i]]
                s['transfinite'].setdefault('kwargs', {})
                s['transfinite']['kwargs']['arrangement'] = 'Right'
                self.surfaces[i] = register_transfinite_surface(s, self.factory)

    def transfinite_volume(self):
        # Check all
        if self.transfinite_all is not None:
            key = 'volumes'
            value = copy.deepcopy(self.transfinite_all.get(key, {}))
            self.volumes[0]['transfinite'] = value
        # Transfinite
        v = self.volumes[0]
        all_tr_surfaces = all('recombine' in x for x in self.surfaces)
        same_rec_surfaces = len(
            set('transfinite' in x for x in self.surfaces)) == 1
        if 'transfinite' in v and all_tr_surfaces and same_rec_surfaces:
            v['transfinite']['cornerTags'] = [x['kwargs']['tag']
                                              for x in self.points]
            self.volumes[0] = register_transfinite_volume(v, self.factory)

    def recombine(self):
        # Children
        for i, c in enumerate(self.children):
            c.recombine()
        if self.is_recombined:
            return
        self.recombine_surfaces()
        self.is_recombined = True

    def transfinite(self):
        # Children
        for i, c in enumerate(self.children):
            c.transfinite()
        if self.is_transfinited:
            return
        # Curves
        self.transfinite_curves()
        # Surfaces
        self.transfinite_surfaces()
        # Volume
        self.transfinite_volume()
        self.is_transfinited = True

# class Primitive:
#     """
#     Primitive is a basic object that topologically represents a cuboid
#     i.e. a convex polyhedron bounded by six quadrilateral faces, whose polyhedral graph is the same as that of a cube.
#
#     | Primitive has 8 points, 12 curves, 6 surfaces and 1 volume.
#     | Primitive is the only object that can be meshed in a structured mesh.
#     | Primitive can contain internal volumes, if so it cannot be meshed in a structured mesh.
#
#     | **Object structure**
#
#     | **Axes**
#     | Y
#     | Z X
#     | NX, NY and NZ are negative X, Y and Z directions
#
#     | **Points**
#     | NZ:
#     | P1 P0
#     | P2 P3
#     | Z:
#     | P5 P4
#     | P6 P7
#
#     | **Curves**
#     | X direction curves from P0 by right-hand rule:
#     | C0: P1 -> P0
#     | C1: P5 -> P4
#     | C2: P6 -> P7
#     | C3: P2 -> P3
#     | Y direction curves from P0 by right-hand rule:
#     | C4: P3 -> P0
#     | C5: P2 -> P1
#     | C6: P6 -> P5
#     | C7: P7 -> P4
#     | Z direction curves from P0 by right-hand rule:
#     | C8:  P0 -> P4
#     | C9:  P1 -> P5
#     | C10: P2 -> P6
#     | C11: P3 -> P7
#
#     | **Surfaces**
#     | NX surface
#     | S0: C5  -> C9  -> -C6 -> -C10
#     | X surface
#     | S1: -C4 -> C11 -> C7  -> -C8
#     | NY surface
#     | S2: -C3 -> C10 -> C2  -> -C11
#     | Y surface
#     | S3: C0  -> C8  -> -C1 -> -C9
#     | NZ surface
#     | S4: -C0 -> -C5 ->  C3 -> C4
#     | Z surface
#     | S5: C1  -> -C7 -> -C2 -> C6
#
#     Args:
#         factory (str): gmsh factory
#             - 'geo' - gmsh
#             - 'occ' - OpenCASCADE
#         point_data (:obj:`numpy.ndarray`, optional): could be
#             - | Coordinates of points with characteristic lengths
#               | [[P0_X, P0_Y, P0_Z, P0_LC],
#               | [[P1_X, P1_Y, P1_Z, P1_LC],
#               | ...,
#               | [P7_X, P7_Y, P7_Z, P7_LC]]
#             - | Coordinates of points
#               | [[P0_X, P0_Y, P0_Z],
#               | [[P1_X, P1_Y, P1_Z],
#               | ...,
#               | [P7_X, P7_Y, P7_Z]]
#             - | Lengths by axes with characteristic length
#               | [L_X, L_Y, L_Z, LC]
#             - | Lengths by axes
#               | [L_X, L_Y, L_Z]
#         transform_data (list of transformation, optional):
#             transformations of points,
#             where transformation is a 2-tuple of data and mask
#
#             - | [[DX, DY, DZ], [P0_M, P1_M, ..., P7_M]]
#             - | [[RDX, RDY, RDZ, RA], [P0_M, P1_M, ..., P7_M]]
#             - | [[ROX, ROY, ROZ, RDX, RDY, RDZ, RA], [P0_M, P1_M, ..., P7_M]]
#             | where:
#             - | DX, DY, DZ - displacement
#             - | ROX, ROY, ROZ - origin of rotation
#             - | RDX, RDY, RDZ - direction of rotation
#             - | RA - angle of rotation
#             - | P0_M, P1_M, ..., P7_M - masks of points (0 - do transformation, 1 - do not)
#         curve_types (list of int):
#             [C0_TYPE, C1_TYPE, ..., C11_TYPE],
#
#             | TYPE:
#             - | 0 - line,
#             - | 1 - circle,
#             - | 2 - ellipse (FIXME not implemented for occ factory),
#             - | 3 - spline,
#             - | 4 - bspline (number of curve points > 1),
#             - | 5 - bezier curve
#         curve_data (list of list of list of float):
#             [[[line1_point1_x, line1_point1_y, line1_point1_z, line1_point1_lc],
#             ...], ..., [[line_12..., ...], ...]]] or
#             [[[line1_point1_x, line1_point1_y, line1_point1_z], ...],
#             ..., [[line_12_point_1, ...], ...]]]
#         transfinite_data (list of list of float):
#             [[line1 number of nodes, type, coefficient], ..., [line12 ...]]
#             or [[x_lines number of nodes, type, coefficient], [y_lines ...],
#             [z_lines ...]]
#             types: 0 - progression, 1 - bump
#         transfinite_type (int): 0, 1, 2 or 4 determines orientation
#             of surfaces' tetrahedra at structured volume
#         volume_name (str): primitive's volumes physical name
#         inner_volumes (list of int): inner volumes,
#             no effect at 'occ' factory, if point_data is None wrap these volumes
#             as Primitive.volumes
#         surfaces_names (list of str): names of boundary surfaces in order:
#             NX, X, NY, Y, NZ, Z.
#         rec (int): Recombine Primitive?
#         trans (int): Transfinite Primitive?
#     """
#
#     def __init__(self, factory, point_data=None, transform_data=None,
#                  curve_types=None, curve_data=None,
#                  transfinite_data=None, transfinite_type=None,
#                  volume_name=None, inner_volumes=None, surfaces_names=None,
#                  in_surfaces_names=None, in_surfaces_mask=None,
#                  rec=None, trans=None, boolean_level=None, exists=None):
#         t00 = time.perf_counter()
#         if factory == 'occ':
#             self.factory = gmsh.model.occ
#         else:
#             self.factory = gmsh.model.geo
#         if transfinite_data is not None:
#             if len(transfinite_data) == 3:
#                 self.transfinite_data = list()
#                 self.transfinite_data.extend([transfinite_data[0]] * 4)
#                 self.transfinite_data.extend([transfinite_data[1]] * 4)
#                 self.transfinite_data.extend([transfinite_data[2]] * 4)
#             else:
#                 self.transfinite_data = transfinite_data
#         else:
#             self.transfinite_data = transfinite_data
#         self.volume_name = volume_name if volume_name is not None else 'V'
#         if surfaces_names is None:
#             self.surfaces_names = ['NX', 'X', 'NY', 'Y', 'NZ', 'Z']
#         elif isinstance(surfaces_names, str):
#             self.surfaces_names = [surfaces_names for _ in range(6)]
#         else:
#             self.surfaces_names = surfaces_names
#         if in_surfaces_names is None:
#             self.in_surfaces_names = ['NXI', 'XI', 'NYI', 'YI', 'NZI', 'ZI']
#         elif isinstance(in_surfaces_names, str):
#             self.in_surfaces_names = [in_surfaces_names for _ in range(6)]
#         else:
#             self.in_surfaces_names = in_surfaces_names
#         if in_surfaces_mask is None:
#             self.in_surf_mask = np.zeros(6)
#         elif isinstance(in_surfaces_mask, int):
#             self.in_surf_mask = [in_surfaces_mask for _ in range(6)]
#         else:
#             self.in_surf_mask = in_surfaces_mask
#         self.transfinite_type = transfinite_type if transfinite_type is not None else 0
#         self.rec = rec if rec is not None else 1
#         self.trans = trans if trans is not None else 1
#         self.points = list()
#         self.curves_points = list()
#         self.curves = list()
#         self.surfaces = list()
#         self.volumes = list()
#         self.points_coordinates = list()
#         self.curves_points_coordinates = list()
#         self.bounding_box = None
#         self.coordinates_evaluated = False
#         self.boolean_level = boolean_level if boolean_level is not None else 0
#         self.exists = exists if exists is not None else 1
#         if transform_data is None:
#             transform_data = []
#         elif isinstance(transform_data, list):
#             if len(transform_data) > 0:
#                 if isinstance(transform_data[0], list):
#                     new_transform_data = []
#                     for td in transform_data:
#                         if isinstance(td[0], list):
#                             new_transform_data.append([np.array(td[0], dtype=float),
#                                                        np.array(td[1], dtype=int)])
#                         else:
#                             new_transform_data.append([np.array(td, dtype=float),
#                                                        np.zeros(8, dtype=int)])
#                     transform_data = new_transform_data
#                 else:
#                     raise ValueError(f'invalid transform_data: {transform_data}')
#         else:
#             raise ValueError(f'invalid transform_data: {transform_data}')
#         if curve_types is None:
#             curve_types = np.zeros(12)
#         if curve_data is None:
#             curve_data = [[] for _ in range(12)]
#         curve_data = [np.array(x, dtype=float) for x in curve_data]
#         if point_data is not None:
#             if len(point_data) == 3:
#                 half_lx = point_data[0] / 2.0
#                 half_ly = point_data[1] / 2.0
#                 half_lz = point_data[2] / 2.0
#                 lc = 1.
#                 point_data = np.array([
#                     [half_lx, half_ly, -half_lz, lc],
#                     [-half_lx, half_ly, -half_lz, lc],
#                     [-half_lx, -half_ly, -half_lz, lc],
#                     [half_lx, -half_ly, -half_lz, lc],
#                     [half_lx, half_ly, half_lz, lc],
#                     [-half_lx, half_ly, half_lz, lc],
#                     [-half_lx, -half_ly, half_lz, lc],
#                     [half_lx, -half_ly, half_lz, lc]
#                 ], dtype=float)
#             elif len(point_data) == 4:
#                 half_lx = point_data[0] / 2.0
#                 half_ly = point_data[1] / 2.0
#                 half_lz = point_data[2] / 2.0
#                 lc = point_data[3]
#                 point_data = np.array([
#                     [half_lx, half_ly, -half_lz, lc],
#                     [-half_lx, half_ly, -half_lz, lc],
#                     [-half_lx, -half_ly, -half_lz, lc],
#                     [half_lx, -half_ly, -half_lz, lc],
#                     [half_lx, half_ly, half_lz, lc],
#                     [-half_lx, half_ly, half_lz, lc],
#                     [-half_lx, -half_ly, half_lz, lc],
#                     [half_lx, -half_ly, half_lz, lc]
#                 ], dtype=float)
#             else:
#                 point_data = np.array(point_data, dtype=float)
#             # Points
#             # t0 = time.time()
#             for td in transform_data:
#                 d, m = td
#                 mask = np.array([[x for _ in range(3)]
#                                  for x in m], dtype=int)
#                 point_data[:, :3] = transform(point_data[:, :3], d, mask)
#             # print(point_data)
#             for d in point_data:
#                 d[0] = round(d[0], registry.point_tol)
#                 d[1] = round(d[1], registry.point_tol)
#                 d[2] = round(d[2], registry.point_tol)
#                 cs = tuple(d[:3])  # x, y and z coordinates
#                 # print(cs)
#                 tag = registry.coord_point_map.get(cs, None)
#                 if tag is None:
#                     tag = self.factory.addPoint(*d)
#                     registry.coord_point_map[cs] = tag
#                 else:
#                     pass
#                     # print(tag, cs, len(registry.coord_point_map), 'point')
#                 self.points.append(tag)
#             # print(f'points: {time.time() - t0}')
#             # Curves points
#             # t0 = time.time()
#             for td in transform_data:
#                 d, m = td
#                 for i in range(len(curve_data)):
#                     if len(curve_data[i]) > 0:
#                         lps = self.curves_local_points[i]
#                         mask = np.array([[m[lps[0]] * m[lps[1]]
#                              for _ in range(3)]
#                              for _ in range(curve_data[i].shape[0])], dtype=int)
#                         curve_data[i][:, :3] = transform(curve_data[i][:, :3],
#                                                          d, mask)
#             # logging.debug(f'curve_data: {curve_data}')
#             for i in range(len(curve_data)):
#                 ps = list()
#                 for j in range(len(curve_data[i])):
#                     curve_data[i][j][0] = round(curve_data[i][j][0],
#                                                 registry.point_tol)
#                     curve_data[i][j][1] = round(curve_data[i][j][1],
#                                                 registry.point_tol)
#                     curve_data[i][j][2] = round(curve_data[i][j][2],
#                                                 registry.point_tol)
#                     cs = tuple(curve_data[i][j][:3])  # x, y and z coordinates
#                     # print(cs)
#                     tag = registry.coord_point_map.get(cs, None)
#                     if tag is None:
#                         tag = self.factory.addPoint(*curve_data[i][j])
#                         registry.coord_point_map[cs] = tag
#                     else:
#                         pass
#                         # print(tag, len(registry.coord_point_map), 'curve_point')
#                     ps.append(tag)
#                 # print(ps, registry.coord_point_map)
#                 self.curves_points.append(ps)
#             # print(self.points)
#             # print(self.curves_points)
#             # print(f'curves points: {time.time() - t0}')
#             # Curves
#             # t0 = time.time()
#             for i in range(12):
#                 # FIXME Workaround for OCC factory
#                 ct = [curve_types[i]]
#                 if ct[0] == 0:
#                     ps = [self.points[self.curves_local_points[i][0]],
#                           self.points[self.curves_local_points[i][1]]]
#                 else:
#                     ps = [self.points[self.curves_local_points[i][0]]] + \
#                          self.curves_points[i] + \
#                          [self.points[self.curves_local_points[i][1]]]
#                 psr = list(reversed(ps))
#                 # print(ct)
#                 # print(ps)
#                 # print(psr)
#                 cs1 = tuple(ct + ps)
#                 cs2 = tuple(ct + psr)
#                 # print(ct, ps)
#                 # print(cs2)
#                 tag = registry.curves.get(cs1, None)
#                 if tag is None:
#                     if self.factory != gmsh.model.occ:
#                         tag = self.add_curve[curve_types[i]](self, i)
#                     else:
#                         tag = self.add_curve[curve_types[i] + 6](self, i)
#                     registry.curves[cs1] = tag
#                     registry.curves[cs2] = -tag
#                 else:
#                     pass
#                     # print(tag, cs1, len(registry.curves), 'curve')
#                 self.curves.append(tag)
#             # pprint(registry.curves)
#             # print('curves: {}'.format(len(registry.curves)))
#             # print(f'curves: {time.time() - t0}')
#             # Surfaces
#             # t0 = time.time()
#             for i in range(6):
#                 cs = list(map(lambda x, y: y * self.curves[x],
#                               self.surfaces_local_curves[i],
#                               self.surfaces_local_curves_signs[i]))
#                 # print(cs)
#                 deq = deque(cs)
#                 # print(deq)
#                 css = []
#                 for _ in range(len(deq)):
#                     deq.rotate(1)
#                     css.append(tuple(deq))
#                 deqr = deque([-1 * x for x in reversed(cs)])
#                 for _ in range(len(deqr)):
#                     deqr.rotate(1)
#                     css.append(tuple(deqr))
#                 # print(css)
#                 tag = None
#                 for c in css:
#                     tag = registry.surfaces.get(c, None)
#                     if tag is not None:
#                         break
#                 # t00 = time.time()
#                 if tag is None:
#                     if self.factory == gmsh.model.geo:
#                         tag = self.factory.addCurveLoop(
#                             list(map(lambda x, y: y * self.curves[x],
#                                      self.surfaces_local_curves[i],
#                                      self.surfaces_local_curves_signs[i])))
#                         tag = self.factory.addSurfaceFilling([tag])
#                     else:
#                         tag = self.factory.addCurveLoop(
#                             list(map(lambda x: self.curves[x],
#                                      self.surfaces_local_curves[i])))
#                         tag = self.factory.addSurfaceFilling(tag)
#                     for c in css:
#                         registry.surfaces[c] = tag
#                 else:
#                     pass
#                     # print(set(registry.surfaces.values()))
#                     # print(tag, css, len(registry.surfaces), 'surface')
#                 self.surfaces.append(tag)
#                 # print(f'surfaces2: {time.time() - t00}')
#             # print('surfaces: {}'.format(len(registry.curves)))
#             # print(len(self.surfaces))
#             # print(f'surfaces: {time.time() - t0}')
#             # Volume
#             # t0 = time.time()
#             if inner_volumes is None:
#                 # FIXME bug always return surface loop tag = -1
#                 # Workaround with registry surface_loop_tag
#                 if self.factory == gmsh.model.occ:
#                     registry.surface_loop_tag += 1
#                     sl_tag = self.factory.addSurfaceLoop(
#                         self.surfaces, registry.surface_loop_tag)
#                 else:
#                     sl_tag = self.factory.addSurfaceLoop(self.surfaces)
#                 tag = self.factory.addVolume([sl_tag])
#                 registry.volumes[tag] = self.surfaces
#             else:
#                 gs = volumes_groups_surfaces_registry(inner_volumes,
#                                                       registry.volumes)
#                 if self.factory == gmsh.model.occ:
#                     # FIXME bug always return surface loop tag = -1
#                     # Workaround with registry surface_loop_tag
#                     registry.surface_loop_tag += 1
#                     out_sl = self.factory.addSurfaceLoop(
#                         self.surfaces, registry.surface_loop_tag)
#                     in_sls = []
#                     for g in gs:
#                         registry.surface_loop_tag += 1
#                         in_sls.append(self.factory.addSurfaceLoop(
#                             g, registry.surface_loop_tag))
#                 else:
#                     out_sl = self.factory.addSurfaceLoop(self.surfaces)
#                     in_sls = [self.factory.addSurfaceLoop(x) for x in gs]
#                 tag = self.factory.addVolume([out_sl] + in_sls)
#                 registry.volumes[tag] = self.surfaces + list(itertools.chain.from_iterable(gs))
#             self.volumes.append(tag)
#             # print(f'volumes: {time.time() - t0}')
#         else:
#             if inner_volumes is not None:
#                 self.volumes = inner_volumes
#         # logging.debug(f'Primitive: {time.perf_counter() - t00:.3f}s')
#
#     def recombine(self):
#         if self.rec:
#             volumes_dim_tags = [(3, x) for x in self.volumes]
#             surfaces_dim_tags = gmsh.model.getBoundary(volumes_dim_tags,
#                                                        combined=False)
#             for dt in surfaces_dim_tags:
#                 gmsh.model.mesh.setRecombine(dt[0], dt[1])
#                 # if self.factory == gmsh.model.occ:
#                 #     gmsh.model.mesh.setRecombine(dt[0], dt[1])
#                 # else:
#                 #     self.factory.mesh.setRecombine(dt[0], dt[1])
#
#     def smooth(self, dim, n):
#         """
#         Smooth mesh. Currently works only with dim == 2
#         :param dim: Dimension
#         :param n: Number of smooth iterations
#         """
#         if dim == 1:
#             volumes_dim_tags = [(3, x) for x in self.volumes]
#             surfaces_dim_tags = gmsh.model.getBoundary(volumes_dim_tags,
#                                                        combined=False)
#             curves_dim_tags = gmsh.model.getBoundary(surfaces_dim_tags,
#                                                      combined=False)
#             for dt in curves_dim_tags:
#                 gmsh.model.mesh.setSmoothing(dim, dt[1], n)
#         elif dim == 2:
#             volumes_dim_tags = [(3, x) for x in self.volumes]
#             surfaces_dim_tags = gmsh.model.getBoundary(volumes_dim_tags,
#                                                        combined=False)
#             for dt in surfaces_dim_tags:
#                 gmsh.model.mesh.setSmoothing(dim, dt[1], n)
#         elif dim == 3:
#             for v in self.volumes:
#                 gmsh.model.mesh.setSmoothing(dim, v, n)
#
#     def transfinite(self, transfinited_surfaces, transfinited_curves):
#         """
#         Transfinite primitive
#         :param transfinited_surfaces: set() of already transfinite surfaces
#         (workaround for double transfinite issue)
#         :param transfinited_curves: set() of already transfinite curves
#         (workaround for double transfinite issue)
#         """
#         if self.trans:
#             result = False
#             # Check
#             check = False
#             # print(len(self.volumes))
#             if len(self.volumes) == 1:  # First
#                 volumes_dim_tags = [(3, x) for x in self.volumes]
#                 surfaces_dim_tags = gmsh.model.getBoundary(volumes_dim_tags,
#                                                            combined=False)
#                 if len(surfaces_dim_tags) == 6:  # Second
#                     points_dim_tags = gmsh.model.getBoundary(volumes_dim_tags,
#                                                              combined=False,
#                                                              recursive=True)
#                     if len(points_dim_tags) == 8:  # Third
#                         surfaces_points = []
#                         for dim_tag in surfaces_dim_tags:
#                             points_dim_tags = gmsh.model.getBoundary(
#                                 [(dim_tag[0], dim_tag[1])], combined=False,
#                                 recursive=True)
#                             surfaces_points.append(
#                                 list(map(lambda x: x[1], points_dim_tags)))
#                         is_4_points = True
#                         for surface_points in surfaces_points:
#                             if len(surface_points) != 4:  # Fourth
#                                 is_4_points = False
#                                 break
#                         if is_4_points:
#                             check = True
#             # Transfinite
#             if check:
#                 if self.transfinite_type == 0:
#                     transfinite_surface_data = [1, 1, 1, 1, 1, 1]
#                     transfinite_volume_data = [0]
#                 elif self.transfinite_type == 1:
#                     transfinite_surface_data = [1, 1, 0, 0, 0, 0]
#                     transfinite_volume_data = [1]
#                 elif self.transfinite_type == 2:
#                     transfinite_surface_data = [0, 0, 0, 0, 1, 1]
#                     transfinite_volume_data = [2]
#                 elif self.transfinite_type == 3:
#                     transfinite_surface_data = [0, 0, 1, 1, 0, 0]
#                     transfinite_volume_data = [3]
#                 else:
#                     transfinite_surface_data = None
#                     transfinite_volume_data = None
#                 if self.transfinite_data is not None:
#                     for i, c in enumerate(self.curves):
#                         if abs(c) not in transfinited_curves:
#                             transfinite_type = self.transfinite_data[i][1]
#                             # # FIXME Workaround for GEO factory
#                             # if self.factory != gmsh.model.geo:
#                             #     transfinite_type = self.transfinite_data[i][1]
#                             # else:
#                             #     transfinite_type = self.transfinite_data[i][
#                             #                            1] + 2
#                             self.transfinite_curve[transfinite_type](self, i)
#                             transfinited_curves.add(abs(c))
#                     if transfinite_surface_data is not None:
#                         for i, s in enumerate(self.surfaces):
#                             if s not in transfinited_surfaces:
#                                 transfinite_type = transfinite_surface_data[i]
#                                 # # FIXME Workaround for GEO factory
#                                 # if self.factory != gmsh.model.geo:
#                                 #     transfinite_type = transfinite_surface_data[
#                                 #         i]
#                                 # else:
#                                 #     transfinite_type = transfinite_surface_data[
#                                 #                            i] + 4
#                                 self.transfinite_surface[transfinite_type](self,
#                                                                            i)
#                                 transfinited_surfaces.add(s)
#                         if transfinite_volume_data is not None:
#                             for i in range(len(self.volumes)):
#                                 transfinite_type = transfinite_volume_data[i]
#                                 # FIXME Workaround for GEO factory
#                                 # if self.factory != gmsh.model.geo:
#                                 #     transfinite_type = transfinite_volume_data[
#                                 #         i]
#                                 # else:
#                                 #     transfinite_type = transfinite_volume_data[
#                                 #                            i] + 4
#                                 self.transfinite_volume[transfinite_type](self,
#                                                                           i)
#                     result = True
#             return result
#
#     def evaluate_coordinates(self):
#         if not self.coordinates_evaluated:
#             for point in self.points:
#                 bb = gmsh.model.getBoundingBox(0, point)
#                 self.points_coordinates.append([bb[0], bb[1], bb[2]])
#             for curve_points in self.curves_points:
#                 cs = []
#                 for point in curve_points:
#                     bb = gmsh.model.getBoundingBox(0, point)
#                     cs.append([bb[0], bb[1], bb[2]])
#                 self.curves_points_coordinates.append(cs)
#             self.coordinates_evaluated = True
#
#     def evaluate_bounding_box(self):
#         if len(self.volumes) > 0:
#             x_mins = []
#             y_mins = []
#             z_mins = []
#             x_maxs = []
#             y_maxs = []
#             z_maxs = []
#             volumes_dim_tags = [(3, x) for x in self.volumes]
#             for dim_tag in volumes_dim_tags:
#                 x_min, y_min, z_min, x_max, y_max, z_max = \
#                     gmsh.model.getBoundingBox(dim_tag[0], dim_tag[1])
#                 x_mins.append(x_min)
#                 y_mins.append(y_min)
#                 z_mins.append(z_min)
#                 x_maxs.append(x_max)
#                 y_maxs.append(y_max)
#                 z_maxs.append(z_max)
#             self.bounding_box = (min(x_mins), min(y_mins), min(z_mins),
#                                  max(x_maxs), max(y_maxs), max(z_maxs))
#         else:
#             self.bounding_box = (0, 0, 0, 0, 0, 0)
#
#     def set_size(self, size):
#         for v in self.volumes:
#             volume_dim_tag = (3, v)
#             points_dim_tags = gmsh.model.getBoundary([volume_dim_tag],
#                                                      combined=False,
#                                                      recursive=True)
#             gmsh.model.mesh.setSize(points_dim_tags, size)
#
#     def get_surfaces(self, combined=True):
#         if len(self.surfaces) == 6:  # unaffected Primitive
#             return self.surfaces
#         else:  # Primitive after boolean
#             volumes_dim_tags = [(3, x) for x in self.volumes]
#             surfaces_dim_tags = gmsh.model.getBoundary(volumes_dim_tags,
#                                                        combined=combined)
#             surfaces = [x[1] for x in surfaces_dim_tags]
#             return surfaces
#
#     curves_local_points = [
#         [1, 0], [5, 4], [6, 7], [2, 3],
#         [3, 0], [2, 1], [6, 5], [7, 4],
#         [0, 4], [1, 5], [2, 6], [3, 7]
#     ]
#
#     surfaces_local_points = [
#         [2, 6, 5, 1],  # NX
#         [3, 7, 4, 0],  # X
#         [2, 6, 7, 3],  # NY
#         [1, 5, 4, 0],  # Y
#         [3, 2, 1, 0],  # NZ
#         [7, 6, 5, 4],  # Z
#     ]
#
#     surfaces_local_curves = [
#         [5, 9, 6, 10],  # NX
#         [4, 11, 7, 8],  # X
#         # [3, 10, 2, 11],  # NY
#         [11, 2, 10, 3],  # NY
#         [0, 8, 1, 9],  # Y
#         [0, 5, 3, 4],  # NZ
#         [1, 7, 2, 6],  # Z
#     ]
#
#     surfaces_local_curves_signs = [
#         [1, 1, -1, -1],  # NX
#         [-1, 1, 1, -1],  # X
#         # [-1, 1, 1, -1],  # NY
#         [1, -1, -1, 1],  # NY
#         [1, 1, -1, -1],  # Y
#         [-1, -1, 1, 1],  # NZ
#         [1, -1, -1, 1],  # Z
#     ]
#
#     transfinite_curve = {
#         0: lambda self, i: gmsh.model.mesh.setTransfiniteCurve(
#             abs(self.curves[i]),
#             self.transfinite_data[i][0],
#             "Progression",
#             self.transfinite_data[i][2] if self.curves[i] > 0 else 1/self.transfinite_data[i][2]
#         ),
#         1: lambda self, i: gmsh.model.mesh.setTransfiniteCurve(
#             abs(self.curves[i]),
#             self.transfinite_data[i][0],
#             "Bump",
#             self.transfinite_data[i][2]
#         ),
#         # FIXME Workaround for GEO factory
#         2: lambda self, i: gmsh.model.mesh.setTransfiniteCurve(
#             self.curves[i],
#             self.transfinite_data[i][0],
#             "Progression",
#             self.transfinite_data[i][2]
#         ),
#         3: lambda self, i: gmsh.model.mesh.setTransfiniteCurve(
#             self.curves[i],
#             self.transfinite_data[i][0],
#             "Bump",
#             self.transfinite_data[i][2]
#         )
#     }
#
#     transfinite_surface = {
#         0: lambda self, i: gmsh.model.mesh.setTransfiniteSurface(
#             self.surfaces[i],
#             "Left",
#             [self.points[x] for x in self.surfaces_local_points[i]]
#         ),
#         1: lambda self, i: gmsh.model.mesh.setTransfiniteSurface(
#             self.surfaces[i],
#             "Right",
#             [self.points[x] for x in self.surfaces_local_points[i]]
#         ),
#         2: lambda self, i: gmsh.model.mesh.setTransfiniteSurface(
#             self.surfaces[i],
#             "AlternateLeft",
#             [self.points[x] for x in self.surfaces_local_points[i]]
#         ),
#         3: lambda self, i: gmsh.model.mesh.setTransfiniteSurface(
#             self.surfaces[i],
#             "AlternateRight",
#             [self.points[x] for x in self.surfaces_local_points[i]]
#         ),
#         # FIXME Workaround for GEO factory
#         4: lambda self, i: gmsh.model.mesh.setTransfiniteSurface(
#             self.surfaces[i],
#             "Left",
#             [self.points[x] for x in self.surfaces_local_points[i]]
#         ),
#         5: lambda self, i: gmsh.model.mesh.setTransfiniteSurface(
#             self.surfaces[i],
#             "Right",
#             [self.points[x] for x in self.surfaces_local_points[i]]
#         ),
#         6: lambda self, i: gmsh.model.mesh.setTransfiniteSurface(
#             self.surfaces[i],
#             "AlternateLeft",
#             [self.points[x] for x in self.surfaces_local_points[i]]
#         ),
#         7: lambda self, i: gmsh.model.mesh.setTransfiniteSurface(
#             self.surfaces[i],
#             "AlternateRight",
#             [self.points[x] for x in self.surfaces_local_points[i]]
#         )
#     }
#
#     transfinite_volume = {
#         0: lambda self, i: gmsh.model.mesh.setTransfiniteVolume(
#             self.volumes[i],
#             [
#                 self.points[0], self.points[1], self.points[2], self.points[3],
#                 self.points[4], self.points[5], self.points[6], self.points[7]
#             ]
#         ),
#         1: lambda self, i: gmsh.model.mesh.setTransfiniteVolume(
#             self.volumes[i],
#             [
#                 self.points[1], self.points[2], self.points[3], self.points[0],
#                 self.points[5], self.points[6], self.points[7], self.points[4]
#             ]
#         ),
#         2: lambda self, i: gmsh.model.mesh.setTransfiniteVolume(
#             self.volumes[i],
#             [
#                 self.points[2], self.points[3], self.points[0], self.points[1],
#                 self.points[6], self.points[7], self.points[4], self.points[5]
#             ]
#         ),
#         3: lambda self, i: gmsh.model.mesh.setTransfiniteVolume(
#             self.volumes[i],
#             [
#                 self.points[3], self.points[0], self.points[1], self.points[2],
#                 self.points[7], self.points[4], self.points[5], self.points[6]
#             ]
#         ),
#         # FIXME Workaround for GEO factory
#         4: lambda self, i: gmsh.model.mesh.setTransfiniteVolume(
#             self.volumes[i],
#             [
#                 self.points[0], self.points[1], self.points[2], self.points[3],
#                 self.points[4], self.points[5], self.points[6], self.points[7]
#             ]
#         ),
#         5: lambda self, i: gmsh.model.mesh.setTransfiniteVolume(
#             self.volumes[i],
#             [
#                 self.points[1], self.points[2], self.points[3], self.points[0],
#                 self.points[5], self.points[6], self.points[7], self.points[4]
#             ]
#         ),
#         6: lambda self, i: gmsh.model.mesh.setTransfiniteVolume(
#             self.volumes[i],
#             [
#                 self.points[2], self.points[3], self.points[0], self.points[1],
#                 self.points[6], self.points[7], self.points[4], self.points[5]
#             ]
#         ),
#         7: lambda self, i: gmsh.model.mesh.setTransfiniteVolume(
#             self.volumes[i],
#             [
#                 self.points[3], self.points[0], self.points[1], self.points[2],
#                 self.points[7], self.points[4], self.points[5], self.points[6]
#             ]
#         )
#     }
#
#     add_curve = {
#         0: lambda self, i: self.factory.addLine(
#             self.points[self.curves_local_points[i][0]],
#             self.points[self.curves_local_points[i][1]]
#         ),
#         1: lambda self, i: self.factory.addCircleArc(
#             self.points[self.curves_local_points[i][0]],
#             self.curves_points[i][0],
#             self.points[self.curves_local_points[i][1]]
#         ),
#         2: lambda self, i: self.factory.addEllipseArc(
#             self.points[self.curves_local_points[i][0]],
#             self.curves_points[i][0],
#             self.curves_points[i][1],
#             self.points[self.curves_local_points[i][1]],
#         ),
#         3: lambda self, i: self.factory.addSpline(
#             [self.points[self.curves_local_points[i][0]]] +
#             self.curves_points[i] +
#             [self.points[self.curves_local_points[i][1]]]
#         ),
#         4: lambda self, i: self.factory.addBSpline(
#             [self.points[self.curves_local_points[i][0]]] +
#             self.curves_points[i] +
#             [self.points[self.curves_local_points[i][1]]]
#         ),
#         5: lambda self, i: self.factory.addBezier(
#             [self.points[self.curves_local_points[i][0]]] +
#             self.curves_points[i] +
#             [self.points[self.curves_local_points[i][1]]]
#         ),
#         6: lambda self, i: self.factory.addLine(
#             self.points[self.curves_local_points[i][0]],
#             self.points[self.curves_local_points[i][1]]
#         ),
#         7: lambda self, i: self.factory.addCircleArc(
#             self.points[self.curves_local_points[i][0]],
#             self.curves_points[i][0],
#             self.points[self.curves_local_points[i][1]]
#         ),
#         # FIXME Workaround for OCC factory: addEllipseArc -> addCircleArc
#         8: lambda self, i: self.factory.addCircleArc(
#             self.points[self.curves_local_points[i][0]],
#             self.curves_points[i][0],
#             self.points[self.curves_local_points[i][1]],
#         ),
#         9: lambda self, i: self.factory.addSpline(
#             [self.points[self.curves_local_points[i][0]]] +
#             self.curves_points[i] +
#             [self.points[self.curves_local_points[i][1]]]
#         ),
#         10: lambda self, i: self.factory.addBSpline(
#             [self.points[self.curves_local_points[i][0]]] +
#             self.curves_points[i] +
#             [self.points[self.curves_local_points[i][1]]]
#         ),
#         11: lambda self, i: self.factory.addBezier(
#             [self.points[self.curves_local_points[i][0]]] +
#             self.curves_points[i] +
#             [self.points[self.curves_local_points[i][1]]]
#         )
#     }
#
#
# def rotation_matrix(axis, theta):
#     """
#     Return the rotation matrix associated with counterclockwise rotation about
#     the given axis by theta radians.
#     """
#     axis = np.array(axis)
#     axis = axis / np.sqrt(np.dot(axis, axis))
#     a = np.cos(np.radians(theta / 2.0))
#     b, c, d = -axis * np.sin(np.radians(theta / 2.0))
#     aa, bb, cc, dd = a * a, b * b, c * c, d * d
#     bc, ad, ac, ab, bd, cd = b * c, a * d, a * c, a * b, b * d, c * d
#     return np.array([[aa + bb - cc - dd, 2 * (bc + ad), 2 * (bd - ac)],
#                      [2 * (bc - ad), aa + cc - bb - dd, 2 * (cd + ab)],
#                      [2 * (bd + ac), 2 * (cd - ab), aa + dd - bb - cc]])
#
#
# def transform(ps, data, mask):
#     mps = np.ma.array(ps, mask=mask)
#     if len(data) == 7:  # rotation around dir by angle relative to origin
#         origin, direction, angle = data[:3], data[3:6], data[6]
#         m = rotation_matrix(direction, angle)
#         lps = mps - origin  # local coordinates relative to origin
#         mps = np.ma.dot(lps, m.T)
#         mps = np.ma.add(mps, origin)
#     elif len(data) == 4:  # rotation about dir by angle relative to (0, 0, 0)
#         direction, angle = data[:3], data[3]
#         m = rotation_matrix(direction, angle)
#         mps = np.ma.dot(mps, m.T)
#     else:  # displacement
#         displacement = data[:3]
#         mps = np.ma.add(mps, displacement)
#     ps = mps.filled(ps)
#     return ps
