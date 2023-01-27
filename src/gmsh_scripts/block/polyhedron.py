from collections import deque

from gmsh_scripts.block import Block
from gmsh_scripts.entity import Point
from gmsh_scripts.entity import Curve
from gmsh_scripts.entity import CurveLoop
from gmsh_scripts.entity import Surface
from gmsh_scripts.entity import SurfaceLoop
from gmsh_scripts.entity import Volume
from gmsh_scripts.registry import register_point, register_curve, register_curve_loop, \
    register_surface, register_surface_loop, register_volume, \
    register_curve_structure, register_surface_structure, \
    register_surface_quadrate, register_volume_structure, unregister_volumes, \
    register_volume2block, get_boolean_old2news, get_boolean_new2olds, \
    get_volume2block, pre_unregister_volume


class Polyhedron(Block):
    def __init__(self, points=None, polygons=None,
                 do_register=True, do_register_children=True,
                 do_unregister=False, do_unregister_children=True,
                 do_unregister_boolean=False,
                 transforms=None, self_transforms=None,
                 zone=None,
                 boolean_level=None,
                 path=None,
                 # Children
                 parent=None, children=None, children_transforms=None):
        super().__init__(
            points=points, curves=None, surfaces=None, volume=None,
            do_register=do_register,
            do_register_children=do_register_children,
            do_unregister=do_unregister,
            do_unregister_children=do_unregister_children,
            do_unregister_boolean=do_unregister_boolean,
            transforms=transforms,
            self_transforms=self_transforms,
            do_quadrate=False,
            do_structure=False,
            structure=None,
            structure_type=None,
            zone=zone,
            boolean_level=boolean_level,
            path=path,
            parent=parent,
            children=children,
            children_transforms=children_transforms)
        self.curves_points, self.surfaces_curves, self.surfaces_curves_signs, \
        self.curves, self.curves_loops, self.surfaces, self.surfaces_loops, \
        self.volumes, self.curves_structures, self.surfaces_structures, \
        self.volumes_structures, self.surfaces_quadrates = self.parse_polygons(polygons)

    @staticmethod
    def parse_points(points):
        return Point.parse_points(points, do_deg2rad=True)

    @staticmethod
    def parse_polygons(polygons):
        if polygons is None:
            raise ValueError(polygons)
        curves = {}  # {(start point, end_point): index}
        surfaces_curves, surfaces_curves_signs = [], []
        for g in polygons:  # polygon is a surfaces in terms of gmsh
            loops = g if isinstance(g[0], list) else [g]
            css, sss = [], []
            for loop in loops:
                cs, ss = [], []  # curves, signs
                ps, n = deque(loop), len(loop)  # polygon points and  number of points
                for _ in range(n):  # move around
                    c1, c2 = (ps[0], ps[1]), (ps[1], ps[0])  # forward and reverse
                    if c1 in curves:
                        c, s = curves[c1], 1
                    elif c2 in curves:
                        c, s = curves[c2], -1
                    else:
                        c, s = curves.setdefault(c1, len(curves)), 1
                    cs.append(c)
                    ss.append(s)
                    ps.rotate(-1)
                css.append(cs)
                sss.append(ss)
            surfaces_curves.append(css)
            surfaces_curves_signs.append(sss)
        curves_points = list(curves)
        surfaces_curves = surfaces_curves
        surfaces_curves_signs = surfaces_curves_signs
        curves = [Curve(name='line') for _ in curves_points]
        curves_loops = [[CurveLoop() for _ in loops] for loops in surfaces_curves]
        surfaces = [Surface(name='plane') for _ in surfaces_curves]
        surfaces_loops = [SurfaceLoop()]
        volumes = [Volume()]
        curves_structures = [None for _ in curves]
        surfaces_structures = [None for _ in surfaces]
        volumes_structures = [None for _ in volumes]
        surfaces_quadrates = [None for _ in surfaces]
        return curves_points, surfaces_curves, surfaces_curves_signs, curves, \
               curves_loops, surfaces, surfaces_loops, volumes, \
               curves_structures, surfaces_structures, volumes_structures, \
               surfaces_quadrates

    @staticmethod
    def parse_curves(curves):
        pass

    @staticmethod
    def parse_surfaces(surfaces):
        pass

    @staticmethod
    def parse_volumes(volumes):
        pass

    @staticmethod
    def parse_structure(structure, do_structure):
        return None, None, None

    @staticmethod
    def parse_do_quadrate(do_quadrate):
        pass

    def register_curves_loops(self):
        for i, loops in enumerate(self.surfaces_curves):
            for j, loop in enumerate(loops):
                signs = self.surfaces_curves_signs[i][j]
                self.curves_loops[i][j].curves = [self.curves[x] for x in loop]
                self.curves_loops[i][j].curves_signs = signs
                self.curves_loops[i][j] = register_curve_loop(self.curves_loops[i][j])

    def register_surfaces(self):
        for i, s in enumerate(self.surfaces):
            self.surfaces[i].curves_loops = self.curves_loops[i]
            self.surfaces[i] = register_surface(self.surfaces[i])


str2obj = {
    Polyhedron.__name__: Polyhedron,
    Polyhedron.__name__.lower(): Polyhedron
}
