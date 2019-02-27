import json

from complex import Complex
from complex_primitive import ComplexPrimitive
from divided_cylinder import DividedCylinder
from matrix import Matrix
from cylinder import Cylinder
from support import check_file


class Pool(Complex):
    """
    Matrix structure of Complex objects
    """

    def __init__(self, factory, indices, transform_data, complex_origins,
                 complex_inputs_paths):
        """

        :param str factory: see Primitive
        :param list of list of int indices:
        :param list of float transform_data:
        :param list of list of float complex_origins:
        :param list of str complex_inputs_paths:
        """
        from complex_factory import ComplexFactory
        primitives = list()
        for i, index in enumerate(indices):
            print(i)
            print(index)
            complex_origin = complex_origins[i]
            x = transform_data[0] + complex_origin[0]
            y = transform_data[1] + complex_origin[1]
            z = transform_data[2] + complex_origin[2]
            path = complex_inputs_paths[i]
            result = check_file(path)
            with open(result['path']) as f:
                input_data = json.load(f)
            complex_type = input_data['metadata']['class_name']
            input_data['arguments']['factory'] = factory
            if complex_type in [Cylinder.__name__,
                                DividedCylinder.__name__,
                                ComplexPrimitive.__name__,
                                Matrix.__name__
                                ]:
                complex_transform_data = input_data['arguments'][
                    'transform_data']
                if complex_transform_data is not None:
                    complex_transform_data[0] = x
                    complex_transform_data[1] = y
                    complex_transform_data[2] = z
                else:
                    complex_transform_data = [x, y, z]
                input_data['arguments'][
                    'transform_data'] = complex_transform_data
            c = ComplexFactory.new(input_data)
            primitives.extend(c.primitives)
        Complex.__init__(self, factory, primitives)
