import logging

import numpy as np
import gmsh

from gmsh_scripts.support.support import DataTree, flatten
from gmsh_scripts.registry import get_boolean_new2olds, get_volume2block, \
    get_unregistered_volumes, POINT_TOL


class Zone:
    def __init__(self):
        pass

    def evaluate_map(self, block):
        dt2zs = {}  # dim-tag to zones
        return dt2zs

    def __call__(self, block):
        dt2zs = self.evaluate_map(block)
        z2dts = {}
        for dt, zs in dt2zs.items():
            dim, tag = dt
            if dim == 3 and len(zs) > 1:
                logging.warning(f'Several zones per one volume {tag}:  {zs}. Using first')
                zs = zs[:1]
            for z in zs:
                z2dts.setdefault(z, [[] for _ in range(4)])
                z2dts[z][dim].append(dt)
        for z, dts in z2dts.items():
            for dim in (0, 1, 2, 3):
                tags = [x[1] for x in dts[dim]]
                if len(tags) != 0:
                    tag = gmsh.model.addPhysicalGroup(dim, tags)
                    gmsh.model.setPhysicalName(dim, tag, z)


class Block(Zone):
    """Name from zone field of entity

            """

    def __init__(self, dims=None, dims_interfaces=None, inter_separator='|'):
        super().__init__()
        self.dims = [2, 3] if dims is None else dims
        self.dims_interfaces = [] if dims_interfaces is None else dims_interfaces
        self.inter_separator = [] if inter_separator is None else inter_separator

    def evaluate_map(self, block):
        dt2zs = {}
        for b in block:
            if 2 in self.dims:
                for i, s in enumerate(b.surfaces):
                    if s.tag is None:
                        continue
                    dt = (2, s.tag)
                    z = b.surfaces_zones[i]
                    dt2zs.setdefault(dt, []).append(z)
            if 3 in self.dims:
                for i, v in enumerate(b.volumes):
                    if v.tag is None:
                        continue
                    dt = (3, v.tag)
                    z = b.volume_zone
                    dt2zs.setdefault(dt, []).append(z)
        # Interfaces
        for dt in list(dt2zs.keys()):
            zs = dt2zs[dt]
            dim, tag = dt
            if len(zs) != 1:  # Interface
                if dim in self.dims_interfaces:
                    dt2zs[dt] = [self.inter_separator.join(zs)]
                else:
                    dt2zs.pop(dt)
            else:  # Boundary
                continue
        return dt2zs


class NoZone(Zone):
    """Name from zone field of entity

        """

    def __init__(self):
        super().__init__()

    def __call__(self, block):
        pass


