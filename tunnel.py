import gmsh

from complex import Complex
from primitive import Primitive


class Tunnel(Complex):
    def __init__(self, factory, transform_data, tunnel_type, args, string_args,
                 array_args, string_array_args):
        """
        :param str factory: see Primitive
        :param list transform_data: see Primitive
        :param int tunnel_type: type for type_factory
        :param list args: float/int arguments
        :param list string_args: string arguments
        :param list of list array_args: arrays of float/int arguments
        :param list of list string_array_args: arrays of string arguments
        """
        if factory == 'occ':
            factory_object = gmsh.model.occ
        else:
            factory_object = gmsh.model.geo
        primitives = list()
        kwargs = locals()
        type_factory[tunnel_type](factory_object, primitives, kwargs)
        Complex.__init__(self, factory, primitives)


def type_0(factory_object, primitives, kwargs):
    pass


def type_1(factory_object, primitives, kwargs):
    # Args
    """
    Arcs: Y Y
    :param factory_object:
    :param primitives:
    :param kwargs:
    """
    factory = kwargs['factory']
    transform_data = kwargs['transform_data']
    args = kwargs['args']
    string_args = kwargs['string_args']
    array_args = kwargs['array_args']
    lx = args[0]
    ly = args[1]
    lz = args[2]
    lc = args[3]
    tt = args[4]
    r = args[5]
    tx = array_args[0]
    ty = array_args[1]
    tz = array_args[2]
    physical_name = string_args[0]
    # Init
    hlx = lx / 2
    hly = ly / 2
    hlz = lz / 2
    p = Primitive(
        factory=factory,
        point_data=[
            [hlx, hly, -hlz, lc],
            [-hlx, hly, -hlz, lc],
            [-hlx, -hly, -hlz, lc],
            [hlx, -hly, -hlz, lc],
            [hlx, hly, hlz, lc],
            [-hlx, hly, hlz, lc],
            [-hlx, -hly, hlz, lc],
            [hlx, -hly, hlz, lc],
        ],
        transform_data=transform_data,
        curve_types=[0, 0, 0, 0, 0, 0, 3, 3, 0, 0, 0, 0],
        curve_data=[
            [], [], [], [],
            [], [], [[-hlx, 0, hlz + r]], [[hlx, 0, hlz + r]],
            [], [], [], []
        ],
        transfinite_data=[tx, ty, tz],
        transfinite_type=tt,
        physical_name=physical_name
    )
    primitives.append(p)


