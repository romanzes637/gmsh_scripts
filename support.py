import os
import math
from pprint import pprint

import numpy as np
import gmsh


# FIXME Bug with this approach:
# File "/share/home/butovr/gmsh_scripts/support.py", line 14,
# in get_volume_points_edges_data
# surfaces_dim_tags = gmsh.model.getBoundary([[3, volume]])
# File "/home/butovr/Programs/gmsh/api/gmsh.py", line 517,
# in getBoundary ierr.value)
# ValueError: ('gmshModelGetBoundary


def get_volume_points_edges_data(volume):
    """
    Return volume points edges data.
    For point's characteristic length (lc) auto setting.
    :param int volume: volume index
    :return:
    {point: (n_edges, edges_min_length, edges_max_length, edges_avg_length)}
    :rtype: dict
    """
    # Get volume edges
    volume_dim_tag = (3, volume)
    surfaces_dim_tags = gmsh.model.getBoundary([volume_dim_tag])
    edges = set()
    for sdt in surfaces_dim_tags:
        curves_dim_tags = gmsh.model.getBoundary([sdt])
        for cdt in curves_dim_tags:
            edges.add(abs(cdt[1]))
    # Get volume points
    points_dim_tags = gmsh.model.getBoundary([volume_dim_tag], recursive=True)
    points = tuple(x[1] for x in points_dim_tags)
    # Get points edges and edges points
    points_edges = {x: set() for x in points}
    edges_points = dict()
    for e in edges:
        edge_dim_tag = (1, e)
        points_dim_tags = gmsh.model.getBoundary([edge_dim_tag])
        edges_points[e] = tuple(x[1] for x in points_dim_tags)
        for p in edges_points[e]:
            points_edges[p].add(e)
    # Calculate edges lengths
    edges_lengths = get_volume_edges_lengths(volume)
    # Prepare the output
    points_edges_data = dict()
    for p in points:
        lengths = list()
        for e in points_edges[p]:
            lengths.append(edges_lengths[e])
        n_edges = len(lengths)
        min_length = min(lengths)
        max_length = max(lengths)
        mean_length = sum(lengths) / n_edges
        points_edges_data[p] = (
            n_edges,
            min_length,
            max_length,
            mean_length
        )
        # print(volume)
        # pprint(points_edges)
        # pprint(edges_points)
    return points_edges_data


def get_volume_edges_lengths(volume):
    """
    Return volume edges straight (start point to end point, not curved) lengths.
    :param volume: volume index
    :return: dictionary (edge: edge_length)
    """
    # Get volume edges
    volume_dim_tag = (3, volume)
    surfaces_dim_tags = gmsh.model.getBoundary([volume_dim_tag])
    edges = set()
    for sdt in surfaces_dim_tags:
        edges_dim_tags = gmsh.model.getBoundary([sdt])
        for edt in edges_dim_tags:
            edges.add(abs(edt[1]))
    # Get edges points
    edges_points = dict()
    for e in edges:
        edge_dim_tag = (1, e)
        points_dim_tags = gmsh.model.getBoundary([edge_dim_tag])
        edges_points[e] = [x[1] for x in points_dim_tags]
    # Calculate edges lengths
    edges_lengths = dict()
    for e in edges:
        ps = edges_points[e]
        bb0 = gmsh.model.getBoundingBox(0, ps[0])
        bb1 = gmsh.model.getBoundingBox(0, ps[1])
        cs0 = [bb0[0], bb0[1], bb0[2]]
        cs1 = [bb1[0], bb1[1], bb1[2]]
        vector = [cs1[0] - cs0[0], cs1[1] - cs0[1], cs1[2] - cs0[2]]
        length = math.sqrt(
            vector[0] * vector[0] + vector[1] * vector[1] + vector[2] * vector[
                2])
        edges_lengths[e] = length
    return edges_lengths


def get_points_coordinates():
    points_coordinates = dict()
    points_dim_tags = gmsh.model.getEntities(0)
    for dt in points_dim_tags:
        point = dt[1]
        bb = gmsh.model.getBoundingBox(0, point)
        coordinates = [bb[0], bb[1], bb[2]]
        points_coordinates[point] = coordinates
    return points_coordinates


def get_edges_points():
    edges_points = dict()
    edges_dim_tags = gmsh.model.getEntities(1)
    for dt in edges_dim_tags:
        points_dim_tags = gmsh.model.getBoundary([dt], combined=False)
        edge = dt[1]
        points = [x[1] for x in points_dim_tags]
        edges_points[edge] = points
    return edges_points


def get_surfaces_edges():
    surfaces_edges = dict()
    surfaces_dim_tags = gmsh.model.getEntities(2)
    for dt in surfaces_dim_tags:
        edges_dim_tags = gmsh.model.getBoundary([dt], combined=False)
        surface = dt[1]
        edges = [x[1] for x in edges_dim_tags]
        surfaces_edges[surface] = edges
    return surfaces_edges


def get_volumes_surfaces():
    volumes_surfaces = dict()
    volumes_dim_tags = gmsh.model.getEntities(3)
    for dt in volumes_dim_tags:
        surfaces_dim_tags = gmsh.model.getBoundary([dt], combined=False)
        volume = dt[1]
        surfaces = [x[1] for x in surfaces_dim_tags]
        volumes_surfaces[volume] = surfaces
    return volumes_surfaces


def get_geometry():
    geo = dict()
    geo['volumes'] = get_volumes_surfaces()
    geo['surfaces'] = get_surfaces_edges()
    geo['edges'] = get_edges_points()
    geo['points'] = get_points_coordinates()
    return geo


