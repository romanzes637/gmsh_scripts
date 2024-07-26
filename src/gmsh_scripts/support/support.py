import logging
import time
import os
import socket
import sys
import getpass
from pathlib import Path

import numpy as np
import gmsh


class LoggingDecorator:
    """Decorator for logger initialization

    Args:
        filename (str): path to log file
        filemode (str): mode of log file
        fmt (str): format of messages
            See https://docs.python.org/3/library/logging.html#logrecord-attributes
        datefmt (str): format of the date
        level (int or str): CRITICAL = 50, FATAL = CRITICAL, ERROR = 40,
            WARNING = 30, WARN = WARNING, INFO = 20, DEBUG = 10, NOTSET = 0
    """

    def __init__(self, filename=None, filemode='a', fmt=None, datefmt=None,
                 level='INFO'):
        self.filename = filename
        self.filemode = filemode
        self.level = level
        if fmt is None:
            fmt = '%(asctime)s.%(msecs)03d%(tz)s|' \
                  '%(hostname)s|%(ip)s|%(user)s|%(process)d|' \
                  '%(levelname)s|%(filename)s|%(lineno)d|%(message)s'
        self.fmt = fmt
        self.datefmt = '%Y-%m-%dT%H:%M:%S' if datefmt is None else datefmt

    def __call__(self, f=None):
        def wrapper(*args, **kwargs):
            try:
                hostname = socket.gethostname()
            except Exception:
                hostname = 'hostname'
            try:
                ip = socket.gethostbyname(hostname)
            except Exception:
                ip = '127.0.0.1'
            try:
                user = getpass.getuser()
            except Exception:
                user = 'user'
            try:
                tz = time.strftime('%z')
            except Exception:
                tz = ''

            fmt = self.fmt.replace('%(hostname)s', hostname)
            fmt = fmt.replace('%(ip)s', ip)
            fmt = fmt.replace('%(user)s', user)
            fmt = fmt.replace('%(tz)s', tz)
            filename = self.filename if self.filename is None else Path(self.filename).resolve()
            logging.basicConfig(filename=filename,
                                filemode=self.filemode,
                                format=fmt, datefmt=self.datefmt,
                                level=self.level)
            logging.info('Logging initialized')
            logging.info(f'hostname: {hostname}')
            logging.info(f'ip: {ip}')
            logging.info(f'user: {user}')
            logging.info(f'pid: {os.getpid()}')
            logging.info(f'python: {sys.executable}')
            logging.info(f'script: {__file__}')
            logging.info(f'working directory: {os.getcwd()}')
            out = f(*args, **kwargs) if f is not None else None
            return out

        return wrapper


class GmshDecorator:
    """Decorator fot gmsh initialization

    1. Initialize
    2. Call function
    3. Finalize
    """

    def __init__(self):
        pass

    def __call__(self, f=None):
        def wrapper(*args, **kwargs):
            gmsh.initialize()
            logging.info('Gmsh initialized')
            out = f(*args, **kwargs) if f is not None else None
            gmsh.finalize()
            logging.info('Gmsh finalized')
            return out

        return wrapper


