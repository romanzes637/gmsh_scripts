from matrix import Matrix


class Cylinder(Matrix):
    surfaces_names_map = {
        ('C', 4): [0, 0, 0, 0, 2, 3],
        ('NX', 4): [1, 0, 0, 0, 2, 3],
        ('X', 4): [0, 1, 0, 0, 2, 3],
        ('NY', 4): [0, 0, 1, 0, 2, 3],
        ('Y', 4): [0, 0, 0, 1, 2, 3],
        ('C', 6): [0, 1, 2, 3, 4, 5],
        ('NX', 6): [0, 1, 2, 3, 4, 5],
        ('X', 6): [0, 1, 2, 3, 4, 5],
        ('NY', 6): [0, 1, 2, 3, 4, 5],
        ('Y', 6): [0, 1, 2, 3, 4, 5],
        ('C', 10): [0, 0, 0, 0, 8, 9],
        ('NX', 10): [4, 0, 0, 0, 8, 9],
        ('X', 10): [1, 5, 0, 0, 8, 9],
        ('NY', 10): [0, 0, 6, 2, 8, 9],
        ('Y', 10): [0, 0, 3, 7, 8, 9],
    }

    def __init__(self, factory, radii, heights, layers_lcs, transform_data,
                 transfinite_r_data, transfinite_h_data, transfinite_phi_data,
                 volumes_names=None, layers_volumes_names=None,
                 surfaces_names=None, layers_surfaces_names=None,
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
        :param list of float radii: layers outer radii [r1, r2, ..., rN]
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
        if ct is None:
            ct = 3
        if ct0s is None:
            ct0s = [1 if i != 0 else 0 for i in range(len(radii))]
        if ct1s is None:
            ct1s = [1 for _ in radii]
        if layers_lcs is None:
            layers_lcs = [[1 for _ in radii] for _ in heights]
        elif not isinstance(layers_lcs, list):
            layers_lcs = [[layers_lcs for _ in radii] for _ in heights]
        if layers_recs is None:
            layers_recs = [[1 for _ in radii] for _ in heights]
        elif not isinstance(layers_recs, list):
            layers_recs = [[layers_recs for _ in radii] for _ in heights]
        if layers_trans is None:
            layers_trans = [[1 for _ in radii] for _ in heights]
        elif not isinstance(layers_trans, list):
            layers_trans = [[layers_trans for _ in radii] for _ in heights]
        if layers_exists is None:
            layers_exists = [[1 for _ in radii] for _ in heights]
        elif not isinstance(layers_exists, list):
            layers_exists = [[layers_exists for _ in radii] for _ in heights]
        if k is None:
            k = 0.5
        if kxs is None:
            kxs = [1 for _ in radii]
        if kys is None:
            kys = [1 for _ in radii]
        if volumes_names is None:
            volumes_names = ['V']
        if layers_volumes_names is None:
            layers_volumes_names = [[0 for _ in radii] for _ in heights]
        if surfaces_names is None:
            surfaces_names = [['NX', 'X', 'NY', 'Y', 'NZ', 'Z']]
        if layers_surfaces_names is None:
            layers_surfaces_names = [[0 for _ in radii] for _ in heights]
        xs, ys, zs, txs, tys, tzs = [], [], heights, [], [], transfinite_h_data
        radii_x = [radii[i] * kxs[i] for i in range(len(radii))]
        radii_y = [radii[i] * kys[i] for i in range(len(radii))]
        for i in range(len(radii) - 1, 0, -1):
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
        for i in range(1, len(radii)):
            xs.append(radii_x[i] - radii_x[i - 1])
            ys.append(radii_y[i] - radii_y[i - 1])
            txs.append(transfinite_r_data[i])
            tys.append(transfinite_r_data[i])
        transform_data[0] -= radii_x[-1]
        transform_data[1] -= radii_y[-1]
        kws = [{"ct": ct, "ct0": 0, "ct1": 0},
               {"ct": ct, "ct0": 1, "ct1": 0},
               {"ct": ct, "ct0": 0, "ct1": 1},
               {"ct": ct, "ct0": 1, "ct1": 1}]
        ct_map = {(x['ct0'], x['ct1']): i for i, x in enumerate(kws)}
        type_map, lcs, recs_map, trans_map, kws_map = [], [], [], [], []
        volumes_map, surfaces_map = [], []
        new_surfaces_names = {}
        ci, cj, ck = len(xs) // 2, len(ys) // 2, len(zs) // 2
        for k in range(len(zs)):
            for j in range(len(ys)):
                for i in range(len(xs)):
                    if i == ci and j == cj:  # C
                        type_map.append(1 if layers_exists[k][0] else 0)
                        lcs.append(layers_lcs[k][0])
                        recs_map.append(layers_recs[k][0])
                        trans_map.append(layers_trans[k][0])
                        volumes_map.append(layers_volumes_names[k][0])
                        kws_map.append(0)
                        sns = surfaces_names[layers_surfaces_names[k][0]]
                        new_sns = [sns[x] for x in self.surfaces_names_map[
                            ('C', len(sns))]]
                        surfaces_map.append(new_surfaces_names.setdefault(
                            tuple(new_sns), len(new_surfaces_names)))
                    elif i == ci:
                        li = abs(j - cj) - 1  # layer index
                        sns = surfaces_names[layers_surfaces_names[k][li]]
                        if j > cj:  # Y
                            type_map.append(7 if layers_exists[k][li] else 0)
                            new_sns = [sns[x] for x in self.surfaces_names_map[
                                ('Y', len(sns))]]
                        else:  # NY
                            type_map.append(9 if layers_exists[k][li] else 0)
                            new_sns = [sns[x] for x in self.surfaces_names_map[
                                ('NY', len(sns))]]
                        surfaces_map.append(new_surfaces_names.setdefault(
                            tuple(new_sns), len(new_surfaces_names)))
                        lcs.append(layers_lcs[k][li])
                        recs_map.append(layers_recs[k][li])
                        trans_map.append(layers_trans[k][li])
                        volumes_map.append(layers_volumes_names[k][li])
                        kws_map.append(ct_map[(ct0s[li], ct1s[li])])
                    elif j == cj:
                        li = abs(i - ci) - 1  # layer index
                        sns = surfaces_names[layers_surfaces_names[k][li]]
                        if i > ci:  # X
                            type_map.append(6 if layers_exists[k][li] else 0)
                            new_sns = [sns[x] for x in self.surfaces_names_map[
                                ('X', len(sns))]]
                        else:  # NX
                            type_map.append(8 if layers_exists[k][li] else 0)
                            new_sns = [sns[x] for x in self.surfaces_names_map[
                                ('NX', len(sns))]]
                        surfaces_map.append(new_surfaces_names.setdefault(
                            tuple(new_sns), len(new_surfaces_names)))
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
                        kws_map.append(0)
        new_surfaces_names = [list(x) for x in new_surfaces_names]
        Matrix.__init__(self, factory, xs=xs, ys=ys, zs=zs,
                        coordinates_type='delta', lcs=lcs,
                        transform_data=transform_data,
                        txs=txs, tys=tys, tzs=tzs,
                        type_map=type_map,
                        volumes_names=volumes_names,
                        volumes_map=volumes_map,
                        surfaces_names=new_surfaces_names,
                        surfaces_map=surfaces_map,
                        recs_map=recs_map, trans_map=trans_map,
                        kws=kws, kws_map=kws_map)