def get_volumes_geometry():
    volumes_surfaces = dict()
    surfaces_edges = dict()
    edges_points = dict()
    points_coordinates = dict()
    volumes_dim_tags = gmsh.model.getEntities(3)
    # Volumes
    surfaces = set()
    for dt in volumes_dim_tags:
        surfaces_dim_tags = gmsh.model.getBoundary([dt], combined=False)
        volume = dt[1]
        volume_surfaces = [x[1] for x in surfaces_dim_tags]
        volumes_surfaces[volume] = volume_surfaces
        surfaces.update(set(volume_surfaces))
    # Surfaces
    edges = set()
    for s in surfaces:
        dim_tag = (2, s)
        edges_dim_tags = gmsh.model.getBoundary([dim_tag], combined=False)
        surface_edges = [x[1] for x in edges_dim_tags]
        surfaces_edges[s] = surface_edges
        abs_surfaces_edges = [abs(x) for x in surface_edges]
        edges.update(set(abs_surfaces_edges))
    # Edges
    points = set()
    for e in edges:
        dim_tag = (1, e)
        points_dim_tags = gmsh.model.getBoundary([dim_tag], combined=False)
        edge_points = [x[1] for x in points_dim_tags]
        edges_points[e] = edge_points
        points.update(set(edge_points))
    # Points
    for p in points:
        bb = gmsh.model.getBoundingBox(0, p)
        coordinates = [bb[0], bb[1], bb[2]]
        points_coordinates[p] = coordinates
    # Geometry
    geo = dict()
    geo['volumes'] = volumes_surfaces
    geo['surfaces'] = surfaces_edges
    geo['edges'] = edges_points
    geo['points'] = points_coordinates
    return geo


def check_geometry(geometry, check_duplicates=False):
    out = dict()
    # Points
    out['unused_points'] = dict()
    used_points = set()
    out['empty_points'] = dict()
    # Edges
    out['unused_edges'] = dict()
    used_edges = set()
    out['empty_edges'] = dict()
    out['one_edges'] = dict()
    out['loop_edges'] = dict()
    # Surfaces
    out['unused_surfaces'] = dict()
    used_surfaces = set()
    out['empty_surfaces'] = dict()
    out['one_surfaces'] = dict()
    out['loop_surfaces'] = dict()
    # Volumes
    out['loop_volumes'] = dict()
    out['empty_volumes'] = dict()
    out['one_volumes'] = dict()
    if check_duplicates:
        out['duplicate_points'] = dict()
        out['duplicate_edges'] = dict()
        out['duplicate_surfaces'] = dict()
        out['duplicate_volumes'] = dict()
    for volume, surfaces in geometry['volumes'].items():
        if len(surfaces) == 0:
            out['empty_volumes'][volume] = surfaces
        elif len(surfaces) == 1:
            out['one_volumes'][volume] = surfaces
        if len(surfaces) != len(set(surfaces)):
            out['loop_volumes'][volume] = surfaces
        used_surfaces.update(surfaces)
        if check_duplicates:
            for volume2, surfaces2 in geometry['volumes'].items():
                if surfaces2 == surfaces:
                    if volume2 != volume:
                        out['duplicate_volumes'].setdefault(volume2, set()).add(
                            volume)
                        out['duplicate_volumes'].setdefault(volume, set()).add(
                            volume2)
    for surface, edges in geometry['surfaces'].items():
        if len(edges) == 0:
            out['empty_surfaces'][surface] = edges
        elif len(edges) == 1:
            out['one_surfaces'][surface] = edges
        if len(edges) != len(set(edges)):
            out['loop_surfaces'][surface] = edges
        abs_edges = [abs(x) for x in edges]
        used_edges.update(abs_edges)
        if surface not in used_surfaces:
            out['unused_surfaces'][surface] = edges
        if check_duplicates:
            for surface2, edges2 in geometry['surfaces'].items():
                if edges2 == edges:
                    if surface2 != surface:
                        out['duplicate_surfaces'].setdefault(surface2,
                                                             set()).add(surface)
                        out['duplicate_surfaces'].setdefault(surface,
                                                             set()).add(
                            surface2)
    for edge, points in geometry['edges'].items():
        if len(points) == 0:
            out['empty_edges'][edge] = points
        elif len(points) == 1:
            out['one_edges'][edge] = points
        if len(points) != len(set(points)):
            out['loop_edges'][edge] = points
        used_points.update(points)
        if edge not in used_edges:
            out['unused_edges'][edge] = points
        if check_duplicates:
            for edge2, points2 in geometry['edges'].items():
                if points2 == points:
                    if edge2 != edge:
                        out['duplicate_edges'].setdefault(edge2, set()).add(
                            edge)
                        out['duplicate_edges'].setdefault(edge, set()).add(
                            edge2)
    for point, coordinates in geometry['points'].items():
        if len(coordinates) == 0:
            out['empty_points'][point] = coordinates
        if point not in used_points:
            out['unused_points'][point] = coordinates
        if check_duplicates:
            for point2, coordinates2 in geometry['points'].items():
                tolerance = gmsh.option.getNumber("Geometry.Tolerance")
                duplicates = list()
                n_coordinates = len(coordinates2)
                for i in range(n_coordinates):
                    difference = abs(coordinates2[i] - coordinates[i])
                    if difference < tolerance:
                        duplicates.append(1)
                    else:
                        duplicates.append(0)
                if sum(duplicates) == n_coordinates:
                    if point2 != point:
                        out['duplicate_points'].setdefault(point2, set()).add(
                            point)
                        out['duplicate_points'].setdefault(point, set()).add(
                            point2)
    for k, v in out.items():
        result = True if len(v) == 0 else False
        answer = 'OK' if result else 'BAD'
        print('{} {}'.format(k, answer))
        if not result:
            pprint(v)
    return out


