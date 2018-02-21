Include "macro_primitive.geo";

Macro hexahedron

hexahedron_nxss = {};
hexahedron_xss = {};
hexahedron_nyss = {};
hexahedron_yss = {};
hexahedron_nzss = {};
hexahedron_zss = {};
hexahedron_vs = {};

// X-Y-NZ point, NX-Y-NZ, NX-NY-NZ, X-NY-NZ, (X - X axis, NX - negative X axis, etc)
// X-Y-Z, NX-Y-Z, NX-NY-Z, X-NY-Z,
// X1 line circle center, X2, X3, X4, (Line numeration by right hand rule from line contains X-Y-NZ point)
// Y1, Y2, Y3, Y4,
// Z1, Z2, Z3, Z4,
// X1 line ellipse point, X2, X3, X4,
// Y1, Y2, Y3, Y4,
// Z1, Z2, Z3, Z4
primitive_lcs = {
  hexahedron_lc, hexahedron_lc, hexahedron_lc, hexahedron_lc,
  hexahedron_lc, hexahedron_lc, hexahedron_lc, hexahedron_lc
};
primitive_xs = {
  hexahedron_a/2, -hexahedron_a/2, -hexahedron_a/2, hexahedron_a/2, 
  hexahedron_a/2, -hexahedron_a/2, -hexahedron_a/2, hexahedron_a/2
};
primitive_ys = {
  hexahedron_b/2, hexahedron_b/2, -hexahedron_b/2, -hexahedron_b/2,
  hexahedron_b/2, hexahedron_b/2, -hexahedron_b/2, -hexahedron_b/2
};
primitive_zs = {
  -hexahedron_c/2, -hexahedron_c/2, -hexahedron_c/2, -hexahedron_c/2,
  hexahedron_c/2, hexahedron_c/2, hexahedron_c/2, hexahedron_c/2
};
primitive_ox = hexahedron_ox; primitive_oy = hexahedron_oy; primitive_oz = hexahedron_oz; // Origin: x, y, z
primitive_rox = hexahedron_rox; primitive_roy = hexahedron_roy; primitive_roz = hexahedron_roz; // Local Rotation Origin: x, y, z
primitive_rax = hexahedron_rax; primitive_ray = hexahedron_ray; primitive_raz = hexahedron_raz; // Local Rotation Angle: x, y, z
// Parameters
primitive_t_1 = hexahedron_t_1; primitive_t_1_1 = hexahedron_t_1_1; primitive_t_1_2 = hexahedron_t_1_2; // Number of X nodes, progression, bump
primitive_t_2 = hexahedron_t_2; primitive_t_2_1 = hexahedron_t_2_1; primitive_t_2_2 = hexahedron_t_2_2; // Number of Y nodes, progression, bump
primitive_t_3 = hexahedron_t_3; primitive_t_3_1 = hexahedron_t_3_1; primitive_t_3_2 = hexahedron_t_3_2; // Number of Z nodes, progression, bump
primitive_t_4 = hexahedron_t_4; // Hex (1) or tet (0) mesh?
primitive_t_5s = {0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0}; // Type of lines: 0 - straight, 1 - circle, 2 - ellipse, 3 - Bezier, 4 - BSpline, 5+ - Spline
primitive_t_6 = hexahedron_t_6; // Type of hex to tet splitting
primitive_t_7s = hexahedron_t_7s[]; // Inner Surfaces
primitive_t_8s = {0, 0, 0, 0, 0, 0}; // Surfaces for changes
primitive_t_9s = {}; // Rotations
primitive_t_10s = {0, 0, 0, 0, 0, 0}; // Plane Surface?

Call primitive;

hexahedron_nxss = primitive_ss[0];
hexahedron_xss = primitive_ss[1];
hexahedron_nyss = primitive_ss[2];
hexahedron_yss = primitive_ss[3];
hexahedron_nzss = primitive_ss[4];
hexahedron_zss = primitive_ss[5];
hexahedron_vs = primitive_vs[];

Return

