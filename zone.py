import logging

import numpy as np
import gmsh

from support import DataTree, flatten
from registry import get_boolean_new2olds, get_volume2block


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


class Boolean(Zone):
    """Construct zones from boolean map and Block's zones

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
        new2old = get_boolean_new2olds()
        v2b = get_volume2block()
        dt2zs = {}
        vs_dt = gmsh.model.getEntities(3)
        tree = DataTree(vs_dt)
        for vi, ss_cs_ps_dt in enumerate(tree.vs_ss_cs_ps_dt):  # Volumes
            if 3 in self.dims:
                v_dt = tree.vs_dt[vi]
                v_t = v_dt[1]
                old_vts = new2old[v_t]
                old_bs = [v2b[x] for x in old_vts]
                new_zs = [b.volume_zone for b in old_bs]
                new_ls = [b.boolean_level for b in old_bs]
                max_l = max(new_ls)
                new_zs = [x for i, x in enumerate(new_zs) if new_ls[i] == max_l]
                new_zs = sorted(list(set(new_zs)))  # unique, alphabetic
                v_z = self.entities_separator.join(new_zs)
                dt2zs.setdefault(v_dt, []).append(v_z)
            else:
                v_z = 'V'
            for si, cs_ps_dt in enumerate(ss_cs_ps_dt):  # Surfaces
                if 2 in self.dims:
                    s_dt = tree.vs_ss_dt[vi][si]
                    s_z = self.entities_separator.join((v_z, str(vi), str(si)))
                    dt2zs.setdefault(s_dt, []).append(s_z)
                for ci, ps_dt in enumerate(cs_ps_dt):  # Curves
                    if 1 in self.dims:
                        c_dt = tree.vs_ss_cs_dt[vi][si][ci]
                        c_dt = (1, abs(c_dt[1]))  # Remove orientation
                        c_z = self.entities_separator.join(
                            ('C',  str(vi), str(si), str(ci)))
                        dt2zs.setdefault(c_dt, []).append(c_z)
                    for pi, p_dt in enumerate(ps_dt):  # Points
                        p_z = self.entities_separator.join(
                            ('P', str(vi), str(si), str(ci), str(pi)))
                        if 0 in self.dims:
                            dt2zs.setdefault(p_dt, []).append(p_z)
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


class DirectionByInterval(Zone):
    """Construct zones from boolean map and Block's zones

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
        new2old = get_boolean_new2olds()
        v2b = get_volume2block()
        vs_dt = gmsh.model.getEntities(3)
        tree = DataTree(vs_dt)
        for vi, ss_cs_ps_dt in enumerate(tree.vs_ss_cs_ps_dt):  # Volumes
            if 3 in self.dims:
                v_dt = tree.vs_dt[vi]
                v_t = v_dt[1]
                old_vts = new2old[v_t]
                old_bs = [v2b[x] for x in old_vts]
                new_zs = [b.volume_zone for b in old_bs]
                new_ls = [b.boolean_level for b in old_bs]
                max_l = max(new_ls)
                new_zs = [x for i, x in enumerate(new_zs) if new_ls[i] == max_l]
                new_zs = sorted(list(set(new_zs)))  # unique, alphabetic
                v_z = self.entities_separator.join(new_zs)
                dt2zs.setdefault(v_dt, []).append(v_z)
            else:
                v_z = 'V'
            for si, cs_ps_dt in enumerate(ss_cs_ps_dt):  # Surfaces
                if 2 in self.dims:
                    s_dt = tree.vs_ss_dt[vi][si]  # dim-tag
                    s_z = self.entities_separator.join((v_z, str(vi), str(si)))
                    dt2zs.setdefault(s_dt, []).append(s_z)
                for ci, ps_dt in enumerate(cs_ps_dt):  # Curves
                    if 1 in self.dims:
                        c_dt = tree.vs_ss_cs_dt[vi][si][ci]
                        c_dt = (1, abs(c_dt[1]))  # Remove orientation
                        c_z = self.entities_separator.join(
                            ('C',  str(vi), str(si), str(ci)))
                        dt2zs.setdefault(c_dt, []).append(c_z)
                    for pi, p_dt in enumerate(ps_dt):  # Points
                        p_z = self.entities_separator.join(
                            ('P', str(vi), str(si), str(ci), str(pi)))
                        if 0 in self.dims:
                            dt2zs.setdefault(p_dt, []).append(p_z)
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
                            ('C',  str(vi), str(si), str(ci)))
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