def initialize_geometry(factory, geometry):
    # Geometry with new indices
    new_geo = dict()
    new_geo['volumes'] = dict()
    new_geo['surfaces'] = dict()
    new_geo['edges'] = dict()
    new_geo['points'] = dict()
    # Old to new indices maps
    old_points_to_new_points = dict()
    old_edges_to_new_edges = dict()
    old_surfaces_to_new_surfaces = dict()
    old_volumes_to_new_volumes = dict()
    print('Initialize Points')
    for i, (k, v) in enumerate(geometry['points'].items()):
        print('Point {} {}/{}'.format(k, i + 1, len(geometry['points'])))
        old_tag = k
        new_tag = factory.addPoint(v[0], v[1], v[2])
        old_points_to_new_points[old_tag] = new_tag
        new_geo['points'][new_tag] = v
    print('Initialize Edges')
    for i, (k, v) in enumerate(geometry['edges'].items()):
        print('Edge {} {}/{}'.format(k, i + 1, len(geometry['edges'])))
        old_points = v
        new_points = [old_points_to_new_points[x] for x in old_points]
        old_tag = k
        new_tag = factory.addLine(new_points[0], new_points[1])
        old_edges_to_new_edges[old_tag] = new_tag
        new_geo['edges'][new_tag] = new_points
    print('Initialize Surfaces')
    for i, (k, v) in enumerate(geometry['surfaces'].items()):
        print('Surface {} {}/{}'.format(k, i + 1, len(geometry['surfaces'])))
        old_edges = v
        old_tag = k
        new_edges = [math.copysign(1, x) * old_edges_to_new_edges[abs(x)] for x
                     in old_edges]
        if factory == gmsh.model.occ:
            abs_new_edges = [abs(x) for x in new_edges]
            # curve_loop_tag = factory.addCurveLoop(abs_new_edges)
            # FIXME signed edges doesn't work
            curve_loop_tag = factory.addWire(
                abs_new_edges)  # FIXME signed edges doesn't work
            new_tag = factory.addSurfaceFilling(curve_loop_tag)
        else:
            curve_loop_tag = factory.addCurveLoop(new_edges)
            new_tag = factory.addSurfaceFilling([curve_loop_tag])
        old_surfaces_to_new_surfaces[old_tag] = new_tag
        new_geo['surfaces'][new_tag] = new_edges
    print('Initialize Volumes')
    for i, (k, v) in enumerate(geometry['volumes'].items()):
        print('Volume {} {}/{}'.format(k, i + 1, len(geometry['volumes'])))
        old_surfaces = v
        new_surfaces = [old_surfaces_to_new_surfaces[x] for x in old_surfaces]
        old_tag = k
        surface_loop_tag = factory.addSurfaceLoop(
            new_surfaces)  # FIXME always return -1
        new_tag = factory.addVolume([surface_loop_tag])
        old_volumes_to_new_volumes[old_tag] = new_tag
        new_geo['volumes'][new_tag] = new_surfaces
    return new_geo


def auto_points_sizes(c=1.0):
    points_sizes = dict()
    volumes_dim_tags = gmsh.model.getEntities(3)
    for vdt in volumes_dim_tags:
        # Evaluate new_size
        ps_es_data = get_volume_points_edges_data(vdt[1])
        min_length = list()
        for k, v in ps_es_data.items():
            min_length.append(c * v[1])
        new_size = min(min_length)
        # Update sizes
        for k, v in ps_es_data.items():
            update_size = True
            old_size = points_sizes.get(k)
            if old_size is not None:
                if new_size > old_size:
                    update_size = False
            if update_size:
                points_sizes[k] = new_size
                point_dim_tag = (0, k)
                gmsh.model.mesh.setSize([point_dim_tag], new_size)
    return points_sizes


def auto_boundary_points_sizes(c=1.0):
    volumes_dim_tags = gmsh.model.getEntities(3)
    # Get boundary surfaces
    surfaces_dim_tags = gmsh.model.getBoundary(volumes_dim_tags)
    # Get boundary surfaces edges
    edges_dim_tags = gmsh.model.getBoundary(surfaces_dim_tags, combined=False,
                                            oriented=False)
    # Points' edges and edges
    points_edges = dict()
    edges = dict()
    for dim_tag in edges_dim_tags:
        dim, tag = dim_tag
        points_dim_tags = gmsh.model.getBoundary([dim_tag])
        edges[tag] = tuple(x[1] for x in points_dim_tags)
        for p in edges[tag]:
            points_edges.setdefault(p, set()).add(tag)
    # Calculate edges lengths
    edges_lengths = dict()
    for edge, points in edges.items():
        bb0 = gmsh.model.getBoundingBox(0, points[0])
        bb1 = gmsh.model.getBoundingBox(0, points[1])
        cs0 = [bb0[0], bb0[1], bb0[2]]
        cs1 = [bb1[0], bb1[1], bb1[2]]
        vector = [cs1[0] - cs0[0], cs1[1] - cs0[1], cs1[2] - cs0[2]]
        length = math.sqrt(
            vector[0] * vector[0] + vector[1] * vector[1] + vector[2] *
            vector[2])
        edges_lengths[edge] = length
    points_sizes = dict()
    for point, edges in points_edges.items():
        lengths = [edges_lengths[x] for x in edges]
        points_sizes[point] = min(lengths) * c
    print(points_sizes)
    for point, size in points_sizes.items():
        gmsh.model.mesh.setSize([(0, point)], size)


def auto_boundary_points_sizes_min_edge_in_surface(c=1.0):
    points_sizes = dict()
    volumes_dim_tags = gmsh.model.getEntities(3)
    # Get boundary surfaces
    surfaces_dim_tags = gmsh.model.getBoundary(volumes_dim_tags)
    for surface_dim_tag in surfaces_dim_tags:
        # Get boundary surface edges
        edges_dim_tags = gmsh.model.getBoundary([surface_dim_tag],
                                                combined=False,
                                                oriented=False)
        # Edges and points' edges
        edges = dict()
        points_edges = dict()
        for dim_tag in edges_dim_tags:
            dim, tag = dim_tag
            points_dim_tags = gmsh.model.getBoundary([dim_tag])
            edges[tag] = tuple(x[1] for x in points_dim_tags)
            for p in edges[tag]:
                points_edges.setdefault(p, set()).add(tag)
        # Calculate edges lengths
        edges_lengths = dict()
        for edge, points in edges.items():
            bb0 = gmsh.model.getBoundingBox(0, points[0])
            bb1 = gmsh.model.getBoundingBox(0, points[1])
            cs0 = [bb0[0], bb0[1], bb0[2]]
            cs1 = [bb1[0], bb1[1], bb1[2]]
            vector = [cs1[0] - cs0[0], cs1[1] - cs0[1], cs1[2] - cs0[2]]
            length = math.sqrt(
                vector[0] * vector[0] + vector[1] * vector[1] + vector[2] *
                vector[2])
            edges_lengths[edge] = length
        for point, edges in points_edges.items():
            lengths = [edges_lengths[x] for x in edges]
            new_size = min(lengths) * c
            old_size = points_sizes.get(point, None)
            if old_size is not None:
                points_sizes[point] = min(new_size, old_size)
            else:
                points_sizes[point] = new_size
    for point, size in points_sizes.items():
        gmsh.model.mesh.setSize([(0, point)], size)


