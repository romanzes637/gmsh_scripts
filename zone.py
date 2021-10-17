from pprint import pprint

import gmsh
import numpy as np

from support import DataTree, flatten


class ZoneMap:
    """Zone name to tags map

    """

    def __init__(self, points=None, curves=None, surfaces=None, volumes=None):
        self.points = {} if points is None else points
        self.curves = {} if curves is None else curves
        self.surfaces = {} if surfaces is None else surfaces
        self.volumes = {} if volumes is None else volumes


class Rule:
    """Converts volumes to ZoneMap

    """

    def __init__(self):
        pass

    def __call__(self, block):
        zm = ZoneMap()
        return zm


class BlockSimple(Rule):
    def __init__(self):
        super().__init__()

    def __call__(self, block):
        zm = ZoneMap()
        for dim in range(0, 4):
            zone2tag = {}
            if dim == 0:
                xs = b.points
            elif dim == 1:
                xs = b.curves
            elif dim == 2:
                xs = b.surfaces
            elif dim == 3:
                xs = b.volumes
            for x in xs:
                if x.zone is not None and x.tag is not None:
                    zone2tag.setdefault(x.zone, []).append(x.tag)


class Block(Rule):
    def __init__(self, point_names=None, curves_names=None, surfaces_names=None,
                 volume_name=None):
        super().__init__()
        if point_names is None:
            self.point_names = ['X_Y_NZ', 'NX_Y_NZ', 'NX_NY_NZ', 'X_NY_NZ',
                                'X_Y_Z', 'NX_Y_Z', 'NX_NY_Z', 'X_NY_Z']
        else:
            self.point_names = point_names
        if curves_names is None:
            self.curves_names = ['X1', 'X2', 'X3', 'X4', 'Y1', 'Y2', 'Y3', 'Y4',
                                 'Z1', 'Z2', 'Z3', 'Z4']
        else:
            self.curves_names = curves_names
        if surfaces_names is None:
            self.surfaces_names = ['NX', 'X', 'NY', 'Y', 'NZ', 'Z']
        else:
            self.surfaces_names = surfaces_names
        self.volume_name = 'B' if volume_name is None else volume_name

    def __call__(self, block):
        vs_dt = [(3, x.tag) for x in block.volumes]
        dt = DataTree(vs_dt)
        vs_dt = dt.vs_dt
        vs_ss_dt = dt.vs_ss_dt
        vs_ss_cs_dt = dt.vs_ss_cs_dt
        vs_ss_cs_ps_dt = dt.vs_ss_cs_ps_dt
        ps_dt_to_cs = dt.ps_dt_to_cs
        for v_i, v_dt in enumerate(vs_dt):
            v_ps_dt = list(set(flatten(vs_ss_cs_ps_dt[v_i])))
            v_ps_cs = np.array([ps_dt_to_cs[x] for x in v_ps_dt])
            v_c = np.mean(v_ps_cs, axis=0)  # Centroid of the volume
            cs2ws = Direction(zones=['NX', 'X', 'NY', 'Y', 'NZ', 'Z'],
                              zones_directions=[[[-1, 0, 0]], [[1, 0, 0]],
                                                [[0, -1, 0]], [[0, 1, 0]],
                                                [[0, 0, -1]], [[0, 0, 1]]],
                              origin=v_c)
            print('Points')
            p_ws = cs2ws(v_ps_cs)
            print(p_ws)
            p_ws_max = np.amax(p_ws, axis=0)
            print(p_ws_max)
            p_ws_max_is = np.argwhere(np.isclose(p_ws, p_ws_max))
            print(p_ws_max_is)
            p2z = {}
            for z_i, p_i in p_ws_max_is:
                p2z.setdefault(p_i, []).append(z_i)
            print(p2z)
            for p_i, z_is in p2z.items():
                p_z = '_'.join([cs2ws.zones[x] for x in z_is])
                print(v_ps_dt[p_i], p_z)
            for s_i, s_dt in enumerate(vs_ss_dt[v_i]):
                print('Surface', s_i, s_dt)
                s_ps_dt = set(flatten(vs_ss_cs_ps_dt[v_i][s_i]))
                s_ps_cs = np.array([ps_dt_to_cs[x] for x in s_ps_dt])
                print(s_ps_cs)
                s_ws = cs2ws(s_ps_cs)
                print(s_ws)
                s_ws_sum = np.sum(s_ws, axis=1)
                print(s_ws_sum)
                s_ws_max = np.amax(s_ws_sum)
                print(s_ws_max)
                s_ws_max_is = np.argwhere(np.isclose(s_ws_sum, s_ws_max))
                print(s_ws_max_is)
                s_z = '_'.join([cs2ws.zones[x] for x in s_ws_max_is[0]])
                print(s_dt, s_z)
        zm = ZoneMap()
        return zm


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
