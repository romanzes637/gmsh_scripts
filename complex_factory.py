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
import complex_union
import cylinder
import divided_cylinder
import experiment
import matrix
import regular_matrix
import regular_bound_matrix
import pool
import polygon
import tunnel
import nkm_eleron_2
import nkm_eleron_trench
from boolean import complex_self
from support import boundary_surfaces_to_six_side_groups, \
    get_boundary_surfaces, check_file, physical_surfaces, \
    auto_complex_points_sizes_min_curve_in_volume, set_boundary_points_sizes, \
    auto_boundary_points_sizes, auto_boundary_points_sizes_min_edge_in_surface, \
    set_points_sizes


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
        complex_union.ComplexUnion.__name__: getattr(
            complex_union, complex_union.ComplexUnion.__name__),
        cylinder.Cylinder.__name__: getattr(
            cylinder, cylinder.Cylinder.__name__),
        divided_cylinder.DividedCylinder.__name__: getattr(
            divided_cylinder, divided_cylinder.DividedCylinder.__name__),
        polygon.Polygon.__name__: getattr(
            polygon, polygon.Polygon.__name__),
        tunnel.Tunnel.__name__: getattr(
            tunnel, tunnel.Tunnel.__name__),
        pool.Pool.__name__: getattr(
            pool, pool.Pool.__name__),
        experiment.Experiment.__name__: getattr(
            experiment, experiment.Experiment.__name__),
        nkm_eleron_2.NkmEleron2.__name__: getattr(
            nkm_eleron_2, nkm_eleron_2.NkmEleron2.__name__),
        nkm_eleron_trench.NkmEleronTrench.__name__: getattr(
            nkm_eleron_trench, nkm_eleron_trench.NkmEleronTrench.__name__)
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
    parser.add_argument('-v', '--verbose', help='verbose mode',
                        action='store_true')
    parser.add_argument('-t', '--test', help='test mode', action='store_true')
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
                        help='gmsh mesh algorithm: 1: Delaunay, 4: Frontal,'
                             ' 5: Frontal Delaunay, 6: Frontal Hex, 7: MMG3D,'
                             ' 9: R-tree, 10: HXT')
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
        args['boundary_type'] = config_args.get('boundary_type', '6')
        args['optimize'] = config_args.get('optimize', True)
        args['mesh_algorithm'] = config_args.get('mesh_algorithm', 1)
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
    if args['verbose']:
        gmsh.option.setNumber("General.Terminal", 1)
    else:
        gmsh.option.setNumber("General.Terminal", 0)
    gmsh.option.setNumber('Geometry.AutoCoherence', 0)  # No effect at occ
    # if args['optimize']:
    #     gmsh.option.setNumber('Mesh.Optimize', 1)
    # else:
    gmsh.option.setNumber('Mesh.Optimize', 0)  # resolving further
    gmsh.option.setNumber('Mesh.Algorithm3D', args['mesh_algorithm'])
    print('Model')
    model_name = basename
    gmsh.model.add(model_name)
    t00 = time.time()
    print('Initialize')
    t0 = time.time()
    c = ComplexFactory.new(input_data)
    factory = c.factory
    print(time.time() - t0)
    print('Synchronize')
    t0 = time.time()
    factory.synchronize()
    print(time.time() - t0)
    if not args['test']:
        print('Evaluate')
        t0 = time.time()
        c.evaluate_coordinates()  # for correct and transfinite
        c.evaluate_bounding_box()  # for boolean
        print(time.time() - t0)
        if args['boolean']:
            print("Boolean")
            complex_self(factory, c)
        # print(len(gmsh.model.getEntities(0)))
        # print(len(gmsh.model.getEntities(1)))
        # print(len(gmsh.model.getEntities(2)))
        # print(len(gmsh.model.getEntities(3)))
        # print('Remove Duplicates')
        # t0 = time.time()
        # factory.removeAllDuplicates()
        # print(time.time() - t0)
        # print('Synchronize')
        # t0 = time.time()
        # factory.synchronize()
        # print(time.time() - t0)
        # print(len(gmsh.model.getEntities(0)))
        # print(len(gmsh.model.getEntities(1)))
        # print(len(gmsh.model.getEntities(2)))
        # print(len(gmsh.model.getEntities(3)))
        # Primitive/Complex Correction
        t0 = time.time()
        ss = set()  # transfinited surfaces
        cs = set()  # transfinited curves
        if args['recombine']:
            print('Correct and Transfinite and Recombine')
            c.transfinite(ss, cs)
            c.recombine()
            # correct_and_transfinite_and_recombine_complex(c, ss, cs)
            # transfinite_and_recombine_complex(c, ss, cs)
        else:
            print('Correct and Transfinite')
            c.transfinite(ss, cs)
            # correct_and_transfinite_complex(c, ss, cs)
            # transfinite_complex(c, ss, cs)
        print(time.time() - t0)
        print('Autosize')
        t0 = time.time()
        if args['auto_size'] is not None:
            print('Auto Size: {}'.format(args['auto_size']))
            pss = dict()
            auto_complex_points_sizes_min_curve_in_volume(c, pss,
                                                          args['auto_size'])
        if args['size'] is not None:
            print('Set Size: {}'.format(args['size']))
            set_points_sizes(args['size'])
        if args['boundary_auto_size'] is not None:
            print('Boundary Auto Size: {}'.format(args['boundary_auto_size']))
            auto_boundary_points_sizes_min_edge_in_surface(
                args['boundary_auto_size'])
        if args['boundary_size'] is not None:
            print('Set Boundary Size: {}'.format(args['boundary_size']))
            set_boundary_points_sizes(args['boundary_size'])
        print(time.time() - t0)
        print("Physical Volumes")
        t0 = time.time()
        ns_to_vs = c.get_map_names_to_volumes()
        for n, vs in ns_to_vs.items():
            tag = gmsh.model.addPhysicalGroup(3, vs)
            gmsh.model.setPhysicalName(3, tag, n)
        print(time.time() - t0)
        print("Physical Surfaces")
        t0 = time.time()
        if args['boundary_type'] == '6':
            print("6 surfaces")
            boundary_surfaces_groups = boundary_surfaces_to_six_side_groups()
            for n, ss in boundary_surfaces_groups.items():
                tag = gmsh.model.addPhysicalGroup(2, ss)
                gmsh.model.setPhysicalName(2, tag, n)
        elif args['boundary_type'] == 'primitive':
            map_names_to_surfaces = dict()
            s_to_is = c.get_map_surface_to_primitives_surfaces_indices()
            boundary_surfaces = get_boundary_surfaces()
            for s in boundary_surfaces:
                primitives_surfaces_indices = s_to_is[s]
                index, surface_index = primitives_surfaces_indices[0]
                surface_name = c.primitives[index].surfaces_names[
                    surface_index]
                map_names_to_surfaces.setdefault(
                    surface_name, list()).append(s)
            for n, ss in map_names_to_surfaces.items():
                tag = gmsh.model.addPhysicalGroup(2, ss)
                gmsh.model.setPhysicalName(2, tag, n)
        elif args['boundary_type'] == 'all':
            print("All surfaces")
            boundary_surfaces = get_boundary_surfaces()
            for i, s in enumerate(boundary_surfaces):
                name = 'S{0}'.format(s)
                tag = gmsh.model.addPhysicalGroup(2, [s])
                gmsh.model.setPhysicalName(2, tag, name)
        else:
            print("By support.physical_surfaces")
            physical_surfaces(**physical_surfaces_kwargs)
        print(time.time() - t0)
        print("Mesh")
        t0 = time.time()
        gmsh.model.mesh.generate(3)
        print(time.time() - t0)
        print('Nodes: {0}'.format(len(gmsh.model.mesh.getNodes()[0])))
        # t0 = time.time()
        # gmsh.model.mesh.removeDuplicateNodes()
        # print(time.time() - t0)
        # print('Nodes: {0}'.format(len(gmsh.model.mesh.getNodes()[0])))
        # es = gmsh.model.mesh.getElements()
        if args['optimize']:
            print("Optimize Mesh")
            t0 = time.time()
            gmsh.model.mesh.optimize('Optimize', True)
            print(time.time() - t0)
    print("Write: {}".format(args['output_path']))
    t0 = time.time()
    gmsh.write(args['output_path'])
    print(time.time() - t0)
    gmsh.finalize()
    print('Time spent: {}s'.format(time.time() - t00))
