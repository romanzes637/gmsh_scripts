import json
import os
import argparse
import socket
from pprint import pprint
import sys

import gmsh
from complex_primitive import ComplexPrimitive
from cylinder import Cylinder
from divided_cylinder import DividedCylinder
from occ_workarounds import correct_and_transfinite_complex


class ComplexFactory:
    def __init__(self):
        pass

    @staticmethod
    def new(input_data):
        """
        Complex's child objects factory by item 'class_name':'Complex's child class name' in input_data['metadata'].
        :param dict input_data: dict should have at least two items: 'metadata':dict and 'arguments':dict,
        'metadata' dict should be 'class_name' item and 'arguments' dict should coincide with child object __init__
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


if __name__ == '__main__':
    print('Python: {0}'.format(sys.executable))
    print('Script: {0}'.format(__file__))
    print('Working Directory: {0}'.format(os.getcwd()))
    print('Host: {}'.format(socket.gethostname()))
    print('PID: {}'.format(os.getpid()))
    print('Arguments')
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--input', help='input filename', required=True)
    parser.add_argument('-o', '--output', help='output filename')
    parser.add_argument('-v', '--verbose', help='verbose', action='store_true')
    parser.add_argument('-t', '--test', help='test mode', action='store_true')
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
    gmsh.initialize()
    if is_verbose:
        gmsh.option.setNumber("General.Terminal", 1)
    else:
        gmsh.option.setNumber("General.Terminal", 0)
    gmsh.option.setNumber('Geometry.AutoCoherence', 0)  # No effect at gmsh.model.occ factory
    gmsh.model.add(model_name)
    print('Input')
    with open(input_path) as f:
        input_data = json.load(f)
    pprint(input_data)
    print('Initialize')
    c = ComplexFactory.new(input_data)
    factory = c.factory
    print('Synchronize')
    factory.synchronize()
    if not is_test:
        print('Evaluate')
        c.evaluate_coordinates()  # for correct and transfinite
        c.evaluate_bounding_box()  # for boolean
        print('Remove Duplicates')
        factory.removeAllDuplicates()
        print('Synchronize')
        factory.synchronize()
        print('Correct and Transfinite')
        ss = set()
        cs = set()
        correct_and_transfinite_complex(c, ss, cs)
        print('Physical')
        for name in c.map_physical_name_to_primitives_indices.keys():
            vs = c.get_volumes_by_physical_name(name)
            tag = gmsh.model.addPhysicalGroup(3, vs)
            gmsh.model.setPhysicalName(3, tag, name)
        print("Mesh")
        gmsh.model.mesh.generate(3)
        gmsh.model.mesh.removeDuplicateNodes()
        print("Write")
        gmsh.write(output_path + '.msh')
    else:
        print("Write")
        gmsh.write(output_path + '.brep')
    gmsh.finalize()
