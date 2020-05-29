from matrix import Matrix


class Cylinder(Matrix):
    surfaces_names_map = {
        ('C', 4): [0, 0, 0, 0, 2, 3],  # Int, Ext, Bottom, Top
        ('NX', 4): [1, 0, 0, 0, 2, 3],  # Int, Ext, Bottom, Top
        ('X', 4): [0, 1, 0, 0, 2, 3],  # Int, Ext, Bottom, Top
        ('NY', 4): [0, 0, 1, 0, 2, 3],  # Int, Ext, Bottom, Top
        ('Y', 4): [0, 0, 0, 1, 2, 3],  # Int, Ext, Bottom, Top
        ('C', 5): [4, 4, 4, 4, 2, 3],  # Int, Ext, Bottom, Top, In
        ('NX', 5): [1, 0, 4, 4, 2, 3],  # Int, Ext, Bottom, Top, In
        ('X', 5): [0, 1, 4, 4, 2, 3],  # Int, Ext, Bottom, Top, In
        ('NY', 5): [4, 4, 1, 0, 2, 3],  # Int, Ext, Bottom, Top, In
        ('Y', 5): [4, 4, 0, 1, 2, 3],  # Int, Ext, Bottom, Top, In
        ('C', 6): [0, 1, 2, 3, 4, 5],  # NX X NY Y NZ Z
        ('NX', 6): [0, 1, 2, 3, 4, 5],  # NX X NY Y NZ Z
        ('X', 6): [0, 1, 2, 3, 4, 5],  # NX X NY Y NZ Z
        ('NY', 6): [0, 1, 2, 3, 4, 5],  # NX X NY Y NZ Z
        ('Y', 6): [0, 1, 2, 3, 4, 5],  # NX X NY Y NZ Z
        ('C', 10): [0, 0, 0, 0, 8, 9],  # INX IX INY IY ENX EX ENY EY B T
        ('NX', 10): [4, 0, 0, 0, 8, 9],  # INX IX INY IY ENX EX ENY EY B T
        ('X', 10): [1, 5, 0, 0, 8, 9],  # INX IX INY IY ENX EX ENY EY B T
        ('NY', 10): [0, 0, 6, 2, 8, 9],  # INX IX INY IY ENX EX ENY EY B T
        ('Y', 10): [0, 0, 3, 7, 8, 9],  # INX IX INY IY ENX EX ENY EY B T
        ('C', 19): [18, 18, 18, 18, 8, 9],  # INX IX INY IY ENX EX ENY EY BC TC BNX TNX BX TX BNY TNY BY TY, I
        ('NX', 19): [4, 0, 18, 18, 10, 11],  # INX IX INY IY ENX EX ENY EY BC TC BNX TNX BX TX BNY TNY BY TY, I
        ('X', 19): [1, 5, 18, 18, 12, 13],  # INX IX INY IY ENX EX ENY EY BC TC BNX TNX BX TX BNY TNY BY TY, I
        ('NY', 19): [18, 18, 6, 2, 14, 15],  # INX IX INY IY ENX EX ENY EY BC TC BNX TNX BX TX BNY TNY BY TY, I
        ('Y', 19): [18, 18, 3, 7, 16, 17],  # INX IX INY IY ENX EX ENY EY BC TC BNX TNX BX TX BNY TNY BY TY, I
    }

    def __init__(self, factory, radii_x, radii_y, heights,
                 layers_lcs, transform_data,
                 transfinite_r_data, transfinite_h_data, transfinite_phi_data,
                 volumes_names=None, layers_volumes_names=None,
                 surfaces_names=None, layers_surfaces_names=None,
                 in_surfaces_names=None, layers_in_surfaces_names=None,
                 in_surfaces_masks=None, layers_in_surfaces_masks=None,
                 layers_recs=None, layers_trans=None, layers_exists=None,
                 k=None, kxs=None, kys=None,
                 ct=None, ct0s=None, ct1s=None):
        """
        Multilayer cylinder
        Used for axisymmetric objects
        Layers structure:
        h - height
        c - radius
        hM_r1 hM_r2 ... hM_rN
        ...   ...   ... ...
        h2_r1 h2_r2 ... h2_rN
        h1_r1 h1_r2 ... h1_rN
        Bottom center of h1_r1 layer is an origin of the cylinder
        :param str factory: see Primitive
        :param list of float radii_x: layers outer radii by X [r1, r2, ..., rN]
        :param list of float radii_y: layers outer radii by Y [r1, r2, ..., rN]
        :param list of float heights: layers heights [h1, h2, ..., hM]
        :param list of list of float layers_lcs: characteristic lengths
        of layers
        [[h1_r1, h1_r2, ..., h1_rN], [h2_r1, h2_r2, ..., h2_rN], ...,
        [hM_r1, hM_r2, ..., hM_rN]]
        :param list of float transform_data: relative to cylinder bottom
        (see Primitive)
        :param list of list of str layers_volumes_names: physical names
        of layers
        [[h1_r1, h1_r2, ..., h1_rN], [h2_r1, h2_r2, ..., h2_rN], ...,
        [hM_r1, hM_r2, ..., hM_rN]]
        :param list of list of float transfinite_r_data: see Primitive
        [[number of r1 nodes, type, coefficient], [number of r2 nodes, type,
        coefficient], ...]
        :param list of list of float transfinite_h_data: see Primitive
        [[number of h1 nodes, type, coefficient], [number of h2 nodes, type,
        coefficient], ...]
        :param list of float transfinite_phi_data: see Primitive
        [number of circumferential nodes, type, coefficient]
        :param list of list of int layers_surfaces_names: Like as layers_physical_names for surfaces
        :param list of list of str surfaces_names:  Names for use in layers_surfaces_names
        :param list of str volumes_names: Names for use in layers_physical_names
        :param list if list of int layers_recs: Recombine primitives? 1 - yes, 0 - no
        :param list if list of int layers_trans: Transfinite primitives? 1 - yes, 0 - no
        :param float k: quadrangle part of first layer radius
        :param list if list of int layers_exists: Create primitives?
        :param list of int kxs: extensions by x
        :param list of int kys: extensions by y
        :param int ct: curve type of cylinder curves
        :param list of int ct0s: curve or straight line for inner radius? 1 - yes, 0 - no
        :param list of int ct1s: curve or straight line for outer radius? 1 - yes, 0 - no
        :return None
        """
        nr = len(radii_x)
        if transform_data is None:
            transform_data = []
        if ct is None:
            ct = 3
        if ct0s is None:
            ct0s = [1 if i != 0 else 0 for i in range(nr)]
        if ct1s is None:
            ct1s = [1 for _ in range(nr)]
        if layers_lcs is None:
            layers_lcs = [[1 for _ in range(nr)] for _ in heights]
        elif not isinstance(layers_lcs, list):
            layers_lcs = [[layers_lcs for _ in range(nr)] for _ in heights]
        if layers_recs is None:
            layers_recs = [[1 for _ in range(nr)] for _ in heights]
        elif not isinstance(layers_recs, list):
            layers_recs = [[layers_recs for _ in range(nr)] for _ in heights]
        if layers_trans is None:
            layers_trans = [[1 for _ in range(nr)] for _ in heights]
        elif not isinstance(layers_trans, list):
            layers_trans = [[layers_trans for _ in range(nr)] for _ in heights]
        if layers_exists is None:
            layers_exists = [[1 for _ in range(nr)] for _ in heights]
        elif not isinstance(layers_exists, list):
            layers_exists = [[layers_exists for _ in range(nr)] for _ in heights]
        if in_surfaces_masks is None:
            in_surfaces_masks = [[0, 0, 0, 0, 0, 0]]
        if layers_in_surfaces_masks is None:
            layers_in_surfaces_masks = [[0 for _ in range(nr)] for _ in heights]
        elif not isinstance(layers_in_surfaces_masks, list):
            layers_in_surfaces_masks = [[layers_in_surfaces_masks for _ in range(nr)] for _ in heights]
        if k is None:
            k = 0.5
        if volumes_names is None:
            volumes_names = ['V']
        if layers_volumes_names is None:
            layers_volumes_names = [[0 for _ in range(nr)] for _ in heights]
        if surfaces_names is None:
            surfaces_names = [['NX', 'X', 'NY', 'Y', 'NZ', 'Z']]
        if layers_surfaces_names is None:
            layers_surfaces_names = [[0 for _ in range(nr)] for _ in heights]
        if in_surfaces_names is None:
            in_surfaces_names = [['NXI', 'XI', 'NYI', 'YI', 'NZI', 'ZI']]
        if layers_in_surfaces_names is None:
            layers_in_surfaces_names = [[0 for _ in range(nr)] for _ in heights]
        xs, ys, zs, txs, tys, tzs = [], [], heights, [], [], transfinite_h_data
        for i in range(nr - 1, 0, -1):
            xs.append(radii_x[i] - radii_x[i - 1])
            ys.append(radii_y[i] - radii_y[i - 1])
            txs.append(transfinite_r_data[i])
            tys.append(transfinite_r_data[i])
        xs.append((1 - k) * radii_x[0])
        xs.append(2 * k * radii_x[0])
        xs.append((1 - k) * radii_x[0])
        ys.append((1 - k) * radii_y[0])
        ys.append(2 * k * radii_y[0])
        ys.append((1 - k) * radii_y[0])
        txs.append(transfinite_r_data[0])
        txs.append(transfinite_phi_data)
        txs.append(transfinite_r_data[0])
        tys.append(transfinite_r_data[0])
        tys.append(transfinite_phi_data)
        tys.append(transfinite_r_data[0])
        for i in range(1, nr):
            xs.append(radii_x[i] - radii_x[i - 1])
            ys.append(radii_y[i] - radii_y[i - 1])
            txs.append(transfinite_r_data[i])
            tys.append(transfinite_r_data[i])
        transform_data = [[-radii_x[-1], -radii_y[-1], 0]] + transform_data
        kws = [{"ct": ct, "ct0": 0, "ct1": 0},
               {"ct": ct, "ct0": 1, "ct1": 0},
               {"ct": ct, "ct0": 0, "ct1": 1},
               {"ct": ct, "ct0": 1, "ct1": 1}]
        ct_map = {(x['ct0'], x['ct1']): i for i, x in enumerate(kws)}
        type_map, lcs, recs_map, trans_map, kws_map = [], [], [], [], []
        volumes_map, surfaces_map = [], []
        new_surfaces_names = {}
        in_surfaces_map, in_surfaces_masks_map = [], []
        new_in_surfaces_names = {}
        new_in_surfaces_mask = {}
        ci, cj, ck = len(xs) // 2, len(ys) // 2, len(zs) // 2
        types = ['empty', 'axisymmetric_nx', 'axisymmetric_x',
                 'axisymmetric_ny', 'axisymmetric_y', 'axisymmetric_core']
        for k in range(len(zs)):
            for j in range(len(ys)):
                for i in range(len(xs)):
                    if i == ci and j == cj:  # C
                        type_map.append(5 if layers_exists[k][0] else 0)
                        lcs.append(layers_lcs[k][0])
                        recs_map.append(layers_recs[k][0])
                        trans_map.append(layers_trans[k][0])
                        volumes_map.append(layers_volumes_names[k][0])
                        kws_map.append(ct_map[(ct0s[0], ct1s[0])])
                        # surfaces
                        sns = surfaces_names[layers_surfaces_names[k][0]]
                        new_sns = [sns[x] for x in self.surfaces_names_map[
                            ('C', len(sns))]]
                        surfaces_map.append(new_surfaces_names.setdefault(
                            tuple(new_sns), len(new_surfaces_names)))
                        # in surfaces
                        in_sns = in_surfaces_names[layers_in_surfaces_names[k][0]]
                        new_in_sns = [in_sns[x] for x in self.surfaces_names_map[
                            ('C', len(in_sns))]]
                        in_surfaces_map.append(new_in_surfaces_names.setdefault(
                            tuple(new_in_sns), len(new_in_surfaces_names)))
                        # in surfaces masks
                        mask = in_surfaces_masks[layers_in_surfaces_masks[k][0]]
                        new_mask = [mask[x] for x in self.surfaces_names_map[
                            ('C', len(mask))]]
                        in_surfaces_masks_map.append(new_in_surfaces_mask.setdefault(
                            tuple(new_mask), len(new_in_surfaces_mask)))
                    elif i == ci:
                        li = abs(j - cj) - 1  # layer index
                        sns = surfaces_names[layers_surfaces_names[k][li]]
                        in_sns = in_surfaces_names[layers_in_surfaces_names[k][li]]
                        mask = in_surfaces_masks[layers_in_surfaces_masks[k][li]]
                        if j > cj:  # Y
                            type_map.append(4 if layers_exists[k][li] else 0)
                            new_sns = [sns[x] for x in self.surfaces_names_map[
                                ('Y', len(sns))]]
                            new_in_sns = [in_sns[x] for x in
                                          self.surfaces_names_map[
                                              ('Y', len(in_sns))]]
                            new_mask = [mask[x] for x in
                                        self.surfaces_names_map[
                                            ('Y', len(mask))]]
                        else:  # NY
                            type_map.append(3 if layers_exists[k][li] else 0)
                            new_sns = [sns[x] for x in self.surfaces_names_map[
                                ('NY', len(sns))]]
                            new_in_sns = [in_sns[x] for x in
                                          self.surfaces_names_map[
                                              ('NY', len(in_sns))]]
                            new_mask = [mask[x] for x in
                                        self.surfaces_names_map[
                                            ('NY', len(mask))]]
                        surfaces_map.append(new_surfaces_names.setdefault(
                            tuple(new_sns), len(new_surfaces_names)))
                        in_surfaces_map.append(new_in_surfaces_names.setdefault(
                            tuple(new_in_sns), len(new_in_surfaces_names)))
                        in_surfaces_masks_map.append(
                            new_in_surfaces_mask.setdefault(
                                tuple(new_mask), len(new_in_surfaces_mask)))
                        lcs.append(layers_lcs[k][li])
                        recs_map.append(layers_recs[k][li])
                        trans_map.append(layers_trans[k][li])
                        volumes_map.append(layers_volumes_names[k][li])
                        kws_map.append(ct_map[(ct0s[li], ct1s[li])])
                    elif j == cj:
                        li = abs(i - ci) - 1  # layer index
                        sns = surfaces_names[layers_surfaces_names[k][li]]
                        in_sns = in_surfaces_names[layers_in_surfaces_names[k][li]]
                        mask = in_surfaces_masks[layers_in_surfaces_masks[k][li]]
                        if i > ci:  # X
                            type_map.append(2 if layers_exists[k][li] else 0)
                            new_sns = [sns[x] for x in self.surfaces_names_map[
                                ('X', len(sns))]]
                            new_in_sns = [in_sns[x] for x in
                                          self.surfaces_names_map[
                                              ('X', len(in_sns))]]
                            new_mask = [mask[x] for x in
                                        self.surfaces_names_map[
                                            ('X', len(mask))]]
                        else:  # NX
                            type_map.append(1 if layers_exists[k][li] else 0)
                            new_sns = [sns[x] for x in self.surfaces_names_map[
                                ('NX', len(sns))]]
                            new_in_sns = [in_sns[x] for x in
                                          self.surfaces_names_map[
                                              ('NX', len(in_sns))]]
                            new_mask = [mask[x] for x in
                                        self.surfaces_names_map[
                                            ('NX', len(mask))]]
                        surfaces_map.append(new_surfaces_names.setdefault(
                            tuple(new_sns), len(new_surfaces_names)))
                        in_surfaces_map.append(new_in_surfaces_names.setdefault(
                            tuple(new_in_sns), len(new_in_surfaces_names)))
                        in_surfaces_masks_map.append(
                            new_in_surfaces_mask.setdefault(
                                tuple(new_mask), len(new_in_surfaces_mask)))
                        lcs.append(layers_lcs[k][li])
                        recs_map.append(layers_recs[k][li])
                        trans_map.append(layers_trans[k][li])
                        volumes_map.append(layers_volumes_names[k][li])
                        kws_map.append(ct_map[(ct0s[li], ct1s[li])])
                    else:
                        type_map.append(0)  # Empty
                        lcs.append(0)
                        recs_map.append(0)
                        trans_map.append(0)
                        volumes_map.append(0)
                        surfaces_map.append(0)
                        in_surfaces_map.append(0)
                        in_surfaces_masks_map.append(0)
                        kws_map.append(0)
        new_surfaces_names = [list(x) for x in new_surfaces_names]
        new_in_surfaces_names = [list(x) for x in new_in_surfaces_names]
        new_in_surfaces_mask = [list(x) for x in new_in_surfaces_mask]
        Matrix.__init__(self, factory, xs=xs, ys=ys, zs=zs,
                        coordinates_type='delta', lcs=lcs,
                        transform_data=transform_data,
                        txs=txs, tys=tys, tzs=tzs,
                        type_map=type_map,
                        types=types,
                        volumes_names=volumes_names,
                        volumes_map=volumes_map,
                        surfaces_names=new_surfaces_names,
                        surfaces_map=surfaces_map,
                        in_surfaces_names=new_in_surfaces_names,
                        in_surfaces_map=in_surfaces_map,
                        in_surfaces_masks=new_in_surfaces_mask,
                        in_surfaces_masks_map=in_surfaces_masks_map,
                        recs_map=recs_map, trans_map=trans_map,
                        kws=kws, kws_map=kws_map)