class DirectionByNormal(Zone):
    """Construct zones from boolean map and Block's zones

    Args:
        dims (list): Which dims to zones
        dims_interfaces (list): Which dims to interfaces zones
        join_interfaces (list): Which interfaces should be joined together,
            Variants:
                1. [[volumes zones], [volumes zones], ...]
                2. [[[volumes zones], [entities zones]], ...]
            If the zone set with * symbol then join all zones which includes
            the zone else only zones that fully match the zone.
        self_separator (str): separator in volume, surface, curve and point
        intra_separator (str): separator between volume, surface, curve and point
        inter_separator (str): separator between interfaces
    """

    def __init__(self, dims=None, dims_interfaces=None,
                 join_interfaces=None,
                 self_separator='_', intra_separator='-', inter_separator='|',
                 zones=None, zones_directions=None):
        super().__init__()
        self.dims = [2, 3] if dims is None else dims
        self.dims_interfaces = [] if dims_interfaces is None else dims_interfaces
        self.join_interfaces = [] if join_interfaces is None else join_interfaces
        self.self_separator = self_separator
        self.intra_separator = intra_separator
        self.inter_separator = inter_separator
        self.zones = ['NX', 'X', 'NY', 'Y', 'NZ', 'Z'] if zones is None else zones
        if zones_directions is None:
            zones_directions = [[[-1, 0, 0]], [[1, 0, 0]],
                                [[0, -1, 0]], [[0, 1, 0]],
                                [[0, 0, -1]], [[0, 0, 1]]]
        # Normalize
        for i, ds in enumerate(zones_directions):
            for j, d in enumerate(ds):
                n = np.linalg.norm(d)
                zones_directions[i][j] = d / n if n != 0 else d
        self.zones_directions = zones_directions

    def evaluate_map(self, block):
        dt2zs = {}
        new2olds = get_boolean_new2olds()
        vs_dt = gmsh.model.getEntities(3)
        v2b = get_volume2block()
        uvs = get_unregistered_volumes()
        e2vs = {}
        e2bb = {}
        for vi, v_dt in enumerate(vs_dt):  # Volumes
            e2bb[v_dt] = v_dt
            tree = DataTree([v_dt])
            v_t = v_dt[1]
            old_vts = new2olds.get(v_t, [v_t])
            bs = [v2b[x] for x in old_vts]
            v_zs = [b.volume_zone for b in bs]
            if len(v_zs) > 1:
                bls = [b.boolean_level for b in bs]
                max_bls_ids = np.argwhere(bls == np.max(bls))
                v_zs = [v_zs[x[0]] for x in max_bls_ids]
            v_z = self.self_separator.join(sorted(set(v_zs)))
            dt2zs.setdefault(v_dt, []).append(v_z)
            if 2 in self.dims:  # Surfaces
                for si, ss_cs_ps_dt in enumerate(tree.vs_ss_cs_ps_dt[0]):
                    s_dt = tree.vs_ss_dt[0][si]
                    s_dt = (s_dt[0], abs(s_dt[1]))  # TODO Use undirected surface?
                    ss_ps = set(flatten(ss_cs_ps_dt))
                    ss_ps_cs = [tree.ps_dt_to_cs[x] for x in ss_ps]
                    s_bb = np.append(np.min(ss_ps_cs, axis=0),
                                     np.max(ss_ps_cs, axis=0))
                    # s_bb = gmsh.model.getBoundingBox(*s_dt)
                    # print(s_bb)
                    e2bb[s_dt] = s_bb
                    n = gmsh.model.getNormal(s_dt[1], [0.5, 0.5])  # Normal
                    # TODO Check what nan and empty means
                    if any(np.isnan(x) for x in n) or len(n) == 0:
                        s_zs = ['X', 'Y', 'Z']
                    else:
                        weights = [[np.dot(n, y) for y in x]
                                   for x in self.zones_directions]
                        agr_weights = [np.mean(x) for x in weights]
                        max_weight_ids = np.argwhere(
                            np.logical_or(
                                np.isclose(agr_weights, np.min(agr_weights)),
                                np.isclose(agr_weights, np.max(agr_weights))))
                        s_zs = [self.zones[x[0]] for x in max_weight_ids]
                    # Correct TODO direction detection?
                    s_zs = [x if x != 'NX' else 'X' for x in s_zs]
                    s_zs = [x if x != 'NY' else 'Y' for x in s_zs]
                    s_zs = [x if x != 'NZ' else 'Z' for x in s_zs]
                    s_z = self.self_separator.join(sorted(set(s_zs)))
                    dt2zs.setdefault(s_dt, []).append(s_z)
                    e2vs.setdefault(s_dt, []).append(v_dt)
        # Sort values
        z2vs = {}
        dt2v = {}
        for dt, zs in dt2zs.items():
            dim, tag = dt
            bb = e2bb[dt]  # min x, min y, min z, max x, max y, max Z
            for z in zs:
                if dim == 2:
                    v = None
                    if 'X' in z.split(self.self_separator):
                        v = bb[0] if v is None else min([v, bb[0]])
                    if 'Y' in z.split(self.self_separator):
                        v = bb[1] if v is None else min([v, bb[1]])
                    if 'Z' in z.split(self.self_separator):
                        v = bb[2] if v is None else min([v, bb[2]])
                    if v is None:
                        continue
                    v = round(v, POINT_TOL)
                    z2vs.setdefault(z, set()).add(v)
                    dt2v[dt] = v
                else:
                    continue
        # Zone value to index map
        z2v2i = {}
        for z, vs in z2vs.items():
            z2v2i[z] = {x: i for i, x in enumerate(sorted(vs))}
        # Update zones
        for dt, zs in dt2zs.items():
            for zi, z in enumerate(zs):
                v2i = z2v2i.get(z, None)
                if v2i is None:
                    continue
                min_i, max_i = min(v2i.values()), max(v2i.values()),
                if z is None:
                    continue
                v = dt2v.get(dt, None)
                if v is None:
                    continue
                i = v2i.get(v, None)
                if i is None:
                    continue
                if any(['X' in z.split(self.self_separator),
                        'Y' in z.split(self.self_separator),
                        'Z' in z.split(self.self_separator)]):
                    if i == min_i:
                        dt2zs[dt][zi] = f'N{z}'
                    elif i == max_i:
                        dt2zs[dt][zi] = z
                    else:
                        dt2zs[dt][zi] = f'{z}{i}'
                else:
                    dt2zs[dt][zi] = f'{z}{i}'
        # Surfaces TODO Add curves and points
        for e_dt, vs_dt in e2vs.items():
            dim, tag = e_dt
            vs_us = [x[1] in uvs for x in vs_dt]  # Are volumes unregistered?
            vs_zs = [dt2zs[x][0] for x in vs_dt]
            e_zs = dt2zs[e_dt]
            do_join_entities = False
            for j in self.join_interfaces:
                if isinstance(j[0], list):
                    v_zs_j, e_z_j = j
                else:
                    v_zs_j, e_z_j = j, None
                if all(x in vs_zs for x in v_zs_j):
                    if e_z_j is None:
                        do_join_entities = True
                    else:
                        e_szs = [y for x in e_zs
                                 for y in x.split(self.self_separator)]
                        do_join_entities = True
                        for z in e_z_j:
                            if z[-1] == '*':  # In string
                                z = z[:-1]
                                for sz in e_szs:
                                    if z not in sz:
                                        do_join_entities = False
                            else:  # String
                                if z not in e_szs:
                                    do_join_entities = False
            v_z = self.inter_separator.join(sorted(set(vs_zs)))
            if not do_join_entities:
                e_z = self.intra_separator.join(sorted(set(e_zs)))
                z = self.intra_separator.join([v_z, e_z])
            else:
                z = v_z
            if all(vs_us):  # All volumes are unregistered
                dt2zs.pop(e_dt, None)
            elif any(vs_us):  # Some volumes are unregistered
                if dim == 2:  # Surface
                    if len(vs_us) == 1:  # Unregistered
                        dt2zs.pop(e_dt, None)
                    elif len(vs_us) == 2:  # Boundary from Interface
                        dt2zs[e_dt] = [z]
            else:  # No volumes are unregistered
                if dim == 2:  # Surface
                    if len(vs_us) == 1:  # Boundary
                        dt2zs[e_dt] = [z]
                    elif len(vs_us) == 2:  # Interface
                        if 2 in self.dims_interfaces:
                            dt2zs[e_dt] = [z]
                        else:
                            dt2zs.pop(e_dt, None)
                    else:
                        raise ValueError(e_dt, vs_dt)
        # Remove unregistered volumes zones
        for dt in list(dt2zs.keys()):
            dim, tag = dt
            if dim == 3 and tag in uvs:
                dt2zs.pop(dt, None)
        return dt2zs

    def __call__(self, block):
        super().__call__(block)


