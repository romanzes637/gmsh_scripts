import json
import os
import argparse
import socket
from pprint import pprint
import sys
import time

import gmsh

import complex
import complex_primitive
import cylinder
import experiment
import matrix
import regular_matrix
import regular_bound_matrix
import polygon
import tunnel
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
        tunnel.Tunnel.__name__: getattr(
            tunnel, tunnel.Tunnel.__name__),
        experiment.Experiment.__name__: getattr(
            experiment, experiment.Experiment.__name__),
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
    print('Python: {0}'.format(sys.executable))
    print('Script: {0}'.format(__file__))
    print('Working Directory: {0}'.format(os.getcwd()))
    print('Host: {0}'.format(socket.gethostname()))
    print('PID: {0}'.format(os.getpid()))
    parser = argparse.ArgumentParser()
    parser.add_argument('config', help='config file', nargs='?')
    parser.add_argument('-i', '--input_path', help='input filename')
    parser.add_argument('-o', '--output_path', help='output filename')
    parser.add_argument('-v', '--verbose', type=int, metavar=1,
                        help='verbose', default=0, nargs='?', const=1)
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
    print('Cmd Arguments')
    cmd_args = parser.parse_args()
    print(cmd_args)
    args = dict()
    args['config'] = cmd_args.config
    if args['config'] is not None:
        print('Using config file: {}'.format(args['config']))
        result = check_file(args['config'])
        with open(result['path']) as f:
            data = json.load(f)
        pprint(data)
        config_args = data['arguments']
        args['input_path'] = config_args.get('input_path', None)
        args['output_path'] = config_args.get('output_path', False)
        args['test'] = config_args.get('test', False)
        args['verbose'] = config_args.get('verbose', False)
        args['recombine'] = config_args.get('recombine', False)
        args['boolean'] = config_args.get('boolean', False)
        args['auto_size'] = config_args.get('auto_size', False)
        args['size'] = config_args.get('size', None)
        args['boundary_size'] = config_args.get('boundary_size', None)
        args['boundary_auto_size'] = config_args.get('boundary_auto_size', None)
        args['boundary_type'] = config_args.get('boundary_type', 'primitive')
        args['optimize'] = config_args.get('optimize', True)
        args['mesh_algorithm'] = config_args.get('mesh_algorithm', 1)
        args['mesh_algorithm_2d'] = config_args.get('mesh_algorithm_2d', 6)
        args['in_surfaces'] = config_args.get('in_surfaces', False)
        args['factory'] = config_args.get('factory', None)
        args['transfinite'] = config_args.get('transfinite', True)
    else:
        args['input_path'] = cmd_args.input_path
        args['output_path'] = cmd_args.output_path
        args['test'] = cmd_args.test
        args['verbose'] = cmd_args.verbose
        args['recombine'] = cmd_args.recombine
        args['boolean'] = cmd_args.boolean
        args['auto_size'] = cmd_args.auto_size
        args['size'] = cmd_args.size
        args['boundary_size'] = cmd_args.boundary_size
        args['boundary_auto_size'] = cmd_args.boundary_auto_size
        args['boundary_type'] = cmd_args.boundary_type
        args['optimize'] = cmd_args.optimize
        args['mesh_algorithm'] = cmd_args.mesh_algorithm
        args['mesh_algorithm_2d'] = cmd_args.mesh_algorithm_2d
        args['in_surfaces'] = cmd_args.in_surfaces
        args['factory'] = cmd_args.factory
        args['transfinite'] = cmd_args.transfinite
    root, extension = os.path.splitext(args['input_path'])
    basename = os.path.basename(root)
    if args['output_path'] is None:
        if not args['test']:
            args['output_path'] = basename + '.msh2'
        else:
            args['output_path'] = basename + '.brep'
    if args['boundary_type'] not in ['6', 'primitive', 'all']:
        print("Boundary input file: {}".format(args['boundary_type']))
        result = check_file(args['boundary_type'])
        with open(result['path']) as f:
            physical_surfaces_input = json.load(f)
        pprint(physical_surfaces_input)
        physical_surfaces_kwargs = physical_surfaces_input['arguments']
    print('Arguments')
    pprint(args)
    # Input data
    print('Input data')
    result = check_file(args['input_path'])
    with open(result['path']) as f:
        input_data = json.load(f)
    pprint(input_data)
    print('gmsh')
    gmsh.initialize()
    print('Options')
    if args['verbose'] > 1:
        gmsh.option.setNumber("General.Terminal", 1)
    else:
        gmsh.option.setNumber("General.Terminal", 0)
    gmsh.option.setNumber('Geometry.AutoCoherence', 0)  # No effect at occ
    gmsh.option.setNumber('Mesh.Optimize', 0)  # resolving further
    gmsh.option.setNumber('Mesh.Algorithm', args['mesh_algorithm_2d'])
    gmsh.option.setNumber('Mesh.Algorithm3D', args['mesh_algorithm'])
    print('Model')
    model_name = basename
    gmsh.model.add(model_name)
    print('Initialize')
    t00 = time.time()
    t0 = time.time()
    if args['factory'] is not None:
        input_data['arguments']['factory'] = args['factory']
    c = ComplexFactory.new(input_data)
    factory = c.factory
    print(f'{time.time() - t0:.3f}s')
    print('Synchronize')
    t0 = time.time()
    factory.synchronize()
    print(f'{time.time() - t0:.3f}s')
    if not args['test']:
        # c.evaluate_coordinates()  # for correction (obsoleted)
        if args['boolean']:
            print('Bounding Box')  # for boolean speedup
            t0 = time.time()
            c.evaluate_bounding_box()
            print(f'{time.time() - t0:.3f}s')
            print("Boolean")
            t0 = time.time()
            complex_self(factory, c, verbose=args['verbose'])
            print(f'{time.time() - t0:.3f}s')
            t0 = time.time()
            print('Synchronize')
            factory.synchronize()
            print(f'{time.time() - t0:.3f}s')
        if args['transfinite']:
            print('Transfinite')
            t0 = time.time()
            ss, cs = set(), set()  # surfaces, curves
            c.transfinite(ss, cs)
            # correct_and_transfinite_complex(c, ss, cs)
            print(f'{time.time() - t0:.3f}s')
        if args['recombine']:
            print('Recombine')
            t0 = time.time()
            c.recombine()
            print(f'{time.time() - t0:.3f}s')
        if args['auto_size'] is not None:
            print('Auto Size: {}'.format(args['auto_size']))
            t0 = time.time()
            pss = dict()
            auto_complex_points_sizes_min_curve_in_volume(c, pss,
                                                          args['auto_size'])
            print(f'{time.time() - t0:.3f}s')
        if args['size'] is not None:
            print('Set Size: {}'.format(args['size']))
            t0 = time.time()
            set_points_sizes(args['size'])
            print(f'{time.time() - t0:.3f}s')
        if args['boundary_auto_size'] is not None:
            print('Boundary Auto Size: {}'.format(args['boundary_auto_size']))
            t0 = time.time()
            auto_boundary_points_sizes_min_edge_in_surface(
                args['boundary_auto_size'])
            print(f'{time.time() - t0:.3f}s')
        if args['boundary_size'] is not None:
            print('Set Boundary Size: {}'.format(args['boundary_size']))
            t0 = time.time()
            set_boundary_points_sizes(args['boundary_size'])
            print(f'{time.time() - t0:.3f}s')
        print("Volumes")
        t0 = time.time()
        ns_to_vs = c.get_map_names_to_volumes()
        for n, vs in ns_to_vs.items():
            tag = gmsh.model.addPhysicalGroup(3, vs)
            gmsh.model.setPhysicalName(3, tag, n)
        print(f'{time.time() - t0:.3f}s')
        print("Surfaces")
        t0 = time.time()
        if args['boundary_type'] == '6':
            # print("by 6 surfaces")
            boundary_surfaces_groups = boundary_surfaces_to_six_side_groups()
            for n, ss in boundary_surfaces_groups.items():
                tag = gmsh.model.addPhysicalGroup(2, ss)
                gmsh.model.setPhysicalName(2, tag, n)
        elif args['boundary_type'] == 'primitive':
            # print("by primitives surfaces")
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
            # print("by all surfaces")
            boundary_surfaces = get_boundary_surfaces()
            for i, s in enumerate(boundary_surfaces):
                name = 'S{0}'.format(s)
                tag = gmsh.model.addPhysicalGroup(2, [s])
                gmsh.model.setPhysicalName(2, tag, name)
        else:
            # print("by support.physical_surfaces")
            physical_surfaces(**physical_surfaces_kwargs)
        print(f'{time.time() - t0:.3f}s')
        if args['in_surfaces']:
            t0 = time.time()
            print('Inner Surfaces')
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
            print(f'{time.time() - t0:.3f}s')
        print("Mesh")
        t0 = time.time()
        gmsh.model.mesh.generate(3)
        print(f'{time.time() - t0:.3f}s')
        print('Nodes: {0}'.format(len(gmsh.model.mesh.getNodes()[0])))
        # t0 = time.time()
        # gmsh.model.mesh.removeDuplicateNodes()
        # print(time.time() - t0)
        # print('Nodes: {0}'.format(len(gmsh.model.mesh.getNodes()[0])))
        # es = gmsh.model.mesh.getElements()
        if args['optimize']:
            print("Optimize Mesh")
            t0 = time.time()
            gmsh.model.mesh.optimize('', True)
            print(f'{time.time() - t0:.3f}s')
    print("Write: {}".format(args['output_path']))
    t0 = time.time()
    gmsh.write(args['output_path'])
    print(f'{time.time() - t0:.3f}s')
    gmsh.finalize()
    print(f'Time spent: {time.time() - t00:.3f}s')
