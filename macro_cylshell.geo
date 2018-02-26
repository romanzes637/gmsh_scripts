Include "macro_primitive.geo";

Macro cylshell

cylshell_iss = {};
cylshell_lss = {};
cylshell_nzss = {};
cylshell_zss = {};
cylshell_vs = {};

// General
// X-Y-NZ point, NX-Y-NZ, NX-NY-NZ, X-NY-NZ, (X - X axis, NX - negative X axis, etc)
// X-Y-Z, NX-Y-Z, NX-NY-Z, X-NY-Z,
// X1 line circle center, X2, X3, X4, (Line numeration by right hand rule from line contains X-Y-NZ point)
// Y1, Y2, Y3, Y4,
// Z1, Z2, Z3, Z4,
// X1 line ellipse point, X2, X3, X4,
// Y1, Y2, Y3, Y4,
// Z1, Z2, Z3, Z4
primitive_lcs = {
  cylshell_lc, cylshell_lc, cylshell_lc, cylshell_lc,
  cylshell_lc, cylshell_lc, cylshell_lc, cylshell_lc,
  cylshell_lc, cylshell_lc, cylshell_lc, cylshell_lc,
  cylshell_lc, cylshell_lc, cylshell_lc, cylshell_lc,
  cylshell_lc, cylshell_lc, cylshell_lc, cylshell_lc
};
primitive_ox = cylshell_ox; primitive_oy = cylshell_oy; primitive_oz = cylshell_oz; // Origin: x, y, z
primitive_rox = cylshell_rox; primitive_roy = cylshell_roy; primitive_roz = cylshell_roz; // Local Rotation Origin: x, y, z
primitive_rax = cylshell_rax; primitive_ray = cylshell_ray; primitive_raz = cylshell_raz; // Local Rotation Angle: x, y, z
// Parameters
primitive_t_3 = cylshell_t_3; primitive_t_3_1 = cylshell_t_3_1; primitive_t_3_2 = cylshell_t_3_2; // Number of Z nodes, progression, bump
primitive_t_4 = cylshell_t_4; // Hex (1) or tet (0) mesh?
primitive_t_7s = {}; // Inner Surfaces
primitive_t_8s = {0, 0, 0, 0, 0, 0}; // Surfaces for changes
primitive_t_9s = {}; // Rotations
primitive_t_10s = {0, 0, 0, 0, 0, 0}; // Plane Surface?

// NX
primitive_xs = {
  -cylshell_r1/Sqrt(2), -cylshell_r2/Sqrt(2), -cylshell_r2/Sqrt(2), -cylshell_r1/Sqrt(2),
  -cylshell_r1/Sqrt(2), -cylshell_r2/Sqrt(2), -cylshell_r2/Sqrt(2), -cylshell_r1/Sqrt(2),
  0, 0, 0, 0,
  0, 0, 0, 0,
  0, 0, 0, 0
};
primitive_ys = {
  cylshell_r1/Sqrt(2), cylshell_r2/Sqrt(2), -cylshell_r2/Sqrt(2), -cylshell_r1/Sqrt(2),
  cylshell_r1/Sqrt(2), cylshell_r2/Sqrt(2), -cylshell_r2/Sqrt(2), -cylshell_r1/Sqrt(2),
  0, 0, 0, 0,
  0, 0, 0, 0,
  0, 0, 0, 0
};
primitive_zs = {
  -cylshell_h/2, -cylshell_h/2, -cylshell_h/2, -cylshell_h/2,
  cylshell_h/2, cylshell_h/2, cylshell_h/2, cylshell_h/2,
  0, 0, 0, 0,
  -cylshell_h/2, -cylshell_h/2, cylshell_h/2, cylshell_h/2,
  0, 0, 0, 0
};
// Parameters
primitive_t_1 = cylshell_t_2; 
If (cylshell_t_2_1)
  primitive_t_1_1 = 1/cylshell_t_2_1;
Else
  primitive_t_1_1 = cylshell_t_2_1;
EndIf
primitive_t_1_2 = cylshell_t_2_2; // Number of X nodes, progression, bump
primitive_t_2 = cylshell_t_1; primitive_t_2_1 = cylshell_t_1_1; primitive_t_2_2 = cylshell_t_1_2; // Number of Y nodes, progression, bump
primitive_t_5s = {0, 0, 0, 0, 1, 1, 1, 1, 0, 0, 0, 0}; // Type of lines: 0 - straight, 1 - circle, 2 - ellipse, 3 - Bezier, 4 - BSpline, 5+ - Spline
primitive_t_6 = 1; // Type of hex to tet splitting

Call primitive;

cylshell_iss += primitive_ss[1];
cylshell_lss += primitive_ss[0];
cylshell_nzss += primitive_ss[4];
cylshell_zss += primitive_ss[5];
cylshell_vs += primitive_vs[];

