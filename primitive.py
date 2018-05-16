import gmsh
import itertools
import time


class Primitive:
    def __init__(self, factory, data, transform_data, curve_types, curve_data,
                 transfinite_curve_data=None, transfinite_type=None):
        self.factory = factory
        self.data = data
        self.transform_data = transform_data
        self.curve_types = curve_types
        self.curve_data = curve_data
        self.transfinite_curve_data = transfinite_curve_data
        self.transfinite_type = transfinite_type
        self.points = []
        self.curves_points = []
        self.curves = []
        self.surfaces = []
        self.volumes = []
        self.bounding_box = []  # [x_min, y_min, z_min, x_max, y_max, z_max] Call self.evaluate_bounding_box() to init
        self.create()

    def create(self):
        for i in range(0, len(self.data), 4):
            tag = self.factory.addPoint(
                self.data[i],
                self.data[i + 1],
                self.data[i + 2],
                self.data[i + 3])
            self.points.append(tag)
        for i in range(len(self.curve_data)):
            ps = []
            for j in range(0, len(self.curve_data[i]), 4):
                tag = self.factory.addPoint(
                    self.curve_data[i][j],
                    self.curve_data[i][j + 1],
                    self.curve_data[i][j + 2],
                    self.curve_data[i][j + 3])
                ps.append(tag)
            self.curves_points.append(ps)
        self.transform()  # Transform is here because bugs when transform() called after curves creation
        for i in range(12):
            tag = self.add_curve[self.curve_types[i]](self, i)
            self.curves.append(tag)
        for i in range(6):
            if self.factory == gmsh.model.geo:
                tag = self.factory.addCurveLoop(
                    map(lambda x, y: y * self.curves[x],
                        self.surfaces_curves[i],
                        self.surfaces_curves_signs[i]))
                tag = self.factory.addSurfaceFilling([tag])
            else:
                tag = self.factory.addCurveLoop(
                    map(lambda x: self.curves[x],
                        self.surfaces_curves[i]))
                tag = self.factory.addSurfaceFilling(tag)
            self.surfaces.append(tag)
        tag = self.factory.addSurfaceLoop(self.surfaces)
        tag = self.factory.addVolume([tag])
        self.volumes.append(tag)
        self.factory.synchronize()
        self.evaluate_bounding_box()

    def transform(self):
        dim_tags = map(lambda x: (0, x), self.points)
        for curve_points in self.curves_points:
            dim_tags += map(lambda x: (0, x), curve_points)
        self.factory.translate(dim_tags, self.transform_data[0], self.transform_data[1], self.transform_data[2])
        self.factory.rotate(dim_tags,
                            self.transform_data[3], self.transform_data[4], self.transform_data[5],
                            1, 0, 0, self.transform_data[6])
        self.factory.rotate(dim_tags,
                            self.transform_data[3], self.transform_data[4], self.transform_data[5],
                            0, 1, 0, self.transform_data[7])
        self.factory.rotate(dim_tags,
                            self.transform_data[3], self.transform_data[4], self.transform_data[5],
                            0, 0, 1, self.transform_data[8])

    def recombine(self):
        for i in range(len(self.surfaces)):
            gmsh.model.mesh.setRecombine(2, self.surfaces[i])

    def smooth(self, n):
        for i in range(len(self.surfaces)):
            gmsh.model.mesh.setSmoothing(2, self.surfaces[i], n)

    def transfinite(self, transfinite_surfaces):
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
                    if self.surfaces[i] not in transfinite_surfaces:  # Workaround from double transfinite surfaces
                        self.transfinite_surface[transfinite_surface_data[i]](self, i)
                        transfinite_surfaces.add(self.surfaces[i])
                if transfinite_volume_data is not None:
                    for i in range(len(self.volumes)):
                        self.transfinite_volume[transfinite_volume_data[i]](self, i)

    def evaluate_bounding_box(self):
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

    def check_to_transfinite(self):
        if self.factory != gmsh.model.occ:
            return True
        if len(self.volumes) != 1:
            return False
        volumes_dim_tags = map(lambda x: (3, x), self.volumes)
        surfaces_dim_tags = gmsh.model.getBoundary(volumes_dim_tags)
        if len(surfaces_dim_tags) != 6:
            return False
        else:
            return True

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

    curve_points = [
        [1, 0], [5, 4], [6, 7], [2, 3],
        [3, 0], [2, 1], [6, 5], [7, 4],
        [0, 4], [1, 5], [2, 6], [3, 7]
    ]

    surfaces_points = [
        [2, 6, 5, 1],  # NX
        [3, 7, 4, 0],  # X
        [2, 6, 7, 3],  # NY
        [1, 5, 4, 0],  # Y
        [3, 2, 1, 0],  # NZ
        [7, 6, 5, 4]  # Z
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
            [self.points[x] for x in self.surfaces_points[i]]
        ),
        1: lambda self, i: gmsh.model.mesh.setTransfiniteSurface(
            self.surfaces[i],
            "Right",
            [self.points[x] for x in self.surfaces_points[i]]
        ),
        2: lambda self, i: gmsh.model.mesh.setTransfiniteSurface(
            self.surfaces[i],
            "AlternateLeft",
            [self.points[x] for x in self.surfaces_points[i]]
        ),
        3: lambda self, i: gmsh.model.mesh.setTransfiniteSurface(
            self.surfaces[i],
            "AlternateRight",
            [self.points[x] for x in self.surfaces_points[i]]
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
            self.points[self.curve_points[i][0]],
            self.points[self.curve_points[i][1]]
        ),
        1: lambda self, i: self.factory.addCircleArc(
            self.points[self.curve_points[i][0]],
            self.curves_points[i][0],
            self.points[self.curve_points[i][1]]
        ),
        2: lambda self, i: self.factory.addEllipseArc(
            self.points[self.curve_points[i][0]],
            self.curves_points[i][0],
            self.curves_points[i][1],
            self.points[self.curve_points[i][1]],
        ),  # TODO implement occ ellipse
        3: lambda self, i: self.factory.addSpline(
            [self.points[self.curve_points[i][0]]] +
            self.curves_points[i] +
            [self.points[self.curve_points[i][1]]]
        ),
        4: lambda self, i: self.factory.addBSpline(
            [self.points[self.curve_points[i][0]]] +
            self.curves_points[i] +
            [self.points[self.curve_points[i][1]]]
        ),
        5: lambda self, i: self.factory.addBezier(
            [self.points[self.curve_points[i][0]]] +
            self.curves_points[i] +
            [self.points[self.curve_points[i][1]]]
        )
    }