class GmshOptionsDecorator:
    """Decorator for setting gmsh options

    1. Set options
    2. Call function

    Options:
        https://gmsh.info/doc/texinfo/gmsh.html#Options

    Unstructured mesh:
        Gmsh provides a choice between several 2D and 3D unstructured algorithms.
        Each algorithm has its own advantages and disadvantages.

        For all 2D unstructured algorithms a Delaunay mesh that contains
        all the points of the 1D mesh is initially constructed using
        a divide-and-conquer algorithm5. Missing edges are recovered using
        edge swaps6. After this initial step several algorithms can be applied
        to generate the final mesh:

        The “MeshAdapt” algorithm7 is based on local mesh modifications.
        This technique makes use of edge swaps, splits, and collapses:
        long edges are split, short edges are collapsed, and edges are swapped
        if a better geometrical configuration is obtained.
        The “Delaunay” algorithm is inspired by the work of the GAMMA team at
        INRIA8. New points are inserted sequentially at the circumcenter of
        the element that has the largest adimensional circumradius.
        The mesh is then reconnected using an anisotropic Delaunay criterion.
        The “Frontal-Delaunay” algorithm is inspired by the work of S. Rebay9.
        Other experimental algorithms with specific features are also available.
        In particular, “Frontal-Delaunay for Quads”10 is a variant of
        the “Frontal-Delaunay” algorithm aiming at generating right-angle triangles
        suitable for recombination; and “BAMG”11 allows to generate anisotropic triangulations.
        For very complex curved surfaces the “MeshAdapt” algorithm is the most robust.
        When high element quality is important, the “Frontal-Delaunay” algorithm
        should be tried. For very large meshes of plane surfaces the “Delaunay”
        algorithm is the fastest; it usually also handles complex mesh size fields
        better than the “Frontal-Delaunay”. When the “Delaunay” or “Frontal-Delaunay”
        algorithms fail, “MeshAdapt” is automatically triggered.
        The “Automatic” algorithm uses “Delaunay” for plane surfaces
        and “MeshAdapt” for all other surfaces.

        Several 3D unstructured algorithms are also available:

        The “Delaunay” algorithm is split into three separate steps.
        First, an initial mesh of the union of all the volumes in the model
        is performed, without inserting points in the volume.
        The surface mesh is then recovered using H. Si’s boundary recovery
        algorithm Tetgen/BR. Then a three-dimensional version of the
        2D Delaunay algorithm described above is applied to insert points in
        the volume to respect the mesh size constraints.
        The “Frontal” algorithm uses J. Schoeberl’s Netgen algorithm 12.
        The “HXT” algorithm13 is a new efficient and parallel reimplementaton
        of the Delaunay algorithm.
        Other experimental algorithms with specific features are also available.
        In particular, “MMG3D”14 allows to generate anisotropic tetrahedralizations.
        The “Delaunay” algorithm is currently the most robust and is the only
        one that supports the automatic generation of hybrid meshes with pyramids.
        Embedded model entities and the Field mechanism to specify element sizes
        (see Specifying mesh element sizes) are currently only supported by the
        “Delaunay” and “HXT” algorithms.

        If your version of Gmsh is compiled with OpenMP support
        (see Compiling the source code), most of the meshing steps can be performed in parallel:

        1D and 2D meshing is parallelized using a coarse-grained approach,
        i.e. curves (resp. surfaces) are each meshed sequentially, but several
        curves (resp. surfaces) can be meshed at the same time.
        3D meshing using HXT is parallelized using a fine-grained approach,
        i.e. the actual meshing procedure for a single volume is done is parallel.
        The number of threads can be controlled with the -nt flag on the command line
        (see Command-line options), or with the
        General.NumThreads, Mesh.MaxNumThreads1D, Mesh.MaxNumThreads2D and Mesh.MaxNumThreads3D
        options (see General options list and Mesh options list).
        To determine the size of mesh elements, Gmsh locally computes the minimum of

        1) the size of the model bounding box;
        2) if `Mesh.MeshSizeFromPoints' is set, the mesh size specified at
           geometrical points;
        3) if `Mesh.MeshSizeFromCurvature' is positive, the mesh size based on
           curvature (the value specifying the number of elements per 2 * pi rad);
        4) the background mesh size field;
        5) any per-entity mesh size constraint.

        This value is then constrained in the interval [`Mesh.MeshSizeMin',
        `Mesh.MeshSizeMax'] and multiplied by `Mesh.MeshSizeFactor'.  In addition,
        boundary mesh sizes (on curves or surfaces) are interpolated inside the
        enclosed entity (surface or volume, respectively) if the option
        `Mesh.MeshSizeExtendFromBoundary' is set (which is the case by default).

        When the element size is fully specified by a background mesh size field (as
        it is in this example), it is thus often desirable to set

        Mesh.MeshSizeExtendFromBoundary = 0;
        Mesh.MeshSizeFromPoints = 0;
        Mesh.MeshSizeFromCurvature = 0;

        This will prevent over-refinement due to small mesh sizes on the boundary.

    Quadrate:
        To generate quadrangles instead of triangles, we can simply add
        gmsh.model.mesh.setRecombine(2, pl)
        If we'd had several surfaces, we could have used the global option
        "Mesh.RecombineAll":

        gmsh.option.setNumber("Mesh.RecombineAll", 1)

        The default recombination algorithm is called "Blossom": it uses a minimum
        cost perfect matching algorithm to generate fully quadrilateral meshes from
        triangulations. More details about the algorithm can be found in the
        following paper: J.-F. Remacle, J. Lambrechts, B. Seny, E. Marchandise,
        A. Johnen and C. Geuzaine, "Blossom-Quad: a non-uniform quadrilateral mesh
        generator using a minimum cost perfect matching algorithm", International
        Journal for Numerical Methods in Engineering 89, pp. 1102-1119, 2012.

        For even better 2D (planar) quadrilateral meshes, you can try the
        experimental "Frontal-Delaunay for quads" meshing algorithm, which is a
        triangulation algorithm that enables to create right triangles almost
        everywhere: J.-F. Remacle, F. Henrotte, T. Carrier-Baudouin, E. Bechet,
        E. Marchandise, C. Geuzaine and T. Mouton. A frontal Delaunay quad mesh
        generator using the L^inf norm. International Journal for Numerical Methods
        in Engineering, 94, pp. 494-512, 2013. Uncomment the following line to try
        the Frontal-Delaunay algorithms for quads:

        gmsh.option.setNumber("Mesh.Algorithm", 8)

        The default recombination algorithm might leave some triangles in the mesh, if
        recombining all the triangles leads to badly shaped quads. In such cases, to
        generate full-quad meshes, you can either subdivide the resulting hybrid mesh
        (with `Mesh.SubdivisionAlgorithm' set to 1), or use the full-quad
        recombination algorithm, which will automatically perform a coarser mesh
        followed by recombination, smoothing and subdivision. Uncomment the following
        line to try the full-quad algorithm:

        gmsh.option.setNumber("Mesh.RecombinationAlgorithm", 2) # or 3

        You can also set the subdivision step alone, with

        gmsh.option.setNumber("Mesh.SubdivisionAlgorithm", 1)

        gmsh.model.mesh.generate(2)

        Note that you could also apply the recombination algorithm and/or the
        subdivision step explicitly after meshing, as follows:

        gmsh.model.mesh.generate(2)
        gmsh.model.mesh.recombine()
        gmsh.option.setNumber("Mesh.SubdivisionAlgorithm", 1)
        gmsh.model.mesh.refine()
    """

    def __init__(self, options=None):
        # Default options
        default_options = {
            'General.Terminal': 0,
            'General.AbortOnError': 0,
            # Abort on error? (0: no,  1: abort meshing,
            # 2: throw an exception unless in interactive mode,
            # 3: throw an exception always, 4: exit)
            # Default value: 0
            'Geometry.OCCParallel': 1,
            # Use multi-threaded OpenCASCADE boolean operators
            # Default value: 0
            'Geometry.AutoCoherence': 1,
            # Should all duplicate entities be automatically
            # removed with the built-in geometry kernel?
            # If Geometry.AutoCoherence = 2, also remove degenerate entities.
            # The option has no effect with the OpenCASCADE kernel
            # Default value: 1
            'Geometry.OCCAutoFix': 1,
            # Automatically fix orientation of wires, faces,
            # shells and volumes when creating new entities
            # with the OpenCASCADE kernel
            # Default value: 1
            'Geometry.OCCDisableStl': 0,
            # Disable STL creation in OpenCASCADE kernel
            # Default value: 0
            'Geometry.OCCBoundsUseStl': 0,
            # Use STL mesh for computing bounds of OpenCASCADE shapes
            # (more accurate, but slower)
            # Default value: 0
            'Geometry.OCCBooleanPreserveNumbering': 1,
            # Try to preserve the numbering of entities through OpenCASCADE
            # boolean operations
            # Default value: 1
            'Geometry.OCCThruSectionsDegree': -1,
            # Maximum degree of surfaces generated by thrusections with
            # the OpenCASCADE kernel, if not explicitly specified
            # (default OCC value if negative)
            # Default value: -1
            'Geometry.OCCUnionUnify': 1,
            # Try to unify faces and edges (remove internal seams) which lie
            # on the same geometry after performing a boolean union with
            # the OpenCASCADE kernel
            # Default value: 1
            'Geometry.OCCUseGenericClosestPoint': 0,
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
            'Mesh.SubdivisionAlgorithm': 0,
            # Mesh subdivision algorithm (0: none, 1: all quadrangles,
            # 2: all hexahedra, 3: barycentric)
            # Default value: 0
            'Mesh.RecombinationAlgorithm': 1,
            # Mesh recombination algorithm (0: simple, 1: blossom,
            # 2: simple full-quad, 3: blossom full-quad)
            # Default value: 1
            'Mesh.RecombineAll': 0,
            # Apply recombination algorithm to all surfaces,
            # ignoring per-surface spec
            # Default value: 0
            'Mesh.RecombineOptimizeTopology': 5,
            # Mesh.RecombineOptimizeTopology
            # Number of topological optimization passes (removal of diamonds,
            # ...) of recombined surface meshes
            # Default value: 5
            'Mesh.Recombine3DAll': 0,
            # Apply recombination3D algorithm to all volumes, ignoring
            # per-volume spec (experimental)
            # Default value: 0
            'Mesh.Recombine3DLevel': 0,
            # 3d recombination level (0: hex, 1: hex+prisms,
            # 2: hex+prism+pyramids) (experimental)
            # Default value: 0
            'Mesh.Recombine3DConformity': 0,
            # 3d recombination conformity type (0: nonconforming,
            # 1: trihedra, 2: pyramids+trihedra, 3:pyramids+hexSplit+trihedra,
            # 4:hexSplit+trihedra)(experimental)
            # Default value: 0
            'Mesh.RefineSteps': 10,
            # Number of refinement steps in the MeshAdapt-based 2D algorithms
            # Default value: 10
            'Mesh.Smoothing': 1,
            # Number of smoothing steps applied to the final mesh
            # Default value: 1
            'Mesh.SmoothNormals': 0,
            # Smooth the mesh normals?
            # Default value: 0
            'Mesh.SmoothCrossField': 0,
            # Apply n barycentric smoothing passes to the 3D cross field
            # Default value: 0
            'Mesh.MeshSizeFactor': 1,
            # Factor applied to all mesh element sizes
            # Default value: 1
            'Mesh.MeshSizeMin': 0,
            # Minimum mesh element size
            # Default value: 0
            'Mesh.MeshSizeMax': 1e+22,
            # Maximum mesh element size
            # Default value: 1e+22
            'Mesh.MeshSizeFromPoints': 1,
            # Compute mesh element sizes from values given at geometry points
            # Default value: 1
            'Mesh.MeshSizeExtendFromBoundary': 1,
            # Extend computation of mesh element sizes from the boundaries
            # into the interior (for 3D Delaunay, use 1: longest or 2:
            # shortest surface edge length)
            # Default value: 1
            'Mesh.MeshSizeFromCurvature': 0,
            # Automatically compute mesh element sizes from curvature, using
            # the value as the target number of elements per 2 * Pi radians
            # Default value: 0
            'Mesh.MeshSizeFromCurvatureIsotropic': 0,
            # Force isotropic curvature estimation when the mesh size is
            # computed from curvature
            # Default value: 0
            'Mesh.MeshSizeFromParametricPoints': 0,
            # Compute mesh element sizes from values given at geometry
            # points defining parametric curves
            # Default value: 0
            'Mesh.MinimumCircleNodes': 7,
            # Minimum number of nodes used to mesh circles and ellipses
            # Default value: 7
            'Mesh.MinimumCurveNodes': 3,
            # Minimum number of nodes used to mesh curves other than lines,
            # circles and ellipses
            # Default value: 3
            'Mesh.Optimize': 0,
            # Optimize the mesh to improve the quality of tetrahedral elements
            # Default value: 1
            'Mesh.OptimizeThreshold': 0.3,
            # Optimize tetrahedra that have a quality below ...
            # Default value: 0.3
            'Mesh.OptimizeNetgen': 0,
            # Optimize the mesh using Netgen to improve the quality of tetrahedral elements
            # Default value: 0
        }
        # Update by new options
        options = {} if options is None else options
        default_options.update(options)
        self.options = default_options

    def __call__(self, f=None):
        def wrapper(*args, **kwargs):
            logging.info('Gmsh options')
            for k, v in self.options.items():
                gmsh.option.setNumber(k, v)
                logging.info(f'{k}: {v}')
            logging.info('Gmsh options end')
            out = f(*args, **kwargs) if f is not None else None
            return out

        return wrapper


