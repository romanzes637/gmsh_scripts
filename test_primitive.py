import unittest
from primitive import Primitive
import gmsh


class MyTestCase(unittest.TestCase):
    def test_something(self):
        # Before using any functions in the Python API, Gmsh must be initialized.
        gmsh.initialize()

        gmsh.option.setNumber("Geometry.AutoCoherence", 0)

        # By default Gmsh will not print out any messages: in order to output messages
        # on the terminal, just set the standard Gmsh option "General.Terminal" (same
        # format and meaning as in .geo files) using gmshOptionSetNumber():
        gmsh.option.setNumber("General.Terminal", 1)

        # This creates a new model, named "t1". If gmshModelCreate() is not called, a
        # new default (unnamed) model will be created on the fly, if necessary.
        gmsh.model.add("primitive")

        factory = gmsh.model.occ

        primitives = []
        for m in range(2):
            primitives.append(Primitive(
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
                [m * 5, m * 5, m * 5, 0, 0, 0, 3.14 / 4, 3.14 / 6, 3.14 / 8],
                # [4, 0, 0, 0, 0, 0, 0, 1, 0, 0, 2, 0],
                [4, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
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
                1,
                factory
            ))
            primitives[m].create()

        factory.synchronize()

        print(primitives[0].get_surfaces())
        print(primitives[0].get_surfaces(oriented=True))
        print(primitives[0].get_surfaces(combined=True))
        print(primitives[0].get_surfaces(recursive=True))

        print(primitives[0].surfaces)
        sf = [1, 2]
        dim_tags = zip([2] * len(sf), sf)

        factory.remove(dim_tags, recursive=True)

        factory.synchronize()

        # sfgs = []
        # for primitive in primitives:
        #     sfgs.append(gmsh.model.addPhysicalGroup(2, primitive.surfaces))
        # for m in range(len(sfgs)):
        #     gmsh.model.setPhysicalName(2, sfgs[m], "S%s" % m)

        # vfgs = []
        # for primitive in primitives:
        #     vfgs.append(gmsh.model.addPhysicalGroup(3, primitive.volumes))
        # for m in range(len(vfgs)):
        #     gmsh.model.setPhysicalName(3, vfgs[m], "V%s" % m)

        # out1, out2 = factory.fuse(
        #     [(3, primitives[0].volumes[0])],
        #     [(3, primitives[1].volumes[0])],
        #     tag=-1,
        #     removeObject=True,
        #     removeTool=True
        # )

        # intersect(objectDimTags,
        #           toolDimTags,
        #           tag=-1,
        #           removeObject=True,
        #           removeTool=True):
        # def cut(objectDimTags,toolDimTags,tag=-1,removeObject=True,removeTool=True):
        out1, out2 = factory.fragment(
            [(3, primitives[0].volumes[0])],
            [(3, primitives[1].volumes[0])],
            tag=-1,
            removeObject=True,
            removeTool=True
        )
        print(out1)
        print(out2)
        # factory.removeAllDuplicates()
        factory.synchronize()

        # pg = gmsh.model.addPhysicalGroup(3, [out1[0][1]])
        # gmsh.model.setPhysicalName(3, pg, "FV")

        # for primitive in primitives:
        # primitive.check_tags()
        # primitive.transfinite()
        # primitive.recombine()
        # primitive.smooth(50)

        # for primitive in primitives:
        #     primitive.check_tags()

        gmsh.model.mesh.generate(3)

        # gmsh.model.mesh.removeDuplicateNodes()

        gmsh.write("primitive.msh")

        gmsh.finalize()


if __name__ == '__main__':
    unittest.main()
