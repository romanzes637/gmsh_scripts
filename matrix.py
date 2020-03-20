import json
from pprint import pprint

import gmsh

from complex import Complex
from primitive import Primitive
from support import check_file


class Matrix(Complex):
    def __init__(self, factory, xs, ys, zs, coordinates_type='direct',
                 lcs=None, transform_data=None, txs=None, tys=None, tzs=None,
                 type_map=None,
                 inputs=None, inputs_map=None,
                 volumes_names=None, volumes_map=None,
                 surfaces_names=None, surfaces_map=None,
                 recs_map=None, trans_map=None):
        """
        Primitives, Complexes and Complex descendants
        as items of 3D matrix structure
        Items data structure (1D array):
        [Z0_Y0_X0, Z0_Y0_X1, ..., Z0_Y0_XN,
         Z0_Y1_X0, Z0_Y1_X1, ..., Z0_Y1_XN,
         ...
         Z0_YM_X0, Z0_YM_X1, ..., Z0_YM_XN,
         Z1_Y0_X0, Z1_Y0_X1, ..., Z1_Y0_XN,
         Z1_Y1_X0, Z1_Y1_X1, ..., Z1_Y1_XN,
         ...
         Z1_YM_X0, Z1_YM_X1, ..., Z1_YM_XN,
         ...
         ...
         ZP_YM_X0, Z0_YM_X1, ..., ZP_YM_XN]
        X0, X1, ..., XN - X layers, where N - number of X layers
        Y0, Y1, ..., YM - Y layers, where M - number of Y layers
        Z0, Z1, ..., ZP - Z layers, where P - number of Z layers
        :param str factory: see Primitive
        :param list of float xs: X axis coordinates
        :param list of float ys: Y axis coordinates
        :param list of float zs: Z axis coordinates
        :param str coordinates_type: 'direct' - exact coordinates or
        'delta' - coordinates differences
        :param list of float lcs: see Primitive
        :param list of float transform_data: see Primitive
        :param list of float txs: X axis transfinite_data (see Primitive)
        :param list of float tys: Y axis transfinite_data (see Primitive)
        :param list of float tzs: Z axis transfinite_data (see Primitive)
        :param list of int type_map: matrix item type (see type_factory below)
        :param list of str inputs: input files
        :param list of int inputs_map: item - input file map
        :param list of str volumes_names: names for items volumes
        :param list of int volumes_map: item - volume name map
        :param list of str surfaces_names: names for items surfaces
        :param list of int surfaces_map: item - surface names map
        :param list of int recs_map: see Primitive
        :param list of int trans_map: see Primitive
        """
        if factory == 'occ':
            factory_object = gmsh.model.occ
        else:
            factory_object = gmsh.model.geo
        if coordinates_type == 'direct':
            nx = len(xs) - 1
            ny = len(ys) - 1
            nz = len(zs) - 1
        elif coordinates_type == 'delta':
            nx = len(xs)
            ny = len(ys)
            nz = len(zs)
        else:
            raise ValueError('coordinates_type: {}'.format(coordinates_type))
        n = nx * ny * nz  # number of matrix items
        if transform_data is None:
            transform_data = [0, 0, 0]
        if txs is None:
            txs = [[3, 0, 1] for _ in range(nx)]
        if tys is None:
            tys = [[3, 0, 1] for _ in range(ny)]
        if tzs is None:
            tzs = [[3, 0, 1] for _ in range(nz)]
        if lcs is None:
            lcs = [1 for _ in range(n)]
        if type_map is None:
            type_map = [1 for _ in range(n)]
        elif not isinstance(type_map, list):
            type_map = [type_map for _ in range(n)]
        if inputs is None:
            inputs = ['input/matrix_item.json']
        if inputs_map is None:
            inputs_map = [0 for _ in range(n)]
        if volumes_names is None:
            volumes_names = ['Matrix']
        if volumes_map is None:
            volumes_map = [0 for _ in range(n)]
        if surfaces_names is None:
            surfaces_names = [['NX', 'X', 'NY', 'Y', 'NZ', 'Z']]
        if surfaces_map is None:
            surfaces_map = [0 for _ in range(n)]
        if recs_map is None:
            recs_map = [1 for _ in range(n)]
        if trans_map is None:
            trans_map = [1 for _ in range(n)]
        # x0, y0, z0 - item start X, Y, Z
        # x1, y1, z1 - item end X, Y, Z
        # xc, yc, zc - item center X, Y, Z
        primitives = list()
        if coordinates_type == 'direct':
            for k in range(nz):
                for j in range(ny):
                    for i in range(nx):
                        gi = i + nx * j + ny * nx * k
                        # print('{}/{}'.format(gi + 1, n))
                        x0 = xs[i] + transform_data[0]
                        x1 = xs[i + 1] + transform_data[0]
                        xc = 0.5 * (x0 + x1)
                        y0 = ys[j] + transform_data[1]
                        y1 = ys[j + 1] + transform_data[1]
                        yc = 0.5 * (y0 + y1)
                        z0 = zs[k] + transform_data[2]
                        z1 = zs[k + 1] + transform_data[2]
                        zc = 0.5 * (z0 + z1)
                        lc = lcs[gi]
                        t = type_map[gi]
                        pn = volumes_names[volumes_map[gi]]
                        sns = surfaces_names[surfaces_map[gi]]
                        inp = inputs[inputs_map[gi]]
                        tx = txs[i]
                        ty = tys[j]
                        tz = tzs[k]
                        trans = trans_map[gi]
                        rec = recs_map[gi]
                        kwargs = locals()
                        type_factory[t](factory_object, primitives, kwargs)
        elif coordinates_type == 'delta':
            primitives = list()
            for k in range(nz):
                for j in range(ny):
                    for i in range(nx):
                        gi = i + nx * j + ny * nx * k
                        # print('{}/{}'.format(gi + 1, n))
                        x0 = sum(xs[:i]) + transform_data[0]
                        x1 = sum(xs[:i + 1]) + transform_data[0]
                        xc = 0.5 * (x0 + x1)
                        y0 = sum(ys[:j]) + transform_data[1]
                        y1 = sum(ys[:j + 1]) + transform_data[1]
                        yc = 0.5 * (y0 + y1)
                        z0 = sum(zs[:k]) + transform_data[2]
                        z1 = sum(zs[:k + 1]) + transform_data[2]
                        zc = 0.5 * (z0 + z1)
                        lc = lcs[gi]
                        t = type_map[gi]
                        pn = volumes_names[volumes_map[gi]]
                        sns = surfaces_names[surfaces_map[gi]]
                        inp = inputs[inputs_map[gi]]
                        tx = txs[i]
                        ty = tys[j]
                        tz = tzs[k]
                        trans = trans_map[gi]
                        rec = recs_map[gi]
                        kwargs = locals()
                        type_factory[t](factory_object, primitives, kwargs)
        else:
            raise ValueError('coordinates_type: {}'.format(coordinates_type))
        Complex.__init__(self, factory, primitives)


