import gmsh


# FIXME Workarounds for OCC to GMSH


# Primitive
# Right primitive's surfaces order: [NX, X, NY, Y, NZ, Z]
def correction(primitive):
    """
    Algorithm that gets actual primitive volume and correct self primitive's data by it.
    Only for 1 volume with 6 surfaces primitive.
    Used by correct_primitive() function, where above conditions are checked.
    :param primitive: primitive object
    """
    surfaces_dim_tags = map(lambda x: (2, x), primitive.surfaces)
    # Surfaces points
    surfaces_points = []
    surfaces_curves = []
    for dim_tag in surfaces_dim_tags:
        points_dim_tags = gmsh.model.getBoundary(dim_tag, combined=False, recursive=True)
        surfaces_points.append(map(lambda x: x[1], points_dim_tags))
        curves_dim_tags = gmsh.model.getBoundary(dim_tag, combined=False)
        surfaces_curves.append(map(lambda x: abs(x[1]), curves_dim_tags))
    # Points
    # [NX, X, NY, Y, NZ, Z]
    points_map = [
        {1, 4, 3},
        {0, 4, 3},
        {0, 4, 2},
        {1, 4, 2},
        {1, 5, 3},
        {0, 5, 3},
        {0, 5, 2},
        {1, 5, 2}
    ]
    flatten_points = [item for sublist in surfaces_points for item in sublist]
    fcs = list(set(flatten_points))
    bs = []
    for c in fcs:
        b = []
        for idx, s_curves in enumerate(surfaces_points):
            if c in s_curves:
                b.append(idx)
        bs.append(set(b))
    primitive.points = map(lambda x: fcs[bs.index(x)], points_map)
    # Curves
    # [NX, X, NY, Y, NZ, Z]
    curves_map = [
        {4, 3},
        {3, 5},
        {5, 2},
        {2, 4},
        {1, 4},
        {4, 0},
        {0, 5},
        {5, 1},
        {1, 3},
        {3, 0},
        {0, 2},
        {2, 1}
    ]
    flatten_curves = [item for sublist in surfaces_curves for item in sublist]
    fcs = list(set(flatten_curves))
    bs = []
    for c in fcs:
        b = []
        for idx, s_curves in enumerate(surfaces_curves):
            if c in s_curves:
                b.append(idx)
        bs.append(set(b))
    primitive.curves = map(lambda x: fcs[bs.index(x)], curves_map)
    #     self.curves = map(lambda x: fcs[bs.index(x)], curves_map)
    #     # print(self.curves)
    #     # x_curves = []
    #     # y_curves = []
    #     # z_curves = []
    #     # min_curve = sys.maxsize
    #     # min_curve_idx = 0
    #     # min_surface_idx = 0
    #     # for i in range(len(surfaces_curves)):
    #     #     for j in range(len(surfaces_curves[i])):
    #     #         curve = surfaces_curves[i][j]
    #     #         if curve < min_curve:
    #     #             min_curve = curve
    #     #             min_curve_idx = i
    #     #             min_surface_idx = j
    #     # # print(min_curve)
    #     # # print(min_surface_idx)
    #     # # print(min_curve_idx)
    #     # x_curves.append(surfaces_curves[min_surface_idx][min_curve_idx])
    #     # if min_curve_idx == 0:
    #     #     x_curves.append(surfaces_curves[min_surface_idx][min_curve_idx + 2])
    #     #     y_curves.append(surfaces_curves[min_surface_idx][min_curve_idx + 1])
    #     #     y_curves.append(surfaces_curves[min_surface_idx][min_curve_idx + 3])
    #     # elif min_curve_idx == 1:
    #     #     x_curves.append(surfaces_curves[min_surface_idx][min_curve_idx + 2])
    #     #     y_curves.append(surfaces_curves[min_surface_idx][min_curve_idx - 1])
    #     #     y_curves.append(surfaces_curves[min_surface_idx][min_curve_idx + 1])
    #     # elif min_curve_idx == 2:
    #     #     x_curves.append(surfaces_curves[min_surface_idx][min_curve_idx - 2])
    #     #     y_curves.append(surfaces_curves[min_surface_idx][min_curve_idx - 1])
    #     #     y_curves.append(surfaces_curves[min_surface_idx][min_curve_idx + 1])
    #     # elif min_curve_idx == 3:
    #     #     x_curves.append(surfaces_curves[min_surface_idx][min_curve_idx - 2])
    #     #     y_curves.append(surfaces_curves[min_surface_idx][min_curve_idx - 3])
    #     #     y_curves.append(surfaces_curves[min_surface_idx][min_curve_idx - 1])
    #     # for i in range(len(surfaces_curves)):
    #     #     if i != min_surface_idx:
    #     #         if x_curves[0] in surfaces_curves[i]:
    #     #             idx = surfaces_curves[i].index(x_curves[0])
    #     #             if idx == 0:
    #     #                 x_curves.append(surfaces_curves[i][idx + 2])
    #     #             elif idx == 1:
    #     #                 x_curves.append(surfaces_curves[i][idx + 2])
    #     #             elif idx == 2:
    #     #                 x_curves.append(surfaces_curves[i][idx - 2])
    #     #             elif idx == 3:
    #     #                 x_curves.append(surfaces_curves[i][idx - 2])
    #     #         elif x_curves[1] in surfaces_curves[i]:
    #     #             idx = surfaces_curves[i].index(x_curves[1])
    #     #             if idx == 0:
    #     #                 x_curves.append(surfaces_curves[i][idx + 2])
    #     #             elif idx == 1:
    #     #                 x_curves.append(surfaces_curves[i][idx + 2])
    #     #             elif idx == 2:
    #     #                 x_curves.append(surfaces_curves[i][idx - 2])
    #     #             elif idx == 3:
    #     #                 x_curves.append(surfaces_curves[i][idx - 2])
    #     #         elif y_curves[0] in surfaces_curves[i]:
    #     #             idx = surfaces_curves[i].index(y_curves[0])
    #     #             if idx == 0:
    #     #                 y_curves.append(surfaces_curves[i][idx + 2])
    #     #             elif idx == 1:
    #     #                 y_curves.append(surfaces_curves[i][idx + 2])
    #     #             elif idx == 2:
    #     #                 y_curves.append(surfaces_curves[i][idx - 2])
    #     #             elif idx == 3:
    #     #                 y_curves.append(surfaces_curves[i][idx - 2])
    #     #         elif y_curves[1] in surfaces_curves[i]:
    #     #             idx = surfaces_curves[i].index(y_curves[1])
    #     #             if idx == 0:
    #     #                 y_curves.append(surfaces_curves[i][idx + 2])
    #     #             elif idx == 1:
    #     #                 y_curves.append(surfaces_curves[i][idx + 2])
    #     #             elif idx == 2:
    #     #                 y_curves.append(surfaces_curves[i][idx - 2])
    #     #             elif idx == 3:
    #     #                 y_curves.append(surfaces_curves[i][idx - 2])
    #     # for i in range(len(surfaces_curves)):
    #     #     for j in range(len(surfaces_curves[i])):
    #     #         curve = surfaces_curves[i][j]
    #     #         if curve not in x_curves and curve not in y_curves and curve not in z_curves:
    #     #             z_curves.append(curve)
    #     # print(x_curves)
    #     # print(y_curves)
    #     # print(z_curves)
    #     # print(self.surfaces_curves)
    #     # self.surfaces_curves = []
    #     # self.surfaces_curves.extend(y_curves)
    #     # self.surfaces_curves.extend(z_curves)
    #     # self.surfaces_curves.extend(x_curves)
    #     # print(self.surfaces_curves)