def flatten(iterable, types=(list,)):
    """Flatten iterable through types

    Args:
        iterable: some iterable
        types: types to recurse

    Returns:
        generator of object: elements
    """
    if isinstance(iterable, types):
        for element in iterable:
            yield from flatten(element, types)
    else:
        yield iterable


class DataTree:
    """Volumes data tree
    # TODO add surfaces loops
    Args:
        vs_dt (list of tuple): Volumes dim-tags

    Attributes:
        vs_dt (list of tuple): Volumes dim-tags
        vs_ss_dt (list of tuple): Surfaces dim-tags of volumes
        vs_ss_cs_dt (list of tuple): Curves dim-tags of surfaces of volumes
        vs_ss_cs_ps_dt (list of tuple): Points dim-tags of curves of surfaces of volumes
        ps_dt_to_cs (dict): Points dim-tags to coordinates
    """

    def __init__(self, vs_dt):
        vs_ss_dt = []  # Surfaces dim-tags of volumes
        vs_ss_cs_dt = []  # Curves dim-tags of surfaces of volumes
        vs_ss_cs_ps_dt = []  # Points dim-tags of curves of surfaces of volumes
        for v_dt in vs_dt:
            # Surfaces dim-tags of the volume
            ss_dt = gmsh.model.getBoundary(dimTags=[v_dt], combined=False,
                                           oriented=True, recursive=False)
            ss_cs_dt = []  # Curves dim-tags of surfaces
            ss_cs_ps_dt = []  # Points dim-tags of curves of surfaces
            for s_dt in ss_dt:
                # Curves dim-tags of the surface
                cs_dt = gmsh.model.getBoundary(dimTags=[s_dt], combined=False,
                                               oriented=True, recursive=False)
                ss_cs_dt.append(cs_dt)
                cs_ps_dt = []  # Points dim-tags of curves
                for c_dt in cs_dt:
                    # Points of the the curve
                    ps_dt = gmsh.model.getBoundary(dimTags=[c_dt],
                                                   combined=False,
                                                   oriented=True,
                                                   recursive=False)
                    cs_ps_dt.append(ps_dt)
                ss_cs_ps_dt.append(cs_ps_dt)
            vs_ss_dt.append(ss_dt)
            vs_ss_cs_dt.append(ss_cs_dt)
            vs_ss_cs_ps_dt.append(ss_cs_ps_dt)
        ps_dt = set(flatten(vs_ss_cs_ps_dt))
        self.ps_dt_to_cs = {x: gmsh.model.getBoundingBox(*x)[:3] for x in ps_dt}
        self.vs_dt = vs_dt
        self.vs_ss_dt = vs_ss_dt
        self.vs_ss_cs_dt = vs_ss_cs_dt
        self.vs_ss_cs_ps_dt = vs_ss_cs_ps_dt
        self.b_sls, self.b_s2sl, self.i_sls, self.i_s2sl = self.evaluate_global_surfaces_loops(vs_ss_dt, vs_ss_cs_dt)

    @staticmethod
    def evaluate_boundary_surfaces(vs_ss_dt):
        b_ss = set()  # Boundary surfaces
        for ss_dt in vs_ss_dt:
            for s_dt in ss_dt:
                if s_dt in b_ss:
                    b_ss.remove(s_dt)
                else:
                    b_ss.add(s_dt)
        return b_ss

    @staticmethod
    def evaluate_global_surfaces_loops(vs_ss_dt, vs_ss_cs_dt):
        b_ss = DataTree.evaluate_boundary_surfaces(vs_ss_dt)
        b_sls, i_sls = [], []
        b_s2sl, i_s2sl = {}, {}
        ss_dt = set(flatten(vs_ss_dt))
        while len(ss_dt) > 0:
            sl, sl_cs, b = [], set(), True  # Surface loop, Curves of surface loop
            new_s = True
            while new_s:
                new_s = False
                for v_i, ss_cs_dt in enumerate(vs_ss_cs_dt):
                    for s_i, cs_dt in enumerate(ss_cs_dt):  # For each remaining surface
                        s_dt = vs_ss_dt[v_i][s_i]
                        if s_dt not in ss_dt:
                            continue
                        if len(sl) == 0:
                            b = s_dt in b_ss
                        else:
                            if (s_dt in b_ss) != b:
                                continue
                        for c_dt in cs_dt:  # For each curve of the surface
                            c_t = abs(c_dt[1])  # Curve tag
                            if len(sl_cs) == 0 or c_t in sl_cs:
                                new_s = True
                                # Add all curves of the surface
                                sl_cs.update(abs(x[1]) for x in ss_cs_dt[s_i])
                                ss_dt.remove(s_dt)  # Remove surface from iteration
                                sl.append(s_dt[1])  # Add surface to loop
                                if b:
                                    b_s2sl[s_dt[1]] = len(b_sls)
                                else:
                                    i_s2sl[s_dt[1]] = len(i_sls)
                                break
            if b:
                b_sls.append(sl)
            else:
                i_sls.append(sl)
        return b_sls, b_s2sl, i_sls, i_s2sl


