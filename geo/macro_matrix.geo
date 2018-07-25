Include "macro_primitive.geo";

Macro matrix

matrix_nxss = {};
matrix_xss = {};
matrix_nyss = {};
matrix_yss = {};
matrix_nzss = {};
matrix_zss = {};
matrix_pvs = {};

For matrix_i In {0 : #matrix_x_centers[]-1}
  For matrix_j In {0 : #matrix_y_centers[]-1}
    For matrix_k In {0 : #matrix_z_centers[]-1}
      matrix_global_idx = matrix_i + matrix_j*#matrix_x_centers[] + matrix_k*#matrix_x_centers[]*#matrix_y_centers[];
      If (matrix_type_map[matrix_global_idx] == 0)
      Else
        primitive_rox = matrix_rox; primitive_roy = matrix_roy; primitive_roz = matrix_roz; // Local Rotation origin
        primitive_rax = matrix_rax; primitive_ray = matrix_ray; primitive_raz = matrix_raz; // Local Rotation angle
        primitive_t_1 = matrix_t_1s[matrix_i]; primitive_t_1_1 = matrix_t_1s_1s[matrix_i]; primitive_t_1_2 = matrix_t_1s_2s[matrix_i]; // N rows nodes, progression, bump
        primitive_t_2 = matrix_t_2s[matrix_j]; primitive_t_2_1 = matrix_t_2s_1s[matrix_j]; primitive_t_2_2 = matrix_t_2s_2s[matrix_j]; // N cols nodes, progression, bump
        primitive_t_3 = matrix_t_3s[matrix_k]; primitive_t_3_1 = matrix_t_3s_1s[matrix_k]; primitive_t_3_2 = matrix_t_3s_2s[matrix_k]; // N tabs nodes, progression, bump
        primitive_t_4 = matrix_t_4; // Recombine to Hex?
        primitive_t_5s = {0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0}; // Curves
        primitive_t_6 = 0; // Structured mesh type
        primitive_t_7s = {}; // Inner Surfaces
        primitive_t_8s = {0, 0, 0, 0, 0, 0}; // Surfaces for changes
        primitive_t_9s = {}; // Global Rotations and Translations
        primitive_t_10s = {0, 0, 0, 0, 0, 0}; // Plane Surfaces
        If (matrix_type_map[matrix_global_idx] == 1) // HEXAHEDRON
          matrix_type_x_1 = matrix_x_starts[matrix_i] - matrix_x_centers[matrix_i];
          matrix_type_x_2 = matrix_x_ends[matrix_i] - matrix_x_centers[matrix_i];
          matrix_type_y_1 = matrix_y_starts[matrix_j] - matrix_y_centers[matrix_j];
          matrix_type_y_2 = matrix_y_ends[matrix_j] - matrix_y_centers[matrix_j];
          matrix_type_z_1 = matrix_z_starts[matrix_k] - matrix_z_centers[matrix_k];
          matrix_type_z_2 = matrix_z_ends[matrix_k] - matrix_z_centers[matrix_k];
          primitive_lcs = {
            matrix_lc, matrix_lc, matrix_lc, matrix_lc,
            matrix_lc, matrix_lc, matrix_lc, matrix_lc
          };
          primitive_xs = {
            matrix_type_x_2, matrix_type_x_1, matrix_type_x_1, matrix_type_x_2,
            matrix_type_x_2, matrix_type_x_1, matrix_type_x_1, matrix_type_x_2
          };
          primitive_ys = {
            matrix_type_y_2, matrix_type_y_2, matrix_type_y_1, matrix_type_y_1, 
            matrix_type_y_2, matrix_type_y_2, matrix_type_y_1, matrix_type_y_1
          };
          primitive_zs = {
            matrix_type_z_1, matrix_type_z_1, matrix_type_z_1, matrix_type_z_1, 
            matrix_type_z_2, matrix_type_z_2, matrix_type_z_2, matrix_type_z_2
          };
          primitive_ox = matrix_x_centers[matrix_i]; primitive_oy = matrix_y_centers[matrix_j]; primitive_oz = matrix_z_centers[matrix_k]; // Origin: x, y, z
        ElseIf (matrix_type_map[matrix_global_idx] == 2) // CYLINDER HALF SHELL X
          matrix_type_r = matrix_x_ends[matrix_i] - matrix_x_r;
          matrix_type_x_1 = matrix_x_starts[matrix_i] - matrix_x_centers[matrix_i];
          matrix_type_x_2 = matrix_x_r + matrix_type_r/Sqrt(2) - matrix_x_centers[matrix_i];
          matrix_type_x_r = matrix_x_r - matrix_x_centers[matrix_i];
          matrix_type_y_1 = matrix_y_starts[matrix_j] - matrix_y_centers[matrix_j];
          matrix_type_y_1_2 = matrix_y_r - matrix_type_r/Sqrt(2) - matrix_y_centers[matrix_j];
          matrix_type_y_2 = matrix_y_ends[matrix_j] - matrix_y_centers[matrix_j];
          matrix_type_y_2_2 = matrix_y_r + matrix_type_r/Sqrt(2) - matrix_y_centers[matrix_j];
          matrix_type_y_r = matrix_y_r - matrix_y_centers[matrix_j];
          matrix_type_z_1 = matrix_z_starts[matrix_k] - matrix_z_centers[matrix_k];
          matrix_type_z_2 = matrix_z_ends[matrix_k] - matrix_z_centers[matrix_k];
          primitive_lcs = {
              matrix_lc, matrix_lc, matrix_lc, matrix_lc,
              matrix_lc, matrix_lc, matrix_lc, matrix_lc,
              matrix_lc, matrix_lc, matrix_lc, matrix_lc,
              matrix_lc, matrix_lc, matrix_lc, matrix_lc,
              matrix_lc, matrix_lc, matrix_lc, matrix_lc
          };
          primitive_xs = {
            matrix_type_x_2, matrix_type_x_1, matrix_type_x_1, matrix_type_x_2,
            matrix_type_x_2, matrix_type_x_1, matrix_type_x_1, matrix_type_x_2,
            0, 0, 0, 0,
            matrix_type_x_r, 0, 0, matrix_type_x_r,
            0, 0, 0, 0
          };
          primitive_ys = {
            matrix_type_y_2_2, matrix_type_y_2, matrix_type_y_1, matrix_type_y_1_2,
            matrix_type_y_2_2, matrix_type_y_2, matrix_type_y_1, matrix_type_y_1_2,
            0, 0, 0, 0,
            matrix_type_y_r, 0, 0, matrix_type_y_r,
            0, 0, 0, 0
          };
          primitive_zs = {
            matrix_type_z_1, matrix_type_z_1, matrix_type_z_1, matrix_type_z_1, 
            matrix_type_z_2, matrix_type_z_2, matrix_type_z_2, matrix_type_z_2,
            0, 0, 0, 0,
            matrix_type_z_1, 0, 0, matrix_type_z_2,
            0, 0, 0, 0
          };
          primitive_ox = matrix_x_centers[matrix_i]; primitive_oy = matrix_y_centers[matrix_j]; primitive_oz = matrix_z_centers[matrix_k]; // Origin: x, y, z
          primitive_t_5s = {0, 0, 0, 0, 1, 0, 0, 1, 0, 0, 0, 0};
        ElseIf (matrix_type_map[matrix_global_idx] == 3) // CYLINDER HALF SHELL Y
          matrix_type_r = matrix_y_ends[matrix_j] - matrix_y_r;
          matrix_type_x_1 = matrix_x_starts[matrix_i] - matrix_x_centers[matrix_i];
          matrix_type_x_1_2 = matrix_x_r - matrix_type_r/Sqrt(2) - matrix_x_centers[matrix_i];
          matrix_type_x_2 = matrix_x_ends[matrix_i] - matrix_x_centers[matrix_i];
          matrix_type_x_2_2 = matrix_x_r + matrix_type_r/Sqrt(2) - matrix_x_centers[matrix_i];
          matrix_type_x_r = matrix_x_r - matrix_x_centers[matrix_i];
          matrix_type_y_1 = matrix_y_starts[matrix_j] - matrix_y_centers[matrix_j];
          matrix_type_y_2 = matrix_y_r + matrix_type_r/Sqrt(2) - matrix_y_centers[matrix_j];
          matrix_type_y_r = matrix_y_r - matrix_y_centers[matrix_j];
          matrix_type_z_1 = matrix_z_starts[matrix_k] - matrix_z_centers[matrix_k];
          matrix_type_z_2 = matrix_z_ends[matrix_k] - matrix_z_centers[matrix_k];
          primitive_lcs = {
              matrix_lc, matrix_lc, matrix_lc, matrix_lc,
              matrix_lc, matrix_lc, matrix_lc, matrix_lc,
              matrix_lc, matrix_lc, matrix_lc, matrix_lc,
              matrix_lc, matrix_lc, matrix_lc, matrix_lc,
              matrix_lc, matrix_lc, matrix_lc, matrix_lc
          };
          primitive_xs = {
              matrix_type_x_2_2, matrix_type_x_1_2, matrix_type_x_1, matrix_type_x_2,
              matrix_type_x_2_2, matrix_type_x_1_2, matrix_type_x_1, matrix_type_x_2,
              matrix_type_x_r, matrix_type_x_r, 0, 0,
              0, 0, 0, 0,
              0, 0, 0, 0
          };
          primitive_ys = {
            matrix_type_y_2, matrix_type_y_2, matrix_type_y_1, matrix_type_y_1,
            matrix_type_y_2, matrix_type_y_2, matrix_type_y_1, matrix_type_y_1,
            matrix_type_y_r, matrix_type_y_r, 0, 0,
            0, 0, 0, 0,
            0, 0, 0, 0
          };
          primitive_zs = {
            matrix_type_z_1, matrix_type_z_1, matrix_type_z_1, matrix_type_z_1, 
            matrix_type_z_2, matrix_type_z_2, matrix_type_z_2, matrix_type_z_2,
            matrix_type_z_1, matrix_type_z_2, 0, 0,
            0, 0, 0, 0,
            0, 0, 0, 0
          };
          primitive_ox = matrix_x_centers[matrix_i]; primitive_oy = matrix_y_centers[matrix_j]; primitive_oz = matrix_z_centers[matrix_k]; // Origin: x, y, z
          primitive_t_5s = {1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0};
        ElseIf (matrix_type_map[matrix_global_idx] == 4) // CYLINDER HALF SHELL NX
          matrix_type_r = matrix_x_r - matrix_x_ends[matrix_i];
          matrix_type_x_1 = matrix_x_r - matrix_type_r/Sqrt(2) - matrix_x_centers[matrix_i];
          matrix_type_x_2 = matrix_x_ends[matrix_i] - matrix_x_centers[matrix_i];
          matrix_type_x_r = matrix_x_r - matrix_x_centers[matrix_i];
          matrix_type_y_1 = matrix_y_starts[matrix_j] - matrix_y_centers[matrix_j];
          matrix_type_y_1_2 = matrix_y_r - matrix_type_r/Sqrt(2) - matrix_y_centers[matrix_j];
          matrix_type_y_2 = matrix_y_ends[matrix_j] - matrix_y_centers[matrix_j];
          matrix_type_y_2_2 = matrix_y_r + matrix_type_r/Sqrt(2) - matrix_y_centers[matrix_j];
          matrix_type_y_r = matrix_y_r - matrix_y_centers[matrix_j];
          matrix_type_z_1 = matrix_z_starts[matrix_k] - matrix_z_centers[matrix_k];
          matrix_type_z_2 = matrix_z_ends[matrix_k] - matrix_z_centers[matrix_k];
          primitive_lcs = {
              matrix_lc, matrix_lc, matrix_lc, matrix_lc,
              matrix_lc, matrix_lc, matrix_lc, matrix_lc,
              matrix_lc, matrix_lc, matrix_lc, matrix_lc,
              matrix_lc, matrix_lc, matrix_lc, matrix_lc,
              matrix_lc, matrix_lc, matrix_lc, matrix_lc
          };
          primitive_xs = {
              matrix_type_x_2, matrix_type_x_1, matrix_type_x_1, matrix_type_x_2,
              matrix_type_x_2, matrix_type_x_1, matrix_type_x_1, matrix_type_x_2,
              0, 0, 0, 0,
              matrix_type_x_r, matrix_type_x_r, matrix_type_x_r, matrix_type_x_r,
              0, 0, 0, 0
          };
          primitive_ys = {
              matrix_type_y_2, matrix_type_y_2_2, matrix_type_y_1_2, matrix_type_y_1,
              matrix_type_y_2, matrix_type_y_2_2, matrix_type_y_1_2, matrix_type_y_1,
              0, 0, 0, 0,
              matrix_type_y_r, matrix_type_y_r, matrix_type_y_r, matrix_type_y_r,
              0, 0, 0, 0
          };
          primitive_zs = {
              matrix_type_z_1, matrix_type_z_1, matrix_type_z_1, matrix_type_z_1, 
              matrix_type_z_2, matrix_type_z_2, matrix_type_z_2, matrix_type_z_2,
              0, 0, 0, 0,
              matrix_type_z_1, matrix_type_z_1, matrix_type_z_2, matrix_type_z_2,
              0, 0, 0, 0
          };
          primitive_ox = matrix_x_centers[matrix_i]; primitive_oy = matrix_y_centers[matrix_j]; primitive_oz = matrix_z_centers[matrix_k]; // Origin: x, y, z
          primitive_t_5s = {0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0};
          primitive_t_6 = 1;
        ElseIf (matrix_type_map[matrix_global_idx] == 5)  // CYLINDER HALF SHELL NY
          matrix_type_r = matrix_y_r - matrix_y_starts[matrix_j];
          matrix_type_x_1 = matrix_x_starts[matrix_i] - matrix_x_centers[matrix_i];
          matrix_type_x_1_2 = matrix_x_r - matrix_type_r/Sqrt(2) - matrix_x_centers[matrix_i];
          matrix_type_x_2 = matrix_x_ends[matrix_i] - matrix_x_centers[matrix_i];
          matrix_type_x_2_2 = matrix_x_r + matrix_type_r/Sqrt(2) - matrix_x_centers[matrix_i];
          matrix_type_x_r = matrix_x_r - matrix_x_centers[matrix_i];
          matrix_type_y_1 = matrix_y_r - matrix_type_r/Sqrt(2) - matrix_y_centers[matrix_j];
          matrix_type_y_2 = matrix_y_ends[matrix_j] - matrix_y_centers[matrix_j];
          matrix_type_y_r = matrix_y_r - matrix_y_centers[matrix_j];
          matrix_type_z_1 = matrix_z_starts[matrix_k] - matrix_z_centers[matrix_k];
          matrix_type_z_2 = matrix_z_ends[matrix_k] - matrix_z_centers[matrix_k];
          primitive_lcs = {
            matrix_lc, matrix_lc, matrix_lc, matrix_lc,
            matrix_lc, matrix_lc, matrix_lc, matrix_lc,
            matrix_lc, matrix_lc, matrix_lc, matrix_lc,
            matrix_lc, matrix_lc, matrix_lc, matrix_lc,
            matrix_lc, matrix_lc, matrix_lc, matrix_lc
          };
          primitive_xs = {
            matrix_type_x_2, matrix_type_x_1, matrix_type_x_1_2, matrix_type_x_2_2,
            matrix_type_x_2, matrix_type_x_1, matrix_type_x_1_2, matrix_type_x_2_2,
            0, 0, matrix_type_x_r, matrix_type_x_r,
            0, 0, 0, 0,
            0, 0, 0, 0
          };
          primitive_ys = {
            matrix_type_y_2, matrix_type_y_2, matrix_type_y_1, matrix_type_y_1,
            matrix_type_y_2, matrix_type_y_2, matrix_type_y_1, matrix_type_y_1,
            0, 0, matrix_type_y_r, matrix_type_y_r,
            0, 0, 0, 0,
            0, 0, 0, 0
          };
          primitive_zs = {
            matrix_type_z_1, matrix_type_z_1, matrix_type_z_1, matrix_type_z_1, 
            matrix_type_z_2, matrix_type_z_2, matrix_type_z_2, matrix_type_z_2,
            0, 0, matrix_type_z_2, matrix_type_z_1,
            0, 0, 0, 0,
            0, 0, 0, 0
          };
          primitive_ox = matrix_x_centers[matrix_i]; primitive_oy = matrix_y_centers[matrix_j]; primitive_oz = matrix_z_centers[matrix_k]; // Origin: x, y, z
          primitive_t_5s = {0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0};
          primitive_t_6 = 3;
        ElseIf (matrix_type_map[matrix_global_idx] == 6)  // CYLINDER SHELL X
          matrix_type_r = matrix_x_starts[matrix_i] - matrix_x_r;
          matrix_type_r_2 = matrix_x_ends[matrix_i] - matrix_x_r;
          matrix_type_x_1 = matrix_x_r + matrix_type_r/Sqrt(2) - matrix_x_centers[matrix_i];
          matrix_type_x_2 = matrix_x_r + matrix_type_r_2/Sqrt(2) - matrix_x_centers[matrix_i];
          matrix_type_x_r = matrix_x_r - matrix_x_centers[matrix_i];
          matrix_type_y_1 = matrix_y_r - matrix_type_r/Sqrt(2) - matrix_y_centers[matrix_j];
          matrix_type_y_1_2 = matrix_y_r - matrix_type_r_2/Sqrt(2) - matrix_y_centers[matrix_j];
          matrix_type_y_2 = matrix_y_r + matrix_type_r/Sqrt(2) - matrix_y_centers[matrix_j];
          matrix_type_y_2_2 = matrix_y_r + matrix_type_r_2/Sqrt(2) - matrix_y_centers[matrix_j];
          matrix_type_y_r = matrix_y_r - matrix_y_centers[matrix_j];
          matrix_type_z_1 = matrix_z_starts[matrix_k] - matrix_z_centers[matrix_k];
          matrix_type_z_2 = matrix_z_ends[matrix_k] - matrix_z_centers[matrix_k];
          primitive_lcs = {
            matrix_lc, matrix_lc, matrix_lc, matrix_lc,
            matrix_lc, matrix_lc, matrix_lc, matrix_lc,
            matrix_lc, matrix_lc, matrix_lc, matrix_lc,
            matrix_lc, matrix_lc, matrix_lc, matrix_lc,
            matrix_lc, matrix_lc, matrix_lc, matrix_lc
          };
          primitive_xs = {
            matrix_type_x_2, matrix_type_x_1, matrix_type_x_1, matrix_type_x_2,
            matrix_type_x_2, matrix_type_x_1, matrix_type_x_1, matrix_type_x_2,
            0, 0, 0, 0,
            matrix_type_x_r, matrix_type_x_r, matrix_type_x_r, matrix_type_x_r,
            0, 0, 0, 0
          };
          primitive_ys = {
            matrix_type_y_2_2, matrix_type_y_2, matrix_type_y_1, matrix_type_y_1_2,
            matrix_type_y_2_2, matrix_type_y_2, matrix_type_y_1, matrix_type_y_1_2,
            0, 0, 0, 0,
            matrix_type_y_r, matrix_type_y_r, matrix_type_y_r, matrix_type_y_r,
            0, 0, 0, 0
          };
          primitive_zs = {
            matrix_type_z_1, matrix_type_z_1, matrix_type_z_1, matrix_type_z_1, 
            matrix_type_z_2, matrix_type_z_2, matrix_type_z_2, matrix_type_z_2, 
            0, 0, 0, 0,
            matrix_type_z_1, matrix_type_z_1, matrix_type_z_2, matrix_type_z_2,
            0, 0, 0, 0
          };
          primitive_ox = matrix_x_centers[matrix_i]; primitive_oy = matrix_y_centers[matrix_j]; primitive_oz = matrix_z_centers[matrix_k]; // Origin: x, y, z
          primitive_t_5s = {0, 0, 0, 0, 1, 1, 1, 1, 0, 0, 0, 0};
        ElseIf (matrix_type_map[matrix_global_idx] == 7) // CYLINDER SHELL Y
          matrix_type_r = matrix_y_starts[matrix_j] - matrix_y_r;
          matrix_type_r_2 = matrix_y_ends[matrix_j] - matrix_y_r;
          matrix_type_x_1 = matrix_x_r - matrix_type_r/Sqrt(2) - matrix_x_centers[matrix_i];
          matrix_type_x_1_2 = matrix_x_r - matrix_type_r_2/Sqrt(2) - matrix_x_centers[matrix_i];
          matrix_type_x_2 = matrix_x_r + matrix_type_r/Sqrt(2) - matrix_x_centers[matrix_i];
          matrix_type_x_2_2 = matrix_x_r + matrix_type_r_2/Sqrt(2) - matrix_x_centers[matrix_i];
          matrix_type_x_r = matrix_x_r - matrix_x_centers[matrix_i];
          matrix_type_y_1 = matrix_y_r + matrix_type_r/Sqrt(2) - matrix_y_centers[matrix_j];
          matrix_type_y_2 = matrix_y_r + matrix_type_r_2/Sqrt(2) - matrix_y_centers[matrix_j];
          matrix_type_y_r = matrix_y_r - matrix_y_centers[matrix_j];
          matrix_type_z_1 = matrix_z_starts[matrix_k] - matrix_z_centers[matrix_k];
          matrix_type_z_2 = matrix_z_ends[matrix_k] - matrix_z_centers[matrix_k];
          primitive_lcs = {
            matrix_lc, matrix_lc, matrix_lc, matrix_lc,
            matrix_lc, matrix_lc, matrix_lc, matrix_lc,
            matrix_lc, matrix_lc, matrix_lc, matrix_lc,
            matrix_lc, matrix_lc, matrix_lc, matrix_lc,
            matrix_lc, matrix_lc, matrix_lc, matrix_lc
          };
          primitive_xs = {
            matrix_type_x_2_2, matrix_type_x_1_2, matrix_type_x_1, matrix_type_x_2,
            matrix_type_x_2_2, matrix_type_x_1_2, matrix_type_x_1, matrix_type_x_2,
            matrix_type_x_r, matrix_type_x_r, matrix_type_x_r, matrix_type_x_r,
            0, 0, 0, 0,
            0, 0, 0, 0
          };
          primitive_ys = {
            matrix_type_y_2, matrix_type_y_2, matrix_type_y_1, matrix_type_y_1,
            matrix_type_y_2, matrix_type_y_2, matrix_type_y_1, matrix_type_y_1,
            matrix_type_y_r, matrix_type_y_r, matrix_type_y_r, matrix_type_y_r,
            0, 0, 0, 0,
            0, 0, 0, 0
          };
          primitive_zs = {
            matrix_type_z_1, matrix_type_z_1, matrix_type_z_1, matrix_type_z_1, 
            matrix_type_z_2, matrix_type_z_2, matrix_type_z_2, matrix_type_z_2,
            matrix_type_z_1, matrix_type_z_2, matrix_type_z_2, matrix_type_z_1,
            0, 0, 0, 0,
            0, 0, 0, 0
          };
          primitive_ox = matrix_x_centers[matrix_i]; primitive_oy = matrix_y_centers[matrix_j]; primitive_oz = matrix_z_centers[matrix_k]; // Origin: x, y, z
          primitive_t_5s = {1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0};
        ElseIf (matrix_type_map[matrix_global_idx] == 8) // CYLINDER SHELL NX
          matrix_type_r = matrix_x_r - matrix_x_ends[matrix_i];
          matrix_type_r_2 = matrix_x_r - matrix_x_starts[matrix_i];
          matrix_type_x_1 = matrix_x_r - matrix_type_r_2/Sqrt(2) - matrix_x_centers[matrix_i];
          matrix_type_x_2 = matrix_x_r - matrix_type_r/Sqrt(2) - matrix_x_centers[matrix_i];
          matrix_type_x_r = matrix_x_r - matrix_x_centers[matrix_i];
          matrix_type_y_1 = matrix_y_r - matrix_type_r/Sqrt(2) - matrix_y_centers[matrix_j];
          matrix_type_y_1_2 = matrix_y_r - matrix_type_r_2/Sqrt(2) - matrix_y_centers[matrix_j];
          matrix_type_y_2 = matrix_y_r + matrix_type_r/Sqrt(2) - matrix_y_centers[matrix_j];
          matrix_type_y_2_2 = matrix_y_r + matrix_type_r_2/Sqrt(2) - matrix_y_centers[matrix_j];
          matrix_type_y_r = matrix_y_r - matrix_y_centers[matrix_j];
          matrix_type_z_1 = matrix_z_starts[matrix_k] - matrix_z_centers[matrix_k];
          matrix_type_z_2 = matrix_z_ends[matrix_k] - matrix_z_centers[matrix_k];
          primitive_lcs = {
              matrix_lc, matrix_lc, matrix_lc, matrix_lc,
              matrix_lc, matrix_lc, matrix_lc, matrix_lc,
              matrix_lc, matrix_lc, matrix_lc, matrix_lc,
              matrix_lc, matrix_lc, matrix_lc, matrix_lc,
              matrix_lc, matrix_lc, matrix_lc, matrix_lc
          };
          primitive_xs = {
              matrix_type_x_2, matrix_type_x_1, matrix_type_x_1, matrix_type_x_2,
              matrix_type_x_2, matrix_type_x_1, matrix_type_x_1, matrix_type_x_2,
              0, 0, 0, 0,
              matrix_type_x_r, matrix_type_x_r, matrix_type_x_r, matrix_type_x_r,
              0, 0, 0, 0
          };
          primitive_ys = {
              matrix_type_y_2, matrix_type_y_2_2, matrix_type_y_1_2, matrix_type_y_1,
              matrix_type_y_2, matrix_type_y_2_2, matrix_type_y_1_2, matrix_type_y_1,
              0, 0, 0, 0,
              matrix_type_y_r, matrix_type_y_r, matrix_type_y_r, matrix_type_y_r,
              0, 0, 0, 0
          };
          primitive_zs = {
              matrix_type_z_1, matrix_type_z_1, matrix_type_z_1, matrix_type_z_1, 
              matrix_type_z_2, matrix_type_z_2, matrix_type_z_2, matrix_type_z_2,
              0, 0, 0, 0,
              matrix_type_z_1, matrix_type_z_1, matrix_type_z_2, matrix_type_z_2,
              0, 0, 0, 0
          };
          primitive_ox = matrix_x_centers[matrix_i]; primitive_oy = matrix_y_centers[matrix_j]; primitive_oz = matrix_z_centers[matrix_k]; // Origin: x, y, z
          primitive_t_5s = {0, 0, 0, 0, 1, 1, 1, 1, 0, 0, 0, 0};
          primitive_t_6 = 1;
        ElseIf (matrix_type_map[matrix_global_idx] == 9) // CYLINDER SHELL NY
          matrix_type_r = matrix_y_r - matrix_y_ends[matrix_j];
          matrix_type_r_2 = matrix_y_r - matrix_y_starts[matrix_j];
          matrix_type_x_1 = matrix_x_r - matrix_type_r/Sqrt(2) - matrix_x_centers[matrix_i];
          matrix_type_x_1_2 = matrix_x_r - matrix_type_r_2/Sqrt(2) - matrix_x_centers[matrix_i];
          matrix_type_x_2 = matrix_x_r + matrix_type_r/Sqrt(2) - matrix_x_centers[matrix_i];
          matrix_type_x_2_2 = matrix_x_r + matrix_type_r_2/Sqrt(2) - matrix_x_centers[matrix_i];
          matrix_type_x_r = matrix_x_r - matrix_x_centers[matrix_i];
          matrix_type_y_1 = matrix_y_r - matrix_type_r_2/Sqrt(2) - matrix_y_centers[matrix_j];
          matrix_type_y_2 = matrix_y_r - matrix_type_r/Sqrt(2) - matrix_y_centers[matrix_j];
          matrix_type_y_r = matrix_y_r - matrix_y_centers[matrix_j];
          matrix_type_z_1 = matrix_z_starts[matrix_k] - matrix_z_centers[matrix_k];
          matrix_type_z_2 = matrix_z_ends[matrix_k] - matrix_z_centers[matrix_k];
          primitive_lcs = {
            matrix_lc, matrix_lc, matrix_lc, matrix_lc,
            matrix_lc, matrix_lc, matrix_lc, matrix_lc,
            matrix_lc, matrix_lc, matrix_lc, matrix_lc,
            matrix_lc, matrix_lc, matrix_lc, matrix_lc,
            matrix_lc, matrix_lc, matrix_lc, matrix_lc
          };
          primitive_xs = {
            matrix_type_x_2, matrix_type_x_1, matrix_type_x_1_2, matrix_type_x_2_2,
            matrix_type_x_2, matrix_type_x_1, matrix_type_x_1_2, matrix_type_x_2_2,
            matrix_type_x_r, matrix_type_x_r, matrix_type_x_r, matrix_type_x_r,
            0, 0, 0, 0,
            0, 0, 0, 0
          };
          primitive_ys = {
            matrix_type_y_2, matrix_type_y_2, matrix_type_y_1, matrix_type_y_1,
            matrix_type_y_2, matrix_type_y_2, matrix_type_y_1, matrix_type_y_1,
            matrix_type_y_r, matrix_type_y_r, matrix_type_y_r, matrix_type_y_r,
            0, 0, 0, 0,
            0, 0, 0, 0
          };
          primitive_zs = {
            matrix_type_z_1, matrix_type_z_1, matrix_type_z_1, matrix_type_z_1, 
            matrix_type_z_2, matrix_type_z_2, matrix_type_z_2, matrix_type_z_2,
            matrix_type_z_1, matrix_type_z_2, matrix_type_z_2, matrix_type_z_1,
            0, 0, 0, 0,
            0, 0, 0, 0
          };
          primitive_ox = matrix_x_centers[matrix_i]; primitive_oy = matrix_y_centers[matrix_j]; primitive_oz = matrix_z_centers[matrix_k]; // Origin: x, y, z
          primitive_t_5s = {1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0};
          primitive_t_6 = 3;
        ElseIf (matrix_type_map[matrix_global_idx] == 10) // CYLINDER HALF SHELL X SYMMETRIC
          matrix_type_r = matrix_x_ends[matrix_i] - matrix_x_r;
          matrix_type_x_1 = matrix_x_starts[matrix_i] - matrix_x_centers[matrix_i];
          matrix_type_x_2 = matrix_x_r + matrix_type_r/Sqrt(2) - matrix_x_centers[matrix_i];
          matrix_type_x_r = matrix_x_r - matrix_x_centers[matrix_i];
          matrix_type_y_1 = matrix_y_starts[matrix_j] - matrix_y_centers[matrix_j];
          matrix_type_y_1_2 = matrix_y_r - matrix_type_r/Sqrt(2) - matrix_y_centers[matrix_j];
          matrix_type_y_2 = matrix_y_ends[matrix_j] - matrix_y_centers[matrix_j];
          matrix_type_y_2_2 = matrix_y_r + matrix_type_r/Sqrt(2) - matrix_y_centers[matrix_j];
          matrix_type_y_r = matrix_y_r - matrix_y_centers[matrix_j];
          matrix_type_z_1 = matrix_z_starts[matrix_k] - matrix_z_centers[matrix_k];
          matrix_type_z_2 = matrix_z_ends[matrix_k] - matrix_z_centers[matrix_k];
          primitive_lcs = {
            matrix_lc, matrix_lc, matrix_lc, matrix_lc,
            matrix_lc, matrix_lc, matrix_lc, matrix_lc,
            matrix_lc, matrix_lc, matrix_lc, matrix_lc,
            matrix_lc, matrix_lc, matrix_lc, matrix_lc,
            matrix_lc, matrix_lc, matrix_lc, matrix_lc
          };
          primitive_xs = {
            matrix_type_x_2, matrix_type_x_1, matrix_type_x_1, matrix_x_ends[matrix_i]-matrix_x_centers[matrix_i],
            matrix_type_x_2, matrix_type_x_1, matrix_type_x_1, matrix_x_ends[matrix_i]-matrix_x_centers[matrix_i],
            0, 0, 0, 0,
            matrix_type_x_r, 0, 0, matrix_type_x_r,
            0, 0, 0, 0
          };
          primitive_ys = {
            matrix_type_y_2_2, matrix_type_y_2, matrix_type_y_1, matrix_y_starts[matrix_j]-matrix_y_centers[matrix_j],
            matrix_type_y_2_2, matrix_type_y_2, matrix_type_y_1, matrix_y_starts[matrix_j]-matrix_y_centers[matrix_j],
            0, 0, 0, 0,
            matrix_type_y_r, 0, 0, matrix_type_y_r,
            0, 0, 0, 0
          };
          primitive_zs = {
            matrix_type_z_1, matrix_type_z_1, matrix_type_z_1, matrix_type_z_1, 
            matrix_type_z_2, matrix_type_z_2, matrix_type_z_2, matrix_type_z_2,
            0, 0, 0, 0,
            matrix_type_z_1, 0, 0, matrix_type_z_2,
            0, 0, 0, 0
          };
          primitive_ox = matrix_x_centers[matrix_i]; primitive_oy = matrix_y_centers[matrix_j]; primitive_oz = matrix_z_centers[matrix_k]; // Origin: x, y, z
          primitive_t_5s = {0, 0, 0, 0, 1, 0, 0, 1, 0, 0, 0, 0};
        ElseIf (matrix_type_map[matrix_global_idx] == 11) // CYLINDER HALF SHELL Y SYMMETRIC
          matrix_type_r = matrix_y_ends[matrix_j] - matrix_y_r;
          matrix_type_x_1 = matrix_x_starts[matrix_i] - matrix_x_centers[matrix_i];
          matrix_type_x_1_2 = matrix_x_r - matrix_type_r/Sqrt(2) - matrix_x_centers[matrix_i];
          matrix_type_x_2 = matrix_x_ends[matrix_i] - matrix_x_centers[matrix_i];
          matrix_type_x_2_2 = matrix_x_r + matrix_type_r/Sqrt(2) - matrix_x_centers[matrix_i];
          matrix_type_x_r = matrix_x_r - matrix_x_centers[matrix_i];
          matrix_type_y_1 = matrix_y_starts[matrix_j] - matrix_y_centers[matrix_j];
          matrix_type_y_2 = matrix_y_r + matrix_type_r/Sqrt(2) - matrix_y_centers[matrix_j];
          matrix_type_y_r = matrix_y_r - matrix_y_centers[matrix_j];
          matrix_type_z_1 = matrix_z_starts[matrix_k] - matrix_z_centers[matrix_k];
          matrix_type_z_2 = matrix_z_ends[matrix_k] - matrix_z_centers[matrix_k];
          primitive_lcs = {
            matrix_lc, matrix_lc, matrix_lc, matrix_lc,
            matrix_lc, matrix_lc, matrix_lc, matrix_lc,
            matrix_lc, matrix_lc, matrix_lc, matrix_lc,
            matrix_lc, matrix_lc, matrix_lc, matrix_lc,
            matrix_lc, matrix_lc, matrix_lc, matrix_lc
          };
          primitive_xs = {
            matrix_type_x_2_2, matrix_x_starts[matrix_i]-matrix_x_centers[matrix_i], matrix_type_x_1, matrix_type_x_2,
            matrix_type_x_2_2, matrix_x_starts[matrix_i]-matrix_x_centers[matrix_i], matrix_type_x_1, matrix_type_x_2,
            matrix_type_x_r, matrix_type_x_r, 0, 0,
            0, 0, 0, 0,
            0, 0, 0, 0
          };
          primitive_ys = {
            matrix_type_y_2, matrix_y_ends[matrix_j]-matrix_y_centers[matrix_j], matrix_type_y_1, matrix_type_y_1,
            matrix_type_y_2, matrix_y_ends[matrix_j]-matrix_y_centers[matrix_j], matrix_type_y_1, matrix_type_y_1,
            matrix_type_y_r, matrix_type_y_r, 0, 0,
            0, 0, 0, 0,
            0, 0, 0, 0
          };
          primitive_zs = {
            matrix_type_z_1, matrix_type_z_1, matrix_type_z_1, matrix_type_z_1, 
            matrix_type_z_2, matrix_type_z_2, matrix_type_z_2, matrix_type_z_2,
            matrix_type_z_1, matrix_type_z_2, 0, 0,
            0, 0, 0, 0,
            0, 0, 0, 0
          };
          primitive_ox = matrix_x_centers[matrix_i]; primitive_oy = matrix_y_centers[matrix_j]; primitive_oz = matrix_z_centers[matrix_k]; // Origin: x, y, z
          primitive_t_5s = {1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0};
        ElseIf (matrix_type_map[matrix_global_idx] == 12) // CYLINDER SHELL X SYMMETRIC
          matrix_type_r = matrix_x_starts[matrix_i] - matrix_x_r;
          matrix_type_r_2 = matrix_x_ends[matrix_i] - matrix_x_r;
          matrix_type_x_1 = matrix_x_r + matrix_type_r/Sqrt(2) - matrix_x_centers[matrix_i];
          matrix_type_x_2 = matrix_x_r + matrix_type_r_2/Sqrt(2) - matrix_x_centers[matrix_i];
          matrix_type_x_r = matrix_x_r - matrix_x_centers[matrix_i];
          matrix_type_y_1 = matrix_y_r - matrix_type_r/Sqrt(2) - matrix_y_centers[matrix_j];
          matrix_type_y_1_2 = matrix_y_r - matrix_type_r_2/Sqrt(2) - matrix_y_centers[matrix_j];
          matrix_type_y_2 = matrix_y_r + matrix_type_r/Sqrt(2) - matrix_y_centers[matrix_j];
          matrix_type_y_2_2 = matrix_y_r + matrix_type_r_2/Sqrt(2) - matrix_y_centers[matrix_j];
          matrix_type_y_r = matrix_y_r - matrix_y_centers[matrix_j];
          matrix_type_z_1 = matrix_z_starts[matrix_k] - matrix_z_centers[matrix_k];
          matrix_type_z_2 = matrix_z_ends[matrix_k] - matrix_z_centers[matrix_k];
          primitive_lcs = {
            matrix_lc, matrix_lc, matrix_lc, matrix_lc,
            matrix_lc, matrix_lc, matrix_lc, matrix_lc,
            matrix_lc, matrix_lc, matrix_lc, matrix_lc,
            matrix_lc, matrix_lc, matrix_lc, matrix_lc,
            matrix_lc, matrix_lc, matrix_lc, matrix_lc
          };
          primitive_xs = {
            matrix_type_x_2, matrix_type_x_1, matrix_x_starts[matrix_i]-matrix_x_centers[matrix_i], matrix_x_ends[matrix_i]-matrix_x_centers[matrix_i],
            matrix_type_x_2, matrix_type_x_1, matrix_x_starts[matrix_i]-matrix_x_centers[matrix_i], matrix_x_ends[matrix_i]-matrix_x_centers[matrix_i],
            0, 0, 0, 0,
            matrix_type_x_r, matrix_type_x_r, matrix_type_x_r, matrix_type_x_r,
            0, 0, 0, 0
          };
          primitive_ys = {
            matrix_type_y_2_2, matrix_type_y_2, matrix_y_starts[matrix_j]-matrix_y_centers[matrix_j], matrix_y_starts[matrix_j]-matrix_y_centers[matrix_j],
            matrix_type_y_2_2, matrix_type_y_2, matrix_y_starts[matrix_j]-matrix_y_centers[matrix_j], matrix_y_starts[matrix_j]-matrix_y_centers[matrix_j],
            0, 0, 0, 0,
            matrix_type_y_r, matrix_type_y_r, matrix_type_y_r, matrix_type_y_r,
            0, 0, 0, 0
          };
          primitive_zs = {
            matrix_type_z_1, matrix_type_z_1, matrix_type_z_1, matrix_type_z_1, 
            matrix_type_z_2, matrix_type_z_2, matrix_type_z_2, matrix_type_z_2, 
            0, 0, 0, 0,
            matrix_type_z_1, matrix_type_z_1, matrix_type_z_2, matrix_type_z_2,
            0, 0, 0, 0
          };
          primitive_ox = matrix_x_centers[matrix_i]; primitive_oy = matrix_y_centers[matrix_j]; primitive_oz = matrix_z_centers[matrix_k]; // Origin: x, y, z
          primitive_t_5s = {0, 0, 0, 0, 1, 1, 1, 1, 0, 0, 0, 0};
        ElseIf (matrix_type_map[matrix_global_idx] == 13) // CYLINDER SHELL Y SYMMETRIC
          matrix_type_r = matrix_y_starts[matrix_j] - matrix_y_r;
          matrix_type_r_2 = matrix_y_ends[matrix_j] - matrix_y_r;
          matrix_type_x_1 = matrix_x_r - matrix_type_r/Sqrt(2) - matrix_x_centers[matrix_i];
          matrix_type_x_1_2 = matrix_x_r - matrix_type_r_2/Sqrt(2) - matrix_x_centers[matrix_i];
          matrix_type_x_2 = matrix_x_r + matrix_type_r/Sqrt(2) - matrix_x_centers[matrix_i];
          matrix_type_x_2_2 = matrix_x_r + matrix_type_r_2/Sqrt(2) - matrix_x_centers[matrix_i];
          matrix_type_x_r = matrix_x_r - matrix_x_centers[matrix_i];
          matrix_type_y_1 = matrix_y_r + matrix_type_r/Sqrt(2) - matrix_y_centers[matrix_j];
          matrix_type_y_2 = matrix_y_r + matrix_type_r_2/Sqrt(2) - matrix_y_centers[matrix_j];
          matrix_type_y_r = matrix_y_r - matrix_y_centers[matrix_j];
          matrix_type_z_1 = matrix_z_starts[matrix_k] - matrix_z_centers[matrix_k];
          matrix_type_z_2 = matrix_z_ends[matrix_k] - matrix_z_centers[matrix_k];
          primitive_cs = {
            matrix_lc, matrix_lc, matrix_lc, matrix_lc,
            matrix_lc, matrix_lc, matrix_lc, matrix_lc,
            matrix_lc, matrix_lc, matrix_lc, matrix_lc,
            matrix_lc, matrix_lc, matrix_lc, matrix_lc,
            matrix_lc, matrix_lc, matrix_lc, matrix_lc
          };
          primitive_xs = {
            matrix_type_x_2_2, matrix_x_starts[matrix_i]-matrix_x_centers[matrix_i], matrix_x_starts[matrix_i]-matrix_x_centers[matrix_i], matrix_type_x_2,
            matrix_type_x_2_2, matrix_x_starts[matrix_i]-matrix_x_centers[matrix_i], matrix_x_starts[matrix_i]-matrix_x_centers[matrix_i], matrix_type_x_2,
            matrix_type_x_r, matrix_type_x_r, matrix_type_x_r, matrix_type_x_r,
            0, 0, 0, 0,
            0, 0, 0, 0
          };
          primitive_ys = {
            matrix_type_y_2, matrix_y_ends[matrix_j]-matrix_y_centers[matrix_j], matrix_y_starts[matrix_j]-matrix_y_centers[matrix_j], matrix_type_y_1,
            matrix_type_y_2, matrix_y_ends[matrix_j]-matrix_y_centers[matrix_j], matrix_y_starts[matrix_j]-matrix_y_centers[matrix_j], matrix_type_y_1,
            matrix_type_y_r, matrix_type_y_r, matrix_type_y_r, matrix_type_y_r,
            0, 0, 0, 0,
            0, 0, 0, 0
          };
          primitive_zs = {
            matrix_type_z_1, matrix_type_z_1, matrix_type_z_1, matrix_type_z_1, 
            matrix_type_z_2, matrix_type_z_2, matrix_type_z_2, matrix_type_z_2,
            matrix_type_z_1, matrix_type_z_2, matrix_type_z_2, matrix_type_z_1,
            0, 0, 0, 0,
            0, 0, 0, 0
          };
          primitive_ox = matrix_x_centers[matrix_i]; primitive_oy = matrix_y_centers[matrix_j]; primitive_oz = matrix_z_centers[matrix_k]; // Origin: x, y, z
          primitive_t_5s = {1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0};
        EndIf
        
        // Deformation
        For MatrixL In {0 : #matrix_deform_map[]/(#matrix_x_centers[]*#matrix_y_centers[]*#matrix_z_centers[])-1}
          matrix_global_deform_idx = matrix_i + matrix_j*#matrix_x_centers[] + matrix_k*#matrix_x_centers[]*#matrix_y_centers[] + MatrixL*#matrix_x_centers[]*#matrix_y_centers[]*#matrix_z_centers[];
          For MatrixM In {0 : #primitive_lcs[]-1}
            If (MatrixM == 0 &&
              (matrix_deform_map[matrix_global_deform_idx] == 10 || 
              matrix_deform_map[matrix_global_deform_idx] == 11 || 
              matrix_deform_map[matrix_global_deform_idx] == 13 || 
              matrix_deform_map[matrix_global_deform_idx] == 14 || 
              matrix_deform_map[matrix_global_deform_idx] == 19 || 
              matrix_deform_map[matrix_global_deform_idx] == 20 || 
              matrix_deform_map[matrix_global_deform_idx] == 22 || 
              matrix_deform_map[matrix_global_deform_idx] == 23))
              primitive_t_9s += 1;
            ElseIf (MatrixM == 1 && 
              (matrix_deform_map[matrix_global_deform_idx] == 11 || 
              matrix_deform_map[matrix_global_deform_idx] == 12 || 
              matrix_deform_map[matrix_global_deform_idx] == 14 || 
              matrix_deform_map[matrix_global_deform_idx] == 15 || 
              matrix_deform_map[matrix_global_deform_idx] == 20 || 
              matrix_deform_map[matrix_global_deform_idx] == 21 || 
              matrix_deform_map[matrix_global_deform_idx] == 23 || 
              matrix_deform_map[matrix_global_deform_idx] == 24))
              primitive_t_9s += 1;
            ElseIf (MatrixM == 2 && 
              (matrix_deform_map[matrix_global_deform_idx] == 14 || 
              matrix_deform_map[matrix_global_deform_idx] == 15 || 
              matrix_deform_map[matrix_global_deform_idx] == 17 || 
              matrix_deform_map[matrix_global_deform_idx] == 18 || 
              matrix_deform_map[matrix_global_deform_idx] == 23 || 
              matrix_deform_map[matrix_global_deform_idx] == 24 || 
              matrix_deform_map[matrix_global_deform_idx] == 26 || 
              matrix_deform_map[matrix_global_deform_idx] == 27))
              primitive_t_9s += 1;
            ElseIf (MatrixM == 3 && 
              (matrix_deform_map[matrix_global_deform_idx] == 13 || 
              matrix_deform_map[matrix_global_deform_idx] == 14 || 
              matrix_deform_map[matrix_global_deform_idx] == 16 || 
              matrix_deform_map[matrix_global_deform_idx] == 17 || 
              matrix_deform_map[matrix_global_deform_idx] == 22 || 
              matrix_deform_map[matrix_global_deform_idx] == 23 || 
              matrix_deform_map[matrix_global_deform_idx] == 25 || 
              matrix_deform_map[matrix_global_deform_idx] == 26))
              primitive_t_9s += 1;
            ElseIf (MatrixM == 4 && 
              (matrix_deform_map[matrix_global_deform_idx] == 1 || 
              matrix_deform_map[matrix_global_deform_idx] == 2 || 
              matrix_deform_map[matrix_global_deform_idx] == 4 || 
              matrix_deform_map[matrix_global_deform_idx] == 5 || 
              matrix_deform_map[matrix_global_deform_idx] == 10 || 
              matrix_deform_map[matrix_global_deform_idx] == 11 || 
              matrix_deform_map[matrix_global_deform_idx] == 13 || 
              matrix_deform_map[matrix_global_deform_idx] == 14))
              primitive_t_9s += 1;
            ElseIf (MatrixM == 5 &&
              (matrix_deform_map[matrix_global_deform_idx] == 2 || 
              matrix_deform_map[matrix_global_deform_idx] == 3 || 
              matrix_deform_map[matrix_global_deform_idx] == 5 || 
              matrix_deform_map[matrix_global_deform_idx] == 6 || 
              matrix_deform_map[matrix_global_deform_idx] == 11 || 
              matrix_deform_map[matrix_global_deform_idx] == 12 || 
              matrix_deform_map[matrix_global_deform_idx] == 14 || 
              matrix_deform_map[matrix_global_deform_idx] == 15))
              primitive_t_9s += 1;
            ElseIf (MatrixM == 6 &&
              (matrix_deform_map[matrix_global_deform_idx] == 5 || 
              matrix_deform_map[matrix_global_deform_idx] == 6 || 
              matrix_deform_map[matrix_global_deform_idx] == 8 || 
              matrix_deform_map[matrix_global_deform_idx] == 9 || 
              matrix_deform_map[matrix_global_deform_idx] == 14 || 
              matrix_deform_map[matrix_global_deform_idx] == 15 || 
              matrix_deform_map[matrix_global_deform_idx] == 17 || 
              matrix_deform_map[matrix_global_deform_idx] == 18))
              primitive_t_9s += 1;
            ElseIf (MatrixM == 7 &&
              (matrix_deform_map[matrix_global_deform_idx] == 4 || 
              matrix_deform_map[matrix_global_deform_idx] == 5 || 
              matrix_deform_map[matrix_global_deform_idx] == 7 || 
              matrix_deform_map[matrix_global_deform_idx] == 8 || 
              matrix_deform_map[matrix_global_deform_idx] == 13 || 
              matrix_deform_map[matrix_global_deform_idx] == 14 || 
              matrix_deform_map[matrix_global_deform_idx] == 16 || 
              matrix_deform_map[matrix_global_deform_idx] == 17))
              primitive_t_9s += 1;
            ElseIf (MatrixM == 8 &&
              (matrix_deform_map[matrix_global_deform_idx] == 10 ||
              matrix_deform_map[matrix_global_deform_idx] == 11 ||
              matrix_deform_map[matrix_global_deform_idx] == 12 ||
              matrix_deform_map[matrix_global_deform_idx] == 13 ||
              matrix_deform_map[matrix_global_deform_idx] == 14 ||
              matrix_deform_map[matrix_global_deform_idx] == 15 ||
              matrix_deform_map[matrix_global_deform_idx] == 19 ||
              matrix_deform_map[matrix_global_deform_idx] == 20 ||
              matrix_deform_map[matrix_global_deform_idx] == 21 ||
              matrix_deform_map[matrix_global_deform_idx] == 22 ||
              matrix_deform_map[matrix_global_deform_idx] == 23 ||
              matrix_deform_map[matrix_global_deform_idx] == 24))
              primitive_t_9s += 1;
            ElseIf (MatrixM == 9 &&
              (matrix_deform_map[matrix_global_deform_idx] == 1 ||
              matrix_deform_map[matrix_global_deform_idx] == 2 ||
              matrix_deform_map[matrix_global_deform_idx] == 3 ||
              matrix_deform_map[matrix_global_deform_idx] == 4 ||
              matrix_deform_map[matrix_global_deform_idx] == 5 ||
              matrix_deform_map[matrix_global_deform_idx] == 6 ||
              matrix_deform_map[matrix_global_deform_idx] == 10 ||
              matrix_deform_map[matrix_global_deform_idx] == 11 ||
              matrix_deform_map[matrix_global_deform_idx] == 12 ||
              matrix_deform_map[matrix_global_deform_idx] == 13 ||
              matrix_deform_map[matrix_global_deform_idx] == 14 ||
              matrix_deform_map[matrix_global_deform_idx] == 15))
              primitive_t_9s += 1;
            ElseIf (MatrixM == 10 &&
              (matrix_deform_map[matrix_global_deform_idx] == 4 ||
              matrix_deform_map[matrix_global_deform_idx] == 5 ||
              matrix_deform_map[matrix_global_deform_idx] == 6 ||
              matrix_deform_map[matrix_global_deform_idx] == 7 ||
              matrix_deform_map[matrix_global_deform_idx] == 8 ||
              matrix_deform_map[matrix_global_deform_idx] == 9 ||
              matrix_deform_map[matrix_global_deform_idx] == 13 ||
              matrix_deform_map[matrix_global_deform_idx] == 14 ||
              matrix_deform_map[matrix_global_deform_idx] == 15 ||
              matrix_deform_map[matrix_global_deform_idx] == 16 ||
              matrix_deform_map[matrix_global_deform_idx] == 17 ||
              matrix_deform_map[matrix_global_deform_idx] == 18))
              primitive_t_9s += 1;
            ElseIf (MatrixM == 11 &&
              (matrix_deform_map[matrix_global_deform_idx] == 13 ||
              matrix_deform_map[matrix_global_deform_idx] == 14 ||
              matrix_deform_map[matrix_global_deform_idx] == 15 ||
              matrix_deform_map[matrix_global_deform_idx] == 16 ||
              matrix_deform_map[matrix_global_deform_idx] == 17 ||
              matrix_deform_map[matrix_global_deform_idx] == 18 ||
              matrix_deform_map[matrix_global_deform_idx] == 22 ||
              matrix_deform_map[matrix_global_deform_idx] == 23 ||
              matrix_deform_map[matrix_global_deform_idx] == 24 ||
              matrix_deform_map[matrix_global_deform_idx] == 25 ||
              matrix_deform_map[matrix_global_deform_idx] == 26 ||
              matrix_deform_map[matrix_global_deform_idx] == 27))
              primitive_t_9s += 1;
            ElseIf (MatrixM == 12 &&
              (matrix_deform_map[matrix_global_deform_idx] == 10 ||
              matrix_deform_map[matrix_global_deform_idx] == 11 ||
              matrix_deform_map[matrix_global_deform_idx] == 13 ||
              matrix_deform_map[matrix_global_deform_idx] == 14 ||
              matrix_deform_map[matrix_global_deform_idx] == 16 ||
              matrix_deform_map[matrix_global_deform_idx] == 17 ||
              matrix_deform_map[matrix_global_deform_idx] == 19 ||
              matrix_deform_map[matrix_global_deform_idx] == 20 ||
              matrix_deform_map[matrix_global_deform_idx] == 22 ||
              matrix_deform_map[matrix_global_deform_idx] == 23 ||
              matrix_deform_map[matrix_global_deform_idx] == 25 ||
              matrix_deform_map[matrix_global_deform_idx] == 26))
              primitive_t_9s += 1;
            ElseIf (MatrixM == 13 &&
              (matrix_deform_map[matrix_global_deform_idx] == 11 ||
              matrix_deform_map[matrix_global_deform_idx] == 12 ||
              matrix_deform_map[matrix_global_deform_idx] == 14 ||
              matrix_deform_map[matrix_global_deform_idx] == 15 ||
              matrix_deform_map[matrix_global_deform_idx] == 17 ||
              matrix_deform_map[matrix_global_deform_idx] == 18 ||
              matrix_deform_map[matrix_global_deform_idx] == 20 ||
              matrix_deform_map[matrix_global_deform_idx] == 21 ||
              matrix_deform_map[matrix_global_deform_idx] == 23 ||
              matrix_deform_map[matrix_global_deform_idx] == 24 ||
              matrix_deform_map[matrix_global_deform_idx] == 26 ||
              matrix_deform_map[matrix_global_deform_idx] == 27))
              primitive_t_9s += 1;
            ElseIf (MatrixM == 14 &&
              (matrix_deform_map[matrix_global_deform_idx] == 2 ||
              matrix_deform_map[matrix_global_deform_idx] == 3 ||
              matrix_deform_map[matrix_global_deform_idx] == 5 ||
              matrix_deform_map[matrix_global_deform_idx] == 6 ||
              matrix_deform_map[matrix_global_deform_idx] == 8 ||
              matrix_deform_map[matrix_global_deform_idx] == 9 ||
              matrix_deform_map[matrix_global_deform_idx] == 11 ||
              matrix_deform_map[matrix_global_deform_idx] == 12 ||
              matrix_deform_map[matrix_global_deform_idx] == 14 ||
              matrix_deform_map[matrix_global_deform_idx] == 15 ||
              matrix_deform_map[matrix_global_deform_idx] == 17 ||
              matrix_deform_map[matrix_global_deform_idx] == 18))
              primitive_t_9s += 1;
            ElseIf (MatrixM == 15 &&
              (matrix_deform_map[matrix_global_deform_idx] == 1 ||
              matrix_deform_map[matrix_global_deform_idx] == 2 ||
              matrix_deform_map[matrix_global_deform_idx] == 4 ||
              matrix_deform_map[matrix_global_deform_idx] == 5 ||
              matrix_deform_map[matrix_global_deform_idx] == 7 ||
              matrix_deform_map[matrix_global_deform_idx] == 8 ||
              matrix_deform_map[matrix_global_deform_idx] == 10 ||
              matrix_deform_map[matrix_global_deform_idx] == 11 ||
              matrix_deform_map[matrix_global_deform_idx] == 13 ||
              matrix_deform_map[matrix_global_deform_idx] == 14 ||
              matrix_deform_map[matrix_global_deform_idx] == 16 ||
              matrix_deform_map[matrix_global_deform_idx] == 17))
              primitive_t_9s += 1;
            Else
              primitive_t_9s += 0;
            EndIf
          EndFor // MatrixM
        EndFor // MatrixL
        Call primitive;
        
        // Physical Volumes
        matrix_pvs += matrix_physical_map[matrix_global_idx];
        matrix_pvs += #primitive_vs[];
        matrix_pvs += primitive_vs[];
        
        // Boundary
        // Result 4^4 = 64 combinations XYZ
        // 1 - positive and negative surfaces, 2 - positive surface, 
        // 3 - negative surface, 4 - none surfaces
        If (matrix_boundary_map[matrix_global_idx] == 444)
        ElseIf (matrix_boundary_map[matrix_global_idx] == 443)
          matrix_nzss += primitive_ss[4];
        ElseIf (matrix_boundary_map[matrix_global_idx] == 442)
          matrix_zss += primitive_ss[5];
        ElseIf (matrix_boundary_map[matrix_global_idx] == 441)
          matrix_nzss += primitive_ss[4];
          matrix_zss += primitive_ss[5];
        ElseIf (matrix_boundary_map[matrix_global_idx] == 434)
          matrix_nyss += primitive_ss[2];
        ElseIf (matrix_boundary_map[matrix_global_idx] == 433)
          matrix_nyss += primitive_ss[2];
          matrix_nzss += primitive_ss[4];
        ElseIf (matrix_boundary_map[matrix_global_idx] == 432)
          matrix_nyss += primitive_ss[2];
          matrix_zss += primitive_ss[5];
        ElseIf (matrix_boundary_map[matrix_global_idx] == 431)
          matrix_nyss += primitive_ss[2];
          matrix_nzss += primitive_ss[4];
          matrix_zss += primitive_ss[5];
        ElseIf (matrix_boundary_map[matrix_global_idx] == 424)
          matrix_yss += primitive_ss[3];
        ElseIf (matrix_boundary_map[matrix_global_idx] == 423)
          matrix_yss += primitive_ss[3];
          matrix_nzss += primitive_ss[4];
        ElseIf (matrix_boundary_map[matrix_global_idx] == 422)
          matrix_yss += primitive_ss[3];
          matrix_zss += primitive_ss[5];
        ElseIf (matrix_boundary_map[matrix_global_idx] == 421)
          matrix_yss += primitive_ss[3];
          matrix_nzss += primitive_ss[4];
          matrix_zss += primitive_ss[5];
        ElseIf (matrix_boundary_map[matrix_global_idx] == 414)
          matrix_nyss += primitive_ss[2];
          matrix_yss += primitive_ss[3];
        ElseIf (matrix_boundary_map[matrix_global_idx] == 413)
          matrix_nyss += primitive_ss[2];
          matrix_yss += primitive_ss[3];
          matrix_zss += primitive_ss[5];
        ElseIf (matrix_boundary_map[matrix_global_idx] == 412)
          matrix_nyss += primitive_ss[2];
          matrix_yss += primitive_ss[3];
          matrix_nzss += primitive_ss[4];
        ElseIf (matrix_boundary_map[matrix_global_idx] == 411)
          matrix_nyss += primitive_ss[2];
          matrix_yss += primitive_ss[3];
          matrix_nzss += primitive_ss[4];
          matrix_zss += primitive_ss[5];  
        ElseIf (matrix_boundary_map[matrix_global_idx] == 344)
          matrix_nxss += primitive_ss[0];
        ElseIf (matrix_boundary_map[matrix_global_idx] == 343)
          matrix_nxss += primitive_ss[0];  
          matrix_nzss += primitive_ss[4];
        ElseIf (matrix_boundary_map[matrix_global_idx] == 342)
          matrix_nxss += primitive_ss[0];
          matrix_zss += primitive_ss[5];
        ElseIf (matrix_boundary_map[matrix_global_idx] == 341)
          matrix_nxss += primitive_ss[0];
          matrix_nzss += primitive_ss[4];
          matrix_zss += primitive_ss[5];
        ElseIf (matrix_boundary_map[matrix_global_idx] == 334)
          matrix_nxss += primitive_ss[0];
          matrix_nyss += primitive_ss[2];
        ElseIf (matrix_boundary_map[matrix_global_idx] == 333)
          matrix_nxss += primitive_ss[0];
          matrix_nyss += primitive_ss[2];
          matrix_nzss += primitive_ss[4];
        ElseIf (matrix_boundary_map[matrix_global_idx] == 332)
          matrix_nxss += primitive_ss[0];
          matrix_nyss += primitive_ss[2];
          matrix_zss += primitive_ss[5];
        ElseIf (matrix_boundary_map[matrix_global_idx] == 331)
          matrix_nxss += primitive_ss[0];
          matrix_nyss += primitive_ss[2];
          matrix_nzss += primitive_ss[4];
          matrix_zss += primitive_ss[5];
        ElseIf (matrix_boundary_map[matrix_global_idx] == 324)
          matrix_nxss += primitive_ss[0];
          matrix_yss += primitive_ss[3];
        ElseIf (matrix_boundary_map[matrix_global_idx] == 323)
          matrix_nxss += primitive_ss[0];
          matrix_yss += primitive_ss[3];
          matrix_nzss += primitive_ss[4];
        ElseIf (matrix_boundary_map[matrix_global_idx] == 322)  
          matrix_nxss += primitive_ss[0];
          matrix_yss += primitive_ss[3];
          matrix_zss += primitive_ss[5];
        ElseIf (matrix_boundary_map[matrix_global_idx] == 321)  
          matrix_nxss += primitive_ss[0];
          matrix_yss += primitive_ss[3];
          matrix_nzss += primitive_ss[4];
          matrix_zss += primitive_ss[5];  
        ElseIf (matrix_boundary_map[matrix_global_idx] == 314)
          matrix_nxss += primitive_ss[0];
          matrix_nyss += primitive_ss[2];
          matrix_yss += primitive_ss[3];
        ElseIf (matrix_boundary_map[matrix_global_idx] == 313)
          matrix_nxss += primitive_ss[0];
          matrix_nyss += primitive_ss[2];
          matrix_yss += primitive_ss[3];
          matrix_nzss += primitive_ss[4];
        ElseIf (matrix_boundary_map[matrix_global_idx] == 312)
          matrix_nxss += primitive_ss[0];
          matrix_nyss += primitive_ss[2];
          matrix_yss += primitive_ss[3];
          matrix_zss += primitive_ss[5]; 
        ElseIf (matrix_boundary_map[matrix_global_idx] == 311)
          matrix_nxss += primitive_ss[0];
          matrix_nyss += primitive_ss[2];
          matrix_yss += primitive_ss[3];
          matrix_nzss += primitive_ss[4];
          matrix_zss += primitive_ss[5];
        ElseIf (matrix_boundary_map[matrix_global_idx] == 244)
          matrix_xss += primitive_ss[1];
        ElseIf (matrix_boundary_map[matrix_global_idx] == 243)
          matrix_xss += primitive_ss[1];
          matrix_nzss += primitive_ss[4];
        ElseIf (matrix_boundary_map[matrix_global_idx] == 242)
          matrix_xss += primitive_ss[1];
          matrix_zss += primitive_ss[5];
        ElseIf (matrix_boundary_map[matrix_global_idx] == 241)
          matrix_xss += primitive_ss[1];
          matrix_nzss += primitive_ss[4];
          matrix_zss += primitive_ss[5];
        ElseIf (matrix_boundary_map[matrix_global_idx] == 234)
          matrix_xss += primitive_ss[1];
          matrix_nyss += primitive_ss[2];
        ElseIf (matrix_boundary_map[matrix_global_idx] == 233)
          matrix_xss += primitive_ss[1];
          matrix_nyss += primitive_ss[2];
          matrix_nzss += primitive_ss[4];
        ElseIf (matrix_boundary_map[matrix_global_idx] == 232)
          matrix_xss += primitive_ss[1];
          matrix_nyss += primitive_ss[2];
          matrix_zss += primitive_ss[5];
        ElseIf (matrix_boundary_map[matrix_global_idx] == 231)
          matrix_xss += primitive_ss[1];
          matrix_nyss += primitive_ss[2];
          matrix_nzss += primitive_ss[4];
          matrix_zss += primitive_ss[5];
        ElseIf (matrix_boundary_map[matrix_global_idx] == 224)
          matrix_xss += primitive_ss[1];
          matrix_yss += primitive_ss[3];
        ElseIf (matrix_boundary_map[matrix_global_idx] == 223)
          matrix_xss += primitive_ss[1];
          matrix_yss += primitive_ss[3];
          matrix_nzss += primitive_ss[4];
        ElseIf (matrix_boundary_map[matrix_global_idx] == 222)  
          matrix_xss += primitive_ss[1];
          matrix_yss += primitive_ss[3];
          matrix_zss += primitive_ss[5];
        ElseIf (matrix_boundary_map[matrix_global_idx] == 221)  
          matrix_xss += primitive_ss[1];
          matrix_yss += primitive_ss[3];
          matrix_nzss += primitive_ss[4];
          matrix_zss += primitive_ss[5];  
        ElseIf (matrix_boundary_map[matrix_global_idx] == 214)
          matrix_xss += primitive_ss[1];
          matrix_nyss += primitive_ss[2];
          matrix_yss += primitive_ss[3];
        ElseIf (matrix_boundary_map[matrix_global_idx] == 213)
          matrix_xss += primitive_ss[1];
          matrix_nyss += primitive_ss[2];
          matrix_yss += primitive_ss[3];
          matrix_nzss += primitive_ss[4];
        ElseIf (matrix_boundary_map[matrix_global_idx] == 212)
          matrix_xss += primitive_ss[1];
          matrix_nyss += primitive_ss[2];
          matrix_yss += primitive_ss[3];
          matrix_zss += primitive_ss[5]; 
        ElseIf (matrix_boundary_map[matrix_global_idx] == 211)
          matrix_xss += primitive_ss[1];
          matrix_nyss += primitive_ss[2];
          matrix_yss += primitive_ss[3];
          matrix_nzss += primitive_ss[4];
          matrix_zss += primitive_ss[5];
        ElseIf (matrix_boundary_map[matrix_global_idx] == 144)
          matrix_nxss += primitive_ss[0];
          matrix_xss += primitive_ss[1];
        ElseIf (matrix_boundary_map[matrix_global_idx] == 143)
          matrix_nxss += primitive_ss[0];
          matrix_xss += primitive_ss[1];
          matrix_nzss += primitive_ss[4];
        ElseIf (matrix_boundary_map[matrix_global_idx] == 142)
          matrix_nxss += primitive_ss[0];
          matrix_xss += primitive_ss[1];
          matrix_zss += primitive_ss[5];
        ElseIf (matrix_boundary_map[matrix_global_idx] == 141)
          matrix_nxss += primitive_ss[0];
          matrix_xss += primitive_ss[1];
          matrix_nzss += primitive_ss[4];
          matrix_zss += primitive_ss[5];
        ElseIf (matrix_boundary_map[matrix_global_idx] == 134)
          matrix_nxss += primitive_ss[0];
          matrix_xss += primitive_ss[1];
          matrix_nyss += primitive_ss[2];
        ElseIf (matrix_boundary_map[matrix_global_idx] == 133)
          matrix_nxss += primitive_ss[0];
          matrix_xss += primitive_ss[1];
          matrix_nyss += primitive_ss[2];
          matrix_nzss += primitive_ss[4];
        ElseIf (matrix_boundary_map[matrix_global_idx] == 132)
          matrix_nxss += primitive_ss[0];
          matrix_xss += primitive_ss[1];
          matrix_nyss += primitive_ss[2];
          matrix_zss += primitive_ss[5];
        ElseIf (matrix_boundary_map[matrix_global_idx] == 131)
          matrix_nxss += primitive_ss[0];
          matrix_xss += primitive_ss[1];
          matrix_nyss += primitive_ss[2];
          matrix_nzss += primitive_ss[4];
          matrix_zss += primitive_ss[5];
        ElseIf (matrix_boundary_map[matrix_global_idx] == 124)
          matrix_nxss += primitive_ss[0];
          matrix_xss += primitive_ss[1];
          matrix_yss += primitive_ss[3];
        ElseIf (matrix_boundary_map[matrix_global_idx] == 123)
          matrix_nxss += primitive_ss[0];
          matrix_xss += primitive_ss[1];
          matrix_yss += primitive_ss[3];
          matrix_nzss += primitive_ss[4];
        ElseIf (matrix_boundary_map[matrix_global_idx] == 122)
          matrix_nxss += primitive_ss[0];                
          matrix_xss += primitive_ss[1];
          matrix_yss += primitive_ss[3];
          matrix_zss += primitive_ss[5];
        ElseIf (matrix_boundary_map[matrix_global_idx] == 121)
          matrix_nxss += primitive_ss[0];
          matrix_xss += primitive_ss[1];
          matrix_yss += primitive_ss[3];
          matrix_nzss += primitive_ss[4];
          matrix_zss += primitive_ss[5];  
        ElseIf (matrix_boundary_map[matrix_global_idx] == 114)
          matrix_nxss += primitive_ss[0];
          matrix_xss += primitive_ss[1];
          matrix_nyss += primitive_ss[2];
          matrix_yss += primitive_ss[3];
        ElseIf (matrix_boundary_map[matrix_global_idx] == 113)
          matrix_nxss += primitive_ss[0];
          matrix_xss += primitive_ss[1];
          matrix_nyss += primitive_ss[2];
          matrix_yss += primitive_ss[3];
          matrix_nzss += primitive_ss[4];
        ElseIf (matrix_boundary_map[matrix_global_idx] == 112)
          matrix_nxss += primitive_ss[0];
          matrix_xss += primitive_ss[1];
          matrix_nyss += primitive_ss[2];
          matrix_yss += primitive_ss[3];
          matrix_zss += primitive_ss[5]; 
        ElseIf (matrix_boundary_map[matrix_global_idx] == 111)
          matrix_nxss += primitive_ss[0];
          matrix_xss += primitive_ss[1];
          matrix_nyss += primitive_ss[2];
          matrix_yss += primitive_ss[3];
          matrix_nzss += primitive_ss[4];
          matrix_zss += primitive_ss[5];
        EndIf
        // Physical Volume (Sprintf("VR%gC%gT%g", matrix_i, matrix_j, matrix_k)) = {vs[]};
      EndIf
    EndFor // matrix_k
  EndFor // matrix_j
EndFor // matrix_i

Return