class Complex:
    def __init__(self, factory, primitives, primitive_physical_groups, lcs=None):
        assert len(primitives) == len(primitive_physical_groups)
        assert len(primitives) == len(lcs) or lcs is None
        self.factory = factory
        self.primitives = primitives
        self.lcs = lcs
        self.primitive_physical_groups = primitive_physical_groups
        for primitive in self.primitives:
            if self.factory != primitive.factory:
                raise ValueError("All primitives factories must be as Complex factory")

    def in_boolean(self):
        combinations = list(itertools.combinations(range(len(self.primitives)), 2))
        # print(combinations)
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

    def get_volumes_idxs_by_physical_group_tag(self, tag):
        idxs = []
        for idx, primitive in enumerate(self.primitives):
            if self.primitive_physical_groups[idx] == tag:
                idxs.extend(primitive.volumes)
        return idxs

    def transfinite(self, transfinite_surfaces):
        for primitive in self.primitives:
            result = primitive.check_to_transfinite()
            print(result)
            if result:
                primitive.transfinite(transfinite_surfaces)


def primitive_boolean(factory, primitive_obj, primitive_tool):
    start = time.time()
    # Check intersection of bounding boxes first (this operation less expensive than boolean)
    is_intersection = True
    if (primitive_obj.bounding_box[0] > primitive_tool.bounding_box[3]  # obj_x_min > tool_x_max
        or primitive_obj.bounding_box[1] > primitive_tool.bounding_box[4]  # obj_y_min > tool_y_max
        or primitive_obj.bounding_box[2] > primitive_tool.bounding_box[5]  # obj_z_min > tool_z_max
        or primitive_obj.bounding_box[3] < primitive_tool.bounding_box[0]  # obj_x_max < tool_x_min
        or primitive_obj.bounding_box[4] < primitive_tool.bounding_box[1]  # obj_y_max < tool_y_min
        or primitive_obj.bounding_box[5] < primitive_tool.bounding_box[2]):  # obj_z_max < tool_z_min
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
