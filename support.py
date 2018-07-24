from pprint import pprint

import gmsh
import math


def get_volume_points_edges_data(volume):
    """
    Return volume points edges data. For point's characteristic length (lc) auto setting.
    :param volume: volume index
    :return: dictionary (point: [n_edges, edges_min_length, edges_max_length, edges_avg_length])
    """
    # Get volume edges
    surfaces_dim_tags = gmsh.model.getBoundary([[3, volume]])
    edges = set()
    for sdt in surfaces_dim_tags:
        curves_dim_tags = gmsh.model.getBoundary([sdt])
        for cdt in curves_dim_tags:
            edges.add(abs(cdt[1]))
    # Get volume points
    points_dim_tags = gmsh.model.getBoundary([[3, volume]], recursive=True)
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
    surfaces_dim_tags = gmsh.model.getBoundary([[3, volume]])
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


def get_volumes_entities():
    volumes_surfaces = dict()
    surfaces_edges = dict()
    edges_points = dict()
    points_coordinates = dict()
    surfaces = set()
    volumes_dim_tags = gmsh.model.getEntities(3)
    for dt in volumes_dim_tags:
        surfaces_dim_tags = gmsh.model.getBoundary([dt], combined=False)
        volume = dt[1]
        volume_surfaces = [x[1] for x in surfaces_dim_tags]
        volumes_surfaces[volume] = volume_surfaces
        surfaces.update(set(volume_surfaces))
    edges = set()
    for s in surfaces:
        dim_tag = [2, s]
        edges_dim_tags = gmsh.model.getBoundary([dim_tag], combined=False)
        surface_edges = [x[1] for x in edges_dim_tags]
        surfaces_edges[s] = surface_edges
        edges.update(set([abs(x) for x in surface_edges]))
    points = set()
    for e in edges:
        dim_tag = [1, e]
        points_dim_tags = gmsh.model.getBoundary([dim_tag], combined=False)
        edge_points = [x[1] for x in points_dim_tags]
        edges_points[e] = edge_points
        points.update(set(edge_points))
    for p in points:
        bb = gmsh.model.getBoundingBox(0, p)
        coordinates = [bb[0], bb[1], bb[2]]
        points_coordinates[p] = coordinates
    parts = dict()
    parts['volumes'] = volumes_surfaces
    parts['surfaces'] = surfaces_edges
    parts['edges'] = edges_points
    parts['points'] = points_coordinates
    return parts


def auto_primitive_points_sizes_min_curve(primitive_obj, points_sizes_dict, k=1.0):
    for v in primitive_obj.volumes:
        ps_cs_data = get_volume_points_edges_data(v)
        for pd in ps_cs_data:
            p = pd[0]  # point index
            size = k * pd[2]  # k * min curve length
            old_size = points_sizes_dict.get(p)
            if old_size is not None:
                if size < old_size:
                    points_sizes_dict[p] = size
                    gmsh.model.mesh.setSize([(0, p)], size)
            else:
                points_sizes_dict[p] = size
                gmsh.model.mesh.setSize([(0, p)], size)


def auto_primitive_points_sizes_min_curve_in_volume(primitive_obj, points_sizes_dict, k=1.0):
    for v in primitive_obj.volumes:
        ps_cs_data = get_volume_points_edges_data(v)
        v_curves_min_length = []
        for pd in ps_cs_data:  # for each volume's point data
            v_curves_min_length.append(k * pd[2])  # k * min curve length
        size = min(v_curves_min_length)  # min curve length of all points
        for pd in ps_cs_data:
            p = pd[0]  # point index
            old_size = points_sizes_dict.get(p)
            if old_size is not None:
                if size < old_size:
                    points_sizes_dict[p] = size
                    gmsh.model.mesh.setSize([(0, p)], size)
            else:
                points_sizes_dict[p] = size
                gmsh.model.mesh.setSize([(0, p)], size)


def auto_complex_points_sizes_min_curve(complex_obj, points_sizes_dict, k=1.0):
    for p in complex_obj.primitives:
        auto_primitive_points_sizes_min_curve(p, points_sizes_dict, k)


def auto_complex_points_sizes_min_curve_in_volume(complex_obj, points_sizes_dict, k=1.0):
    for p in complex_obj.primitives:
        auto_primitive_points_sizes_min_curve_in_volume(p, points_sizes_dict, k)


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


def structure_cuboid(volume, transfinited_surfaces, min_edge_nodes, c=1.0):
    volumes_dts = [[3, volume]]
    surfaces_dts = gmsh.model.getBoundary(volumes_dts)
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
    pprint(surfaces_points)
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
    pprint(surfaces_points)
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
    pprint(edges_groups)
    pprint(groups_edges)
    edges_lengths = get_volume_edges_lengths(volume)
    min_lengths = dict()
    for k, v in groups_edges.items():
        lengths = map(lambda x: edges_lengths[x], v)
        min_lengths[k] = min(lengths)
    pprint(min_lengths)
    min_length = min(min_lengths.values())
    n_nodes = dict()
    for k, v in min_lengths.items():
        a = max(c * v / min_length, 1)
        n_nodes[k] = int(min_edge_nodes * a)
    print(n_nodes)
    for k, v in edges_groups.items():
        gmsh.model.mesh.setTransfiniteCurve(k, n_nodes[v], "Progression", 1)
    for k, v in surfaces_points.items():
        if k not in transfinited_surfaces:
            gmsh.model.mesh.setTransfiniteSurface(k, cornerTags=v)
    gmsh.model.mesh.setTransfiniteVolume(volume)
