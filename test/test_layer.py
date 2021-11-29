import unittest

import numpy as np

from support import GmshDecorator, LoggingDecorator, GmshOptionsDecorator
from strategy import Simple, Fast, Boolean
from layer import Layer
from matrix import Matrix
from coordinate_system import Path
from zone import BlockSimple, NoZone, BlockVolumes, Mesh
from zone import Boolean as BooleanZone
from structure import NoStructure
from quadrate import NoQuadrate
from size import NoSize
from boolean import Boolean as BooleanFunction
from boolean import BooleanBoundingBox, BooleanAll, BooleanAllBlock
from support import timeit


class TestLayer(unittest.TestCase):

    @LoggingDecorator(level='DEBUG')
    @GmshDecorator()
    @GmshOptionsDecorator()
    def test_layer(self):
        for factory in ['geo', 'occ']:
            model_name = f'test_layer-{factory}'
            layer = Layer(
                layers=[['1;.4;3', '2;.3', '3;.5'],
                        ['1;.3', '2;.3']],
                layers_curves=[['line', 'line', 'circle_arc'],
                               ['line', 'line']],
                layers_types=[['in', 'in', 'in'],
                              ['in', 'in']],
                do_register_map=[[[1, 1, 1],
                                  [1, 1, 1]]],
                boolean_level_map=[[[0, 1, 2],
                                    [3, 4, 5]]]
                # transforms=[[3, 0, 1]]
            )
            Fast(factory, model_name)(layer)

    @LoggingDecorator(level='DEBUG')
    @GmshDecorator()
    @GmshOptionsDecorator()
    def test_layer_one(self):
        for factory in ['geo', 'occ']:
            model_name = f'test_layer_one-{factory}'
            layer = Layer(
                layers=[['1;.4;3', '2;.3'],
                        ['1;.3']],
                layers_curves=[['line', 'circle_arc'],
                               ['line']]
            )
            Fast(factory, model_name)(layer)

    @LoggingDecorator(level='DEBUG')
    @GmshDecorator()
    @GmshOptionsDecorator()
    def test_layer_one_ext(self):
        for factory in ['geo', 'occ']:
            model_name = f'test_layer_one_ext-{factory}'
            layer = Layer(
                layers=[['1;.4;3', '2:3;.3;4'],
                        ['1;.4;3', '2:3;.3;4'],
                        ['1;.4;3', '2:3;.3;4'],
                        ['1;.4;3', '2:3;.3;4'],
                        ['1:5;.3;5']],
                layers_curves=[['circle_arc', ['spline', [[.3, .1, 0], [.7, .1, 0]]]],
                               ['circle_arc', 'line'],
                               ['circle_arc', ['spline', [[.3, -.1, 0], [.7, -.1, 0]]]],
                               ['circle_arc', 'line'],
                               ['line']]
            )
            Fast(factory, model_name)(layer)

    @LoggingDecorator(level='DEBUG')
    @GmshDecorator()
    @GmshOptionsDecorator()
    def test_layer_path(self):
        for factory in ['geo', 'occ']:
            model_name = f'test_layer_path-{factory}'
            curves = [['line', [[10, 0, x], [10, 0, x + 10], 'sph']]
                      for x in np.linspace(0, 80, 9)]
            orientations = [[[1, 180, x], 'sph'] for x in np.linspace(90, 0, 10)]
            cs = Path(factory=factory, curves=curves, orientations=orientations)
            layer = Layer(
                layers=[['1;1', '2;1', '3;1'],
                        ['1:8;1'],
                        cs],
                layers_curves=[['line', 'line', 'circle_arc'],
                               ['line']]
            )
            Fast(factory, model_name)(layer)

    @LoggingDecorator(level='DEBUG')
    @GmshDecorator()
    @GmshOptionsDecorator({
        # Use generic algorithm to compute point projections in
        # the OpenCASCADE kernel (less robust, but significally faster in
        # some configurations)
        # Default value: 0
        "Mesh.Algorithm": 6,
        # 2D mesh algorithm (1: MeshAdapt, 2: Automatic,
        # 3: Initial mesh only, 5: Delaunay, 6: Frontal-Delaunay, 7: BAMG,
        # 8: Frontal-Delaunay for Quads, 9: Packing of Parallelograms)
        # Default value: 6
        'Mesh.Algorithm3D': 1,
        # 3D mesh algorithm (1: Delaunay, 3: Initial mesh only, 4: Frontal,
        # 7: MMG3D, 9: R_tree, 10: HXT)
        # Default value: 1
        'Mesh.MeshSizeFromCurvature': 10,  # Default value: 0
        # Automatically compute mesh element sizes from curvature, using
        # the value as the target number of elements per 2 * Pi radians
        'Mesh.SubdivisionAlgorithm': 2,  # Default value: 0, 2 for hexahedral mesh
        # Mesh subdivision algorithm (0: none, 1: all quadrangles,
        # 2: all hexahedra, 3: barycentric)
        'Mesh.RecombinationAlgorithm': 1,  # No effect
        # Mesh recombination algorithm (0: simple, 1: blossom,
        # 2: simple full-quad, 3: blossom full-quad)
        # Default value: 1
        'Mesh.RecombineAll': 0,
        # Apply recombination algorithm to all surfaces,
        # ignoring per-surface spec
        # Default value: 0
        'Mesh.RecombineOptimizeTopology': 5,  # No effect
        # Mesh.RecombineOptimizeTopology
        # Number of topological optimization passes (removal of diamonds,
        # ...) of recombined surface meshes
        # Default value: 5
        'Mesh.Recombine3DAll': 0,  # No effect
        # Apply recombination3D algorithm to all volumes, ignoring
        # per-volume spec (experimental)
        # Default value: 0
        'Mesh.Recombine3DLevel': 0,
        # 3d recombination level (0: hex, 1: hex+prisms, 2: hex+prism+pyramids)
        # (experimental)
        # Default value: 0
        'Mesh.Recombine3DConformity': 0,  # Negligible effect
        # 3d recombination conformity type (0: nonconforming, 1: trihedra,
        # 2: pyramids+trihedra, 3:pyramids+hexSplit+trihedra,
        # 4:hexSplit+trihedra) (experimental)
        # Default value: 0
    })
    def test_layer_boolean(self):
        """Test 2 Layers in the Matrix boolean

        Issues:
            1. PCL Error: A segment and a facet intersect at point
                Solution: Set appropriate mesh size or use MeshSizeFromCurvature
                See: https://gitlab.onelab.info/gmsh/gmsh/-/issues/766
        """
        factory = 'occ'
        model_name = f'test_layer_boolean-{factory}'
        curves = [['line', [[10, 0, x], [10, 0, x + 10], 'sph']]
                  for x in np.linspace(0, 80, 9)]
        orientations = [[[1, 180, x], 'sph'] for x in np.linspace(90, 0, 10)]
        cs = Path(factory=factory, curves=curves, orientations=orientations)
        b = Matrix(points=[[0, 15], [-7, 7], [0, 13]], zones=["M"],
                   boolean_level_map=0)
        layer = Layer(
            layers=[['1;1;5', '1.5;1;5'],
                    ['1:5;1;3'],
                    cs],
            layers_curves=[['line', 'circle_arc'],
                           ['line']],
            zones=['L1'],
            boolean_level_map=1,
            quadrate_map=0,
            do_unregister_map=0,
            do_unregister_boolean_map=0,
            parent=b
        )
        b.add_child(layer)
        layer2 = Layer(
            layers=[['1;1;3', '1.5;1;3'],
                    # ['.1;1;3', '.8;1;3', '1;1;3'],
                    ['1:5;1;3'],
                    cs],
            layers_curves=[['line', 'circle_arc'],
                           ['line']],
            transforms=[[0, 0, 0, 0, 0, 1, 80], [5, -5, 0]],
            boolean_level_map=1,
            do_unregister_map=1,
            do_unregister_boolean_map=1,
            quadrate_map=1,
            zones=['L2'],
            parent=b
        )
        b.add_child(layer2)
        s = Boolean(factory, model_name,
                    boolean_function=BooleanAllBlock(),
                    # structure_function=NoStructure(),
                    quadrate_function=NoQuadrate(),
                    size_function=NoSize(),
                    zone_function=BooleanZone(dims_interfaces=()))
        timeit(s)(b)