class Mesh(Zone):
    """Construct zones from mesh instead of Block's zones

    Args:
        dims (tuple of int): Which dims to zones
        dims_interfaces (tuple of int): Which dims to interfaces zones
        join_interfaces (str): Join interfaces zones
            'all' - join all in alphabetical order
            'first' - get first only in alphabetical order
            None - don't join
        entities_separator (str):
            separator between volume, surface, curve and point
        join_separator (str):
            separator used in join_interfaces
    """

    def __init__(self, dims=(0, 1, 2, 3), dims_interfaces=(0, 1, 2, 3),
                 join_interfaces='all', entities_separator='_',
                 join_separator='-'):
        self.dims = dims
        self.dims_interfaces = dims_interfaces
        self.join_interfaces = join_interfaces
        self.entities_separator = entities_separator
        self.join_separator = join_separator
        super().__init__()

    def evaluate_map(self, block):
        dt2zs = {}
        vs_dt = gmsh.model.getEntities(3)
        tree = DataTree(vs_dt)
        for vi, ss_cs_ps_dt in enumerate(tree.vs_ss_cs_ps_dt):  # Volumes
            if 3 in self.dims:
                v_dt = tree.vs_dt[vi]
                v_z = self.entities_separator.join(('V', str(vi)))
                dt2zs.setdefault(v_dt, set()).add(v_z)
            for si, cs_ps_dt in enumerate(ss_cs_ps_dt):  # Surfaces
                if 2 in self.dims:
                    s_dt = tree.vs_ss_dt[vi][si]
                    s_z = self.entities_separator.join(('S', str(vi), str(si)))
                    dt2zs.setdefault(s_dt, set()).add(s_z)
                for ci, ps_dt in enumerate(cs_ps_dt):  # Curves
                    if 1 in self.dims:
                        c_dt = tree.vs_ss_cs_dt[vi][si][ci]
                        c_dt = (1, abs(c_dt[1]))  # Remove orientation
                        c_z = self.entities_separator.join(
                            ('C', str(vi), str(si), str(ci)))
                        dt2zs.setdefault(c_dt, set()).add(c_z)
                    for pi, p_dt in enumerate(ps_dt):  # Points
                        p_z = self.entities_separator.join(
                            ('P', str(vi), str(si), str(ci), str(pi)))
                        if 0 in self.dims:
                            dt2zs.setdefault(p_dt, set()).add(p_z)
        # Remove interfaces unless they are not dims_interfaces
        dt2zs = {k: v for k, v in dt2zs.items()
                 if len(v) == 1 or k[0] in self.dims_interfaces}
        # Join interfaces names
        if self.join_interfaces is not None:
            if self.join_interfaces == 'first':
                dt2zs = {k: [sorted(list(v))[0]] for k, v in dt2zs.items()}
            elif self.join_interfaces == 'all':
                dt2zs = {k: [self.join_separator.join(sorted(list(v)))]
                         for k, v in dt2zs.items()}
            else:
                raise ValueError(self.join_interfaces)
        return dt2zs

    def __call__(self, block):
        super().__call__(block)


str2obj = {
    Zone.__name__: Zone,
    NoZone.__name__: NoZone,
    Mesh.__name__: Mesh,
    DirectionByNormal.__name__: DirectionByNormal,
    Block.__name__: Block
}
