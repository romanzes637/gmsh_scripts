import gmsh
import json
import numpy as np
import copy  # for dict copy, items of dict are shallow copies

from complex import Complex
from support import check_file


class Point(Complex):
    def __init__(self, factory, coordinate_system,
                 transform_data, coordinates,
                 inputs, inputs_map,
                 transforms, transforms_map):
        """
        Placing Complexes by coordinates in cylindrical coordinate system
        coordinate_system (str): cartesian, cylindrical, spherical
        coordinates (list of list of int):
        [[x, y, z], ...], [[r, phi, z], ...] or [[r, phi, theta], ...], where
        x, y, z  (inf, inf),
        r - radius [0, inf),
        phi - azimuthal angle [0, 360) (counterclockwise from X to Y),
        theta - polar angle [0, 180] [from top to bottom, i.e XY-plane is 90]
        for other parameters see matrix.py

        """
        if factory == 'occ':
            factory_object = gmsh.model.occ
        elif factory == 'geo':
            factory_object = gmsh.model.geo
        else:
            raise ValueError(factory)

        coordinate_system = 'cartesian' if coordinate_system is None else coordinate_system
        transform_data = [] if transform_data is None else transform_data
        coordinates = [] if coordinates is None else coordinates
        coordinates = np.array(coordinates)
        print(coordinates)
        if coordinate_system == 'cylindrical':
            coordinates = np.apply_along_axis(
                cylindrical_to_cartesian, 1, coordinates)
        elif coordinate_system == 'spherical':
            coordinates = np.apply_along_axis(
                spherical_to_cartesian, 1, coordinates)
        print(coordinates)
        inputs = [] if inputs is None else inputs
        if inputs_map is None:  # default
            inputs_map = [0 for _ in coordinates]
        elif isinstance(inputs_map, int):  # int to list
            inputs_map = [inputs_map for _ in coordinates]
        else:
            raise ValueError(inputs_map)
        transforms = [[]] if transforms is None else transforms
        if transforms_map is None:  # default
            transforms_map = [0 for _ in coordinates]
        elif isinstance(transforms_map, int):  # int to list
            transforms_map = [transforms_map for _ in coordinates]
        else:
            raise ValueError(transforms_map)
        inputs_datas = []
        for i in inputs:
            result = check_file(i)
            with open(result['path']) as f:
                d = json.load(f)
            inputs_datas.append(d)

        primitives = []
        for i, c in enumerate(coordinates):
            input_data = copy.deepcopy(inputs_datas[inputs_map[i]])
            if input_data['arguments'].get('transform_data', None) is None:
                input_data['arguments']['transform_data'] = []
            # print(xcs[gi], ycs[gi], z0s[gi])
            input_data['arguments']['transform_data'].extend([c])
            input_data['arguments']['transform_data'].extend(transform_data)
            print(input_data['arguments']['transform_data'])
            input_data['arguments']['factory'] = factory
            from complex_factory import ComplexFactory
            c = ComplexFactory.new(input_data)
            primitives.extend(c.primitives)
        Complex.__init__(self, factory, primitives)


def cylindrical_to_cartesian(cs):
    return [cs[0] * np.cos(np.radians(cs[1])),
            cs[0] * np.sin(np.radians(cs[1])), cs[2]]


def spherical_to_cartesian(cs):
    return [cs[0] * np.cos(np.radians(cs[1])) * np.sin(np.radians(cs[2])),
            cs[0] * np.sin(np.radians(cs[1])) * np.sin(np.radians(cs[2])),
            cs[0] * np.cos(np.radians(cs[2]))]