def plot_quality():
    gmsh.plugin.setNumber('AnalyseMeshQuality', 'JacobianDeterminant', 1)
    gmsh.plugin.setNumber('AnalyseMeshQuality', 'IGEMeasure', 1)
    gmsh.plugin.setNumber('AnalyseMeshQuality', 'ICNMeasure', 1)
    gmsh.plugin.setNumber('AnalyseMeshQuality', 'Recompute', 1)
    gmsh.plugin.setNumber('AnalyseMeshQuality', 'DimensionOfElements', -1)
    gmsh.plugin.run('AnalyseMeshQuality')
    logging.info('Mesh quality')
    log = gmsh.logger.get()
    for message in log:
        if any([message.startswith(x)
                for x in ['Info: minJ', 'Info: minJ/maxJ',
                          'Info: IGE', 'Info: ICN']]):
            logging.info(message)
        else:
            logging.debug(message)


def plot_statistics():
    logging.info('Mesh statistics')
    types_names = {
        1: '2-node line',
        2: '3-node triangle',
        3: '4-node quadrangle',
        4: '4-node tetrahedron',
        5: '8-node hexahedron',
        6: '6-node prism',
        7: '5-node pyramid',
        8: '3-node second order line',
        9: '6-node second order triangle',
        10: '9-node second order quadrangle',
        11: '10-node second order tetrahedron',
        12: '27-node second order hexahedron',
        13: '18-node second order prism',
        14: '14-node second order pyramid',
        15: '1-node point',
        16: '8-node second order quadrangle',
        17: '20-node second order hexahedron',
        18: '15-node second order prism',
        19: '13-node second order pyramid'}
    n_elements, nodes = 0, set()
    element_types, element_tags, node_tags = gmsh.model.mesh.get_elements(-1)
    for i, et in enumerate(element_types):
        name, ets, nts = types_names[et], element_tags[i], node_tags[i]
        logging.info(f'{name}: {len(ets)} ')
        n_elements += len(ets)
        nodes.update(nts)
    logging.info(f'Total: {len(nodes)} nodes and {n_elements} elements')