# Empty
def type_0(factory_object, primitives, kwargs):
    pass


# Primitive
def type_1(factory_object, primitives, kwargs):
    # Args
    x0 = kwargs['x0']
    x1 = kwargs['x1']
    y0 = kwargs['y0']
    y1 = kwargs['y1']
    z0 = kwargs['z0']
    z1 = kwargs['z1']
    lc = kwargs['lc']
    tx = kwargs['tx']
    ty = kwargs['ty']
    tz = kwargs['tz']
    pn = kwargs['pn']
    sns = kwargs['sns']
    trans = kwargs['trans']
    rec = kwargs['rec']
    factory_str = kwargs['factory']
    primitives.append(Primitive(
        factory_str,
        [
            [x1, y1, z0, lc],
            [x0, y1, z0, lc],
            [x0, y0, z0, lc],
            [x1, y0, z0, lc],
            [x1, y1, z1, lc],
            [x0, y1, z1, lc],
            [x0, y0, z1, lc],
            [x1, y0, z1, lc],
        ],
        [0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [[], [], [], [], [], [], [], [], [], [], [], []],
        [tx, ty, tz],
        0,
        physical_name=pn,
        surfaces_names=sns,
        rec=rec,
        trans=trans
    ))


def type_2(factory_object, primitives, kwargs):
    from complex_factory import ComplexFactory
    # Args
    x0 = kwargs['x0']
    x1 = kwargs['x1']
    y0 = kwargs['y0']
    yc = kwargs['yc']
    y1 = kwargs['y1']
    z0 = kwargs['z0']
    zc = kwargs['zc']
    z1 = kwargs['z1']
    lc = kwargs['lc']
    tx = kwargs['tx']
    ty = kwargs['ty']
    tz = kwargs['tz']
    pn = kwargs['pn']
    trans = kwargs['trans']
    rec = kwargs['rec']
    inputs = kwargs['inputs']
    factory = kwargs['factory']
    # Internal
    borehole_input_path = inputs[0]
    result = check_file(borehole_input_path)
    with open(result['path']) as f:
        borehole_input = json.load(f)
    # pprint(borehole_input)
    n_boreholes = 10
    x0_borehole = x0 + 1.850
    dx_borehole = 2.500
    dz_borehole = -1.700
    boreholes = list()
    borehole_input['arguments']['factory'] = factory
    for borehole_i, borehole in enumerate(
            range(n_boreholes)):
        new_transform = borehole_input['arguments'][
            'transform_data']
        new_transform[
            0] = x0_borehole + dx_borehole * borehole_i
        new_transform[1] = yc
        new_transform[2] = zc + dz_borehole
        borehole_input['arguments'][
            'transform_data'] = new_transform
        b = ComplexFactory.new(borehole_input)
        boreholes.append(b)
        primitives.extend(b.primitives)
    # !!! FACTORY SYNC and EVALUATE !!!
    factory_object.synchronize()
    for b in boreholes:
        b.evaluate_coordinates()
    factory_object.removeAllDuplicates()  # ERROR IF REMOVE
    factory_object.synchronize()  # ERROR IF REMOVE
    inner_volumes = list()
    for b in boreholes:
        inner_volumes.extend(b.get_volumes())
    # External
    primitives.append(Primitive(
        factory,
        [
            [x1, y1, z0, lc],
            [x0, y1, z0, lc],
            [x0, y0, z0, lc],
            [x1, y0, z0, lc],
            [x1, y1, z1, lc],
            [x0, y1, z1, lc],
            [x0, y0, z1, lc],
            [x1, y0, z1, lc],
        ],
        [0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [[], [], [], [], [], [], [], [], [], [], [], []],
        [tx, ty, tz],
        0,
        pn,
        inner_volumes,
        rec=rec,
        trans=trans
    ))


def type_3(factory_object, primitives, kwargs):
    from complex_factory import ComplexFactory
    # Args
    xc = kwargs['xc']
    yc = kwargs['yc']
    z0 = kwargs['z0']
    inp = kwargs['inp']
    # Do
    factory = kwargs['factory']
    result = check_file(inp)
    with open(result['path']) as f:
        input_data = json.load(f)
    input_data['arguments']['factory'] = factory
    old_transform = input_data['arguments'].get('transform_data', [0, 0, 0])
    new_transform = old_transform
    new_transform[0] = old_transform[0] + xc
    new_transform[1] = old_transform[1] + yc
    new_transform[2] = old_transform[2] + z0
    print(new_transform)
    input_data['arguments']['transform_data'] = new_transform
    c = ComplexFactory.new(input_data)
    primitives.extend(c.primitives)


def type_4(factory_object, primitives, kwargs):
    from complex_factory import ComplexFactory
    # Args
    x0 = kwargs['x0']
    yc = kwargs['yc']
    z0 = kwargs['z0']
    inp = kwargs['inp']
    # Do
    factory = kwargs['factory']
    result = check_file(inp)
    with open(result['path']) as f:
        input_data = json.load(f)
    input_data['arguments']['factory'] = factory
    old_transform = input_data['arguments'].get('transform_data', [0, 0, 0])
    new_transform = old_transform
    new_transform[0] = old_transform[0] + x0
    new_transform[1] = old_transform[1] + yc
    new_transform[2] = old_transform[2] + z0
    input_data['arguments']['transform_data'] = new_transform
    c = ComplexFactory.new(input_data)
    primitives.extend(c.primitives)


type_factory = {
    0: type_0,  # Empty
    1: type_1,  # Primitive
    2: type_2,  # Borehole
    3: type_3,  # Complex at (xc, yc, z0)
    4: type_4   # Complex at (x0, yc, z0)
}
