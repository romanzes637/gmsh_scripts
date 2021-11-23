from itertools import product

import numpy as np

from matrix import Matrix
from coordinate_system import LayerXY
from support import flatten


class Layer(Matrix):
    def __init__(self, layers=None, layers_curves_names=None, layers_types=None,
                 do_register_map=None, transforms=None, boolean_level_map=None):
        layers = Layer.correct_layers(layers)
        layers_curves_names = Layer.correct_layers(layers_curves_names)
        layers_types = Layer.correct_layers(layers_types)
        lxy = LayerXY(layers=layers[:-2],
                      curves_names=layers_curves_names[:-2],
                      layers_types=layers_types[:-2])
        transforms = [] if transforms is None else transforms
        # To matrix points
        xs = layers[0]
        ys = layers[1]
        zs = layers[4]
        nxs = Layer.invert_layer(layers[2])
        nys = Layer.invert_layer(layers[3])
        nzs = Layer.invert_layer(layers[5])
        pxs = nxs + xs  # NX + X
        pys = nys + ys  # NY + Y
        pzs = nzs + [0] + zs  # NZ + 0 +  Z
        mean_mxi = len(nxs) - 1  # Center to X
        mean_myi = len(nys) - 1  # Center to Y
        mean_mzi = len(nzs)  # Center to Z
        ns = [len(x) for x in layers]
        points = [pxs, pys, pzs, lxy]
        nxs, nys, nzs = len(pxs), len(pys), len(pzs)
        n_blocks_x, n_blocks_y, n_blocks_z = nxs - 1, nys - 1, nzs - 1
        print(points)
        m2l_b2b_g2l, m2l_b2b_l2g = [], {}
        m2l_b2b_g2g = []
        print(layers)
        mlis = product(*(range(n_blocks_z), range(n_blocks_y), range(n_blocks_x)))
        print(mean_mxi, mean_myi, mean_mzi)
        n_x, n_y, n_nx, n_ny, n_z, n_nz = ns
        n_zs = n_z + n_nz
        n_lx = n_x * n_zs
        n_ly = n_y * n_zs
        n_lnx = n_nx * n_zs
        n_lny = n_ny * n_zs
        print(n_blocks_x, n_blocks_y, n_blocks_z)
        print(n_x, n_y, n_nx, n_ny, n_z, n_nz)
        for mgi, mli in enumerate(mlis):
            mzi, myi, mxi = mli
            if mzi >= mean_mzi:  # Z
                lzi = mzi - mean_mzi
                if mxi >= mean_mxi and myi == mean_myi:  # X
                    lci = mxi - mean_mxi
                    lli = (0, 0, lzi, lci)
                    lgi = n_x * lzi + lci
                elif myi >= mean_myi and mxi == mean_mxi:  # Y
                    lci = myi - mean_myi
                    lli = (1, 0, lzi, lci)
                    lgi = n_lx + n_y * lzi + lci
                elif mxi < mean_mxi and myi == mean_myi:  # NX
                    lci = mean_mxi - mxi
                    lli = (2, 0, lzi, lci)
                    lgi = n_lx + n_ly + n_nx * lzi + lci
                elif myi < mean_myi and mxi == mean_mxi:  # NY
                    lci = mean_myi - myi
                    lli = (3, 0, lzi, lci)
                    lgi = n_lx + n_ly + n_lnx + n_ny * lzi + lci
                else:
                    lli, lgi = None, None
            else:
                lzi = mzi
                if mxi >= mean_mxi and myi == mean_myi:  # NZ X
                    lci = mxi - mean_mxi
                    lli = (0, 1, lzi, lci)
                    lgi = n_x * n_z + n_x * lzi + lci
                elif myi >= mean_myi and mxi == mean_mxi:  # NZ Y
                    lci = myi - mean_myi
                    lli = (1, 1, lzi, lci)
                    lgi = n_lx + n_y * n_z + n_y * lzi + lci
                elif mxi < mean_mxi and myi == mean_myi:  # NZ NX
                    lci = mean_mxi - mxi
                    lli = (2, 1, lzi, lci)
                    lgi = n_lx + n_ly + n_nx * n_z + n_nx * lzi + lci
                elif myi < mean_myi and mxi == mean_mxi:  # NZ NY
                    lci = mean_myi - myi
                    lli = (3, 1, lzi, lci)
                    lgi = n_lx + n_ly + n_lnx + n_ny * n_z + n_ny * lzi + lci
                else:
                    lli, lgi = None, None
            m2l_b2b_g2l.append(lli)
            m2l_b2b_g2g.append(lgi)
        m2l_b2b_l2g = {x: i for i, x in enumerate(m2l_b2b_g2l) if x is not None}
        default_do_register_map = [0 if x is None else 1 for x in m2l_b2b_g2l]
        boolean_level_map = Layer.correct_map(boolean_level_map)
        boolean_level_map = Layer.parse_map(boolean_level_map, -1, m2l_b2b_g2g,
                                            item_types=(int,))
        # print(np.array(boolean_level_map).reshape((n_blocks_z, n_blocks_y, n_blocks_x)))
        do_register_map = Layer.correct_map(do_register_map)
        do_register_map = Layer.parse_map(do_register_map, 1, m2l_b2b_g2g,
                                          item_types=(bool, int))
        matrix_do_register_map = [x * y for x, y in zip(default_do_register_map,
                                                        do_register_map)]
        structure_type_map = []
        structure_type = ['LLL', 'LRR', 'RLR', 'RRL']
        for li in m2l_b2b_g2l:
            if li is None:
                s = None
            elif li[0] == 0:  # X
                s = 0
            elif li[0] == 1:  # Y
                s = 0
            elif li[0] == 2:  # NX
                s = 1
            elif li[0] == 3:  # # NY
                s = 2
            else:
                raise ValueError(li)
            structure_type_map.append(s)
        # print(np.array(structure_type_map).reshape((n_blocks_z, n_blocks_y, n_blocks_x)))
        curves, curves_map = Layer.parse_layers_curves(layers_curves_names,
                                                       m2l_b2b_g2l, layers)
        print(np.array(curves_map).reshape((n_blocks_z, n_blocks_y, n_blocks_x)))
        # print(curves)
        super().__init__(points=points,
                         curves=curves,
                         curves_map=curves_map,
                         transforms=[LayerXY.__name__] + transforms,
                         do_register_map=matrix_do_register_map,
                         structure_type=structure_type,
                         structure_type_map=structure_type_map,
                         boolean_level_map=boolean_level_map)

    @staticmethod
    def correct_layers(layers):
        if len(layers) == 2:  # X and Z -> X = Y = NX = NY, Z, NZ == []
            return [layers[0] for _ in range(4)] + [layers[1]] + [[]]
        else:
            raise ValueError(layers)

    @staticmethod
    def invert_layer(layer):
        values = [float(x.split(';')[0].split(':')[0]) if isinstance(x, str) else x for x in layer]
        props = [';'.join(':'.join('' if i == 0 and j == 0 else z for j, z in enumerate(y.split(':'))) for i, y in
                          enumerate(x.split(';'))) if isinstance(x, str) else None for x in layer]
        new_layer = [f'-{x}{props[i + 1]}' if i + 1 < len(props) and props[i + 1] is not None else -x for i, x in
                     enumerate(values)][::-1]
        return new_layer

    @staticmethod
    def correct_map(m):
        # Correct layers
        if len(m) == 1:  # X -> X=X, Y=X, NX=X, NY=X
            m = [m for _ in range(4)]
        elif len(m) == 2:  # X, Y -> X, Y, NX=X, NY=Y
            m = m + m
        elif len(m) == 4:  # X, Y, NX, X - OK!
            pass
        else:
            raise ValueError(m)
        print(m)
        # Correct in layers
        for i, l in enumerate(m):
            if len(l) == 1:  # Z -> Z, NZ=[[]]
                m[i] = l + [[[]]]
            elif len(l) == 2:  # Z, NZ - OK!
                pass
            else:
                raise ValueError(m, l)
        print(m)
        print(list(flatten(m)))
        return m

    @staticmethod
    def parse_map(m, default, new2old, item_types=()):
        # Default value for all items if map is None
        if m is None:
            m = [default for _ in new2old]
            return m
        m = list(flatten(m))
        # Check on single item of type in item_types
        for t in item_types:
            if isinstance(t, list) and isinstance(m, list):  # list of ...
                if all(isinstance(ti, mi) for ti in t for mi in m):
                    m = [m for _ in new2old]
                    return m
            elif isinstance(m, t):  # non list types
                m = [m for _ in new2old]
                return m
        # Old list to new list
        if isinstance(m, list):
            m = [m[x] if x is not None else default for x in new2old]
            return m
        else:  # Something wrong
            raise ValueError(m)

    @staticmethod
    def parse_layers_curves(layers_curves_names, n2o_b2b_g2l, layers):
        curves, curves_map = [], []
        zs = [0] + layers[4]
        curves = [
            [['line'], ['line'], ['line'], ['line'],
             ['line'], ['line'], ['line'], ['line'],
             ['line'], ['line'], ['line'], ['line']]]
        for li in n2o_b2b_g2l:
            if li is None:
                s = None
            elif li[0] == 0:  # X
                zi, xi = li[-2] + 1, li[-1]
                pxi = xi - 1 if xi != 0 else xi
                pzi = zi - 1 if zi != 0 else zi
                ct = layers_curves_names[0][xi]
                pct = layers_curves_names[0][pxi]
                z, pz = zs[zi], zs[pzi]
                if isinstance(z, str):
                    z = float(z.split(';')[0].split(':')[0])
                if isinstance(pz, str):
                    pz = float(pz.split(';')[0].split(':')[0])
                if ct == 'line' and pct == 'line':
                    s = 0
                else:
                    c = [['line'], ['line'], ['line'], ['line'],
                         [ct, [[0, 0, pz]]],
                         [pct, [[0, 0, pz]]],
                         [pct, [[0, 0, z]]],
                         [ct, [[0, 0, z]]],
                         ['line'], ['line'], ['line'], ['line']]
                    curves.append(c)
                    s = len(curves) - 1
            elif li[0] == 1:  # Y
                zi, yi = li[-2] + 1, li[-1]
                pyi = yi - 1 if yi != 0 else pyi
                pzi = zi - 1 if zi != 0 else zi
                ct = layers_curves_names[0][yi]
                pct = layers_curves_names[0][pyi]
                z, pz = zs[zi], zs[pzi]
                if isinstance(z, str):
                    z = float(z.split(';')[0].split(':')[0])
                if isinstance(pz, str):
                    pz = float(pz.split(';')[0].split(':')[0])
                if ct == 'line' and pct == 'line':
                    s = 0
                else:
                    c = [[ct, [[0, 0, pz]]],
                         [ct, [[0, 0, z]]],
                         [pct, [[0, 0, z]]],
                         [pct, [[0, 0, pz]]],
                         ['line'], ['line'], ['line'], ['line'],
                         ['line'], ['line'], ['line'], ['line']]
                    curves.append(c)
                    s = len(curves) - 1
            elif li[0] == 2:  # NX
                zi, nxi = li[-2] + 1, li[-1]
                pnxi = nxi - 1 if nxi != 0 else nxi
                pzi = zi - 1 if zi != 0 else zi
                ct = layers_curves_names[0][nxi]
                pct = layers_curves_names[0][pnxi]
                z, pz = zs[zi], zs[pzi]
                if isinstance(z, str):
                    z = float(z.split(';')[0].split(':')[0])
                if isinstance(pz, str):
                    pz = float(pz.split(';')[0].split(':')[0])
                if ct == 'line' and pct == 'line':
                    s = 0
                else:
                    c = [['line'], ['line'], ['line'], ['line'],
                         [pct, [[0, 0, pz]]],
                         [ct, [[0, 0, pz]]],
                         [ct, [[0, 0, z]]],
                         [pct, [[0, 0, z]]],
                         ['line'], ['line'], ['line'], ['line']]
                    curves.append(c)
                    s = len(curves) - 1
            elif li[0] == 3:  # # NY
                zi, nyi = li[-2] + 1, li[-1]
                pnyi = nyi - 1 if nyi != 0 else nyi
                pzi = zi - 1 if zi != 0 else zi
                ct = layers_curves_names[0][nyi]
                pct = layers_curves_names[0][pnyi]
                z, pz = zs[zi], zs[pzi]
                if isinstance(z, str):
                    z = float(z.split(';')[0].split(':')[0])
                if isinstance(pz, str):
                    pz = float(pz.split(';')[0].split(':')[0])
                if ct == 'line' and pct == 'line':
                    s = 0
                else:
                    c = [[pct, [[0, 0, pz]]],
                         [pct, [[0, 0, z]]],
                         [ct, [[0, 0, z]]],
                         [ct, [[0, 0, pz]]],
                         ['line'], ['line'], ['line'], ['line'],
                         ['line'], ['line'], ['line'], ['line']]
                    curves.append(c)
                    s = len(curves) - 1
            else:
                raise ValueError(li)
            curves_map.append(s)
        return curves, curves_map


str2obj = {
    Layer.__name__: Layer,
    Layer.__name__.lower(): Layer
}
