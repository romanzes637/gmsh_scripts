import argparse
import json
import socket
from pprint import pprint

import gmsh
import sys

import os

from occ_workarounds import correct_and_transfinite_primitive


class Primitive:
    def __init__(self, factory, point_data, transform_data=None, curve_types=None, curve_data=None,
                 transfinite_data=None, transfinite_type=None, physical_name=None):
        """
        Base object with six quadrangular surfaces and eight points
        The object (e.g. number of its volumes/surfaces) could be changed in process,
        if not it may be meshed to structured mesh
        Object structure:
        Axes:
        Y
        Z X
        Points:
        Top Z:
        P5 P4
        P6 P7
        Bottom Z:
        P1 P0
        P2 P3
        Curves:
        L0: P1 -> P0  L1: P5 -> P4  L2: P6  -> P7   L3: P2 -> P3 (X direction curves from P0 by right-hand rule)
        L4: P3 -> P0  L5: P2 -> P1  L6: P6  -> P5   L7: P7 -> P4 (Y direction curves from P0 by right-hand rule)
        L8: P0 -> P4  L9: P1 -> P5  L10: P2 -> P6  L11: P3 -> P7 (Z direction curves from P0 by right-hand rule)
        Surfaces:
        S0: L5  -> L9  -> -L6 -> -L10 (NX surface)
        S1: -L4 -> L11 -> L7  -> -L8  (X surface)
        S2: -L3 -> L10 -> L2  -> -L11 (NY surface)
        S3: L0  -> L8  -> -L1 -> -L9  (Y surface)
        S4: -L0 -> -L5 ->  L3 -> L4   (NZ surface)
        S5: L1  -> -L7 -> -L2 -> L6   (Z surface)
        :param str factory: gmsh factory (currently: 'geo' or 'occ')
        :param list of list of float point_data:
        [[point1_x, point1_y, point1_z, point1_lc], ..., [point8_x, point8_y, point8_z, point8_lc]] or
        [[point1_x, point1_y, point1_z], ..., [point8_x, point8_y, point8_z]] or
        [length_x, length_y, length_z, lc] or
        [length_x, length_y, length_z]
        :param list of float transform_data:
        [displacement x, y, z] or
        [displacement x, y, z, rotation origin x, y, z, rotation angle x, y, z] or
        [displacement x, y, z, rotation vector x, y, z, rotation angle] or
        [displacement x, y, z, rotation angle x, y, z]
        :param list of int curve_types: [line1_type, line2_type, ..., line12_type],
        types: 0 - line, 1 - circle, 2 - ellipse (FIXME not implemented for occ factory),
        3 - spline, 4 - bspline (number of curve points > 1), 5 - bezier curve
        :param list of list of list of float curve_data:
        [[[line1_point1_x, line1_point1_y, line1_point1_z, line1_point1_lc], ...], ..., [[line_12..., ...], ...]]] or
        [[[line1_point1_x, line1_point1_y, line1_point1_z], ...], ..., [[line_12_point_1, ...], ...]]]
        :param list of list of float transfinite_data:
        [[line1 number of nodes, type, coefficient], ..., [line12 ...]] or
        [[x_lines number of nodes, type, coefficient], [y_lines ...], [z_lines ...]]
        types: 0 - progression, 1 - bump
        :param int transfinite_type: 0, 1, 2 or 4 determines orientation of surfaces' tetrahedra at structured volume
        :param str physical_name: primitive's volumes physical name
        """
        if factory == 'occ':
            self.factory = gmsh.model.occ
        else:
            self.factory = gmsh.model.geo
        if len(point_data) == 3:
            half_lx = point_data[0] / 2.0
            half_ly = point_data[1] / 2.0
            half_lz = point_data[2] / 2.0
            new_point_data = [
                [half_lx, half_ly, -half_lz],
                [-half_lx, half_ly, -half_lz],
                [-half_lx, -half_ly, -half_lz],
                [half_lx, -half_ly, -half_lz],
                [half_lx, half_ly, half_lz],
                [-half_lx, half_ly, half_lz],
                [-half_lx, -half_ly, half_lz],
                [half_lx, -half_ly, half_lz]
            ]
        elif len(point_data) == 4:
            half_lx = point_data[0] / 2.0
            half_ly = point_data[1] / 2.0
            half_lz = point_data[2] / 2.0
            lc = point_data[3]
            new_point_data = [
                [half_lx, half_ly, -half_lz, lc],
                [-half_lx, half_ly, -half_lz, lc],
                [-half_lx, -half_ly, -half_lz, lc],
                [half_lx, -half_ly, -half_lz, lc],
                [half_lx, half_ly, half_lz, lc],
                [-half_lx, half_ly, half_lz, lc],
                [-half_lx, -half_ly, half_lz, lc],
                [half_lx, -half_ly, half_lz, lc]
            ]
        else:
            new_point_data = point_data
        if curve_types is None:
            curve_types = [0] * 12
        if curve_data is None:
            curve_data = [[]] * 12
        if transfinite_data is not None:
            if len(transfinite_data) == 3:
                self.transfinite_data = list()
                self.transfinite_data.extend([transfinite_data[0]] * 4)
                self.transfinite_data.extend([transfinite_data[1]] * 4)
                self.transfinite_data.extend([transfinite_data[2]] * 4)
            else:
                self.transfinite_data = transfinite_data
        else:
            self.transfinite_data = transfinite_data
        if transfinite_type is None:
            self.transfinite_type = 0
        else:
            self.transfinite_type = transfinite_type
        if physical_name is None:
            self.physical_name = Primitive.__name__
        else:
            self.physical_name = physical_name
        self.points = []
        self.curves_points = []
        self.curves = []
        self.surfaces = []
        self.volumes = []
        # Points
        for i in range(len(new_point_data)):
            tag = self.factory.addPoint(*new_point_data[i])
            self.points.append(tag)
        for i in range(len(curve_data)):
            ps = []
            for j in range(len(curve_data[i])):
                tag = self.factory.addPoint(*curve_data[i][j])
                ps.append(tag)
            self.curves_points.append(ps)
        # Transform
        if transform_data is not None:
            dim_tags = map(lambda x: (0, x), self.points)
            for curve_points in self.curves_points:
                dim_tags += map(lambda x: (0, x), curve_points)
            self.factory.translate(dim_tags, transform_data[0], transform_data[1], transform_data[2])
            if len(transform_data) == 6:
                self.factory.rotate(dim_tags,
                                    transform_data[0], transform_data[1], transform_data[2],
                                    1, 0, 0, transform_data[3])
                self.factory.rotate(dim_tags,
                                    transform_data[0], transform_data[1], transform_data[2],
                                    0, 1, 0, transform_data[4])
                self.factory.rotate(dim_tags,
                                    transform_data[0], transform_data[1], transform_data[2],
                                    0, 0, 1, transform_data[5])
            elif len(transform_data) == 7:
                self.factory.rotate(dim_tags,
                                    transform_data[0], transform_data[1], transform_data[2],
                                    transform_data[3], transform_data[4], transform_data[5],
                                    transform_data[6])
            elif len(transform_data) == 9:
                self.factory.rotate(dim_tags,
                                    transform_data[3], transform_data[4], transform_data[5],
                                    1, 0, 0, transform_data[6])
                self.factory.rotate(dim_tags,
                                    transform_data[3], transform_data[4], transform_data[5],
                                    0, 1, 0, transform_data[7])
                self.factory.rotate(dim_tags,
                                    transform_data[3], transform_data[4], transform_data[5],
                                    0, 0, 1, transform_data[8])
        # Curves
        for i in range(12):
            tag = self.add_curve[curve_types[i]](self, i)
            self.curves.append(tag)
        # Surfaces
        for i in range(6):
            if self.factory == gmsh.model.geo:
                tag = self.factory.addCurveLoop(
                    map(lambda x, y: y * self.curves[x],
                        self.surfaces_local_curves[i],
                        self.surfaces_local_curves_signs[i]))
                tag = self.factory.addSurfaceFilling([tag])
            else:
                tag = self.factory.addCurveLoop(
                    map(lambda x: self.curves[x],
                        self.surfaces_local_curves[i]))
                tag = self.factory.addSurfaceFilling(tag)
            self.surfaces.append(tag)
        # Volume
        tag = self.factory.addSurfaceLoop(self.surfaces)  # FIXME always return -1
        tag = self.factory.addVolume([tag])
        self.volumes.append(tag)
        self.points_coordinates = []
        self.curves_points_coordinates = []
        self.bounding_box = None  # [x_min, y_min, z_min, x_max, y_max, z_max] Call self.evaluate_bounding_box() to init

    def recombine(self):
        volumes_dim_tags = map(lambda x: (3, x), self.volumes)
        surfaces_dim_tags = gmsh.model.getBoundary(volumes_dim_tags, combined=False)
        for dt in surfaces_dim_tags:
            if self.factory == gmsh.model.occ:
                gmsh.model.mesh.setRecombine(dt[0], dt[1])
            else:
                self.factory.mesh.setRecombine(dt[0], dt[1])

    def smooth(self, dim, n):
        """
        Smooth mesh. Currently works only with dim == 2
        :param dim: Dimension
        :param n: Number of smooth iterations
        """
        if dim == 1:
            volumes_dim_tags = map(lambda x: (3, x), self.volumes)
            surfaces_dim_tags = gmsh.model.getBoundary(volumes_dim_tags, combined=False)
            curves_dim_tags = gmsh.model.getBoundary(surfaces_dim_tags, combined=False)
            for dt in curves_dim_tags:
                gmsh.model.mesh.setSmoothing(dim, dt[1], n)
        elif dim == 2:
            volumes_dim_tags = map(lambda x: (3, x), self.volumes)
            surfaces_dim_tags = gmsh.model.getBoundary(volumes_dim_tags, combined=False)
            for dt in surfaces_dim_tags:
                gmsh.model.mesh.setSmoothing(dim, dt[1], n)
        elif dim == 3:
            for v in self.volumes:
                gmsh.model.mesh.setSmoothing(dim, v, n)

    def transfinite(self, transfinited_surfaces, transfinited_curves):
        """
        Transfinite primitive
        :param transfinited_surfaces: set() of already transfinite surfaces (workaround for double transfinite issue)
        :param transfinited_curves: set() of already transfinite curves (workaround for double transfinite issue)
        """
        result = False
        # Check
        check = False
        if len(self.volumes) == 1:  # First
            volumes_dim_tags = map(lambda x: (3, x), self.volumes)
            surfaces_dim_tags = gmsh.model.getBoundary(volumes_dim_tags, combined=False)
            if len(surfaces_dim_tags) == 6:  # Second
                points_dim_tags = gmsh.model.getBoundary(volumes_dim_tags, combined=False, recursive=True)
                if len(points_dim_tags) == 8:  # Third
                    surfaces_points = []
                    for dim_tag in surfaces_dim_tags:
                        points_dim_tags = gmsh.model.getBoundary(
                            (dim_tag[0], dim_tag[1]), combined=False, recursive=True)
                        surfaces_points.append(map(lambda x: x[1], points_dim_tags))
                    is_4_points = True
                    for surface_points in surfaces_points:
                        if len(surface_points) != 4:  # Fourth
                            is_4_points = False
                            break
                    if is_4_points:
                        check = True
        # Transfinite
        if check:
            if self.transfinite_type == 0:
                transfinite_surface_data = [1, 1, 1, 1, 1, 1]
                transfinite_volume_data = [0]
            elif self.transfinite_type == 1:
                transfinite_surface_data = [1, 1, 0, 0, 0, 0]
                transfinite_volume_data = [1]
            elif self.transfinite_type == 2:
                transfinite_surface_data = [0, 0, 0, 0, 1, 1]
                transfinite_volume_data = [2]
            elif self.transfinite_type == 3:
                transfinite_surface_data = [0, 0, 1, 1, 0, 0]
                transfinite_volume_data = [3]
            else:
                transfinite_surface_data = None
                transfinite_volume_data = None
            if self.transfinite_data is not None:
                for i, c in enumerate(self.curves):
                    if c not in transfinited_curves:
                        if self.factory != gmsh.model.geo:  # FIXME Workaround for GEO factory
                            transfinite_type = self.transfinite_data[i][1]
                        else:
                            transfinite_type = self.transfinite_data[i][1] + 2
                        self.transfinite_curve[transfinite_type](self, i)
                        transfinited_curves.add(c)
                if transfinite_surface_data is not None:
                    for i, s in enumerate(self.surfaces):
                        if s not in transfinited_surfaces:
                            if self.factory != gmsh.model.geo:  # FIXME Workaround for GEO factory
                                transfinite_type = transfinite_surface_data[i]
                            else:
                                transfinite_type = transfinite_surface_data[i] + 4
                            self.transfinite_surface[transfinite_type](self, i)
                            transfinited_surfaces.add(s)
                    if transfinite_volume_data is not None:
                        for i in range(len(self.volumes)):
                            if self.factory != gmsh.model.geo:  # FIXME Workaround for GEO factory
                                transfinite_type = transfinite_volume_data[i]
                            else:
                                transfinite_type = transfinite_volume_data[i] + 4
                            self.transfinite_volume[transfinite_type](self, i)
                result = True
        return result

    def evaluate_coordinates(self):
        for point in self.points:
            bb = gmsh.model.getBoundingBox(0, point)
            self.points_coordinates.append([bb[0], bb[1], bb[2]])
        for curve_points in self.curves_points:
            cs = []
            for point in curve_points:
                bb = gmsh.model.getBoundingBox(0, point)
                cs.append([bb[0], bb[1], bb[2]])
            self.curves_points_coordinates.append(cs)

    def evaluate_bounding_box(self):
        if len(self.volumes) > 0:
            x_mins = []
            y_mins = []
            z_mins = []
            x_maxs = []
            y_maxs = []
            z_maxs = []
            volumes_dim_tags = map(lambda x: [3, x], self.volumes)
            for dim_tag in volumes_dim_tags:
                x_min, y_min, z_min, x_max, y_max, z_max = gmsh.model.getBoundingBox(dim_tag[0], dim_tag[1])
                x_mins.append(x_min)
                y_mins.append(y_min)
                z_mins.append(z_min)
                x_maxs.append(x_max)
                y_maxs.append(y_max)
                z_maxs.append(z_max)
            self.bounding_box = [min(x_mins), min(y_mins), min(z_mins), max(x_maxs), max(y_maxs), max(z_maxs)]
        else:
            self.bounding_box = [0, 0, 0, 0, 0, 0]

    def set_size(self, size):
        for v in self.volumes:
            volume_dim_tag = [3, v]
            points_dim_tags = gmsh.model.getBoundary([volume_dim_tag], combined=False, recursive=True)
            gmsh.model.mesh.setSize(points_dim_tags, size)

    def get_surfaces(self, combined=True):
        volumes_dim_tags = map(lambda x: [3, x], self.volumes)
        surfaces_dim_tags = gmsh.model.getBoundary(volumes_dim_tags, combined=combined)
        surfaces = map(lambda x: x[1], surfaces_dim_tags)
        return surfaces

    surfaces_names = {
        0: "NX",
        1: "X",
        2: "NY",
        3: "Y",
        4: "NZ",
        5: "Z"
    }

    curves_local_points = [
        [1, 0], [5, 4], [6, 7], [2, 3],
        [3, 0], [2, 1], [6, 5], [7, 4],
        [0, 4], [1, 5], [2, 6], [3, 7]
    ]

    surfaces_local_points = [
        [2, 6, 5, 1],  # NX
        [3, 7, 4, 0],  # X
        [2, 6, 7, 3],  # NY
        [1, 5, 4, 0],  # Y
        [3, 2, 1, 0],  # NZ
        [7, 6, 5, 4],  # Z
    ]

    surfaces_local_curves = [
        [5, 9, 6, 10],
        [4, 11, 7, 8],
        [3, 10, 2, 11],
        [0, 8, 1, 9],
        [0, 5, 3, 4],
        [1, 7, 2, 6]
    ]

    surfaces_local_curves_signs = [
        [1, 1, -1, -1],
        [-1, 1, 1, -1],
        [-1, 1, 1, -1],
        [1, 1, -1, -1],
        [-1, -1, 1, 1],
        [1, -1, -1, 1]
    ]

    transfinite_curve = {
        0: lambda self, i: gmsh.model.mesh.setTransfiniteCurve(
            self.curves[i],
            self.transfinite_data[i][0],
            "Progression",
            self.transfinite_data[i][2]
        ),
        1: lambda self, i: gmsh.model.mesh.setTransfiniteCurve(
            self.curves[i],
            self.transfinite_data[i][0],
            "Bump",
            self.transfinite_data[i][2]
        ),
        2: lambda self, i: gmsh.model.geo.mesh.setTransfiniteCurve(
            self.curves[i],
            self.transfinite_data[i][0],
            "Progression",
            self.transfinite_data[i][2]
        ),
        3: lambda self, i: gmsh.model.geo.mesh.setTransfiniteCurve(
            self.curves[i],
            self.transfinite_data[i][0],
            "Bump",
            self.transfinite_data[i][2]
        )
    }

    transfinite_surface = {
        0: lambda self, i: gmsh.model.mesh.setTransfiniteSurface(
            self.surfaces[i],
            "Left",
            [self.points[x] for x in self.surfaces_local_points[i]]
        ),
        1: lambda self, i: gmsh.model.mesh.setTransfiniteSurface(
            self.surfaces[i],
            "Right",
            [self.points[x] for x in self.surfaces_local_points[i]]
        ),
        2: lambda self, i: gmsh.model.mesh.setTransfiniteSurface(
            self.surfaces[i],
            "AlternateLeft",
            [self.points[x] for x in self.surfaces_local_points[i]]
        ),
        3: lambda self, i: gmsh.model.mesh.setTransfiniteSurface(
            self.surfaces[i],
            "AlternateRight",
            [self.points[x] for x in self.surfaces_local_points[i]]
        ),
        4: lambda self, i: gmsh.model.geo.mesh.setTransfiniteSurface(
            self.surfaces[i],
            "Left",
            [self.points[x] for x in self.surfaces_local_points[i]]
        ),
        5: lambda self, i: gmsh.model.geo.mesh.setTransfiniteSurface(
            self.surfaces[i],
            "Right",
            [self.points[x] for x in self.surfaces_local_points[i]]
        ),
        6: lambda self, i: gmsh.model.geo.mesh.setTransfiniteSurface(
            self.surfaces[i],
            "AlternateLeft",
            [self.points[x] for x in self.surfaces_local_points[i]]
        ),
        7: lambda self, i: gmsh.model.geo.mesh.setTransfiniteSurface(
            self.surfaces[i],
            "AlternateRight",
            [self.points[x] for x in self.surfaces_local_points[i]]
        )
    }

    transfinite_volume = {
        0: lambda self, i: gmsh.model.mesh.setTransfiniteVolume(
            self.volumes[i],
            [
                self.points[0], self.points[1], self.points[2], self.points[3],
                self.points[4], self.points[5], self.points[6], self.points[7]
            ]
        ),
        1: lambda self, i: gmsh.model.mesh.setTransfiniteVolume(
            self.volumes[i],
            [
                self.points[1], self.points[2], self.points[3], self.points[0],
                self.points[5], self.points[6], self.points[7], self.points[4]
            ]
        ),
        2: lambda self, i: gmsh.model.mesh.setTransfiniteVolume(
            self.volumes[i],
            [
                self.points[2], self.points[3], self.points[0], self.points[1],
                self.points[6], self.points[7], self.points[4], self.points[5]
            ]
        ),
        3: lambda self, i: gmsh.model.mesh.setTransfiniteVolume(
            self.volumes[i],
            [
                self.points[3], self.points[0], self.points[1], self.points[2],
                self.points[7], self.points[4], self.points[5], self.points[6]
            ]
        ),
        4: lambda self, i: gmsh.model.geo.mesh.setTransfiniteVolume(
            self.volumes[i],
            [
                self.points[0], self.points[1], self.points[2], self.points[3],
                self.points[4], self.points[5], self.points[6], self.points[7]
            ]
        ),
        5: lambda self, i: gmsh.model.geo.mesh.setTransfiniteVolume(
            self.volumes[i],
            [
                self.points[1], self.points[2], self.points[3], self.points[0],
                self.points[5], self.points[6], self.points[7], self.points[4]
            ]
        ),
        6: lambda self, i: gmsh.model.geo.mesh.setTransfiniteVolume(
            self.volumes[i],
            [
                self.points[2], self.points[3], self.points[0], self.points[1],
                self.points[6], self.points[7], self.points[4], self.points[5]
            ]
        ),
        7: lambda self, i: gmsh.model.geo.mesh.setTransfiniteVolume(
            self.volumes[i],
            [
                self.points[3], self.points[0], self.points[1], self.points[2],
                self.points[7], self.points[4], self.points[5], self.points[6]
            ]
        )
    }

    add_curve = {
        0: lambda self, i: self.factory.addLine(
            self.points[self.curves_local_points[i][0]],
            self.points[self.curves_local_points[i][1]]
        ),
        1: lambda self, i: self.factory.addCircleArc(
            self.points[self.curves_local_points[i][0]],
            self.curves_points[i][0],
            self.points[self.curves_local_points[i][1]]
        ),
        2: lambda self, i: self.factory.addEllipseArc(
            self.points[self.curves_local_points[i][0]],
            self.curves_points[i][0],
            self.curves_points[i][1],
            self.points[self.curves_local_points[i][1]],
        ),  # FIXME implement occ ellipse
        3: lambda self, i: self.factory.addSpline(
            [self.points[self.curves_local_points[i][0]]] +
            self.curves_points[i] +
            [self.points[self.curves_local_points[i][1]]]
        ),
        4: lambda self, i: self.factory.addBSpline(
            [self.points[self.curves_local_points[i][0]]] +
            self.curves_points[i] +
            [self.points[self.curves_local_points[i][1]]]
        ),
        5: lambda self, i: self.factory.addBezier(
            [self.points[self.curves_local_points[i][0]]] +
            self.curves_points[i] +
            [self.points[self.curves_local_points[i][1]]]
        )
    }