def auto_primitive_points_sizes_min_curve(primitive_obj, points_sizes_dict,
                                          c=1.0):
    for v in primitive_obj.volumes:
        ps_cs_data = get_volume_points_edges_data(v)
        for pd in ps_cs_data:
            p = pd[0]  # point index
            size = c * pd[1]  # c * min curve length
            old_size = points_sizes_dict.get(p)
            if old_size is not None:
                if size < old_size:
                    points_sizes_dict[p] = size
                    gmsh.model.mesh.setSize([(0, p)], size)
            else:
                points_sizes_dict[p] = size
                gmsh.model.mesh.setSize([(0, p)], size)


def auto_primitive_points_sizes_min_curve_in_volume(primitive_obj, points_sizes,
                                                    c=1.0):
    for volume in primitive_obj.volumes:
        # Evaluate new_size
        ps_es_data = get_volume_points_edges_data(volume)
        min_length = list()
        for k, v in ps_es_data.items():
            min_length.append(c * v[1])
        new_size = min(min_length)
        # Update sizes
        for k, v in ps_es_data.items():
            update_size = True
            old_size = points_sizes.get(k)
            if old_size is not None:
                if new_size > old_size:
                    update_size = False
            if update_size:
                points_sizes[k] = new_size
                point_dim_tag = (0, k)
                gmsh.model.mesh.setSize([point_dim_tag], new_size)


def auto_complex_points_sizes_min_curve(complex_obj, points_sizes_dict, k=1.0):
    for p in complex_obj.primitives:
        auto_primitive_points_sizes_min_curve(p, points_sizes_dict, k)


def auto_complex_points_sizes_min_curve_in_volume(complex_obj,
                                                  points_sizes_dict, k=1.0):
    for p in complex_obj.primitives:
        auto_primitive_points_sizes_min_curve_in_volume(p, points_sizes_dict, k)


def set_boundary_points_sizes(size):
    volumes_dim_tags = gmsh.model.getEntities(3)
    points_dim_tags = gmsh.model.getBoundary(volumes_dim_tags, recursive=True)
    gmsh.model.mesh.setSize(points_dim_tags, size)


def set_points_sizes(size):
    points_dim_tags = gmsh.model.getEntities(0)
    gmsh.model.mesh.setSize(points_dim_tags, size)


def get_bounding_box_by_boundary_surfaces(boundary_surfaces):
    points_x = dict()
    points_y = dict()
    points_z = dict()
    surfaces_dim_tags = [(2, x) for x in boundary_surfaces]
    points_dim_tags = gmsh.model.getBoundary(surfaces_dim_tags, combined=False,
                                             recursive=True)
    for dt in points_dim_tags:
        dim = dt[0]
        p = dt[1]
        bb = gmsh.model.getBoundingBox(dim, p)
        points_x[p] = bb[0]
        points_y[p] = bb[1]
        points_z[p] = bb[2]
    pprint(points_x)
    pprint(points_y)
    pprint(points_z)
    p_max_x = max(points_x, key=(lambda x: points_x[x]))
    p_min_x = min(points_x, key=(lambda x: points_x[x]))
    p_max_y = max(points_y, key=(lambda x: points_y[x]))
    p_min_y = min(points_y, key=(lambda x: points_y[x]))
    p_max_z = max(points_z, key=(lambda x: points_z[x]))
    p_min_z = min(points_z, key=(lambda x: points_z[x]))
    max_x = points_x[p_max_x]
    min_x = points_x[p_min_x]
    max_y = points_y[p_max_y]
    min_y = points_y[p_min_y]
    max_z = points_z[p_max_z]
    min_z = points_z[p_min_z]
    return min_x, min_y, min_z, max_x, max_y, max_z


def get_boundary_surfaces():
    volumes_dim_tags = gmsh.model.getEntities(3)
    surfaces_dim_tags = gmsh.model.getBoundary(volumes_dim_tags)
    surfaces = [x[1] for x in surfaces_dim_tags]
    return surfaces


def get_interior_surfaces():
    ss = set(x[1] for x in gmsh.model.getEntities(2))
    bss = set(x[1] for x in gmsh.model.getBoundary(gmsh.model.getEntities(3)))
    iss = ss - bss
    return iss


