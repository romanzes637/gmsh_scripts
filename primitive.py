import gmsh
import itertools
import time

import math


class Primitive:
    def __init__(self, factory, point_data, transform_data, curve_types=None, curve_data=None,
                 transfinite_curve_data=None, transfinite_type=None):
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
        :param factory: gmsh factory (currently: gmsh.model.geo or gmsh.model.occ)
        :param point_data: [[point1_x, point1_y, point1_z, point1_lc], ..., [point8_x, point8_y, point8_z, point8_lc]]
        :param transform_data: [displacement x, y, z] or
        [displacement x, y, z, rotation origin x, y, z, rotation angle x, y, z] or
        [displacement x, y, z, rotation vector x, y, z, rotation angle]
        :param curve_types: [line1_type, line2_type, ..., line12_type],
        types: 0 - line, 1 - circle, 2 - ellipse (FIXME not implemented for occ factory),
        3 - spline, 4 - bspline (number of curve points > 1), 5 - bezier curve
        :param curve_data: [[line1_point1_x, line1_point1_y, line1_point1_z], ...], ...]
        :param transfinite_curve_data: [[line1 number of nodes, type, coefficient], ..., [line12 ...]]
        types: 0 - progression, 1 - bump
        :param transfinite_type: 0, 1, 2 or 4 determines orientation of tetrahedra at structured volume and its surfaces
        """
        if curve_types is None:
            curve_types = [0] * 12
        if curve_data is None:
            curve_data = [[]] * 12
        self.factory = factory
        self.transfinite_curve_data = transfinite_curve_data
        self.transfinite_type = transfinite_type
        self.points = []
        self.curves_points = []
        self.curves = []
        self.surfaces = []
        self.volumes = []
        self.points_coordinates = []
        for i in range(len(point_data)):
            tag = self.factory.addPoint(
                point_data[i][0],
                point_data[i][1],
                point_data[i][2],
                point_data[i][3]
            )
            self.points.append(tag)
        for i in range(len(curve_data)):
            ps = []
            for j in range(len(curve_data[i])):
                tag = self.factory.addPoint(
                    curve_data[i][j][0],
                    curve_data[i][j][1],
                    curve_data[i][j][2],
                    curve_data[i][j][3]
                )
                ps.append(tag)
            self.curves_points.append(ps)
        # Transform
        dim_tags = map(lambda x: (0, x), self.points)
        for curve_points in self.curves_points:
            dim_tags += map(lambda x: (0, x), curve_points)
        self.factory.translate(dim_tags, transform_data[0], transform_data[1], transform_data[2])
        if len(transform_data) == 7:
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
        for i in range(12):
            tag = self.add_curve[curve_types[i]](self, i)
            self.curves.append(tag)
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
        tag = self.factory.addSurfaceLoop(self.surfaces)
        tag = self.factory.addVolume([tag])
        self.volumes.append(tag)
        self.factory.synchronize()
        for point in self.points:
            bb = gmsh.model.getBoundingBox(0, point)
            self.points_coordinates.append([bb[0], bb[1], bb[2]])
        self.bounding_box = []  # [x_min, y_min, z_min, x_max, y_max, z_max] Call self.evaluate_bounding_box() to init
        self.evaluate_bounding_box()

    def recombine(self):
        for i in range(len(self.surfaces)):
            gmsh.model.mesh.setRecombine(2, self.surfaces[i])

    def smooth(self, n):
        for i in range(len(self.surfaces)):
            gmsh.model.mesh.setSmoothing(2, self.surfaces[i], n)

    def transfinite(self, transfinite_surfaces):
        """
        Transfinite primitive
        :param transfinite_surfaces: set() of already transfinite surfaces (workaround for double transfinite issue)
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
                    is_4 = True
                    for surface_points in surfaces_points:
                        if len(surface_points) != 4:  # Fourth
                            is_4 = False
                            break
                    if is_4:
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
            if self.transfinite_curve_data is not None:
                for i in range(len(self.curves)):
                    self.transfinite_curve[self.transfinite_curve_data[i][1]](self, i)
                if transfinite_surface_data is not None:
                    for i in range(len(self.surfaces)):
                        if self.surfaces[i] not in transfinite_surfaces:
                            self.transfinite_surface[transfinite_surface_data[i]](self, i)
                            transfinite_surfaces.add(self.surfaces[i])
                    if transfinite_volume_data is not None:
                        for i in range(len(self.volumes)):
                            self.transfinite_volume[transfinite_volume_data[i]](self, i)
                result = True
        return result

    def evaluate_bounding_box(self):
        if len(self.volumes) > 0:
            x_mins = []
            y_mins = []
            z_mins = []
            x_maxs = []
            y_maxs = []
            z_maxs = []
            volumes_dim_tags = map(lambda x: (3, x), self.volumes)
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

    def set_size(self, size, volume_idx=None):
        if volume_idx is None:
            for i in range(len(self.volumes)):
                volumes_dim_tags = (3, self.volumes[i])
                points_dim_tags = gmsh.model.getBoundary(
                    volumes_dim_tags, combined=False, recursive=True
                )
                gmsh.model.mesh.setSize(points_dim_tags, size)
                # print(points_dim_tags)
        else:
            volumes_dim_tags = (3, self.volumes[volume_idx])
            points_dim_tags = gmsh.model.getBoundary(
                volumes_dim_tags, combined=False, recursive=True
            )
            gmsh.model.mesh.setSize(points_dim_tags, size)
            # print(points_dim_tags)

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
            self.transfinite_curve_data[i][0],
            "Progression",
            self.transfinite_curve_data[i][2]
        ),
        1: lambda self, i: gmsh.model.mesh.setTransfiniteCurve(
            self.curves[i],
            self.transfinite_curve_data[i][0],
            "Bump",
            self.transfinite_curve_data[i][2]
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


class Complex:
    def __init__(self, factory, primitives, primitives_physical_data, lcs=None):
        """
        Object that's consisted of primitives
        :param factory: gmsh factory (currently: gmsh.model.geo or gmsh.model.occ)
        :param primitives: [primitive 1, 2, ..., N]
        :param primitives_physical_data: [physical index of primitive 1, 2, ..., N]
        :param lcs: [characteristic length of primitive 1, 2, ..., N]
        """
        for primitive in primitives:
            assert factory == primitive.factory
        assert len(primitives) == len(primitives_physical_data)
        if lcs is not None:
            assert len(primitives) == len(lcs)
        self.factory = factory
        self.primitives = primitives
        self.primitives_physical_data = primitives_physical_data
        self.lcs = lcs

    def inner_boolean(self):
        combinations = list(itertools.combinations(range(len(self.primitives)), 2))
        for combination in combinations:
            print("Inner Boolean %s by %s" % combination)
            primitive_boolean(self.factory, self.primitives[combination[0]], self.primitives[combination[1]])

    def set_size(self, size=None, primitive_idx=None, volume_idx=None):
        if size is None and self.lcs is not None:
            for idx, primitive in enumerate(self.primitives):
                primitive.set_size(self.lcs[idx])
        elif primitive_idx is None and volume_idx is None:
            for primitive in self.primitives:
                primitive.set_size(size)
        elif primitive_idx is not None and volume_idx is None:
            self.primitives[primitive_idx].set_size(size)
        elif primitive_idx is not None and volume_idx is not None:
            self.primitives[primitive_idx].set_size(size, volume_idx)
        else:
            raise ValueError("primitive_idx must be not None if volume_idx is not None")

    def get_volumes_by_physical_index(self, idx):
        vs = []
        for primitive_idx, primitive in enumerate(self.primitives):
            if self.primitives_physical_data[primitive_idx] == idx:
                vs.extend(primitive.volumes)
        return vs

    def transfinite(self, transfinite_surfaces):
        results = []
        for primitive in self.primitives:
            result = primitive.transfinite(transfinite_surfaces)
            results.append(result)
        return results

    def get_union_volume(self):
        dim_tags = []
        for primitive in self.primitives:
            dim_tags += map(lambda x: (3, x), primitive.volumes)
        out_dim_tags, out_dim_tags_map = self.factory.fuse(
            dim_tags[:1], dim_tags[1:], tag=-1, removeObject=False, removeTool=False)
        self.factory.synchronize()
        return out_dim_tags


def primitive_boolean(factory, primitive_obj, primitive_tool):
    start = time.time()
    # Check intersection of bounding boxes first (this operation less expensive than boolean)
    is_intersection = True
    if primitive_obj.bounding_box[0] > primitive_tool.bounding_box[3]:  # obj_x_min > tool_x_max
        is_intersection = False
    if primitive_obj.bounding_box[1] > primitive_tool.bounding_box[4]:  # obj_y_min > tool_y_max
        is_intersection = False
    if primitive_obj.bounding_box[2] > primitive_tool.bounding_box[5]:  # obj_z_min > tool_z_max
        is_intersection = False
    if primitive_obj.bounding_box[3] < primitive_tool.bounding_box[0]:  # obj_x_max < tool_x_min
        is_intersection = False
    if primitive_obj.bounding_box[4] < primitive_tool.bounding_box[1]:  # obj_y_max < tool_y_min
        is_intersection = False
    if primitive_obj.bounding_box[5] < primitive_tool.bounding_box[2]:  # obj_z_max < tool_z_min
        is_intersection = False
    # Check on empty primitive_obj:
    if len(primitive_obj.volumes) <= 0:
        is_intersection = False
    print(is_intersection)
    if is_intersection:
        obj_dim_tags = map(lambda x: (3, x), primitive_obj.volumes)
        tool_dim_tags = map(lambda x: (3, x), primitive_tool.volumes)
        out_dim_tags, out_dim_tags_map = factory.fragment(obj_dim_tags, tool_dim_tags)
        # factory.removeAllDuplicates()
        factory.synchronize()
        new_obj_volumes = []
        for i in range(len(primitive_obj.volumes)):
            new_dim_tags = out_dim_tags_map[i]
            for j in range(len(new_dim_tags)):
                new_obj_volumes.append(new_dim_tags[j][1])
        new_tool_volumes = []
        for i in range(len(primitive_obj.volumes), len(primitive_obj.volumes) + len(primitive_tool.volumes)):
            new_dim_tags = out_dim_tags_map[i]
            for j in range(len(new_dim_tags)):
                new_tool_volumes.append(new_dim_tags[j][1])
        common_vs = set(new_obj_volumes) & set(new_tool_volumes)
        for v in common_vs:
            new_obj_volumes.remove(v)
        primitive_obj.volumes = new_obj_volumes
        primitive_tool.volumes = new_tool_volumes
        primitive_obj.evaluate_bounding_box()
        primitive_tool.evaluate_bounding_box()
    print('{:.3f}s'.format(time.time() - start))


def primitive_cut_by_volume_boolean(factory, primitive_obj, volume):
    start = time.time()
    # Check intersection of bounding boxes first (this operation less expensive than boolean)
    is_intersection = True
    x_min, y_min, z_min, x_max, y_max, z_max = gmsh.model.getBoundingBox(3, volume)
    if primitive_obj.bounding_box[0] > x_max:  # obj_x_min > tool_x_max
        is_intersection = False
    if primitive_obj.bounding_box[1] > y_max:  # obj_y_min > tool_y_max
        is_intersection = False
    if primitive_obj.bounding_box[2] > z_max:  # obj_z_min > tool_z_max
        is_intersection = False
    if primitive_obj.bounding_box[3] < x_min:  # obj_x_max < tool_x_min
        is_intersection = False
    if primitive_obj.bounding_box[4] < y_min:  # obj_y_max < tool_y_min
        is_intersection = False
    if primitive_obj.bounding_box[5] < z_min:  # obj_z_max < tool_z_min
        is_intersection = False
    # Check on empty primitive_obj:
    if len(primitive_obj.volumes) <= 0:
        is_intersection = False
    print(is_intersection)
    if is_intersection:
        obj_dim_tags = map(lambda x: (3, x), primitive_obj.volumes)
        tool_dim_tags = [(3, volume)]
        out_dim_tags, out_dim_tags_map = factory.fragment(obj_dim_tags, tool_dim_tags, removeTool=False)
        new_obj_volumes = []
        for i in range(len(primitive_obj.volumes)):
            new_dim_tags = out_dim_tags_map[i]
            for j in range(len(new_dim_tags)):
                new_obj_volumes.append(new_dim_tags[j][1])
        new_tool_volumes = []
        for i in range(len(primitive_obj.volumes), len(primitive_obj.volumes) + 1):
            new_dim_tags = out_dim_tags_map[i]
            for j in range(len(new_dim_tags)):
                new_tool_volumes.append(new_dim_tags[j][1])
        common_vs = set(new_obj_volumes) & set(new_tool_volumes)
        for v in common_vs:
            new_obj_volumes.remove(v)
        # Remove new_tool_volumes
        dts = map(lambda x: (3, x), new_tool_volumes)
        factory.remove(dts)
        # factory.removeAllDuplicates()
        factory.synchronize()
        primitive_obj.volumes = new_obj_volumes
        primitive_obj.evaluate_bounding_box()
    print('{:.3f}s'.format(time.time() - start))


def complex_boolean(factory, complex_obj, complex_tool):
    for obj_idx, primitive_obj in enumerate(complex_obj.primitives):
        for tool_idx, primitive_tool in enumerate(complex_tool.primitives):
            print("Boolean primitive_obj %s by primitive_tool %s" % (obj_idx, tool_idx))
            primitive_boolean(factory, primitive_obj, primitive_tool)


def primitive_complex_boolean(factory, primitive_obj, complex_tool):
    for idx, primitive_tool in enumerate(complex_tool.primitives):
        print("Boolean primitive_obj by complex_tool's primitive %s" % idx)
        primitive_boolean(factory, primitive_obj, primitive_tool)


def complex_primitive_boolean(factory, complex_obj, primitive_tool):
    for idx, primitive_obj in enumerate(complex_obj.primitives):
        print("Boolean complex_obj's primitive %s by primitive_tool" % idx)
        primitive_boolean(factory, primitive_obj, primitive_tool)


def read_complex_type_1(factory, path, transform_data, curve_type, transfinite_data, physical_tag, lc):
    primitives_curves = []
    origins = []
    rotations = []
    curves = []
    cnt = 0
    with open(path) as f:
        for line in f:
            if not line.startswith("#"):
                tokens = line.split()
                # print(tokens)
                if len(tokens) > 0:
                    cnt += 1
                    if cnt == 1:
                        origins.append(map(lambda x: float(x), tokens))
                    elif cnt == 2:
                        rotations.append(map(lambda x: float(x), tokens))
                    else:
                        curve = []
                        cs = map(lambda x: float(x), tokens)
                        point_cs = []
                        cs_cnt = 0
                        for c in cs:
                            cs_cnt += 1
                            point_cs.append(c)
                            if cs_cnt == 3:
                                cs_cnt = 0
                                curve.append(point_cs)
                                point_cs = []
                        curves.append(curve)
                    if cnt == 14:
                        cnt = 0
                        primitives_curves.append(curves)
                        curves = []
    primitives = []
    physical_data = []
    lcs = []
    for i in range(len(origins)):
        p0 = list(primitives_curves[i][8][0])
        p1 = list(primitives_curves[i][0][0])
        p2 = list(primitives_curves[i][3][0])
        p3 = list(primitives_curves[i][4][0])
        p4 = list(primitives_curves[i][1][len(primitives_curves[i][1]) - 1])
        p5 = list(primitives_curves[i][1][0])
        p6 = list(primitives_curves[i][6][0])
        p7 = list(primitives_curves[i][7][0])
        p0.append(float(lc))
        p1.append(float(lc))
        p2.append(float(lc))
        p3.append(float(lc))
        p4.append(float(lc))
        p5.append(float(lc))
        p6.append(float(lc))
        p7.append(float(lc))
        point_data = [p0, p1, p2, p3, p4, p5, p6, p7]
        curve_data = []
        curve_types = []
        for j in range(len(primitives_curves[i])):
            points = []
            n_points = len(primitives_curves[i][j])
            if n_points > 2:
                for k in range(1, n_points - 1):
                    point_with_lc = list(primitives_curves[i][j][k])
                    point_with_lc.append(float(lc))
                    points.append(point_with_lc)
                curve_data.append(points)
                curve_types.append(curve_type)
            else:
                curve_data.append([])
                curve_types.append(0)
        t_form_data = []
        t_form_data.append(origins[i][0] + transform_data[0])
        t_form_data.append(origins[i][1] + transform_data[1])
        t_form_data.append(origins[i][2] + transform_data[2])
        if len(rotations[i]) == 3:
            t_form_data.append(t_form_data[0])
            t_form_data.append(t_form_data[1])
            t_form_data.append(t_form_data[2])
            t_form_data.append(rotations[i][0])
            t_form_data.append(rotations[i][1])
            t_form_data.append(rotations[i][2])
        elif len(rotations[i]) == 4:
            t_form_data.append(rotations[i][0])
            t_form_data.append(rotations[i][1])
            t_form_data.append(rotations[i][2])
            t_form_data.append(rotations[i][3])
        t_finite_data = [
            [transfinite_data[0], 0, 1],
            [transfinite_data[0], 0, 1],
            [transfinite_data[0], 0, 1],
            [transfinite_data[0], 0, 1],
            [transfinite_data[1], 0, 1],
            [transfinite_data[1], 0, 1],
            [transfinite_data[1], 0, 1],
            [transfinite_data[1], 0, 1],
            [transfinite_data[2], 0, 1],
            [transfinite_data[2], 0, 1],
            [transfinite_data[2], 0, 1],
            [transfinite_data[2], 0, 1],
        ]
        t_finite_type = 0
        primitives.append(Primitive(
            factory,
            point_data,
            t_form_data,
            curve_types,
            curve_data,
            t_finite_data,
            t_finite_type
        ))
        physical_data.append(physical_tag)
        lcs.append(lc)
    return Complex(factory, primitives, physical_data, lcs)


def read_complex_type_2(factory, path, transform_data, transfinite_data, physical_tag, lc):
    origins = []
    rotations = []
    coordinates = []
    primitives_cs = []
    cnt = 0
    with open(path) as f:
        for line in f:
            if not line.startswith("#"):
                tokens = line.split()
                # print(tokens)
                if len(tokens) > 0:
                    cnt += 1
                    if cnt == 1:
                        origins.append(map(lambda x: float(x), tokens))
                    elif cnt == 2:
                        rotations.append(map(lambda x: float(x), tokens))
                    else:
                        coordinates.append(map(lambda x: float(x), tokens))
                    if cnt == 10:
                        cnt = 0
                        primitives_cs.append(coordinates)
                        coordinates = []
    primitives = []
    physical_data = []
    lcs = []
    for i in range(len(origins)):
        point_data = []
        for j in range(len(primitives_cs[i])):
            point_with_lc = list(primitives_cs[i][j])
            point_with_lc.append(float(lc))
            point_data.append(point_with_lc)
        t_form_data = [
            origins[i][0] + transform_data[0],
            origins[i][1] + transform_data[1],
            origins[i][2] + transform_data[2]
        ]
        if len(rotations[i]) == 3:
            t_form_data.append(t_form_data[0])
            t_form_data.append(t_form_data[1])
            t_form_data.append(t_form_data[2])
            t_form_data.append(rotations[i][0])
            t_form_data.append(rotations[i][1])
            t_form_data.append(rotations[i][2])
        elif len(rotations[i]) == 4:
            t_form_data.append(rotations[i][0])
            t_form_data.append(rotations[i][1])
            t_form_data.append(rotations[i][2])
            t_form_data.append(rotations[i][3])
        t_finite_data = [
            [transfinite_data[0], 0, 1],
            [transfinite_data[0], 0, 1],
            [transfinite_data[0], 0, 1],
            [transfinite_data[0], 0, 1],
            [transfinite_data[1], 0, 1],
            [transfinite_data[1], 0, 1],
            [transfinite_data[1], 0, 1],
            [transfinite_data[1], 0, 1],
            [transfinite_data[2], 0, 1],
            [transfinite_data[2], 0, 1],
            [transfinite_data[2], 0, 1],
            [transfinite_data[2], 0, 1],
        ]  # TODO do n_points of smaller edge length smaller and so on
        t_finite_type = 0
        primitives.append(Primitive(
            factory,
            point_data,
            t_form_data,
            transfinite_curve_data=t_finite_data,
            transfinite_type=t_finite_type
        ))
        physical_data.append(physical_tag)
        lcs.append(lc)
    return Complex(factory, primitives, physical_data, lcs)


def divide_primitive(divide_data, base_points, curves_points=None):
    nx = divide_data[0]
    ny = divide_data[1]
    nz = divide_data[2]
    points = []
    if curves_points is None:
        curves_points = [[]] * 12
    for i in range(12):
        if len(curves_points[i]) > 0:
            points.append([
                base_points[Primitive.curves_local_points[i][0]],
                curves_points[i],
                base_points[Primitive.curves_local_points[i][1]]
            ])
        else:
            points.append([
                base_points[Primitive.curves_local_points[i][0]],
                base_points[Primitive.curves_local_points[i][1]]
            ])
    curves_lengths = []
    for i in range(len(points)):
        length = 0
        for j in range(1, len(points[i])):
            p0 = points[i][j - 1]
            p1 = points[i][j]
            r = [p1[0] - p0[0], p1[1] - p0[1], p1[2] - p0[2]]
            length += math.sqrt(r[0] * r[0] + r[1] * r[1] + r[2] * r[2])
        curves_lengths.append(length)
    curves_delta_lengths = []
    for i in range(4):
        curves_delta_lengths.append(curves_lengths[i] / nx)
    for i in range(4, 8):
        curves_delta_lengths.append(curves_lengths[i] / ny)
    for i in range(8, 12):
        curves_delta_lengths.append(curves_lengths[i] / nz)
    new_points = []
    for i in range(12):
        dl = curves_delta_lengths[i]
        dl_cnt = dl
        new_curve_points = []
        new_curve_parts = []
        for j in range(1, len(points[i])):
            p0 = points[i][j - 1]
            p1 = points[i][j]
            new_curve_points.append(p0)
            new = False
            while not new:
                r = [p1[0] - p0[0], p1[1] - p0[1], p1[2] - p0[2]]
                mag = math.sqrt(r[0] * r[0] + r[1] * r[1] + r[2] * r[2])
                norm = [r[0] / mag, r[1] / mag, r[2] / mag]
                if mag > dl_cnt:
                    new_p = [
                        p0[0] + norm[0] * dl_cnt,
                        p0[1] + norm[1] * dl_cnt,
                        p0[2] + norm[2] * dl_cnt,
                        p0[3]
                    ]
                    p0 = new_p
                    new_curve_points.append(new_p)
                    new_curve_parts.append(new_curve_points)
                    new_curve_points = [new_p]
                    dl_cnt = dl
                else:
                    new_curve_points.append(p1)
                    new = True
                    dl_cnt -= mag
        new_curve_parts.append(new_curve_points)
        new_points.append(new_curve_parts)
    for i in range(nx):
        for j in range(ny):
            for k in range(nz):
                print("a")
    return new_points


class Environment:
    def __init__(self, factory, lx, ly, lz, lc, transform_data, inner_surfaces):
        self.factory = factory
        self.lx = lx
        self.ly = ly
        self.lz = lz
        self.lc = lc
        self.transform_data = transform_data
        self.inner_surfaces = inner_surfaces
        # Points
        self.points = []
        self.points.append(factory.addPoint(lx / 2, ly / 2, -lz / 2, lc))
        self.points.append(factory.addPoint(-lx / 2, ly / 2, -lz / 2, lc))
        self.points.append(factory.addPoint(-lx / 2, -ly / 2, -lz / 2, lc))
        self.points.append(factory.addPoint(lx / 2, -ly / 2, -lz / 2, lc))
        self.points.append(factory.addPoint(lx / 2, ly / 2, lz / 2, lc))
        self.points.append(factory.addPoint(-lx / 2, ly / 2, lz / 2, lc))
        self.points.append(factory.addPoint(-lx / 2, -ly / 2, lz / 2, lc))
        self.points.append(factory.addPoint(lx / 2, -ly / 2, lz / 2, lc))
        # Transform
        dim_tags = zip([0] * len(self.points), self.points)
        factory.translate(dim_tags, transform_data[0], transform_data[1], transform_data[2])
        factory.rotate(dim_tags, transform_data[3], transform_data[4], transform_data[5],
                       1, 0, 0, transform_data[6])
        factory.rotate(dim_tags, transform_data[3], transform_data[4], transform_data[5],
                       0, 1, 0, transform_data[7])
        factory.rotate(dim_tags, transform_data[3], transform_data[4], transform_data[5],
                       0, 0, 1, transform_data[8])
        # Curves
        self.curves = []
        for i in range(len(self.curves_points)):
            curve_points = [self.points[x] for x in self.curves_points[i]]
            self.curves.append(factory.addLine(curve_points[0], curve_points[1]))
        # Surfaces
        self.surfaces = []
        for i in range(len(self.surfaces_curves)):
            if factory == gmsh.model.geo:
                cl_tag = factory.addCurveLoop(
                    map(lambda x, y: y * self.curves[x], self.surfaces_curves[i], self.surfaces_curves_signs[i]))
                self.surfaces.append(factory.addSurfaceFilling([cl_tag]))
            else:
                cl_tag = factory.addCurveLoop([self.curves[x] for x in self.surfaces_curves[i]])
                self.surfaces.append(factory.addSurfaceFilling(cl_tag))
        # Volumes
        self.volumes = []
        out_sl_tag = factory.addSurfaceLoop(self.surfaces)
        in_sl_tag = factory.addSurfaceLoop(inner_surfaces)
        self.volumes.append(factory.addVolume([out_sl_tag, in_sl_tag]))
        factory.synchronize()

    curves_points = [
        [1, 0], [5, 4], [6, 7], [2, 3],
        [3, 0], [2, 1], [6, 5], [7, 4],
        [0, 4], [1, 5], [2, 6], [3, 7]
    ]

    surfaces_curves = [
        [5, 9, 6, 10],
        [4, 11, 7, 8],
        [3, 10, 2, 11],
        [0, 8, 1, 9],
        [0, 5, 3, 4],
        [1, 7, 2, 6]
    ]

    surfaces_curves_signs = [
        [1, 1, -1, -1],
        [-1, 1, 1, -1],
        [-1, 1, 1, -1],
        [1, 1, -1, -1],
        [-1, -1, 1, 1],
        [1, -1, -1, 1]
    ]

    surfaces_names = {
        0: "NX",
        1: "X",
        2: "NY",
        3: "Y",
        4: "NZ",
        5: "Z"
    }
