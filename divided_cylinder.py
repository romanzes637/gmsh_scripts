import argparse
import json
from pprint import pprint
import os

import gmsh

from cylinder import Cylinder
from occ_workarounds import correct_and_transfinite_complex


class DividedCylinder(Cylinder):
    def __init__(self, factory, radii, heights, layers_lcs, transform_data, layers_physical_names,
                 transfinite_r_data, transfinite_h_data, transfinite_phi_data, divide_r_data, divide_h_data):
        """
        Divided multilayer cylinder for boolean operations
        :param str factory: see Cylinder
        :param list of float radii: see Cylinder
        :param list of float heights: see Cylinder
        :param list of list of float layers_lcs: see Cylinder
        :param list of float transform_data: see Cylinder
        :param list of list of str layers_physical_names: see Cylinder
        :param list of list of float transfinite_r_data: see Cylinder
        :param list of list of float transfinite_h_data: see Cylinder
        :param list of float transfinite_phi_data: see Cylinder
        :param list of int divide_r_data: [number of r1 parts, number of r2 parts, ..., number of rN parts]
        :param list of int divide_h_data: [number of h1 parts, number of h2 parts, ..., number of hM parts]
        :return None
        """
        new_radii = list()
        new_heights = list()
        new_layers_physical_names = list()
        new_primitives_lcs = list()
        new_transfinite_r_data = list()
        new_transfinite_h_data = list()
        map_new_to_old_r = dict()
        map_old_to_new_r = dict()
        map_old_to_new_h = dict()
        map_new_to_old_h = dict()
        # Evaluate new radii
        for i, n in enumerate(divide_r_data):
            map_old_to_new_r[i] = list()
            if i == 0:
                r0 = 0
                r1 = radii[i]
            else:
                r0 = radii[i - 1]
                r1 = radii[i]
            delta_r = float(r1 - r0)  # total delta
            dr = delta_r / n  # increment delta
            r = r0  # new r
            for j in range(n):
                r += dr
                new_radii.append(r)
                new_i = len(new_radii) - 1
                map_old_to_new_r[i].append(new_i)
                map_new_to_old_r[new_i] = i
        # Evaluate new heights
        for i, n in enumerate(divide_h_data):
            map_old_to_new_h[i] = list()
            h0 = 0
            h1 = heights[i]
            delta_h = float(h1 - h0)  # total delta
            dh = delta_h / n  # increment delta
            for j in range(n):
                new_heights.append(dh)
                new_i = len(new_heights) - 1
                map_old_to_new_h[i].append(new_i)
                map_new_to_old_h[new_i] = i
        # Evaluate new 1d arrays
        for i, h in enumerate(new_heights):
            old_i = map_new_to_old_h[i]
            new_transfinite_h_data.append(transfinite_h_data[old_i])
        for j, r in enumerate(new_radii):
            old_j = map_new_to_old_r[j]
            new_transfinite_r_data.append(transfinite_r_data[old_j])
        # Evaluate new 2d arrays
        for i, h in enumerate(new_heights):
            old_i = map_new_to_old_h[i]
            radii_lcs = list()
            radii_physical_names = list()
            for j, r in enumerate(new_radii):
                old_j = map_new_to_old_r[j]
                radii_lcs.append(layers_lcs[old_i][old_j])
                radii_physical_names.append(layers_physical_names[old_i][old_j])
            new_primitives_lcs.append(radii_lcs)
            new_layers_physical_names.append(radii_physical_names)
        # pprint(map_old_to_new_r)
        # pprint(map_old_to_new_h)
        # print(new_radii)
        # print(new_heights)
        # print(new_layers_physical_names)
        # print(new_primitives_lcs)
        # print(new_transfinite_r_data)
        # print(new_transfinite_h_data)
        Cylinder.__init__(self, factory, new_radii, new_heights, new_primitives_lcs, transform_data,
                          new_layers_physical_names, new_transfinite_r_data, new_transfinite_h_data,
                          transfinite_phi_data)


if __name__ == '__main__':
    print('Arguments')
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--input', help='input filename', default='input_test_divided_cylinder.json')
    parser.add_argument('-o', '--output', help='output filename')
    parser.add_argument('-v', '--verbose', help='verbose', action='store_true')
    parser.add_argument('-t', '--test', help='test mode', action='store_true')
    args = parser.parse_args()
    basename, extension = os.path.splitext(args.input)
    if args.output is None:
        args.output = basename
    print(args)
    is_test = args.test
    is_verbose = args.verbose
    output_path = args.output
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
        d = json.load(f)
    pprint(d)
    print('Initialize')
    cylinder = DividedCylinder(**d)
    factory = cylinder.factory
    print('Synchronize')
    factory.synchronize()
    if not is_test:
        print('Evaluate')
        cylinder.evaluate_coordinates()  # for correct and transfinite
        cylinder.evaluate_bounding_box()  # for boolean
        print('Remove Duplicates')
        factory.removeAllDuplicates()
        print('Synchronize')
        factory.synchronize()
        print('Correct and Transfinite')
        ss = set()
        cs = set()
        correct_and_transfinite_complex(cylinder, ss, cs)
        print('Physical')
        for name in cylinder.map_physical_name_to_primitives_indices.keys():
            vs = cylinder.get_volumes_by_physical_name(name)
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
