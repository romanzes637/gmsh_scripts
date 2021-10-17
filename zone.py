import numpy as np
import gmsh

from support import DataTree, flatten


class Rule:
    """
    """

    def __init__(self):
        pass

    def __call__(self, block):
        pass


class BlockSimple(Rule):
    def __init__(self):
        super().__init__()

    def __call__(self, block):
        dt2zs = []  # tag to zone maps
        for b in block:
            dt2z = {}  # tag to zone map
            for i, entities in enumerate([b.points, b.curves,
                                          b.surfaces, b.volumes]):
                for e in entities:
                    dt, z = (i, e.tag), e.zone
                    if dt is not None and e.zone is not None:
                        dt2z[dt] = z
            dt2zs.append(dt2z)
        z2dt = {}  # zone to dim-tags map
        for dim in range(4):  # 0 - points, 1 - curves, 2 - surfaces, 3 - volumes
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


class BlockDirection(Rule):
    def __init__(self, zones=None, zones_directions=None):
        super().__init__()
        self.zones = ['NX', 'X', 'NY', 'Y', 'NZ', 'Z'] if zones is None else zones
        if zones_directions is None:
            self.zones_directions = [[[-1, 0, 0]], [[1, 0, 0]],
                                     [[0, -1, 0]], [[0, 1, 0]],
                                     [[0, 0, -1]], [[0, 0, 1]]]
        else:
            self.zones_directions = zones_directions

    def __call__(self, block):
        dt2zs = []  # tag to zone maps for each volume
        for b in block:
            vs_zs = [x.zone for x in b.volumes if x.tag is not None]
            vs_dt = [(3, x.tag) for x in b.volumes if x.tag is not None]
            tree = DataTree(vs_dt)
            for v_i, v_dt in enumerate(tree.vs_dt):
                dt2z = {}
                # Volume zone
                v_z = vs_zs[v_i]
                dt2z[v_dt] = v_z
                # Volume points
                # Points dim-tags
                v_ps_dt = list(set(flatten(tree.vs_ss_cs_ps_dt[v_i])))
                # Points coordinates
                v_ps_cs = np.array([tree.ps_dt_to_cs[x] for x in v_ps_dt])
                print(v_ps_cs)
                v_c = np.mean(v_ps_cs, axis=0)  # Centroid of the volume
                print(v_c, v_z)
                # Coordinates weights by direction
                cs2ws = Direction(zones=self.zones,
                                  zones_directions=self.zones_directions,
                                  origin=v_c)
                p_ws = cs2ws(v_ps_cs)  # Points zones weights
                p_ws_max = np.amax(p_ws, axis=0)
                p_ws_max_is = np.argwhere(np.isclose(p_ws, p_ws_max))
                p2z = {}
                for z_i, p_i in p_ws_max_is:
                    p2z.setdefault(p_i, []).append(z_i)
                for p_i, z_is in p2z.items():
                    p_z = '_'.join([cs2ws.zones[x] for x in z_is])
                    p_dt = v_ps_dt[p_i]
                    dt2z[p_dt] = p_z
                print('Surfaces')
                print(tree.vs_ss_dt[v_i])
                for s_i, s_dt in enumerate(tree.vs_ss_dt[v_i]):
                    cs2ws = Direction(zones=self.zones,
                                      zones_directions=self.zones_directions,
                                      origin=v_c)
                    # Points dim-tags
                    s_ps_dt = set(flatten(tree.vs_ss_cs_ps_dt[v_i][s_i]))
                    # Points coordinates
                    s_ps_cs = np.array([tree.ps_dt_to_cs[x] for x in s_ps_dt])
                    s_ws = cs2ws(s_ps_cs)
                    s_ws_sum = np.sum(s_ws, axis=1)
                    s_ws_max = np.amax(s_ws_sum)
                    s_ws_max_is = np.argwhere(np.isclose(s_ws_sum, s_ws_max))
                    print(s_ws_max_is)
                    s_z = '_'.join([cs2ws.zones[x[0]] for x in s_ws_max_is])
                    dt2z[s_dt] = s_z
                    # Curves
                    for c_i, c_dt in enumerate(tree.vs_ss_cs_dt[v_i][s_i]):
                        # print(c_dt)
                        c_ps_dt = set(flatten(tree.vs_ss_cs_ps_dt[v_i][s_i][c_i]))
                        # print(c_ps_dt)
                        c_ps_cs = np.array([tree.ps_dt_to_cs[x] for x in c_ps_dt])
                        # print(c_ps_cs)
                        cs2ws = Direction(zones=self.zones,
                                          zones_directions=self.zones_directions,
                                          origin=c_ps_cs[0])
                        c_ps_cs = [c_ps_cs[1]]
                        # print(c_ps_cs)
                        c_ws = cs2ws(c_ps_cs)
                        # print(c_ws)
                        c_ws = np.abs(c_ws)
                        c_ws_sum = np.sum(c_ws, axis=1)
                        c_ws_max = np.amax(c_ws_sum)
                        # print(c_ws_max)
                        c_ws_max_is = np.argwhere(np.isclose(c_ws, c_ws_max))
                        # print(c_ws_max_is)
                        c_z = '_'.join([cs2ws.zones[x[0]] for x in c_ws_max_is])
                        dt2z[(c_dt[0], abs(c_dt[1]))] = c_z
                dt2zs.append(dt2z)
        z2dt = {}  # zone to dim-tags map
        print(dt2zs)
        for dim in range(4):  # 0 - points, 1 - curves, 2 - surfaces, 3 - volumes
            es_dt = gmsh.model.getEntities(dim)
            for dt in es_dt:
                zs = []  # zones
                for dt2z in dt2zs:
                    if dt in dt2z:
                        zs.append(dt2z[dt])
                if dim == 2:
                    if len(zs) == 1:  # Boundary entities only
                        z2dt.setdefault(zs[0], []).append(dt)
                elif len(zs) > 0:
                    z2dt.setdefault(zs[0], []).append(dt)
        print(z2dt)
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
        ps_cs -= self.origin
        if self.normalize_points:
            ps_cs = [x / np.linalg.norm(x) for x in ps_cs]
        weights = [np.mean(np.dot(ps_cs, x.T), axis=1)
                   for x in self.zones_directions]
        return weights