if __name__ == '__main__':
    print('Python: {0}'.format(sys.executable))
    print('Script: {0}'.format(__file__))
    print('Working Directory: {0}'.format(os.getcwd()))
    print('Host: {}'.format(socket.gethostname()))
    print('PID: {}'.format(os.getpid()))
    print('Arguments')
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--input', help='input filename', default='input_primitive.json')
    parser.add_argument('-o', '--output', help='output filename')
    parser.add_argument('-v', '--verbose', help='verbose', action='store_true')
    parser.add_argument('-t', '--test', help='test mode', action='store_true')
    args = parser.parse_args()
    basename, extension = os.path.splitext(args.input)
    if args.output is None:
        args.output = basename
    print(args)
    is_test = args.test
    is_verbose = args.verbose
    output_path = args.output
    input_path = args.input
    model_name = basename
    gmsh.initialize()
    if is_verbose:
        gmsh.option.setNumber("General.Terminal", 1)
    else:
        gmsh.option.setNumber("General.Terminal", 0)
    gmsh.option.setNumber('Geometry.AutoCoherence', 0)  # No effect at gmsh.model.occ factory
    gmsh.model.add(model_name)
    print('Input')
    with open(input_path) as f:
        d = json.load(f)
    pprint(d)
    print('Initialize')
    primitive = Primitive(**d['arguments'])
    factory = primitive.factory
    print('Synchronize')
    factory.synchronize()
    if not is_test:
        print('Evaluate')
        primitive.evaluate_coordinates()  # for correct and transfinite
        primitive.evaluate_bounding_box()  # for boolean
        print('Remove Duplicates')
        factory.removeAllDuplicates()
        print('Synchronize')
        factory.synchronize()
        print("Correct and Transfinite")
        ss = set()
        cs = set()
        correct_and_transfinite_primitive(primitive, ss, cs)
        print("Physical")
        vs = primitive.volumes
        tag = gmsh.model.addPhysicalGroup(3, vs)
        gmsh.model.setPhysicalName(3, tag, primitive.physical_name)
        for i, s in enumerate(primitive.surfaces):
            tag = gmsh.model.addPhysicalGroup(2, [s])
            gmsh.model.setPhysicalName(2, tag, primitive.surfaces_names[i])
        print("Mesh")
        gmsh.model.mesh.generate(3)
        gmsh.model.mesh.removeDuplicateNodes()
        print("Write")
        gmsh.write(output_path + '.msh')
    else:
        print("Write")
        gmsh.write(output_path + '.brep')
    gmsh.finalize()
