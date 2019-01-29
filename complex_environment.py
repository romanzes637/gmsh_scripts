import argparse
import json
import socket
from pprint import pprint

import gmsh
import os

import sys

from boolean import complex_by_complex
from complex_factory import ComplexFactory
from occ_workarounds import correct_and_transfinite_complex
from support import check_file, physical_surfaces, get_boundary_surfaces, \
    boundary_surfaces_to_six_side_groups, \
    auto_complex_points_sizes_min_curve_in_volume

if __name__ == '__main__':
    print('Python: {0}'.format(sys.executable))
    print('Script: {0}'.format(__file__))
    print('Working Directory: {0}'.format(os.getcwd()))
    print('Host: {0}'.format(socket.gethostname()))
    print('PID: {0}'.format(os.getpid()))
    print('Arguments')
    parser = argparse.ArgumentParser()
    parser.add_argument('input', help='input filename')
    parser.add_argument('-o', '--output', help='output filename')
    parser.add_argument('-v', '--verbose', help='verbose', action='store_true')
    parser.add_argument('-t', '--test', help='test mode', action='store_true')
    parser.add_argument('-r', '--recombine', help='recombine',
                        action='store_true')
    parser.add_argument('-b', '--boolean', help='boolean', action='store_true')
    parser.add_argument('-a', '--all_boundaries', help='all_boundaries',
                        action='store_true')
    parser.add_argument('-p', '--physical_surfaces',
                        help='support.physical_surfaces input filename')
    parser.add_argument('-s', '--size', type=float, metavar=0.1,
                        help='mesh auto sizing with size factor (default: 1.0)',
                        default=None, nargs='?', const=1.0)
    args = parser.parse_args()
    print(args)
    root, extension = os.path.splitext(args.input)
    basename = os.path.basename(root)
    if args.output is None:
        output_path = basename
    else:
        output_path = args.output
    is_test = args.test
    is_verbose = args.verbose
    input_path = args.input
    model_name = basename
    is_recombine = args.recombine
    is_boolean = args.boolean
    is_all_boundaries = args.all_boundaries
    size = args.size
    if args.physical_surfaces is None:
        is_physical_surfaces = False
    else:
        is_physical_surfaces = True
    gmsh.initialize()
    # gmsh options
    if is_verbose:
        gmsh.option.setNumber("General.Terminal", 1)
    else:
        gmsh.option.setNumber("General.Terminal", 0)
    gmsh.option.setNumber('Geometry.AutoCoherence', 0)  # No effect at occ
    # 1: Delaunay, 4: Frontal, 5: Frontal Delaunay, 6: Frontal Hex, 7: MMG3D,
    # 9: R-tree, 10: HXT
    gmsh.option.setNumber('Mesh.Algorithm3D', 1)
    gmsh.model.add(model_name)
    print('Input Complex Environment')
    result = check_file(input_path)
    with open(result['path']) as f:
        input_data = json.load(f)
    pprint(input_data)
    print('Input Environment')
    result = check_file(input_data['arguments']['environment'])
    with open(result['path']) as f:
        e_data = json.load(f)
        e_data['arguments']['factory'] = input_data['arguments']['factory']
    pprint(e_data)
    print('Input Complex')
    result = check_file(input_data['arguments']['complex'])
    with open(result['path']) as f:
        c_data = json.load(f)
        c_data['arguments']['factory'] = input_data['arguments']['factory']
    pprint(c_data)
    print('Initialize')
    print('Environment')
    e = ComplexFactory.new(e_data)
    print('Complex')
    c = ComplexFactory.new(c_data)
    if input_data['arguments']['factory'] == 'occ':
        factory = gmsh.model.occ
    else:
        factory = gmsh.model.geo
    print('Synchronize')
    factory.synchronize()
    if not is_test:
        print('Evaluate')
        e.evaluate_coordinates()  # for correct and transfinite
        c.evaluate_coordinates()  # for correct and transfinite
        if is_boolean:
            print("Boolean")
            e.evaluate_bounding_box()  # for boolean
            c.evaluate_bounding_box()  # for boolean
            complex_by_complex(factory, e, c)
        print('Remove Duplicates')
        factory.removeAllDuplicates()
        print('Synchronize')
        factory.synchronize()
        print('Correct and Transfinite')
        ss = set()
        cs = set()
        correct_and_transfinite_complex(e, ss, cs)
        correct_and_transfinite_complex(c, ss, cs)
        if size is not None:
            print('Set Size')
            pss = dict()
            auto_complex_points_sizes_min_curve_in_volume(c, pss, size)
        if is_recombine:
            print('Recombine')
            e.recombine()
            c.recombine()
        print('Physical')
        print("Volumes")
        print('Environment')
        for name in e.map_physical_name_to_primitives_indices.keys():
            vs = e.get_volumes_by_physical_name(name)
            tag = gmsh.model.addPhysicalGroup(3, vs)
            gmsh.model.setPhysicalName(3, tag, name)
        print('Complex')
        for name in c.map_physical_name_to_primitives_indices.keys():
            vs = c.get_volumes_by_physical_name(name)
            tag = gmsh.model.addPhysicalGroup(3, vs)
            gmsh.model.setPhysicalName(3, tag, name)
        print("Surfaces")
        if is_physical_surfaces:
            print("By support.physical_surfaces")
            print("Input for support.physical_surfaces")
            result = check_file(args.physical_surfaces)
            with open(result['path']) as f:
                physical_surfaces_input = json.load(f)
            # pprint(physical_surfaces_input)
            physical_surfaces_kwargs = physical_surfaces_input['arguments']
            physical_surfaces(**physical_surfaces_kwargs)
        else:
            if is_all_boundaries:
                print("All surfaces")
                boundary_surfaces = get_boundary_surfaces()
                for i, s in enumerate(boundary_surfaces):
                    name = 'S{0}'.format(s)
                    tag = gmsh.model.addPhysicalGroup(2, [s])
                    gmsh.model.setPhysicalName(2, tag, name)
            else:
                print("6 surfaces")
                boundary_surfaces_groups = boundary_surfaces_to_six_side_groups()
                for i, (name, ss) in enumerate(
                        boundary_surfaces_groups.items()):
                    tag = gmsh.model.addPhysicalGroup(2, ss)
                    gmsh.model.setPhysicalName(2, tag, name)
        print("Mesh")
        gmsh.model.mesh.generate(3)
        gmsh.model.mesh.removeDuplicateNodes()
        print("Write")
        gmsh.write(output_path + '.msh')
    else:
        print("Write")
        gmsh.write(output_path + '.brep')
    gmsh.finalize()
