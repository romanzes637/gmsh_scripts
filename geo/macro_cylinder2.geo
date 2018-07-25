Include "macro_primitive.geo";

Macro cylinder2

cylinder2_nxss = {};
cylinder2_xss = {};
cylinder2_nyss = {};
cylinder2_yss = {};
cylinder2_nzss = {};
cylinder2_zss = {};
cylinder2_bss = {};
cylinder2_vs = {};


// X-Y-NZ point, NX-Y-NZ, NX-NY-NZ, X-NY-NZ, (X - X axis, NX - negative X axis, etc)
// X-Y-Z, NX-Y-Z, NX-NY-Z, X-NY-Z,
// X1 line circle center, X2, X3, X4, (Line numeration by right hand rule from line contains X-Y-NZ point)
// Y1, Y2, Y3, Y4,
// Z1, Z2, Z3, Z4,
// X1 line ellipse point, X2, X3, X4,
// Y1, Y2, Y3, Y4,
// Z1, Z2, Z3, Z4
primitive_lcs = {
  cylinder2_lc, cylinder2_lc, cylinder2_lc, cylinder2_lc,
  cylinder2_lc, cylinder2_lc, cylinder2_lc, cylinder2_lc,
  cylinder2_lc, cylinder2_lc, cylinder2_lc, cylinder2_lc,
  cylinder2_lc, cylinder2_lc, cylinder2_lc, cylinder2_lc,
  cylinder2_lc, cylinder2_lc, cylinder2_lc, cylinder2_lc
};
primitive_xs = {
  cylinder2_r/Sqrt(2), -cylinder2_r/Sqrt(2), -cylinder2_r/Sqrt(2), cylinder2_r/Sqrt(2), 
  cylinder2_r/Sqrt(2), -cylinder2_r/Sqrt(2), -cylinder2_r/Sqrt(2), cylinder2_r/Sqrt(2), 
  0, 0, 0, 0,
  0, 0, 0, 0,
  0, 0, 0, 0
};
primitive_ys = {
  cylinder2_r/Sqrt(2), cylinder2_r/Sqrt(2), -cylinder2_r/Sqrt(2), -cylinder2_r/Sqrt(2),
  cylinder2_r/Sqrt(2), cylinder2_r/Sqrt(2), -cylinder2_r/Sqrt(2), -cylinder2_r/Sqrt(2),
  0, 0, 0, 0,
  0, 0, 0, 0,
  0, 0, 0, 0
};
primitive_zs = {
  -cylinder2_h/2, -cylinder2_h/2, -cylinder2_h/2, -cylinder2_h/2,
  cylinder2_h/2, cylinder2_h/2, cylinder2_h/2, cylinder2_h/2,
  -cylinder2_h/2, cylinder2_h/2, cylinder2_h/2, -cylinder2_h/2,
  -cylinder2_h/2, -cylinder2_h/2, cylinder2_h/2, cylinder2_h/2,
  0, 0, 0, 0
};
primitive_ox = cylinder2_ox; primitive_oy = cylinder2_oy; primitive_oz = cylinder2_oz; // Origin: x, y, z
primitive_rox = cylinder2_rox; primitive_roy = cylinder2_roy; primitive_roz = cylinder2_roz; // Local Rotation Origin: x, y, z
primitive_rax = cylinder2_rax; primitive_ray = cylinder2_ray; primitive_raz = cylinder2_raz; // Local Rotation Angle: x, y, z
// Parameters
primitive_t_1 = cylinder2_t1; primitive_t_1_1 = cylinder2_t1t1; primitive_t_1_2 = cylinder2_t1t2; // Number of X nodes, progression, bump
primitive_t_2 = cylinder2_t2; primitive_t_2_1 = cylinder2_t2t1; primitive_t_2_2 = cylinder2_t2t2; // Number of Y nodes, progression, bump
primitive_t_3 = cylinder2_t3; primitive_t_3_1 = cylinder2_t3t1; primitive_t_3_2 = cylinder2_t3t2; // Number of Z nodes, progression, bump
primitive_t_4 = cylinder2_t4; // Hex (1) or tet (0) mesh?
primitive_t_5s = {1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0}; // Type of lines: 0 - straight, 1 - circle, 2 - ellipse, 3 - Bezier, 4 - BSpline, 5+ - Spline
primitive_t_6 = cylinder2_t6; // Type of hex to tet splitting
primitive_t_7s = cylinder2_t7s[]; // Inner Surfaces
primitive_t_8s = {0, 0, 0, 0, 0, 0}; // Surfaces for changes
primitive_t_9s = {}; // Rotations
primitive_t_10s = {0, 0, 0, 0, 1, 1}; // Plane Surface?

Call primitive;

cylinder2_nxss = primitive_ss[0];
cylinder2_xss = primitive_ss[1];
cylinder2_nyss = primitive_ss[2];
cylinder2_yss = primitive_ss[3];
cylinder2_nzss = primitive_ss[4];
cylinder2_zss = primitive_ss[5];
cylinder2_bss += cylinder2_nxss[];
cylinder2_bss += cylinder2_xss[];
cylinder2_bss += cylinder2_nyss[];
cylinder2_bss += cylinder2_yss[];
cylinder2_bss += cylinder2_nzss[];
cylinder2_bss += cylinder2_zss[];

cylinder2_vs = primitive_vs[];

Return

