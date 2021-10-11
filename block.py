import logging
from pprint import pprint
import copy
import time
import numpy as np

from support import volumes_surfaces_to_volumes_groups_surfaces
from transform import factory as transform_factory
from transform import reduce_transforms
from registry import register_point, register_curve, register_curve_loop, \
    register_surface, register_surface_loop, register_volume, \
    register_recombine_surface, register_transfinite_curve, \
    register_transfinite_surface, register_transfinite_volume, unregister_volume
from coordinate_system import factory as cs_factory
from point import Point
from curve import Curve
from curve_loop import CurveLoop
from surface import Surface
from surface_loop import SurfaceLoop
from volume import Volume
from structure import Structure
from quadrate import Quadrate


class Block:
    def __init__(self, factory='geo',
                 points=None, curves=None, surfaces=None, volumes=None,
                 do_register=True, use_register_tag=False, do_unregister=False,
                 do_register_children=True, do_unregister_children=True,
                 transforms=None,
                 recombine_all=None, transfinite_all=None,
                 parent=None, children=None, children_transforms=None,
                 boolean_level=None):
        """Basic building block of the mesh

        Block is a cuboid with 8 points, 12 curves, 6 surfaces and 1 volume.

        Note:
            If boolean_level is not None then no internal volumes of children.

        Args:
            points(list of dict, list of list, list): 8 corner points of the block
            curves(list of dict, list of list, list, list of Curve): 12 edge curves of the block
            surfaces(list of dict, list of list, list, list of Surface): 6 boundary surfaces of the block
            volumes(list of dict, list of list, list, list of Volume): volumes of the block (1 by now, TODO several volumes)
            do_register(bool): register Block in the registry
            use_register_tag(bool): use tag from registry instead tag from gmsh
            do_unregister(bool): unregister Block from the registry
            do_register_children(bool): invoke register for children
            do_unregister_children(bool): invoke unregister for children
            transforms(list of dict, list of list, list of Transform): points and curves points transforms (Translation, Rotation, Coordinate Change, etc)
            recombine_all(list of dict, bool): transform triangles to quadrangles for surfaces and tetrahedra to hexahedra for volumes
            transfinite_all(list of dict, list of list, list of Transform): make structured mesh instead of unstructured by some rule
            parent(Block): parent of the Block
            children(list of Block): children of the Block
            children_transforms(list of list of dict, list of list of list, list of list of Transform): transforms for children Blocks
            boolean_level(int): Block boolean level, if the Block level > another Block level, then intersected volume joins to the Block, if levels are equal third Block is created, if None - don't do boolean
        """
        self.factory = factory
        self.points = self.parse_points(points)
        self.curves = self.parse_curves(curves)
        self.surfaces = self.parse_surfaces(surfaces)
        self.volumes = self.parse_volumes(volumes)
        self.register_tag = use_register_tag
        self.do_register = do_register
        self.do_unregister = do_unregister
        self.do_register_children = do_register_children
        self.do_unregister_children = do_unregister_children
        self.transforms = self.parse_transforms(transforms, parent)
        self.recombine_all = recombine_all
        self.transfinite_all = self.parse_transfinite_all(transfinite_all)
        self.parent = parent
        self.children = [] if children is None else children
        if children_transforms is None:
            children_transforms = [[] for _ in self.children]
        for i, t in enumerate(children_transforms):
            children_transforms[i] = self.parse_transforms(t, parent)
        self.children_transforms = children_transforms
        self.boolean_level = boolean_level
        # Support
        self.curves_loops = [CurveLoop() for _ in range(6)]
        self.surfaces_loops = [SurfaceLoop()]
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
            points = [[0.5, 0.5, -0.5],
                      [-0.5, 0.5, -0.5],
                      [-0.5, -0.5, -0.5],
                      [0.5, -0.5, -0.5],
                      [0.5, 0.5, 0.5],
                      [0.5, 0.5, 0.5],
                      [0.5, 0.5, 0.5],
                      [0.5, 0.5, 0.5]]
            points = self.parse_points(points)
        elif isinstance(points, list):
            if len(points) == 0:  # Could be on curves points
                points = []
            # dx/dy/dz, cs
            elif all([len(points) == 2, any([isinstance(points[0], float),
                                             isinstance(points[0], int)]),
                      isinstance(points[1], str)]):
                a, cs_name = 0.5 * points[0], points[1]
                points = [[a, a, -a], [-a, a, -a], [-a, -a, -a], [a, -a, -a],
                          [a, a, a], [-a, a, a], [-a, -a, a], [a, -a, a],
                          cs_name]
                points = self.parse_points(points)
            # dx, dy, dz
            elif all([len(points) == 3,
                      any([isinstance(points[0], float),
                           isinstance(points[0], int)]),
                      any([isinstance(points[1], float),
                           isinstance(points[1], int)]),
                      any([isinstance(points[2], float),
                           isinstance(points[2], int)])]):
                a, b, c = 0.5 * points[0], 0.5 * points[1], 0.5 * points[2]
                points = [[a, b, -c], [-a, b, -c], [-a, -b, -c], [a, -b, -c],
                          [a, b, c], [-a, b, c], [-a, -b, c], [a, -b, c]]
                points = self.parse_points(points)
            # dx, dy, dz, cs
            elif all([len(points) == 4,
                      any([isinstance(points[0], float),
                           isinstance(points[0], int)]),
                      any([isinstance(points[1], float),
                           isinstance(points[1], int)]),
                      any([isinstance(points[2], float),
                           isinstance(points[2], int)]),
                      isinstance(points[3], str)]):
                a, b, c = 0.5 * points[0], 0.5 * points[1], 0.5 * points[2]
                cs_name = points[3]
                points = [[a, b, -c], [-a, b, -c], [-a, -b, -c], [a, -b, -c],
                          [a, b, c], [-a, b, c], [-a, -b, c], [a, -b, c],
                          cs_name]
                points = self.parse_points(points)
            else:  # [[x1, y1, z1, ...], [x2, y2, z2, ...], ...]
                new_points = []
                cs_name = 'cartesian'
                if isinstance(points[-1], str):
                    points, cs_name = points[:-1], points[-1]
                cs = cs_factory[cs_name]()
                for p in points:
                    if isinstance(p, dict):
                        cs_kwargs = p.get('coordinate_system', 'cartesian')
                        if isinstance(cs_kwargs, str):
                            p['coordinate_system'] = cs_factory[cs_kwargs]()
                        elif isinstance(cs_kwargs, dict):
                            cs_name = cs_kwargs.pop('name')
                            p['coordinate_system'] = cs_factory[cs_name](**cs_kwargs)
                        new_p = Point(**p)
                    elif isinstance(p, list):
                        if len(p) == cs.dim and not isinstance(p[0], list):
                            new_p = Point(coordinates=p, coordinate_system=cs)
                        elif len(p) == cs.dim + 1 and not isinstance(p[0], list):
                            cs = cs_factory['cartesian']()
                            new_p = Point(coordinates=p[:3],
                                          coordinate_system=cs,
                                          meshSize=p[3])
                        else:
                            raise ValueError(p)
                    else:
                        raise ValueError(p)
                    if cs_name == 'cylindrical':
                        new_p.coordinates[1] = np.deg2rad(new_p.coordinates[1])
                    elif cs_name in ['spherical', 'toroidal', 'tokamak']:
                        new_p.coordinates[1] = np.deg2rad(new_p.coordinates[1])
                        new_p.coordinates[2] = np.deg2rad(new_p.coordinates[2])
                    new_points.append(new_p)
                points = new_points
        elif isinstance(points, float) or isinstance(points, int):  # dx/dy/dz
            a = 0.5 * points
            points = [[a, a, -a], [-a, a, -a], [-a, -a, -a], [a, -a, -a],
                      [a, a, a], [-a, a, a], [-a, -a, a], [a, -a, a]]
            points = self.parse_points(points)
        else:
            raise ValueError(points)
        return points

    def parse_curves(self, curves):
        curves = [{} for _ in range(12)] if curves is None else curves
        for i, c in enumerate(curves):
            if isinstance(c, dict):
                curves[i] = Curve(**c)
            elif isinstance(c, list):
                new_c = Curve()
                if len(c) > 0:
                    if not isinstance(c[0], str):
                        Curve.name = 'polyline'
                        Curve.points = c
                    else:
                        if len(c) == 2:
                            Curve.name = c[0]
                            Curve.points = c[1]
                        elif len(c) == 3:
                            Curve.name = c[0]
                            Curve.points = c[1]
                            Curve.kwargs = c[2]
                        else:
                            raise ValueError(c)
                curves[i] = new_c
            else:
                raise ValueError(c)
            curves[i].points = self.parse_points(curves[i].points)
        return curves

    def parse_surfaces(self, surfaces):
        if surfaces is None:
            surfaces = [{} for _ in range(6)]
        for i, s in enumerate(surfaces):
            if isinstance(s, dict):
                surfaces[i] = Surface(**s)
            else:
                raise ValueError(s)
            surfaces[i].name = 'fill'
        return surfaces

    def parse_volumes(self, volumes):
        if volumes is None:
            volumes = [{}]
        for i, v in enumerate(volumes):
            if isinstance(v, dict):
                volumes[i] = Volume(**v)
            else:
                raise ValueError(v)
        return volumes

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
                ps = [x.coordinates for x in parent.points]
                kwargs['cs_from'] = cs_factory['block'](ps=ps)
            transforms[i] = transform_factory[name](**kwargs)
        return transforms

    def parse_transfinite_all(self, transfinite_all):
        if isinstance(transfinite_all, dict):
            if 'curves' in transfinite_all:
                value = copy.deepcopy(transfinite_all['curves'])
                for i, c in enumerate(self.curves):
                    self.curves[i].structure = Structure(**value)
            elif all(['curves_x' in transfinite_all,
                      'curves_y' in transfinite_all,
                      'curves_z' in transfinite_all]):
                for i, c in enumerate(self.curves):
                    direction = self.curves_directions[i]
                    key = f'curves_{direction}'
                    value = copy.deepcopy(transfinite_all[key])
                    self.curves[i].structure = Structure(**value)
            else:
                raise ValueError(transfinite_all)
            # Surfaces
            key = 'surfaces'
            value = copy.deepcopy(self.transfinite_all.get(
                key, {'name': 'surface'}))
            for i, s in enumerate(self.surfaces):
                self.surfaces[i].structure = Structure(**value)
            # Volume
            key = 'volumes'
            value = copy.deepcopy(self.transfinite_all.get(
                key, {'name': 'volume'}))
            self.volumes[0].structure = Structure(**value)
        elif isinstance(transfinite_all, list):
            if len(transfinite_all) == 3:
                # Curves
                d2i = {'curves_x': 0, 'curves_y': 1, 'curves_z': 2}
                for i, c in enumerate(self.curves):
                    direction = self.curves_directions[i]
                    key = f'curves_{direction}'
                    index = d2i[key]
                    values = transfinite_all[index]
                    value = {'name': 'curve',
                             'nPoints': values[0],
                             'meshType': values[1],
                             'coef': values[2]}
                    self.curves[i].structure = Structure(**value)
                # Surfaces
                for i, s in enumerate(self.surfaces):
                    self.surfaces[i].structure = Structure(name='surface')
                # Volume
                self.volumes[0].structure = Structure(name='volume')
        elif transfinite_all is None:
            pass
        else:
            raise ValueError(transfinite_all)
        return transfinite_all

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
            if isinstance(p.coordinate_system, cs_factory['block']):
                p.coordinate_system.ps = [x.coordinates
                                          for x in self.parent.points]
            self.points[i] = reduce_transforms(self.transforms, p)
        # Curve Points
        for i, c in enumerate(self.curves):
            for j, p in enumerate(c.points):
                if isinstance(p.coordinate_system, cs_factory['block']):
                    p.coordinate_system.ps = [x.coordinates
                                              for x in self.parent.points]
                self.curves[i].points[j] = reduce_transforms(self.transforms, p)

    def register_points(self):
        for i, p in enumerate(self.points):
            self.points[i] = register_point(self.factory, p, self.register_tag)

    def register_curve_points(self):
        for i, c in enumerate(self.curves):
            for j, p in enumerate(c.points):
                c.points[j] = register_point(self.factory, p, self.register_tag)
            # Add start and end points to curves
            p0 = self.points[self.curves_points[i][0]]
            p1 = self.points[self.curves_points[i][1]]
            c.points = [p0] + c.points + [p1]

    def register_curves(self):
        for i, c in enumerate(self.curves):
            self.curves[i] = register_curve(self.factory, c, self.register_tag)

    def register_curves_loops(self):
        for i, cl in enumerate(self.curves_loops):
            self.curves_loops[i].curves = [self.curves[x] for x in self.surfaces_curves[i]]
            self.curves_loops[i].curves_signs = self.surfaces_curves_signs[i]
            self.curves_loops[i] = register_curve_loop(self.factory,
                                                       self.curves_loops[i],
                                                       self.register_tag)

    def register_surfaces(self):
        for i, s in enumerate(self.surfaces):
            self.surfaces[i].curves_loops = [self.curves_loops[i]]
            self.surfaces[i] = register_surface(self.factory, self.surfaces[i], self.register_tag)

    def register_surfaces_loops(self):
        # External
        self.surfaces_loops[0].surfaces = self.surfaces
        self.surfaces_loops[0] = register_surface_loop(
            self.factory, self.surfaces_loops[0], self.register_tag)
        # Internal
        internal_volumes = []
        for i, c in enumerate(self.children):
            if c.do_register:
                if not c.is_registered:
                    raise ValueError('Register children before parent!')
                internal_volumes.append(c.volumes)
        volumes_surfaces = [[z.tag for z in y.surfaces_loops[0].surfaces]
                            for x in internal_volumes
                            for y in x]
        surfaces_groups = volumes_surfaces_to_volumes_groups_surfaces(
            volumes_surfaces)
        for g in surfaces_groups:
            sl = SurfaceLoop(surfaces=[Surface(tag=x) for x in g])
            sl = register_surface_loop(self.factory, sl, self.register_tag)
            self.surfaces_loops.append(sl)

    def register_volumes(self):
        v = self.volumes[0]
        v.surfaces_loops = self.surfaces_loops
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
                self.surfaces[i].quadrate = Quadrate(**self.recombine_all)
        # Recombine
        for i, s in enumerate(self.surfaces):
            if s.quadrate is not None:
                self.surfaces[i] = register_recombine_surface(s, self.factory)

    def transfinite_curves(self):
        # Transfinite
        for i, c in enumerate(self.curves):
            if c.structure is not None:
                self.curves[i] = register_transfinite_curve(c, self.factory)

    def transfinite_surfaces(self):
        # Transfinite
        for i, s in enumerate(self.surfaces):
            all_tr_curves = all(self.curves[x].structure is not None for x in
                                self.surfaces_curves[i])
            if all_tr_curves and s.structure is not None:
                s.structure.kwargs['cornerTags'] = [
                    self.points[x]['kwargs']['tag']
                    for x in self.surfaces_points[i]]
                s.structure.kwargs['arrangement'] = 'Right'
                self.surfaces[i] = register_transfinite_surface(s, self.factory)

    def transfinite_volume(self):
        # Transfinite
        v = self.volumes[0]
        all_tr_surfaces = all(x.quadrate is not None for x in self.surfaces)
        same_rec_surfaces = len(
            set(x.structure is not None for x in self.surfaces)) == 1
        if v.structure is not None and all_tr_surfaces and same_rec_surfaces:
            v.structure.kwargs['cornerTags'] = [x['kwargs']['tag']
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