def correct_primitive(primitive, surfaces_map):
    volumes_dim_tags = map(lambda x: (3, x), primitive.volumes)
    surfaces_dim_tags = gmsh.model.getBoundary(volumes_dim_tags, combined=False)
    if len(surfaces_dim_tags) == 6:
        primitive.surfaces = map(lambda x: surfaces_dim_tags[x][1], surfaces_map)
        correction(primitive)


def primitive_default_surfaces_map():
    """
    Get surfaces map to correct primitive after primitive.create() in __init__
    :return:
    """
    return [2, 0, 1, 3, 4, 5]  # [NY, NX, X, Y, NZ, Z] to [NX, X, NY, Y, NZ, Z]


# Complex
def correct_complex(complex_obj, surfaces_maps):
    for idx, primitive in enumerate(complex_obj.primitives):
        correct_primitive(primitive, surfaces_maps[idx])


# Cylinder
def get_cylinder_primitives_types(cylinder):
    """
    Cylinder primitives types for correction to transfinite
    Coordinate axes directions (before primitive.transform())
    Y
    Z X
    Top and higher cylinder's primitives surfaces map types
                  .
                  .
                  .
                 15
                 15
                 11
    ... 16 16 12  9 10 14 14 ...
                 13
                 17
                 17
                  .
                  .
                  .
    Bottom cylinder's primitives surfaces map types
              .
              .
              .
              6
              6
              2
    ... 7 7 3 0 1 5 5 ...
              4
              8
              8
              .
              .
              .
    :param cylinder:
    :return: ts: primitives types
    """
    n_radii = len(cylinder.radii)
    n_heights = len(cylinder.heights)
    ts = []
    for i in range(n_heights):
        for j in range(n_radii):
            if j == 0:
                if i == 0:
                    start_t = 0
                else:
                    start_t = 9
                ts.append(start_t)
                ts.append(start_t + 1)
                ts.append(start_t + 2)
                ts.append(start_t + 3)
                ts.append(start_t + 4)
            else:
                if i == 0:
                    start_t = 5
                else:
                    start_t = 14
                ts.append(start_t)
                ts.append(start_t + 1)
                ts.append(start_t + 2)
                ts.append(start_t + 3)
    return ts


