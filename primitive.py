import gmsh


class Primitive:
    data = []
    origin = []
    rotation = []
    curve_types = []
    curve_data = []
    points = []
    curve_points = []
    curves = []
    surfaces = []
    volumes = []
    line_points = [
        [1, 0], [5, 4], [6, 7], [2, 3],
        [3, 0], [2, 1], [6, 5], [7, 4],
        [0, 4], [1, 5], [2, 6], [3, 7]
    ]
    surface_lines = [
        [5, 9, 6, 10],
        [4, 11, 7, 8],
        [3, 10, 2, 11],
        [0, 8, 1, 9],
        [0, 5, 3, 4],
        [1, 7, 2, 6]
    ]
    surface_lines_sign = [
        [1, 1, -1, -1],
        [-1, 1, 1, -1],
        [-1, 1, 1, -1],
        [1, 1, -1, -1],
        [-1, -1, 1, 1],
        [1, -1, -1, 1]
    ]
    transfinite_data = []
    transfinite_surface_data = []
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
        )
    }
    transfinite_surface = {
        0: lambda self, i: gmsh.model.mesh.setTransfiniteSurface(
            self.surfaces[i],
            "Left"
        ),
        1: lambda self, i: gmsh.model.mesh.setTransfiniteSurface(
            self.surfaces[i],
            "Right"
        ),
        2: lambda self, i: gmsh.model.mesh.setTransfiniteSurface(
            self.surfaces[i],
            "AlternateLeft"
        ),
        3: lambda self, i: gmsh.model.mesh.setTransfiniteSurface(
            self.surfaces[i],
            "AlternateRight"
        )
    }
    add_curve = {
        0: lambda self, i: gmsh.model.geo.addLine(
            self.points[self.line_points[i][0]],
            self.points[self.line_points[i][1]]
        ),
        1: lambda self, i: gmsh.model.geo.addCircleArc(
            self.points[self.line_points[i][0]],
            self.curve_points[i][0],
            self.points[self.line_points[i][1]]
        ),
        2: lambda self, i: gmsh.model.geo.addEllipseArc(
            self.points[self.line_points[i][0]],
            self.curve_points[i][0],
            self.curve_points[i][1],
            self.points[self.line_points[i][1]],
        ),
        3: lambda self, i: gmsh.model.geo.addSpline(
            [self.points[self.line_points[i][0]]] +
            self.curve_points[i] +
            [self.points[self.line_points[i][1]]]
        ),
        4: lambda self, i: gmsh.model.geo.addBSpline(
            [self.points[self.line_points[i][0]]] +
            self.curve_points[i] +
            [self.points[self.line_points[i][1]]]
        ),
        5: lambda self, i: gmsh.model.geo.addBezier(
            [self.points[self.line_points[i][0]]] +
            self.curve_points[i] +
            [self.points[self.line_points[i][1]]]
        )
    }

    def __init__(self, data, origin, rotation, curve_types, curve_data, transfinite_data, transfinite_surface_data):
        self.data = data
        self.origin = origin
        self.rotation = rotation
        self.curve_types = curve_types
        self.curve_data = curve_data
        self.transfinite_data = transfinite_data
        self.transfinite_surface_data = transfinite_surface_data

    def recombine(self):
        for i in range(6):
            gmsh.model.mesh.setRecombine(2, self.surfaces[i])

    def smooth(self, n):
        for i in range(6):
            gmsh.model.mesh.setSmoothing(2, self.surfaces[i], n)

    def transfinite(self):
        for i in range(12):
            self.transfinite_curve[self.transfinite_data[i][1]](self, i)
        for i in range(6):
            self.transfinite_surface[self.transfinite_surface_data[i]](self, i)
        for i in range(len(self.volumes)):
            gmsh.model.mesh.setTransfiniteVolume(self.volumes[i])

    def create(self):
        for i in range(0, len(self.data), 4):
            tag = gmsh.model.geo.addPoint(
                self.data[i],
                self.data[i + 1],
                self.data[i + 2],
                self.data[i + 3])
            self.points.append(tag)
        for i in range(0, len(self.curve_data)):
            ps = []
            for j in range(0, len(self.curve_data[i]), 4):
                tag = gmsh.model.geo.addPoint(
                    self.curve_data[i][j],
                    self.curve_data[i][j + 1],
                    self.curve_data[i][j + 2],
                    self.curve_data[i][j + 3])
                ps.append(tag)
            self.curve_points.append(ps)
        # gmsh.model.geo.translate(self.points, self.origin[0], self.origin[1], self.origin[2])
        # gmsh.model.geo.rotate(self.points, self.rotation[0], self.rotation[1],
        #                       self.rotation[2], 1, 0, 0, self.rotation[3])
        # gmsh.model.geo.rotate(self.points, self.rotation[0], self.rotation[1],
        #                       self.rotation[2], 0, 1, 0, self.rotation[4])
        # gmsh.model.geo.rotate(self.points, self.rotation[0], self.rotation[1],
        #                       self.rotation[2], 0, 0, 1, self.rotation[5])
        # for i in range(0, len(self.curve_points)):
        #     gmsh.model.geo.translate(self.curve_points[i], self.origin[0], self.origin[1], self.origin[2])
        #     gmsh.model.geo.rotate(self.curve_points[i], self.rotation[0],
        #                           self.rotation[1], self.rotation[2], 1, 0, 0, self.rotation[3])
        #     gmsh.model.geo.rotate(self.curve_points[i], self.rotation[0], self.rotation[1], self.rotation[2], 0, 1, 0,
        #                           self.rotation[4])
        #     gmsh.model.geo.rotate(self.curve_points[i], self.rotation[0], self.rotation[1], self.rotation[2], 0, 0, 1,
        #                           self.rotation[5])
        for i in range(12):
            tag = self.add_curve[self.curve_types[i]](self, i)
            self.curves.append(tag)
        for i in range(6):
            tag = gmsh.model.geo.addCurveLoop(
                map(lambda x, y: y * self.curves[x],
                    self.surface_lines[i], self.surface_lines_sign[i]))
            tag = gmsh.model.geo.addSurfaceFilling([tag])
            self.surfaces.append(tag)
        tag = gmsh.model.geo.addSurfaceLoop(self.surfaces)
        tag = gmsh.model.geo.addVolume([tag])
        self.volumes.append(tag)