class NoZone(Zone):
    """Name from zone field of entity

        """

    def __init__(self):
        super().__init__()

    def __call__(self, block):
        pass


class BlockVolumes(Zone):
    """Zones from volumes of blocks

    """

    def __init__(self):
        super().__init__()

    def evaluate_map(self, block):
        dt2zs = {}  # dim-tag to zone maps
        for bi, b in enumerate(block):
            vs = list(flatten([x.volumes for x in b]))
            vs_dt = [(3, x.tag) for x in vs if x.tag is not None]
            vs_zs = [x.zone for x in vs if x.tag is not None]
            tree = DataTree(vs_dt)
            for vi, ss_dt in enumerate(tree.vs_ss_dt):
                v_dt = tree.vs_dt[vi]
                v_z = vs_zs[vi]
                dt2zs.setdefault(v_dt, set()).add(f'{v_z}-{bi}-{vi}')
                for si, s_dt in enumerate(ss_dt):
                    dt2zs.setdefault(s_dt, set()).add(f'{v_z}-{bi}-{vi}-{si}')
        return dt2zs

    def __call__(self, block):
        super().__call__(block)


class BlockSimple(Zone):
    """Name from zone field of entity

    """

    def __init__(self, dims=(0, 1, 2, 3)):
        super().__init__()
        self.dims = dims

    def __call__(self, block):
        dt2zs = []  # dim-tag to zone maps
        for b in block:
            dt2z = {}  # dim-tag to zone map
            for i, es in enumerate([b.points, b.curves, b.surfaces, b.volumes]):
                for e in es:
                    dt, z = (i, e.tag), e.zone
                    if dt is not None and e.zone is not None:
                        dt2z[dt] = z
            dt2zs.append(dt2z)
        z2dt = {}  # zone to dim-tags map
        for dim in self.dims:
            es_dt = gmsh.model.getEntities(dim)
            for dt in es_dt:
                zs = []  # zones
                for dt2z in dt2zs:
                    if dt in dt2z:
                        zs.append(dt2z[dt])
                if len(zs) == 1:  # Boundary entities only
                    z = zs[0]
                    z2dt.setdefault(z, []).append(dt)
        # Add zones
        for zone, tags in z2dt.items():
            dims, tags = [x[0] for x in tags], [x[1] for x in tags]
            dim = dims[0]
            tag = gmsh.model.addPhysicalGroup(dim, tags)
            gmsh.model.setPhysicalName(dim, tag, zone)


