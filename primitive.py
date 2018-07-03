import itertools
import time
import gmsh


class Primitive:
    def __init__(self, factory, point_data, transform_data=None, curve_types=None, curve_data=None,
                 transfinite_curve_data=None, transfinite_type=None, volume_name="Default"):
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
        [displacement x, y, z, rotation vector x, y, z, rotation angle] or
        [displacement x, y, z, rotation angle x, y, z]
        :param curve_types: [line1_type, line2_type, ..., line12_type],
        types: 0 - line, 1 - circle, 2 - ellipse (FIXME not implemented for occ factory),
        3 - spline, 4 - bspline (number of curve points > 1), 5 - bezier curve
        :param curve_data: [[line1_point1_x, line1_point1_y, line1_point1_z], ...], ...]
        :param transfinite_curve_data: [[line1 number of nodes, type, coefficient], ..., [line12 ...]]
        types: 0 - progression, 1 - bump
        :param transfinite_type: 0, 1, 2 or 4 determines orientation of tetrahedra at structured volume and its surfaces
        :param volume_name: primitive's physical volume name
        """
        self.factory = factory
        if curve_types is None:
            curve_types = [0] * 12
        if curve_data is None:
            curve_data = [[]] * 12
        self.transfinite_curve_data = transfinite_curve_data
        self.transfinite_type = transfinite_type
        self.volume_name = volume_name
        self.points = []
        self.curves_points = []
        self.curves = []
        self.surfaces = []
        self.volumes = []
        # Points
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
        tag = self.factory.addSurfaceLoop(self.surfaces)
        tag = self.factory.addVolume([tag])
        self.volumes.append(tag)
        self.factory.synchronize()
        # Other
        self.points_coordinates = []
        self.curves_points_coordinates = []
        for point in self.points:
            bb = gmsh.model.getBoundingBox(0, point)
            self.points_coordinates.append([bb[0], bb[1], bb[2]])
        for curve_points in self.curves_points:
            cs = []
            for point in curve_points:
                bb = gmsh.model.getBoundingBox(0, point)
                cs.append([bb[0], bb[1], bb[2]])
            self.curves_points_coordinates.append(cs)
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

    def set_size(self, size):
        for v in self.volumes:
            points_dim_tags = gmsh.model.getBoundary([(3, v)], combined=False, recursive=True)
            gmsh.model.mesh.setSize(points_dim_tags, size)

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
    def __init__(self, factory, primitives):
        """
        Object consisting of primitives
        :param factory: gmsh factory (currently: gmsh.model.geo or gmsh.model.occ)
        :param primitives: [primitive 1, primitive 2, ..., primitive N]
        """
        for primitive in primitives:
            assert factory == primitive.factory
        self.factory = factory
        self.primitives = primitives
        self.volumes_names_dict = {}
        for i, primitive in enumerate(self.primitives):
            key = primitive.volume_name
            if key in self.volumes_names_dict:
                self.volumes_names_dict[key].append(i)
            else:
                self.volumes_names_dict[key] = [i]

    def inner_boolean(self):
        combinations = list(itertools.combinations(range(len(self.primitives)), 2))
        for combination in combinations:
            print("Boolean primitive_obj {} {} by primitive_tool {} {}".format(
                combination[0], self.primitives[combination[0]].volume_name,
                combination[1], self.primitives[combination[1]].volume_name))
            primitive_boolean(self.factory, self.primitives[combination[0]], self.primitives[combination[1]])

    def set_size(self, size, primitive_idx=None):
        if primitive_idx is not None:
            self.primitives[primitive_idx].set_size(size)
        else:
            for primitive in self.primitives:
                primitive.set_size(size)

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

    def get_volumes_by_name(self, name):
        vs = []
        primitive_idxs = self.volumes_names_dict.get(name)
        if primitive_idxs is not None:
            for i in primitive_idxs:
                vs.extend(self.primitives[i].volumes)
        return vs


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
        print("Zero object!")
    # Check on empty primitive_tool:
    if len(primitive_tool.volumes) <= 0:
        is_intersection = False
        print("Zero tool!")
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
        # primitive_obj.evaluate_bounding_box()  # FIXME bad bounding box after boolean
        # primitive_tool.evaluate_bounding_box()
    print('{:.3f}s'.format(time.time() - start))


def complex_boolean(factory, complex_obj, complex_tool):
    for obj_idx, primitive_obj in enumerate(complex_obj.primitives):
        for tool_idx, primitive_tool in enumerate(complex_tool.primitives):
            print("Boolean primitive_obj {}/{} {} by primitive_tool {}/{} {}".format(
                obj_idx + 1, len(complex_obj.primitives), primitive_obj.volume_name,
                tool_idx + 1, len(complex_tool.primitives), primitive_tool.volume_name))
            primitive_boolean(factory, primitive_obj, primitive_tool)


def primitive_complex_boolean(factory, primitive_obj, complex_tool):
    for idx, primitive_tool in enumerate(complex_tool.primitives):
        print("Boolean primitive_obj {} by complex_tool's primitive {}/{} {}".format(
            primitive_obj.volume_name,
            idx + 1, len(complex_tool.primitives), primitive_tool.volume_name))
        primitive_boolean(factory, primitive_obj, primitive_tool)


def complex_primitive_boolean(factory, complex_obj, primitive_tool):
    for idx, primitive_obj in enumerate(complex_obj.primitives):
        print("Boolean complex_obj's primitive {}/{} {} by primitive_tool {}".format(
            idx + 1, len(complex_obj.primitives), primitive_obj.volume_name,
            primitive_tool.volume_name))
        primitive_boolean(factory, primitive_obj, primitive_tool)


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
        # Remove new_tool_volumes without volume itself (it happens when there is no real intersection)
        if volume in new_tool_volumes:
            new_tool_volumes.remove(volume)
        dts = map(lambda x: (3, x), new_tool_volumes)
        factory.remove(dts)
        factory.synchronize()
        primitive_obj.volumes = new_obj_volumes
        # primitive_obj.evaluate_bounding_box()
    print('{:.3f}s'.format(time.time() - start))


def complex_cut_by_volume_boolean(factory, complex_obj, volume):
    for idx, primitive_obj in enumerate(complex_obj.primitives):
        print("Cut boolean complex_obj's primitive {}/{} {} by volume {}".format(
            idx + 1, len(complex_obj.primitives), primitive_obj.volume_name, volume))
        primitive_cut_by_volume_boolean(factory, primitive_obj, volume)


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
