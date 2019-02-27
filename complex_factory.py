import json
import os
import argparse
import socket
from pprint import pprint
import sys

import gmsh

from boolean import complex_self
from complex_primitive import ComplexPrimitive
from complex_union import ComplexUnion
from cylinder import Cylinder
from divided_cylinder import DividedCylinder
from experiment import Experiment
from matrix import Matrix
from pool import Pool
from polygon import Polygon
from tunnel import Tunnel
from occ_workarounds import correct_and_transfinite_complex, \
    correct_and_transfinite_and_recombine_complex
from support import boundary_surfaces_to_six_side_groups, \
    get_boundary_surfaces, check_file, physical_surfaces, \
    auto_complex_points_sizes_min_curve_in_volume, set_boundary_points_sizes, \
    auto_boundary_points_sizes, auto_boundary_points_sizes_min_edge_in_surface, \
    set_points_sizes


class ComplexFactory:
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
        if class_name == ComplexPrimitive.__name__:
            return ComplexPrimitive(**kwargs)
        if class_name == Cylinder.__name__:
            return Cylinder(**kwargs)
        if class_name == DividedCylinder.__name__:
            return DividedCylinder(**kwargs)
        if class_name == Matrix.__name__:
            return Matrix(**kwargs)
        if class_name == Tunnel.__name__:
            return Tunnel(**kwargs)
        if class_name == Experiment.__name__:
            return Experiment(**kwargs)
        if class_name == ComplexUnion.__name__:
            return ComplexUnion(**kwargs)
        if class_name == Polygon.__name__:
            return Polygon(**kwargs)
        if class_name == Pool.__name__:
            return Pool(**kwargs)


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
                        default='6', choices=['6', 'all', 'path_to_file'])
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
        args['mesh_algorithm'] = cmd_args.mesh_algorithm
    root, extension = os.path.splitext(args['input_path'])
    basename = os.path.basename(root)
    if args['output_path'] is None:
        if not args['test']:
            args['output_path'] = basename + '.msh2'
        else:
            args['output_path'] = basename + '.brep'
    if args['boundary_type'] not in ['6', 'all']:
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
    gmsh.option.setNumber('Mesh.Algorithm3D', args['mesh_algorithm'])
    print('Model')
    model_name = basename
    gmsh.model.add(model_name)
    print('Initialize')
    c = ComplexFactory.new(input_data)
    factory = c.factory
    print('Synchronize')
    factory.synchronize()
    if not args['test']:
        print('Evaluate')
        c.evaluate_coordinates()  # for correct and transfinite
        c.evaluate_bounding_box()  # for boolean
        if args['boolean']:
            print("Boolean")
            complex_self(factory, c)
        print('Remove Duplicates')
        factory.removeAllDuplicates()
        print('Synchronize')
        factory.synchronize()
        # Primitive/Complex Correction
        ss = set()
        cs = set()
        if args['recombine']:
            print('Correct and Transfinite and Recombine')
            correct_and_transfinite_and_recombine_complex(c, ss, cs)
        else:
            print('Correct and Transfinite')
            correct_and_transfinite_complex(c, ss, cs)
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
        print('Physical')
        print("Volumes")
        for name in c.map_physical_name_to_primitives_indices.keys():
            vs = c.get_volumes_by_physical_name(name)
            tag = gmsh.model.addPhysicalGroup(3, vs)
            gmsh.model.setPhysicalName(3, tag, name)
        print("Surfaces")
        if args['boundary_type'] == '6':
            print("6 surfaces")
            boundary_surfaces_groups = boundary_surfaces_to_six_side_groups()
            for i, (name, ss) in enumerate(
                    boundary_surfaces_groups.items()):
                tag = gmsh.model.addPhysicalGroup(2, ss)
                gmsh.model.setPhysicalName(2, tag, name)
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
        print("Mesh")
        gmsh.model.mesh.generate(3)
        gmsh.model.mesh.removeDuplicateNodes()
    print("Write: {}".format(args['output_path']))
    gmsh.write(args['output_path'])
    gmsh.finalize()