class BlockDirection(Zone):
    def __init__(self, zones=None, zones_directions=None, dims=(0, 1, 2, 3),
                 make_interface=False, add_volume_tag=False, add_volume_zone=True,
                 add_surface_loop_tag=False, add_in_out_boundary=False):
        super().__init__()
        self.zones = ['NX', 'X', 'NY', 'Y', 'NZ', 'Z'] if zones is None else zones
        if zones_directions is None:
            self.zones_directions = [[[-1, 0, 0]], [[1, 0, 0]],
                                     [[0, -1, 0]], [[0, 1, 0]],
                                     [[0, 0, -1]], [[0, 0, 1]]]
        else:
            self.zones_directions = zones_directions
        self.dims = dims  # 0 - points, 1 - curves, 2 - surfaces, 3 - volumes
        self.make_interface = make_interface
        self.add_volume_tag = add_volume_tag
        self.add_volume_zone = add_volume_zone
        self.add_surface_loop_tag = add_surface_loop_tag
        self.add_in_out_boundary = add_in_out_boundary

    def make_zone_name(self, name, surface_loop_type, surface_loop_tag,
                       volume_tag, volume_zone):
        new_name = ''
        # Surface loop
        if surface_loop_type == 'boundary':
            if self.add_in_out_boundary:
                if surface_loop_tag == 0:  # External boundary
                    new_name += 'BE'
                else:  # Internal boundary
                    new_name += 'BI'
            else:  # Boundary
                new_name += 'B'
        else:  # Interface
            new_name = 'I'
        if self.add_surface_loop_tag:
            new_name += f'-{surface_loop_tag}'
        new_name += '__'
        # Volume
        if self.add_volume_zone and self.add_volume_tag:
            new_name += f'{volume_zone}-{volume_tag}_'
        elif self.add_volume_zone:
            new_name += f'{volume_zone}_'
        elif self.add_volume_tag:
            new_name += f'{volume_tag}_'
        else:
            pass
        # Name
        new_name += name
        return new_name

    def __call__(self, block):
        dt2zs = []  # tag to zone maps for each volume
        vs = list(flatten([x.volumes for x in block]))
        vs_dt = [(3, x.tag) for x in vs if x.tag is not None]
        vs_zs = [x.zone for x in vs if x.tag is not None]
        tree = DataTree(vs_dt)
        for i, (sl_t, sls, s2sl) in enumerate([('boundary', tree.b_sls, tree.b_s2sl),
                                               ('interface', tree.i_sls, tree.i_s2sl)]):
            sl_ps = {}  # Points of surfaces loops
            for v_i, v_dt in enumerate(tree.vs_dt):
                for s_i, s_dt in enumerate(tree.vs_ss_dt[v_i]):
                    if not s_dt[1] in s2sl:
                        continue
                    ps_dt = set(flatten(tree.vs_ss_cs_ps_dt[v_i][s_i]))
                    sl_i = s2sl[s_dt[1]]
                    sl_ps.setdefault(sl_i, set()).update(ps_dt)
            sls_cs2ws = []
            for sl_i, sl in enumerate(sls):
                sl_ps_cs = np.array([tree.ps_dt_to_cs[x] for x in sl_ps[sl_i]])
                sl_c = np.mean(sl_ps_cs, axis=0)  # Centroid of the surface loop
                # Coordinates to weights map of surface loop
                sl_cs2ws = Direction(zones=self.zones,
                                     zones_directions=self.zones_directions,
                                     origin=sl_c)
                sls_cs2ws.append(sl_cs2ws)
            for v_i, v_dt in enumerate(tree.vs_dt):
                dt2z = {}
                # Volume zone
                v_t = v_dt[1]
                v_z = vs_zs[v_i]
                dt2z[v_dt] = v_z
                for s_i, s_dt in enumerate(tree.vs_ss_dt[v_i]):
                    if not s_dt[1] in s2sl:
                        continue
                    sl_i = s2sl[s_dt[1]]
                    sl_cs2ws = sls_cs2ws[sl_i]
                    # Surface dim-tag
                    s_dt = tree.vs_ss_dt[v_i][s_i]
                    # Points of surface dim-tags
                    s_ps_dt = list(set(flatten(tree.vs_ss_cs_ps_dt[v_i][s_i])))
                    # Points of surface coordinates
                    s_ps_cs = np.array([tree.ps_dt_to_cs[x] for x in s_ps_dt])
                    # Weights by directions
                    s_ws = sl_cs2ws(s_ps_cs)
                    s_ws_sum = np.sum(s_ws, axis=1)
                    s_ws_max = np.amax(s_ws_sum)
                    s_ws_max_is = np.argwhere(np.isclose(s_ws_sum, s_ws_max))
                    s_z = '-'.join([sl_cs2ws.zones[x[0]] for x in s_ws_max_is])
                    s_z = self.make_zone_name(name=s_z, surface_loop_tag=sl_i,
                                              surface_loop_type=sl_t,
                                              volume_tag=v_t, volume_zone=v_z)
                    dt2z[s_dt] = s_z
                    # Points
                    p_ws_max = np.amax(s_ws, axis=0)
                    p_ws_max_is = np.argwhere(np.isclose(s_ws, p_ws_max))
                    p2zs = {}
                    for z_i, p_i in p_ws_max_is:
                        p2zs.setdefault(p_i, []).append(z_i)
                    for p_i, zs_i in p2zs.items():
                        p_dt = s_ps_dt[p_i]
                        p_z = '-'.join([sl_cs2ws.zones[x] for x in zs_i])
                        p_z = self.make_zone_name(name=p_z, surface_loop_tag=sl_i,
                                                  surface_loop_type=sl_t,
                                                  volume_tag=v_t, volume_zone=v_z)
                        dt2z[p_dt] = p_z
                    # Curves
                    for c_i, c_dt in enumerate(tree.vs_ss_cs_dt[v_i][s_i]):
                        c_ps_dt = set(flatten(tree.vs_ss_cs_ps_dt[v_i][s_i][c_i]))
                        c_ps_cs = np.array([tree.ps_dt_to_cs[x] for x in c_ps_dt])
                        c_cs2ws = Direction(zones=self.zones,
                                            zones_directions=self.zones_directions,
                                            origin=c_ps_cs[0])
                        c_ps_cs = [c_ps_cs[1]]
                        c_ws = c_cs2ws(c_ps_cs)
                        c_ws = np.abs(c_ws)
                        c_ws_sum = np.sum(c_ws, axis=1)
                        c_ws_max = np.amax(c_ws_sum)
                        c_ws_max_is = np.argwhere(np.isclose(c_ws, c_ws_max))
                        c_z = '-'.join([c_cs2ws.zones[x[0]] for x in c_ws_max_is])
                        c_z = self.make_zone_name(name=c_z, surface_loop_tag=sl_i,
                                                  surface_loop_type=sl_t,
                                                  volume_tag=v_t, volume_zone=v_z)
                        dt2z[(c_dt[0], abs(c_dt[1]))] = c_z
                dt2zs.append(dt2z)
        z2dt = {}  # zone to dim-tags map
        for dim in self.dims:
            es_dt = gmsh.model.getEntities(dim)
            for dt in es_dt:
                zs = []  # zones
                for dt2z in dt2zs:
                    if dt in dt2z:
                        zs.append(dt2z[dt])
                if dim == 2:
                    if len(zs) == 1:  # Boundary
                        z2dt.setdefault(zs[0], []).append(dt)
                    elif len(zs) > 0 and self.make_interface:  # Interface
                        z = f'{"--".join(zs)}'
                        z2dt.setdefault(z, []).append(dt)
                elif len(zs) > 0:
                    z2dt.setdefault(zs[0], []).append(dt)
        # Add zones
        for z, dts in z2dt.items():
            unique_dims = {x[0] for x in dts}
            for dim in unique_dims:
                tags = [x[1] for x in dts if x[0] == dim]
                tag = gmsh.model.addPhysicalGroup(dim, tags)
                gmsh.model.setPhysicalName(dim, tag, z)


