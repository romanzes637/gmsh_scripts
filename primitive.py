import gmsh
import itertools
from collections import deque
from itertools import permutations
from pprint import pprint
import time
import numpy as np

from occ_workarounds import correct_and_transfinite_primitive
from support import volumes_groups_surfaces, volumes_groups_surfaces_registry
import registry


class Primitive:
    def __init__(self, factory, point_data=None, transform_data=None,
                 curve_types=None, curve_data=None,
                 transfinite_data=None, transfinite_type=None,
                 volume_name=None, inner_volumes=None, surfaces_names=None,
                 rec=None, trans=None):
        """
        Base object with six quadrangular surfaces and eight points
        The object (e.g. number of its volumes/surfaces)
        could be changed in process, if not it may be meshed to structured mesh
        Object structure:
        Axes:
        Y
        Z X
        Points:
        Top Z:
        P5 P4
        P6 P7
        Bottom Z:
        P1 P0
        P2 P3
        Curves:
        L0: P1 -> P0  L1: P5 -> P4  L2: P6  -> P7   L3: P2 -> P3
        (X direction curves from P0 by right-hand rule)
        L4: P3 -> P0  L5: P2 -> P1  L6: P6  -> P5   L7: P7 -> P4
        (Y direction curves from P0 by right-hand rule)
        L8: P0 -> P4  L9: P1 -> P5  L10: P2 -> P6  L11: P3 -> P7
        (Z direction curves from P0 by right-hand rule)
        Surfaces:
        S0: L5  -> L9  -> -L6 -> -L10 (NX surface)
        S1: -L4 -> L11 -> L7  -> -L8  (X surface)
        S2: -L3 -> L10 -> L2  -> -L11 (NY surface)
        S3: L0  -> L8  -> -L1 -> -L9  (Y surface)
        S4: -L0 -> -L5 ->  L3 -> L4   (NZ surface)
        S5: L1  -> -L7 -> -L2 -> L6   (Z surface)
        :param str factory: gmsh factory (currently: 'geo' or 'occ')
        :param list of list of float point_data:
        [[point1_x, point1_y, point1_z, point1_lc], ...,
        [point8_x, point8_y, point8_z, point8_lc]] or
        [[point1_x, point1_y, point1_z], ...,
        [point8_x, point8_y, point8_z]] or
        [length_x, length_y, length_z, lc] or
        [length_x, length_y, length_z]
        :param list transform_data:
        list of transformations: [transformation, transformation, ...]
        where transformation is
        [[displacement x, y, z], [mask]] or
        [[rotation direction x, y, z, rot. angle], [mask]] or
        [[rot. origin x, y, z, rot. direction x, y, z, rot. angle], [mask]]
        :param list of int curve_types:
        [line1_type, line2_type, ..., line12_type],
        types: 0 - line, 1 - circle, 2 - ellipse
        (FIXME not implemented for occ factory),
        3 - spline, 4 - bspline (number of curve points > 1), 5 - bezier curve
        :param list of list of list of float curve_data:
        [[[line1_point1_x, line1_point1_y, line1_point1_z, line1_point1_lc],
        ...], ..., [[line_12..., ...], ...]]] or
        [[[line1_point1_x, line1_point1_y, line1_point1_z], ...],
        ..., [[line_12_point_1, ...], ...]]]
        :param list of list of float transfinite_data:
        [[line1 number of nodes, type, coefficient], ..., [line12 ...]]
        or [[x_lines number of nodes, type, coefficient], [y_lines ...],
        [z_lines ...]]
        types: 0 - progression, 1 - bump
        :param int transfinite_type: 0, 1, 2 or 4 determines orientation
        of surfaces' tetrahedra at structured volume
        :param str volume_name: primitive's volumes physical name
        :param list of int inner_volumes: inner volumes,
        no effect at 'occ' factory, if point_data is None wrap these volumes
        as Primitive.volumes
        :param list of str surfaces_names: names of boundary surfaces in order:
        NX, X, NY, Y, NZ, Z.
        :param int rec: Recombine Primitive?
        :param int trans: Transfinite Primitive?
        """
        if factory == 'occ':
            self.factory = gmsh.model.occ
        else:
            self.factory = gmsh.model.geo
        if transfinite_data is not None:
            if len(transfinite_data) == 3:
                self.transfinite_data = list()
                self.transfinite_data.extend([transfinite_data[0]] * 4)
                self.transfinite_data.extend([transfinite_data[1]] * 4)
                self.transfinite_data.extend([transfinite_data[2]] * 4)
            else:
                self.transfinite_data = transfinite_data
        else:
            self.transfinite_data = transfinite_data
        self.volume_name = volume_name if volume_name is not None else 'V'
        self.surfaces_names = surfaces_names if surfaces_names is not None else [
            'NX', 'X', 'NY', 'Y', 'NZ', 'Z']
        self.transfinite_type = transfinite_type if transfinite_type is not None else 0
        self.rec = rec if rec is not None else 1
        self.trans = trans if trans is not None else 1
        self.points = list()
        self.curves_points = list()
        self.curves = list()
        self.surfaces = list()
        self.volumes = list()
        self.points_coordinates = list()
        self.curves_points_coordinates = list()
        self.bounding_box = None
        self.coordinates_evaluated = False
        if transform_data is None:
            transform_data = []
        elif isinstance(transform_data, list):
            if isinstance(transform_data[0], list):
                new_transform_data = []
                for td in transform_data:
                    if isinstance(td[0], list):
                        new_transform_data.append([np.array(td[0], dtype=float),
                                                   np.array(td[1], dtype=int)])
                    else:
                        new_transform_data.append([np.array(td, dtype=float),
                                                   np.ones(8, dtype=int)])
                transform_data = new_transform_data
            else:
                raise ValueError(f'invalid transform_data: {transform_data}')
        else:
            raise ValueError(f'invalid transform_data: {transform_data}')
        if curve_types is None:
            curve_types = np.zeros(12)
        if curve_data is None:
            curve_data = [[] for _ in range(12)]
        curve_data = [np.array(x, dtype=float) for x in curve_data]
        if point_data is not None:
            if len(point_data) == 3:
                half_lx = point_data[0] / 2.0
                half_ly = point_data[1] / 2.0
                half_lz = point_data[2] / 2.0
                lc = 1.
                point_data = np.array([
                    [half_lx, half_ly, -half_lz, lc],
                    [-half_lx, half_ly, -half_lz, lc],
                    [-half_lx, -half_ly, -half_lz, lc],
                    [half_lx, -half_ly, -half_lz, lc],
                    [half_lx, half_ly, half_lz, lc],
                    [-half_lx, half_ly, half_lz, lc],
                    [-half_lx, -half_ly, half_lz, lc],
                    [half_lx, -half_ly, half_lz, lc]
                ], dtype=float)
            elif len(point_data) == 4:
                half_lx = point_data[0] / 2.0
                half_ly = point_data[1] / 2.0
                half_lz = point_data[2] / 2.0
                lc = point_data[3]
                point_data = np.array([
                    [half_lx, half_ly, -half_lz, lc],
                    [-half_lx, half_ly, -half_lz, lc],
                    [-half_lx, -half_ly, -half_lz, lc],
                    [half_lx, -half_ly, -half_lz, lc],
                    [half_lx, half_ly, half_lz, lc],
                    [-half_lx, half_ly, half_lz, lc],
                    [-half_lx, -half_ly, half_lz, lc],
                    [half_lx, -half_ly, half_lz, lc]
                ], dtype=float)
            else:
                point_data = np.array(point_data, dtype=float)
            # Points
            # t0 = time.time()
            for td in transform_data:
                d, m = td
                mask = np.array([[not x for _ in range(point_data.shape[1] - 1)]
                                 for x in m], dtype=int)
                point_data[:, :3] = transform(point_data[:, :3], d, mask)
            for d in point_data:
                d[0] = round(d[0], registry.point_tol)
                d[1] = round(d[1], registry.point_tol)
                d[2] = round(d[2], registry.point_tol)
                cs = tuple(d[:3])  # x, y and z coordinates
                # print(cs)
                tag = registry.coord_point_map.get(cs, None)
                if tag is None:
                    tag = self.factory.addPoint(*d)
                    registry.coord_point_map[cs] = tag
                else:
                    pass
                    # print(tag, cs, len(registry.coord_point_map), 'point')
                self.points.append(tag)
            # print(f'points: {time.time() - t0}')
            # Curves points
            # t0 = time.time()
            for td in transform_data:
                d, m = td
                for i in range(len(curve_data)):
                    if len(curve_data[i]) > 0:
                        lps = self.curves_local_points[i]
                        mask = np.array([
                            [not m[lps[0]] * m[lps[1]]
                             for _ in range(curve_data[i].shape[1] - 1)]
                            for _ in range(curve_data[i].shape[0])], dtype=int)
                        curve_data[i][:, :3] = transform(curve_data[i][:, :3],
                                                         d, mask)
            for i in range(len(curve_data)):
                ps = list()
                for j in range(len(curve_data[i])):
                    curve_data[i][j][0] = round(curve_data[i][j][0],
                                                registry.point_tol)
                    curve_data[i][j][1] = round(curve_data[i][j][1],
                                                registry.point_tol)
                    curve_data[i][j][2] = round(curve_data[i][j][2],
                                                registry.point_tol)
                    cs = tuple(curve_data[i][j][:3])  # x, y and z coordinates
                    # print(cs)
                    tag = registry.coord_point_map.get(cs, None)
                    if tag is None:
                        tag = self.factory.addPoint(*curve_data[i][j])
                        registry.coord_point_map[cs] = tag
                    else:
                        pass
                        # print(tag, len(registry.coord_point_map), 'curve_point')
                    ps.append(tag)
                # print(ps, registry.coord_point_map)
                self.curves_points.append(ps)
            # print(self.points)
            # print(self.curves_points)
            # print(f'curves points: {time.time() - t0}')
            # Curves
            # t0 = time.time()
            for i in range(12):
                # FIXME Workaround for OCC factory
                ct = [curve_types[i]]
                if ct[0] == 0:
                    ps = [self.points[self.curves_local_points[i][0]],
                          self.points[self.curves_local_points[i][1]]]
                else:
                    ps = [self.points[self.curves_local_points[i][0]]] + \
                         self.curves_points[i] + \
                         [self.points[self.curves_local_points[i][1]]]
                psr = list(reversed(ps))
                # print(ct)
                # print(ps)
                # print(psr)
                cs1 = tuple(ct + ps)
                cs2 = tuple(ct + psr)
                # print(ct, ps)
                # print(cs2)
                tag = registry.curves.get(cs1, None)
                if tag is None:
                    if self.factory != gmsh.model.occ:
                        tag = self.add_curve[curve_types[i]](self, i)
                    else:
                        tag = self.add_curve[curve_types[i] + 6](self, i)
                    registry.curves[cs1] = tag
                    registry.curves[cs2] = -tag
                else:
                    pass
                    # print(tag, cs1, len(registry.curves), 'curve')
                self.curves.append(tag)
            # pprint(registry.curves)
            # print('curves: {}'.format(len(registry.curves)))
            # print(f'curves: {time.time() - t0}')
            # Surfaces
            # t0 = time.time()
            for i in range(6):
                cs = list(map(lambda x, y: y * self.curves[x],
                              self.surfaces_local_curves[i],
                              self.surfaces_local_curves_signs[i]))
                # print(cs)
                deq = deque(cs)
                # print(deq)
                css = []
                for _ in range(len(deq)):
                    deq.rotate(1)
                    css.append(tuple(deq))
                deqr = deque([-1 * x for x in reversed(cs)])
                for _ in range(len(deqr)):
                    deqr.rotate(1)
                    css.append(tuple(deqr))
                # print(css)
                tag = None
                for c in css:
                    tag = registry.surfaces.get(c, None)
                    if tag is not None:
                        break
                # t00 = time.time()
                if tag is None:
                    if self.factory == gmsh.model.geo:
                        tag = self.factory.addCurveLoop(
                            list(map(lambda x, y: y * self.curves[x],
                                     self.surfaces_local_curves[i],
                                     self.surfaces_local_curves_signs[i])))
                        tag = self.factory.addSurfaceFilling([tag])
                    else:
                        tag = self.factory.addCurveLoop(
                            list(map(lambda x: self.curves[x],
                                     self.surfaces_local_curves[i])))
                        tag = self.factory.addSurfaceFilling(tag)
                    for c in css:
                        registry.surfaces[c] = tag
                else:
                    pass
                    # print(set(registry.surfaces.values()))
                    # print(tag, css, len(registry.surfaces), 'surface')
                self.surfaces.append(tag)
                # print(f'surfaces2: {time.time() - t00}')
            # print('surfaces: {}'.format(len(registry.curves)))
            # print(len(self.surfaces))
            # print(f'surfaces: {time.time() - t0}')
            # Volume
            # t0 = time.time()
            if inner_volumes is None:
                # gs = volumes_groups_surfaces_registry(list(registry.volumes),
                #                                       registry.volumes)
                # print(gs)
                # print(len(gs))
                # FIXME always return tag = -1
                tag = self.factory.addSurfaceLoop(self.surfaces)
                tag = self.factory.addVolume([tag])
                registry.volumes[tag] = self.surfaces
            else:
                # gs = volumes_groups_surfaces(inner_volumes)
                gs = volumes_groups_surfaces_registry(inner_volumes,
                                                      registry.volumes)
                if self.factory == gmsh.model.occ:
                    # FIXME bug always return tag = -1 by default
                    out_sl = self.factory.addSurfaceLoop(self.surfaces, 1)
                    in_sls = list()
                    for i, g in enumerate(gs):
                        # FIXME bug always return tag = -1 by default
                        in_sls.append(self.factory.addSurfaceLoop(g, 2 + i))
                else:
                    out_sl = self.factory.addSurfaceLoop(self.surfaces)
                    flatten_in_sls = list(itertools.chain.from_iterable(gs))
                    in_sls = [self.factory.addSurfaceLoop(flatten_in_sls)]
                sls = list()
                sls.append(out_sl)
                sls += in_sls
                tag = self.factory.addVolume(sls)
                registry.volumes[tag] = sls
            self.volumes.append(tag)
            # print(f'volumes: {time.time() - t0}')
        else:
            if inner_volumes is not None:
                self.volumes = inner_volumes
        # pprint(registry.coord_point_map)

    def recombine(self):
        if self.rec:
            volumes_dim_tags = [(3, x) for x in self.volumes]
            surfaces_dim_tags = gmsh.model.getBoundary(volumes_dim_tags,
                                                       combined=False)
            for dt in surfaces_dim_tags:
                if self.factory == gmsh.model.occ:
                    gmsh.model.mesh.setRecombine(dt[0], dt[1])
                else:
                    self.factory.mesh.setRecombine(dt[0], dt[1])

    def smooth(self, dim, n):
        """
        Smooth mesh. Currently works only with dim == 2
        :param dim: Dimension
        :param n: Number of smooth iterations
        """
        if dim == 1:
            volumes_dim_tags = [(3, x) for x in self.volumes]
            surfaces_dim_tags = gmsh.model.getBoundary(volumes_dim_tags,
                                                       combined=False)
            curves_dim_tags = gmsh.model.getBoundary(surfaces_dim_tags,
                                                     combined=False)
            for dt in curves_dim_tags:
                gmsh.model.mesh.setSmoothing(dim, dt[1], n)
        elif dim == 2:
            volumes_dim_tags = [(3, x) for x in self.volumes]
            surfaces_dim_tags = gmsh.model.getBoundary(volumes_dim_tags,
                                                       combined=False)
            for dt in surfaces_dim_tags:
                gmsh.model.mesh.setSmoothing(dim, dt[1], n)
        elif dim == 3:
            for v in self.volumes:
                gmsh.model.mesh.setSmoothing(dim, v, n)

    def transfinite(self, transfinited_surfaces, transfinited_curves):
        """
        Transfinite primitive
        :param transfinited_surfaces: set() of already transfinite surfaces
        (workaround for double transfinite issue)
        :param transfinited_curves: set() of already transfinite curves
        (workaround for double transfinite issue)
        """
        if self.trans:
            result = False
            # Check
            check = False
            # print(len(self.volumes))
            if len(self.volumes) == 1:  # First
                volumes_dim_tags = [(3, x) for x in self.volumes]
                surfaces_dim_tags = gmsh.model.getBoundary(volumes_dim_tags,
                                                           combined=False)
                if len(surfaces_dim_tags) == 6:  # Second
                    points_dim_tags = gmsh.model.getBoundary(volumes_dim_tags,
                                                             combined=False,
                                                             recursive=True)
                    if len(points_dim_tags) == 8:  # Third
                        surfaces_points = []
                        for dim_tag in surfaces_dim_tags:
                            points_dim_tags = gmsh.model.getBoundary(
                                [(dim_tag[0], dim_tag[1])], combined=False,
                                recursive=True)
                            surfaces_points.append(
                                list(map(lambda x: x[1], points_dim_tags)))
                        is_4_points = True
                        for surface_points in surfaces_points:
                            if len(surface_points) != 4:  # Fourth
                                is_4_points = False
                                break
                        if is_4_points:
                            check = True
            # Transfinite
            if check:
                if self.transfinite_type == 0:
                    transfinite_surface_data = [1, 1, 1, 1, 1, 1]
                    transfinite_volume_data = [0]
                elif self.transfinite_type == 1:
                    transfinite_surface_data = [1, 1, 0, 0, 0, 0]
                    transfinite_volume_data = [1]
                elif self.transfinite_type == 2:
                    transfinite_surface_data = [0, 0, 0, 0, 1, 1]
                    transfinite_volume_data = [2]
                elif self.transfinite_type == 3:
                    transfinite_surface_data = [0, 0, 1, 1, 0, 0]
                    transfinite_volume_data = [3]
                else:
                    transfinite_surface_data = None
                    transfinite_volume_data = None
                if self.transfinite_data is not None:
                    for i, c in enumerate(self.curves):
                        if c not in transfinited_curves:
                            # FIXME Workaround for GEO factory
                            if self.factory != gmsh.model.geo:
                                transfinite_type = self.transfinite_data[i][1]
                            else:
                                transfinite_type = self.transfinite_data[i][
                                                       1] + 2
                            self.transfinite_curve[transfinite_type](self, i)
                            transfinited_curves.add(c)
                    if transfinite_surface_data is not None:
                        for i, s in enumerate(self.surfaces):
                            if s not in transfinited_surfaces:
                                # FIXME Workaround for GEO factory
                                if self.factory != gmsh.model.geo:
                                    transfinite_type = transfinite_surface_data[
                                        i]
                                else:
                                    transfinite_type = transfinite_surface_data[
                                                           i] + 4
                                self.transfinite_surface[transfinite_type](self,
                                                                           i)
                                transfinited_surfaces.add(s)
                        if transfinite_volume_data is not None:
                            for i in range(len(self.volumes)):
                                # FIXME Workaround for GEO factory
                                if self.factory != gmsh.model.geo:
                                    transfinite_type = transfinite_volume_data[
                                        i]
                                else:
                                    transfinite_type = transfinite_volume_data[
                                                           i] + 4
                                self.transfinite_volume[transfinite_type](self,
                                                                          i)
                    result = True
            # print(check, result)
            return result

    def evaluate_coordinates(self):
        if not self.coordinates_evaluated:
            for point in self.points:
                bb = gmsh.model.getBoundingBox(0, point)
                self.points_coordinates.append([bb[0], bb[1], bb[2]])
            for curve_points in self.curves_points:
                cs = []
                for point in curve_points:
                    bb = gmsh.model.getBoundingBox(0, point)
                    cs.append([bb[0], bb[1], bb[2]])
                self.curves_points_coordinates.append(cs)
            self.coordinates_evaluated = True

    def evaluate_bounding_box(self):
        if len(self.volumes) > 0:
            x_mins = []
            y_mins = []
            z_mins = []
            x_maxs = []
            y_maxs = []
            z_maxs = []
            volumes_dim_tags = [(3, x) for x in self.volumes]
            for dim_tag in volumes_dim_tags:
                x_min, y_min, z_min, x_max, y_max, z_max = \
                    gmsh.model.getBoundingBox(dim_tag[0], dim_tag[1])
                x_mins.append(x_min)
                y_mins.append(y_min)
                z_mins.append(z_min)
                x_maxs.append(x_max)
                y_maxs.append(y_max)
                z_maxs.append(z_max)
            self.bounding_box = (min(x_mins), min(y_mins), min(z_mins),
                                 max(x_maxs), max(y_maxs), max(z_maxs))
        else:
            self.bounding_box = (0, 0, 0, 0, 0, 0)

    def set_size(self, size):
        for v in self.volumes:
            volume_dim_tag = (3, v)
            points_dim_tags = gmsh.model.getBoundary([volume_dim_tag],
                                                     combined=False,
                                                     recursive=True)
            gmsh.model.mesh.setSize(points_dim_tags, size)

    def get_surfaces(self, combined=True):
        volumes_dim_tags = [(3, x) for x in self.volumes]
        surfaces_dim_tags = gmsh.model.getBoundary(volumes_dim_tags,
                                                   combined=combined)
        surfaces = [x[1] for x in surfaces_dim_tags]
        return surfaces

    curves_local_points = [
        [1, 0], [5, 4], [6, 7], [2, 3],
        [3, 0], [2, 1], [6, 5], [7, 4],
        [0, 4], [1, 5], [2, 6], [3, 7]
    ]

    surfaces_local_points = [
        [2, 6, 5, 1],  # NX
        [3, 7, 4, 0],  # X
        [2, 6, 7, 3],  # NY
        [1, 5, 4, 0],  # Y
        [3, 2, 1, 0],  # NZ
        [7, 6, 5, 4],  # Z
    ]

    surfaces_local_curves = [
        [5, 9, 6, 10],  # NX
        [4, 11, 7, 8],  # X
        # [3, 10, 2, 11],  # NY
        [11, 2, 10, 3],  # NY
        [0, 8, 1, 9],  # Y
        [0, 5, 3, 4],  # NZ
        [1, 7, 2, 6],  # Z
    ]

    surfaces_local_curves_signs = [
        [1, 1, -1, -1],  # NX
        [-1, 1, 1, -1],  # X
        # [-1, 1, 1, -1],  # NY
        [1, -1, -1, 1],  # NY
        [1, 1, -1, -1],  # Y
        [-1, -1, 1, 1],  # NZ
        [1, -1, -1, 1],  # Z
    ]

    transfinite_curve = {
        0: lambda self, i: gmsh.model.mesh.setTransfiniteCurve(
            abs(self.curves[i]),
            self.transfinite_data[i][0],
            "Progression",
            self.transfinite_data[i][2]
        ),
        1: lambda self, i: gmsh.model.mesh.setTransfiniteCurve(
            abs(self.curves[i]),
            self.transfinite_data[i][0],
            "Bump",
            self.transfinite_data[i][2]
        ),
        # FIXME Workaround for GEO factory
        2: lambda self, i: gmsh.model.geo.mesh.setTransfiniteCurve(
            self.curves[i],
            self.transfinite_data[i][0],
            "Progression",
            self.transfinite_data[i][2]
        ),
        3: lambda self, i: gmsh.model.geo.mesh.setTransfiniteCurve(
            self.curves[i],
            self.transfinite_data[i][0],
            "Bump",
            self.transfinite_data[i][2]
        )
    }

    transfinite_surface = {
        0: lambda self, i: gmsh.model.mesh.setTransfiniteSurface(
            self.surfaces[i],
            "Left",
            [self.points[x] for x in self.surfaces_local_points[i]]
        ),
        1: lambda self, i: gmsh.model.mesh.setTransfiniteSurface(
            self.surfaces[i],
            "Right",
            [self.points[x] for x in self.surfaces_local_points[i]]
        ),
        2: lambda self, i: gmsh.model.mesh.setTransfiniteSurface(
            self.surfaces[i],
            "AlternateLeft",
            [self.points[x] for x in self.surfaces_local_points[i]]
        ),
        3: lambda self, i: gmsh.model.mesh.setTransfiniteSurface(
            self.surfaces[i],
            "AlternateRight",
            [self.points[x] for x in self.surfaces_local_points[i]]
        ),
        # FIXME Workaround for GEO factory
        4: lambda self, i: gmsh.model.geo.mesh.setTransfiniteSurface(
            self.surfaces[i],
            "Left",
            [self.points[x] for x in self.surfaces_local_points[i]]
        ),
        5: lambda self, i: gmsh.model.geo.mesh.setTransfiniteSurface(
            self.surfaces[i],
            "Right",
            [self.points[x] for x in self.surfaces_local_points[i]]
        ),
        6: lambda self, i: gmsh.model.geo.mesh.setTransfiniteSurface(
            self.surfaces[i],
            "AlternateLeft",
            [self.points[x] for x in self.surfaces_local_points[i]]
        ),
        7: lambda self, i: gmsh.model.geo.mesh.setTransfiniteSurface(
            self.surfaces[i],
            "AlternateRight",
            [self.points[x] for x in self.surfaces_local_points[i]]
        )
    }

    transfinite_volume = {
        0: lambda self, i: gmsh.model.mesh.setTransfiniteVolume(
            self.volumes[i],
            [
                self.points[0], self.points[1], self.points[2], self.points[3],
                self.points[4], self.points[5], self.points[6], self.points[7]
            ]
        ),
        1: lambda self, i: gmsh.model.mesh.setTransfiniteVolume(
            self.volumes[i],
            [
                self.points[1], self.points[2], self.points[3], self.points[0],
                self.points[5], self.points[6], self.points[7], self.points[4]
            ]
        ),
        2: lambda self, i: gmsh.model.mesh.setTransfiniteVolume(
            self.volumes[i],
            [
                self.points[2], self.points[3], self.points[0], self.points[1],
                self.points[6], self.points[7], self.points[4], self.points[5]
            ]
        ),
        3: lambda self, i: gmsh.model.mesh.setTransfiniteVolume(
            self.volumes[i],
            [
                self.points[3], self.points[0], self.points[1], self.points[2],
                self.points[7], self.points[4], self.points[5], self.points[6]
            ]
        ),
        # FIXME Workaround for GEO factory
        4: lambda self, i: gmsh.model.geo.mesh.setTransfiniteVolume(
            self.volumes[i],
            [
                self.points[0], self.points[1], self.points[2], self.points[3],
                self.points[4], self.points[5], self.points[6], self.points[7]
            ]
        ),
        5: lambda self, i: gmsh.model.geo.mesh.setTransfiniteVolume(
            self.volumes[i],
            [
                self.points[1], self.points[2], self.points[3], self.points[0],
                self.points[5], self.points[6], self.points[7], self.points[4]
            ]
        ),
        6: lambda self, i: gmsh.model.geo.mesh.setTransfiniteVolume(
            self.volumes[i],
            [
                self.points[2], self.points[3], self.points[0], self.points[1],
                self.points[6], self.points[7], self.points[4], self.points[5]
            ]
        ),
        7: lambda self, i: gmsh.model.geo.mesh.setTransfiniteVolume(
            self.volumes[i],
            [
                self.points[3], self.points[0], self.points[1], self.points[2],
                self.points[7], self.points[4], self.points[5], self.points[6]
            ]
        )
    }

    add_curve = {
        0: lambda self, i: self.factory.addLine(
            self.points[self.curves_local_points[i][0]],
            self.points[self.curves_local_points[i][1]]
        ),
        1: lambda self, i: self.factory.addCircleArc(
            self.points[self.curves_local_points[i][0]],
            self.curves_points[i][0],
            self.points[self.curves_local_points[i][1]]
        ),
        2: lambda self, i: self.factory.addEllipseArc(
            self.points[self.curves_local_points[i][0]],
            self.curves_points[i][0],
            self.curves_points[i][1],
            self.points[self.curves_local_points[i][1]],
        ),
        3: lambda self, i: self.factory.addSpline(
            [self.points[self.curves_local_points[i][0]]] +
            self.curves_points[i] +
            [self.points[self.curves_local_points[i][1]]]
        ),
        4: lambda self, i: self.factory.addBSpline(
            [self.points[self.curves_local_points[i][0]]] +
            self.curves_points[i] +
            [self.points[self.curves_local_points[i][1]]]
        ),
        5: lambda self, i: self.factory.addBezier(
            [self.points[self.curves_local_points[i][0]]] +
            self.curves_points[i] +
            [self.points[self.curves_local_points[i][1]]]
        ),
        6: lambda self, i: self.factory.addLine(
            self.points[self.curves_local_points[i][0]],
            self.points[self.curves_local_points[i][1]]
        ),
        7: lambda self, i: self.factory.addCircleArc(
            self.points[self.curves_local_points[i][0]],
            self.curves_points[i][0],
            self.points[self.curves_local_points[i][1]]
        ),
        # FIXME Workaround for OCC factory: addEllipseArc -> addCircleArc
        8: lambda self, i: self.factory.addCircleArc(
            self.points[self.curves_local_points[i][0]],
            self.curves_points[i][0],
            self.points[self.curves_local_points[i][1]],
        ),
        9: lambda self, i: self.factory.addSpline(
            [self.points[self.curves_local_points[i][0]]] +
            self.curves_points[i] +
            [self.points[self.curves_local_points[i][1]]]
        ),
        10: lambda self, i: self.factory.addBSpline(
            [self.points[self.curves_local_points[i][0]]] +
            self.curves_points[i] +
            [self.points[self.curves_local_points[i][1]]]
        ),
        11: lambda self, i: self.factory.addBezier(
            [self.points[self.curves_local_points[i][0]]] +
            self.curves_points[i] +
            [self.points[self.curves_local_points[i][1]]]
        )
    }