def timeit(f):
    def wrapper(*args, **kwargs):
        t = time.perf_counter()
        out = f(*args, **kwargs)
        module = f.__module__
        try:  # function
            name = module + '.' + f.__name__
        except Exception:  # class
            name = module + '.' + f.__class__.__name__
        logging.info(f'{name} - {time.perf_counter() - t:.3f}s')
        return out

    return wrapper


def beta_function(xs, a, b, n=10000):
    """Beta function

    https://en.wikipedia.org/wiki/Beta_function#Incomplete_beta_function

    Args:
        xs (float, np.ndarray): argument(s)
        a (float): alpha
        b (float): beta
        n (int): number of integration steps

    Returns:
        float, np.ndarray: value
    """
    ts, dt = np.linspace(0, xs, n, retstep=True)
    ts = np.ma.masked_values(ts, 0)  # leads to inf
    ts = np.ma.masked_values(ts, 1)  # leads to inf
    vs = ts ** (a - 1) * (1 - ts) ** (b - 1) * dt
    vs = vs.filled(0)
    return np.sum(vs, axis=0)


def beta_pdf(xs, a, b, n=10000):
    """Beta probability density function

    https://en.wikipedia.org/wiki/Beta_distribution#Probability_density_function

    Args:
        xs (float, np.ndarray): argument(s)
        a (float): alpha
        b (float): beta
        n (int): number of integration steps

    Returns:
        float, np.ndarray: value
    """
    t = beta_function(1, a, b, n)
    if a < 1 or b < 1:  # Correct 0 and 1
        _, dt = np.linspace(0, 1, n, retstep=True)
        if isinstance(xs, np.ndarray):
            xs[np.isclose(xs, 0)] = dt
            xs[np.isclose(xs, 1)] = 1 - dt
        else:
            xs = dt if np.isclose(xs, 0) else xs
            xs = 1 - dt if np.isclose(xs, 1) else xs
    return xs ** (a - 1) * (1 - xs) ** (b - 1) / t


