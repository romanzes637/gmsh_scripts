import logging
from pprint import pprint
import copy
import time
import numpy as np
import itertools

from support import volumes_surfaces_to_volumes_groups_surfaces
from transform import factory as transform_factory
from transform import reduce_transforms
from registry import register_point, register_curve, register_curve_loop, \
    register_surface, register_surface_loop, register_volume, \
    register_quadrate_surface, register_structure_curve, \
    register_structure_surface, register_structure_volume, unregister_volume
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
                 quadrate_all=None, structure_all=None,
                 parent=None, children=None, children_transforms=None,
                 boolean_level=None):
        """Basic building block of the mesh

        Block is a cuboid with 8 points, 12 curves, 6 surfaces and 1 volume.

        | **Axes**
        | Y
        | Z X
        | NX, NY and NZ are negative X, Y and Z directions

        | **Points**
        | NZ:
        | P1 P0
        | P2 P3
        | Z:
        | P5 P4
        | P6 P7

        | **Curves**
        | X direction curves from P0 by right-hand rule:
        | C0: P1 -> P0
        | C1: P5 -> P4
        | C2: P6 -> P7
        | C3: P2 -> P3
        | Y direction curves from P0 by right-hand rule:
        | C4: P3 -> P0
        | C5: P2 -> P1
        | C6: P6 -> P5
        | C7: P7 -> P4
        | Z direction curves from P0 by right-hand rule:
        | C8:  P0 -> P4
        | C9:  P1 -> P5
        | C10: P2 -> P6
        | C11: P3 -> P7

        | **Surfaces**
        | NX surface
        | S0: C5  -> C9  -> -C6 -> -C10
        | X surface
        | S1: -C4 -> C11 -> C7  -> -C8
        | NY surface
        | S2: -C3 -> C10 -> C2  -> -C11
        | Y surface
        | S3: C0  -> C8  -> -C1 -> -C9
        | NZ surface
        | S4: -C0 -> -C5 ->  C3 -> C4
        | Z surface
        | S5: C1  -> -C7 -> -C2 -> C6

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
            quadrate_all(list of dict, bool): transform triangles to quadrangles for surfaces and tetrahedra to hexahedra for volumes
            structure_all(list of dict, list of list, list of Transform): make structured mesh instead of unstructured by some rule
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
        self.quadrate_all = quadrate_all
        self.structure_all = self.parse_structure_all(structure_all)
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
        self.is_quadrated = False
        self.is_structured = False

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
        elif isinstance(points, float) or isinstance(points, int):  # dx/dy/dz
            a = 0.5 * points
            points = [[a, a, -a], [-a, a, -a], [-a, -a, -a], [a, -a, -a],
                      [a, a, a], [-a, a, a], [-a, -a, a], [a, -a, a]]
            points = self.parse_points(points)
        elif isinstance(points, list):
            if len(points) == 0:  # Could be on curves points
                points = []
            # dx/dy/dz, cs
            elif len(points) == 2 and all([any([isinstance(points[0], float),
                                                isinstance(points[0], int)]),
                                           isinstance(points[1], str)]):
                a, cs_name = 0.5 * points[0], points[1]
                points = [[a, a, -a], [-a, a, -a], [-a, -a, -a], [a, -a, -a],
                          [a, a, a], [-a, a, a], [-a, -a, a], [a, -a, a],
                          cs_name]
                points = self.parse_points(points)
            # dx, dy, dz
            elif len(points) == 3 and all([any([isinstance(points[0], float),
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
            elif len(points) == 4 and all([any([isinstance(points[0], float),
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
                cs_name = 'cartesian'
                if isinstance(points[-1], str):
                    points, cs_name = points[:-1], points[-1]
                cs = cs_factory[cs_name]()
                for i, p in enumerate(points):
                    kwargs = {}
                    if isinstance(p, dict):
                        kwargs = p
                        cs_kwargs = p.get('coordinate_system', 'cartesian')
                        if isinstance(cs_kwargs, str):
                            kwargs['coordinate_system'] = cs_factory[cs_kwargs]()
                        elif isinstance(cs_kwargs, dict):
                            cs_name = cs_kwargs.pop('name')
                            kwargs['coordinate_system'] = cs_factory[cs_name](
                                **cs_kwargs)
                    elif isinstance(p, list):
                        if len(p) == cs.dim and not isinstance(p[0], list):
                            kwargs['coordinates'] = p
                            kwargs['coordinate_system'] = cs
                        elif len(p) == cs.dim + 1 and not isinstance(p[0],
                                                                     list):
                            kwargs['coordinates'] = p[:3]
                            kwargs['coordinate_system'] = cs_factory['cartesian']()
                            kwargs['meshSize'] = p[3]
                        else:
                            raise ValueError(p)
                    else:
                        raise ValueError(p)
                    if cs_name == 'cylindrical':
                        kwargs['coordinates'][1] = np.deg2rad(kwargs['coordinates'][1])
                    elif cs_name in ['spherical', 'toroidal', 'tokamak']:
                        kwargs['coordinates'][1] = np.deg2rad(kwargs['coordinates'][1])
                        kwargs['coordinates'][2] = np.deg2rad(kwargs['coordinates'][2])
                    points[i] = Point(**kwargs)
        else:
            raise ValueError(points)
        return points

    def parse_curves(self, curves):
        curves = [{} for _ in range(12)] if curves is None else curves
        for i, c in enumerate(curves):
            kwargs = {}
            if isinstance(c, dict):
                kwargs = c
                kwargs['points'] = self.parse_points(kwargs.get('points', []))
            elif isinstance(c, list):
                if len(c) > 0:
                    if not isinstance(c[0], str):
                        kwargs['name'] = 'polyline'
                        kwargs['points'] = self.parse_points(c)
                    else:
                        if len(c) == 2:
                            kwargs['name'] = c[0]
                            kwargs['points'] = self.parse_points(c[1])
                        elif len(c) == 3:
                            kwargs['name'] = c[0]
                            kwargs['points'] = self.parse_points(c[1])
                            kwargs['kwargs'] = c[2]
                        else:
                            raise ValueError(c)
                else:
                    kwargs['name'] = 'line'
            else:
                raise ValueError(c)
            curves[i] = Curve(**kwargs)
        return curves

    def parse_surfaces(self, surfaces):
        surfaces = [{} for _ in range(6)] if surfaces is None else surfaces
        for i, s in enumerate(surfaces):
            kwargs = {}
            if isinstance(s, dict):
                kwargs = s
            else:
                raise ValueError(s)
            kwargs['name'] = 'fill'  # Must be!
            surfaces[i] = Surface(**kwargs)
        return surfaces

    def parse_volumes(self, volumes):
        volumes = [{}] if volumes is None else volumes
        for i, v in enumerate(volumes):
            kwargs = {}
            if isinstance(v, dict):
                kwargs = v
            else:
                raise ValueError(v)
            volumes[i] = Volume(**kwargs)
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

    def parse_structure_all(self, structure_all):
        if isinstance(structure_all, dict):
            if 'curves' in structure_all:
                value = copy.deepcopy(structure_all['curves'])
                for i, c in enumerate(self.curves):
                    self.curves[i].structure = Structure(**value)
            elif all(['curves_x' in structure_all,
                      'curves_y' in structure_all,
                      'curves_z' in structure_all]):
                for i, c in enumerate(self.curves):
                    direction = self.curves_directions[i]
                    key = f'curves_{direction}'
                    value = copy.deepcopy(structure_all[key])
                    self.curves[i].structure = Structure(**value)
            else:
                raise ValueError(structure_all)
            # Surfaces
            key = 'surfaces'
            value = copy.deepcopy(self.structure_all.get(
                key, {'name': 'surface'}))
            for i, s in enumerate(self.surfaces):
                self.surfaces[i].structure = Structure(**value)
            # Volume
            key = 'volumes'
            value = copy.deepcopy(self.structure_all.get(
                key, {'name': 'volume'}))
            self.volumes[0].structure = Structure(**value)
        elif isinstance(structure_all, list):
            if len(structure_all) == 3:
                # Curves
                d2i = {'curves_x': 0, 'curves_y': 1, 'curves_z': 2}
                for i, c in enumerate(self.curves):
                    direction = self.curves_directions[i]
                    key = f'curves_{direction}'
                    index = d2i[key]
                    values = structure_all[index]
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
        elif structure_all is None:
            pass
        else:
            raise ValueError(structure_all)
        return structure_all

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
                if self.parent is None:
                    raise ValueError(
                        'The parent must exist with Block Coordinate System!')
                p.coordinate_system.ps = [x.coordinates
                                          for x in self.parent.points]
            self.points[i] = reduce_transforms(self.transforms, p)
        # Curve Points
        for i, c in enumerate(self.curves):
            for j, p in enumerate(c.points):
                if isinstance(p.coordinate_system, cs_factory['block']):
                    if self.parent is None:
                        raise ValueError(
                            'The parent must exist with Block Coordinate System!')
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
            self.curves_loops[i].curves = [self.curves[x] for x in
                                           self.surfaces_curves[i]]
            self.curves_loops[i].curves_signs = self.surfaces_curves_signs[i]
            self.curves_loops[i] = register_curve_loop(self.factory,
                                                       self.curves_loops[i],
                                                       self.register_tag)

    def register_surfaces(self):
        for i, s in enumerate(self.surfaces):
            self.surfaces[i].curves_loops = [self.curves_loops[i]]
            self.surfaces[i] = register_surface(self.factory, self.surfaces[i],
                                                self.register_tag)

    def register_surfaces_loops(self):
        # External
        self.surfaces_loops[0].surfaces = self.surfaces
        self.surfaces_loops[0] = register_surface_loop(
            self.factory, self.surfaces_loops[0], self.register_tag)
        # Internal
        if self.boolean_level is None:
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
        if self.quadrate_all is not None:
            if isinstance(self.quadrate_all, bool):
                self.quadrate_all = {}
            elif isinstance(self.quadrate_all, dict):
                pass
            else:
                raise ValueError(self.quadrate_all)
            for i, s in enumerate(self.surfaces):
                self.surfaces[i].quadrate = Quadrate(**self.quadrate_all)
        # Recombine
        for i, s in enumerate(self.surfaces):
            if s.quadrate is not None:
                self.surfaces[i] = register_quadrate_surface(s, self.factory)

    def structure_curves(self):
        # Transfinite
        for i, c in enumerate(self.curves):
            if c.structure is not None:
                self.curves[i] = register_structure_curve(c, self.factory)

    def structure_surfaces(self):
        # Transfinite
        for i, s in enumerate(self.surfaces):
            all_tr_curves = all(self.curves[x].structure is not None for x in
                                self.surfaces_curves[i])
            if all_tr_curves and s.structure is not None:
                s.structure.kwargs['cornerTags'] = [
                    self.points[x]['kwargs']['tag']
                    for x in self.surfaces_points[i]]
                s.structure.kwargs['arrangement'] = 'Right'
                self.surfaces[i] = register_structure_surface(s, self.factory)

    def structure_volume(self):
        # Transfinite
        v = self.volumes[0]
        all_tr_surfaces = all(x.quadrate is not None for x in self.surfaces)
        same_rec_surfaces = len(
            set(x.structure is not None for x in self.surfaces)) == 1
        if v.structure is not None and all_tr_surfaces and same_rec_surfaces:
            v.structure.kwargs['cornerTags'] = [x['kwargs']['tag']
                                                for x in self.points]
            self.volumes[0] = register_structure_volume(v, self.factory)

    def quadrate(self):
        # Children
        for i, c in enumerate(self.children):
            c.quadrate()
        if self.is_quadrated:
            return
        self.recombine_surfaces()
        self.is_quadrated = True

    def structure(self):
        # Children
        for i, c in enumerate(self.children):
            c.structure()
        if self.is_structured:
            return
        # Curves
        self.structure_curves()
        # Surfaces
        self.structure_surfaces()
        # Volume
        self.structure_volume()
        self.is_structured = True

    def get_all_blocks(self):
        """
        Recursively collect blocks through children
        Returns:
            blocks(list of Block): list of blocks
        """
        def get_blocks(block, blocks):
            blocks.append(block)
            for b in block.children:
                get_blocks(b, blocks)

        bs = []
        get_blocks(self, bs)
        return bs
