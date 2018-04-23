import unittest
from primitive import Primitive
import gmsh


class MyTestCase(unittest.TestCase):
    def test_mix(self):
        # Before using any functions in the Python API, Gmsh must be initialized.
        gmsh.initialize()

        gmsh.option.setNumber("Geometry.AutoCoherence", 0)

        # By default Gmsh will not print out any messages: in order to output messages
        # on the terminal, just set the standard Gmsh option "General.Terminal" (same
        # format and meaning as in .geo files) using gmshOptionSetNumber():
        gmsh.option.setNumber("General.Terminal", 1)

        # This creates a new model, named "t1". If gmshModelCreate() is not called, a
        # new default (unnamed) model will be created on the fly, if necessary.
        gmsh.model.add("primitive_test_mix")

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
        environment.create()
        environment.correct_after_occ()

        primitives = []
        for m in range(2):
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
                [m * 5, m * 5, m * 6, 0, 0, 0, 3.14 / 4, 3.14 / 6, 3.14 / 8],
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
            primitives[m].create()
            primitives[m].correct_after_occ()

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
            [25, 25, 25, 0, 0, 0, 3.14 / 8, 3.14 / 6, 3.14 / 4],
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
        primitives[2].create()
        primitives[2].correct_after_occ()

        print("Boolean 0 by 1")
        Primitive.boolean(factory, primitives[0], primitives[1])
        factory.synchronize()

        print("Boolean environment by 0")
        Primitive.boolean(factory, environment, primitives[0])
        factory.synchronize()

        print("Boolean environment by 1")
        Primitive.boolean(factory, environment, primitives[1])
        factory.synchronize()

        print("Boolean environment by 2")
        Primitive.boolean(factory, environment, primitives[2])
        factory.synchronize()

        environment.set_size(25)
        primitives[0].set_size(3)
        primitives[1].set_size(4)
        primitives[2].set_size(5)

        print("Physical Volumes")
        v_fgs = []
        for primitive in primitives:
            v_fgs.append(gmsh.model.addPhysicalGroup(3, primitive.volumes))
        for m in range(len(v_fgs)):
            gmsh.model.setPhysicalName(3, v_fgs[m], "V%s" % m)

        env_fg = gmsh.model.addPhysicalGroup(3, environment.volumes)
        gmsh.model.setPhysicalName(3, env_fg, "Environment")

        for primitive in primitives:
            result = primitive.correct_to_transfinite()
            if result:
                primitive.transfinite()

        print("Physical Surfaces")
        s_dim_tags = environment.get_actual_surfaces()
        s_fgs = []
        s_fgs_names = ["X", "Y", "NZ", "NY", "Z", "NX"]
        for i in range(6):
            s_fgs.append(gmsh.model.addPhysicalGroup(2, s_dim_tags[i]))
            gmsh.model.setPhysicalName(2, s_fgs[i], s_fgs_names[i])

        gmsh.option.setNumber("Mesh.Algorithm3D", 4)

        factory.removeAllDuplicates()

        gmsh.model.mesh.generate(3)

        gmsh.model.mesh.removeDuplicateNodes()

        gmsh.write("primitive_test_mix.msh")
        gmsh.finalize()

    def test_transfinite(self):
        # Before using any functions in the Python API, Gmsh must be initialized.
        gmsh.initialize()

        gmsh.option.setNumber("Geometry.AutoCoherence", 0)

        # By default Gmsh will not print out any messages: in order to output messages
        # on the terminal, just set the standard Gmsh option "General.Terminal" (same
        # format and meaning as in .geo files) using gmshOptionSetNumber():
        gmsh.option.setNumber("General.Terminal", 1)

        # This creates a new model, named "t1". If gmshModelCreate() is not called, a
        # new default (unnamed) model will be created on the fly, if necessary.
        gmsh.model.add("primitive_test_transfinite")

        factory = gmsh.model.occ

        primitives = []
        for m in range(4):
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
                [m * 15, m * 15, m * 6, 0, 0, 0, 0, 0, 0],
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
                m
            ))
            primitives[m].create()
            primitives[m].correct_after_occ()

        fgs = []
        for idx, primitive in enumerate(primitives):
            fgs.append(gmsh.model.addPhysicalGroup(3, primitive.volumes))
            gmsh.model.setPhysicalName(3, fgs[idx], "V%s" % idx)
            fsgs = []
            for i in range(len(primitive.surfaces)):
                fsgs.append(gmsh.model.addPhysicalGroup(2, [primitive.surfaces[i]]))
                gmsh.model.setPhysicalName(2, fsgs[i], "%s%s" % (primitive.surface_names[i], idx))

        for primitive in primitives:
            result = primitive.correct_to_transfinite()
            if result:
                primitive.transfinite()

        factory.removeAllDuplicates()

        gmsh.model.mesh.generate(3)

        gmsh.model.mesh.removeDuplicateNodes()

        gmsh.write("primitive_test_transfinite.msh")

        gmsh.finalize()

    def test_super_mix(self):
        # Before using any functions in the Python API, Gmsh must be initialized.
        gmsh.initialize()

        gmsh.option.setNumber("Geometry.AutoCoherence", 0)

        # By default Gmsh will not print out any messages: in order to output messages
        # on the terminal, just set the standard Gmsh option "General.Terminal" (same
        # format and meaning as in .geo files) using gmshOptionSetNumber():
        gmsh.option.setNumber("General.Terminal", 1)

        # This creates a new model, named "t1". If gmshModelCreate() is not called, a
        # new default (unnamed) model will be created on the fly, if necessary.
        gmsh.model.add("primitive_test_super_mix")

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
        environment.create()
        environment.correct_after_occ()

        primitives = []
        for m in range(3):
            if m == 1:
                primitives.append(Primitive(
                    factory,
                    [
                        5, 5, -15, 1,
                        -5, 5, -15, 1,
                        -5, -5, -15, 1,
                        5, -5, -15, 1,
                        5, 5, 15, 1,
                        -5, 5, 15, 1,
                        -5, -5, 15, 1,
                        5, -5, 15, 1,
                    ],
                    [m * 5, m * 5, m * 6, 0, 0, 0, 0, 0, 0],
                    [1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0],
                    [
                        [0, 0, 0, 0],
                        [0, 0, 0, 0],
                        [0, 0, 0, 0],
                        [0, 0, 0, 0],
                        [0, 0, 0, 0],
                        [0, 0, 0, 0],
                        [0, 0, 0, 0],
                        [0, 0, 0, 0],
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
                        5, -10, 15, 1,
                    ],
                    [m * 5, m * 5, m * 6, 0, 0, 0, 3.14 / 4, 3.14 / 6, 3.14 / 8],
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
            primitives[m].create()
            primitives[m].correct_after_occ()

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
            [25, 25, -25, 0, 0, 0, 3.14 / 8, 3.14 / 6, 3.14 / 4],
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
        primitives[3].create()
        primitives[3].correct_after_occ()

        print("Boolean 0 by 2")
        Primitive.boolean(factory, primitives[0], primitives[2])
        factory.synchronize()

        print("Boolean 0 by 1")
        Primitive.boolean(factory, primitives[0], primitives[1])
        factory.synchronize()

        print("Boolean 2 by 1")
        Primitive.boolean(factory, primitives[2], primitives[1])
        factory.synchronize()

        for idx, primitive in enumerate(primitives):
            print("Boolean environment by %s" % idx)
            Primitive.boolean(factory, environment, primitive)
            factory.synchronize()

        environment.set_size(25)
        primitives[0].set_size(3)
        primitives[1].set_size(4)
        primitives[2].set_size(5)
        primitives[3].set_size(3)

        print("Physical Volumes")
        v_fgs = []
        for primitive in primitives:
            v_fgs.append(gmsh.model.addPhysicalGroup(3, primitive.volumes))
        for m in range(len(v_fgs)):
            gmsh.model.setPhysicalName(3, v_fgs[m], "V%s" % m)

        env_fg = gmsh.model.addPhysicalGroup(3, environment.volumes)
        gmsh.model.setPhysicalName(3, env_fg, "Environment")

        for primitive in primitives:
            result = primitive.correct_to_transfinite()
            if result:
                primitive.transfinite()

        print("Physical Surfaces")
        s_dim_tags = environment.get_actual_surfaces()
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

        gmsh.model.mesh.removeDuplicateNodes()

        gmsh.write("primitive_test_super_mix.msh")
        gmsh.finalize()


if __name__ == '__main__':
    unittest.main()
