from pprint import pprint
import math

import gmsh


# FIXME Bug with this approach:
# File "/share/home/butovr/gmsh_scripts/support.py", line 14, in get_volume_points_edges_data
# surfaces_dim_tags = gmsh.model.getBoundary([[3, volume]])
# File "/home/butovr/Programs/gmsh/api/gmsh.py", line 517, in getBoundary ierr.value)
# ValueError: ('gmshModelGetBoundary returned non-zero error code: ', 1)
def get_volume_points_edges_data(volume):
    """
    Return volume points edges data. For point's characteristic length (lc) auto setting.
    :param volume: volume index
    :return: dictionary (point: [n_edges, edges_min_length, edges_max_length, edges_avg_length])
    """
    # Get volume edges
    volume_dim_tag = [3, volume]
    surfaces_dim_tags = gmsh.model.getBoundary([volume_dim_tag])
    edges = set()
    for sdt in surfaces_dim_tags:
        curves_dim_tags = gmsh.model.getBoundary([sdt])
        for cdt in curves_dim_tags:
            edges.add(abs(cdt[1]))
    # Get volume points
    points_dim_tags = gmsh.model.getBoundary([volume_dim_tag], recursive=True)
    points = map(lambda x: x[1], points_dim_tags)
    # Get points edges and edges points
    points_edges = {x: set() for x in points}
    edges_points = dict()
    for e in edges:
        edge_dim_tag = [1, e]
        points_dim_tags = gmsh.model.getBoundary([edge_dim_tag])
        edges_points[e] = map(lambda x: x[1], points_dim_tags)
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
        points_edges_data[p] = [
            n_edges,
            min_length,
            max_length,
            mean_length
        ]
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
    volume_dim_tag = [3, volume]
    surfaces_dim_tags = gmsh.model.getBoundary([volume_dim_tag])
    edges = set()
    for sdt in surfaces_dim_tags:
        edges_dim_tags = gmsh.model.getBoundary([sdt])
        for edt in edges_dim_tags:
            edges.add(abs(edt[1]))
    # Get edges points
    edges_points = dict()
    for e in edges:
        edge_dim_tag = [1, e]
        points_dim_tags = gmsh.model.getBoundary([edge_dim_tag])
        edges_points[e] = map(lambda x: x[1], points_dim_tags)
    # Calculate edges lengths
    edges_lengths = dict()
    for e in edges:
        ps = edges_points[e]
        bb0 = gmsh.model.getBoundingBox(0, ps[0])
        bb1 = gmsh.model.getBoundingBox(0, ps[1])
        cs0 = [bb0[0], bb0[1], bb0[2]]
        cs1 = [bb1[0], bb1[1], bb1[2]]
        vector = [cs1[0] - cs0[0], cs1[1] - cs0[1], cs1[2] - cs0[2]]
        length = math.sqrt(vector[0] * vector[0] + vector[1] * vector[1] + vector[2] * vector[2])
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
        dim_tag = [2, s]
        edges_dim_tags = gmsh.model.getBoundary([dim_tag], combined=False)
        surface_edges = [x[1] for x in edges_dim_tags]
        surfaces_edges[s] = surface_edges
        abs_surfaces_edges = [abs(x) for x in surface_edges]
        edges.update(set(abs_surfaces_edges))
    # Edges
    points = set()
    for e in edges:
        dim_tag = [1, e]
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
                        out['duplicate_volumes'].setdefault(volume2, set()).add(volume)
                        out['duplicate_volumes'].setdefault(volume, set()).add(volume2)
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
                        out['duplicate_surfaces'].setdefault(surface2, set()).add(surface)
                        out['duplicate_surfaces'].setdefault(surface, set()).add(surface2)
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
                        out['duplicate_edges'].setdefault(edge2, set()).add(edge)
                        out['duplicate_edges'].setdefault(edge, set()).add(edge2)
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
                        out['duplicate_points'].setdefault(point2, set()).add(point)
                        out['duplicate_points'].setdefault(point, set()).add(point2)
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
        new_edges = [math.copysign(1, x) * old_edges_to_new_edges[abs(x)] for x in old_edges]
        if factory == gmsh.model.occ:
            abs_new_edges = [abs(x) for x in new_edges]
            # curve_loop_tag = factory.addCurveLoop(abs_new_edges)  # FIXME signed edges doesn't work
            curve_loop_tag = factory.addWire(abs_new_edges)  # FIXME signed edges doesn't work
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
        surface_loop_tag = factory.addSurfaceLoop(new_surfaces)  # FIXME always return -1
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
                point_dim_tag = [0, k]
                gmsh.model.mesh.setSize([point_dim_tag], new_size)
    return points_sizes


def auto_primitive_points_sizes_min_curve(primitive_obj, points_sizes_dict, c=1.0):
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


def auto_primitive_points_sizes_min_curve_in_volume(primitive_obj, points_sizes, c=1.0):
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
                point_dim_tag = [0, k]
                gmsh.model.mesh.setSize([point_dim_tag], new_size)


