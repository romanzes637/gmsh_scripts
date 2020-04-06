# import math
from primitive import Primitive
from complex import Complex


class ComplexPrimitive(Complex):
    def __init__(self, factory, point_data=None, transform_data=None,
                 curve_types=None, curve_data=None,
                 transfinite_data=None, transfinite_type=None,
                 volume_name=None, inner_volumes=None, surfaces_names=None,
                 rec=None, trans=None):
        """
        """
        p = Primitive(factory, point_data=point_data,
                      transform_data=transform_data,
                      curve_types=curve_types, curve_data=curve_data,
                      transfinite_data=transfinite_data,
                      transfinite_type=transfinite_type,
                      volume_name=volume_name, inner_volumes=inner_volumes,
                      surfaces_names=surfaces_names,
                      rec=rec, trans=trans)
        primitives = [p]
        Complex(factory, primitives)
        # if len(point_data) == 3:
        #     half_lx = point_data[0] / 2.0
        #     half_ly = point_data[1] / 2.0
        #     half_lz = point_data[2] / 2.0
        #     primitive_lc = None
        #     new_point_data = [
        #         [half_lx, half_ly, -half_lz],
        #         [-half_lx, half_ly, -half_lz],
        #         [-half_lx, -half_ly, -half_lz],
        #         [half_lx, -half_ly, -half_lz],
        #         [half_lx, half_ly, half_lz],
        #         [-half_lx, half_ly, half_lz],
        #         [-half_lx, -half_ly, half_lz],
        #         [half_lx, -half_ly, half_lz]
        #     ]
        # elif len(point_data) == 4:
        #     half_lx = point_data[0] / 2.0
        #     half_ly = point_data[1] / 2.0
        #     half_lz = point_data[2] / 2.0
        #     primitive_lc = point_data[3]
        #     new_point_data = [
        #         [half_lx, half_ly, -half_lz],
        #         [-half_lx, half_ly, -half_lz],
        #         [-half_lx, -half_ly, -half_lz],
        #         [half_lx, -half_ly, -half_lz],
        #         [half_lx, half_ly, half_lz],
        #         [-half_lx, half_ly, half_lz],
        #         [-half_lx, -half_ly, half_lz],
        #         [half_lx, -half_ly, half_lz]
        #     ]
        # else:
        #     primitive_lc = None
        #     new_point_data = [x[:3] for x in point_data]  # slice lc if exist
        # if curve_data is None:
        #     curve_data = [[]] * 12
        # if physical_name is None:
        #     physical_name = ComplexPrimitive.__name__
        # ps_base_points, ps_curves_points = divide_primitive(divide_data,
        #                                                     new_point_data,
        #                                                     curve_data)
        # for i, bps in enumerate(ps_base_points):
        #     if primitive_lc is not None:
        #         new_point_data = [x + [primitive_lc] for x in ps_base_points[i]]
        #     else:
        #         new_point_data = ps_base_points[i]
        #     new_curve_data = list()
        #     for cps in ps_curves_points[i]:
        #         if primitive_lc is not None:
        #             new_curve_data.append([x + [primitive_lc] for x in cps])
        #         else:
        #             new_curve_data.append(cps)
        #     primitives.append(Primitive(
        #         factory, new_point_data, transform_data, curve_types,
        #         new_curve_data, transfinite_data, transfinite_type,
        #         physical_name, inner_volumes, surfaces_names
        #     ))
        Complex.__init__(self, factory, primitives)

