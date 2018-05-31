import gmsh
import math


def get_volume_points_curves_data(volume):
    """
    Return volume's points curves data. For point's characteristic length (lc) auto setting.
    :param volume: volume index
    :return: [[p1_index, p1_n_curves, p1_curves_min_length, p1_curves_max_length, p1_curves_avg_length], ...]
    """
    surfaces_dim_tags = gmsh.model.getBoundary([(3, volume)], combined=False)
    surfaces = map(lambda x: x[1], surfaces_dim_tags)
    curves = set()
    for surface in surfaces:
        curves_dim_tags = gmsh.model.getBoundary([(2, surface)], combined=False)
        for dt in curves_dim_tags:
            curves.add(abs(dt[1]))
    points_dim_tags = gmsh.model.getBoundary([(3, volume)], combined=False, recursive=True)
    points = map(lambda x: x[1], points_dim_tags)
    points_curves = {x: set() for x in points}
    curves_points = {}
    for c in curves:
        out_dim_tags = gmsh.model.getBoundary([(1, c)], combined=False)
        curves_points.update({c: map(lambda x: x[1], out_dim_tags)})
        for ps in curves_points[c]:
            points_curves[ps].add(c)
    curves_sqr_lengths = {}
    for c in curves:
        cp = curves_points[c]
        bb0 = gmsh.model.getBoundingBox(0, cp[0])
        bb1 = gmsh.model.getBoundingBox(0, cp[1])
        cs0 = [bb0[0], bb0[1], bb0[2]]
        cs1 = [bb1[0], bb1[1], bb1[2]]
        r = [cs1[0] - cs0[0], cs1[1] - cs0[1], cs1[2] - cs0[2]]
        length = r[0] * r[0] + r[1] * r[1] + r[2] * r[2]
        curves_sqr_lengths.update({c: length})
    points_curves_data = []
    for p in points:
        sqr_lengths = []
        for c in points_curves[p]:
            sqr_lengths.append(curves_sqr_lengths[c])
        n_curves = len(sqr_lengths)
        min_sqr_length = min(sqr_lengths)
        max_sqr_length = max(sqr_lengths)
        avg_sqr_length = sum(sqr_lengths) / n_curves
        points_curves_data.append([
            p,
            n_curves,
            math.sqrt(min_sqr_length),
            math.sqrt(max_sqr_length),
            math.sqrt(avg_sqr_length)
        ])
    return points_curves_data


def auto_primitive_points_sizes_min_curve(primitive_obj, points_sizes_dict):
    for v in primitive_obj.volumes:
        ps_cs_data = get_volume_points_curves_data(v)
        for pd in ps_cs_data:
            p = pd[0]
            size = pd[2]  # min curve length
            old_size = points_sizes_dict.get(p)
            if old_size is not None:
                if size < old_size:
                    points_sizes_dict.update({p: size})
                    gmsh.model.mesh.setSize([(0, p)], size)
            else:
                points_sizes_dict.update({p: size})
                gmsh.model.mesh.setSize([(0, p)], size)


def auto_complex_points_sizes_min_curve(complex_obj, points_sizes_dict):
    for p in complex_obj.primitives:
        auto_primitive_points_sizes_min_curve(p, points_sizes_dict)
