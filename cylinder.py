import gmsh
from primitive import Primitive
import math


class Cylinder:
    surface_names = {
        0: "Internal",
        1: "Lateral",
        2: "Bottom",
        3: "Up"
    }

    to_primitive_surface = [
        [0, 2, 1, 3, None],  # X, Y, NX, NY, Core
        [1, 3, 0, 2, None],  # X, Y, NX, NY, Core
        [4, 4, 4, 4, 4],  # X, Y, NX, NY, Core
        [5, 5, 5, 5, 5]  # X, Y, NX, NY, Core
    ]

    def __init__(self, lcs, radii, heights, k, transform, transfinite_curve_data=None):
        self.lcs = lcs
        self.radii = radii
        self.heights = heights
        self.k = k
        self.transform = transform
        self.transfinite_curve_data = transfinite_curve_data
        self.transfinite_types = [0, 0, 0, 1, 3]
        self.primitives = []
        # Initialisation
        h_cnt = 0
        for i in range(len(self.heights)):
            r = self.radii[0] * math.sqrt(2)
            kr = self.k * self.radii[0] * math.sqrt(2)
            h = float(self.heights[i])
            h_cnt += h / 2
            # Core center
            self.primitives.append(Primitive(
                [
                    kr, kr, -h / 2, self.lcs[0],
                    -kr, kr, -h / 2, self.lcs[0],
                    -kr, -kr, -h / 2, self.lcs[0],
                    kr, -kr, -h / 2, self.lcs[0],
                    kr, kr, h / 2, self.lcs[0],
                    -kr, kr, h / 2, self.lcs[0],
                    -kr, -kr, h / 2, self.lcs[0],
                    kr, -kr, h / 2, self.lcs[0]
                ],
                [
                    self.transform[0], self.transform[1], self.transform[2] + h_cnt,
                    self.transform[3], self.transform[4], self.transform[5],
                    self.transform[6], self.transform[7], self.transform[8],
                ],
                [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                [[], [], [], [], [], [], [], [], [], [], [], []],
                [
                    self.transfinite_curve_data[0],
                    self.transfinite_curve_data[0],
                    self.transfinite_curve_data[0],
                    self.transfinite_curve_data[0],
                    self.transfinite_curve_data[0],
                    self.transfinite_curve_data[0],
                    self.transfinite_curve_data[0],
                    self.transfinite_curve_data[0],
                    self.transfinite_curve_data[2][i],
                    self.transfinite_curve_data[2][i],
                    self.transfinite_curve_data[2][i],
                    self.transfinite_curve_data[2][i],
                ],
                self.transfinite_types[0]
            ))
            # Core X
            self.primitives.append(Primitive(
                [
                    r, r, -h / 2, self.lcs[0],
                    kr, kr, -h / 2, self.lcs[0],
                    kr, -kr, -h / 2, self.lcs[0],
                    r, -r, -h / 2, self.lcs[0],
                    r, r, h / 2, self.lcs[0],
                    kr, kr, h / 2, self.lcs[0],
                    kr, -kr, h / 2, self.lcs[0],
                    r, -r, h / 2, self.lcs[0]
                ],
                [
                    self.transform[0], self.transform[1], self.transform[2] + h_cnt,
                    self.transform[3], self.transform[4], self.transform[5],
                    self.transform[6], self.transform[7], self.transform[8],
                ],
                [0, 0, 0, 0, 1, 0, 0, 1, 0, 0, 0, 0],
                [
                    [], [], [], [],
                    [0, 0, -h / 2, 1], [], [], [0, 0, h / 2, 1],
                    [], [], [], []
                ],
                [
                    self.transfinite_curve_data[1][0],
                    self.transfinite_curve_data[1][0],
                    self.transfinite_curve_data[1][0],
                    self.transfinite_curve_data[1][0],
                    self.transfinite_curve_data[0],
                    self.transfinite_curve_data[0],
                    self.transfinite_curve_data[0],
                    self.transfinite_curve_data[0],
                    self.transfinite_curve_data[2][i],
                    self.transfinite_curve_data[2][i],
                    self.transfinite_curve_data[2][i],
                    self.transfinite_curve_data[2][i],
                ],
                self.transfinite_types[1]
            ))
            # Core Y
            self.primitives.append(Primitive(
                [
                    r, r, -h / 2, self.lcs[0],
                    -r, r, -h / 2, self.lcs[0],
                    -kr, kr, -h / 2, self.lcs[0],
                    kr, kr, -h / 2, self.lcs[0],
                    r, r, h / 2, self.lcs[0],
                    -r, r, h / 2, self.lcs[0],
                    -kr, kr, h / 2, self.lcs[0],
                    kr, kr, h / 2, self.lcs[0]
                ],
                [
                    self.transform[0], self.transform[1], self.transform[2] + h_cnt,
                    self.transform[3], self.transform[4], self.transform[5],
                    self.transform[6], self.transform[7], self.transform[8],
                ],
                [1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                [
                    [0, 0, -h / 2, 1], [0, 0, h / 2, 1], [], [],
                    [], [], [], [],
                    [], [], [], []
                ],
                [
                    self.transfinite_curve_data[0],
                    self.transfinite_curve_data[0],
                    self.transfinite_curve_data[0],
                    self.transfinite_curve_data[0],
                    self.transfinite_curve_data[1][0],
                    self.transfinite_curve_data[1][0],
                    self.transfinite_curve_data[1][0],
                    self.transfinite_curve_data[1][0],
                    self.transfinite_curve_data[2][i],
                    self.transfinite_curve_data[2][i],
                    self.transfinite_curve_data[2][i],
                    self.transfinite_curve_data[2][i],
                ],
                self.transfinite_types[2]
            ))
            # Core NX
            if self.transfinite_curve_data[1][0][1] == 0:
                k3 = 1 / self.transfinite_curve_data[1][0][2]
            else:
                k3 = self.transfinite_curve_data[1][0][2]
            self.primitives.append(Primitive(
                [
                    -kr, kr, -h / 2, self.lcs[0],
                    -r, r, -h / 2, self.lcs[0],
                    -r, -r, -h / 2, self.lcs[0],
                    -kr, -kr, -h / 2, self.lcs[0],
                    -kr, kr, h / 2, self.lcs[0],
                    -r, r, h / 2, self.lcs[0],
                    -r, -r, h / 2, self.lcs[0],
                    -kr, -kr, h / 2, self.lcs[0],
                ],
                [
                    self.transform[0], self.transform[1], self.transform[2] + h_cnt,
                    self.transform[3], self.transform[4], self.transform[5],
                    self.transform[6], self.transform[7], self.transform[8],
                ],
                [0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0],
                [
                    [], [], [], [],
                    [], [0, 0, -h / 2, 1], [0, 0, h / 2, 1], [],
                    [], [], [], []
                ],
                [
                    [
                        self.transfinite_curve_data[1][0][0],
                        self.transfinite_curve_data[1][0][1],
                        k3
                    ],
                    [
                        self.transfinite_curve_data[1][0][0],
                        self.transfinite_curve_data[1][0][1],
                        k3
                    ],
                    [
                        self.transfinite_curve_data[1][0][0],
                        self.transfinite_curve_data[1][0][1],
                        k3
                    ],
                    [
                        self.transfinite_curve_data[1][0][0],
                        self.transfinite_curve_data[1][0][1],
                        k3
                    ],
                    self.transfinite_curve_data[0],
                    self.transfinite_curve_data[0],
                    self.transfinite_curve_data[0],
                    self.transfinite_curve_data[0],
                    self.transfinite_curve_data[2][i],
                    self.transfinite_curve_data[2][i],
                    self.transfinite_curve_data[2][i],
                    self.transfinite_curve_data[2][i],
                ],
                self.transfinite_types[3]
            ))
            # Core NY
            if self.transfinite_curve_data[1][0][1] == 0:
                k3 = 1 / self.transfinite_curve_data[1][0][2]
            else:
                k3 = self.transfinite_curve_data[1][0][2]
            self.primitives.append(Primitive(
                [
                    kr, -kr, -h / 2, self.lcs[0],
                    -kr, -kr, -h / 2, self.lcs[0],
                    -r, -r, -h / 2, self.lcs[0],
                    r, -r, -h / 2, self.lcs[0],
                    kr, -kr, h / 2, self.lcs[0],
                    -kr, -kr, h / 2, self.lcs[0],
                    -r, -r, h / 2, self.lcs[0],
                    r, -r, h / 2, self.lcs[0],
                ],
                [
                    self.transform[0], self.transform[1], self.transform[2] + h_cnt,
                    self.transform[3], self.transform[4], self.transform[5],
                    self.transform[6], self.transform[7], self.transform[8],
                ],
                [0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0],
                [
                    [], [], [0, 0, h / 2, 1], [0, 0, -h / 2, 1],
                    [], [], [], [],
                    [], [], [], []
                ],
                [
                    self.transfinite_curve_data[0],
                    self.transfinite_curve_data[0],
                    self.transfinite_curve_data[0],
                    self.transfinite_curve_data[0],
                    [
                        self.transfinite_curve_data[1][0][0],
                        self.transfinite_curve_data[1][0][1],
                        k3
                    ],
                    [
                        self.transfinite_curve_data[1][0][0],
                        self.transfinite_curve_data[1][0][1],
                        k3
                    ],
                    [
                        self.transfinite_curve_data[1][0][0],
                        self.transfinite_curve_data[1][0][1],
                        k3
                    ],
                    [
                        self.transfinite_curve_data[1][0][0],
                        self.transfinite_curve_data[1][0][1],
                        k3
                    ],
                    self.transfinite_curve_data[2][i],
                    self.transfinite_curve_data[2][i],
                    self.transfinite_curve_data[2][i],
                    self.transfinite_curve_data[2][i],
                ],
                self.transfinite_types[4]
            ))
            # Layers
            for j in range(1, len(self.radii)):
                r1 = self.radii[j - 1] * math.sqrt(2)
                r2 = self.radii[j] * math.sqrt(2)
                # Layer X
                self.primitives.append(Primitive(
                    [
                        r2, r2, -h / 2, self.lcs[j],
                        r1, r1, -h / 2, self.lcs[j],
                        r1, -r1, -h / 2, self.lcs[j],
                        r2, -r2, -h / 2, self.lcs[j],
                        r2, r2, h / 2, self.lcs[j],
                        r1, r1, h / 2, self.lcs[j],
                        r1, -r1, h / 2, self.lcs[j],
                        r2, -r2, h / 2, self.lcs[j]
                    ],
                    [
                        self.transform[0], self.transform[1], self.transform[2] + h_cnt,
                        self.transform[3], self.transform[4], self.transform[5],
                        self.transform[6], self.transform[7], self.transform[8],
                    ],
                    [0, 0, 0, 0, 1, 1, 1, 1, 0, 0, 0, 0],
                    [
                        [], [], [], [],
                        [0, 0, -h / 2, 1], [0, 0, -h / 2, 1], [0, 0, h / 2, 1], [0, 0, h / 2, 1],
                        [], [], [], []
                    ],
                    [
                        self.transfinite_curve_data[1][j],
                        self.transfinite_curve_data[1][j],
                        self.transfinite_curve_data[1][j],
                        self.transfinite_curve_data[1][j],
                        self.transfinite_curve_data[0],
                        self.transfinite_curve_data[0],
                        self.transfinite_curve_data[0],
                        self.transfinite_curve_data[0],
                        self.transfinite_curve_data[2][i],
                        self.transfinite_curve_data[2][i],
                        self.transfinite_curve_data[2][i],
                        self.transfinite_curve_data[2][i],
                    ],
                    self.transfinite_types[1]
                ))
                # Layer Y
                self.primitives.append(Primitive(
                    [
                        r2, r2, -h / 2, self.lcs[j],
                        -r2, r2, -h / 2, self.lcs[j],
                        -r1, r1, -h / 2, self.lcs[j],
                        r1, r1, -h / 2, self.lcs[j],
                        r2, r2, h / 2, self.lcs[j],
                        -r2, r2, h / 2, self.lcs[j],
                        -r1, r1, h / 2, self.lcs[j],
                        r1, r1, h / 2, self.lcs[j]
                    ],
                    [
                        self.transform[0], self.transform[1], self.transform[2] + h_cnt,
                        self.transform[3], self.transform[4], self.transform[5],
                        self.transform[6], self.transform[7], self.transform[8],
                    ],
                    [1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0],
                    [
                        [0, 0, -h / 2, 1], [0, 0, h / 2, 1], [0, 0, h / 2, 1], [0, 0, -h / 2, 1],
                        [], [], [], [],
                        [], [], [], []
                    ],
                    [
                        self.transfinite_curve_data[0],
                        self.transfinite_curve_data[0],
                        self.transfinite_curve_data[0],
                        self.transfinite_curve_data[0],
                        self.transfinite_curve_data[1][j],
                        self.transfinite_curve_data[1][j],
                        self.transfinite_curve_data[1][j],
                        self.transfinite_curve_data[1][j],
                        self.transfinite_curve_data[2][i],
                        self.transfinite_curve_data[2][i],
                        self.transfinite_curve_data[2][i],
                        self.transfinite_curve_data[2][i],
                    ],
                    self.transfinite_types[2]
                ))
                # Layer NX
                if self.transfinite_curve_data[1][j][1] == 0:
                    k3 = 1 / self.transfinite_curve_data[1][j][2]
                else:
                    k3 = self.transfinite_curve_data[1][j][2]
                self.primitives.append(Primitive(
                    [
                        -r1, r1, -h / 2, self.lcs[j],
                        -r2, r2, -h / 2, self.lcs[j],
                        -r2, -r2, -h / 2, self.lcs[j],
                        -r1, -r1, -h / 2, self.lcs[j],
                        -r1, r1, h / 2, self.lcs[j],
                        -r2, r2, h / 2, self.lcs[j],
                        -r2, -r2, h / 2, self.lcs[j],
                        -r1, -r1, h / 2, self.lcs[j],
                    ],
                    [
                        self.transform[0], self.transform[1], self.transform[2] + h_cnt,
                        self.transform[3], self.transform[4], self.transform[5],
                        self.transform[6], self.transform[7], self.transform[8],
                    ],
                    [0, 0, 0, 0, 1, 1, 1, 1, 0, 0, 0, 0],
                    [
                        [], [], [], [],
                        [0, 0, -h / 2, 1], [0, 0, -h / 2, 1], [0, 0, h / 2, 1], [0, 0, h / 2, 1],
                        [], [], [], []
                    ],
                    [
                        [
                            self.transfinite_curve_data[1][j][0],
                            self.transfinite_curve_data[1][j][1],
                            k3
                        ],
                        [
                            self.transfinite_curve_data[1][j][0],
                            self.transfinite_curve_data[1][j][1],
                            k3
                        ],
                        [
                            self.transfinite_curve_data[1][j][0],
                            self.transfinite_curve_data[1][j][1],
                            k3
                        ],
                        [
                            self.transfinite_curve_data[1][j][0],
                            self.transfinite_curve_data[1][j][1],
                            k3
                        ],
                        self.transfinite_curve_data[0],
                        self.transfinite_curve_data[0],
                        self.transfinite_curve_data[0],
                        self.transfinite_curve_data[0],
                        self.transfinite_curve_data[2][i],
                        self.transfinite_curve_data[2][i],
                        self.transfinite_curve_data[2][i],
                        self.transfinite_curve_data[2][i],
                    ],
                    self.transfinite_types[3]
                ))
                # Layer NY
                if self.transfinite_curve_data[1][j][1] == 0:
                    k3 = 1 / self.transfinite_curve_data[1][j][2]
                else:
                    k3 = self.transfinite_curve_data[1][j][2]
                self.primitives.append(Primitive(
                    [
                        r1, -r1, -h / 2, self.lcs[j],
                        -r1, -r1, -h / 2, self.lcs[j],
                        -r2, -r2, -h / 2, self.lcs[j],
                        r2, -r2, -h / 2, self.lcs[j],
                        r1, -r1, h / 2, self.lcs[j],
                        -r1, -r1, h / 2, self.lcs[j],
                        -r2, -r2, h / 2, self.lcs[j],
                        r2, -r2, h / 2, self.lcs[j],
                    ],
                    [
                        self.transform[0], self.transform[1], self.transform[2] + h_cnt,
                        self.transform[3], self.transform[4], self.transform[5],
                        self.transform[6], self.transform[7], self.transform[8],
                    ],
                    [1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0],
                    [
                        [0, 0, -h / 2, 1], [0, 0, h / 2, 1], [0, 0, h / 2, 1], [0, 0, -h / 2, 1],
                        [], [], [], [],
                        [], [], [], []
                    ],
                    [
                        self.transfinite_curve_data[0],
                        self.transfinite_curve_data[0],
                        self.transfinite_curve_data[0],
                        self.transfinite_curve_data[0],
                        [
                            self.transfinite_curve_data[1][j][0],
                            self.transfinite_curve_data[1][j][1],
                            k3
                        ],
                        [
                            self.transfinite_curve_data[1][j][0],
                            self.transfinite_curve_data[1][j][1],
                            k3
                        ],
                        [
                            self.transfinite_curve_data[1][j][0],
                            self.transfinite_curve_data[1][j][1],
                            k3
                        ],
                        [
                            self.transfinite_curve_data[1][j][0],
                            self.transfinite_curve_data[1][j][1],
                            k3
                        ],
                        self.transfinite_curve_data[2][i],
                        self.transfinite_curve_data[2][i],
                        self.transfinite_curve_data[2][i],
                        self.transfinite_curve_data[2][i],
                    ],
                    self.transfinite_types[4]
                ))
            h_cnt += h / 2

    def create(self):
        for primitive in self.primitives:
            primitive.create()

    def transfinite(self):
        for primitive in self.primitives:
            primitive.transfinite()

    def set_layer_volume_physical_group(self, height_idx, radius_idx, tag):
        start_idx = height_idx * (len(self.radii) * 4 + 1) + radius_idx * 4 + 1
        for i in range(start_idx, start_idx + 4):
            self.primitives[i].volumes_physical_groups[0] = tag
        if radius_idx == 0:
            self.primitives[start_idx - 1].volumes_physical_groups[0] = tag

    def set_layer_surface_physical_group(self, height_idx, radius_idx, surface_idx, tag):
        start_idx = height_idx * (len(self.radii) * 4 + 1) + radius_idx * 4 + 1
        for i in range(start_idx, start_idx + 4):
            idx = self.to_primitive_surface[surface_idx][i - start_idx]
            self.primitives[i].surfaces_physical_groups[idx] = tag
        if radius_idx == 0:
            idx = self.to_primitive_surface[surface_idx][4]
            self.primitives[start_idx-1].surfaces_physical_groups[idx] = tag


# Before using any functions in the Python API, Gmsh must be initialized.
gmsh.initialize()

gmsh.option.setNumber("Geometry.AutoCoherence", 0)

# By default Gmsh will not print out any messages: in order to output messages
# on the terminal, just set the standard Gmsh option "General.Terminal" (same
# format and meaning as in .geo files) using gmshOptionSetNumber():
gmsh.option.setNumber("General.Terminal", 1)

# This creates a new model, named "t1". If gmshModelCreate() is not called, a
# new default (unnamed) model will be created on the fly, if necessary.
gmsh.model.add("cylinder")

#factory = gmsh.model.occ
factory = gmsh.model.geo

cylinder = Cylinder(
    [1, 1, 1],
    [1, 2, 3],
    [3, 4, 5],
    0.3,
    # [1, 2, 3, 0, 0, 0, 3.14/2, -3.14/4, 3.14/6],
    [0, 0, 0, 0, 0, 0, 0, 0, 0],
    [
        [5, 0, 1],
        [
            [6, 0, 1.2],
            [7, 1, 0.2],
            [8, 0, 1.3]
        ],
        [
            [15, 1, 0.4],
            [16, 0, 1.2],
            [17, 1, 0.3]
        ]
    ]
)

cylinder.create()

volume_groups = {
    0: "V0",
    1: "V1",
    2: "V2"
}
cylinder.set_layer_volume_physical_group(0, 0, 0)
cylinder.set_layer_volume_physical_group(0, 1, 0)
cylinder.set_layer_volume_physical_group(0, 2, 0)
cylinder.set_layer_volume_physical_group(1, 0, 1)
cylinder.set_layer_volume_physical_group(1, 1, 1)
cylinder.set_layer_volume_physical_group(1, 2, 1)
cylinder.set_layer_volume_physical_group(2, 0, 2)
cylinder.set_layer_volume_physical_group(2, 1, 2)
cylinder.set_layer_volume_physical_group(2, 2, 2)
for key, value in volume_groups.items():
    tags = []
    for p in cylinder.primitives:
        if p.volumes_physical_groups[0] == key:
            tags.append(p.volumes[0])
    group_tag = gmsh.model.addPhysicalGroup(3, tags)
    gmsh.model.setPhysicalName(3, group_tag, value)

surface_groups = {
    0: "S0",
    1: "S1",
    2: "S2",
    3: "S3"
}
cylinder.set_layer_surface_physical_group(0, 0, 2, 2)
cylinder.set_layer_surface_physical_group(0, 1, 2, 2)
cylinder.set_layer_surface_physical_group(0, 2, 2, 2)
cylinder.set_layer_surface_physical_group(0, 2, 1, 0)
cylinder.set_layer_surface_physical_group(1, 2, 1, 0)
cylinder.set_layer_surface_physical_group(2, 2, 1, 0)
cylinder.set_layer_surface_physical_group(2, 0, 3, 3)
cylinder.set_layer_surface_physical_group(2, 1, 3, 3)
cylinder.set_layer_surface_physical_group(2, 2, 3, 3)
for key, value in surface_groups.items():
    tags = []
    for p in cylinder.primitives:
        for k in range(len(p.surfaces_physical_groups)):
            if p.surfaces_physical_groups[k] == key:
                tags.append(p.surfaces[k])
    group_tag = gmsh.model.addPhysicalGroup(2, tags)
    gmsh.model.setPhysicalName(2, group_tag, value)


cylinder.transfinite()

factory.removeAllDuplicates()

# We can then generate a 2D mesh...
gmsh.model.mesh.generate(3)

gmsh.model.mesh.removeDuplicateNodes()

# ... and save it to disk
gmsh.write("cylinder.msh")

# This should be called at the end:
gmsh.finalize()
