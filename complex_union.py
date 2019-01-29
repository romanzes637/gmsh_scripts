import json

import gmsh

from boolean import complex_self
from complex import Complex
from support import check_file


class ComplexUnion(Complex):
    def __init__(self, factory, inputs):
        from complex_factory import ComplexFactory
        if factory == 'occ':
            factory_object = gmsh.model.occ
        else:
            factory_object = gmsh.model.geo
        primitives = list()
        for i in inputs:
            result = check_file(i)
            with open(result['path']) as f:
                input_data = json.load(f)
                input_data['arguments']['factory'] = factory
            c = ComplexFactory.new(input_data)
            primitives.extend(c.primitives)
        Complex.__init__(self, factory, primitives)
        print('Synchronize')
        factory_object.synchronize()
        print('Evaluate')
        self.evaluate_coordinates()
        self.evaluate_bounding_box()
        print('Self Boolean')
        complex_self(factory_object, self)
