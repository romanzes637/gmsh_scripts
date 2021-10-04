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
                 parent=None, children=None, children_transforms=None):
        self.factory = factory
        self.points = self.parse_points(points)
        self.curves = self.parse_curves(curves)
        self.surfaces = [{} for _ in range(6)] if surfaces is None else surfaces
        self.volumes = [{}] if volumes is None else volumes
        self.register_tag = register_tag
        self.do_register = do_register
        self.do_unregister = do_unregister
        self.do_register_children = do_register_children
        self.do_unregister_children = do_unregister_children
        self.transforms = self.parse_transforms(transforms, parent)
        self.recombine_all = recombine_all
        self.transfinite_all = transfinite_all
        self.parent = parent
        self.children = [] if children is None else children
        if children_transforms is None:
            children_transforms = [[] for _ in self.children]
        for i, t in enumerate(children_transforms):
            children_transforms[i] = self.parse_transforms(t, parent)
        self.children_transforms = children_transforms
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
        if points is None:
            points = [
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
        if isinstance(points, list):
            new_points = []
            if len(points) == 0:
                return points
            cs_name = 'cartesian'
            coord_system = cs_factory[cs_name]()
            dim = coord_system.dim
            if isinstance(points[-1], str):
                points, cs_name = points[:-1], points[-1]
            for p in points:
                if isinstance(p, dict):
                    cs = p.get('coordinate_system', cs_name)
                    if isinstance(cs, str):
                        p['coordinate_system'] = {'name': cs}
                    new_p = p
                elif isinstance(p, list):
                    if len(p) == dim and not isinstance(p[0], list):
                        new_p = {'coordinates': p,
                                 'coordinate_system':
                                     {'name': cs_name,
                                      'origin': [0, 0, 0]},
                                 'kwargs': {'meshSize': 0.}}
                    elif len(p) == dim + 1 and not isinstance(p[0], list):
                        new_p = {'coordinates': p[:3],
                                 'coordinate_system':
                                     {'name': cs_name,
                                      'origin': [0, 0, 0]},
                                 'kwargs': {'meshSize': p[3]}}
                    else:
                        raise ValueError(p)
                else:
                    raise ValueError(p)
                if cs_name == 'cylindrical':
                    new_p['coordinates'][1] = np.deg2rad(new_p['coordinates'][1])
                elif cs_name in ['spherical', 'toroidal', 'tokamak']:
                    new_p['coordinates'][1] = np.deg2rad(new_p['coordinates'][1])
                    new_p['coordinates'][2] = np.deg2rad(new_p['coordinates'][2])
                new_points.append(new_p)
            points = new_points
        else:
            raise ValueError(points)
        return points

    def parse_curves(self, curves):
        curves = [{} for _ in range(12)] if curves is None else curves
        for i, c in enumerate(curves):
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
                curves[i] = new_c
            else:
                raise ValueError(c)
            curves[i].setdefault('name', 'line')
            curves[i].setdefault('points', [])
            curves[i]['points'] = self.parse_points(curves[i]['points'])
        return curves

    def parse_transforms(self, transforms, parent):
        transforms = [] if transforms is None else transforms
        for i, t in enumerate(transforms):
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
            elif isinstance(t, dict):
                name = t.pop('name')
                kwargs = t
            else:
                raise ValueError(t)
            if 'angle' in kwargs:
                kwargs['angle'] = np.deg2rad(kwargs['angle'])
            if name.startswith('block'):
                ps = [x['coordinates'] for x in parent.points]
                kwargs['cs_from'] = cs_factory['block'](ps=ps)
            transforms[i] = transform_factory[name](**kwargs)
        return transforms

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

    def add_child(self, child, transforms=None):
        transforms = [] if transforms is None else transforms
        self.children.append(child)
        transforms = self.parse_transforms(transforms, self.parent)
        self.children_transforms.append(transforms)

    def transform(self):
        # Children
        for i, c in enumerate(self.children):
            c.transforms.extend(self.children_transforms[i])
            c.transforms.extend(self.transforms)
            c.transform()
        for i, p in enumerate(self.points):
            cs_kwargs = copy.deepcopy(p.get('coordinate_system', {}))
            cs_name = cs_kwargs.pop('name', 'cartesian')
            if cs_name.startswith('block'):
                ps = [x['coordinates'] for x in self.parent.points]
                cs_kwargs['ps'] = ps
            cs = cs_factory[cs_name](**cs_kwargs)
            vs = p.get('coordinates', np.zeros(3))
            p2 = Point(cs=cs, vs=vs)
            p2 = reduce_transforms(self.transforms, p2)
            self.points[i]['coordinates'] = p2.vs
        # Curve Points
        for i, c in enumerate(self.curves):
            for j, p in enumerate(c['points']):
                cs_kwargs = p.get('coordinate_system', {})
                cs_name = cs_kwargs.pop('name', 'cartesian')
                if cs_name.startswith('block'):
                    ps = [x['coordinates'] for x in self.parent.points]
                    cs_kwargs['ps'] = ps
                cs = cs_factory[cs_name](**cs_kwargs)
                vs = p.get('coordinates', np.zeros(3))
                p2 = Point(cs=cs, vs=vs)
                p2 = reduce_transforms(self.transforms, p2)
                self.curves[i]['points'][j]['coordinates'] = p2.vs

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
