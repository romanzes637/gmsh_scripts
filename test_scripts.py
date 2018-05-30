import gmsh
import math

import occ_workarounds as occ_ws

import unittest
import itertools

import time

from borehole import Borehole
from primitive import primitive_boolean, primitive_cut_by_volume_boolean, Environment, complex_cut_by_volume_boolean
from import_text import read_complex_type_1, read_complex_type_2, read_complex_type_2_to_complex_primitives
from complex_primitive import ComplexPrimitive
from primitive import complex_boolean
from primitive import Primitive
from primitive import Complex
from primitive import primitive_complex_boolean
from cylinder import Cylinder


class TestScripts(unittest.TestCase):
    def test_transfinite(self):
        start_time = time.time()

        gmsh.initialize()

        gmsh.option.setNumber("General.Terminal", 1)
        gmsh.model.add("test_transfinite")

        # factory = gmsh.model.geo
        factory = gmsh.model.occ

        print("Creation")
        start = time.time()
        primitives = []
        for i in range(4):
            primitives.append(Primitive(
                factory,
                [
                    [5, 10, -15, 1],
                    [-5, 10, -15, 1],
                    [-5, -10, -15, 1],
                    [5, -10, -15, 1],
                    [5, 10, 15, 1],
                    [-5, 10, 15, 1],
                    [-5, -10, 15, 1],
                    [5, -10, 15, 1],
                ],
                [30 + i * 15, 0, 0, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                [
                    [
                        [-2, 20, -20, 1],
                        [-1, 20, -20, 1],
                        [1, 20, -20, 1],
                        [2, 20, -20, 1]
                    ],
                    [],
                    [],
                    [],
                    [],
                    [],
                    [],
                    [[0, 0, 0, 0]],
                    [],
                    [],
                    [[0, 0, 0, 0], [0, 0, 0, 0]],
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
                    [10, 5, -15, 1],
                    [-10, 5, -15, 1],
                    [-10, -5, -15, 1],
                    [10, -5, -15, 1],
                    [10, 5, 15, 1],
                    [-10, 5, 15, 1],
                    [-10, -5, 15, 1],
                    [10, -5, 15, 1],
                ],
                [0, 30 + i * 15, 0, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                [
                    [
                        [-2, 20, -20, 1],
                        [-1, 20, -20, 1],
                        [1, 20, -20, 1],
                        [2, 20, -20, 1]
                    ],
                    [],
                    [],
                    [],
                    [],
                    [],
                    [],
                    [[0, 0, 0, 0]],
                    [],
                    [],
                    [[0, 0, 0, 0], [0, 0, 0, 0]],
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
                    [15, 10, -5, 1],
                    [-15, 10, -5, 1],
                    [-15, -10, -5, 1],
                    [15, -10, -5, 1],
                    [15, 10, 5, 1],
                    [-15, 10, 5, 1],
                    [-15, -10, 5, 1],
                    [15, -10, 5, 1],
                ],
                [0, 0, 30 + i * 15, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                [
                    [
                        [-2, 20, -20, 1],
                        [-1, 20, -20, 1],
                        [1, 20, -20, 1],
                        [2, 20, -20, 1]
                    ],
                    [],
                    [],
                    [],
                    [],
                    [],
                    [],
                    [[0, 0, 0, 0]],
                    [],
                    [],
                    [[0, 0, 0, 0], [0, 0, 0, 0]],
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
        print('{:.3f}s'.format(time.time() - start))

        print("Correction")
        start = time.time()
        for primitive in primitives:
            result = occ_ws.correct_primitive(primitive)
            print(result)
        print('{:.3f}s'.format(time.time() - start))

        print("Transfinite")
        start = time.time()
        ss = set()
        for primitive in primitives:
            result = primitive.transfinite(ss)
            print(result)
        print('{:.3f}s'.format(time.time() - start))

        print("Physical")
        for idx, primitive in enumerate(primitives):
            tag = gmsh.model.addPhysicalGroup(3, primitive.volumes)
            gmsh.model.setPhysicalName(3, tag, "V{}".format(idx))
            for surface_idx, surface in enumerate(primitive.surfaces):
                tag = gmsh.model.addPhysicalGroup(2, [surface])
                gmsh.model.setPhysicalName(2, tag, "{}{}".format(primitive.surfaces_names[surface_idx], idx))

        gmsh.model.mesh.generate(3)

        gmsh.model.mesh.removeDuplicateNodes()

        gmsh.write("test_transfinite.msh")

        gmsh.finalize()

        print('\nElapsed time: {:.3f}s'.format(time.time() - start_time))

    def test_primitive_environment(self):
        """
        Primitive in Environment
        """
        start_time = time.time()

        gmsh.initialize()

        gmsh.option.setNumber("Geometry.AutoCoherence", 0)
        gmsh.option.setNumber("General.Terminal", 1)
        gmsh.option.setNumber("Mesh.Algorithm3D", 4)

        gmsh.model.add("test_primitive_environment")

        factory = gmsh.model.geo
        # factory = gmsh.model.occ  # TODO Doesn't work with occ because volume with holes is not created

        print("Primitive")
        primitive = Primitive(
            factory,
            [
                [5, 10, -15, 5],
                [-5, 10, -15, 5],
                [-5, -10, -15, 5],
                [5, -10, -15, 5],
                [5, 10, 15, 5],
                [-5, 10, 15, 5],
                [-5, -10, 15, 5],
                [5, -10, 15, 5],
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
        environment = Environment(factory, 50, 50, 50, 5, [0, 0, 0, 0, 0, 0, 0, 0, 0], primitive.surfaces)

        print("Remove All Duplicates")
        factory.removeAllDuplicates()

        print("Physical Groups")
        tag = gmsh.model.addPhysicalGroup(3, primitive.volumes)
        gmsh.model.setPhysicalName(3, tag, "Primitive")
        tag = gmsh.model.addPhysicalGroup(3, environment.volumes)
        gmsh.model.setPhysicalName(3, tag, "Environment")
        for i in range(len(environment.surfaces)):
            tag = gmsh.model.addPhysicalGroup(2, [environment.surfaces[i]])
            gmsh.model.setPhysicalName(2, tag, environment.surfaces_names[i])

        print("Transfinite")
        ss = set()
        primitive.transfinite(ss)

        gmsh.model.mesh.generate(3)

        gmsh.model.mesh.removeDuplicateNodes()

        gmsh.write("test_primitive_environment.msh")

        gmsh.finalize()

        print('\nElapsed time: {:.3f}s'.format(time.time() - start_time))

    def test_primitive_environment_boolean(self):
        """
        Test Primitive in Environment boolean
        """
        start_time = time.time()

        gmsh.initialize()

        gmsh.option.setNumber("General.Terminal", 1)
        gmsh.option.setNumber("Mesh.Algorithm3D", 4)

        gmsh.model.add("test_primitive_environment_boolean")

        factory = gmsh.model.occ

        print("Creation")
        start = time.time()
        environment = Primitive(
            factory,
            [
                [100, 100, -100, 50],
                [-100, 100, -100, 50],
                [-100, -100, -100, 50],
                [100, -100, -100, 50],
                [100, 100, 100, 50],
                [-100, 100, 100, 50],
                [-100, -100, 100, 50],
                [100, -100, 100, 50]
            ],
            [0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [[], [], [], [], [], [], [], [], [], [], [], []]
        )
        primitive = Primitive(
            factory,
            [
                [5, 10, -15, 1],
                [-5, 10, -15, 2],
                [-5, -10, -15, 3],
                [5, -10, -15, 4],
                [5, 10, 15, 5],
                [-5, 10, 15, 6],
                [-5, -10, 15, 7],
                [5, -10, 15, 8],
            ],
            [1, -3, 5, -2, 5, -1, math.pi / 3, -math.pi / 4, -math.pi / 6],
            [5, 0, 0, 0, 0, 0, 0, 1, 0, 0, 1, 0],
            [
                [
                    [-2, 20, -20, 1],
                    [-1, 20, -20, 1],
                    [1, 20, -20, 1],
                    [2, 20, -20, 1]
                ],
                [],
                [],
                [],
                [],
                [],
                [],
                [[0, 0, 0, 0]],
                [],
                [],
                [[0, 0, 0, 0], [0, 0, 0, 0]],
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
            0
        )
        print('{:.3f}s'.format(time.time() - start))

        print("Environment by Primitive boolean")
        start = time.time()
        primitive_boolean(factory, environment, primitive)
        print('{:.3f}s'.format(time.time() - start))

        print("Remove All Duplicates")
        start = time.time()
        factory.removeAllDuplicates()
        factory.synchronize()
        print('{:.3f}s'.format(time.time() - start))

        print("Correction")
        start = time.time()
        result = occ_ws.correct_primitive(primitive)
        print("Primitive {}".format(result))
        result = occ_ws.correct_primitive(environment)
        print("Environment {}".format(result))
        print('{:.3f}s'.format(time.time() - start))

        print("Transfinite")
        start = time.time()
        ss = set()
        result = primitive.transfinite(ss)
        print("Primitive {}".format(result))
        result = environment.transfinite(ss)
        print("Environment {}".format(result))
        print('{:.3f}s'.format(time.time() - start))

        print("Physical Volumes")
        tag = gmsh.model.addPhysicalGroup(3, primitive.volumes)
        gmsh.model.setPhysicalName(3, tag, "Primitive")
        tag = gmsh.model.addPhysicalGroup(3, environment.volumes)
        gmsh.model.setPhysicalName(3, tag, "Environment")

        print("Physical Surfaces")
        # for idx, surface in enumerate(primitive.surfaces):
        #     tag = gmsh.model.addPhysicalGroup(2, [surface])
        #     gmsh.model.setPhysicalName(2, tag, "Primitive{}".format(primitive.surfaces_names[idx]))
        volumes_dim_tags = map(lambda x: (3, x), environment.volumes)
        surfaces_dim_tags = gmsh.model.getBoundary(volumes_dim_tags, combined=False)
        surfaces_names = ["X", "Z", "NY", "NZ", "Y", "NX"]
        for i in range(6):
            tag = gmsh.model.addPhysicalGroup(surfaces_dim_tags[i][0], [surfaces_dim_tags[i][1]])
            gmsh.model.setPhysicalName(2, tag, surfaces_names[i])

        gmsh.model.mesh.generate(3)

        gmsh.model.mesh.removeDuplicateNodes()

        gmsh.write("test_primitive_environment_boolean.msh")

        gmsh.finalize()

        print('\nElapsed time: {:.3f}s'.format(time.time() - start_time))

    def test_mix(self):
        start_time = time.time()

        gmsh.initialize()

        gmsh.option.setNumber("Mesh.Algorithm3D", 4)
        gmsh.option.setNumber("General.Terminal", 1)

        gmsh.model.add("test_mix")

        factory = gmsh.model.occ

        environment = Primitive(
            factory,
            [
                [50, 60, -70, 10],
                [-50, 60, -70, 10],
                [-50, -60, -70, 10],
                [50, -60, -70, 10],
                [50, 60, 70, 10],
                [-50, 60, 70, 10],
                [-50, -60, 70, 10],
                [50, -60, 70, 10],
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
                    [5, 10, -15, 1],
                    [-5, 10, -15, 1],
                    [-5, -10, -15, 1],
                    [5, -10, -15, 1],
                    [5, 10, 15, 1],
                    [-5, 10, 15, 1],
                    [-5, -10, 15, 1],
                    [5, -10, 15, 1],
                ],
                [i * 5, i * 5, i * 6, 0, 0, 0, 3.14 * i / 4, 3.14 * i / 6, 3.14 * i / 8],
                [5, 0, 0, 0, 0, 0, 0, 1, 0, 0, 1, 0],
                [
                    [
                        [-2, 20, -20, 1],
                        [-1, 20, -20, 1],
                        [1, 20, -20, 1],
                        [2, 20, -20, 1]
                    ],
                    [],
                    [],
                    [],
                    [],
                    [],
                    [],
                    [[0, 0, 0, 0]],
                    [],
                    [],
                    [[0, 0, 0, 0], [0, 0, 0, 0]],
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

        print("Boolean")
        start = time.time()
        combinations = list(itertools.combinations(range(n_primitives), 2))
        print(combinations)
        for combination in combinations:
            print("Boolean primitive %s by primitive %s" % combination)
            primitive_boolean(factory, primitives[combination[0]], primitives[combination[1]])

        for idx, primitive in enumerate(primitives):
            print("Boolean environment by borehole %s" % idx)
            primitive_boolean(factory, environment, primitive)
        print('{:.3f}s'.format(time.time() - start))

        print("Remove All Duplicates")
        start = time.time()
        factory.removeAllDuplicates()
        factory.synchronize()
        print('{:.3f}s'.format(time.time() - start))

        print("Correction")
        start = time.time()
        for primitive in primitives:
            occ_ws.correct_primitive(primitive)
        print('{:.3f}s'.format(time.time() - start))

        print("Set Sizes")
        start = time.time()
        environment.set_size(25)
        for primitive in primitives:
            primitive.set_size(5)
        print('{:.3f}s'.format(time.time() - start))

        print("Transfinite")  # Works only after correct_complex_after_boolean()
        start = time.time()
        ss = set()  # already transfinite surfaces (workaround for double transfinite issue)
        for primitive in primitives:
            primitive.transfinite(ss)
        print('{:.3f}s'.format(time.time() - start))

        print("Primitives Physical")
        for idx, primitive in enumerate(primitives):
            tag = gmsh.model.addPhysicalGroup(3, primitive.volumes)
            gmsh.model.setPhysicalName(3, tag, "V{}".format(idx))

        print("Environment Physical")
        tag = gmsh.model.addPhysicalGroup(3, environment.volumes)
        gmsh.model.setPhysicalName(3, tag, "Environment")
        volumes_dim_tags = map(lambda x: (3, x), environment.volumes)
        surfaces_dim_tags = gmsh.model.getBoundary(volumes_dim_tags, combined=False)
        surfaces_names = ["X", "Z", "NY", "NZ", "Y", "NX"]
        for i in range(6):
            tag = gmsh.model.addPhysicalGroup(surfaces_dim_tags[i][0], [surfaces_dim_tags[i][1]])
            gmsh.model.setPhysicalName(2, tag, surfaces_names[i])
            #     gmsh.model.setPhysicalName(2, tag, 'S%s' % i)

        gmsh.model.mesh.generate(3)

        gmsh.model.mesh.removeDuplicateNodes()

        gmsh.write("test_mix.msh")

        gmsh.finalize()

        print('\nElapsed time: {:.3f}s'.format(time.time() - start_time))

    def test_primitive_mix(self):
        """
        Three primitive boreholes and three primitive rock intrusions.
        Two intrusions intersect each over and two boreholes,
        i.e. one borehole and one complex_type_1 aren't intersected.
        All boreholes and intrusions are included in rock environment.
        """
        start_time = time.time()

        gmsh.initialize()

        gmsh.option.setNumber("General.Terminal", 1)
        gmsh.option.setNumber("Mesh.Algorithm3D", 4)

        gmsh.model.add("test_primitive_mix")

        factory = gmsh.model.occ

        print("Creation")
        start = time.time()
        environment = Primitive(
            factory,
            [
                [100, 100, -100, 100],
                [-100, 100, -100, 100],
                [-100, -100, -100, 100],
                [100, -100, -100, 100],
                [100, 100, 100, 100],
                [-100, 100, 100, 100],
                [-100, -100, 100, 100],
                [100, -100, 100, 100]
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
                    [5, 5, -30, 1],
                    [-5, 5, -30, 1],
                    [-5, -5, -30, 1],
                    [5, -5, -30, 1],
                    [5, 5, 30, 1],
                    [-5, 5, 30, 1],
                    [-5, -5, 30, 1],
                    [5, -5, 30, 1]
                ],
                [25 * i, 0, 0, 0, 0, 0, 0, 0, 0],
                [1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0],
                [
                    [[0, 0, -30, 0]],
                    [[0, 0, 30, 0]],
                    [[0, 0, 30, 0]],
                    [[0, 0, -30, 0]],
                    [[0, 0, -30, 0]],
                    [[0, 0, -30, 0]],
                    [[0, 0, 30, 0]],
                    [[0, 0, 30, 0]],
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
        n_intrusions = 3
        intrusions = []
        for i in range(n_intrusions):
            if i == 0:
                intrusions.append(Primitive(
                    factory,
                    [
                        [5, 10, -15, 1],
                        [-5, 10, -15, 1],
                        [-5, -10, -15, 1],
                        [5, -10, -15, 1],
                        [5, 10, 15, 1],
                        [-5, 10, 15, 1],
                        [-5, -10, 15, 1],
                        [5, -10, 15, 1]
                    ],
                    [25, 40, -50, 0, 0, 0, 3.14 / 8, 3.14 / 6, 3.14 / 4],
                    [4, 0, 0, 0, 0, 0, 0, 1, 0, 0, 1, 0],
                    [
                        [
                            [-2, 20, -20, 1],
                            [-1, 20, -20, 1],
                            [1, 20, -20, 1],
                            [2, 20, -20, 1]
                        ],
                        [],
                        [],
                        [],
                        [],
                        [],
                        [],
                        [[0, 0, 0, 0]],
                        [],
                        [],
                        [[0, 0, 0, 0], [0, 0, 0, 0]],
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
                        [5, 10, -15, 1],
                        [-5, 10, -15, 1],
                        [-5, -10, -15, 1],
                        [5, -10, -15, 1],
                        [5, 10, 15, 1],
                        [-5, 10, 15, 1],
                        [-5, -10, 15, 1],
                        [5, -10, 15, 1]
                    ],
                    [3 * i, 3 * i, 3 * i, 0, 0, 0, 3.14 * i / 4, 3.14 * i / 6, 3.14 * i / 8],
                    [5, 0, 0, 0, 0, 0, 0, 1, 0, 0, 1, 0],
                    [
                        [
                            [-2, 20, -20, 1],
                            [-1, 20, -20, 1],
                            [1, 20, -20, 1],
                            [2, 20, -20, 1]
                        ],
                        [],
                        [],
                        [],
                        [],
                        [],
                        [],
                        [[0, 0, 0, 0]],
                        [],
                        [],
                        [[0, 0, 0, 0], [0, 0, 0, 0]],
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
        print('{:.3f}s'.format(time.time() - start))

        print("Boolean")
        start = time.time()
        combinations = list(itertools.combinations(range(n_intrusions), 2))
        print(combinations)
        for combination in combinations:
            print("Boolean primitive %s by primitive %s" % combination)
            primitive_boolean(factory, intrusions[combination[0]], intrusions[combination[1]])
        for idx, borehole in enumerate(boreholes):
            for idx2, primitive in enumerate(intrusions):
                print("Boolean primitive %s by borehole %s" % (idx2, idx))
                primitive_boolean(factory, primitive, borehole)
        for idx, borehole in enumerate(boreholes):
            print("Boolean environment by borehole %s" % idx)
            primitive_boolean(factory, environment, borehole)
        for idx, intrusion in enumerate(intrusions):
            print("Boolean environment by primitive %s" % idx)
            primitive_boolean(factory, environment, intrusion)
        print('{:.3f}s'.format(time.time() - start))

        print("Remove All Duplicates")
        start = time.time()
        factory.removeAllDuplicates()
        factory.synchronize()
        print('{:.3f}s'.format(time.time() - start))

        print("Correction")
        start = time.time()
        for borehole in boreholes:
            occ_ws.correct_primitive(borehole)
        for intrusion in intrusions:
            occ_ws.correct_primitive(intrusion)
        print('{:.3f}s'.format(time.time() - start))

        print("Set Sizes")
        start = time.time()
        environment.set_size(50)
        for borehole in boreholes:
            borehole.set_size(10)
        for intrusion in intrusions:
            intrusion.set_size(10)
        print('{:.3f}s'.format(time.time() - start))

        print("Transfinite")  # Works only after correct_complex_after_boolean()
        start = time.time()
        ss = set()  # already transfinite surfaces (workaround for double transfinite issue)
        for borehole in boreholes:
            borehole.transfinite(ss)
        for intrusion in intrusions:
            intrusion.transfinite(ss)
        print('{:.3f}s'.format(time.time() - start))

        print("Physical Volumes")
        intrusion_fgs = []
        for primitive in intrusions:
            intrusion_fgs.append(gmsh.model.addPhysicalGroup(3, primitive.volumes))
        for i in range(len(intrusion_fgs)):
            gmsh.model.setPhysicalName(3, intrusion_fgs[i], "Intrusion{}".format(i))
        borehole_fgs = []
        for borehole in boreholes:
            borehole_fgs.append(gmsh.model.addPhysicalGroup(3, borehole.volumes))
        for i in range(len(borehole_fgs)):
            gmsh.model.setPhysicalName(3, borehole_fgs[i], "Borehole{}".format(i))
        env_fg = gmsh.model.addPhysicalGroup(3, environment.volumes)
        gmsh.model.setPhysicalName(3, env_fg, "Environment")

        print("Physical Surfaces")
        volumes_dim_tags = map(lambda x: (3, x), environment.volumes)
        surfaces_dim_tags = gmsh.model.getBoundary(volumes_dim_tags, combined=False)
        surfaces_names = ["X", "Z", "NY", "NZ", "Y", "NX"]
        for i in range(6):
            tag = gmsh.model.addPhysicalGroup(surfaces_dim_tags[i][0], [surfaces_dim_tags[i][1]])
            gmsh.model.setPhysicalName(2, tag, surfaces_names[i])

        gmsh.model.mesh.generate(3)

        gmsh.model.mesh.removeDuplicateNodes()

        gmsh.write("test_primitive_mix.msh")

        gmsh.finalize()

        print('\nElapsed time: {:.3f}s'.format(time.time() - start_time))

    def test_complex_mix(self):
        """
        Test complex boreholes and complex intrusions inscribed in environment.
        """
        start_time = time.time()

        gmsh.initialize()

        gmsh.option.setNumber("General.Terminal", 1)
        gmsh.option.setNumber("Mesh.Algorithm3D", 4)

        gmsh.model.add("test_complex_mix")

        factory = gmsh.model.occ

        print("Creation")
        start = time.time()
        # Environment
        environment = Primitive(
            factory,
            [
                [100, 100, -100, 10],
                [-100, 100, -100, 10],
                [-100, -100, -100, 10],
                [100, -100, -100, 10],
                [100, 100, 100, 10],
                [-100, 100, 100, 10],
                [-100, -100, 100, 10],
                [100, -100, 100, 10]
            ],
            [0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [[], [], [], [], [], [], [], [], [], [], [], []]
        )
        # Boreholes
        n_boreholes = 3
        boreholes = []
        boreholes_pgs = []
        for i in range(n_boreholes):
            boreholes_pgs.append(0)
            boreholes.append(Primitive(
                factory,
                [
                    [5, 5, -30, 1],
                    [-5, 5, -30, 1],
                    [-5, -5, -30, 1],
                    [5, -5, -30, 1],
                    [5, 5, 30, 1],
                    [-5, 5, 30, 1],
                    [-5, -5, 30, 1],
                    [5, -5, 30, 1]
                ],
                [25 * i, 0, 0, 0, 0, 0, 0, 0, 0],
                [1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0],
                [
                    [[0, 0, -30, 0]],
                    [[0, 0, 30, 0]],
                    [[0, 0, 30, 0]],
                    [[0, 0, -30, 0]],
                    [[0, 0, -30, 0]],
                    [[0, 0, -30, 0]],
                    [[0, 0, 30, 0]],
                    [[0, 0, 30, 0]],
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
                        [5, 10, -15, 1],
                        [-5, 10, -15, 1],
                        [-5, -10, -15, 1],
                        [5, -10, -15, 1],
                        [5, 10, 15, 1],
                        [-5, 10, 15, 1],
                        [-5, -10, 15, 1],
                        [5, -10, 15, 1]
                    ],
                    [25, 40, -50, 0, 0, 0, 3.14 / 8, 3.14 / 6, 3.14 / 4],
                    [4, 0, 0, 0, 0, 0, 0, 1, 0, 0, 1, 0],
                    [
                        [
                            [-2, 20, -20, 1],
                            [-1, 20, -20, 1],
                            [1, 20, -20, 1],
                            [2, 20, -20, 1]
                        ],
                        [],
                        [],
                        [],
                        [],
                        [],
                        [],
                        [[0, 0, 0, 0]],
                        [],
                        [],
                        [[0, 0, 0, 0], [0, 0, 0, 0]],
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
                        [5, 10, -15, 1],
                        [-5, 10, -15, 1],
                        [-5, -10, -15, 1],
                        [5, -10, -15, 1],
                        [5, 10, 15, 1],
                        [-5, 10, 15, 1],
                        [-5, -10, 15, 1],
                        [5, -10, 15, 1]
                    ],
                    [3 * i, 3 * i, 3 * i, 0, 0, 0, 3.14 * i / 4, 3.14 * i / 6, 3.14 * i / 8],
                    [5, 0, 0, 0, 0, 0, 0, 1, 0, 0, 1, 0],
                    [
                        [
                            [-2, 20, -20, 1],
                            [-1, 20, -20, 1],
                            [1, 20, -20, 1],
                            [2, 20, -20, 1]
                        ],
                        [],
                        [],
                        [],
                        [],
                        [],
                        [],
                        [[0, 0, 0, 0]],
                        [],
                        [],
                        [[0, 0, 0, 0], [0, 0, 0, 0]],
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
        complex_intrusions = Complex(factory, intrusions, intrusions_pgs)
        print('{:.3f}s'.format(time.time() - start))

        print("Booleans")
        start = time.time()
        print("Intrusions Inner Boolean")
        complex_intrusions.inner_boolean()
        print("Intrusions by Boreholes Boolean")
        complex_boolean(factory, complex_intrusions, complex_boreholes)
        print("Environment by Intrusions Boolean")
        primitive_complex_boolean(factory, environment, complex_intrusions)
        print("Environment by Boreholes Boolean")
        primitive_complex_boolean(factory, environment, complex_boreholes)
        print('{:.3f}s'.format(time.time() - start))

        print("Remove All Duplicates")
        start = time.time()
        factory.removeAllDuplicates()
        factory.synchronize()
        print('{:.3f}s'.format(time.time() - start))

        print("Correction")
        start = time.time()
        occ_ws.correct_complex(complex_boreholes)
        occ_ws.correct_complex(complex_intrusions)
        print('{:.3f}s'.format(time.time() - start))

        print("Set Sizes")
        start = time.time()
        environment.set_size(50)
        complex_boreholes.set_size(3)
        complex_intrusions.set_size(1)
        print('{:.3f}s'.format(time.time() - start))

        print("Transfinite")  # Works only after correct_complex_after_boolean()
        start = time.time()
        ss = set()  # already transfinite surfaces (workaround for double transfinite issue)
        complex_boreholes.transfinite(ss)
        complex_intrusions.transfinite(ss)
        print('{:.3f}s'.format(time.time() - start))

        print("Physical Volumes")
        v_fgs_names = ["Borehole", "Intrusion"]
        for idx, name in enumerate(v_fgs_names):
            volumes_idxs = []
            volumes_idxs.extend(complex_boreholes.get_volumes_by_physical_index(idx))
            volumes_idxs.extend(complex_intrusions.get_volumes_by_physical_index(idx))
            tag = gmsh.model.addPhysicalGroup(3, volumes_idxs)
            gmsh.model.setPhysicalName(3, tag, name)
        env_fg = gmsh.model.addPhysicalGroup(3, environment.volumes)
        gmsh.model.setPhysicalName(3, env_fg, "Rock")

        print("Physical Surfaces")
        volumes_dim_tags = map(lambda x: (3, x), environment.volumes)
        surfaces_dim_tags = gmsh.model.getBoundary(volumes_dim_tags, combined=False)
        surfaces_names = ["X", "Z", "NY", "NZ", "Y", "NX"]
        for i in range(6):
            tag = gmsh.model.addPhysicalGroup(surfaces_dim_tags[i][0], [surfaces_dim_tags[i][1]])
            gmsh.model.setPhysicalName(2, tag, surfaces_names[i])

        gmsh.model.mesh.generate(3)

        gmsh.model.mesh.removeDuplicateNodes()

        gmsh.write("test_complex_mix.msh")

        gmsh.finalize()

        print('\nElapsed time: {:.3f}s'.format(time.time() - start_time))

    def test_cylinder(self):
        """
        Test complex cylinder
        """
        start_time = time.time()

        gmsh.initialize()

        gmsh.option.setNumber("General.Terminal", 1)
        gmsh.option.setNumber("Mesh.Algorithm3D", 4)

        gmsh.model.add("test_cylinder")

        factory = gmsh.model.occ

        cylinder = Cylinder(
            factory,
            [10, 20, 30],
            [10, 20, 30],
            [[5, 5, 5], [7, 7, 7], [9, 9, 9]],
            [0, 0, 0, 0, 0, 0, 0, 0, 0],
            [[0, 1, 2], [3, 4, 5], [6, 7, 8]],
            [[3, 0, 1], [4, 0, 1], [5, 0, 1]],
            [[3, 0, 1], [4, 0, 1], [5, 0, 1]],
            [5, 0, 1]
        )

        print("Remove All Duplicates")
        factory.removeAllDuplicates()
        factory.synchronize()

        print("Correction")
        occ_ws.correct_complex(cylinder)

        print("Transfinite")
        ss = set()
        cylinder.transfinite(ss)

        print("Physical")
        vs_names = ["V0", "V1", "V2", "V3", "V4", "V5", "V6", "V7", "V8"]
        for idx, name in enumerate(vs_names):
            volumes_idxs = []
            volumes_idxs.extend(cylinder.get_volumes_by_physical_index(idx))
            tag = gmsh.model.addPhysicalGroup(3, volumes_idxs)
            gmsh.model.setPhysicalName(3, tag, name)

        gmsh.model.mesh.generate(3)

        gmsh.model.mesh.removeDuplicateNodes()

        gmsh.write("test_cylinder.msh")

        gmsh.finalize()

        print('\nElapsed time: {:.3f}s'.format(time.time() - start_time))

    def test_cylinder_boolean(self):
        """
        Test complex cylinder in an environment by boolean
        """
        start_time = time.time()

        gmsh.initialize()

        gmsh.option.setNumber("General.Terminal", 1)
        gmsh.option.setNumber("Mesh.Algorithm3D", 4)

        gmsh.model.add("test_cylinder_boolean")

        factory = gmsh.model.occ

        print("Creation")
        start = time.time()
        environment = Primitive(
            factory,
            [
                [100, 100, -100, 50],
                [-100, 100, -100, 50],
                [-100, -100, -100, 50],
                [100, -100, -100, 50],
                [100, 100, 100, 50],
                [-100, 100, 100, 50],
                [-100, -100, 100, 50],
                [100, -100, 100, 50]
            ],
            [0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [[], [], [], [], [], [], [], [], [], [], [], []]
        )
        # cylinder = Cylinder(
        #     factory,
        #     [5],
        #     [10],
        #     [[5]],
        #     [0, 0, 0, 0, 0, 0, 0, 0, 0],
        #     [[0]],
        #     [[3, 0, 1]],
        #     [[4, 0, 1]],
        #     [5, 0, 1]
        # )
        # cylinder = Cylinder(
        #     factory,
        #     [5, 10],
        #     [10],
        #     [[5, 6, 7]],
        #     [0, 0, 0, 0, 0, 0, 0, 0, 0],
        #     [[0, 1]],
        #     [[3, 0, 1], [4, 0, 1]],
        #     [[4, 0, 1]],
        #     [5, 0, 1]
        # )
        # cylinder = Cylinder(
        #     factory,
        #     [5],
        #     [10, 15],
        #     [[5], [6]],
        #     [0, 0, 0, 0, 0, 0, 0, 0, 0],
        #     [[0], [0]],
        #     [[3, 0, 1]],
        #     [[4, 0, 1], [5, 0, 1]],
        #     [5, 0, 1]
        # )
        # cylinder = Cylinder(
        #     factory,
        #     [10, 20],
        #     [30, 40],
        #     [[5, 6], [6, 7]],
        #     [0, 0, 0, 0, 0, 0, 0, 0, 0],
        #     [[0, 1], [0, 1]],
        #     [[3, 0, 1], [4, 0, 1]],
        #     [[4, 0, 1], [5, 0, 1]],
        #     [5, 0, 1]
        # )
        cylinder = Cylinder(
            factory,
            [5, 10, 15],
            [5, 10, 15],
            [[5, 6, 7], [6, 7, 8], [7, 8, 9]],
            [0, 0, 0, 0, 0, 0, 0, 0, 0],
            [[0, 1, 2], [0, 1, 2], [0, 1, 2]],
            [[3, 0, 1.1], [4, 1, 1.2], [5, 0, 1.3]],
            [[4, 1, 0.9], [5, 0, 0.8], [6, 1, 0.7]],
            [5, 0, 1]
        )
        print('{:.3f}s'.format(time.time() - start))

        print("Environment by Cylinder boolean")
        start = time.time()
        primitive_complex_boolean(factory, environment, cylinder)
        print('{:.3f}s'.format(time.time() - start))

        print("Remove All Duplicates")
        start = time.time()
        factory.removeAllDuplicates()
        factory.synchronize()
        print('{:.3f}s'.format(time.time() - start))

        print("Correction")
        start = time.time()
        occ_ws.correct_complex(cylinder)
        print('{:.3f}s'.format(time.time() - start))

        print("Transfinite")  # Works only after correct_complex_after_boolean()
        start = time.time()
        ss = set()  # already transfinite surfaces (workaround for double transfinite issue)
        cylinder.transfinite(ss)
        print('{:.3f}s'.format(time.time() - start))

        # print("Physical")
        # for idx, primitive in enumerate(cylinder.primitives):
        #     tag = gmsh.model.addPhysicalGroup(3, primitive.volumes)
        #     gmsh.model.setPhysicalName(3, tag, "V{}".format(idx))
        #     for surface_idx, surface in enumerate(primitive.surfaces):
        #         tag = gmsh.model.addPhysicalGroup(2, [surface])
        #         gmsh.model.setPhysicalName(2, tag, "{}{}".format(primitive.surfaces_names[surface_idx], idx))

        print("Physical Groups")
        v_fgs_names = ["V0", "V1", "V2"]
        for idx, name in enumerate(v_fgs_names):
            volumes_idxs = []
            volumes_idxs.extend(cylinder.get_volumes_by_physical_index(idx))
            tag = gmsh.model.addPhysicalGroup(3, volumes_idxs)
            gmsh.model.setPhysicalName(3, tag, name)

        print("Physical Environment")
        env_fg = gmsh.model.addPhysicalGroup(3, environment.volumes)
        gmsh.model.setPhysicalName(3, env_fg, "Environment")
        volumes_dim_tags = map(lambda x: (3, x), environment.volumes)
        surfaces_dim_tags = gmsh.model.getBoundary(volumes_dim_tags, combined=False)
        surfaces_names = ["X", "Z", "NY", "NZ", "Y", "NX"]
        for i in range(6):
            tag = gmsh.model.addPhysicalGroup(surfaces_dim_tags[i][0], [surfaces_dim_tags[i][1]])
            gmsh.model.setPhysicalName(2, tag, surfaces_names[i])
            #     gmsh.model.setPhysicalName(2, tag, 'S%s' % i)

        gmsh.model.mesh.generate(3)

        gmsh.model.mesh.removeDuplicateNodes()

        gmsh.write("test_cylinder_boolean.msh")

        gmsh.finalize()

        print('\nElapsed time: {:.3f}s'.format(time.time() - start_time))

    def test_cylinder_boolean_by_primitive(self):
        """
        Test complex cylinder, primitive, environment by boolean
        """
        start_time = time.time()

        gmsh.initialize()

        gmsh.option.setNumber("General.Terminal", 1)
        gmsh.option.setNumber("Mesh.Algorithm3D", 4)

        gmsh.model.add("test_cylinder_boolean_by_primitive")

        factory = gmsh.model.occ

        print("Creation")
        start = time.time()
        environment = Primitive(
            factory,
            [
                [100, 100, -100, 50],
                [-100, 100, -100, 50],
                [-100, -100, -100, 50],
                [100, -100, -100, 50],
                [100, 100, 100, 50],
                [-100, 100, 100, 50],
                [-100, -100, 100, 50],
                [100, -100, 100, 50]
            ],
            [0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [[], [], [], [], [], [], [], [], [], [], [], []]
        )
        cylinder = Cylinder(
            factory,
            [5],
            [50],
            [[5]],
            [0, 0, -25, 0, 0, 0, 0, 0, 0],
            [[0]],
            [[3, 0, 1]],
            [[4, 0, 1]],
            [5, 0, 1]
        )
        # cylinder = Cylinder(
        #     factory,
        #     [5, 10],
        #     [10],
        #     [[5, 6, 7]],
        #     [0, 0, 0, 0, 0, 0, 0, 0, 0],
        #     [[0, 1]],
        #     [[3, 0, 1], [4, 0, 1]],
        #     [[4, 0, 1]],
        #     [5, 0, 1]
        # )
        # cylinder = Cylinder(
        #     factory,
        #     [5],
        #     [10, 15],
        #     [[5], [6]],
        #     [0, 0, 0, 0, 0, 0, 0, 0, 0],
        #     [[0], [0]],
        #     [[3, 0, 1]],
        #     [[4, 0, 1], [5, 0, 1]],
        #     [5, 0, 1]
        # )
        # cylinder = Cylinder(
        #     factory,
        #     [10, 20],
        #     [30, 40],
        #     [[5, 6], [6, 7]],
        #     [0, 0, 0, 0, 0, 0, 0, 0, 0],
        #     [[0, 1], [0, 1]],
        #     [[3, 0, 1], [4, 0, 1]],
        #     [[4, 0, 1], [5, 0, 1]],
        #     [5, 0, 1]
        # )
        # cylinder = Cylinder(
        #     factory,
        #     [5, 7, 9],
        #     [25, 25, 25],
        #     [[5, 6, 7], [6, 7, 8], [7, 8, 9]],
        #     [0, 0, -25, 0, 0, 0, 0, 0, 0],
        #     [[0, 1, 2], [0, 1, 2], [0, 1, 2]],
        #     [[3, 0, 1.1], [4, 1, 1.2], [5, 0, 1.3]],
        #     [[10, 1, 0.9], [10, 0, 0.8], [10, 1, 0.7]],
        #     [5, 0, 1]
        # )
        # cylinder = Cylinder(
        #     factory,
        #     [5],
        #     [25, 25, 25],
        #     [[5], [5], [5]],
        #     [0, 0, -50, 0, 0, 0, 0, 0, 0],
        #     [[0], [1], [2]],
        #     [[3, 0, 1]],
        #     [[25, 0, 1], [25, 0, 1], [25, 0, 1]],
        #     [5, 0, 1]
        # )
        # cylinder = Cylinder(
        #     factory,
        #     [5],
        #     [25, 25, 25, 25, 25],
        #     [[5], [5], [5], [5], [5]],
        #     [0, 0, -50, 0, 0, 0, 0, 0, 0],
        #     [[0], [0], [0], [0], [0]],
        #     [[3, 0, 1]],
        #     [[4, 0, 1], [4, 0, 1], [4, 0, 1], [4, 0, 1], [4, 0, 1]],
        #     [5, 0, 1]
        # )
        primitive = Primitive(
            factory,
            [
                [5, 10, -15, 1],
                [-5, 10, -15, 2],
                [-5, -10, -15, 3],
                [5, -10, -15, 4],
                [5, 10, 15, 5],
                [-5, 10, 15, 6],
                [-5, -10, 15, 7],
                [5, -10, 15, 8],
            ],
            [1, -3, 0, -2, 5, -1, math.pi / 3, -math.pi / 4, -math.pi / 6],
            [5, 0, 0, 0, 0, 0, 0, 1, 0, 0, 1, 0],
            [
                [
                    [-2, 20, -20, 1],
                    [-1, 20, -20, 1],
                    [1, 20, -20, 1],
                    [2, 20, -20, 1]
                ],
                [],
                [],
                [],
                [],
                [],
                [],
                [[0, 0, 0, 0]],
                [],
                [],
                [[0, 0, 0, 0], [0, 0, 0, 0]],
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
            0
        )
        print('{:.3f}s'.format(time.time() - start))

        print("Cylinder Union")
        print(gmsh.model.getEntities(3))
        out = cylinder.get_union_volume()
        print(gmsh.model.getEntities(3))

        print("Primitive by Cylinder boolean")
        start = time.time()
        primitive_cut_by_volume_boolean(factory, primitive, out[0][1])
        print(gmsh.model.getEntities(3))
        primitive_complex_boolean(factory, primitive, cylinder)
        print('{:.3f}s'.format(time.time() - start))

        print("Environment by Cylinder boolean")
        start = time.time()
        primitive_complex_boolean(factory, environment, cylinder)
        print('{:.3f}s'.format(time.time() - start))

        print("Environment by Primitive boolean")
        start = time.time()
        primitive_boolean(factory, environment, primitive)
        print('{:.3f}s'.format(time.time() - start))

        print("Remove All Duplicates")
        start = time.time()
        factory.removeAllDuplicates()
        factory.synchronize()
        print(gmsh.model.getEntities(3))
        print('{:.3f}s'.format(time.time() - start))

        print("Correction")
        start = time.time()
        occ_ws.correct_complex(cylinder)
        print('{:.3f}s'.format(time.time() - start))

        print("Set Sizes")
        start = time.time()
        primitive.set_size(3)
        cylinder.set_size(1)
        print('{:.3f}s'.format(time.time() - start))

        print("Transfinite")  # Works only after correct_complex_after_boolean()
        start = time.time()
        ss = set()  # already transfinite surfaces (workaround for double transfinite issue)
        cylinder.transfinite(ss)
        print('{:.3f}s'.format(time.time() - start))

        # print("Physical")
        # for idx, primitive in enumerate(cylinder.primitives):
        #     tag = gmsh.model.addPhysicalGroup(3, primitive.volumes)
        #     gmsh.model.setPhysicalName(3, tag, "V{}".format(idx))
        #     for surface_idx, surface in enumerate(primitive.surfaces):
        #         tag = gmsh.model.addPhysicalGroup(2, [surface])
        #         gmsh.model.setPhysicalName(2, tag, "{}{}".format(primitive.surfaces_names[surface_idx], idx))

        # tag = gmsh.model.addPhysicalGroup(3, [out[0][1]])
        # gmsh.model.setPhysicalName(3, tag, "Union")

        print("Primitive Physical")
        tag = gmsh.model.addPhysicalGroup(3, primitive.volumes)
        gmsh.model.setPhysicalName(3, tag, "Primitive")

        print("Cylinder Physical")
        physical_group_names = ["V0", "V1", "V2"]
        for idx, name in enumerate(physical_group_names):
            volumes_idxs = []
            volumes_idxs.extend(cylinder.get_volumes_by_physical_index(idx))
            tag = gmsh.model.addPhysicalGroup(3, volumes_idxs)
            gmsh.model.setPhysicalName(3, tag, name)

        print("Environment Physical")
        tag = gmsh.model.addPhysicalGroup(3, environment.volumes)
        gmsh.model.setPhysicalName(3, tag, "Environment")
        volumes_dim_tags = map(lambda x: (3, x), environment.volumes)
        surfaces_dim_tags = gmsh.model.getBoundary(volumes_dim_tags, combined=False)
        surfaces_names = ["X", "Z", "NY", "NZ", "Y", "NX"]
        for i in range(6):
            tag = gmsh.model.addPhysicalGroup(surfaces_dim_tags[i][0], [surfaces_dim_tags[i][1]])
            gmsh.model.setPhysicalName(2, tag, surfaces_names[i])
            #     gmsh.model.setPhysicalName(2, tag, 'S%s' % i)

        gmsh.model.mesh.generate(3)

        gmsh.model.mesh.removeDuplicateNodes()

        gmsh.write("test_cylinder_boolean_by_primitive.msh")

        gmsh.finalize()

        print('\nElapsed time: {:.3f}s'.format(time.time() - start_time))

    def test_borehole(self):
        """
        Test borehole
        """
        start_time = time.time()

        gmsh.initialize()

        gmsh.option.setNumber("General.Terminal", 1)
        gmsh.option.setNumber("Mesh.Algorithm3D", 4)

        gmsh.model.add("test_borehole")

        factory = gmsh.model.occ

        print("Creation")
        start = time.time()
        repo_center_depth = 487.5  # repository center depth
        env_length_x = 500
        env_length_y = 500
        repo_lc = 100
        environment = Primitive(
            factory,
            [
                [env_length_x / 2, env_length_y / 2, -repo_center_depth, repo_lc],
                [-env_length_x / 2, env_length_y / 2, -repo_center_depth, repo_lc],
                [-env_length_x / 2, -env_length_y / 2, -repo_center_depth, repo_lc],
                [env_length_x / 2, -env_length_y / 2, -repo_center_depth, repo_lc],
                [env_length_x / 2, env_length_y / 2, repo_center_depth, repo_lc],
                [-env_length_x / 2, env_length_y / 2, repo_center_depth, repo_lc],
                [-env_length_x / 2, -env_length_y / 2, repo_center_depth, repo_lc],
                [env_length_x / 2, -env_length_y / 2, repo_center_depth, repo_lc]
            ],
            [0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [[], [], [], [], [], [], [], [], [], [], [], []]
        )
        borehole = Borehole(
            factory,
            [[1, 1, 1], [1, 1, 1], [1, 1, 1]],
            [0, 0, -37.5, 0, 0, 0, 0, 0, 0],
            [[3, 0, 1], [3, 0, 1], [3, 0, 1]],
            [[10, 0, 1], [10, 0, 1], [10, 0, 1]],
            [3, 0, 1],
            2
        )
        print('{:.3f}s'.format(time.time() - start))

        print("Environment by Borehole boolean")
        start = time.time()
        primitive_complex_boolean(factory, environment, borehole)
        print('{:.3f}s'.format(time.time() - start))

        print("Remove All Duplicates")
        start = time.time()
        factory.removeAllDuplicates()
        factory.synchronize()
        print('{:.3f}s'.format(time.time() - start))

        print("Correction and Transfinite")
        start = time.time()
        correction_rs = occ_ws.correct_complex(borehole)
        print(correction_rs)
        ss = set()  # already transfinite surfaces (workaround for double transfinite issue)
        transfinite_rs = []
        for idx, primitive in enumerate(borehole.primitives):
            if correction_rs[idx]:
                result = primitive.transfinite(ss)
                transfinite_rs.append(result)
            else:
                transfinite_rs.append(None)
        print(transfinite_rs)
        print('{:.3f}s'.format(time.time() - start))

        print("Set Sizes")
        start = time.time()
        environment.set_size(repo_lc)
        print('{:.3f}s'.format(time.time() - start))

        print("Borehole Physical")
        for idx, name in enumerate(borehole.physical_names):
            volumes_idxs = []
            volumes_idxs.extend(borehole.get_volumes_by_physical_index(idx))
            tag = gmsh.model.addPhysicalGroup(3, volumes_idxs)
            gmsh.model.setPhysicalName(3, tag, name)

        print("Environment Physical")
        tag = gmsh.model.addPhysicalGroup(3, environment.volumes)
        gmsh.model.setPhysicalName(3, tag, "Environment")
        volumes_dim_tags = map(lambda x: (3, x), environment.volumes)
        surfaces_dim_tags = gmsh.model.getBoundary(volumes_dim_tags, combined=False)
        surfaces_names = ["X", "Z", "NY", "NZ", "Y", "NX"]
        for i in range(len(surfaces_names)):
            tag = gmsh.model.addPhysicalGroup(surfaces_dim_tags[i][0], [surfaces_dim_tags[i][1]])
            gmsh.model.setPhysicalName(2, tag, surfaces_names[i])
            #     gmsh.model.setPhysicalName(2, tag, 'S%s' % i)

        gmsh.model.mesh.generate(3)

        gmsh.model.mesh.removeDuplicateNodes()

        gmsh.write("test_borehole.msh")

        gmsh.finalize()

        print('\nElapsed time: {:.3f}s'.format(time.time() - start_time))

    def test_borehole_with_intersection(self):
        """
        Test borehole with intersection
        Note.
        There is a relation of characteristic length parameters on result of mesh building.
        Shortly: high lc parameter at small volume can lead to mesh construction issues.
        As example: setting borehole lcs: [[1, 1, 1], [1, 1, 1], [1, 1, 1]] leads to zero volume 169,
        but if lcs is changed to [[1, 1, 1], [1, 0.5, 1], [1, 1, 1]] then mesh generation will perform well.
        """
        start_time = time.time()

        gmsh.initialize()

        gmsh.option.setNumber("General.Terminal", 1)
        # (1=Delaunay, 2=New Delaunay, 4=Frontal, 5=Frontal Delaunay, 6=Frontal Hex, 7=MMG3D, 9=R-tree)
        gmsh.option.setNumber("Mesh.Algorithm3D", 4)

        gmsh.model.add("test_borehole_with_intersection")

        factory = gmsh.model.occ

        print("Creation")
        start = time.time()
        repo_center_depth = 487.5  # repository center depth
        env_length_x = 500
        env_length_y = 500
        env_lc = 100
        environment = Primitive(
            factory,
            [
                [env_length_x / 2, env_length_y / 2, -repo_center_depth, env_lc],
                [-env_length_x / 2, env_length_y / 2, -repo_center_depth, env_lc],
                [-env_length_x / 2, -env_length_y / 2, -repo_center_depth, env_lc],
                [env_length_x / 2, -env_length_y / 2, -repo_center_depth, env_lc],
                [env_length_x / 2, env_length_y / 2, repo_center_depth, env_lc],
                [-env_length_x / 2, env_length_y / 2, repo_center_depth, env_lc],
                [-env_length_x / 2, -env_length_y / 2, repo_center_depth, env_lc],
                [env_length_x / 2, -env_length_y / 2, repo_center_depth, env_lc]
            ]
        )
        borehole = Borehole(
            factory,
            [[0.6, 0.3, 0.1], [0.6, 0.3, 0.1], [0.6, 0.3, 0.1]],
            [0, 0, -37.5, 0, 0, 0, 0, 0, 0],
            [[3, 0, 1], [3, 0, 1], [3, 0, 1]],
            [[10, 0, 1], [10, 0, 1], [10, 0, 1]],
            [3, 0, 1],
            10
        )
        int_length = 650  # 650
        int_width = 200  # 200
        int_thickness = 5
        int_lc = 5  # 5
        int_center_x = 0
        int_center_y = 0
        int_center_z = 0  # 35
        int_rotation_x = math.pi / 4  # math.pi / 4
        int_rotation_y = -math.pi / 3  # -math.pi / 4
        int_rotation_z = 0
        int_dz = 10  # 75  # 10
        int_dy = 0  # 5  # 20
        int_physical_tag = 0
        int_name = "Intrusion"
        intrusion = ComplexPrimitive(
            factory,
            [15, 5, 1],
            [
                [int_length / 2, int_width / 2 + int_dy, -int_thickness / 2 - int_dz, int_lc],
                [-int_length / 2, int_width / 2, -int_thickness / 2, int_lc],
                [-int_length / 2, -int_width / 2, -int_thickness / 2, int_lc],
                [int_length / 2, -int_width / 2 - int_dy / 2, -int_thickness / 2 - int_dz / 2, int_lc],
                [int_length / 2, int_width / 2, int_thickness / 2 - int_dz / 3, int_lc],
                [-int_length / 2, int_width / 2, int_thickness / 2, int_lc],
                [-int_length / 2, -int_width / 2, int_thickness / 2, int_lc],
                [int_length / 2, -int_width / 2, int_thickness / 2, int_lc],
            ],
            int_physical_tag,
            int_lc,
            [int_center_x, int_center_y, int_center_z, int_rotation_x, int_rotation_y, int_rotation_z],
            transfinite_data=[[5, 0, 1], [5, 0, 1], [5, 0, 1]]
        )
        print('{:.3f}s'.format(time.time() - start))

        print("Complex Union")
        start = time.time()
        out = borehole.get_union_volume()
        print('{:.3f}s'.format(time.time() - start))

        print("Intrusion by Borehole boolean")
        start = time.time()
        complex_cut_by_volume_boolean(factory, intrusion, out[0][1])
        complex_boolean(factory, intrusion, borehole)
        print('{:.3f}s'.format(time.time() - start))

        print("Environment by Borehole boolean")
        start = time.time()
        primitive_complex_boolean(factory, environment, borehole)
        print('{:.3f}s'.format(time.time() - start))

        print("Environment by Intrusion boolean")
        start = time.time()
        primitive_complex_boolean(factory, environment, intrusion)
        print('{:.3f}s'.format(time.time() - start))

        print("Remove All Duplicates")
        start = time.time()
        factory.removeAllDuplicates()
        factory.synchronize()
        print('{:.3f}s'.format(time.time() - start))

        print("Correct and Transfinite")
        start = time.time()
        ss = set()
        occ_ws.correct_and_transfinite_complex(borehole, ss)
        occ_ws.correct_and_transfinite_complex(intrusion, ss)
        print('{:.3f}s'.format(time.time() - start))

        print("Set Sizes")
        start = time.time()
        environment.set_size(env_lc)
        intrusion.set_size()
        borehole.set_size()
        print('{:.3f}s'.format(time.time() - start))

        print("Intrusion Physical")
        vs = intrusion.get_volumes_by_physical_index(int_physical_tag)
        tag = gmsh.model.addPhysicalGroup(3, vs)
        gmsh.model.setPhysicalName(3, tag, int_name)
        # print("Debug Intrusion Physical")
        # for idx, primitive in enumerate(intrusion.primitives):
        #     tag = gmsh.model.addPhysicalGroup(3, primitive.volumes)
        #     gmsh.model.setPhysicalName(3, tag, "V_I{}".format(idx))
        #     for surface_idx, surface in enumerate(primitive.surfaces):
        #         tag = gmsh.model.addPhysicalGroup(2, [surface])
        #         gmsh.model.setPhysicalName(2, tag, "S_I_{}{}".format(primitive.surfaces_names[surface_idx], idx))

        print("Borehole Physical")
        for idx, name in enumerate(borehole.physical_names):
            volumes_idxs = []
            volumes_idxs.extend(borehole.get_volumes_by_physical_index(idx))
            tag = gmsh.model.addPhysicalGroup(3, volumes_idxs)
            gmsh.model.setPhysicalName(3, tag, name)
        # print("Debug Borehole Physical")
        # for idx, primitive in enumerate(borehole.primitives):
        #     tag = gmsh.model.addPhysicalGroup(3, primitive.volumes)
        #     gmsh.model.setPhysicalName(3, tag, "V_B{}".format(idx))
        #     for surface_idx, surface in enumerate(primitive.surfaces):
        #         tag = gmsh.model.addPhysicalGroup(2, [surface])
        #         gmsh.model.setPhysicalName(2, tag, "S_B_{}{}".format(primitive.surfaces_names[surface_idx], idx))

        print("Environment Physical")
        tag = gmsh.model.addPhysicalGroup(3, environment.volumes)
        gmsh.model.setPhysicalName(3, tag, "Environment")
        volumes_dim_tags = map(lambda x: (3, x), environment.volumes)
        surfaces_dim_tags = gmsh.model.getBoundary(volumes_dim_tags, combined=False)
        surfaces_names = ["X", "Z", "NY", "NZ", "Y", "NX"]
        for i in range(len(surfaces_names)):
            tag = gmsh.model.addPhysicalGroup(surfaces_dim_tags[i][0], [surfaces_dim_tags[i][1]])
            gmsh.model.setPhysicalName(2, tag, surfaces_names[i])
            #     gmsh.model.setPhysicalName(2, tag, 'S%s' % i)

        # Debug volume 169
        # volumes_dim_tags = map(lambda x: (3, x), [169])
        # surfaces_dim_tags = gmsh.model.getBoundary(volumes_dim_tags, combined=False)
        # for surface_idx, surface in enumerate(surfaces_dim_tags):
        #     tag = gmsh.model.addPhysicalGroup(2, [surface[1]])
        #     gmsh.model.setPhysicalName(2, tag, "S_{}".format(surface_idx))
        # tag = gmsh.model.addPhysicalGroup(3, [169])
        # gmsh.model.setPhysicalName(3, tag, "V_169")

        gmsh.model.mesh.generate(3)

        gmsh.model.mesh.removeDuplicateNodes()

        gmsh.write("test_borehole_with_intersection_test_10b_15x5x1i_0.1_env.msh")

        gmsh.finalize()

        print('\nElapsed time: {:.3f}s'.format(time.time() - start_time))

    def test_read_complex(self):
        """
        Test read Complex
        """
        start_time = time.time()

        gmsh.initialize()

        gmsh.option.setNumber("General.Terminal", 1)
        gmsh.option.setNumber("Mesh.Algorithm3D", 4)

        gmsh.model.add("test_read_complex")

        factory = gmsh.model.occ

        print("Reading")
        start = time.time()
        intrusion = read_complex_type_2(factory, "complex_type_2", [0, 0, 0], [5, 10, 15], 0, 1)
        print('{:.3f}s'.format(time.time() - start))

        print("Creation")
        start = time.time()
        environment = Primitive(
            factory,
            [
                [100, 100, -100, 50],
                [-100, 100, -100, 50],
                [-100, -100, -100, 50],
                [100, -100, -100, 50],
                [100, 100, 100, 50],
                [-100, 100, 100, 50],
                [-100, -100, 100, 50],
                [100, -100, 100, 50]
            ],
            [0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [[], [], [], [], [], [], [], [], [], [], [], []]
        )
        print('{:.3f}s'.format(time.time() - start))

        print("Inner Intrusion boolean")
        start = time.time()
        intrusion.inner_boolean()
        print('{:.3f}s'.format(time.time() - start))

        print("Environment by Intrusion boolean")
        start = time.time()
        primitive_complex_boolean(factory, environment, intrusion)
        print('{:.3f}s'.format(time.time() - start))

        print("Remove All Duplicates")
        start = time.time()
        factory.removeAllDuplicates()
        factory.synchronize()
        print('{:.3f}s'.format(time.time() - start))

        print("Correction and Transfinite")
        start = time.time()
        c_rs = occ_ws.correct_complex(intrusion)
        print(c_rs)
        ss = set()  # already transfinite surfaces (workaround for double transfinite issue)
        t_rs = []
        for idx, primitive in enumerate(intrusion.primitives):
            if c_rs[idx]:
                result = primitive.transfinite(ss)
                t_rs.append(result)
            else:
                t_rs.append(None)
        print(t_rs)
        print('{:.3f}s'.format(time.time() - start))

        print("Set Sizes")
        start = time.time()
        environment.set_size(50)
        intrusion.set_size(3)
        print('{:.3f}s'.format(time.time() - start))

        print("Physical Volumes")
        v_fgs_names = ["Intrusion"]
        for idx, name in enumerate(v_fgs_names):
            volumes_idxs = []
            volumes_idxs.extend(intrusion.get_volumes_by_physical_index(idx))
            tag = gmsh.model.addPhysicalGroup(3, volumes_idxs)
            gmsh.model.setPhysicalName(3, tag, name)

        print("Environment Physical")
        tag = gmsh.model.addPhysicalGroup(3, environment.volumes)
        gmsh.model.setPhysicalName(3, tag, "Environment")
        volumes_dim_tags = map(lambda x: (3, x), environment.volumes)
        surfaces_dim_tags = gmsh.model.getBoundary(volumes_dim_tags, combined=False)
        surfaces_names = ["X", "Z", "NY", "NZ", "Y", "NX"]
        for i in range(len(surfaces_names)):
            tag = gmsh.model.addPhysicalGroup(surfaces_dim_tags[i][0], [surfaces_dim_tags[i][1]])
            gmsh.model.setPhysicalName(2, tag, surfaces_names[i])
            #     gmsh.model.setPhysicalName(2, tag, 'S%s' % i)

        gmsh.model.mesh.generate(3)

        gmsh.model.mesh.removeDuplicateNodes()

        gmsh.write("test_read_complex.msh")

        gmsh.finalize()

        print('\nElapsed time: {:.3f}s'.format(time.time() - start_time))

    def test_complex_primitive(self):
        """
        Test ComplexPrimitive
        """
        start_time = time.time()

        gmsh.initialize()

        gmsh.option.setNumber("General.Terminal", 1)
        gmsh.option.setNumber("Mesh.Algorithm3D", 4)

        gmsh.model.add("test_complex_primitive")

        factory = gmsh.model.occ

        print("Creating")
        start = time.time()
        int_length = 20
        int_width = 20
        int_thickness = 1
        int_lc = 1
        int_center_x = 0
        int_center_y = 0
        int_center_z = 0
        int_rotation_x = math.pi / 4  # math.pi / 4
        int_rotation_y = -math.pi / 4  # -math.pi / 4
        int_rotation_z = 0
        int_dz = 10  # 10
        int_dy = 0  # 20
        int_physical_tag = 100
        int_name = "ComplexPrimitive"
        cp = ComplexPrimitive(
            factory,
            [3, 3, 1],
            [
                [int_length / 2, int_width / 2 + int_dy, -int_thickness / 2 - int_dz, int_lc],
                [-int_length / 2, int_width / 2, -int_thickness / 2, int_lc],
                [-int_length / 2, -int_width / 2, -int_thickness / 2, int_lc],
                [int_length / 2, -int_width / 2 - int_dy / 2, -int_thickness / 2 - int_dz / 2, int_lc],
                [int_length / 2, int_width / 2, int_thickness / 2 - int_dz / 3, int_lc],
                [-int_length / 2, int_width / 2, int_thickness / 2, int_lc],
                [-int_length / 2, -int_width / 2, int_thickness / 2, int_lc],
                [int_length / 2, -int_width / 2, int_thickness / 2, int_lc],
            ],
            int_physical_tag,
            int_lc,
            [int_center_x, int_center_y, int_center_z, int_rotation_x, int_rotation_y, int_rotation_z],
            transfinite_data=[[5, 0, 1], [5, 0, 1], [5, 0, 1]]
        )
        print('{:.3f}s'.format(time.time() - start))

        print("Remove All Duplicates")
        start = time.time()
        factory.removeAllDuplicates()
        factory.synchronize()
        print('{:.3f}s'.format(time.time() - start))

        print("Correction and Transfinite")
        start = time.time()
        correction_rs = occ_ws.correct_complex(cp)
        print(correction_rs)
        ss = set()  # already transfinite surfaces (workaround for double transfinite issue)
        transfinite_rs = []
        for idx, intrusion in enumerate(cp.primitives):
            if correction_rs[idx]:
                result = intrusion.transfinite(ss)
                transfinite_rs.append(result)
            else:
                transfinite_rs.append(None)
        print(transfinite_rs)
        print('{:.3f}s'.format(time.time() - start))

        print("Physical")
        vs = cp.get_volumes_by_physical_index(int_physical_tag)
        tag = gmsh.model.addPhysicalGroup(3, vs)
        gmsh.model.setPhysicalName(3, tag, int_name)

        gmsh.model.mesh.generate(3)

        gmsh.model.mesh.removeDuplicateNodes()

        gmsh.write("test_complex_primitive.msh")

        gmsh.finalize()

        print('\nElapsed time: {:.3f}s'.format(time.time() - start_time))

    def test_read_complex_primitives(self):
        """
        Test read ComplexPrimitives
        """
        start_time = time.time()

        gmsh.initialize()

        gmsh.option.setNumber("General.Terminal", 1)
        gmsh.option.setNumber("Mesh.Algorithm3D", 4)

        gmsh.model.add("test_read_complex_primitives")

        factory = gmsh.model.occ

        int_name = "Intrusion"
        int_physical_tag = 0
        int_lc = 5
        int_center_x = 0
        int_center_y = 0
        int_center_z = 0
        int_n_x = 2
        int_n_y = 1
        int_n_z = 1
        int_tr_x = [5, 0, 1]
        int_tr_y = [5, 0, 1]
        int_tr_z = [5, 0, 1]
        int_rotation_x = math.pi / 4  # math.pi / 4
        int_rotation_y = -math.pi / 3  # -math.pi / 4
        int_rotation_z = 0
        print("Reading")
        start = time.time()
        complex_primitives = read_complex_type_2_to_complex_primitives(
            factory, "complex_type_2",
            [int_n_x, int_n_y, int_n_z],
            int_physical_tag, int_lc,
            [int_center_x, int_center_y, int_center_z],
            [int_tr_x, int_tr_y, int_tr_z])
        print('{:.3f}s'.format(time.time() - start))

        print("Creation")
        start = time.time()
        environment = Primitive(
            factory,
            [
                [100, 100, -100, 50],
                [-100, 100, -100, 50],
                [-100, -100, -100, 50],
                [100, -100, -100, 50],
                [100, 100, 100, 50],
                [-100, 100, 100, 50],
                [-100, -100, 100, 50],
                [100, -100, 100, 50]
            ],
            [0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [[], [], [], [], [], [], [], [], [], [], [], []]
        )
        print('{:.3f}s'.format(time.time() - start))

        print("ComplexPrimitives boolean")
        start = time.time()
        combinations = list(itertools.combinations(range(len(complex_primitives)), 2))
        for combination in combinations:
            print("Boolean %s by %s" % combination)
            complex_boolean(factory, complex_primitives[combination[0]], complex_primitives[combination[1]])
        print('{:.3f}s'.format(time.time() - start))

        print("Environment by Intrusion boolean")
        start = time.time()
        for cp in complex_primitives:
            primitive_complex_boolean(factory, environment, cp)
        print('{:.3f}s'.format(time.time() - start))

        print("Remove All Duplicates")
        start = time.time()
        factory.removeAllDuplicates()
        factory.synchronize()
        print('{:.3f}s'.format(time.time() - start))

        print("Correction and Transfinite")
        start = time.time()
        ss = set()
        for cp in complex_primitives:
            occ_ws.correct_and_transfinite_complex(cp, ss)
        print('{:.3f}s'.format(time.time() - start))

        print("Set Sizes")
        start = time.time()
        for cp in complex_primitives:
            cp.set_size()
        print('{:.3f}s'.format(time.time() - start))

        print("Physical Volumes")
        vs = []
        for cp in complex_primitives:
            vs += cp.get_volumes_by_physical_index(int_physical_tag)
        tag = gmsh.model.addPhysicalGroup(3, vs)
        gmsh.model.setPhysicalName(3, tag, int_name)

        print("Environment Physical")
        tag = gmsh.model.addPhysicalGroup(3, environment.volumes)
        gmsh.model.setPhysicalName(3, tag, "Environment")
        volumes_dim_tags = map(lambda x: (3, x), environment.volumes)
        surfaces_dim_tags = gmsh.model.getBoundary(volumes_dim_tags, combined=False)
        surfaces_names = ["X", "Z", "NY", "NZ", "Y", "NX"]
        for i in range(len(surfaces_names)):
            tag = gmsh.model.addPhysicalGroup(surfaces_dim_tags[i][0], [surfaces_dim_tags[i][1]])
            gmsh.model.setPhysicalName(2, tag, surfaces_names[i])
            #     gmsh.model.setPhysicalName(2, tag, 'S%s' % i)

        gmsh.model.mesh.generate(3)

        gmsh.model.mesh.removeDuplicateNodes()

        gmsh.write("test_read_complex_primitives.msh")

        gmsh.finalize()

        print('\nElapsed time: {:.3f}s'.format(time.time() - start_time))


if __name__ == '__main__':
    unittest.main()
