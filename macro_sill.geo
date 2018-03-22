Include "macro_primitive.geo";

Macro sill
sill_vs[] = {};
// X-Y-NZ point, NX-Y-NZ, NX-NY-NZ, X-NY-NZ, (X - X axis, NX - negative X axis, etc)
// X-Y-Z, NX-Y-Z, NX-NY-Z, X-NY-Z,
// X1 line circle center, X2, X3, X4, (Line numeration by right hand rule from line contains X-Y-NZ point)
// Y1, Y2, Y3, Y4,
// Z1, Z2, Z3, Z4,
// X1 line ellipse point, X2, X3, X4,
// Y1, Y2, Y3, Y4,
// Z1, Z2, Z3, Z4
primitive_lcs[] = {
  sill_lcs[0], sill_lcs[1], sill_lcs[2], sill_lcs[3],
  sill_lcs[4], sill_lcs[5], sill_lcs[6], sill_lcs[7],
  1, 1, 1, 1,
  1, 1, 1, 1,
  1, 1, 1, 1,
  1, 1, 1, 1,
  1, 1, 1, 1,
  1, 1, 1, 1
};
primitive_xs[] = {
  1*sill_kx, -1*sill_kx, -1*sill_kx, 1*sill_kx, 
  1*sill_kx, -1*sill_kx, -1*sill_kx, 1*sill_kx, 
  0, 0, 0, 0,
  0, 0, 0, 0,
  0, 0, 0, 0,
  0, 0, 0, 0,
  0, 0, 0, 0,
  0, 0, 0, 0
};
primitive_ys[] = {
  1*sill_ky, 1*sill_ky, -1*sill_ky, -1*sill_ky,
  1*sill_ky, 1*sill_ky, -1*sill_ky, -1*sill_ky,
  0, 0, 0, 0,
  0, 0, 0, 0,
  0, 0, 0, 0,
  0, 0, 0, 0,
  0, 0, 0, 0,
  0, 0, 0, 0
};
primitive_zs[] = {
  -4*sill_kz, -3*sill_kz, 8*sill_kz, -1*sill_kz,
  -3*sill_kz, -1*sill_kz, 10*sill_kz, 1*sill_kz,
  0, 0, 0, 0,
  0, 0, 0, 0,
  0, 0, 0, 0,
  0, 0, 0, 0,
  0, 0, 0, 0,
  0, 0, 0, 0
};
primitive_ox = sill_ox; primitive_oy = sill_oy; primitive_oz = sill_oz; // Origin: x, y, z
primitive_rox = 0; primitive_roy = 0; primitive_roz = 0; // Local Rotation Origin: x, y, z
primitive_rax = 0; primitive_ray = 0; primitive_raz = 0; // Local Rotation Angle: x, y, z
// Parameters
primitive_t_1 = 0; primitive_t_1_1 = 0; primitive_t_1_2 = 0; // Number of X nodes, progression, bump
primitive_t_2 = 0; primitive_t_2_1 = 0; primitive_t_2_2 = 0; // Number of Y nodes, progression, bump
primitive_t_3 = 0; primitive_t_3_1 = 0; primitive_t_3_2 = 0; // Number of Z nodes, progression, bump
primitive_t_4 = 0; // Hex (1) or tet (0) mesh?
primitive_t_5s[] = {0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0}; // Type of lines: 0 - straight, 1 - circle, 2 - ellipse, 3 - Bezier, 4 - BSpline, 5+ - Spline
primitive_t_6 = 0; // Type of hex to tet splitting
primitive_t_7s[] = {}; // Inner Surfaces
primitive_t_8s[] = {0, 0, 0, 0, 0, 0}; // Surfaces for changes
primitive_t_9s[] = {}; // Rotations
primitive_t_10s[] = {0, 0, 0, 0, 0, 0}; // Plane Surface?
// Curve 0 (point 1 -> point 2)
primitive_t_5s_lcs_0[] = {};
primitive_t_5s_xs_0[] = {};
primitive_t_5s_ys_0[] = {};
primitive_t_5s_zs_0[] = {};
n = 24; // Number of curve points
dy = 2; // Delta Y
dx = (n-1)/n*(primitive_xs[0]-primitive_xs[1]); // Delta X
For i In {1 : n}
  primitive_t_5s_lcs_0[] += 0.1;
  primitive_t_5s_xs_0[] += primitive_xs[1] + i/n*dx;
  primitive_t_5s_ys_0[] += primitive_ys[1] + Sin(i/n*2*Pi)*dy;
  primitive_t_5s_zs_0[] += primitive_zs[1];
EndFor
Call primitive;
sill_vs[] += primitive_vs[];

Return
