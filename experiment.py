import json

import gmsh

from boolean import complex_by_complex, sort_object_no_shared_no_tool_no_shared
from complex import Complex
from support import check_file


class Experiment(Complex):
    def __init__(self, factory, inputs):
        from complex_factory import ComplexFactory
        if factory == 'occ':
            factory_object = gmsh.model.occ
        else:
            factory_object = gmsh.model.geo
        result = check_file(inputs[0])
        with open(result['path']) as f:
            input_data = json.load(f)
        e = ComplexFactory.new(input_data)
        result = check_file(inputs[3])
        with open(result['path']) as f:
            input_data = json.load(f)
        t = ComplexFactory.new(input_data)
        print('Synchronize')
        factory_object.synchronize()
        print('Evaluate')
        e.evaluate_coordinates()
        e.evaluate_bounding_box()
        t.evaluate_coordinates()
        t.evaluate_bounding_box()
        complex_by_complex(
            factory_object, e, t,
            sort_function=sort_object_no_shared_no_tool_no_shared)
        primitives = list()
        primitives.extend(e.primitives)
        for i in range(1, 3):
            result = check_file(inputs[i])
            with open(result['path']) as f:
                input_data = json.load(f)
            c = ComplexFactory.new(input_data)
            primitives.extend(c.primitives)
        Complex.__init__(self, factory, primitives)