def boundary_surfaces_to_six_side_groups():
    """
    Try group boundary surfaces them into 6 groups by sides of cuboid:
    NX, NY, NZ, X, Y, Z
    :return: dict surfaces_groups
    """
    boundary_surfaces = get_boundary_surfaces()
    surfaces_groups = {
        'NX': list(),
        'NY': list(),
        'NZ': list(),
        'X': list(),
        'Y': list(),
        'Z': list(),
    }
    # Points coordinates
    points_x = dict()
    points_y = dict()
    points_z = dict()
    surfaces_dim_tags = [(2, x) for x in boundary_surfaces]
    points_dim_tags = gmsh.model.getBoundary(surfaces_dim_tags, combined=False,
                                             recursive=True)
    for dt in points_dim_tags:
        dim = dt[0]
        p = dt[1]
        bb = gmsh.model.getBoundingBox(dim, p)
        points_x[p] = bb[0]
        points_y[p] = bb[1]
        points_z[p] = bb[2]
    # Evaluate bounding box
    p_max_x = max(points_x, key=(lambda x: points_x[x]))
    p_min_x = min(points_x, key=(lambda x: points_x[x]))
    p_max_y = max(points_y, key=(lambda x: points_y[x]))
    p_min_y = min(points_y, key=(lambda x: points_y[x]))
    p_max_z = max(points_z, key=(lambda x: points_z[x]))
    p_min_z = min(points_z, key=(lambda x: points_z[x]))
    max_x = points_x[p_max_x]
    min_x = points_x[p_min_x]
    max_y = points_y[p_max_y]
    min_y = points_y[p_min_y]
    max_z = points_z[p_max_z]
    min_z = points_z[p_min_z]
    # Check surfaces for parallel to NX, NY, NZ, X, Y, Z
    for s in boundary_surfaces:
        surface_dim_tag = (2, s)
        points_dim_tags = gmsh.model.getBoundary([surface_dim_tag],
                                                 combined=False, recursive=True)
        s_points_xs = list()
        s_points_ys = list()
        s_points_zs = list()
        for dt in points_dim_tags:
            p = dt[1]
            s_points_xs.append(points_x[p])
            s_points_ys.append(points_y[p])
            s_points_zs.append(points_z[p])
        tol = gmsh.option.getNumber("Geometry.Tolerance")
        done = False
        while not done:
            # Check X
            s_min_x = min(s_points_xs)
            s_max_x = max(s_points_xs)
            if abs(s_max_x - s_min_x) < tol:
                # Check X or NX
                while not done:
                    if abs(s_min_x - min_x) < tol:
                        surfaces_groups['NX'].append(s)
                        done = True
                    elif abs(s_max_x - max_x) < tol:
                        surfaces_groups['X'].append(s)
                        done = True
                    else:
                        tol *= 10
                break
            # Check Y
            s_min_y = min(s_points_ys)
            s_max_y = max(s_points_ys)
            if abs(s_max_y - s_min_y) < tol:
                # Check Y or NY
                while not done:
                    if abs(s_min_y - min_y) < tol:
                        surfaces_groups['NY'].append(s)
                        done = True
                    elif abs(s_max_y - max_y) < tol:
                        surfaces_groups['Y'].append(s)
                        done = True
                    else:
                        tol *= 10
                break
            # Check Z
            s_min_z = min(s_points_zs)
            s_max_z = max(s_points_zs)
            if abs(s_max_z - s_min_z) < tol:
                # Check Z or NZ
                while not done:
                    if abs(s_min_z - min_z) < tol:
                        surfaces_groups['NZ'].append(s)
                        done = True
                    elif abs(s_max_z - max_z) < tol:
                        surfaces_groups['Z'].append(s)
                        done = True
                    else:
                        tol *= 10
                break
            tol *= 10
    return surfaces_groups


def physical_surfaces(name_surfaces_map):
    for name, surfaces in name_surfaces_map.items():
        tag = gmsh.model.addPhysicalGroup(2, surfaces)
        gmsh.model.setPhysicalName(2, tag, name)


def volumes_surfaces_to_volumes_groups_surfaces(volumes_surfaces):
    """
    For Environment object. For each distinct inner volume in Environment
    should exist the surface loop. If inner volumes touch each other they unite
    to volume group and have common surface loop.
    :param volumes_surfaces: [[v1_s1, ..., v1_si], ..., [vj_s1, ..., vj_si]]
    :return: volumes_groups_surfaces [[vg1_s1, ..., vg1_si], ...]
    """
    vs_indexes = set(range(len(volumes_surfaces)))
    # gs = list()
    # gs_out = list()
    # for i, ss in enumerate(volumes_surfaces):
    #     new_group = True
    #     for j, g in enumerate(gs):
    #         for s in ss:
    #             if s in g:
    #                 gs[j].update(ss)
    #                 gs_out[j].symmetric_difference_update(ss)
    #                 new_group = False
    #     if new_group:
    #         gs.append(set(ss))
    #         gs_out.append(set(ss))
    # print(gs)
    # if len(gs) > 1:
    #     print(gs[0].intersection(gs[1]))
    # if len(gs) > 2:
    #     print(gs[1].intersection(gs[2]))
    #     print(gs[2].intersection(gs[0]))
    while len(vs_indexes) != 0:
        current_index = list(vs_indexes)[0]
        current_surfaces = set(volumes_surfaces[current_index])
        other_indexes = {x for x in vs_indexes if x != current_index}
        is_intersection = True
        while is_intersection:
            is_intersection = False
            new_other_indexes = {x for x in other_indexes}
            for i in other_indexes:
                surfaces_i = set(volumes_surfaces[i])
                intersection = current_surfaces.intersection(surfaces_i)
                if len(intersection) > 0:
                    is_intersection = True
                    # Update current
                    current_surfaces.symmetric_difference_update(surfaces_i)
                    new_other_indexes.remove(i)
                    vs_indexes.remove(i)
                    # Update global
                    volumes_surfaces[current_index] = list(current_surfaces)
                    volumes_surfaces[i] = list()
            other_indexes = new_other_indexes
        vs_indexes.remove(current_index)
    volumes_surfaces_groups = [x for x in volumes_surfaces if len(x) != 0]
    return volumes_surfaces_groups


def auto_volumes_groups_surfaces():
    volumes_dim_tags = gmsh.model.getEntities(3)
    volumes_surfaces = list()
    for vdt in volumes_dim_tags:
        surfaces_dim_tags = gmsh.model.getBoundary([vdt], oriented=False)
        ss = [x[1] for x in surfaces_dim_tags]
        volumes_surfaces.append(ss)
    return volumes_surfaces_to_volumes_groups_surfaces(volumes_surfaces)


def volumes_groups_surfaces(volumes):
    volumes_dim_tags = [(3, x) for x in volumes]
    volumes_surfaces = list()
    for vdt in volumes_dim_tags:
        surfaces_dim_tags = gmsh.model.getBoundary([vdt], oriented=False)
        ss = [x[1] for x in surfaces_dim_tags]
        volumes_surfaces.append(ss)
    return volumes_surfaces_to_volumes_groups_surfaces(volumes_surfaces)


def volumes_groups_surfaces_registry(volumes, registry_volumes):
    volumes_surfaces = [registry_volumes[x] for x in volumes]
    return volumes_surfaces_to_volumes_groups_surfaces(volumes_surfaces)


