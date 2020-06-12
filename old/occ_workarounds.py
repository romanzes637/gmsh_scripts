import gmsh


# FIXME? Workarounds for OCC to GMSH


# Primitive
def correct_primitive(primitive):
    corrected = False
    if len(primitive.volumes) == 1:
        volumes_dim_tags = [(3, x) for x in primitive.volumes]
        surfaces_dim_tags = gmsh.model.getBoundary(dimTags=volumes_dim_tags,
                                                   combined=False)
        if len(surfaces_dim_tags) == 6:
            points_dim_tags = gmsh.model.getBoundary(volumes_dim_tags, combined=False, recursive=True)
            if len(points_dim_tags) == 8:
                points_coordinates = []
                for dim_tag in points_dim_tags:
                    bb = gmsh.model.getBoundingBox(dim_tag[0], dim_tag[1])
                    points_coordinates.append([bb[0], bb[1], bb[2]])
                # Create map from old to new points indices and correct primitive.points
                map_old_new_points = []
                for old_cs in primitive.points_coordinates:
                    tol = gmsh.option.getNumber("Geometry.Tolerance")
                    tol /= 10
                    found = False
                    while not found:
                        tol *= 10
                        for new_idx, new_cs in enumerate(points_coordinates):
                            # print(abs(old_cs[0] - new_cs[0]), abs(old_cs[1] - new_cs[1]), abs(old_cs[2] - new_cs[2]))
                            if abs(old_cs[0] - new_cs[0]) < tol:
                                if abs(old_cs[1] - new_cs[1]) < tol:
                                    if abs(old_cs[2] - new_cs[2]) < tol:
                                        map_old_new_points.append(new_idx)
                                        found = True
                if len(map_old_new_points) != 8:  # FIXME there is a problem if it happened...
                    print("WARNING: len(map_old_new_points) != 8")
                    return False
                primitive.points = map(lambda x: points_dim_tags[x][1], map_old_new_points)
                # Correct surfaces
                surfaces_points = []
                for dim_tag in surfaces_dim_tags:
                    points_dim_tags = gmsh.model.getBoundary([dim_tag], combined=False, recursive=True)
                    surfaces_points.append(map(lambda x: x[1], points_dim_tags))
                is_4_points = True  # Check for 4 points in each surface, if not stop
                for surface_points in surfaces_points:
                    if len(surface_points) != 4:
                        is_4_points = False
                if is_4_points:
                    # Surfaces local points
                    surfaces_local_points = []
                    for surface_points in surfaces_points:
                        surface_local_points = []
                        for point in surface_points:
                            surface_local_points.append(primitive.points.index(point))
                        surfaces_local_points.append(surface_local_points)
                    # Create map from old to new surfaces indices and correct primitive.surfaces
                    map_old_new_surfaces = []
                    for old_ps in primitive.surfaces_local_points:
                        for new_idx, new_ps in enumerate(surfaces_local_points):
                            if set(old_ps) == set(new_ps):
                                map_old_new_surfaces.append(new_idx)
                    primitive.surfaces = map(lambda x: surfaces_dim_tags[x][1], map_old_new_surfaces)
                    # Correct curves
                    curves = set()
                    for dim_tag in surfaces_dim_tags:
                        curves_dim_tags = gmsh.model.getBoundary([dim_tag], combined=False)
                        for curve in curves_dim_tags:
                            curves.add(abs(curve[1]))
                    curves_points = []
                    for curve in curves:
                        points_dim_tags = gmsh.model.getBoundary([(1, curve)], combined=False)
                        curves_points.append(map(lambda x: x[1], points_dim_tags))
                    # Curves local points
                    curves_local_points = []
                    for curve_points in curves_points:
                        curve_local_points = []
                        for point in curve_points:
                            curve_local_points.append(primitive.points.index(point))
                        curves_local_points.append(curve_local_points)
                    # Create map from old to new curves indices and correct primitive.curves
                    map_old_new_curves = []
                    for old_ps in primitive.curves_local_points:
                        for new_idx, new_ps in enumerate(curves_local_points):
                            if set(old_ps) == set(new_ps):
                                map_old_new_curves.append(new_idx)
                    list_curves = list(curves)
                    primitive.curves = map(lambda x: list_curves[x], map_old_new_curves)
                    corrected = True
    return corrected


# Complex
def correct_complex(complex_obj):
    results = []
    for p in complex_obj.primitives:
        result = correct_primitive(p)
        results.append(result)
    return results


def correct_and_transfinite_primitive(primitive_obj, ss, cs):
    """
    Correct Primitive, if Primitive corrected => transfinite it
    :param primitive_obj: Primitive object
    :param ss: set() - already transfinited surfaces
    :param cs: set() - already transfinited curves
    """
    result = correct_primitive(primitive_obj)
    if result:
        result = primitive_obj.transfinite(ss, cs)
    else:
        result = None
    return result


def correct_and_transfinite_complex(complex_obj, ss, cs):
    """
    Correct Complex's Primitives then if Primitive corrected => transfinite it
    :param complex_obj: Complex object
    :param ss: set() - already transfinited surfaces
    :param cs: set() - already transfinited curves
    """
    correction_rs = correct_complex(complex_obj)
    transfinite_rs = []
    for i, p in enumerate(complex_obj.primitives):
        if correction_rs[i]:
            result = p.transfinite(ss, cs)
            transfinite_rs.append(result)
        else:
            transfinite_rs.append(None)
    return transfinite_rs


def transfinite_complex(complex_obj, ss, cs):
    """
    Correct Complex's Primitives then if Primitive corrected => transfinite it
    :param complex_obj: Complex object
    :param ss: set() - already transfinited surfaces
    :param cs: set() - already transfinited curves
    """
    transfinite_rs = []
    for i, p in enumerate(complex_obj.primitives):
        result = p.transfinite(ss, cs)
        transfinite_rs.append(result)
    return transfinite_rs


def transfinite_and_recombine_complex(complex_obj, ss, cs):
    """
    Correct Complex's Primitives then if Primitive corrected =>
    transfinite and recombine it
    :param complex_obj: Complex object
    :param ss: set() - already transfinited surfaces
    :param cs: set() - already transfinited curves
    """
    transfinite_rs = transfinite_complex(complex_obj, ss, cs)
    for i, p in enumerate(complex_obj.primitives):
        p.recombine()
    return transfinite_rs


def correct_and_transfinite_and_recombine_complex(complex_obj, ss, cs):
    """
    Correct Complex's Primitives then if Primitive corrected =>
    transfinite and recombine it
    :param complex_obj: Complex object
    :param ss: set() - already transfinited surfaces
    :param cs: set() - already transfinited curves
    """
    correction_rs = correct_complex(complex_obj)
    transfinite_rs = []
    for i, p in enumerate(complex_obj.primitives):
        if correction_rs[i]:
            result = p.transfinite(ss, cs)
            transfinite_rs.append(result)
            p.recombine()
        else:
            transfinite_rs.append(None)
    return transfinite_rs


def correct_and_transfinite_and_recombine_primitive(primitive_obj, ss, cs):
    """
    Correct Primitive, if Primitive corrected => transfinite it
    :param primitive_obj: Primitive object
    :param ss: set() - already transfinited surfaces
    :param cs: set() - already transfinited curves
    """
    result = correct_primitive(primitive_obj)
    if result:
        result = primitive_obj.transfinite(ss, cs)
        primitive_obj.recombine()
    else:
        result = None
    return result
