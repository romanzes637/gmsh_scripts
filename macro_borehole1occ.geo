Include "macro_primitive.geo";

Macro borehole1occ
borehole1occ_vs[] = {};
For borehole1occ_i In {0 : #borehole1occ_rs[]-1}
  // X-Y-NZ point, NX-Y-NZ, NX-NY-NZ, X-NY-NZ, (X - X axis, NX - negative X axis, etc)
  // X-Y-Z, NX-Y-Z, NX-NY-Z, X-NY-Z,
  // X1 line circle center, X2, X3, X4, (Line numeration by right hand rule from line contains X-Y-NZ point)
  // Y1, Y2, Y3, Y4,
  // Z1, Z2, Z3, Z4,
  // X1 line ellipse point, X2, X3, X4,
  // Y1, Y2, Y3, Y4,
  // Z1, Z2, Z3, Z4
  primitive_lcs[] = {
    borehole1occ_lcs[borehole1occ_i], borehole1occ_lcs[borehole1occ_i], borehole1occ_lcs[borehole1occ_i], borehole1occ_lcs[borehole1occ_i],
    borehole1occ_lcs[borehole1occ_i], borehole1occ_lcs[borehole1occ_i], borehole1occ_lcs[borehole1occ_i], borehole1occ_lcs[borehole1occ_i],
    borehole1occ_lcs[borehole1occ_i], borehole1occ_lcs[borehole1occ_i], borehole1occ_lcs[borehole1occ_i], borehole1occ_lcs[borehole1occ_i],
    borehole1occ_lcs[borehole1occ_i], borehole1occ_lcs[borehole1occ_i], borehole1occ_lcs[borehole1occ_i], borehole1occ_lcs[borehole1occ_i],
    borehole1occ_lcs[borehole1occ_i], borehole1occ_lcs[borehole1occ_i], borehole1occ_lcs[borehole1occ_i], borehole1occ_lcs[borehole1occ_i]
  };
  primitive_xs[] = {
    borehole1occ_rs[borehole1occ_i], 0, -borehole1occ_rs[borehole1occ_i], 0, 
    borehole1occ_rs[borehole1occ_i], 0, -borehole1occ_rs[borehole1occ_i], 0, 
    0, 0, 0, 0,
    0, 0, 0, 0,
    0, 0, 0, 0
  };
  primitive_ys[] = {
    0, borehole1occ_rs[borehole1occ_i], 0, -borehole1occ_rs[borehole1occ_i],
    0, borehole1occ_rs[borehole1occ_i], 0, -borehole1occ_rs[borehole1occ_i],
    0, 0, 0, 0,
    0, 0, 0, 0,
    0, 0, 0, 0
  };
  primitive_zs[] = {
    -borehole1occ_hs[borehole1occ_i]/2, -borehole1occ_hs[borehole1occ_i]/2, -borehole1occ_hs[borehole1occ_i]/2, -borehole1occ_hs[borehole1occ_i]/2,
    borehole1occ_hs[borehole1occ_i]/2, borehole1occ_hs[borehole1occ_i]/2, borehole1occ_hs[borehole1occ_i]/2, borehole1occ_hs[borehole1occ_i]/2,
    -borehole1occ_hs[borehole1occ_i]/2, borehole1occ_hs[borehole1occ_i]/2, borehole1occ_hs[borehole1occ_i]/2, -borehole1occ_hs[borehole1occ_i]/2,
    -borehole1occ_hs[borehole1occ_i]/2, -borehole1occ_hs[borehole1occ_i]/2, borehole1occ_hs[borehole1occ_i]/2, borehole1occ_hs[borehole1occ_i]/2,
    0, 0, 0, 0
  };
  primitive_ox = borehole1occ_ox; primitive_oy = borehole1occ_oy; primitive_oz = borehole1occ_oz; // Origin: x, y, z
  primitive_rox = 0; primitive_roy = 0; primitive_roz = 0; // Local Rotation Origin: x, y, z
  primitive_rax = 0; primitive_ray = 0; primitive_raz = 0; // Local Rotation Angle: x, y, z
  // Parameters
  primitive_t_1 = 0; primitive_t_1_1 = 0; primitive_t_1_2 = 0; // Number of X nodes, progression, bump
  primitive_t_2 = 0; primitive_t_2_1 = 0; primitive_t_2_2 = 0; // Number of Y nodes, progression, bump
  primitive_t_3 = 0; primitive_t_3_1 = 0; primitive_t_3_2 = 0; // Number of Z nodes, progression, bump
  primitive_t_4 = 0; // Hex (1) or tet (0) mesh?
  primitive_t_5s[] = {1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0}; // Type of lines: 0 - straight, 1 - circle, 2 - ellipse, 3 - Bezier, 4 - BSpline, 5+ - Spline
  primitive_t_6 = 0; // Type of hex to tet splitting
  primitive_t_7s[] = {}; // Inner Surfaces
  primitive_t_8s[] = {0, 0, 0, 0, 0, 0}; // Surfaces for changes
  primitive_t_9s[] = {}; // Rotations
  primitive_t_10s[] = {0, 0, 0, 0, 0, 0}; // Plane Surface?
  Call primitive;
  borehole1occ_vs[] += primitive_vs[];
EndFor
If (#borehole1occ_rs[] > 1)
  borehole1occ_out[] = BooleanFragments{ Volume{borehole1occ_vs[]}; Delete; } {};
Else
  borehole1occ_out[] = borehole1occ_vs[];
EndIf

Return