def rotation_matrix(axis, theta):
    """
    Return the rotation matrix associated with counterclockwise rotation about
    the given axis by theta radians.
    """
    axis = np.array(axis)
    axis = axis / np.sqrt(np.dot(axis, axis))
    a = np.cos(np.radians(theta / 2.0))
    b, c, d = -axis * np.sin(np.radians(theta / 2.0))
    aa, bb, cc, dd = a * a, b * b, c * c, d * d
    bc, ad, ac, ab, bd, cd = b * c, a * d, a * c, a * b, b * d, c * d
    return np.array([[aa + bb - cc - dd, 2 * (bc + ad), 2 * (bd - ac)],
                     [2 * (bc - ad), aa + cc - bb - dd, 2 * (cd + ab)],
                     [2 * (bd + ac), 2 * (cd - ab), aa + dd - bb - cc]])


def transform(ps, data, mask):
    mps = np.ma.array(ps, mask=mask)
    if len(data) == 7:  # rotation around dir by angle relative to origin
        origin, direction, angle = data[:3], data[3:6], data[6]
        m = rotation_matrix(direction, angle)
        lps = mps - origin  # local coordinates relative to origin
        mps = np.ma.dot(lps, m.T)
        mps = np.ma.add(mps, origin)
    elif len(data) == 4:  # rotation about dir by angle relative to (0, 0, 0)
        direction, angle = data[:3], data[3]
        m = rotation_matrix(direction, angle)
        mps = np.ma.dot(mps, m.T)
    else:  # displacement
        displacement = data[:3]
        mps = np.ma.add(mps, displacement)
    ps = mps.filled(ps)
    return ps