# Before using any functions in the Python API, Gmsh must be initialized.
gmsh.initialize()

# gmsh.option.setNumber("Geometry.AutoCoherence", 0)

# By default Gmsh will not print out any messages: in order to output messages
# on the terminal, just set the standard Gmsh option "General.Terminal" (same
# format and meaning as in .geo files) using gmshOptionSetNumber():
gmsh.option.setNumber("General.Terminal", 1)

# This creates a new model, named "t1". If gmshModelCreate() is not called, a
# new default (unnamed) model will be created on the fly, if necessary.
gmsh.model.add("primitive")

p = Primitive(
    [
        5, 10, -15, 1,
        -5, 10, -15, 1,
        -5, -10, -15, 1,
        5, -10, -15, 1,
        5, 10, 15, 1,
        -5, 10, 15, 1,
        -5, -10, 15, 1,
        5, -10, 15, 1,
    ],
    [5, 0, 0],
    [0, 3, 4, 1, 3, 4],
    [3, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [
        [
            0, 0, 0, 1,
            1, 0, 0, 1,
            2, 0, 0, 1,
            3, 0, 0, 1
        ],
        [0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0],
    ],
    [
        [15, 1, 1.2],
        [15, 1, 1.2],
        [15, 1, 1.2],
        [15, 1, 1.2],
        [10, 0, 1.3],
        [10, 0, 1.3],
        [10, 0, 1.3],
        [10, 0, 1.3],
        [5, 1, 1.4],
        [5, 1, 1.4],
        [5, 1, 1.4],
        [5, 1, 1.4]
    ],
    [0, 0, 0, 0, 1, 1]
)

p.create()

gmsh.model.geo.synchronize()

p.transfinite()

# p.recombine()

gmsh.model.geo.removeAllDuplicates()

# We can then generate a 2D mesh...
gmsh.model.mesh.generate(3)

# p.smooth(100)

# ... and save it to disk
gmsh.write("primitive.msh")

# This should be called at the end:
gmsh.finalize()



# lines: 0 - straight, 1 - circle, 2 - ellipse, 3 - Bezier, 4 - BSpline, 5 + - Spline
# primitive_t_6 = 0; // Type
# primitive_t_7s = {}; // Inner
# Surfaces
# primitive_t_8s = {0, 0, 0, 0, 0, 0}; // Surfaces
# for changes
#     primitive_t_9s = {}; // Rotations
# primitive_t_10s = {0, 0, 0, 0, 0, 0}; // Plane
# Surface?