def beta_cdf(xs, a, b, n=10000):
    """Beta cumulative distribution function

    https://en.wikipedia.org/wiki/Beta_distribution#Cumulative_distribution_function
    https://en.wikipedia.org/wiki/Beta_function#Incomplete_beta_function

    Args:
        xs (float, np.ndarray): argument(s)
        a (float): alpha
        b (float): beta
        n (int): number of integration steps

    Returns:
        float, np.ndarray: value [0, 1]
    """
    t = beta_function(1, a, b, n)
    # Different integrations steps by x value
    if isinstance(xs, np.ndarray):
        tx = np.array([beta_function(x, a, b, int(np.ceil(n * x))) for x in xs])
    else:
        nx = int(np.ceil(n * xs))
        tx = beta_function(xs, a, b, nx)  # Incomplete beta function
    return tx / t


def check_on_file(path):
    """Check path on the file

    In the order:
    1. If file at absolute path
    2. Else if file at relative to current working directory path
    3. Else if file at relative to running script directory path
    4. Else if file at relative to real running script directory path
    (with eliminating all symbolics links)
    0. Else no file

    Args:
        path (str): path to check

    Returns:
        tuple: result, expanded path to file or None
    """
    # Expand path
    path_expand_vars = os.path.expandvars(path)
    path_expand_vars_user = os.path.expanduser(path_expand_vars)
    # Get directories
    wd_path = os.getcwd()
    script_dir_path = os.path.dirname(os.path.abspath(__file__))
    # Set paths to file check
    clear_path = path_expand_vars_user
    rel_wd_path = os.path.join(wd_path, path_expand_vars_user)
    rel_script_path = os.path.join(script_dir_path, path_expand_vars_user)
    real_rel_script_path = os.path.realpath(rel_script_path)
    # Check on file:
    if os.path.isfile(clear_path):
        return 'clear', clear_path
    elif os.path.isfile(rel_wd_path):
        return 'relative_to_cwd', rel_wd_path
    elif os.path.isfile(rel_script_path):
        return 'relative_to_script', rel_script_path
    elif os.path.isfile(real_rel_script_path):
        return 'relative_to_real_script', real_rel_script_path
    else:  # No file
        return None, None