# TODO distance, box, cylinder, ball etc
class CoordinatesToWeights:
    """Convert points coordinates to weights of zones

    Args:
        zones (list of str): names of zones

    Attributes:
        zones (list of str): names of zones
    """

    def __init__(self, zones):
        self.zones = zones

    def __call__(self, points_coordinates):
        """Convert coordinates to weights

        Args:
            points_coordinates (np.ndarray): 2D array of points coordinates

        Returns:
            (np.ndarray): 2D array of points weights by zone
        """
        pass


class Direction(CoordinatesToWeights):
    """

    Args:
        zones_directions (np.ndarray): 3D array of zones directions
        origin (np.ndarray): 1D origin of local coordinate system
        normalize_directions (bool): Normalize coordinates to unit vectors
        normalize_points (bool): Normalize directions to unit vectors

    Attributes:
        zones_directions (np.ndarray): list of 3D array of zones directions
        origin (np.ndarray): 1D origin of local coordinate system
        normalize_directions (bool): Normalize coordinates to unit vectors
        normalize_points (bool): Normalize directions to unit vectors
    """

    def __init__(self, zones, zones_directions, origin=None,
                 normalize_directions=True,
                 normalize_points=True):
        super().__init__(zones)
        if normalize_directions:
            zones_directions = [x / np.linalg.norm(x, axis=1, keepdims=True)
                                for x in zones_directions]
        self.zones_directions = zones_directions
        self.origin = [0, 0, 0] if origin is None else origin
        self.normalize_directions = normalize_directions
        self.normalize_points = normalize_points

    def __call__(self, ps_cs):
        ps_cs = ps_cs - self.origin
        if self.normalize_points:
            ps_cs = [x / np.linalg.norm(x) for x in ps_cs]
        weights = [np.mean(np.dot(ps_cs, x.T), axis=1)
                   for x in self.zones_directions]
        return weights


str2obj = {
    Zone.__name__: Zone,
    BlockSimple.__name__: BlockSimple,
    BlockDirection.__name__: BlockDirection,
    NoZone.__name__: NoZone,
    Boolean.__name__: Boolean,
    DirectionByInterval.__name__: DirectionByInterval
}