def type_2(factory_object, primitives, kwargs):
    # Args
    """
    Arcs: X X
    :param factory_object:
    :param primitives:
    :param kwargs:
    """
    factory = kwargs['factory']
    transform_data = kwargs['transform_data']
    args = kwargs['args']
    string_args = kwargs['string_args']
    array_args = kwargs['array_args']
    lx = args[0]
    ly = args[1]
    lz = args[2]
    lc = args[3]
    tt = args[4]
    r = args[5]
    tx = array_args[0]
    ty = array_args[1]
    tz = array_args[2]
    physical_name = string_args[0]
    # Init
    hlx = lx / 2
    hly = ly / 2
    hlz = lz / 2
    p = Primitive(
        factory=factory,
        point_data=[
            [hlx, hly, -hlz, lc],
            [-hlx, hly, -hlz, lc],
            [-hlx, -hly, -hlz, lc],
            [hlx, -hly, -hlz, lc],
            [hlx, hly, hlz, lc],
            [-hlx, hly, hlz, lc],
            [-hlx, -hly, hlz, lc],
            [hlx, -hly, hlz, lc],
        ],
        transform_data=transform_data,
        curve_types=[0, 3, 3, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        curve_data=[
            [], [[0, hly, hlz + r]], [[0, -hly, hlz + r]], [],
            [], [], [], [],
            [], [], [], []
        ],
        transfinite_data=[tx, ty, tz],
        transfinite_type=tt,
        physical_name=physical_name
    )
    primitives.append(p)


def type_3(factory_object, primitives, kwargs):
    # Args
    """
    Arcs: X Y
    :param factory_object:
    :param primitives:
    :param kwargs:
    """
    factory = kwargs['factory']
    transform_data = kwargs['transform_data']
    args = kwargs['args']
    string_args = kwargs['string_args']
    array_args = kwargs['array_args']
    lx = args[0]
    ly = args[1]
    lz = args[2]
    lc = args[3]
    tt = args[4]
    r = args[5]
    tx = array_args[0]
    ty = array_args[1]
    tz = array_args[2]
    physical_name = string_args[0]
    # Init
    hlx = lx / 2
    hly = ly / 2
    hlz = lz / 2
    p = Primitive(
        factory=factory,
        point_data=[
            [hlx, hly, -hlz, lc],
            [-hlx, hly, -hlz, lc],
            [-hlx, -hly, -hlz, lc],
            [hlx, -hly, -hlz, lc],
            [hlx, hly, hlz, lc],
            [-hlx, hly, hlz, lc],
            [-hlx, -hly, hlz, lc],
            [hlx, -hly, hlz, lc],
        ],
        transform_data=transform_data,
        curve_types=[0, 3, 0, 0, 0, 0, 0, 3, 0, 0, 0, 0],
        curve_data=[
            [], [[0, hly, hlz + r]], [], [],
            [], [], [], [[hlx, 0, hlz + r]],
            [], [], [], []
        ],
        transfinite_data=[tx, ty, tz],
        transfinite_type=tt,
        physical_name=physical_name
    )
    primitives.append(p)


def type_4(factory_object, primitives, kwargs):
    # Args
    """
    Arcs: NX Y
    :param factory_object:
    :param primitives:
    :param kwargs:
    """
    factory = kwargs['factory']
    transform_data = kwargs['transform_data']
    args = kwargs['args']
    string_args = kwargs['string_args']
    array_args = kwargs['array_args']
    lx = args[0]
    ly = args[1]
    lz = args[2]
    lc = args[3]
    tt = args[4]
    r = args[5]
    tx = array_args[0]
    ty = array_args[1]
    tz = array_args[2]
    physical_name = string_args[0]
    # Init
    hlx = lx / 2
    hly = ly / 2
    hlz = lz / 2
    p = Primitive(
        factory=factory,
        point_data=[
            [hlx, hly, -hlz, lc],
            [-hlx, hly, -hlz, lc],
            [-hlx, -hly, -hlz, lc],
            [hlx, -hly, -hlz, lc],
            [hlx, hly, hlz, lc],
            [-hlx, hly, hlz, lc],
            [-hlx, -hly, hlz, lc],
            [hlx, -hly, hlz, lc],
        ],
        transform_data=transform_data,
        curve_types=[0, 3, 0, 0, 0, 0, 3, 0, 0, 0, 0, 0],
        curve_data=[
            [], [[0, hly, hlz + r]], [], [],
            [], [], [[-hlx, 0, hlz + r]], [],
            [], [], [], []
        ],
        transfinite_data=[tx, ty, tz],
        transfinite_type=tt,
        physical_name=physical_name
    )
    primitives.append(p)


def type_5(factory_object, primitives, kwargs):
    # Args
    """
    Arcs: NX NY
    :param factory_object:
    :param primitives:
    :param kwargs:
    """
    factory = kwargs['factory']
    transform_data = kwargs['transform_data']
    args = kwargs['args']
    string_args = kwargs['string_args']
    array_args = kwargs['array_args']
    lx = args[0]
    ly = args[1]
    lz = args[2]
    lc = args[3]
    tt = args[4]
    r = args[5]
    tx = array_args[0]
    ty = array_args[1]
    tz = array_args[2]
    physical_name = string_args[0]
    # Init
    hlx = lx / 2
    hly = ly / 2
    hlz = lz / 2
    p = Primitive(
        factory=factory,
        point_data=[
            [hlx, hly, -hlz, lc],
            [-hlx, hly, -hlz, lc],
            [-hlx, -hly, -hlz, lc],
            [hlx, -hly, -hlz, lc],
            [hlx, hly, hlz, lc],
            [-hlx, hly, hlz, lc],
            [-hlx, -hly, hlz, lc],
            [hlx, -hly, hlz, lc],
        ],
        transform_data=transform_data,
        curve_types=[0, 0, 3, 0, 0, 0, 3, 0, 0, 0, 0, 0],
        curve_data=[
            [], [], [[0, -hly, hlz + r]], [],
            [], [], [[-hlx, 0, hlz + r]], [],
            [], [], [], []
        ],
        transfinite_data=[tx, ty, tz],
        transfinite_type=tt,
        physical_name=physical_name
    )
    primitives.append(p)


def type_6(factory_object, primitives, kwargs):
    # Args
    """
    Arcs: X NY
    :param factory_object:
    :param primitives:
    :param kwargs:
    """
    factory = kwargs['factory']
    transform_data = kwargs['transform_data']
    args = kwargs['args']
    string_args = kwargs['string_args']
    array_args = kwargs['array_args']
    lx = args[0]
    ly = args[1]
    lz = args[2]
    lc = args[3]
    tt = args[4]
    r = args[5]
    tx = array_args[0]
    ty = array_args[1]
    tz = array_args[2]
    physical_name = string_args[0]
    # Init
    hlx = lx / 2
    hly = ly / 2
    hlz = lz / 2
    p = Primitive(
        factory=factory,
        point_data=[
            [hlx, hly, -hlz, lc],
            [-hlx, hly, -hlz, lc],
            [-hlx, -hly, -hlz, lc],
            [hlx, -hly, -hlz, lc],
            [hlx, hly, hlz, lc],
            [-hlx, hly, hlz, lc],
            [-hlx, -hly, hlz, lc],
            [hlx, -hly, hlz, lc],
        ],
        transform_data=transform_data,
        curve_types=[0, 0, 3, 0, 0, 0, 0, 3, 0, 0, 0, 0],
        curve_data=[
            [], [], [[0, -hly, hlz + r]], [],
            [], [], [], [[hlx, 0, hlz + r]],
            [], [], [], []
        ],
        transfinite_data=[tx, ty, tz],
        transfinite_type=tt,
        physical_name=physical_name
    )
    primitives.append(p)


def type_7(factory_object, primitives, kwargs):
    # Args
    """
    Arcs: X Y NX
    :param factory_object:
    :param primitives:
    :param kwargs:
    """
    factory = kwargs['factory']
    transform_data = kwargs['transform_data']
    args = kwargs['args']
    string_args = kwargs['string_args']
    array_args = kwargs['array_args']
    lx = args[0]
    ly = args[1]
    lz = args[2]
    lc = args[3]
    tt = args[4]
    r = args[5]
    tx = array_args[0]
    ty = array_args[1]
    tz = array_args[2]
    physical_name = string_args[0]
    # Init
    hlx = lx / 2
    hly = ly / 2
    hlz = lz / 2
    p = Primitive(
        factory=factory,
        point_data=[
            [hlx, hly, -hlz, lc],
            [-hlx, hly, -hlz, lc],
            [-hlx, -hly, -hlz, lc],
            [hlx, -hly, -hlz, lc],
            [hlx, hly, hlz, lc],
            [-hlx, hly, hlz, lc],
            [-hlx, -hly, hlz, lc],
            [hlx, -hly, hlz, lc],
        ],
        transform_data=transform_data,
        curve_types=[0, 0, 3, 0, 0, 0, 3, 3, 0, 0, 0, 0],
        curve_data=[
            [], [], [[0, -hly, hlz + r]], [],
            [], [], [[-hlx, 0, hlz + r]], [[hlx, 0, hlz + r]],
            [], [], [], []
        ],
        transfinite_data=[tx, ty, tz],
        transfinite_type=tt,
        physical_name=physical_name
    )
    primitives.append(p)


def type_8(factory_object, primitives, kwargs):
    # Args
    """
    Arcs: X Y NY
    :param factory_object:
    :param primitives:
    :param kwargs:
    """
    factory = kwargs['factory']
    transform_data = kwargs['transform_data']
    args = kwargs['args']
    string_args = kwargs['string_args']
    array_args = kwargs['array_args']
    lx = args[0]
    ly = args[1]
    lz = args[2]
    lc = args[3]
    tt = args[4]
    r = args[5]
    tx = array_args[0]
    ty = array_args[1]
    tz = array_args[2]
    physical_name = string_args[0]
    # Init
    hlx = lx / 2
    hly = ly / 2
    hlz = lz / 2
    p = Primitive(
        factory=factory,
        point_data=[
            [hlx, hly, -hlz, lc],
            [-hlx, hly, -hlz, lc],
            [-hlx, -hly, -hlz, lc],
            [hlx, -hly, -hlz, lc],
            [hlx, hly, hlz, lc],
            [-hlx, hly, hlz, lc],
            [-hlx, -hly, hlz, lc],
            [hlx, -hly, hlz, lc],
        ],
        transform_data=transform_data,
        curve_types=[0, 3, 3, 0, 0, 0, 0, 3, 0, 0, 0, 0],
        curve_data=[
            [], [[0, hly, hlz + r]], [[0, -hly, hlz + r]], [],
            [], [], [], [[hlx, 0, hlz + r]],
            [], [], [], []
        ],
        transfinite_data=[tx, ty, tz],
        transfinite_type=tt,
        physical_name=physical_name
    )
    primitives.append(p)


def type_9(factory_object, primitives, kwargs):
    # Args
    """
    Arcs: NX NY X
    :param factory_object:
    :param primitives:
    :param kwargs:
    """
    factory = kwargs['factory']
    transform_data = kwargs['transform_data']
    args = kwargs['args']
    string_args = kwargs['string_args']
    array_args = kwargs['array_args']
    lx = args[0]
    ly = args[1]
    lz = args[2]
    lc = args[3]
    tt = args[4]
    r = args[5]
    tx = array_args[0]
    ty = array_args[1]
    tz = array_args[2]
    physical_name = string_args[0]
    # Init
    hlx = lx / 2
    hly = ly / 2
    hlz = lz / 2
    p = Primitive(
        factory=factory,
        point_data=[
            [hlx, hly, -hlz, lc],
            [-hlx, hly, -hlz, lc],
            [-hlx, -hly, -hlz, lc],
            [hlx, -hly, -hlz, lc],
            [hlx, hly, hlz, lc],
            [-hlx, hly, hlz, lc],
            [-hlx, -hly, hlz, lc],
            [hlx, -hly, hlz, lc],
        ],
        transform_data=transform_data,
        curve_types=[0, 0, 3, 0, 0, 0, 3, 3, 0, 0, 0, 0],
        curve_data=[
            [], [], [[0, -hly, hlz + r]], [],
            [], [], [[-hlx, 0, hlz + r]], [[hlx, 0, hlz + r]],
            [], [], [], []
        ],
        transfinite_data=[tx, ty, tz],
        transfinite_type=tt,
        physical_name=physical_name
    )
    primitives.append(p)


def type_10(factory_object, primitives, kwargs):
    # Args
    """
    Arcs: NX NY Y
    :param factory_object:
    :param primitives:
    :param kwargs:
    """
    factory = kwargs['factory']
    transform_data = kwargs['transform_data']
    args = kwargs['args']
    string_args = kwargs['string_args']
    array_args = kwargs['array_args']
    lx = args[0]
    ly = args[1]
    lz = args[2]
    lc = args[3]
    tt = args[4]
    r = args[5]
    tx = array_args[0]
    ty = array_args[1]
    tz = array_args[2]
    physical_name = string_args[0]
    # Init
    hlx = lx / 2
    hly = ly / 2
    hlz = lz / 2
    p = Primitive(
        factory=factory,
        point_data=[
            [hlx, hly, -hlz, lc],
            [-hlx, hly, -hlz, lc],
            [-hlx, -hly, -hlz, lc],
            [hlx, -hly, -hlz, lc],
            [hlx, hly, hlz, lc],
            [-hlx, hly, hlz, lc],
            [-hlx, -hly, hlz, lc],
            [hlx, -hly, hlz, lc],
        ],
        transform_data=transform_data,
        curve_types=[0, 3, 3, 0, 0, 0, 3, 0, 0, 0, 0, 0],
        curve_data=[
            [], [[0, hly, hlz + r]], [[0, -hly, hlz + r]], [],
            [], [], [[-hlx, 0, hlz + r]], [],
            [], [], [], []
        ],
        transfinite_data=[tx, ty, tz],
        transfinite_type=tt,
        physical_name=physical_name
    )
    primitives.append(p)


def type_11(factory_object, primitives, kwargs):
    # Args
    """
    Arcs: X Y NX NY
    :param factory_object:
    :param primitives:
    :param kwargs:
    """
    factory = kwargs['factory']
    transform_data = kwargs['transform_data']
    args = kwargs['args']
    string_args = kwargs['string_args']
    array_args = kwargs['array_args']
    lx = args[0]
    ly = args[1]
    lz = args[2]
    lc = args[3]
    tt = args[4]
    r = args[5]
    tx = array_args[0]
    ty = array_args[1]
    tz = array_args[2]
    physical_name = string_args[0]
    # Init
    hlx = lx / 2
    hly = ly / 2
    hlz = lz / 2
    p = Primitive(
        factory=factory,
        point_data=[
            [hlx, hly, -hlz, lc],
            [-hlx, hly, -hlz, lc],
            [-hlx, -hly, -hlz, lc],
            [hlx, -hly, -hlz, lc],
            [hlx, hly, hlz, lc],
            [-hlx, hly, hlz, lc],
            [-hlx, -hly, hlz, lc],
            [hlx, -hly, hlz, lc],
        ],
        transform_data=transform_data,
        curve_types=[0, 3, 3, 0, 0, 0, 3, 3, 0, 0, 0, 0],
        curve_data=[
            [], [[0, hly, hlz + r]], [[0, -hly, hlz + r]], [],
            [], [], [[-hlx, 0, hlz + r]], [[hlx, 0, hlz + r]],
            [], [], [], []
        ],
        transfinite_data=[tx, ty, tz],
        transfinite_type=tt,
        physical_name=physical_name
    )
    primitives.append(p)


type_factory = {
    0: type_0,  # None
    1: type_1,  # Arcs: X X
    2: type_2,  # Arcs: Y Y
    3: type_3,  # Arcs: X Y
    4: type_4,  # Arcs: NX Y
    5: type_5,  # Arcs: NX NY
    6: type_6,  # Arcs: X NY
    7: type_7,  # Arcs: X Y NX
    8: type_8,  # Arcs: X Y NY
    9: type_9,  # Arcs: NX NY X
    10: type_10,  # Arcs: NX NY Y
    11: type_11,  # Arcs: X Y NX NY
}