def get_volume_composition(volume):
    volume_dt = (3, volume)
    points_dts = gmsh.model.getBoundary([volume_dt], recursive=True)
    n_points = len(points_dts)
    surfaces_dts = gmsh.model.getBoundary([volume_dt])
    n_surfaces = len(surfaces_dts)
    edges = set()
    for surface_dt in surfaces_dts:
        edges_dts = gmsh.model.getBoundary([surface_dt], oriented=False)
        for edge_dt in edges_dts:
            edge = edge_dt[1]
            edges.add(edge)
    n_edges = len(edges)
    return n_points, n_surfaces, n_edges


def is_cuboid(volume):
    result = False
    n_points = 8
    n_surfaces = 6
    n_edges = 12
    n_edges_per_surface = 4  # FIXME needs to check this?
    volume_dt = (3, volume)
    points_dts = gmsh.model.getBoundary([volume_dt], recursive=True)
    if len(points_dts) == n_points:
        surfaces_dts = gmsh.model.getBoundary([volume_dt])
        if len(surfaces_dts) == n_surfaces:
            edges = set()
            is_n_edges_per_surface = True
            for surface_dt in surfaces_dts:
                edges_dts = gmsh.model.getBoundary([surface_dt])
                if len(edges_dts) == n_edges_per_surface:
                    for edge_dt in edges_dts:
                        edge = abs(edge_dt[1])
                        edges.add(edge)
                else:
                    is_n_edges_per_surface = False
                    break
            if len(edges) == n_edges and is_n_edges_per_surface:
                result = True
    return result


def structure_cuboid(volume, structured_surfaces, structured_edges,
                     min_edge_nodes, c=1.0):
    volume_dt = (3, volume)
    surfaces_dts = gmsh.model.getBoundary([volume_dt])
    surfaces_edges = dict()
    surfaces_points = dict()
    edges = set()
    for surface_dt in surfaces_dts:
        edges_dts = gmsh.model.getBoundary([surface_dt],
                                           combined=False)  # Save order
        surface = surface_dt[1]
        surfaces_edges[surface] = list()
        surfaces_points[surface] = list()
        for edge_dt in edges_dts:
            edge = abs(edge_dt[1])
            surfaces_edges[surface].append(edge)
            edges.add(edge)
            points_dts = gmsh.model.getBoundary([edge_dt],
                                                combined=False)  # Save order
            p0 = points_dts[0][1]
            p1 = points_dts[1][1]
            if p0 not in surfaces_points[surface]:
                surfaces_points[surface].append(p0)
            if p1 not in surfaces_points[surface]:
                surfaces_points[surface].append(p1)
    # pprint(surfaces_points)
    min_point = min(min(x) for x in surfaces_points.values())
    first_point = min_point
    diagonal_surfaces = list()
    for k, v in surfaces_points.items():
        if first_point not in v:
            diagonal_surfaces.append(k)
    diagonal_point = None
    diagonal_point_set = set()
    for s in diagonal_surfaces:
        diagonal_point_set.update(set(surfaces_points[s]))
    for s in diagonal_surfaces:
        diagonal_point_set.intersection_update(set(surfaces_points[s]))
    for p in diagonal_point_set:
        diagonal_point = p
    circular_permutations = {
        0: [0, 1, 2, 3],
        1: [3, 0, 1, 2],
        2: [2, 3, 0, 1],
        3: [1, 2, 3, 0]
    }
    for k, v in surfaces_points.items():
        if first_point in v:
            point = first_point
        else:
            point = diagonal_point
        for p in circular_permutations.values():
            new_v = [v[x] for x in p]
            if new_v[0] == point:
                surfaces_points[k] = new_v
                break
    # pprint(surfaces_points)
    edges_groups = dict()
    groups_edges = dict()
    for i in range(3):
        groups_edges[i] = list()
        start_edge = None
        for e in edges:
            if e not in edges_groups:
                start_edge = e
                break
        edges_groups[start_edge] = i
        groups_edges[i].append(start_edge)
        start_edge_surfaces = list()
        for k, v in surfaces_edges.items():
            if start_edge in v:
                start_edge_surfaces.append(k)
        get_opposite_edge_index = {
            0: 2,
            1: 3,
            2: 0,
            3: 1
        }
        opposite_edge = None
        for s in start_edge_surfaces:
            surface_edges = surfaces_edges[s]
            start_edge_index = surface_edges.index(start_edge)
            opposite_edge_index = get_opposite_edge_index[start_edge_index]
            opposite_edge = surface_edges[opposite_edge_index]
            edges_groups[opposite_edge] = i
            groups_edges[i].append(opposite_edge)
        for k, v in surfaces_edges.items():
            if k not in start_edge_surfaces:
                if opposite_edge in v:
                    last_opposite_edge_index = v.index(opposite_edge)
                    diagonal_edge_index = get_opposite_edge_index[
                        last_opposite_edge_index]
                    diagonal_edge = v[diagonal_edge_index]
                    edges_groups[diagonal_edge] = i
                    groups_edges[i].append(diagonal_edge)
                    break
    # pprint(edges_groups)
    # pprint(groups_edges)
    edges_lengths = get_volume_edges_lengths(volume)
    groups_min_lengths = dict()
    for group, edges in groups_edges.items():
        lengths = [edges_lengths[x] for x in edges]
        groups_min_lengths[group] = min(lengths)
    # pprint(groups_min_lengths)
    min_length = min(groups_min_lengths.values())
    # number of nodes
    groups_n_nodes = dict()
    for group, length in groups_min_lengths.items():
        a = max(c * length / min_length, 1)
        n_nodes = int(min_edge_nodes * a)
        groups_n_nodes[group] = n_nodes
    # correct number of nodes from already structured edges
    for edge, group in edges_groups.items():
        if edge in structured_edges:
            groups_n_nodes[group] = structured_edges[edge]
    # pprint(groups_n_nodes)
    # Structure
    for edge, group in edges_groups.items():
        if edge not in structured_edges:
            n_nodes = groups_n_nodes[group]
            gmsh.model.mesh.setTransfiniteCurve(edge, n_nodes, "Progression", 1)
            structured_edges[edge] = n_nodes
    for surface, points in surfaces_points.items():
        if surface not in structured_surfaces:
            gmsh.model.mesh.setTransfiniteSurface(surface, cornerTags=points)
            structured_surfaces.add(surface)
    gmsh.model.mesh.setTransfiniteVolume(volume)


