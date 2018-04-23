import gmsh
import sys


class Primitive:
    surface_names = {
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
    surface_curves = [
        [5, 9, 6, 10],
        [4, 11, 7, 8],
        [3, 10, 2, 11],
        [0, 8, 1, 9],
        [0, 5, 3, 4],
        [1, 7, 2, 6]
    ]
    surface_points = [
        [2, 6, 5, 1],  # NX
        [3, 7, 4, 0],  # X
        [2, 6, 7, 3],  # NY
        [1, 5, 4, 0],  # Y
        [3, 2, 1, 0],  # NZ
        [7, 6, 5, 4]  # Z
    ]
    surface_curves_sign = [
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
            [self.points[x] for x in self.surface_points[i]]
        ),
        1: lambda self, i: gmsh.model.mesh.setTransfiniteSurface(
            self.surfaces[i],
            "Right",
            [self.points[x] for x in self.surface_points[i]]
        ),
        2: lambda self, i: gmsh.model.mesh.setTransfiniteSurface(
            self.surfaces[i],
            "AlternateLeft",
            [self.points[x] for x in self.surface_points[i]]
        ),
        3: lambda self, i: gmsh.model.mesh.setTransfiniteSurface(
            self.surfaces[i],
            "AlternateRight",
            [self.points[x] for x in self.surface_points[i]]
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

    def __init__(self, factory, data, transform_data, curve_types, curve_data,
                 transfinite_curve_data=None, transfinite_type=None):
        self.data = data
        self.transform_data = transform_data
        self.curve_types = curve_types
        self.curve_data = curve_data
        self.transfinite_curve_data = transfinite_curve_data
        if transfinite_type == 0:
            self.transfinite_surface_data = [1, 1, 1, 1, 1, 1]
            self.transfinite_volume_data = [0]
        elif transfinite_type == 1:
            self.transfinite_surface_data = [1, 1, 0, 0, 0, 0]
            self.transfinite_volume_data = [1]
        elif transfinite_type == 2:
            self.transfinite_surface_data = [0, 0, 0, 0, 1, 1]
            self.transfinite_volume_data = [2]
        elif transfinite_type == 3:
            self.transfinite_surface_data = [0, 0, 1, 1, 0, 0]
            self.transfinite_volume_data = [3]
        else:
            self.transfinite_surface_data = None
            self.transfinite_volume_data = None
        self.points = []
        self.curves_points = []
        self.curves = []
        self.surfaces = []
        self.volumes = []
        self.surfaces_physical_groups = [
            None, None, None, None, None, None]  # NX, X, NY, Y, NZ, Z
        self.volumes_physical_groups = [None]
        self.factory = factory

    def recombine(self):
        for i in range(len(self.surfaces)):
            gmsh.model.mesh.setRecombine(2, self.surfaces[i])

    def smooth(self, n):
        for i in range(len(self.surfaces)):
            gmsh.model.mesh.setSmoothing(2, self.surfaces[i], n)

    def transfinite(self):
        if self.transfinite_curve_data is not None:
            for i in range(len(self.curves)):
                self.transfinite_curve[self.transfinite_curve_data[i][1]](self, i)
            if self.transfinite_surface_data is not None:
                for i in range(len(self.surfaces)):
                    self.transfinite_surface[self.transfinite_surface_data[i]](self, i)
                if self.transfinite_volume_data is not None:
                    for i in range(len(self.volumes)):
                        self.transfinite_volume[self.transfinite_volume_data[i]](self, i)

    def transform(self):
        dim_tags = zip([0] * len(self.points), self.points)
        for curve_points in self.curves_points:
            dim_tags += zip([0] * len(curve_points), curve_points)
        self.factory.translate(
            dim_tags, self.transform_data[0], self.transform_data[1], self.transform_data[2]
        )
        self.factory.rotate(dim_tags,
                            self.transform_data[3], self.transform_data[4], self.transform_data[5],
                            1, 0, 0, self.transform_data[6])
        self.factory.rotate(dim_tags,
                            self.transform_data[3], self.transform_data[4], self.transform_data[5],
                            0, 1, 0, self.transform_data[7])
        self.factory.rotate(dim_tags,
                            self.transform_data[3], self.transform_data[4], self.transform_data[5],
                            0, 0, 1, self.transform_data[8])

    def get_actual_surfaces(self, combined=False, oriented=False, recursive=False):
        volumes_dim_tags = zip([3] * len(self.volumes), self.volumes)
        surfaces_dim_tags = gmsh.model.getBoundary(
            volumes_dim_tags, combined=combined, oriented=oriented, recursive=recursive
        )
        return surfaces_dim_tags

    def correct_after_occ(self):
        surfaces_dim_tags = self.get_actual_surfaces()
        new_surfaces = [x[1] for x in surfaces_dim_tags]
        bad_surfaces = [x for x in self.surfaces if x not in new_surfaces]
        # print(surfaces_dim_tags)
        # print(new_surfaces)
        # print(bad_surfaces)
        surface_map = [2, 0, 1, 3, 4, 5]  # [NX, X, NY, Y, NZ, Z] to [X, NY, NX, Y, NZ, Z]
        self.surfaces = map(lambda x: new_surfaces[x], surface_map)
        # print(self.surfaces)
        bad_surfaces_dim_tags = zip([2] * len(bad_surfaces), bad_surfaces)
        self.factory.remove(bad_surfaces_dim_tags, recursive=True)

    def correct_to_transfinite(self):
        surfaces_dim_tags = self.get_actual_surfaces()
        # print(surfaces_dim_tags)
        if len(surfaces_dim_tags) == 6:
            new_surfaces = [x[1] for x in surfaces_dim_tags]
            # print(new_surfaces)
            # print(bad_surfaces)
            surface_map = [2, 0, 1, 3, 4, 5]  # [NX, X, NY, Y, NZ, Z] to [X, NY, NX, Y, NZ, Z]
            self.surfaces = map(lambda x: new_surfaces[x], surface_map)
            # print(self.surfaces)
            surfaces_dim_tags = zip([2] * len(self.surfaces), self.surfaces)
            curves = []
            for i in range(len(surfaces_dim_tags)):
                # print(surfaces_dim_tags[i])
                curves_dim_tags = gmsh.model.getBoundary(surfaces_dim_tags[i], combined=False)
                # print(curves_dim_tags)
                curves.append([abs(x[1]) for x in curves_dim_tags])
            x_curves = []
            y_curves = []
            z_curves = []
            min_curve = sys.maxsize
            min_curve_idx = 0
            min_surface_idx = 0
            for i in range(len(curves)):
                for j in range(len(curves[i])):
                    curve = curves[i][j]
                    if curve < min_curve:
                        min_curve = curve
                        min_curve_idx = i
                        min_surface_idx = j
            # print(min_curve)
            # print(min_surface_idx)
            # print(min_curve_idx)
            x_curves.append(curves[min_surface_idx][min_curve_idx])
            if min_curve_idx == 0:
                x_curves.append(curves[min_surface_idx][min_curve_idx + 2])
                y_curves.append(curves[min_surface_idx][min_curve_idx + 1])
                y_curves.append(curves[min_surface_idx][min_curve_idx + 3])
            elif min_curve_idx == 1:
                x_curves.append(curves[min_surface_idx][min_curve_idx + 2])
                y_curves.append(curves[min_surface_idx][min_curve_idx - 1])
                y_curves.append(curves[min_surface_idx][min_curve_idx + 1])
            elif min_curve_idx == 2:
                x_curves.append(curves[min_surface_idx][min_curve_idx - 2])
                y_curves.append(curves[min_surface_idx][min_curve_idx - 1])
                y_curves.append(curves[min_surface_idx][min_curve_idx + 1])
            elif min_curve_idx == 3:
                x_curves.append(curves[min_surface_idx][min_curve_idx - 2])
                y_curves.append(curves[min_surface_idx][min_curve_idx - 3])
                y_curves.append(curves[min_surface_idx][min_curve_idx - 1])
            for i in range(len(curves)):
                if i != min_surface_idx:
                    if x_curves[0] in curves[i]:
                        idx = curves[i].index(x_curves[0])
                        if idx == 0:
                            x_curves.append(curves[i][idx + 2])
                        elif idx == 1:
                            x_curves.append(curves[i][idx + 2])
                        elif idx == 2:
                            x_curves.append(curves[i][idx - 2])
                        elif idx == 3:
                            x_curves.append(curves[i][idx - 2])
                    elif x_curves[1] in curves[i]:
                        idx = curves[i].index(x_curves[1])
                        if idx == 0:
                            x_curves.append(curves[i][idx + 2])
                        elif idx == 1:
                            x_curves.append(curves[i][idx + 2])
                        elif idx == 2:
                            x_curves.append(curves[i][idx - 2])
                        elif idx == 3:
                            x_curves.append(curves[i][idx - 2])
                    elif y_curves[0] in curves[i]:
                        idx = curves[i].index(y_curves[0])
                        if idx == 0:
                            y_curves.append(curves[i][idx + 2])
                        elif idx == 1:
                            y_curves.append(curves[i][idx + 2])
                        elif idx == 2:
                            y_curves.append(curves[i][idx - 2])
                        elif idx == 3:
                            y_curves.append(curves[i][idx - 2])
                    elif y_curves[1] in curves[i]:
                        idx = curves[i].index(y_curves[1])
                        if idx == 0:
                            y_curves.append(curves[i][idx + 2])
                        elif idx == 1:
                            y_curves.append(curves[i][idx + 2])
                        elif idx == 2:
                            y_curves.append(curves[i][idx - 2])
                        elif idx == 3:
                            y_curves.append(curves[i][idx - 2])
            for i in range(len(curves)):
                for j in range(len(curves[i])):
                    curve = curves[i][j]
                    if curve not in x_curves and curve not in y_curves and curve not in z_curves:
                        z_curves.append(curve)
            # print(x_curves)
            # print(y_curves)
            # print(z_curves)
            self.curves = []
            self.curves.extend(x_curves)
            self.curves.extend(z_curves)
            self.curves.extend(y_curves)
            # print(self.curves)
            points_dim_tags = gmsh.model.getBoundary(surfaces_dim_tags, recursive=True)
            new_points = [x[1] for x in points_dim_tags]
            self.points = new_points
            # print(self.points)
            return True
        return False

    def set_size(self, size, volume_idx=None):
        if volume_idx is None:
            for i in range(len(self.volumes)):
                volumes_dim_tags = (3, self.volumes[i])
                points_dim_tags = gmsh.model.getBoundary(
                    volumes_dim_tags, recursive=True
                )
                gmsh.model.mesh.setSize(points_dim_tags, size)
                # print(points_dim_tags)
        else:
            volumes_dim_tags = (3, self.volumes[volume_idx])
            points_dim_tags = gmsh.model.getBoundary(
                volumes_dim_tags, recursive=True
            )
            gmsh.model.mesh.setSize(points_dim_tags, size)
            # print(points_dim_tags)

    def check_tags(self):
        dim_tags = zip([3] * len(self.volumes), self.volumes)
        surface_dim_tags = gmsh.model.getBoundary(
            dim_tags, combined=False, oriented=False, recursive=False
        )
        result = [self.surfaces[i] - surface_dim_tags[i][1] for i in range(len(surface_dim_tags))]
        assert (sum(result) == 0)
        # print (surface_dim_tags)
        for i in range(len(surface_dim_tags)):
            # print (surface_dim_tags[i])
            curve_dim_tags = gmsh.model.getBoundary(
                surface_dim_tags[i], combined=False, oriented=False, recursive=False
            )
            # print (curve_dim_tags)
            result = [self.curves[self.surface_curves[i][j]] - curve_dim_tags[j][1] for j in
                      range(len(curve_dim_tags) - 4)]
            assert (sum(result) == 0)
            for j in range(len(curve_dim_tags) - 4):
                # print (curve_dim_tags[i])
                point_dim_tags = gmsh.model.getBoundary(
                    curve_dim_tags[j], combined=False, oriented=False, recursive=False
                )
                # print (point_dim_tags)
                result = [self.points[self.curve_points[self.surface_curves[i][j]][k]] - point_dim_tags[k][1] for k in
                          range(len(point_dim_tags) - 2)]
                assert (sum(result) == 0)
        print ("Check tags ok")

    def create(self):
        for i in range(0, len(self.data), 4):
            tag = self.factory.addPoint(
                self.data[i],
                self.data[i + 1],
                self.data[i + 2],
                self.data[i + 3])
            self.points.append(tag)
        for i in range(0, len(self.curve_data)):
            ps = []
            for j in range(0, len(self.curve_data[i]), 4):
                tag = self.factory.addPoint(
                    self.curve_data[i][j],
                    self.curve_data[i][j + 1],
                    self.curve_data[i][j + 2],
                    self.curve_data[i][j + 3])
                ps.append(tag)
            self.curves_points.append(ps)
        self.transform()  # bugs when transform() called after curves creation
        for i in range(12):
            tag = self.add_curve[self.curve_types[i]](self, i)
            self.curves.append(tag)
        for i in range(6):
            if self.factory == gmsh.model.geo:
                tag = self.factory.addCurveLoop(
                    map(lambda x, y: y * self.curves[x],
                        self.surface_curves[i],
                        self.surface_curves_sign[i]))
                tag = self.factory.addSurfaceFilling([tag])
            else:
                tag = self.factory.addCurveLoop(
                    map(lambda x: self.curves[x],
                        self.surface_curves[i]))
                tag = self.factory.addSurfaceFilling(tag)
            self.surfaces.append(tag)
        tag = self.factory.addSurfaceLoop(self.surfaces)
        tag = self.factory.addVolume([tag])
        self.volumes.append(tag)
        self.factory.synchronize()

    @staticmethod
    def boolean(factory, obj, tool, remove_tool=True):
        obj_dim_tags = zip([3] * len(obj.volumes), obj.volumes)
        tool_dim_tags = zip([3] * len(tool.volumes), tool.volumes)
        # print(obj.volumes)
        # print(tool.volumes)
        out1, out2 = factory.fragment(
            obj_dim_tags,
            tool_dim_tags,
            tag=-1,
            removeObject=True,
            removeTool=remove_tool
        )
        # print(out1)
        # print(out2)
        new_obj_volumes = []
        for i in range(len(obj.volumes)):
            new_dims_tags = out2[i]
            for j in range(len(new_dims_tags)):
                new_obj_volumes.append(new_dims_tags[j][1])
        # print(new_obj_volumes)
        new_tool_volumes = []
        for i in range(len(obj.volumes), len(obj.volumes) + len(tool.volumes)):
            new_dims_tags = out2[i]
            for j in range(len(new_dims_tags)):
                new_tool_volumes.append(new_dims_tags[j][1])
        # print(new_tool_volumes)
        common_vs = set(new_obj_volumes) & set(new_tool_volumes)
        # print(common_vs)
        for v in common_vs:
            new_obj_volumes.remove(v)
        # print(new_obj_volumes)
        obj.volumes = new_obj_volumes
        tool.volumes = new_tool_volumes
        # print(obj.volumes)
        # print(tool.volumes)
