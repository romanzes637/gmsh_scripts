import logging
from pprint import pprint
import copy
import time
from pathlib import Path

import numpy as np
import gmsh

from support import volumes_surfaces_to_volumes_groups_surfaces
from transform import factory as transform_factory
from transform import BlockToCartesian
from transform import reduce_transforms
from registry import register_point, register_curve, register_curve_loop, \
    register_surface, register_surface_loop, register_volume, \
    register_quadrate_surface, register_structure_curve, \
    register_structure_surface, register_structure_volume, unregister_volume
from coordinate_system import Block as BlockCS
from point import Point
from curve import Curve
from curve_loop import CurveLoop
from surface import Surface
from surface_loop import SurfaceLoop
from volume import Volume
from structure import Structure
from quadrate import Quadrate


class Block:
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
        factory (str): gmsh factory (geo or occ)
        points (list of dict, list of list, list): 8 corner points of the block
        curves (list of dict, list of list, list, list of Curve): 12 edge curves of the block
        surfaces (list of dict, list of list, list, list of Surface): 6 boundary surfaces of the block
        volumes (list of dict, list of list, list, list of Volume): volumes of the block (1 by now, TODO several volumes)
        do_register (bool): register Block in the registry
        use_register_tag (bool): use tag from registry instead tag from gmsh
        do_unregister (bool): unregister Block from the registry
        do_register_children (bool): invoke register for children
        do_unregister_children (bool): invoke unregister for children
        transforms (list of dict, list of list, list of Transform): points and curves points transforms (Translation, Rotation, Coordinate Change, etc)
        quadrate_all (list of dict, bool): transform triangles to quadrangles for surfaces and tetrahedra to hexahedra for volumes
        structure_all (list of dict, list of list, list of Transform): make structured mesh instead of unstructured by some rule
        parent (Block): parent of the Block
        children (list of Block): children of the Block
        children_transforms (list of list of dict, list of list of list, list of list of Transform): transforms for children Blocks
        boolean_level (int): Block boolean level, if the Block level > another Block level, then intersected volume joins to the Block, if levels are equal third Block is created, if None - don't do boolean
    """

    def __init__(self, factory='geo',
                 points=None, curves=None, surfaces=None, volumes=None,
                 do_register=True, use_register_tag=False, do_unregister=False,
                 do_register_children=True, do_unregister_children=True,
                 do_unregister_boolean=False, do_unregister_boolean_children=True,
                 transforms=None,
                 quadrate_all=None, structure_all=None, zone_all=None,
                 parent=None, children=None, children_transforms=None,
                 boolean_level=None, file_name=None):
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
        self.do_unregister_boolean = do_unregister_boolean
        self.do_unregister_boolean_children = do_unregister_boolean_children
        self.transforms = self.parse_transforms(transforms, parent)
        self.quadrate_all = quadrate_all
        self.structure_all = self.parse_structure_all(structure_all)
        self.parse_zone_all(zone_all)
        self.parent = parent
        self.children = [] if children is None else children
        if children_transforms is None:
            children_transforms = [[] for _ in self.children]
        for i, t in enumerate(children_transforms):
            children_transforms[i] = self.parse_transforms(t, parent)
        self.children_transforms = children_transforms
        self.boolean_level = boolean_level
        self.file_name = file_name
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

    @staticmethod
    def parse_points(points):
        if points is None:
            points = [[1, 1, -1], [-1, 1, -1], [-1, -1, -1], [1, -1, -1],
                      [1, 1, 1], [-1, 1, 1], [-1, -1, 1], [1, -1, 1]]
        if isinstance(points, float) or isinstance(points, int):  # lx/ly/lz
            a = 0.5 * points
            points = [[a, a, -a], [-a, a, -a], [-a, -a, -a], [a, -a, -a],
                      [a, a, a], [-a, a, a], [-a, -a, a], [a, -a, a]]
        elif isinstance(points, list):
            if len(points) == 0:
                pass
            # lx/ly/lz, coordinate_system
            elif len(points) == 2 and all([any([isinstance(points[0], float),
                                                isinstance(points[0], int)]),
                                           isinstance(points[1], str)]):
                a, cs_name = 0.5 * points[0], points[1]
                points = [[a, a, -a], [-a, a, -a], [-a, -a, -a], [a, -a, -a],
                          [a, a, a], [-a, a, a], [-a, -a, a], [a, -a, a],
                          cs_name]
            # lx, ly, lz
            elif len(points) == 3 and all([any([isinstance(points[0], float),
                                                isinstance(points[0], int)]),
                                           any([isinstance(points[1], float),
                                                isinstance(points[1], int)]),
                                           any([isinstance(points[2], float),
                                                isinstance(points[2], int)])]):
                a, b, c = 0.5 * points[0], 0.5 * points[1], 0.5 * points[2]
                points = [[a, b, -c], [-a, b, -c], [-a, -b, -c], [a, -b, -c],
                          [a, b, c], [-a, b, c], [-a, -b, c], [a, -b, c]]
            # lx, ly, lz, coordinate_system
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
        else:
            raise ValueError(points)
        return Point.parse_points(points, do_deg2rad=True)

    @staticmethod
    def parse_curves(curves):
        curves = [{} for _ in range(12)] if curves is None else curves
        for i, c in enumerate(curves):
            kwargs = {}
            if isinstance(c, dict):
                kwargs = c
                kwargs['points'] = Point.parse_points(kwargs.get('points', []),
                                                      do_deg2rad=True)
            elif isinstance(c, list):
                if len(c) > 0:
                    if not isinstance(c[0], str):
                        kwargs['name'] = 'polyline'
                        kwargs['points'] = Point.parse_points(c)
                    else:
                        if len(c) == 2:
                            kwargs['name'] = c[0]
                            kwargs['points'] = Point.parse_points(
                                c[1], do_deg2rad=True)
                        elif len(c) == 3:
                            kwargs['name'] = c[0]
                            kwargs['points'] = Point.parse_points(
                                c[1], do_deg2rad=True)
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

    @staticmethod
    def parse_transforms(transforms, parent):
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
            if transform_factory[name] == BlockToCartesian:
                ps = [x.coordinates for x in parent.points]
                kwargs['cs_from'] = BlockCS(ps=ps)
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

    def parse_zone_all(self, zone_all):
        if isinstance(zone_all, str):  # Volumes zone
            for v in self.volumes:
                v.zone = zone_all
        elif isinstance(zone_all, list):
            if isinstance(zone_all[0], str):
                for i, v in enumerate(self.volumes):
                    v.zone = zone_all[i]
            else:
                if len(zone_all) == 1:  # Volumes zones
                    v_zs = zone_all[0]
                    for i, v in enumerate(self.volumes):
                        v.zone = v_zs[i]
                elif len(zone_all) == 2:  # Volumes ans surfaces zones
                    v_zs, s_zs = zone_all[0], zone_all[1]
                    self.parse_zone_all(v_zs)
                    for i, s in enumerate(self.surfaces):
                        s.zone = s_zs[i]
                elif len(zone_all) == 3:  # Volumes ans surfaces zones
                    v_s_zs, c_zs = zone_all[:2], zone_all[2]
                    self.parse_zone_all(v_s_zs)
                    for i, c in enumerate(self.curves):
                        c.zone = c_zs[i]
                elif len(zone_all) == 4:  # Volumes ans surfaces zones
                    v_s_c_zs, p_zs = zone_all[:3], zone_all[3]
                    self.parse_zone_all(v_s_c_zs)
                    for i, p in enumerate(self.points):
                        p.zone = p_zs[i]

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
            if isinstance(p.coordinate_system, BlockCS):
                if self.parent is None:
                    raise ValueError(
                        'The parent must exist with Block Coordinate System!')
                p.coordinate_system.ps = [x.coordinates
                                          for x in self.parent.points]
            self.points[i] = reduce_transforms(self.transforms, p)
        # Curve Points
        for i, c in enumerate(self.curves):
            for j, p in enumerate(c.points):
                if isinstance(p.coordinate_system, BlockCS):
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

    def unregister(self, zone_separator='-'):
        # Children
        if self.do_unregister_children:
            for i, c in enumerate(self.children):
                c.unregister()
        # Self
        if not self.do_unregister:
            return
        if not self.is_registered:
            return
        for i, v in enumerate(self.volumes):
            if v.zone is not None:
                if zone_separator not in v.zone:
                    self.volumes[i] = unregister_volume(self.factory, v,
                                                        self.register_tag)

    def unregister_boolean(self, zone_separator='-'):
        # Children
        if self.do_unregister_boolean_children:
            for i, c in enumerate(self.children):
                c.unregister_boolean()
        # Self
        if not self.do_unregister_boolean:
            return
        if self.boolean_level is None:
            return
        for i, v in enumerate(self.volumes):
            if zone_separator in v.zone:
                self.volumes[i] = unregister_volume(self.factory, v,
                                                    self.register_tag)

    def quadrate_surfaces(self):
        if self.quadrate_all is None:
            return
        # Check all
        if isinstance(self.quadrate_all, bool):
            self.quadrate_all = {}
        elif isinstance(self.quadrate_all, dict):
            pass
        else:
            raise ValueError(self.quadrate_all)
        for i, s in enumerate(self.surfaces):
            self.surfaces[i].quadrate = Quadrate(**self.quadrate_all)
        # Quadrate
        if self.boolean_level is not None:
            for v in self.volumes:
                if v.tag is None:
                    continue
                for s_dt in gmsh.model.getBoundary(dimTags=[(3, v.tag)],
                                                   combined=False,
                                                   oriented=True,
                                                   recursive=False):
                    s = Surface(tag=s_dt[1],
                                quadrate=Quadrate(**self.quadrate_all))
                    register_quadrate_surface(s, self.factory)
        else:
            for i, s in enumerate(self.surfaces):
                if s.quadrate is not None:
                    self.surfaces[i] = register_quadrate_surface(s, self.factory)

    def structure_curves(self):
        # Structure
        for i, c in enumerate(self.curves):
            if c.structure is not None:
                self.curves[i] = register_structure_curve(c, self.factory)

    def structure_surfaces(self):
        # Structure
        for i, s in enumerate(self.surfaces):
            all_tr_curves = all(self.curves[x].structure is not None for x in
                                self.surfaces_curves[i])
            if all_tr_curves and s.structure is not None:
                s.structure.kwargs['cornerTags'] = [
                    self.points[x].tag for x in self.surfaces_points[i]]
                s.structure.kwargs['arrangement'] = 'Right'
                self.surfaces[i] = register_structure_surface(s, self.factory)

    def structure_volume(self):
        # Structure
        v = self.volumes[0]
        all_tr_surfaces = all(x.quadrate is not None for x in self.surfaces)
        same_rec_surfaces = len(
            set(x.structure is not None for x in self.surfaces)) == 1
        if v.structure is not None and all_tr_surfaces and same_rec_surfaces:
            v.structure.kwargs['cornerTags'] = [x.tag for x in self.points]
            self.volumes[0] = register_structure_volume(v, self.factory)

    def quadrate(self):
        # Children
        for i, c in enumerate(self.children):
            c.quadrate()
        if self.is_quadrated or self.quadrate_all is None:
            return
        self.quadrate_surfaces()
        self.is_quadrated = True

    def structure(self):
        # Children
        for i, c in enumerate(self.children):
            c.structure()
        if self.boolean_level is not None:  # TODO structure after boolean
            return
        if self.is_structured:
            return
        # Curves
        self.structure_curves()
        # Surfaces
        self.structure_surfaces()
        # Volume
        self.structure_volume()
        self.is_structured = True

    def __iter__(self):
        """Iterate children of the block recursively

        Examples:
            Tree

            0
                00
                    001

                    002
                01
                    011

                    012

            Iterator

            0, 00, 001, 002, 01, 011, 012

        Returns:
            generator of Block: blocks
        """
        yield self
        for child in self.children:
            yield from iter(child)

    def make_tree(self):
        """Tree of blocks

        Returns:
            dict: children of blocks
        """
        tree = {}
        for b in self:  # See __iter__
            tree.setdefault(b.parent, []).append(b)
        return tree

    def plot_tree(self, file_name=None, height='600px', width='600px',
                  hierarchical=True, show_buttons=True, label_type='file_name',
                  group_type='file_name', title_type='file_name',
                  bgcolor='black', font_color='white'):
        def get_value(b, t):
            if t == 'block':
                v = f'type: {type(b).__name__} <br> '
                v += f'id: {id(b)} <br> '
                v += f'parent_id: {id(b.parent) if b.parent is not None else None} <br> '
                zs = ", ".join({x.zone for x in b.volumes if x.zone is not None and x.tag is not None})
                v += f'volume zones: {zs} <br> '
                v += ' <br> '.join(f'{x}: {b.__getattribute__(x)}' for x in (
                    'file_name', 'factory', 'boolean_level', 'register_tag',
                    'do_register', 'do_register_children', 'do_unregister',
                    'do_unregister_boolean', 'do_unregister_boolean_children',
                    'is_registered', 'is_quadrated', 'is_structured'))
            elif t == 'file_name':
                v = b.file_name
            elif t == 'boolean_level':
                v = str(b.boolean_level)
            elif t == 'volume_zone':
                v = ", ".join({x.zone for x in b.volumes if x.zone is not None and x.tag is not None})
            elif t == 'id':
                v = id(b)
            elif t == 'type':
                v = type(b).__name__
            else:
                v = None
            return v

        if file_name is None:
            if self.file_name is not None:
                file_name = f"{Path(self.file_name).with_suffix('').name}-tree"
            else:
                file_name = f'{id(self)}-tree'
        logging.info(f'Tree of {id(self)} with label by {label_type} '
                     f'title by {title_type} '
                     f'and group by {group_type}')
        prev_parent = None
        parent2depth = {prev_parent: 0}
        depth2nodes = {}
        parent2children = {}
        cnt = 0  # nodes counter
        for b in self:  # See __iter__
            cnt += 1
            parent = b.parent
            if parent not in parent2depth:
                parent2depth[parent] = parent2depth[prev_parent] + 1
            prev_parent = parent
            depth = parent2depth[parent]
            depth2nodes.setdefault(depth, []).append(b)
            parent2children.setdefault(parent, []).append(b)
            label = get_value(self, label_type)
            label = label if label is not None else ''
            logging.info(f'{"_" * depth}{id(b)} {label}')
        d2n = ", ".join(f"{k}-{len(v)}" for k, v in depth2nodes.items())
        logging.info(f'Number of nodes: {cnt}')
        logging.info(f'Nodes by depth: {d2n}')
        logging.info(f'Max depth: {max(depth2nodes)}')
        try:
            logging.info(f'pyvis network')
            from pyvis.network import Network

            n = Network(height=height, width=width, directed=True,
                        layout=hierarchical, bgcolor=bgcolor,
                        font_color=font_color)
            if show_buttons:
                n.show_buttons()
            nodes, edges, groups = set(), set(), {}
            for p, cs in parent2children.items():
                if p is None:  # Skip root
                    continue
                if p not in nodes:
                    g = get_value(p, group_type)
                    groups.setdefault(g, len(groups))
                    label = get_value(p, label_type)
                    label = label if label is not None else ' '
                    n.add_node(id(p), label=label, group=groups[g],
                               value=len(p.children), level=parent2depth[p.parent],
                               title=get_value(p, title_type))
                    nodes.add(p)
                for c in cs:
                    if c not in nodes:
                        g = get_value(c, group_type)
                        groups.setdefault(g, len(groups))
                        label = get_value(c, label_type)
                        label = label if label is not None else ' '
                        n.add_node(id(c), label=label, group=groups[g],
                                   value=len(c.children), level=parent2depth[c.parent],
                                   title=get_value(c, title_type))
                        nodes.add(c)
                    if (p, c) not in edges:
                        n.add_edge(id(p), id(c))
                        edges.add((p, c))
            p = Path(file_name).with_suffix('.html')
            logging.info(f'Writing pyvis network to {p}')
            n.write_html(str(p))
        except Exception as e:
            logging.warning(e)
