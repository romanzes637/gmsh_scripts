import unittest
import logging
import time
from itertools import product

import numpy as np
import gmsh

from block import Block
from matrix import Matrix
from coordinate_system import Path
from registry import reset as reset_registry
from support import timeit, GmshDecorator, GmshOptionsDecorator, LoggingDecorator
from strategy import Boolean, Simple
from size import BooleanPoint, BooleanEdge, Bagging

logging.basicConfig(level=logging.INFO)


class TestMatrix(unittest.TestCase):

    @LoggingDecorator()
    @GmshDecorator()
    @GmshOptionsDecorator()
    def test_init_3x3(self):
        for factory in ['geo']:
            model_name = f'test_matrix_init_3x3-{factory}'
            m = Matrix(points=[['-1', '1:4;.2:-3:0.5:0.5'],
                               ['-1', '1:4;.2:-3:0.5:0.5'],
                               ['-1;0.5', '1:4:2:2;2']])
            Simple(factory, model_name)(m)

    @GmshDecorator()
    def test_init(self):
        for factory in ['geo', 'occ']:
            reset_registry()
            model_name = f'test_matrix_init_{factory}'
            logging.info(model_name)
            gmsh.model.add(model_name)
            ms = []
            m1 = Matrix(factory=factory, points=[
                [1, 2],
                ['360:6'],
                ['360:6'],
                [10, 20, 30, 40],
                [1.5, 1.5, 0.75, 0.75],
                [1.5, 0.75, 1.5, 0.75],
                'tokamak',
                'trace'
            ], transforms=['tok2car', [0, 0, -50]])
            ms.append(m1)
            m2 = Matrix(factory=factory, points=[
                [1, 2],
                ['360:6'],
                ['360:6'],
                [10, 20, 30],
                [0.75],
                [1.5],
                'tokamak',
                'product'
            ], transforms=['tok2car', [0, 0, 50]])
            ms.append(m2)
            m3 = Matrix(factory=factory, points=[
                [1, 2],
                ['360:6'],
                [0, 1],
                'cyl',
            ], transforms=['cyl2car', [-50, 0, 0]])
            ms.append(m3)
            m4 = Matrix(factory=factory, points=[
                [1, 2],
                ['360:6'],
                ['360:6'],
                [10],
                'tor'
            ], transforms=['tor2car', [0, -50, 0]])
            ms.append(m4)
            m5 = Matrix(factory=factory, points=[
                [1, 2, 3],
                ['360:6'],
                ['increment', 10, '160:10'],
                'sph'
            ], transforms=['sph2car', [50, 0, 0]])
            ms.append(m5)
            curves = [['line', [[10, 0, x], [10, 0, x + 10], 'sph']]
                      for x in np.linspace(0, 80, 9)]
            orientations = [[[1, 180, x], 'sph'] for x in np.linspace(90, 0, 10)]
            p = Path(factory=factory, curves=curves, orientations=orientations)
            points = [
                ['1:3'],
                ['1:3'],
                # ['1:21:1.5:1.5'],
                ['1:5'],
                p
                # 'trace' by default
            ]
            m6 = Matrix(factory=factory, points=points, transforms=['pat2car'])
            ms.append(m6)
            for i, m in enumerate(ms):
                t0 = time.perf_counter()
                m.transform()
                logging.info(f'Transform_{i + 1} {time.perf_counter() - t0}')
                t0 = time.perf_counter()
                m.register()
                logging.info(f'Register_{i + 1} {time.perf_counter() - t0}')
            if factory == 'geo':
                for m in ms:
                    m.quadrate()
                    m.structure()
                gmsh.model.geo.synchronize()
            elif factory == 'occ':
                gmsh.model.occ.synchronize()
                for m in ms:
                    m.quadrate()
                    m.structure()
            else:
                raise ValueError(factory)
            gmsh.write(f'{model_name}.geo_unrolled')

    @GmshDecorator()
    def test_map(self):
        for factory in ['geo', 'occ']:
            reset_registry()
            use_register_tag = False
            model_name = f'test_matrix_map_{factory}'
            logging.info(model_name)
            gmsh.model.add(model_name)
            points = [
                [1, 2, 3],  # r - inner radius (r < r2)
                ['180:5', '360:5'],  # phi - inner angle [0, 2*pi)
                ['180:5', '360:5'],  # theta - outer angle [0, 2*pi)
                [12, 24, 36, 48],  # r2 - outer radius
                [1.5, 1.5, 0.75, 0.75],  # kxy - inner radius XY scale coefficient in positive outer radius direction
                [1.5, 0.75, 1.5, 0.75],  # kz - inner radius Z scale coefficient
                'tokamak',
                'trace'
            ]
            do_register_map = [
                # param 1: [12, 1.5, 1.5]
                # Z1
                1, 1,  # Y1, X1, X2
                1, 1,  # Y2, X1, X2
                # Z2
                0, 0,  # Y1, X1, X2
                0, 0,  # Y2, X1, X2
                # param 2: [24, 1.5, 0.75]
                # Z1
                1, 1,  # Y1, X1, X2
                0, 0,  # Y2, X1, X2
                # Z2
                1, 1,  # Y1, X1, X2
                0, 0,  # Y2, X1, X2
                # param 3: [36, 0.75, 1.5]
                # Z1
                1, 0,  # Y1, X1, X2
                1, 0,  # Y2, X1, X2
                # Z2
                1, 0,  # Y1, X1, X2
                1, 0,  # Y2, X1, X2
                # param 4: [48, 0.75, 0.75]
                # Z1
                1, 1,  # Y1, X1, X2
                1, 1,  # Y2, X1, X2
                # Z2
                1, 1,  # Y1, X1, X2
                1, 1,  # Y2, X1, X2
            ]
            m_trace = Matrix(factory=factory, points=points,
                             use_register_tag=use_register_tag,
                             transforms=['tok2car'],
                             do_register_map=do_register_map)
            points = [
                [1, 2, 3],  # r - inner radius (r < r2)
                ['180:5', '360:5'],  # phi - inner angle [0, 2*pi)
                ['180:5', '360:5'],  # theta - outer angle [0, 2*pi)
                [60, 72, 84],  # r2 - outer radius
                [0.75],  # kxy - inner radius XY scale coefficient in positive outer radius direction
                [1.5],  # kz - inner radius Z scale coefficient
                'tokamak',
                'product'
            ]
            do_register_map = [
                # param 1: [60, 0.75, 1.5]
                # Z1
                1, 1,  # Y1, X1, X2
                1, 1,  # Y2, X1, X2
                # Z2
                0, 0,  # Y1, X1, X2
                0, 0,  # Y2, X1, X2
                # param 2: [72, 0.75, 1.5]
                # Z1
                1, 1,  # Y1, X1, X2
                0, 0,  # Y2, X1, X2
                # Z2
                1, 1,  # Y1, X1, X2
                0, 0,  # Y2, X1, X2
                # param 3: [84, 0.75, 1.5]
                # Z1
                1, 0,  # Y1, X1, X2
                1, 0,  # Y2, X1, X2
                # Z2
                1, 0,  # Y1, X1, X2
                1, 0,  # Y2, X1, X2
            ]
            m_product = Matrix(factory=factory, points=points,
                               use_register_tag=use_register_tag,
                               transforms=['tok2car'],
                               do_register_map=do_register_map)
            t0 = time.perf_counter()
            m_trace.transform()
            m_product.transform()
            print(f'Transform {time.perf_counter() - t0}')
            t0 = time.perf_counter()
            m_trace.register()
            m_product.register()
            print(f'Register {time.perf_counter() - t0}')
            t0 = time.perf_counter()
            if factory == 'geo':
                m_trace.quadrate()
                m_product.quadrate()
                m_trace.structure()
                m_product.structure()
                gmsh.model.geo.synchronize()
            elif factory == 'occ':
                gmsh.model.occ.synchronize()
                m_trace.quadrate()
                m_product.quadrate()
                m_trace.structure()
                m_product.structure()
            else:
                raise ValueError(factory)
            print(f'Synchronize {time.perf_counter() - t0}')
            gmsh.write(f'{model_name}.geo_unrolled')
            # gmsh.model.mesh.generate(3)
            # gmsh.write(f'{model_name}.msh2')

    @GmshDecorator()
    def test_boolean(self):
        # https://gmsh.info/doc/texinfo/gmsh.html#Choosing-the-right-unstructured-algorithm
        # Gmsh provides a choice between several 2D and 3D unstructured algorithms.
        # Each algorithm has its own advantages and disadvantages.
        #
        # For all 2D unstructured algorithms a Delaunay mesh that contains
        # all the points of the 1D mesh is initially constructed using
        # a divide-and-conquer algorithm5. Missing edges are recovered using
        # edge swaps6. After this initial step several algorithms can be applied
        # to generate the final mesh:
        #
        # The “MeshAdapt” algorithm7 is based on local mesh modifications.
        # This technique makes use of edge swaps, splits, and collapses:
        # long edges are split, short edges are collapsed, and edges are swapped
        # if a better geometrical configuration is obtained.
        # The “Delaunay” algorithm is inspired by the work of the GAMMA team at
        # INRIA8. New points are inserted sequentially at the circumcenter of
        # the element that has the largest adimensional circumradius.
        # The mesh is then reconnected using an anisotropic Delaunay criterion.
        # The “Frontal-Delaunay” algorithm is inspired by the work of S. Rebay9.
        # Other experimental algorithms with specific features are also available.
        # In particular, “Frontal-Delaunay for Quads”10 is a variant of
        # the “Frontal-Delaunay” algorithm aiming at generating right-angle triangles
        # suitable for recombination; and “BAMG”11 allows to generate anisotropic triangulations.
        # For very complex curved surfaces the “MeshAdapt” algorithm is the most robust.
        # When high element quality is important, the “Frontal-Delaunay” algorithm
        # should be tried. For very large meshes of plane surfaces the “Delaunay”
        # algorithm is the fastest; it usually also handles complex mesh size fields
        # better than the “Frontal-Delaunay”. When the “Delaunay” or “Frontal-Delaunay”
        # algorithms fail, “MeshAdapt” is automatically triggered.
        # The “Automatic” algorithm uses “Delaunay” for plane surfaces
        # and “MeshAdapt” for all other surfaces.
        #
        # Several 3D unstructured algorithms are also available:
        #
        # The “Delaunay” algorithm is split into three separate steps.
        # First, an initial mesh of the union of all the volumes in the model
        # is performed, without inserting points in the volume.
        # The surface mesh is then recovered using H. Si’s boundary recovery
        # algorithm Tetgen/BR. Then a three-dimensional version of the
        # 2D Delaunay algorithm described above is applied to insert points in
        # the volume to respect the mesh size constraints.
        # The “Frontal” algorithm uses J. Schoeberl’s Netgen algorithm 12.
        # The “HXT” algorithm13 is a new efficient and parallel reimplementaton
        # of the Delaunay algorithm.
        # Other experimental algorithms with specific features are also available.
        # In particular, “MMG3D”14 allows to generate anisotropic tetrahedralizations.
        # The “Delaunay” algorithm is currently the most robust and is the only
        # one that supports the automatic generation of hybrid meshes with pyramids.
        # Embedded model entities and the Field mechanism to specify element sizes
        # (see Specifying mesh element sizes) are currently only supported by the
        # “Delaunay” and “HXT” algorithms.
        #
        # If your version of Gmsh is compiled with OpenMP support
        # (see Compiling the source code), most of the meshing steps can be performed in parallel:
        #
        # 1D and 2D meshing is parallelized using a coarse-grained approach,
        # i.e. curves (resp. surfaces) are each meshed sequentially, but several
        # curves (resp. surfaces) can be meshed at the same time.
        # 3D meshing using HXT is parallelized using a fine-grained approach,
        # i.e. the actual meshing procedure for a single volume is done is parallel.
        # The number of threads can be controlled with the -nt flag on the command line
        # (see Command-line options), or with the
        # General.NumThreads, Mesh.MaxNumThreads1D, Mesh.MaxNumThreads2D and Mesh.MaxNumThreads3D
        # options (see General options list and Mesh options list).

        # 2D mesh algorithm (1: MeshAdapt, 2: Automatic, 3: Initial mesh only,
        # 5: Delaunay, 6: Frontal-Delaunay, 7: BAMG,
        # 8: Frontal-Delaunay for Quads, 9: Packing of Parallelograms)
        # Default value: 6
        # m2d = {1: 'MeshAdapt', 2: 'Automatic', 3: 'Initial_mesh_only',
        #         5: 'Delaunay', 6: 'Frontal_Delaunay', 7: 'BAMG',
        #         8: 'Frontal_Delaunay_for_Quads', 9: 'Packing_of_Parallelograms'}
        # m2d = {5: 'Delaunay', 6: 'Frontal-Delaunay', 8: 'Frontal-Delaunay for Quads'}
        # m2d = {5: 'Frontal_Delaunay'}
        m2d = {6: 'Frontal_Delaunay', 8: 'Frontal_Delaunay_for_Quads'}
        # m2d = {8: 'Frontal_Delaunay_for_Quads'}

        # 3D mesh algorithm (1: Delaunay, 3: Initial mesh only,
        # 4: Frontal, 7: MMG3D, 9: R_tree, 10: HXT)
        # Default value: 1
        # m3d = {1: 'Delaunay', 3: 'Initial mesh only', 4: 'Frontal', 7: 'MMG3D',
        #         9: 'R_tree', 10: 'HXT'}
        # m3d = {1: 'Delaunay', 4: 'Frontal'}
        m3d = {1: 'Delaunay'}

        # To determine the size of mesh elements, Gmsh locally computes the minimum of
        #
        # 1) the size of the model bounding box;
        # 2) if `Mesh.MeshSizeFromPoints' is set, the mesh size specified at
        #    geometrical points;
        # 3) if `Mesh.MeshSizeFromCurvature' is positive, the mesh size based on
        #    curvature (the value specifying the number of elements per 2 * pi rad);
        # 4) the background mesh size field;
        # 5) any per-entity mesh size constraint.
        #
        # This value is then constrained in the interval [`Mesh.MeshSizeMin',
        # `Mesh.MeshSizeMax'] and multiplied by `Mesh.MeshSizeFactor'.  In addition,
        # boundary mesh sizes (on curves or surfaces) are interpolated inside the
        # enclosed entity (surface or volume, respectively) if the option
        # `Mesh.MeshSizeExtendFromBoundary' is set (which is the case by default).
        #
        # When the element size is fully specified by a background mesh size field (as
        # it is in this example), it is thus often desirable to set
        #
        # Mesh.MeshSizeExtendFromBoundary = 0;
        # Mesh.MeshSizeFromPoints = 0;
        # Mesh.MeshSizeFromCurvature = 0;
        #
        # This will prevent over-refinement due to small mesh sizes on the boundary.

        # Compute mesh element sizes from values given at geometry points
        # Default value: 1
        # msp = {0: 'no_points', 1: "points"}
        msp = {1: "points", 0: 'no_points'}
        # msp = {0: 'no_points'}
        # msp = {1: 'points'}

        # Extend computation of mesh element sizes from the boundaries
        # into the interior (for 3D Delaunay, use 1: longest or
        # 2: shortest surface edge length)
        # Default value: 1
        # msb = {1: "longest_edge", 0: 'no_edge', 2: 'shortest_edge'}
        msb = {2: 'shortest_edge'}

        # To generate quadrangles instead of triangles, we can simply add
        # gmsh.model.mesh.setRecombine(2, pl)
        # If we'd had several surfaces, we could have used the global option
        # "Mesh.RecombineAll":
        #
        # gmsh.option.setNumber("Mesh.RecombineAll", 1)
        #
        # The default recombination algorithm is called "Blossom": it uses a minimum
        # cost perfect matching algorithm to generate fully quadrilateral meshes from
        # triangulations. More details about the algorithm can be found in the
        # following paper: J.-F. Remacle, J. Lambrechts, B. Seny, E. Marchandise,
        # A. Johnen and C. Geuzaine, "Blossom-Quad: a non-uniform quadrilateral mesh
        # generator using a minimum cost perfect matching algorithm", International
        # Journal for Numerical Methods in Engineering 89, pp. 1102-1119, 2012.
        #
        # For even better 2D (planar) quadrilateral meshes, you can try the
        # experimental "Frontal-Delaunay for quads" meshing algorithm, which is a
        # triangulation algorithm that enables to create right triangles almost
        # everywhere: J.-F. Remacle, F. Henrotte, T. Carrier-Baudouin, E. Bechet,
        # E. Marchandise, C. Geuzaine and T. Mouton. A frontal Delaunay quad mesh
        # generator using the L^inf norm. International Journal for Numerical Methods
        # in Engineering, 94, pp. 494-512, 2013. Uncomment the following line to try
        # the Frontal-Delaunay algorithms for quads:
        #
        # gmsh.option.setNumber("Mesh.Algorithm", 8)
        #
        # The default recombination algorithm might leave some triangles in the mesh, if
        # recombining all the triangles leads to badly shaped quads. In such cases, to
        # generate full-quad meshes, you can either subdivide the resulting hybrid mesh
        # (with `Mesh.SubdivisionAlgorithm' set to 1), or use the full-quad
        # recombination algorithm, which will automatically perform a coarser mesh
        # followed by recombination, smoothing and subdivision. Uncomment the following
        # line to try the full-quad algorithm:
        #
        # gmsh.option.setNumber("Mesh.RecombinationAlgorithm", 2) # or 3
        #
        # You can also set the subdivision step alone, with
        #
        # gmsh.option.setNumber("Mesh.SubdivisionAlgorithm", 1)
        #
        # gmsh.model.mesh.generate(2)
        #
        # Note that you could also apply the recombination algorithm and/or the
        # subdivision step explicitly after meshing, as follows:
        #
        # gmsh.model.mesh.generate(2)
        # gmsh.model.mesh.recombine()
        # gmsh.option.setNumber("Mesh.SubdivisionAlgorithm", 1)
        # gmsh.model.mesh.refine()

        # Mesh.RecombinationAlgorithm
        # Mesh recombination algorithm (0: simple, 1: blossom, 2: simple full-quad, 3: blossom full-quad)
        # Default value: 1
        # Saved in: General.OptionsFileName
        # mrb = {0: 'simple', 1: 'blossom', 2: 'simple_full_quad', 3: 'blossom_full_quad'}
        mrb = {3: 'blossom_full_quad'}

        # Mesh subdivision algorithm (0: none, 1: all quadrangles, 2: all hexahedra, 3: barycentric)
        # Default value: 0
        # sd = {0: 'no_subdivision', 1: 'all_quadrangles', 2: 'all_hexahedra', 3: 'barycentric'}
        sd = {0: 'no_subdivision', 2: 'all_hexahedra'}
        # sd = {2: 'all_hexahedra'}
        # sd = {3: 'barycentric'}

        # Mesh.RecombineAll
        # Apply recombination algorithm to all surfaces, ignoring per-surface spec
        # Default value: 0
        # Saved in: General.OptionsFileName

        # Mesh.RecombineOptimizeTopology
        # Number of topological optimization passes (removal of diamonds, ...) of recombined surface meshes
        # Default value: 5
        # Saved in: General.OptionsFileName

        # Mesh.Recombine3DAll
        # Apply recombination3D algorithm to all volumes, ignoring per-volume spec (experimental)
        # Default value: 0
        # Saved in: General.OptionsFileName

        # Mesh.Recombine3DLevel
        # 3d recombination level (0: hex, 1: hex+prisms, 2: hex+prism+pyramids) (experimental)
        # Default value: 0
        # Saved in: General.OptionsFileName

        # Mesh.Recombine3DConformity
        # 3d recombination conformity type (0: nonconforming, 1: trihedra, 2: pyramids+trihedra, 3:pyramids+hexSplit+trihedra, 4:hexSplit+trihedra)(experimental)
        # Default value: 0
        # Saved in: General.OptionsFileName

        # Mesh.Smoothing
        # Number of smoothing steps applied to the final mesh
        # Default value: 1
        # Saved in: General.OptionsFileName

        qd = {0: 'no_quadrate', 1: 'quadrate_in', 2: 'quadrate_out', 3: 'quadrate_in_out'}
        # qd = {1: 'quadrate_in'}
        # st = {0: 'no_structure', 1: 'structure_in', 2: 'structure_out', 3: 'structure_in_out'}
        st = {0: 'no_structure', 1: 'structure_in'}
        # st = {1: 'structure_in'}
        params = list(product(sd.items(), m2d.items(), m3d.items(),
                              msb.items(), msp.items(), mrb.items(),
                              qd.items(), st.items()))
        for i, p in enumerate(params):
            factory = 'occ'
            model_name = f'test_matrix_boolean-{i + 1}_{len(params)}-{factory}-{"-".join([x[1] for x in p])}'
            logging.info(model_name)
            sd, m2d, m3d, msb, msp, mrb, qd, st = p
            reset_registry()
            gmsh.model.add(model_name)
            gmsh.option.setNumber('Geometry.OCCParallel', 1)
            gmsh.option.setNumber("Mesh.SubdivisionAlgorithm", sd[0])
            gmsh.option.setNumber("Mesh.RecombinationAlgorithm", mrb[0])
            gmsh.option.setNumber("Mesh.Algorithm", m2d[0])
            gmsh.option.setNumber("Mesh.Algorithm3D", m3d[0])
            gmsh.option.setNumber("Mesh.MeshSizeExtendFromBoundary", msb[0])
            # Factor applied to all mesh element sizes
            # Default value: 1
            gmsh.option.setNumber("Mesh.MeshSizeFactor", 1)
            # Mesh.MeshSizeMin
            # Default value: 0
            gmsh.option.setNumber("Mesh.MeshSizeMin", 0)
            # Maximum mesh element size
            # Default value: 1e+22
            gmsh.option.setNumber("Mesh.MeshSizeMax", 1e+22)
            # Automatically compute mesh element sizes from curvature,
            # using the value as the target number of elements per 2 * Pi radians
            # Default value: 0
            gmsh.option.setNumber("Mesh.MeshSizeFromCurvature", 0)
            # Force isotropic curvature estimation when the mesh size
            # is computed from curvature
            # Default value: 0
            gmsh.option.setNumber("Mesh.MeshSizeFromCurvatureIsotropic", 0)
            gmsh.option.setNumber("Mesh.MeshSizeFromPoints", msp[0])
            # Compute mesh element sizes from values given at geometry
            # points defining parametric curves
            gmsh.option.setNumber("Mesh.MeshSizeFromParametricPoints", 0)
            boolean_with_bboxes = True
            if qd[0] == 0:
                quadrate_in, quadrate_out = None, None
            elif qd[0] == 1:
                quadrate_in, quadrate_out = True, None
            elif qd[0] == 2:
                quadrate_in, quadrate_out = None, True
            elif qd[0] == 3:
                quadrate_in, quadrate_out = True, True
            else:
                raise ValueError(qd)
            if st[0] == 0:
                structure_in, structure_out = None, None
            elif st[0] == 1:
                structure_in = [[3, 0, 1], [4, 0, 1], [5, 0, 1]]
                structure_out = None
            elif st[0] == 2:
                structure_in = None
                structure_out = [[3, 0, 1], [4, 0, 1], [5, 0, 1]]
            elif st[0] == 3:
                structure_in = [[3, 0, 1], [4, 0, 1], [5, 0, 1]]
                structure_out = [[3, 0, 1], [4, 0, 1], [5, 0, 1]]
            else:
                raise ValueError(st)
            try:
                b = Block(factory=factory, points=[10, 20, 30, 5.0],
                          boolean_level=0,
                          structure=structure_out,
                          quadrate=quadrate_out,
                          zone='Block1')
                b2 = Block(factory=factory, parent=b, points=[1, 2, 3, 0.5],
                           boolean_level=1,
                           structure=structure_in,
                           quadrate=quadrate_in,
                           zone='Block2')
                b.add_child(b2)
                Boolean()(factory, model_name, b)
            except Exception as e:
                logging.warning(e)
                with open(f'{model_name}.txt', 'a') as f:
                    f.write(f'{e}')
            finally:
                try:
                    gmsh.model.remove()
                except Exception as e:
                    logging.warning(e)
                    with open(f'{model_name}.txt', 'a') as f:
                        f.write(f'{e}')

    @GmshDecorator()
    def test_boolean_tunnels(self):
        m2d = {'Frontal_Delaunay': 6}
        m3d = {'Delaunay': 1}
        # sd = {'all_hexahedra': 2, 'no_subdivision': 0}
        sd = {'all_hexahedra': 2}
        # st = {'structure_quadrate': 2, 'no_structure': 0, 'structure': 1}
        st = {'structure_quadrate': 2}
        # st = {'structure': 1}
        # st = {'no_structure': 0}
        # msb = {'longest_edge': 1, 'no_edge': 0, 'shortest_edge': 2}
        msb = {'shortest_edge': 2, 'longest_edge': 1}
        # msp = {'points': 1, 'points.5x': 1, 'no_points': 0, 'points2x': 1}
        msp = {'points': 1, 'points.5x': 1, 'points2x': 1}
        # para = {'parallel': 1, 'no_parallel': 0}
        para = {'parallel': 1}
        strategy = {'boolean_point_min': 1, 'boolean_point_edge_mean': 2}
        factory = 'occ'
        params = list(product(m2d.items(), m3d.items(),  sd.items(), st.items(),
                              msb.items(), msp.items(),
                              para.items(), strategy.items()))
        for i, p in enumerate(params):
            m2d, m3d, sd, st, msb, msp, para, strategy = p
            model_name = f'test_boolean_tunnels-{i + 1}_{len(params)}-{"-".join(x[0] for x in p)}'
            logging.info(model_name)
            gmsh.option.setNumber('Geometry.OCCParallel', para[1])
            # General.NumThreads, Mesh.MaxNumThreads1D, Mesh.MaxNumThreads2D and Mesh.MaxNumThreads3D
            gmsh.option.setNumber("Mesh.Algorithm", m2d[1])
            gmsh.option.setNumber("Mesh.Algorithm3D", m3d[1])
            gmsh.option.setNumber("Mesh.SubdivisionAlgorithm", sd[1])
            gmsh.option.setNumber("Mesh.MeshSizeExtendFromBoundary", msb[1])
            gmsh.option.setNumber("Mesh.MeshSizeFromPoints", msp[1])
            # gmsh.option.setNumber("Mesh.MeshSizeFactor", 1)
            # gmsh.option.setNumber("Mesh.MeshSizeMin", 0)
            # gmsh.option.setNumber("Mesh.MeshSizeMax", 1e+22)
            # gmsh.option.setNumber("Mesh.MeshSizeFromCurvature", 0)
            # gmsh.option.setNumber("Mesh.MeshSizeFromCurvatureIsotropic", 0)
            # gmsh.option.setNumber("Mesh.MeshSizeFromParametricPoints", 0)
            if msp[0] in ['points', 'no_points']:
                mesh_size = 1
            elif msp[0] == 'points2x':
                mesh_size = 2
            elif msp[0] == 'points.5x':
                mesh_size = 0.5
            else:
                raise ValueError(msp)
            if st[0] == 'no_structure':
                structure_all, quadrate_all = None, None
            elif st[0] == 'structure':
                structure_all = [[3, 0, 1], [4, 0, 1], [5, 0, 1]]
                quadrate_all = None
            elif st[0] == 'structure_quadrate':
                # gmsh.option.setNumber("Mesh.RecombineAll", 1)
                structure_all = [[3, 0, 1], [4, 0, 1], [5, 0, 1]]
                quadrate_all = True
            else:
                raise ValueError(st)
            # b = Block(factory=factory,
            #           points=[10, 20, 30, mesh_size],
            #           boolean_level=0,
            #           structure_all=None,
            #           quadrate_all=None,
            #           zone_all='Rock')
            b = Matrix(factory=factory,
                       points=[
                           [-5, '5:4'],
                           [-10, '10:4'],
                           [-15, '15:4'],
                           mesh_size],
                       structure_map=structure_all,
                       quadrate_map=quadrate_all,
                       boolean_level_map=0,
                       zone_map='Rock')
            curves = [['line', [[10, 0, x], [10, 0, x + 10], 'sph']]
                      for x in np.linspace(0, 80, 9)]
            orientations = [[[1, 180, x], 'sph'] for x in np.linspace(90, 0, 10)]
            points = [
                [0, f'1:2;{.5*mesh_size}'],
                [0, f'1:2;{.5*mesh_size}'],
                [0, f'1:3;{.5*mesh_size}'],
                Path(factory=factory, curves=curves, orientations=orientations)
                # 'trace' by default
            ]
            m = Matrix(factory=factory, points=points,
                       parent=b,
                       transforms=['pat2car', [-5, 0, -15]],
                       structure_map=structure_all,
                       quadrate_map=quadrate_all,
                       boolean_level_map=1,
                       zone_map='Tunnel1')
            b.add_child(m)
            m = Matrix(factory=factory, points=points,
                       parent=b,
                       transforms=['pat2car',
                                   [5, 0, 0, 0, 0, 1, 45], [-5, 0, -15]],
                       structure_map=structure_all,
                       quadrate_map=quadrate_all,
                       boolean_level_map=1,
                       zone_map='Tunnel2')
            b.add_child(m)
            if strategy[0] == 'boolean_edge_max':
                Boolean(size_function=BooleanEdge(intra_function='max'))(
                    factory, model_name, b,)
            elif strategy[0] == 'boolean_point_min':
                Boolean(size_function=BooleanPoint(intra_function='min'))(
                    factory, model_name, b,)
            elif strategy[0] == 'boolean_point_edge_mean':
                Boolean(size_function=Bagging(inter_function='mean', sizes=(
                        BooleanPoint(intra_function='min'),
                        BooleanEdge(intra_function='max'))))(
                    factory, model_name, b,)
            else:
                raise ValueError(strategy)


if __name__ == '__main__':
    unittest.main()
