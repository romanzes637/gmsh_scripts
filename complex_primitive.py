from primitive import Primitive
from complex import Complex


class ComplexPrimitive(Complex):
    def __init__(self, factory, point_data=None, transform_data=None,
                 curve_types=None, curve_data=None,
                 transfinite_data=None, transfinite_type=None,
                 volume_name=None, inner_volumes=None, surfaces_names=None,
                 rec=None, trans=None):
        """
        Complex with one Primitive
        """
        primitives = [Primitive(factory, point_data=point_data,
                      transform_data=transform_data,
                      curve_types=curve_types, curve_data=curve_data,
                      transfinite_data=transfinite_data,
                      transfinite_type=transfinite_type,
                      volume_name=volume_name, inner_volumes=inner_volumes,
                      surfaces_names=surfaces_names,
                      rec=rec, trans=trans)]
        Complex(factory, primitives)
        Complex.__init__(self, factory, primitives)
