from itertools import product

import numpy as np

from matrix import Matrix
from coordinate_system import LayerXY
from coordinate_system import str2obj as cs_str2obj
from transform import str2obj as tr_str2obj
from support import flatten


class Layer(Matrix):
    def __init__(self, layers=None, layers_curves=None, layers_types=None,
                 do_register_map=None, transforms=None, boolean_level_map=None):
        str_layers = [x for x in layers if isinstance(x, str)]
        other_layers = [x for x in layers if not isinstance(x, (int, float, str, list))]
        coordinate_system = str_layers[0] if len(str_layers) > 0 else 'cartesian'
        coordinate_system = cs_str2obj[coordinate_system]()
        for layer in other_layers:
            if isinstance(layer, tuple(cs_str2obj.values())):
                coordinate_system = layer
                break
        layers = [x for x in layers if isinstance(x, list)]
        if layers_types is None:
            layers_types = [['in' for _ in x] for x in layers]
        if layers_curves is None:
            layers_curves = [['line' for y in x] for x in layers]
        layers = Layer.correct_layers(layers)
        layers_curves = Layer.correct_layers(layers_curves)
        layers_types = Layer.correct_layers(layers_types)
        lxy = LayerXY(layers=layers[:-2],
                      layers_curves=layers_curves[:-2],
                      layers_types=layers_types[:-2])
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
        mlis = product(*(range(n_blocks_z), range(n_blocks_y), range(n_blocks_x)))
        n_x, n_y, n_nx, n_ny, n_z, n_nz = ns
        n_zs = n_z + n_nz
        n_lx = n_x * n_zs
        n_ly = n_y * n_zs
        n_lnx = n_nx * n_zs
        n_lny = n_ny * n_zs
        m2l_b2b_g2l, m2l_b2b_g2g = [], []
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
        # Boolean
        boolean_level_map = Layer.correct_map(boolean_level_map)
        boolean_level_map = Layer.parse_map(
            boolean_level_map, None, m2l_b2b_g2g, (int,))
        # print(np.array(boolean_level_map).reshape((n_blocks_z, n_blocks_y, n_blocks_x)))
        # Register
        default_do_register_map = [0 if x is None else 1 for x in m2l_b2b_g2l]
        do_register_map = Layer.correct_map(do_register_map)
        do_register_map = Layer.parse_map(
            do_register_map, 1, m2l_b2b_g2g, (bool, int))
        matrix_do_register_map = [x * y for x, y in zip(
            default_do_register_map, do_register_map)]
        structure_type, structure_type_map = Layer.parse_layers_structure_type(
            m2l_b2b_g2l)
        curves, curves_map = Layer.parse_layers_curves(
            layers_curves, m2l_b2b_g2l, layers)
        # print(np.array(structure_type_map).reshape((n_blocks_z, n_blocks_y, n_blocks_x)))
        # Transforms
        transforms = [] if transforms is None else transforms
        lxy2car = tr_str2obj['LayerXYToCartesian']()
        any1some = tr_str2obj['AnyAsSome'](cs_to=coordinate_system)
        some2car = tr_str2obj[f'{type(coordinate_system).__name__}ToCartesian'](
            cs_from=coordinate_system)
        matrix_transforms = [lxy2car, any1some, some2car] + transforms
        super().__init__(points=points,
                         curves=curves,
                         curves_map=curves_map,
                         transforms=matrix_transforms,
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
        if m is None:
            return None
        # Correct layers
        if len(m) == 1:  # X -> X=X, Y=X, NX=X, NY=X
            m = [m for _ in range(4)]
        elif len(m) == 2:  # X, Y -> X, Y, NX=X, NY=Y
            m = m + m
        elif len(m) == 4:  # X, Y, NX, X - OK!
            pass
        else:
            raise ValueError(m)
        # Correct in layers
        for i, l in enumerate(m):
            if len(l) == 1:  # Z -> Z, NZ=[[]]
                m[i] = l + [[[]]]
            elif len(l) == 2:  # Z, NZ - OK!
                pass
            else:
                raise ValueError(m, l)
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
    def parse_layers_curves(layers_curves_names, m2l_b2b_g2l, layers):
        """Parse layers curves

        Args:
            layers_curves_names (list of list): curves of layers
            m2l_b2b_g2l (list): global index of a block of the matrix to
                local index of a block of the layer
            layers (list of list): TODO coordinates of parced layers

        Returns:
            tuple: curves (list) curves map of the matrix (list)
        """
        curves, curves_map = [], []
        for li in m2l_b2b_g2l:  # local index (0-3, 0-1, zi, ci) of the layer
            if li is None:
                s = None
            else:
                if li[1] == 0:  # Z
                    zs = [0] + layers[4]
                elif li[1] == 1:  # NZ
                    zs = layers[5][::-1] + [0]
                else:
                    raise ValueError(li)
                zi, ci = li[-2] + 1, li[-1]
                pzi, pci = zi - 1 if zi != 0 else zi, ci - 1 if ci != 0 else ci
                z, pz = zs[zi], zs[pzi]
                if isinstance(z, str):
                    z = float(z.split(';')[0].split(':')[0])
                if isinstance(pz, str):
                    pz = float(pz.split(';')[0].split(':')[0])
                if li[0] == 0:  # X
                    ct = layers_curves_names[0][ci]
                    pct = layers_curves_names[0][pci]
                    cs = [['line'], ['line'], ['line'], ['line'],
                          [ct, [[0, 0, pz]]] if ct != 'line' else ['line'],
                          [pct, [[0, 0, pz]]] if pct != 'line' else ['line'],
                          [pct, [[0, 0, z]]] if pct != 'line' else ['line'],
                          [ct, [[0, 0, z]]] if ct != 'line' else ['line'],
                          ['line'], ['line'], ['line'], ['line']]
                elif li[0] == 1:  # Y
                    ct = layers_curves_names[1][ci]
                    pct = layers_curves_names[1][pci]
                    cs = [[ct, [[0, 0, pz]]] if ct != 'line' else ['line'],
                          [ct, [[0, 0, z]]] if ct != 'line' else ['line'],
                          [pct, [[0, 0, z]]] if pct != 'line' else ['line'],
                          [pct, [[0, 0, pz]]] if pct != 'line' else ['line'],
                          ['line'], ['line'], ['line'], ['line'],
                          ['line'], ['line'], ['line'], ['line']]
                elif li[0] == 2:  # NX
                    ct = layers_curves_names[2][ci]
                    pct = layers_curves_names[2][pci]
                    cs = [['line'], ['line'], ['line'], ['line'],
                          [pct, [[0, 0, pz]]] if pct != 'line' else ['line'],
                          [ct, [[0, 0, pz]]] if ct != 'line' else ['line'],
                          [ct, [[0, 0, z]]] if ct != 'line' else ['line'],
                          [pct, [[0, 0, z]]] if pct != 'line' else ['line'],
                          ['line'], ['line'], ['line'], ['line']]
                elif li[0] == 3:  # NY
                    ct = layers_curves_names[3][ci]
                    pct = layers_curves_names[3][pci]
                    cs = [[pct, [[0, 0, pz]]] if pct != 'line' else ['line'],
                          [pct, [[0, 0, z]]] if pct != 'line' else ['line'],
                          [ct, [[0, 0, z]]] if ct != 'line' else ['line'],
                          [ct, [[0, 0, pz]]] if ct != 'line' else ['line'],
                          ['line'], ['line'], ['line'], ['line'],
                          ['line'], ['line'], ['line'], ['line']]
                else:
                    raise ValueError(li)
                curves.append(cs)
                s = len(curves) - 1
            curves_map.append(s)
        return curves, curves_map

    @staticmethod
    def parse_layers_structure_type(m2l_b2b_g2l):
        structure_type_map = []
        for li in m2l_b2b_g2l:
            if li is None:
                s = None
            elif li[0] == 0:  # X
                s = 0
            elif li[0] == 1:  # Y
                s = 0
            elif li[0] == 2:  # NX
                s = 1
            elif li[0] == 3:  # NY
                s = 2
            else:
                raise ValueError(li)
            structure_type_map.append(s)
        structure_type = ['LLL', 'LRR', 'RLR', 'RRL']
        return structure_type, structure_type_map


str2obj = {
    Layer.__name__: Layer
}