// X
primitive_xs = {
  cylshell_r2/Sqrt(2), cylshell_r1/Sqrt(2), cylshell_r1/Sqrt(2), cylshell_r2/Sqrt(2), 
  cylshell_r2/Sqrt(2), cylshell_r1/Sqrt(2), cylshell_r1/Sqrt(2), cylshell_r2/Sqrt(2),
  0, 0, 0, 0,
  0, 0, 0, 0,
  0, 0, 0, 0
};
primitive_ys = {
  cylshell_r2/Sqrt(2), cylshell_r1/Sqrt(2), -cylshell_r1/Sqrt(2), -cylshell_r2/Sqrt(2),
  cylshell_r2/Sqrt(2), cylshell_r1/Sqrt(2), -cylshell_r1/Sqrt(2), -cylshell_r2/Sqrt(2),
  0, 0, 0, 0,
  0, 0, 0, 0,
  0, 0, 0, 0
};
primitive_zs = {
  -cylshell_h/2, -cylshell_h/2, -cylshell_h/2, -cylshell_h/2,
  cylshell_h/2, cylshell_h/2, cylshell_h/2, cylshell_h/2,
  0, 0, 0, 0,
  -cylshell_h/2, -cylshell_h/2, cylshell_h/2, cylshell_h/2,
  0, 0, 0, 0
};
primitive_t_1 = cylshell_t_2; primitive_t_1_1 = cylshell_t_2_1; primitive_t_1_2 = cylshell_t_2_2; // Number of X nodes, progression, bump
primitive_t_2 = cylshell_t_1; primitive_t_2_1 = cylshell_t_1_1; primitive_t_2_2 = cylshell_t_1_2; // Number of Y nodes, progression, bump
primitive_t_5s = {0, 0, 0, 0, 1, 1, 1, 1, 0, 0, 0, 0}; // Type of lines: 0 - straight, 1 - circle, 2 - ellipse, 3 - Bezier, 4 - BSpline, 5+ - Spline
primitive_t_6 = 0; // Type of hex to tet splitting

Call primitive;

cylshell_iss += primitive_ss[0];
cylshell_lss += primitive_ss[1];
cylshell_nzss += primitive_ss[4];
cylshell_zss += primitive_ss[5];
cylshell_vs += primitive_vs[];

// NY
primitive_xs = {
  cylshell_r1/Sqrt(2), -cylshell_r1/Sqrt(2), -cylshell_r2/Sqrt(2), cylshell_r2/Sqrt(2),
  cylshell_r1/Sqrt(2), -cylshell_r1/Sqrt(2), -cylshell_r2/Sqrt(2), cylshell_r2/Sqrt(2),
  0, 0, 0, 0,
  0, 0, 0, 0,
  0, 0, 0, 0
};
primitive_ys = {
  -cylshell_r1/Sqrt(2), -cylshell_r1/Sqrt(2), -cylshell_r2/Sqrt(2), -cylshell_r2/Sqrt(2),
  -cylshell_r1/Sqrt(2), -cylshell_r1/Sqrt(2), -cylshell_r2/Sqrt(2), -cylshell_r2/Sqrt(2),
  0, 0, 0, 0,
  0, 0, 0, 0,
  0, 0, 0, 0
};
primitive_zs = {
  -cylshell_h/2, -cylshell_h/2, -cylshell_h/2, -cylshell_h/2,
  cylshell_h/2, cylshell_h/2, cylshell_h/2, cylshell_h/2,
  -cylshell_h/2, cylshell_h/2, cylshell_h/2, -cylshell_h/2,
  0, 0, 0, 0,
  0, 0, 0, 0
};
primitive_t_1 = cylshell_t_1; primitive_t_1_1 = cylshell_t_1_1; primitive_t_1_2 = cylshell_t_1_2; // Number of X nodes, progression, bump
primitive_t_2 = cylshell_t_2; primitive_t_2_1 = cylshell_t_2_1; primitive_t_2_2 = cylshell_t_2_2; // Number of Y nodes, progression, bump
primitive_t_5s = {1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0}; // Type of lines: 0 - straight, 1 - circle, 2 - ellipse, 3 - Bezier, 4 - BSpline, 5+ - Spline
primitive_t_6 = 3; // Type of hex to tet splitting

Call primitive;

cylshell_iss += primitive_ss[3];
cylshell_lss += primitive_ss[2];
cylshell_nzss += primitive_ss[4];
cylshell_zss += primitive_ss[5];
cylshell_vs += primitive_vs[];

// Y
primitive_xs = {
  cylshell_r2/Sqrt(2), -cylshell_r2/Sqrt(2), -cylshell_r1/Sqrt(2), cylshell_r1/Sqrt(2),
  cylshell_r2/Sqrt(2), -cylshell_r2/Sqrt(2), -cylshell_r1/Sqrt(2), cylshell_r1/Sqrt(2),
  0, 0, 0, 0,
  0, 0, 0, 0,
  0, 0, 0, 0
};
primitive_ys = {
  cylshell_r2/Sqrt(2), cylshell_r2/Sqrt(2), cylshell_r1/Sqrt(2), cylshell_r1/Sqrt(2),
  cylshell_r2/Sqrt(2), cylshell_r2/Sqrt(2), cylshell_r1/Sqrt(2), cylshell_r1/Sqrt(2),
  0, 0, 0, 0,
  0, 0, 0, 0,
  0, 0, 0, 0
};
primitive_zs = {
  -cylshell_h/2, -cylshell_h/2, -cylshell_h/2, -cylshell_h/2,
  cylshell_h/2, cylshell_h/2, cylshell_h/2, cylshell_h/2,
  -cylshell_h/2,  cylshell_h/2, cylshell_h/2, -cylshell_h/2,
  0, 0, 0, 0,
  0, 0, 0, 0
};
primitive_t_1 = cylshell_t_1; primitive_t_1_1 = cylshell_t_1_1; primitive_t_1_2 = cylshell_t_1_2; // Number of X nodes, progression, bump
primitive_t_2 = cylshell_t_2; primitive_t_2_1 = cylshell_t_2_1; primitive_t_2_2 = cylshell_t_2_2; // Number of Y nodes, progression, bump
primitive_t_5s = {1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0}; // Type of lines: 0 - straight, 1 - circle, 2 - ellipse, 3 - Bezier, 4 - BSpline, 5+ - Spline
primitive_t_6 = 0; // Type of hex to tet splitting

Call primitive;

cylshell_iss += primitive_ss[2];
cylshell_lss += primitive_ss[3];
cylshell_nzss += primitive_ss[4];
cylshell_zss += primitive_ss[5];
cylshell_vs += primitive_vs[];

Return