def volumes_surfaces_to_volumes_groups_surfaces(volumes_surfaces):
    """
    For Environment object. For each distinct inner volume in Environment
    should exist the surface loop. If inner volumes touch each other they unite
    to volume group and have common surface loop.
    :param volumes_surfaces: [[v1_s1, ..., v1_si], ..., [vj_s1, ..., vj_si]]
    :return: volumes_groups_surfaces [[vg1_s1, ..., vg1_si], ...]
    """
    vs_indexes = set(range(len(volumes_surfaces)))
    while len(vs_indexes) != 0:
        current_index = list(vs_indexes)[0]
        current_surfaces = set(volumes_surfaces[current_index])
        other_indexes = {x for x in vs_indexes if x != current_index}
        is_intersection = True
        while is_intersection:
            is_intersection = False
            new_other_indexes = {x for x in other_indexes}
            for i in other_indexes:
                surfaces_i = set(volumes_surfaces[i])
                intersection = current_surfaces.intersection(surfaces_i)
                if len(intersection) > 0:
                    is_intersection = True
                    # Update current
                    current_surfaces.symmetric_difference_update(surfaces_i)
                    new_other_indexes.remove(i)
                    vs_indexes.remove(i)
                    # Update global
                    volumes_surfaces[current_index] = list(current_surfaces)
                    volumes_surfaces[i] = list()
            other_indexes = new_other_indexes
        vs_indexes.remove(current_index)
    volumes_surfaces_groups = [x for x in volumes_surfaces if len(x) != 0]
    return volumes_surfaces_groups