def get_cylinder_surfaces_maps(cylinder):
    """
    Surfaces maps to correct_complex() function.
    :param cylinder:
    :return: surfaces_maps:
    """
    n_radii = len(cylinder.radii)
    n_heights = len(cylinder.heights)
    if n_radii == 1 and n_heights == 1:
        surfaces_maps = map(
            lambda x:
            cylinder_primitive_surfaces_map_by_primitive_type_1_1[x],
            get_cylinder_primitives_types(cylinder))
    elif n_radii == 1 and n_heights == 2:
        surfaces_maps = map(
            lambda x:
            cylinder_primitive_surfaces_map_by_primitive_type_1_2[x],
            get_cylinder_primitives_types(cylinder))
    elif n_radii == 2 and n_heights == 1:
        surfaces_maps = map(
            lambda x:
            cylinder_primitive_surfaces_map_by_primitive_type_2_1[x],
            get_cylinder_primitives_types(cylinder))
    elif n_radii == 2 and n_heights == 2:
        surfaces_maps = map(
            lambda x:
            cylinder_primitive_surfaces_map_by_primitive_type_2_2[x],
            get_cylinder_primitives_types(cylinder))
    else:
        surfaces_maps = map(
            lambda x:
            cylinder_primitive_surfaces_map_by_primitive_type[x],
            get_cylinder_primitives_types(cylinder))
    return surfaces_maps

# Primitive type's surfaces map for n_radii == 1 and n_heights == 1
cylinder_primitive_surfaces_map_by_primitive_type_1_1 = {
    0: [5, 0, 2, 3, 4, 1],
    1: [0, 5, 2, 3, 4, 1],
    2: [2, 3, 0, 5, 4, 1],
    3: [5, 0, 2, 3, 4, 1],
    4: [2, 3, 5, 0, 1, 4],
}
# Primitive type's surfaces map for n_radii == 1 and n_heights == 2
cylinder_primitive_surfaces_map_by_primitive_type_1_2 = {
    0: [5, 0, 4, 1, 2, 3],
    1: [0, 5, 4, 1, 2, 3],
    2: [1, 4, 0, 5, 2, 3],
    3: [5, 0, 1, 4, 2, 3],
    4: [4, 1, 5, 0, 2, 3],
    9: [2, 3, 1, 4, 0, 5],
    10: [2, 3, 4, 1, 0, 5],
    11: [1, 4, 2, 3, 0, 5],
    12: [3, 2, 4, 1, 0, 5],
    13: [1, 4, 2, 3, 0, 5],
}
# Primitive type's surfaces map for n_radii == 2 and n_heights == 1
cylinder_primitive_surfaces_map_by_primitive_type_2_1 = {
    0: [5, 0, 4, 1, 2, 3],
    1: [0, 5, 4, 1, 2, 3],
    2: [1, 4, 0, 5, 2, 3],
    3: [5, 0, 1, 4, 2, 3],
    4: [4, 1, 5, 0, 2, 3],
    5: [0, 5, 2, 3, 1, 4],
    6: [2, 3, 0, 5, 1, 4],
    7: [5, 0, 2, 3, 1, 4],
    8: [2, 3, 5, 0, 4, 1],
}
# Primitive type's surfaces map for n_radii == 2 and n_heights == 2
cylinder_primitive_surfaces_map_by_primitive_type_2_2 = {
    0: [5, 0, 4, 1, 2, 3],
    1: [0, 5, 4, 1, 2, 3],
    2: [1, 4, 0, 5, 2, 3],
    3: [5, 0, 1, 4, 2, 3],
    4: [4, 1, 5, 0, 2, 3],
    5: [0, 5, 1, 4, 2, 3],
    6: [1, 4, 0, 5, 2, 3],
    7: [5, 0, 1, 4, 2, 3],
    8: [4, 1, 5, 0, 2, 3],
    9: [2, 3, 1, 4, 0, 5],
    10: [2, 3, 4, 1, 0, 5],
    11: [1, 4, 2, 3, 0, 5],
    12: [3, 2, 4, 1, 0, 5],
    13: [1, 4, 2, 3, 0, 5],
    14: [2, 3, 4, 1, 0, 5],
    15: [1, 4, 2, 3, 0, 5],
    16: [3, 2, 4, 1, 0, 5],
    17: [1, 4, 2, 3, 0, 5],
}
# Primitive type's surfaces map for n_radii > 2 and n_heights > 2
cylinder_primitive_surfaces_map_by_primitive_type = {
    0: [5, 0, 4, 1, 2, 3],
    1: [0, 5, 4, 1, 2, 3],
    2: [1, 4, 0, 5, 2, 3],
    3: [5, 0, 1, 4, 2, 3],
    4: [4, 1, 5, 0, 2, 3],
    5: [0, 5, 2, 3, 1, 4],
    6: [2, 3, 0, 5, 1, 4],
    7: [5, 0, 2, 3, 1, 4],
    8: [2, 3, 5, 0, 4, 1],
    9: [2, 3, 1, 4, 0, 5],
    10: [2, 3, 4, 1, 0, 5],
    11: [1, 4, 2, 3, 0, 5],
    12: [3, 2, 4, 1, 0, 5],
    13: [1, 4, 2, 3, 0, 5],
    14: [2, 3, 4, 1, 0, 5],
    15: [1, 4, 2, 3, 0, 5],
    16: [3, 2, 4, 1, 0, 5],
    17: [1, 4, 2, 3, 0, 5],
}







