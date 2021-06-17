import json
import os
import argparse
import socket
import sys
import time
import logging
import copy
import getpass

import gmsh

import complex
import complex_primitive
import cylinder
import matrix
import regular_matrix
import regular_bound_matrix
import polygon
import point
import uni
from boolean import complex_self
from support import boundary_surfaces_to_six_side_groups, \
    get_boundary_surfaces, check_file, physical_surfaces, \
    auto_complex_points_sizes_min_curve_in_volume, set_boundary_points_sizes, \
    auto_boundary_points_sizes_min_edge_in_surface, \
    set_points_sizes, get_interior_surfaces


class ComplexFactory:
    constructor_map = {
        complex.Complex.__name__: getattr(
            complex, complex.Complex.__name__),
        matrix.Matrix.__name__: getattr(
            matrix, matrix.Matrix.__name__),
        regular_matrix.RegularMatrix.__name__: getattr(
            regular_matrix, regular_matrix.RegularMatrix.__name__),
        regular_bound_matrix.RegularBoundMatrix.__name__: getattr(
            regular_bound_matrix, regular_bound_matrix.RegularBoundMatrix.__name__),
        complex_primitive.ComplexPrimitive.__name__: getattr(
            complex_primitive, complex_primitive.ComplexPrimitive.__name__),
        cylinder.Cylinder.__name__: getattr(
            cylinder, cylinder.Cylinder.__name__),
        polygon.Polygon.__name__: getattr(
            polygon, polygon.Polygon.__name__),
        point.Point.__name__: getattr(point, point.Point.__name__),
        uni.Uni.__name__: getattr(uni, uni.Uni.__name__)
    }

    def __init__(self):
        pass

    @staticmethod
    def new(input_data):
        """
        Complex's child objects factory by item 'class_name':
        'Complex's child class name' in input_data['metadata'].
        :param dict input_data: dict should have at least two items:
        'metadata':dict and 'arguments':dict,
        'metadata' dict should be 'class_name' item and 'arguments' dict
        should coincide with child object __init__
        method arguments
        :return: Complex
        """
        class_name = input_data['metadata']['class_name']
        kwargs = input_data['arguments']
        return ComplexFactory.constructor_map[class_name](**kwargs)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('config', help='config file', nargs='?')
    parser.add_argument('-i', '--input_path', help='input filename')
    parser.add_argument('-o', '--output_path', help='output filename')
    parser.add_argument('-l', '--log_path', help='log filename')
    parser.add_argument('-L', '--log_level', default='INFO',
                        choices=logging._nameToLevel.keys())
    parser.add_argument('-T', '--test', help='test mode', action='store_true')
    parser.add_argument('-r', '--recombine', help='recombine',
                        action='store_true')
    parser.add_argument('-b', '--boolean', help='boolean', action='store_true')
    parser.add_argument('-B', '--boundary_type', help='boundary',
                        default='primitive', choices=['6', 'primitive', 'all',
                                                      'path_to_file'])
    parser.add_argument('-s', '--auto_size', type=float, metavar=1.0,
                        help='mesh auto size factor', default=None,
                        nargs='?', const=1.0)
    parser.add_argument('-S', '--size', type=float, metavar=5.0,
                        help='points mesh size', default=None)
    parser.add_argument('-z', '--boundary_auto_size', type=float, metavar=1.0,
                        help='boundary mesh auto size factor',
                        default=None, nargs='?', const=1.0)
    parser.add_argument('-Z', '--boundary_size', type=float, metavar=10.0,
                        help='boundary points mesh size',
                        default=None)
    parser.add_argument('-O', '--optimize',
                        help='optimize mesh after generation',
                        action='store_true')
    parser.add_argument('-m', '--mesh_algorithm', type=int, default=1,
                        help='gmsh 3D mesh algorithm: 1: Delaunay, 4: Frontal, '
                             '7: MMG3D, 9: R-tree, 10: HXT')
    parser.add_argument('-M', '--mesh_algorithm_2d', type=int, default=6,
                        help='gmsh 2D mesh algorithm: 1: MeshAdapt,'
                             '2: Automatic, 5: Delaunay, 6: Frontal-Delaunay,'
                             '7: BAMG, 8: Frontal-Delaunay for Quads,'
                             '9: Packing of Parallelograms')
    parser.add_argument('-I', '--in_surfaces', help='make inner surfaces',
                        action='store_true')
    parser.add_argument('-t', '--transfinite', help='transfinite surfaces',
                        action='store_true')
    parser.add_argument('-f', '--factory', help='gmsh factory',
                        default=None, choices=['geo', 'occ'])
    cmd_args = vars(parser.parse_args())
    args = copy.deepcopy(cmd_args)
    config_args = None
    if cmd_args['config'] is not None:
        result = check_file(cmd_args['config'])
        with open(result['path']) as f:
            data = json.load(f)
        config_args = data['arguments']
        args.update(config_args)
    root, extension = os.path.splitext(args['input_path'])
    basename = os.path.basename(root)
    # Test mode
    if not args['test']:
        if args['output_path'] is None:
            args['output_path'] = basename + '.msh2'
    else:
        args['output_path'] = basename + '.brep'
    # Explicit boundaries
    if args['boundary_type'] not in ['6', 'primitive', 'all']:
        result = check_file(args['boundary_type'])
        with open(result['path']) as f:
            physical_surfaces_input = json.load(f)
        physical_surfaces_kwargs = physical_surfaces_input['arguments']
    # Logging
    if args['log_path'] is None:
        args['log_path'] = basename + '.log'
    log_level_int = logging._nameToLevel[args['log_level']]
    tz = time.strftime('%z')
    user = getpass.getuser()
    hostname = socket.gethostname()
    ip = socket.gethostbyname(hostname)
    logging.basicConfig(
        filename=args['log_path'],
        filemode='a',
        format='%(asctime)s.%(msecs)03d' + tz + f'|{hostname}|{ip}|{user}' +
               '|%(process)d|%(levelname)s|%(filename)s|%(lineno)d|%(message)s',
        datefmt='%Y-%m-%dT%H:%M:%S',
        level=log_level_int)
    # Log
    logging.info(f'hostname: {socket.gethostname()}')
    logging.info(f'ip: {socket.gethostbyname(socket.gethostname())}')
    logging.info(f'user: {getpass.getuser()}')
    logging.info(f'pid: {os.getpid()}')
    logging.info(f'python: {sys.executable}')
    logging.info(f'script: {__file__}')
    logging.info(f'working directory: {os.getcwd()}')
    logging.info(f'cmd args: {cmd_args}')
    logging.info(f'config args: {config_args}')
    logging.info(f'args: {args}')
    logging.info('gmsh')
    t00 = time.perf_counter()
    t0 = time.perf_counter()
    gmsh.initialize()
    if args['log_level'] == "NOTSET":
        gmsh.option.setNumber("General.Terminal", 1)
    else:
        gmsh.option.setNumber("General.Terminal", 0)
    gmsh.option.setNumber('Geometry.AutoCoherence', 0)  # No effect at occ
    gmsh.option.setNumber('Mesh.Optimize', 0)  # resolving further
    gmsh.option.setNumber('Mesh.Algorithm', args['mesh_algorithm_2d'])
    gmsh.option.setNumber('Mesh.Algorithm3D', args['mesh_algorithm'])
    model_name = basename
    gmsh.model.add(model_name)
    logging.info(f'gmsh: {time.perf_counter() - t0:.3f}s')
    logging.info('Initialize')
    t0 = time.perf_counter()
    result = check_file(args['input_path'])
    with open(result['path']) as f:
        input_data = json.load(f)
    logging.info(f'input data: {input_data}')
    if args['factory'] is not None:
        input_data['arguments']['factory'] = args['factory']
    c = ComplexFactory.new(input_data)
    factory = c.factory
    logging.info(f'Initialize: {time.perf_counter() - t0:.3f}s')
    logging.info('Synchronize')
    t0 = time.perf_counter()
    factory.synchronize()
    logging.info(f'Synchronize: {time.perf_counter() - t0:.3f}s')
    if not args['test']:
        if args['boolean']:
            if args['factory'] != 'occ':
                logging.critical('Boolean is only available in the occ factory!')
                raise ValueError('Boolean is only available in the occ factory!')
            logging.info('Bounding Box')  # for boolean speedup
            t0 = time.perf_counter()
            c.evaluate_bounding_box()
            logging.info(f'Bounding Box: {time.perf_counter() - t0:.3f}s')
            logging.info("Boolean")
            t0 = time.perf_counter()
            complex_self(factory, c)
            logging.info(f'Boolean: {time.perf_counter() - t0:.3f}s')
            logging.info('Synchronize')
            t0 = time.perf_counter()
            factory.synchronize()
            logging.info(f'Synchronize: {time.perf_counter() - t0:.3f}s')
        if args['transfinite']:
            logging.info('Transfinite')
            t0 = time.perf_counter()
            ss, cs = set(), set()  # surfaces, curves
            c.transfinite(ss, cs)
            logging.info(f'Transfinite: {time.perf_counter() - t0:.3f}s')
        if args['recombine']:
            logging.info('Recombine')
            t0 = time.perf_counter()
            c.recombine()
            logging.info(f'Recombine: {time.perf_counter() - t0:.3f}s')
        if args['auto_size'] is not None:
            logging.info('Auto Size: {}'.format(args['auto_size']))
            t0 = time.perf_counter()
            pss = dict()
            auto_complex_points_sizes_min_curve_in_volume(c, pss,
                                                          args['auto_size'])
            logging.info(f'Auto Size: {time.perf_counter() - t0:.3f}s')
        if args['size'] is not None:
            logging.info('Set Size: {}'.format(args['size']))
            t0 = time.perf_counter()
            set_points_sizes(args['size'])
            logging.info(f'Set Size {time.perf_counter() - t0:.3f}s')
        if args['boundary_auto_size'] is not None:
            logging.info('Boundary Auto Size: {}'.format(args['boundary_auto_size']))
            t0 = time.perf_counter()
            auto_boundary_points_sizes_min_edge_in_surface(
                args['boundary_auto_size'])
            logging.info(f'Boundary Auto Size {time.perf_counter() - t0:.3f}s')
        if args['boundary_size'] is not None:
            logging.info('Set Boundary Size: {}'.format(args['boundary_size']))
            t0 = time.perf_counter()
            set_boundary_points_sizes(args['boundary_size'])
            logging.info(f'Set Boundary Size: {time.perf_counter() - t0:.3f}s')
        logging.info("Volumes")
        t0 = time.perf_counter()
        ns_to_vs = c.get_map_names_to_volumes()
        for n, vs in ns_to_vs.items():
            tag = gmsh.model.addPhysicalGroup(3, vs)
            gmsh.model.setPhysicalName(3, tag, n)
        logging.info(f'Volumes: {time.perf_counter() - t0:.3f}s')
        logging.info("Surfaces")
        t0 = time.perf_counter()
        if args['boundary_type'] == '6':
            logging.info("by 6 surfaces")
            boundary_surfaces_groups = boundary_surfaces_to_six_side_groups()
            for n, ss in boundary_surfaces_groups.items():
                tag = gmsh.model.addPhysicalGroup(2, ss)
                gmsh.model.setPhysicalName(2, tag, n)
        elif args['boundary_type'] == 'primitive':
            logging.info("by primitives surfaces")
            n2s = dict()  # surface name to surface global index
            s2psi = c.get_map_surface_to_primitives_surfaces_indices()
            bs = get_boundary_surfaces()
            for s in bs:
                sn = None
                psi = s2psi[s]  # [(primitive, surf local index)]
                if len(psi) != 0:
                    pi, si = psi[0]  # from first primitive
                    sn = c.primitives[pi].surfaces_names[si]
                else:  # After boolean
                    sn = 'S'
                n2s.setdefault(sn, []).append(s)
            for n, ss in n2s.items():
                tag = gmsh.model.addPhysicalGroup(2, ss)
                gmsh.model.setPhysicalName(2, tag, n)
        elif args['boundary_type'] == 'all':
            logging.info("by all surfaces")
            boundary_surfaces = get_boundary_surfaces()
            for i, s in enumerate(boundary_surfaces):
                name = 'S{0}'.format(s)
                tag = gmsh.model.addPhysicalGroup(2, [s])
                gmsh.model.setPhysicalName(2, tag, name)
        else:
            logging.info("by explicit surfaces")
            physical_surfaces(**physical_surfaces_kwargs)
        logging.info(f'Surfaces: {time.perf_counter() - t0:.3f}s')
        if args['in_surfaces']:
            t0 = time.perf_counter()
            logging.info('Inner Surfaces')
            n2s = {}  # surface name to surface global index
            if 's2psi' not in locals():  # s2i not exists
                s2psi = c.get_map_surface_to_primitives_surfaces_indices()
            in_surfaces = get_interior_surfaces()
            for s in in_surfaces:
                sn = None
                psi = s2psi[s]
                if len(psi) != 0:
                    for pi, si in psi:
                        mask = c.primitives[pi].in_surf_mask
                        if not mask[si]:
                            sn = c.primitives[pi].in_surfaces_names[si]
                            break
                else:  # After boolean or masked
                    sn = 'SI'
                if sn is not None:
                    n2s.setdefault(sn, []).append(s)
            for n, ss in n2s.items():
                tag = gmsh.model.addPhysicalGroup(2, ss)
                gmsh.model.setPhysicalName(2, tag, n)
            logging.info(f'Inner Surfaces: {time.perf_counter() - t0:.3f}s')
        logging.info("Mesh")
        t0 = time.perf_counter()
        gmsh.model.mesh.generate(3)
        logging.info(f'Mesh: {time.perf_counter() - t0:.3f}s')
        logging.info(f'nodes: {len(gmsh.model.mesh.getNodes()[0])}')
        if args['optimize']:
            logging.info("Optimize")
            t0 = time.perf_counter()
            gmsh.model.mesh.optimize('', True)
            logging.info(f'Optimize: {time.perf_counter() - t0:.3f}s')
    logging.info("Write: {}".format(args['output_path']))
    t0 = time.perf_counter()
    gmsh.write(args['output_path'])
    logging.info(f'Write: {time.perf_counter() - t0:.3f}s')
    gmsh.finalize()
    logging.info(f'Time spent: {time.perf_counter() - t00:.3f}s')
