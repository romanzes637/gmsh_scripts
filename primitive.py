import gmsh


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
        ),
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

    def __init__(self, data, transform, curve_types, curve_data,
                 transfinite_curve_data=None, transfinite_type=None,
                 factory=gmsh.model.geo):
        self.data = data
        self.transform = transform
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

    def __transform(self):
        dim_tags = zip([0] * len(self.points), self.points)
        for curve_points in self.curves_points:
            dim_tags += zip([0] * len(curve_points), curve_points)
        self.factory.translate(
            dim_tags, self.transform[0], self.transform[1], self.transform[2]
        )
        self.factory.rotate(dim_tags,
                            self.transform[3], self.transform[4], self.transform[5],
                            1, 0, 0, self.transform[6])
        self.factory.rotate(dim_tags,
                            self.transform[3], self.transform[4], self.transform[5],
                            0, 1, 0, self.transform[7])
        self.factory.rotate(dim_tags,
                            self.transform[3], self.transform[4], self.transform[5],
                            0, 0, 1, self.transform[8])

    def get_surfaces(self, combined=False, oriented=False, recursive=False):
        dim_tags = zip([3] * len(self.volumes), self.volumes)
        surface_dim_tags = gmsh.model.getBoundary(
            dim_tags, combined=combined, oriented=oriented, recursive=recursive
        )
        return surface_dim_tags

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
        self.__transform()  # bugs when __transform() called after curves creation
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
                # tag = self.factory.addCurveLoop(
                #     map(lambda x, y: y * self.curves[x],
                #         self.surface_curves[i],
                #         self.surface_curves_sign[i]))
                tag = self.factory.addCurveLoop(
                    map(lambda x: self.curves[x],
                        self.surface_curves[i]))
                tag = self.factory.addSurfaceFilling(tag)
            self.surfaces.append(tag)
        tag = self.factory.addSurfaceLoop(self.surfaces)
        tag = self.factory.addVolume([tag])
        self.volumes.append(tag)
        self.factory.synchronize()