# def get_primitives_points(x_lines, y_lines, z_lines):
#     primitives_base_points = []
#     primitives_curves_points = []
#     primitives_curves = []
#     nx = len(x_lines[0][0])
#     ny = len(x_lines[0]) - 1
#     nz = len(x_lines) - 1
#     for k in range(nz):
#         for j in range(ny):
#             for i in range(nx):
#                 x3 = x_lines[k][j][i]
#                 x0 = x_lines[k][j + 1][i]
#                 x2 = x_lines[k + 1][j][i]
#                 x1 = x_lines[k + 1][j + 1][i]
#                 y1 = y_lines[k][i][j]
#                 y0 = y_lines[k][i + 1][j]
#                 y2 = y_lines[k + 1][i][j]
#                 y3 = y_lines[k + 1][i + 1][j]
#                 z2 = z_lines[j][i][k]
#                 z3 = z_lines[j][i + 1][k]
#                 z1 = z_lines[j + 1][i][k]
#                 z0 = z_lines[j + 1][i + 1][k]
#                 primitives_curves.append(
#                     [x0, x1, x2, x3, y0, y1, y2, y3, z0, z1, z2, z3])
#     for primitive_curves in primitives_curves:
#         p0 = primitive_curves[8][0]
#         p1 = primitive_curves[0][0]
#         p2 = primitive_curves[3][0]
#         p3 = primitive_curves[4][0]
#         p4 = primitive_curves[1][-1]
#         p5 = primitive_curves[1][0]
#         p6 = primitive_curves[6][0]
#         p7 = primitive_curves[7][0]
#         primitives_base_points.append([p0, p1, p2, p3, p4, p5, p6, p7])
#         primitive_curves_points = []
#         for curve in primitive_curves:
#             primitive_curves_points.append(curve[1:-1])
#         primitives_curves_points.append(primitive_curves_points)
#     return primitives_base_points, primitives_curves_points
#
#
# def get_lines_between_two_surfaces(s0_lines_parts_points_0,
#                                    s1_lines_parts_points_0, n_parts):
#     lines_points = []
#     for i in range(len(s0_lines_parts_points_0)):
#         s0_line_parts_points_0 = s0_lines_parts_points_0[i]
#         s1_line_parts_points_0 = s1_lines_parts_points_0[i]
#         line_points = []
#         for j in range(len(s0_line_parts_points_0) - 1):
#             s0_line_part_points_0 = s0_line_parts_points_0[j]
#             s1_line_part_points_0 = s1_line_parts_points_0[j]
#             p0 = s0_line_part_points_0[-1]
#             p1 = s1_line_part_points_0[-1]
#             ps = divide_line([p0, p1], n_parts)
#             line_points.append(ps)
#         lines_points.append(line_points)
#     return lines_points
#
#
# def divide_line(ps, n_parts):
#     new_ps = []
#     line_length = 0
#     for i in range(1, len(ps)):
#         p0 = ps[i - 1]
#         p1 = ps[i]
#         r = [p1[0] - p0[0], p1[1] - p0[1], p1[2] - p0[2]]
#         line_length += math.sqrt(r[0] * r[0] + r[1] * r[1] + r[2] * r[2])
#     part_length = line_length / n_parts
#     part_ps = []
#     cnt = part_length
#     for i in range(1, len(ps)):
#         p0 = ps[i - 1]
#         p1 = ps[i]
#         part_ps.append(p0)
#         next_point = False
#         if cnt == 0:
#             new_ps.append(part_ps)
#             part_ps = [p0]
#             cnt = part_length
#         while not next_point:
#             r = [p1[0] - p0[0], p1[1] - p0[1], p1[2] - p0[2]]
#             mag = math.sqrt(r[0] * r[0] + r[1] * r[1] + r[2] * r[2])
#             norm = [r[0] / mag, r[1] / mag, r[2] / mag]
#             tol = 1e-8
#             if (mag - cnt) > tol:
#                 new_p = [
#                     p0[0] + norm[0] * cnt,
#                     p0[1] + norm[1] * cnt,
#                     p0[2] + norm[2] * cnt
#                 ]
#                 p0 = new_p
#                 part_ps.append(p0)
#                 new_ps.append(part_ps)
#                 part_ps = [p0]
#                 cnt = part_length
#             else:
#                 next_point = True
#                 cnt -= mag
#     part_ps.append(ps[len(ps) - 1])
#     new_ps.append(part_ps)
#     assert len(new_ps) == n_parts
#     return new_ps
#
#
# def get_surface_lines(line_points_0_0, line_points_0_1, line_points_1_0,
#                       line_points_1_1):
#     n_points_0 = len(line_points_0_0)
#     n_points_1 = len(line_points_1_0)
#     lines_points_0 = []
#     for i in range(n_points_1 - 1):
#         p0 = line_points_1_0[i][-1]
#         p1 = line_points_1_1[i][-1]
#         ps = divide_line([p0, p1], n_points_0)
#         lines_points_0.append(ps)
#     lines_points_1 = []
#     for i in range(n_points_0 - 1):
#         p0 = line_points_0_0[i][-1]
#         p1 = line_points_0_1[i][-1]
#         ps = divide_line([p0, p1], n_points_1)
#         lines_points_1.append(ps)
#     # Correction
#     for i in range(n_points_1 - 1):
#         for j in range(n_points_0 - 1):
#             # Correct line part point 1
#             x_line_point_1 = lines_points_0[i][j][-1]
#             z_line_point_1 = lines_points_1[j][i][-1]
#             ps = [x_line_point_1, z_line_point_1]
#             centroid = centroid_point(ps)
#             lines_points_0[i][j][-1] = centroid
#             lines_points_1[j][i][-1] = centroid
#             # Change next line part point 0
#             # to corrected current line part point 1
#             lines_points_0[i][j + 1][0] = centroid
#             lines_points_1[j][i + 1][0] = centroid
#     return lines_points_0, lines_points_1
#
#
# def centroid_point(ps):
#     sum_x = 0
#     sum_y = 0
#     sum_z = 0
#     for p in ps:
#         sum_x += p[0]
#         sum_y += p[1]
#         sum_z += p[2]
#     n_p = len(ps)
#     mean_x = sum_x / n_p
#     mean_y = sum_y / n_p
#     mean_z = sum_z / n_p
#     c = [mean_x, mean_y, mean_z]
#     return c
#
#
# def divide_primitive(divide_data, base_points, curves_points):
#     lines = list()
#     for i in range(12):
#         ps = list()
#         if len(curves_points[i]) > 0:
#             ps.append(base_points[Primitive.curves_local_points[i][0]])
#             ps.extend(curves_points[i])
#             ps.append(base_points[Primitive.curves_local_points[i][-1]])
#         else:
#             ps.append(base_points[Primitive.curves_local_points[i][0]])
#             ps.append(base_points[Primitive.curves_local_points[i][-1]])
#         lines.append(ps)
#
#     # Edges lines
#     new_lines = list()
#     nx = divide_data[0]
#     ny = divide_data[1]
#     nz = divide_data[2]
#     for i in range(4):
#         new_lines.append(divide_line(lines[i], nx))
#     for i in range(4, 8):
#         new_lines.append(divide_line(lines[i], ny))
#     for i in range(8, 12):
#         new_lines.append(divide_line(lines[i], nz))
#
#     # Surface NX lines
#     nx_y_lines, nx_z_lines = get_surface_lines(new_lines[5], new_lines[6],
#                                                new_lines[10], new_lines[9])
#     # Surface X
#     x_y_lines, x_z_lines = get_surface_lines(new_lines[4], new_lines[7],
#                                              new_lines[11], new_lines[8])
#     # Surface NY lines
#     ny_x_lines, ny_z_lines = get_surface_lines(new_lines[3], new_lines[2],
#                                                new_lines[10], new_lines[11])
#     # Surface Y lines
#     y_x_lines, y_z_lines_points = get_surface_lines(new_lines[0], new_lines[1],
#                                                     new_lines[9], new_lines[8])
#     # Surface NZ lines
#     nz_x_lines, nz_y_lines = get_surface_lines(new_lines[3], new_lines[0],
#                                                new_lines[5], new_lines[4])
#     # Surface Z lines
#     z_x_lines, z_y_lines = get_surface_lines(new_lines[2], new_lines[1],
#                                              new_lines[6], new_lines[7])
#
#     # Volume lines
#     nx_x_lines = get_lines_between_two_surfaces(nx_y_lines, x_y_lines, nx)
#     ny_y_lines = get_lines_between_two_surfaces(ny_x_lines, y_x_lines, ny)
#     nz_z_lines = get_lines_between_two_surfaces(nz_x_lines, z_x_lines, nz)
#
#     # Volume lines correction
#     correct_volume_lines(nx_x_lines, ny_y_lines, nz_z_lines)
#
#     # Sum
#     x_lines = list()
#     first_layer_lines = list()
#     first_layer_lines.append(new_lines[3])
#     for line_points in nz_x_lines:
#         first_layer_lines.append(line_points)
#     first_layer_lines.append(new_lines[0])
#     x_lines.append(first_layer_lines)
#     for i in range(len(ny_x_lines)):
#         layer_lines = list()
#         layer_lines.append(ny_x_lines[i])
#         for line_points in nx_x_lines[i]:
#             layer_lines.append(line_points)
#         layer_lines.append(y_x_lines[i])
#         x_lines.append(layer_lines)
#     last_layer_lines = list()
#     last_layer_lines.append(new_lines[2])
#     for line_points in z_x_lines:
#         last_layer_lines.append(line_points)
#     last_layer_lines.append(new_lines[1])
#     x_lines.append(last_layer_lines)
#
#     y_lines = list()
#     first_layer_lines = list()
#     first_layer_lines.append(new_lines[5])
#     for line_points in nz_y_lines:
#         first_layer_lines.append(line_points)
#     first_layer_lines.append(new_lines[4])
#     y_lines.append(first_layer_lines)
#     for i in range(len(nx_y_lines)):
#         layer_lines = list()
#         layer_lines.append(nx_y_lines[i])
#         for line_points in ny_y_lines[i]:
#             layer_lines.append(line_points)
#         layer_lines.append(x_y_lines[i])
#         y_lines.append(layer_lines)
#     last_layer_lines = list()
#     last_layer_lines.append(new_lines[6])
#     for line_points in z_y_lines:
#         last_layer_lines.append(line_points)
#     last_layer_lines.append(new_lines[7])
#     y_lines.append(last_layer_lines)
#
#     z_lines = list()
#     first_layer_lines = list()
#     first_layer_lines.append(new_lines[10])
#     for line_points in ny_z_lines:
#         first_layer_lines.append(line_points)
#     first_layer_lines.append(new_lines[11])
#     z_lines.append(first_layer_lines)
#     for i in range(len(nx_z_lines)):
#         layer_lines = list()
#         layer_lines.append(nx_z_lines[i])
#         for line_points in nz_z_lines[i]:
#             layer_lines.append(line_points)
#         layer_lines.append(x_z_lines[i])
#         z_lines.append(layer_lines)
#     last_layer_lines = list()
#     last_layer_lines.append(new_lines[9])
#     for line_points in y_z_lines_points:
#         last_layer_lines.append(line_points)
#     last_layer_lines.append(new_lines[8])
#     z_lines.append(last_layer_lines)
#
#     primitives_base_points, primitives_curves_points = get_primitives_points(
#         x_lines, y_lines, z_lines)
#
#     return primitives_base_points, primitives_curves_points
#
#
# # FIXME bug with divide_data [1, 2, 3]: ny = len(ny_y_lines[0][0])
# def correct_volume_lines(nx_x_lines, ny_y_lines, nz_z_lines):
#     # FIXME plug to one layer
#     if len(nx_x_lines) == 0 or len(ny_y_lines) == 0 or len(nz_z_lines) == 0:
#         return
#     nx = len(nx_x_lines[0][0])
#     ny = len(ny_y_lines[0][0])
#     nz = len(nz_z_lines[0][0])
#     for k in range(nz - 1):
#         for j in range(ny - 1):
#             for i in range(nx - 1):
#                 # Correct line part point 1
#                 x_line_point_1 = nx_x_lines[k][j][i][-1]
#                 y_line_point_1 = ny_y_lines[k][i][j][-1]
#                 z_line_point_1 = nz_z_lines[j][i][k][-1]
#                 ps = [x_line_point_1, y_line_point_1, z_line_point_1]
#                 centroid = centroid_point(ps)
#                 nx_x_lines[k][j][i][-1] = centroid
#                 ny_y_lines[k][i][j][-1] = centroid
#                 nz_z_lines[j][i][k][-1] = centroid
#                 # Change next line part point 0
#                 # to corrected curtent line part point 1
#                 nx_x_lines[k][j][i + 1][0] = centroid
#                 ny_y_lines[k][i][j + 1][0] = centroid
#                 nz_z_lines[j][i][k + 1][0] = centroid