def check_file(path):
    """
    Check path on the existing file in the order:
    0. If file at absolute path
    1. Else if file at relative to current working directory path
    2. Else if file at relative to running script directory path
    3. Else if file at relative to real running script directory path
    (with eliminating all symbolics links)
    -1. Else no file
    :param str path:
    :return dict: {'type': int, 'path': str}
    """
    # Expand path
    path_expand_vars = os.path.expandvars(path)
    path_expand_vars_user = os.path.expanduser(path_expand_vars)
    # Get directories
    wd_path = os.getcwd()
    script_dir_path = os.path.dirname(os.path.abspath(__file__))
    # Set paths to file check
    clear_path = path_expand_vars_user
    rel_wd_path = os.path.join(wd_path, path_expand_vars_user)
    rel_script_path = os.path.join(script_dir_path, path_expand_vars_user)
    real_rel_script_path = os.path.realpath(rel_script_path)
    # Check on file:
    result = dict()
    if os.path.isfile(clear_path):
        result['type'] = 0
        result['path'] = clear_path
    elif os.path.isfile(rel_wd_path):
        result['type'] = 1
        result['path'] = rel_wd_path
    elif os.path.isfile(rel_script_path):
        result['type'] = 2
        result['path'] = rel_script_path
    elif os.path.isfile(real_rel_script_path):
        result['type'] = 3
        result['path'] = real_rel_script_path
    else:  # No file
        result['type'] = -1
        result['path'] = path
    return result


def rotation_matrix(axis, theta, deg=True):
    """
    Return the rotation matrix associated with counterclockwise rotation about
    the given axis by theta degrees.
    """
    theta = np.radians(theta) if deg else theta
    axis = np.array(axis)
    axis = axis / np.sqrt(np.dot(axis, axis))
    a = np.cos(0.5 * theta)
    b, c, d = -axis * np.sin(0.5 * theta)
    aa, bb, cc, dd = a * a, b * b, c * c, d * d
    bc, ad, ac, ab, bd, cd = b * c, a * d, a * c, a * b, b * d, c * d
    return np.array([[aa + bb - cc - dd, 2 * (bc + ad), 2 * (bd - ac)],
                     [2 * (bc - ad), aa + cc - bb - dd, 2 * (cd + ab)],
                     [2 * (bd + ac), 2 * (cd - ab), aa + dd - bb - cc]])


def transform(ps, data, mask=None, deg=True):
    mask = mask if mask is not None else np.zeros_like(ps)
    mps = np.ma.array(ps, mask=mask)
    if len(data) == 7:  # rotation around dir by angle relative to origin
        origin, direction, angle = data[:3], data[3:6], data[6]
        m = rotation_matrix(direction, angle, deg)
        lps = mps - origin  # local coordinates relative to origin
        mps = np.ma.dot(lps, m.T)
        mps = np.ma.add(mps, origin)
    elif len(data) == 4:  # rotation about dir by angle relative to (0, 0, 0)
        direction, angle = data[:3], data[3]
        m = rotation_matrix(direction, angle, deg)
        mps = np.ma.dot(mps, m.T)
    elif len(data) == 3:  # displacement
        displacement = data[:3]
        mps = np.ma.add(mps, displacement)
    else:
        raise ValueError(data)
    ps = mps.filled(ps)
    return ps


def transform_transform(t, data, deg=True):
    if len(t) == 3:  # displacement
        return list(transform([t[:3]], data, deg=deg)[0])
    elif len(t) == 4:  # rotation direction, angle
        return list(transform([t[:3]], data, deg=deg)[0]) + transform[4]
    elif len(t) == 7:  # rotation origin, direction, angle
        return list(transform([t[:3]], data, deg=deg)[0]) \
               + list(transform([t[3:6]], data, deg=deg)[0]) + t[6]
    else:
        raise ValueError(t)


def transform_transforms(ts, data, deg=True):
    return [transform_transform(t, data, deg) for t in ts]


def cylindrical_to_cartesian(cs, deg=True):
    """
    [[x, y, z], ...], [[r, phi, z], ...] or [[r, phi, theta], ...], where
    x, y, z  (inf, inf),
    r - radius [0, inf),
    phi - azimuthal angle [0, 360) (counterclockwise from X to Y),
    theta - polar angle [0, 180] [from top to bottom, i.e XY-plane is 90]
    """
    if deg:
        return [cs[0] * np.cos(np.radians(cs[1])),
                cs[0] * np.sin(np.radians(cs[1])), cs[2]]
    else:
        return [cs[0] * np.cos(cs[1]), cs[0] * np.sin(cs[1]), cs[2]]


def toroidal_to_cartesian(cs, deg=True):
    """
    [r, phi, theta, r2] -> [x, y, z]
    r - inner radius (r < r2)
    phi - inner angle [0-360]
    theta - outer angle [0-360]
    r2 - outer radius
    """
    r, phi, theta, r2 = cs[:4]
    if deg:
        phi, theta = np.radians(phi), np.radians(theta)
    return [r2 * np.cos(theta) + r * np.cos(phi) * np.cos(theta),
            r2 * np.sin(theta) + r * np.cos(phi) * np.sin(theta),
            r * np.sin(phi)]