def auto_complex_points_sizes_min_curve(complex_obj, points_sizes_dict, k=1.0):
    for p in complex_obj.primitives:
        auto_primitive_points_sizes_min_curve(p, points_sizes_dict, k)


def auto_complex_points_sizes_min_curve_in_volume(complex_obj, points_sizes_dict, k=1.0):
    for p in complex_obj.primitives:
        auto_primitive_points_sizes_min_curve_in_volume(p, points_sizes_dict, k)


def get_bounding_box_by_boundary_surfaces(boundary_surfaces):
    points_x = dict()
    points_y = dict()
    points_z = dict()
    surfaces_dim_tags = map(lambda x: [2, x], boundary_surfaces)
    points_dim_tags = gmsh.model.getBoundary(surfaces_dim_tags, combined=False, recursive=True)
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
    surfaces = map(lambda x: x[1], surfaces_dim_tags)
    return surfaces


def boundary_surfaces_to_six_side_groups():
    """
    Try group boundary surfaces them into 6 groups by sides of cuboid (NX, NY, NZ, X, Y, Z)
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
    surfaces_dim_tags = map(lambda x: [2, x], boundary_surfaces)
    points_dim_tags = gmsh.model.getBoundary(surfaces_dim_tags, combined=False, recursive=True)
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
        surface_dim_tag = [2, s]
        points_dim_tags = gmsh.model.getBoundary(surface_dim_tag, combined=False, recursive=True)
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
                    if abs(s_min_x - min_x ) < tol:
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


def volumes_surfaces_to_volumes_groups_surfaces(volumes_surfaces):
    """
    For Environment object. For each distinct inner volume in Environment should exist
    the surface loop. If inner volumes touch each other they unite to volume group
    and have common surface loop.
    :param volumes_surfaces: [[v1_s1, ..., v1_si], ..., [vj_s1, ..., vj_si]]
    :return: volumes_groups_surfaces [[vg1_s1, ..., vg1_si], ..., [vgj_s1, ..., vgj_si]]
    """
    vgs_ss = list()  # volumes_groups_surfaces
    vs_set = set(range(len(volumes_surfaces)))  # Set of yet unallocated volumes indices to volumes groups
    while len(vs_set) != 0:
        current_vs = list(vs_set)
        v0 = current_vs[0]  # Start with volume 0 surfaces
        vg_ss = set(volumes_surfaces[v0])
        for i in range(1, len(current_vs)):
            vi = current_vs[i]
            vi_ss = set(volumes_surfaces[vi])
            # print(vg_ss, vi_ss)
            intersection = vg_ss.intersection(vi_ss)
            if len(intersection) > 0:  # If volume group and volume i surfaces have common surfaces
                vg_ss.symmetric_difference_update(vi_ss)  # Add volume i surfaces to volume group without common
                vs_set.remove(vi)  # Remove volume i from vs_set
        vgs_ss.append(list(vg_ss))
        vs_set.remove(v0)
    return vgs_ss


def auto_volumes_groups_surfaces():
    volumes_dim_tags = gmsh.model.getEntities(3)  # all model volumes
    volumes_surfaces = list()
    for vdt in volumes_dim_tags:
        surfaces_dim_tags = gmsh.model.getBoundary([vdt])  # volume surfaces
        ss = map(lambda x: x[1], surfaces_dim_tags)
        volumes_surfaces.append(ss)
    return volumes_surfaces_to_volumes_groups_surfaces(volumes_surfaces)


def get_volume_composition(volume):
    volume_dt = [3, volume]
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
    volume_dt = [3, volume]
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


def structure_cuboid(volume, structured_surfaces, structured_edges, min_edge_nodes, c=1.0):
    volume_dt = [3, volume]
    surfaces_dts = gmsh.model.getBoundary([volume_dt])
    surfaces_edges = dict()
    surfaces_points = dict()
    edges = set()
    for surface_dt in surfaces_dts:
        edges_dts = gmsh.model.getBoundary([surface_dt], combined=False)  # Save order
        surface = surface_dt[1]
        surfaces_edges[surface] = list()
        surfaces_points[surface] = list()
        for edge_dt in edges_dts:
            edge = abs(edge_dt[1])
            surfaces_edges[surface].append(edge)
            edges.add(edge)
            points_dts = gmsh.model.getBoundary([edge_dt], combined=False)  # Save order
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
            new_v = map(lambda x: v[x], p)
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
                    diagonal_edge_index = get_opposite_edge_index[last_opposite_edge_index]
                    diagonal_edge = v[diagonal_edge_index]
                    edges_groups[diagonal_edge] = i
                    groups_edges[i].append(diagonal_edge)
                    break
    # pprint(edges_groups)
    # pprint(groups_edges)
    edges_lengths = get_volume_edges_lengths(volume)
    groups_min_lengths = dict()
    for group, edges in groups_edges.items():
        lengths = map(lambda x: edges_lengths[x], edges)
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
