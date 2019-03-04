import json
from pprint import pprint

import gmsh

from complex import Complex
from primitive import Primitive
from support import check_file


class Matrix(Complex):
    def __init__(self, factory, xs, ys, zs, lcs, type_map,
                 physical_map, physical_names, txs, tys, tzs, inputs,
                 transform_data=None, surfaces_map=None, surfaces_names=None):
        """
            NZ
          LAYER1
            NY
        NX      X
            Y
          LAYER2
            NY
        NX      X
            Y
          LAYER3
            NY
        NX      X
            Y
            Z
        :param factory:
        :param xs:
        :param ys:
        :param zs:
        :param lcs:
        :param type_map:
        :param physical_map:
        :param physical_names:
        :param txs:
        :param tys:
        :param tzs:
        :param inputs:
        """
        if factory == 'occ':
            factory_object = gmsh.model.occ
        else:
            factory_object = gmsh.model.geo
        nx = len(xs) - 1
        ny = len(ys) - 1
        nz = len(zs) - 1
        n = nx * ny * nz
        if lcs is None:
            lcs = list()
            for z in range(nz):
                for y in range(ny):
                    for x in range(nx):
                        lcs.append(1)
        if type_map is None:
            for z in range(nz):
                for y in range(ny):
                    for x in range(nx):
                        type_map.append(1)
        if physical_map is None:
            physical_map = list()
            for z in range(nz):
                for y in range(ny):
                    for x in range(nx):
                        physical_map.append(0)
        if surfaces_map is None:
            surfaces_map = list()
            for z in range(nz):
                for y in range(ny):
                    for x in range(nx):
                        surfaces_map.append(0)
        if physical_names is None:
            physical_names = ['Matrix']
        if transform_data is None:
            transform_data = [0, 0, 0]
        if surfaces_names is None:
            surfaces_names = [['NX', 'X', 'NY', 'Y', 'NZ', 'Z']]
        primitives = list()
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
                    pn = physical_names[physical_map[gi]]
                    sns = surfaces_names[surfaces_map[gi]]
                    tx = txs[i]
                    ty = tys[j]
                    tz = tzs[k]
                    kwargs = locals()
                    type_factory[t](factory_object, primitives, kwargs)
        Complex.__init__(self, factory, primitives)


def type_0(factory_object, primitives, kwargs):
    pass


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
        surfaces_names=sns
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
        inner_volumes
    ))


def type_3(factory_object, primitives, kwargs):
    from complex_factory import ComplexFactory
    # Args
    x0 = kwargs['x0']
    x1 = kwargs['x1']
    xc = kwargs['xc']
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
    # Do
    inputs = kwargs['inputs']
    factory = kwargs['factory']
    input_path = inputs[0]
    result = check_file(input_path)
    with open(result['path']) as f:
        input_data = json.load(f)
    input_data['arguments']['factory'] = factory
    new_transform = input_data['arguments']['transform_data']
    new_transform[0] = xc
    new_transform[1] = yc
    new_transform[2] = z0
    input_data['arguments']['transform_data'] = new_transform
    c = ComplexFactory.new(input_data)
    primitives.extend(c.primitives)


type_factory = {
    0: type_0,
    1: type_1,
    2: type_2,
    3: type_3
}
