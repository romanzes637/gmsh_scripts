from pprint import pprint

import gmsh
import math


def get_volume_points_curves_data(volume):
    """
    Return volume's points curves data. For point's characteristic length (lc) auto setting.
    :param volume: volume index
    :return: [[p1_index, p1_n_curves, p1_curves_min_length, p1_curves_max_length, p1_curves_avg_length], [p2...], ...]
    """
    # Get volume curves
    surfaces_dim_tags = gmsh.model.getBoundary([[3, volume]])
    curves = set()
    for sdt in surfaces_dim_tags:
        curves_dim_tags = gmsh.model.getBoundary([sdt])
        for cdt in curves_dim_tags:
            curves.add(abs(cdt[1]))
    # Get points' curves and curves' points
    points_dim_tags = gmsh.model.getBoundary([[3, volume]], recursive=True)
    points = map(lambda x: x[1], points_dim_tags)
    points_curves = {x: set() for x in points}
    curves_points = dict()
    for c in curves:
        points_dim_tags = gmsh.model.getBoundary([[1, c]])
        curves_points[c] = map(lambda x: x[1], points_dim_tags)
        for p in curves_points[c]:
            points_curves[p].add(c)
    # Calculate curves' square lengths
    curves_sqr_lengths = dict()
    curves_points_coordinates = dict()
    for c in curves:
        ps = curves_points[c]
        bb0 = gmsh.model.getBoundingBox(0, ps[0])
        bb1 = gmsh.model.getBoundingBox(0, ps[1])
        curves_points_coordinates[c] = [bb0, bb1]
        cs0 = [bb0[0], bb0[1], bb0[2]]
        cs1 = [bb1[0], bb1[1], bb1[2]]
        r = [cs1[0] - cs0[0], cs1[1] - cs0[1], cs1[2] - cs0[2]]
        sqr_length = r[0] * r[0] + r[1] * r[1] + r[2] * r[2]
        curves_sqr_lengths[c] = sqr_length
    # Prepare the output
    points_curves_data = list()
    for p in points:
        sqr_lengths = list()
        for c in points_curves[p]:
            sqr_lengths.append(curves_sqr_lengths[c])
        n_curves = len(sqr_lengths)
        min_sqr_length = min(sqr_lengths)
        max_sqr_length = max(sqr_lengths)
        mean_sqr_length = sum(sqr_lengths) / n_curves  # Mean Square (MS)
        points_curves_data.append([
            p,
            n_curves,
            math.sqrt(min_sqr_length),
            math.sqrt(max_sqr_length),
            math.sqrt(mean_sqr_length)  # Root Mean Square (RMS)
        ])
        # print(volume)
        # pprint(points_curves)
        # pprint(curves_points)
        # pprint(curves_points_coordinates)
        # pprint(curves_sqr_lengths)
    return points_curves_data


def auto_points_sizes(k=1.0):
    points_sizes = dict()
    volumes_dim_tags = gmsh.model.getEntities(3)  # all model volumes
    for vdt in volumes_dim_tags:
        ps_cs_data = get_volume_points_curves_data(vdt[1])
        v_curves_min_length = []
        for pd in ps_cs_data:  # for each volume's point data
            v_curves_min_length.append(k * pd[2])  # k * min curve length
        size = min(v_curves_min_length)  # min curve length of all points
        for pd in ps_cs_data:
            p = pd[0]  # point index
            old_size = points_sizes.get(p)
            if old_size is not None:
                if size < old_size:
                    points_sizes[p] = size
                    gmsh.model.mesh.setSize([[0, p]], size)
            else:
                points_sizes[p] = size
                gmsh.model.mesh.setSize([[0, p]], size)
    return points_sizes


def auto_primitive_points_sizes_min_curve(primitive_obj, points_sizes_dict, k=1.0):
    for v in primitive_obj.volumes:
        ps_cs_data = get_volume_points_curves_data(v)
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
        ps_cs_data = get_volume_points_curves_data(v)
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