def tokamak_to_cartesian(cs, deg=True):
    """
    [r, phi, theta, r2, kxy, kz]
    r - inner radius (r < r2)
    phi - inner angle [0-360]
    theta - outer angle [0-360]
    r2 - outer radius
    kxy - inner radius XY scale coefficient in positive outer radius direction
    kz - inner radius Z scale coefficient
    """
    r, phi, theta, r2, kxy, kz = cs[:6]
    if deg:
        phi, theta = np.radians(phi), np.radians(theta)
    if 0 <= phi <= 0.5 * np.pi or 1.5 * np.pi <= phi <= 2 * np.pi:
        return [
            r2 * np.cos(theta) + kxy * r * np.cos(phi) * np.cos(theta),
            r2 * np.sin(theta) + kxy * r * np.cos(phi) * np.sin(theta),
            kz * r * np.sin(phi)]
    else:
        return [
            r2 * np.cos(theta) + r * np.cos(phi) * np.cos(theta),
            r2 * np.sin(theta) + r * np.cos(phi) * np.sin(theta),
            kz * r * np.sin(phi)]


def spherical_to_cartesian(cs, deg=True):
    """
    [[x, y, z], ...], [[r, phi, z], ...] or [[r, phi, theta], ...], where
    x, y, z  (inf, inf),
    r - radius [0, inf),
    phi - azimuthal angle [0, 360) (counterclockwise from X to Y),
    theta - polar angle [0, 180] [from top to bottom, i.e XY-plane is 90]
    """
    if deg:
        return [
            cs[0] * np.cos(np.radians(cs[1])) * np.sin(np.radians(cs[2])),
            cs[0] * np.sin(np.radians(cs[1])) * np.sin(np.radians(cs[2])),
            cs[0] * np.cos(np.radians(cs[2]))]
    else:
        return [cs[0] * np.cos(cs[1]) * np.sin(cs[2]),
                cs[0] * np.sin(cs[1]) * np.sin(cs[2]),
                cs[0] * np.cos(cs[2])]


def cartesian_to_cartesian(cs, deg=True):
    return cs[:3]


def cell_to_local(cs, deg=True):
    x, y, z, xc, yc, zc, x0, x1, y0, y1, z0, z1 = cs
    return [x0 + x * (x1 - x0), y0 + y * (y1 - y0), z0 + z * (z1 - z0)]


coordinates_to_coordinates_map = {
    ('cylindrical', 'cartesian'): cylindrical_to_cartesian,
    ('spherical', 'cartesian'): spherical_to_cartesian,
    ('cartesian', 'cartesian'): cartesian_to_cartesian,
    ('toroidal', 'cartesian'): toroidal_to_cartesian,
    ('tokamak', 'cartesian'): tokamak_to_cartesian,
    ('cell', 'local'): cell_to_local
}


def transform_to_transform(t, cs0, cs1, c=None):
    f = coordinates_to_coordinates_map[(cs0, cs1)]
    if c is not None:
        if len(t) == 3:  # displacement
            return f(t + c)
        elif len(t) == 4:  # rotation direction, angle
            return f(t[:3] + c) + [t[3]]
        elif len(t) == 7:  # rotation origin, direction, angle
            return f(t[:3] + c) + f(t[3:6] + c) + [t[6]]
        else:
            raise ValueError(t)
    else:
        if len(t) == 3:  # displacement
            return f(t)
        elif len(t) == 4:  # rotation direction, angle
            return f(t[:3]) + [t[3]]
        elif len(t) == 7:  # rotation origin, direction, angle
            return f(t[:3]) + f(t[3:6]) + [t[6]]
        else:
            raise ValueError(t)


def transforms_to_transforms(ts, cs0, cs1, cs=None):
    if cs is None:
        return [transform_to_transform(t, cs0, cs1) for t in ts]
    else:
        return [transform_to_transform(t, cs0, cs1, c) for t, c in zip(ts, cs)]


def coordinates_to_coordinates(ps, cs0, cs1):
    f = coordinates_to_coordinates_map[(cs0, cs1)]
    return [f(x) for x in ps]


def parse_indexing(cs, coordinates_type):
    """
    Parse grid coordinates indexing
    """
    new_cs = []  # new coordinates
    n2o = {}  # new to old local item map
    ni = 0  # new index
    oi = 0  # old index
    for i, c in enumerate(cs):
        if isinstance(c, (int, float)):
            if coordinates_type == 'direct':  # Divide dc interval into nc parts
                new_cs.append(c)
                if i != len(cs) - 1:  # skip last coordinate
                    n2o[ni] = oi
                    ni += 1
                    oi += 1
            elif coordinates_type == 'delta':
                new_cs.append(c)
                n2o[ni] = oi
                ni += 1
                oi += 1
            else:
                raise ValueError(coordinates_type)
        elif isinstance(c, str):  # Advanced indexing
            if coordinates_type == 'direct':  # Divide dc interval into nc parts
                c0, c1, nc = cs[i - 1], cs[i + 1], int(c)
                dc = (c1 - c0) / nc
                for _ in range(nc - 1):
                    new_cs.append(new_cs[ni - 1] + dc)
                    n2o[ni] = oi - 1
                    ni += 1
            elif coordinates_type == 'delta':
                dc, nc = cs[i - 1], int(c)  # Copy dc interval nc times
                for _ in range(nc):
                    new_cs.append(dc)
                    n2o[ni] = oi - 1
                    ni += 1
            else:
                raise ValueError(coordinates_type)
    return new_cs, n2o


def rotation(ps, origin, direction, angle, **kwargs):
    """Rotation of points around direction at origin by angle
    Args:
        ps:
        origin:
        direction:
        angle:

    Returns:
        nps: (list of list of float or list of float): new point(s)
    """
    m = rotation_matrix(direction, angle)
    lps = np.subtract(ps, origin)  # local coordinates relative to origin
    return np.matmul(lps, m.T) + origin


def affine(ps, origin, vs, **kwargs):
    """Affine transformation of point(s) (y = Ax + b)
    A - coordinate system basis vectors
    b - coordinate system origin
    x - old points
    y - new points
    Args:
        ps: (list of list of float or list of float): point(s)
        (number of points, old dim) or (old dim)
        origin: (list of float): coordinate system origin (new dim)
        vs: (list of list of float): coordinate system basis vectors
        (old dim, new dim)
    Returns:
        nps: (list of list of float or list of float): new point(s)
    """
    return np.matmul(ps, vs) + origin
