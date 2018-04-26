import gmsh

import unittest
import itertools

from primitive import Environment
from primitive import Primitive
from primitive import Complex
from primitive import primitive_complex_boolean
from cylinder import Cylinder


class TestScripts(unittest.TestCase):
    def test_primitive_env(self):
        """
        Primitive within Environment
        """
        gmsh.initialize()

        gmsh.option.setNumber("Geometry.AutoCoherence", 0)
        gmsh.option.setNumber("General.Terminal", 1)
        gmsh.option.setNumber("Mesh.Algorithm3D", 4)

        gmsh.model.add("test_primitive_env")

        factory = gmsh.model.geo
        # factory = gmsh.model.occ # TODO Doesn't work with occ because volume with holes is not created

        print("Primitive")
        primitive = Primitive(
            factory,
            [
                5, 10, -15, 5,
                -5, 10, -15, 5,
                -5, -10, -15, 5,
                5, -10, -15, 5,
                5, 10, 15, 5,
                -5, 10, 15, 5,
                -5, -10, 15, 5,
                5, -10, 15, 5,
            ],
            [0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [[], [], [], [], [], [], [], [], [], [], [], []],
            [
                [5, 0, 1], [5, 0, 1], [5, 0, 1], [5, 0, 1],
                [10, 0, 1], [10, 0, 1], [10, 0, 1], [10, 0, 1],
                [15, 0, 1], [15, 0, 1], [15, 0, 1], [15, 0, 1]
            ],
            0
        )

        print("Environment")
        environment = Environment(
            factory, 50, 50, 50, 5, [0, 0, 0, 0, 0, 0, 0, 0, 0], primitive.surfaces)

        print("Physical Groups")
        primitive_fg = gmsh.model.addPhysicalGroup(3, primitive.volumes)
        gmsh.model.setPhysicalName(3, primitive_fg, "Primitive")
        env_fg = gmsh.model.addPhysicalGroup(3, environment.volumes)
        gmsh.model.setPhysicalName(3, env_fg, "Environment")
        s_fgs = []
        for i in range(len(environment.surfaces)):
            s_fgs.append(gmsh.model.addPhysicalGroup(2, [environment.surfaces[i]]))
            gmsh.model.setPhysicalName(2, s_fgs[i], environment.surfaces_names[i])

        print("Transfinite")
        primitive.transfinite()

        print("Remove All Duplicates")
        factory.removeAllDuplicates()

        print("Generate Mesh")
        gmsh.model.mesh.generate(3)

        print("Remove Mesh Duplicate Nodes")
        gmsh.model.mesh.removeDuplicateNodes()

        gmsh.write("test_primitive_env.msh")

        gmsh.finalize()

    def test_mix(self):
        gmsh.initialize()

        gmsh.option.setNumber("Geometry.AutoCoherence", 0)
        gmsh.option.setNumber("General.Terminal", 1)

        gmsh.model.add("test_mix")

        factory = gmsh.model.occ

        environment = Primitive(
            factory,
            [
                50, 60, -70, 10,
                -50, 60, -70, 10,
                -50, -60, -70, 10,
                50, -60, -70, 10,
                50, 60, 70, 10,
                -50, 60, 70, 10,
                -50, -60, 70, 10,
                50, -60, 70, 10,
            ],
            [0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [[], [], [], [], [], [], [], [], [], [], [], []]
        )
        n_primitives = 2
        primitives = []
        for i in range(n_primitives):
            primitives.append(Primitive(
                factory,
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
                [i * 5, i * 5, i * 6, 0, 0, 0, 3.14 * i / 4, 3.14 * i / 6, 3.14 * i / 8],
                [5, 0, 0, 0, 0, 0, 0, 1, 0, 0, 1, 0],
                [
                    [
                        -2, 20, -20, 1,
                        -1, 20, -20, 1,
                        1, 20, -20, 1,
                        2, 20, -20, 1
                    ],
                    [],
                    [],
                    [],
                    [],
                    [],
                    [],
                    [0, 0, 0, 0],
                    [],
                    [],
                    [0, 0, 0, 0, 0, 0, 0, 0],
                    []
                ],
                [
                    [5, 0, 1],
                    [5, 0, 1],
                    [5, 0, 1],
                    [5, 0, 1],
                    [10, 0, 1],
                    [10, 0, 1],
                    [10, 0, 1],
                    [10, 0, 1],
                    [15, 0, 1],
                    [15, 0, 1],
                    [15, 0, 1],
                    [15, 0, 1]
                ],
                1
            ))

        combinations = list(itertools.combinations(range(n_primitives), 2))
        print(combinations)
        for combination in combinations:
            print("Boolean primitive %s by primitive %s" % combination)
            Primitive.boolean(factory, primitives[combination[0]], primitives[combination[1]])

        for idx, primitive in enumerate(primitives):
            print("Boolean environment by borehole %s" % idx)
            Primitive.boolean(factory, environment, primitive)

        environment.set_size(25)
        for idx, primitive in enumerate(primitives):
            primitive.set_size(10)

        print("Physical Volumes")
        v_fgs = []
        for primitive in primitives:
            v_fgs.append(gmsh.model.addPhysicalGroup(3, primitive.volumes))
        for i in range(len(v_fgs)):
            gmsh.model.setPhysicalName(3, v_fgs[i], "V%s" % i)

        env_fg = gmsh.model.addPhysicalGroup(3, environment.volumes)
        gmsh.model.setPhysicalName(3, env_fg, "Environment")

        for primitive in primitives:
            result = primitive.correct_to_transfinite()
            if result:
                primitive.transfinite()

        print("Physical Surfaces")
        volumes_dim_tags = zip([3] * len(environment.volumes), environment.volumes)
        s_dim_tags = gmsh.model.getBoundary(volumes_dim_tags)
        s_fgs = []
        s_fgs_names = ["X", "Y", "NZ", "NY", "Z", "NX"]
        for i in range(6):
            s_fgs.append(gmsh.model.addPhysicalGroup(2, s_dim_tags[i]))
            gmsh.model.setPhysicalName(2, s_fgs[i], s_fgs_names[i])

        gmsh.option.setNumber("Mesh.Algorithm3D", 4)

        factory.removeAllDuplicates()

        gmsh.model.mesh.generate(3)

        gmsh.model.mesh.removeDuplicateNodes()

        gmsh.write("test_mix.msh")
        gmsh.finalize()

    def test_transfinite(self):
        gmsh.initialize()

        gmsh.option.setNumber("Geometry.AutoCoherence", 0)
        gmsh.option.setNumber("General.Terminal", 1)
        gmsh.model.add("test_transfinite")

        factory = gmsh.model.occ

        primitives = []
        for i in range(4):
            primitives.append(Primitive(
                factory,
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
                [30 + i * 15, 0, 0, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                [
                    [
                        -2, 20, -20, 1,
                        -1, 20, -20, 1,
                        1, 20, -20, 1,
                        2, 20, -20, 1
                    ],
                    [],
                    [],
                    [],
                    [],
                    [],
                    [],
                    [0, 0, 0, 0],
                    [],
                    [],
                    [0, 0, 0, 0, 0, 0, 0, 0],
                    []
                ],
                [
                    [5, 0, 1],
                    [5, 0, 1],
                    [5, 0, 1],
                    [5, 0, 1],
                    [10, 0, 1],
                    [10, 0, 1],
                    [10, 0, 1],
                    [10, 0, 1],
                    [15, 0, 1],
                    [15, 0, 1],
                    [15, 0, 1],
                    [15, 0, 1]
                ],
                i
            ))
        for i in range(4):
            primitives.append(Primitive(
                factory,
                [
                    10, 5, -15, 1,
                    -10, 5, -15, 1,
                    -10, -5, -15, 1,
                    10, -5, -15, 1,
                    10, 5, 15, 1,
                    -10, 5, 15, 1,
                    -10, -5, 15, 1,
                    10, -5, 15, 1,
                ],
                [0, 30 + i * 15, 0, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                [
                    [
                        -2, 20, -20, 1,
                        -1, 20, -20, 1,
                        1, 20, -20, 1,
                        2, 20, -20, 1
                    ],
                    [],
                    [],
                    [],
                    [],
                    [],
                    [],
                    [0, 0, 0, 0],
                    [],
                    [],
                    [0, 0, 0, 0, 0, 0, 0, 0],
                    []
                ],
                [
                    [10, 0, 1],
                    [10, 0, 1],
                    [10, 0, 1],
                    [10, 0, 1],
                    [5, 0, 1],
                    [5, 0, 1],
                    [5, 0, 1],
                    [5, 0, 1],
                    [15, 0, 1],
                    [15, 0, 1],
                    [15, 0, 1],
                    [15, 0, 1]
                ],
                i
            ))
        for i in range(4):
            primitives.append(Primitive(
                factory,
                [
                    15, 10, -5, 1,
                    -15, 10, -5, 1,
                    -15, -10, -5, 1,
                    15, -10, -5, 1,
                    15, 10, 5, 1,
                    -15, 10, 5, 1,
                    -15, -10, 5, 1,
                    15, -10, 5, 1,
                ],
                [0, 0, 30 + i * 15, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                [
                    [
                        -2, 20, -20, 1,
                        -1, 20, -20, 1,
                        1, 20, -20, 1,
                        2, 20, -20, 1
                    ],
                    [],
                    [],
                    [],
                    [],
                    [],
                    [],
                    [0, 0, 0, 0],
                    [],
                    [],
                    [0, 0, 0, 0, 0, 0, 0, 0],
                    []
                ],
                [
                    [15, 0, 1],
                    [15, 0, 1],
                    [15, 0, 1],
                    [15, 0, 1],
                    [10, 0, 1],
                    [10, 0, 1],
                    [10, 0, 1],
                    [10, 0, 1],
                    [5, 0, 1],
                    [5, 0, 1],
                    [5, 0, 1],
                    [5, 0, 1]
                ],
                i
            ))

        for primitive in primitives:
            result = primitive.correct_to_transfinite()
            if result:
                primitive.transfinite()

        fgs = []
        for idx, primitive in enumerate(primitives):
            fgs.append(gmsh.model.addPhysicalGroup(3, primitive.volumes))
            gmsh.model.setPhysicalName(3, fgs[idx], "V%s" % idx)
            fsgs = []
            for i in range(len(primitive.surfaces)):
                print(primitive.surfaces[i], primitive.surfaces_names[i])
                fsgs.append(gmsh.model.addPhysicalGroup(2, [primitive.surfaces[i]]))
                gmsh.model.setPhysicalName(2, fsgs[i], "%s%s" % (primitive.surfaces_names[i], idx))

        factory.removeAllDuplicates()

        gmsh.model.mesh.generate(3)

        gmsh.model.mesh.removeDuplicateNodes()

        gmsh.write("test_transfinite.msh")

        gmsh.finalize()

    def test_super_mix(self):
        gmsh.initialize()

        gmsh.option.setNumber("Geometry.AutoCoherence", 0)
        gmsh.option.setNumber("General.Terminal", 1)
        gmsh.model.add("test_super_mix")

        factory = gmsh.model.occ

        environment = Primitive(
            factory,
            [
                100, 100, -100, 100,
                -100, 100, -100, 100,
                -100, -100, -100, 100,
                100, -100, -100, 100,
                100, 100, 100, 100,
                -100, 100, 100, 100,
                -100, -100, 100, 100,
                100, -100, 100, 100
            ],
            [0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [[], [], [], [], [], [], [], [], [], [], [], []]
        )
        n_boreholes = 3
        boreholes = []
        for i in range(n_boreholes):
            boreholes.append(Primitive(
                factory,
                [
                    5, 5, -30, 1,
                    -5, 5, -30, 1,
                    -5, -5, -30, 1,
                    5, -5, -30, 1,
                    5, 5, 30, 1,
                    -5, 5, 30, 1,
                    -5, -5, 30, 1,
                    5, -5, 30, 1
                ],
                [25 * i, 0, 0, 0, 0, 0, 0, 0, 0],
                [1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0],
                [
                    [0, 0, -30, 0],
                    [0, 0, 30, 0],
                    [0, 0, 30, 0],
                    [0, 0, -30, 0],
                    [0, 0, -30, 0],
                    [0, 0, -30, 0],
                    [0, 0, 30, 0],
                    [0, 0, 30, 0],
                    [],
                    [],
                    [],
                    []
                ],
                [
                    [5, 0, 1],
                    [5, 0, 1],
                    [5, 0, 1],
                    [5, 0, 1],
                    [5, 0, 1],
                    [5, 0, 1],
                    [5, 0, 1],
                    [5, 0, 1],
                    [15, 0, 1],
                    [15, 0, 1],
                    [15, 0, 1],
                    [15, 0, 1]
                ],
                1
            ))
        n_primitives = 3
        primitives = []
        for i in range(n_primitives):
            if i == 0:
                primitives.append(Primitive(
                    factory,
                    [
                        5, 10, -15, 1,
                        -5, 10, -15, 1,
                        -5, -10, -15, 1,
                        5, -10, -15, 1,
                        5, 10, 15, 1,
                        -5, 10, 15, 1,
                        -5, -10, 15, 1,
                        5, -10, 15, 1
                    ],
                    [25, 40, -50, 0, 0, 0, 3.14 / 8, 3.14 / 6, 3.14 / 4],
                    [4, 0, 0, 0, 0, 0, 0, 1, 0, 0, 1, 0],
                    [
                        [
                            -2, 20, -20, 1,
                            -1, 20, -20, 1,
                            1, 20, -20, 1,
                            2, 20, -20, 1
                        ],
                        [],
                        [],
                        [],
                        [],
                        [],
                        [],
                        [0, 0, 0, 0],
                        [],
                        [],
                        [0, 0, 0, 0, 0, 0, 0, 0],
                        []
                    ],
                    [
                        [5, 0, 1],
                        [5, 0, 1],
                        [5, 0, 1],
                        [5, 0, 1],
                        [10, 0, 1],
                        [10, 0, 1],
                        [10, 0, 1],
                        [10, 0, 1],
                        [15, 0, 1],
                        [15, 0, 1],
                        [15, 0, 1],
                        [15, 0, 1]
                    ],
                    1
                ))
            else:
                primitives.append(Primitive(
                    factory,
                    [
                        5, 10, -15, 1,
                        -5, 10, -15, 1,
                        -5, -10, -15, 1,
                        5, -10, -15, 1,
                        5, 10, 15, 1,
                        -5, 10, 15, 1,
                        -5, -10, 15, 1,
                        5, -10, 15, 1
                    ],
                    [3 * i, 3 * i, 3 * i, 0, 0, 0, 3.14 * i / 4, 3.14 * i / 6, 3.14 * i / 8],
                    [5, 0, 0, 0, 0, 0, 0, 1, 0, 0, 1, 0],
                    [
                        [
                            -2, 20, -20, 1,
                            -1, 20, -20, 1,
                            1, 20, -20, 1,
                            2, 20, -20, 1
                        ],
                        [],
                        [],
                        [],
                        [],
                        [],
                        [],
                        [0, 0, 0, 0],
                        [],
                        [],
                        [0, 0, 0, 0, 0, 0, 0, 0],
                        []
                    ],
                    [
                        [5, 0, 1],
                        [5, 0, 1],
                        [5, 0, 1],
                        [5, 0, 1],
                        [10, 0, 1],
                        [10, 0, 1],
                        [10, 0, 1],
                        [10, 0, 1],
                        [15, 0, 1],
                        [15, 0, 1],
                        [15, 0, 1],
                        [15, 0, 1]
                    ],
                    1
                ))
        combinations = list(itertools.combinations(range(n_primitives), 2))
        print(combinations)
        for combination in combinations:
            print("Boolean primitive %s by primitive %s" % combination)
            Primitive.boolean(factory, primitives[combination[0]], primitives[combination[1]])
        for idx, borehole in enumerate(boreholes):
            for idx2, primitive in enumerate(primitives):
                print("Boolean primitive %s by borehole %s" % (idx2, idx))
                Primitive.boolean(factory, primitive, borehole)
        for idx, borehole in enumerate(boreholes):
            print("Boolean environment by borehole %s" % idx)
            Primitive.boolean(factory, environment, borehole)
        for idx, primitive in enumerate(primitives):
            print("Boolean environment by primitive %s" % idx)
            Primitive.boolean(factory, environment, primitive)

        environment.set_size(50)
        # FIXME bug then primitive mesh size != borehole mesh size (Not always...)
        for idx, primitive in enumerate(primitives):
            primitive.set_size(10)
        for idx, borehole in enumerate(boreholes):
            borehole.set_size(10)

        print("Physical Volumes")
        v_fgs = []
        for primitive in primitives:
            v_fgs.append(gmsh.model.addPhysicalGroup(3, primitive.volumes))
        for i in range(len(v_fgs)):
            gmsh.model.setPhysicalName(3, v_fgs[i], "V%s" % i)
        borehole_fgs = []
        for borehole in boreholes:
            borehole_fgs.append(gmsh.model.addPhysicalGroup(3, borehole.volumes))
        for i in range(len(borehole_fgs)):
            gmsh.model.setPhysicalName(3, borehole_fgs[i], "Borehole%s" % i)
        env_fg = gmsh.model.addPhysicalGroup(3, environment.volumes)
        gmsh.model.setPhysicalName(3, env_fg, "Environment")

        print("Transfinite")
        for borehole in boreholes:
            result = borehole.correct_to_transfinite()
            if result:
                borehole.transfinite()
        for primitive in primitives:
            result = primitive.correct_to_transfinite()
            if result:
                primitive.transfinite()

        print("Physical Surfaces")
        volumes_dim_tags = zip([3] * len(environment.volumes), environment.volumes)
        s_dim_tags = gmsh.model.getBoundary(volumes_dim_tags)
        s_fgs = []
        s_fgs_names = ["X", "Y", "NZ", "NY", "Z", "NX"]
        for i in range(6):
            s_fgs.append(gmsh.model.addPhysicalGroup(2, s_dim_tags[i]))
            gmsh.model.setPhysicalName(2, s_fgs[i], s_fgs_names[i])

        gmsh.option.setNumber("Mesh.Algorithm3D", 4)

        print("Remove All Duplicates")
        factory.removeAllDuplicates()

        print("Mesh Generate")
        gmsh.model.mesh.generate(3)

        print("Remove Mesh Duplicate Nodes")
        gmsh.model.mesh.removeDuplicateNodes()

        gmsh.write("primitive_test_super_mix.msh")
        gmsh.finalize()

    def test_complex(self):
        gmsh.initialize()

        # gmsh.option.setNumber("Geometry.AutoCoherence", 0)
        gmsh.option.setNumber("General.Terminal", 1)
        gmsh.option.setNumber("Mesh.Algorithm3D", 4)

        gmsh.model.add("test_complex")

        factory = gmsh.model.occ

        # Environment
        environment = Primitive(
            factory,
            [
                100, 100, -100, 10,
                -100, 100, -100, 10,
                -100, -100, -100, 10,
                100, -100, -100, 10,
                100, 100, 100, 10,
                -100, 100, 100, 10,
                -100, -100, 100, 10,
                100, -100, 100, 10
            ],
            [0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [[], [], [], [], [], [], [], [], [], [], [], []]
        )
        environment.create()
        environment.correct_after_occ()
        # Boreholes
        n_boreholes = 3
        boreholes = []
        boreholes_pgs = []
        for i in range(n_boreholes):
            boreholes_pgs.append(0)
            boreholes.append(Primitive(
                factory,
                [
                    5, 5, -30, 1,
                    -5, 5, -30, 1,
                    -5, -5, -30, 1,
                    5, -5, -30, 1,
                    5, 5, 30, 1,
                    -5, 5, 30, 1,
                    -5, -5, 30, 1,
                    5, -5, 30, 1
                ],
                [25 * i, 0, 0, 0, 0, 0, 0, 0, 0],
                [1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0],
                [
                    [0, 0, -30, 0],
                    [0, 0, 30, 0],
                    [0, 0, 30, 0],
                    [0, 0, -30, 0],
                    [0, 0, -30, 0],
                    [0, 0, -30, 0],
                    [0, 0, 30, 0],
                    [0, 0, 30, 0],
                    [],
                    [],
                    [],
                    []
                ],
                [
                    [5, 0, 1],
                    [5, 0, 1],
                    [5, 0, 1],
                    [5, 0, 1],
                    [5, 0, 1],
                    [5, 0, 1],
                    [5, 0, 1],
                    [5, 0, 1],
                    [15, 0, 1],
                    [15, 0, 1],
                    [15, 0, 1],
                    [15, 0, 1]
                ],
                1
            ))
            boreholes[i].create()
            boreholes[i].correct_after_occ()
        complex_boreholes = Complex(factory, boreholes, boreholes_pgs)
        # Intrusions
        n_intrusions = 3
        intrusions = []
        intrusions_pgs = []
        for i in range(n_intrusions):
            intrusions_pgs.append(1)
            if i == 0:
                intrusions.append(Primitive(
                    factory,
                    [
                        5, 10, -15, 1,
                        -5, 10, -15, 1,
                        -5, -10, -15, 1,
                        5, -10, -15, 1,
                        5, 10, 15, 1,
                        -5, 10, 15, 1,
                        -5, -10, 15, 1,
                        5, -10, 15, 1
                    ],
                    [25, 40, -50, 0, 0, 0, 3.14 / 8, 3.14 / 6, 3.14 / 4],
                    [4, 0, 0, 0, 0, 0, 0, 1, 0, 0, 1, 0],
                    [
                        [
                            -2, 20, -20, 1,
                            -1, 20, -20, 1,
                            1, 20, -20, 1,
                            2, 20, -20, 1
                        ],
                        [],
                        [],
                        [],
                        [],
                        [],
                        [],
                        [0, 0, 0, 0],
                        [],
                        [],
                        [0, 0, 0, 0, 0, 0, 0, 0],
                        []
                    ],
                    [
                        [5, 0, 1],
                        [5, 0, 1],
                        [5, 0, 1],
                        [5, 0, 1],
                        [10, 0, 1],
                        [10, 0, 1],
                        [10, 0, 1],
                        [10, 0, 1],
                        [15, 0, 1],
                        [15, 0, 1],
                        [15, 0, 1],
                        [15, 0, 1]
                    ],
                    1
                ))
            else:
                intrusions.append(Primitive(
                    factory,
                    [
                        5, 10, -15, 1,
                        -5, 10, -15, 1,
                        -5, -10, -15, 1,
                        5, -10, -15, 1,
                        5, 10, 15, 1,
                        -5, 10, 15, 1,
                        -5, -10, 15, 1,
                        5, -10, 15, 1
                    ],
                    [3 * i, 3 * i, 3 * i, 0, 0, 0, 3.14 * i / 4, 3.14 * i / 6, 3.14 * i / 8],
                    [5, 0, 0, 0, 0, 0, 0, 1, 0, 0, 1, 0],
                    [
                        [
                            -2, 20, -20, 1,
                            -1, 20, -20, 1,
                            1, 20, -20, 1,
                            2, 20, -20, 1
                        ],
                        [],
                        [],
                        [],
                        [],
                        [],
                        [],
                        [0, 0, 0, 0],
                        [],
                        [],
                        [0, 0, 0, 0, 0, 0, 0, 0],
                        []
                    ],
                    [
                        [5, 0, 1],
                        [5, 0, 1],
                        [5, 0, 1],
                        [5, 0, 1],
                        [10, 0, 1],
                        [10, 0, 1],
                        [10, 0, 1],
                        [10, 0, 1],
                        [15, 0, 1],
                        [15, 0, 1],
                        [15, 0, 1],
                        [15, 0, 1]
                    ],
                    1
                ))
            intrusions[i].create()
            intrusions[i].correct_after_occ()
        complex_intrusions = Complex(factory, intrusions, intrusions_pgs)

        print("Booleans")
        print("Intrusions Inner Boolean")
        complex_intrusions.inner_boolean()
        print("Intrusions by Boreholes Boolean")
        Complex.boolean(factory, complex_intrusions, complex_boreholes)
        print("Environment by Intrusions Boolean")
        primitive_complex_boolean(factory, environment, complex_intrusions)
        print("Environment by Boreholes Boolean")
        primitive_complex_boolean(factory, environment, complex_boreholes)

        print("Set Mesh Sizes")
        environment.set_size(50)
        # FIXME bug then complex_boreholes mesh size != complex_intrusions mesh size (Not always...)
        complex_boreholes.set_size(10)
        complex_intrusions.set_size(10)

        print("Physical Groups")
        v_fgs_names = ["Borehole", "Intrusion"]
        for idx, name in enumerate(v_fgs_names):
            volumes_idxs = []
            volumes_idxs.extend(complex_boreholes.get_volumes_idxs_by_physical_group_tag(idx))
            volumes_idxs.extend(complex_intrusions.get_volumes_idxs_by_physical_group_tag(idx))
            tag = gmsh.model.addPhysicalGroup(3, volumes_idxs)
            gmsh.model.setPhysicalName(3, tag, name)
        # Environment
        env_fg = gmsh.model.addPhysicalGroup(3, environment.volumes)
        gmsh.model.setPhysicalName(3, env_fg, "Rock")
        volumes_dim_tags = zip([3] * len(environment.volumes), environment.volumes)
        s_dim_tags = gmsh.model.getBoundary(volumes_dim_tags)
        env_s_fgs = []
        env_s_fgs_names = ["X", "Y", "NZ", "NY", "Z", "NX"]
        for i in range(6):
            env_s_fgs.append(gmsh.model.addPhysicalGroup(2, s_dim_tags[i]))
            gmsh.model.setPhysicalName(2, env_s_fgs[i], env_s_fgs_names[i])

        print("Transfinite")
        complex_boreholes.transfinite()
        complex_intrusions.transfinite()

        print("Remove All Duplicates")
        factory.removeAllDuplicates()

        print("Mesh Generate")
        gmsh.model.mesh.generate(3)

        print("Remove Mesh Duplicate Nodes")
        gmsh.model.mesh.removeDuplicateNodes()

        gmsh.write("test_complex.msh")

        gmsh.finalize()

    def test_cylinder(self):
        gmsh.initialize()

        gmsh.option.setNumber("Geometry.AutoCoherence", 0)
        gmsh.option.setNumber("General.Terminal", 1)
        # gmsh.option.setNumber("Mesh.Algorithm3D", 4)

        gmsh.model.add("test_cylinder")

        factory = gmsh.model.occ

        # cylinder = Cylinder(
        #     factory,
        #     [10, 20, 30],
        #     [10, 20, 30],
        #     [[5, 5, 5], [7, 7, 7], [9, 9, 9]],
        #     [0, 0, 0, 0, 0, 0, 0, 0, 0],
        #     [[0, 1, 2], [3, 4, 5], [6, 7, 8]],
        #     [[3, 0, 1], [4, 0, 1], [5, 0, 1]],
        #     [[3, 0, 1], [4, 0, 1], [5, 0, 1]],
        #     [5, 0, 1]
        # )

        cylinder = Cylinder(
            factory,
            [20],
            [10],
            [[5]],
            [0, 0, 0, 0, 0, 0, 0, 0, 0],
            [[0]],
            [[3, 0, 1]],
            [[4, 0, 1]],
            [5, 0, 1]
        )

        # print("Physical Groups")
        # v_fgs_names = ["V0", "V1", "V2", "V3", "V4", "V5", "V6", "V7", "V8"]
        # for idx, name in enumerate(v_fgs_names):
        #     volumes_idxs = []
        #     volumes_idxs.extend(cylinder.get_volumes_idxs_by_physical_group_tag(idx))
        #     tag = gmsh.model.addPhysicalGroup(3, volumes_idxs)
        #     gmsh.model.setPhysicalName(3, tag, name)

        for idx, primitive in enumerate(cylinder.primitives):
            fsgs = []
            for i in range(len(primitive.surfaces)):
                fsgs.append(gmsh.model.addPhysicalGroup(2, [primitive.surfaces[i]]))
                gmsh.model.setPhysicalName(2, fsgs[i], "%s%s" % (primitive.surfaces_names[i], idx))


        print("Transfinite")
        cylinder.transfinite()

        print("Remove All Duplicates")
        factory.removeAllDuplicates()

        print("Generate Mesh")
        gmsh.model.mesh.generate(3)

        print("Remove Mesh Duplicate Nodes")
        gmsh.model.mesh.removeDuplicateNodes()

        gmsh.write("test_cylinder.msh")

        gmsh.finalize()

    def test_cylinder_boolean(self):
        gmsh.initialize()

        gmsh.option.setNumber("Geometry.AutoCoherence", 0)
        gmsh.option.setNumber("General.Terminal", 1)
        gmsh.option.setNumber("Mesh.Algorithm3D", 4)

        gmsh.model.add("test_cylinder_boolean")

        factory = gmsh.model.occ

        # Environment
        environment = Primitive(
            factory,
            [
                100, 100, -100, 10,
                -100, 100, -100, 10,
                -100, -100, -100, 10,
                100, -100, -100, 10,
                100, 100, 100, 10,
                -100, 100, 100, 10,
                -100, -100, 100, 10,
                100, -100, 100, 10
            ],
            [0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [[], [], [], [], [], [], [], [], [], [], [], []]
        )
        environment.create()
        environment.correct_after_occ()

        # cylinder = Cylinder(
        #     factory,
        #     [10, 20, 30],
        #     [10, 20, 30],
        #     [[5, 5, 5], [7, 7, 7], [9, 9, 9]],
        #     [0, 0, 0, 0, 0, 0, 0, 0, 0],
        #     [[0, 1, 2], [3, 4, 5], [6, 7, 8]],
        #     [[3, 0, 1], [4, 0, 1], [5, 0, 1]],
        #     [[3, 0, 1], [4, 0, 1], [5, 0, 1]],
        #     [5, 0, 1]
        # )

        cylinder = Cylinder(
            factory,
            [20],
            [10],
            [[5]],
            [0, 0, 0, 0, 0, 0, 0, 0, 0],
            [[0]],
            [[3, 0, 1]],
            [[4, 0, 1]],
            [5, 0, 1]
        )

        print("Environment by Cylinder Boolean")
        primitive_complex_boolean(factory, environment, cylinder)

        # print("Set Mesh Sizes")
        # environment.set_size(50)
        # cylinder.set_size(10)

        print("Physical Groups")
        v_fgs_names = ["V0", "V1", "V2", "V3", "V4", "V5", "V6", "V7", "V8"]
        for idx, name in enumerate(v_fgs_names):
            volumes_idxs = []
            volumes_idxs.extend(cylinder.get_volumes_idxs_by_physical_group_tag(idx))
            tag = gmsh.model.addPhysicalGroup(3, volumes_idxs)
            gmsh.model.setPhysicalName(3, tag, name)
        # Environment
        env_fg = gmsh.model.addPhysicalGroup(3, environment.volumes)
        gmsh.model.setPhysicalName(3, env_fg, "Rock")
        volumes_dim_tags = zip([3] * len(environment.volumes), environment.volumes)
        s_dim_tags = gmsh.model.getBoundary(volumes_dim_tags)
        env_s_fgs = []
        env_s_fgs_names = ["X", "Y", "NZ", "NY", "Z", "NX"]
        for i in range(6):
            env_s_fgs.append(gmsh.model.addPhysicalGroup(2, s_dim_tags[i]))
            gmsh.model.setPhysicalName(2, env_s_fgs[i], env_s_fgs_names[i])

        print("Transfinite")
        cylinder.transfinite()

        print("Remove All Duplicates")
        factory.removeAllDuplicates()

        print("Mesh Generate")
        gmsh.model.mesh.generate(3)

        print("Remove Mesh Duplicate Nodes")
        gmsh.model.mesh.removeDuplicateNodes()

        gmsh.write("test_cylinder_boolean.msh")

        gmsh.finalize()

    def test_close_primitives(self):
        gmsh.initialize()

        # gmsh.option.setNumber("Geometry.AutoCoherence", 0)
        # gmsh.option.setNumber("Mesh.Algorithm3D", 4)
        gmsh.option.setNumber("General.Terminal", 1)

        gmsh.model.add("test_close_primitives")

        factory = gmsh.model.occ

        # Environment
        # environment = Primitive(
        #     factory,
        #     [
        #         100, 100, -100, 50,
        #         -100, 100, -100, 50,
        #         -100, -100, -100, 50,
        #         100, -100, -100, 50,
        #         100, 100, 100, 50,
        #         -100, 100, 100, 50,
        #         -100, -100, 100, 50,
        #         100, -100, 100, 50
        #     ],
        #     [0, 0, 0, 0, 0, 0, 0, 0, 0],
        #     [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        #     [[], [], [], [], [], [], [], [], [], [], [], []]
        # )
        # environment.create()
        # environment.correct_after_occ()

        primitives = []
        coordinates = [
            [0, 0],
            [10, 0],
            [-10, 0],
            [0, 20],
            [0, -20],
            [10, 20],
            [10, -20],
            [-10, 20],
            [-10, -20]
        ]
        # coordinates = [
        #     [0, 0],
        #     [20, 0],
        #     [-20, 0],
        #     [0, 30],
        #     [0, -30],
        #     [20, 30],
        #     [20, -30],
        #     [-20, 30],
        #     [-20, -30]
        # ]
        for i in range(9):
            primitives.append(Primitive(
                factory,
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
                [coordinates[i][0], coordinates[i][1], 0, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                [[], [], [], [], [], [], [], [], [], [], [], []],
                [
                    [5, 0, 1],
                    [5, 0, 1],
                    [5, 0, 1],
                    [5, 0, 1],
                    [10, 0, 1],
                    [10, 0, 1],
                    [10, 0, 1],
                    [10, 0, 1],
                    [15, 0, 1],
                    [15, 0, 1],
                    [15, 0, 1],
                    [15, 0, 1]
                ],
                0
            ))

        # for primitive in primitives:
        #     Primitive.boolean(factory, environment, primitive)

        # for primitive in primitives:
        #     result = primitive.correct_to_transfinite()
        #     if result:
        #         primitive.transfinite()

        # Primitives
        fgs = []
        for idx, primitive in enumerate(primitives):
            fgs.append(gmsh.model.addPhysicalGroup(3, primitive.volumes))
            gmsh.model.setPhysicalName(3, fgs[idx], "V%s" % idx)
            fsgs = []
            for i in range(len(primitive.surfaces)):
                fsgs.append(gmsh.model.addPhysicalGroup(2, [primitive.surfaces[i]]))
                gmsh.model.setPhysicalName(2, fsgs[i], "%s%s" % (primitive.surfaces_names[i], idx))
        # Environment
        # env_fg = gmsh.model.addPhysicalGroup(3, environment.volumes)
        # gmsh.model.setPhysicalName(3, env_fg, "Rock")
        # env_s_dim_tags = environment.get_actual_surfaces()
        # env_s_fgs = []
        # env_s_fgs_names = ["X", "Y", "NZ", "NY", "Z", "NX"]
        # for i in range(6):
        #     env_s_fgs.append(gmsh.model.addPhysicalGroup(2, env_s_dim_tags[i]))
        #     gmsh.model.setPhysicalName(2, env_s_fgs[i], env_s_fgs_names[i])

        factory.removeAllDuplicates()

        gmsh.model.mesh.generate(3)

        gmsh.model.mesh.removeDuplicateNodes()

        gmsh.write("test_close_primitives.msh")

        gmsh.finalize()


if __name__ == '__main__':
    unittest.main()
