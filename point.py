import gmsh
import json

from complex import Complex
from support import check_file


class Point(Complex):
    def __init__(self, factory, coordinate_system,
                 transform_data, coordinates,
                 inputs, inputs_map,
                 transforms, transforms_map):
        """Placing Complexes by coordinates in cylindrical coordinate system"""
        if factory == 'occ':
            factory_object = gmsh.model.occ
        elif factory == 'geo':
            factory_object = gmsh.model.geo
        else:
            raise ValueError(factory)
        # cartesian, cylindrical, spherical
        coordinate_system = 'cartesian' if coordinate_system is None else coordinate_system
        transform_data = [] if transform_data is None else transform_data
        coordinates = [] if coordinates is None else coordinates
        inputs = [] if inputs is None else inputs
        if inputs_map is None:  # default
            inputs_map = [0 for _ in range(coordinates)]
        elif isinstance(inputs_map, int):  # int to list
            inputs_map = [inputs_map for _ in range(coordinates)]
        else:
            raise ValueError(inputs_map)
        transforms = [[]] if transforms is None else transforms
        if transforms_map is None:  # default
            transforms_map = [0 for _ in range(coordinates)]
        elif isinstance(transforms_map, int):  # int to list
            transforms_map = [transforms_map for _ in range(coordinates)]
        else:
            raise ValueError(transforms_map)
        inputs_datas = []
        for i in inputs:
            result = check_file(i)
            with open(result['path']) as f:
                d = json.load(f)
            inputs_datas.append(d)

        primitives = []
        Complex.__init__(self, factory, primitives)
