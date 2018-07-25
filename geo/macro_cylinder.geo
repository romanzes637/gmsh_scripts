Include "macro_primitive.geo";
Include "macro_hexahedron.geo";

Macro cylinder

cylinder_lss = {};
cylinder_nzss = {};
cylinder_zss = {};
cylinder_vs = {};

// Core
hexahedron_lc = cylinder_lc; // Points characteristic length
hexahedron_a = 2*cylinder_k*cylinder_r; // X length
hexahedron_b = 2*cylinder_k*cylinder_r; // Y length
hexahedron_c = cylinder_h; // Z length
hexahedron_ox = cylinder_ox; hexahedron_oy = cylinder_oy; hexahedron_oz = cylinder_oz; // Origin: x, y, z
hexahedron_rox = cylinder_rox; hexahedron_roy = cylinder_roy; hexahedron_roz = cylinder_roz; // Local Rotation Origin: x, y, z
hexahedron_rax = cylinder_rax; hexahedron_ray = cylinder_ray; hexahedron_raz = cylinder_raz; // Local Rotation Angle: x, y, z
// Parameters
hexahedron_t_1 = cylinder_t_1; hexahedron_t_1_1 = cylinder_t_1_1; hexahedron_t_1_2 = cylinder_t_1_2; // Number of X nodes, progression, bump
hexahedron_t_2 = cylinder_t_1; hexahedron_t_2_1 = cylinder_t_1_1; hexahedron_t_2_2 = cylinder_t_1_2; // Number of Y nodes, progression, bump
hexahedron_t_3 = cylinder_t_3; hexahedron_t_3_1 = cylinder_t_3_1; hexahedron_t_3_2 = cylinder_t_3_2; // Number of Z nodes, progression, bump
hexahedron_t_4 = cylinder_t_4; // Hex (1) or tet (0) mesh?
hexahedron_t_6 = 0; // Type of hex to tet splitting
hexahedron_t_7s = {}; // Inner Surfaces

Call hexahedron;

cylinder_nzss += hexahedron_nzss[];
cylinder_zss += hexahedron_zss[];
cylinder_vs += hexahedron_vs[];

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
  cylinder_lc, cylinder_lc, cylinder_lc, cylinder_lc,
  cylinder_lc, cylinder_lc, cylinder_lc, cylinder_lc,
  cylinder_lc, cylinder_lc, cylinder_lc, cylinder_lc,
  cylinder_lc, cylinder_lc, cylinder_lc, cylinder_lc,
  cylinder_lc, cylinder_lc, cylinder_lc, cylinder_lc
};
primitive_ox = cylinder_ox; primitive_oy = cylinder_oy; primitive_oz = cylinder_oz; // Origin: x, y, z
primitive_rox = cylinder_rox; primitive_roy = cylinder_roy; primitive_roz = cylinder_roz; // Local Rotation Origin: x, y, z
primitive_rax = cylinder_rax; primitive_ray = cylinder_ray; primitive_raz = cylinder_raz; // Local Rotation Angle: x, y, z
// Parameters
primitive_t_3 = cylinder_t_3; primitive_t_3_1 = cylinder_t_3_1; primitive_t_3_2 = cylinder_t_3_2; // Number of Z nodes, progression, bump
primitive_t_4 = cylinder_t_4; // Hex (1) or tet (0) mesh?
primitive_t_7s = {}; // Inner Surfaces
primitive_t_8s = {0, 0, 0, 0, 0, 0}; // Surfaces for changes
primitive_t_9s = {}; // Rotations
primitive_t_10s = {0, 0, 0, 0, 0, 0}; // Plane Surface?

// NX
primitive_xs = {
  -cylinder_k*cylinder_r, -cylinder_r/Sqrt(2), -cylinder_r/Sqrt(2), -cylinder_k*cylinder_r,
  -cylinder_k*cylinder_r, -cylinder_r/Sqrt(2), -cylinder_r/Sqrt(2), -cylinder_k*cylinder_r, 
  0, 0, 0, 0,
  0, 0, 0, 0,
  0, 0, 0, 0
};
primitive_ys = {
  cylinder_k*cylinder_r, cylinder_r/Sqrt(2), -cylinder_r/Sqrt(2), -cylinder_k*cylinder_r,
  cylinder_k*cylinder_r, cylinder_r/Sqrt(2), -cylinder_r/Sqrt(2), -cylinder_k*cylinder_r,
  0, 0, 0, 0,
  0, 0, 0, 0,
  0, 0, 0, 0
};
primitive_zs = {
  -cylinder_h/2, -cylinder_h/2, -cylinder_h/2, -cylinder_h/2,
  cylinder_h/2, cylinder_h/2, cylinder_h/2, cylinder_h/2,
  0, 0, 0, 0,
  0, -cylinder_h/2, cylinder_h/2, 0,
  0, 0, 0, 0
};
// Parameters
primitive_t_1 = cylinder_t_2; 
If (cylinder_t_2_1)
  primitive_t_1_1 = 1/cylinder_t_2_1;
Else
  primitive_t_1_1 = cylinder_t_2_1;
EndIf
primitive_t_1_2 = cylinder_t_2_2; // Number of X nodes, progression, bump
primitive_t_2 = cylinder_t_1; primitive_t_2_1 = cylinder_t_1_1; primitive_t_2_2 = cylinder_t_1_2; // Number of Y nodes, progression, bump
primitive_t_5s = {0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0}; // Type of lines: 0 - straight, 1 - circle, 2 - ellipse, 3 - Bezier, 4 - BSpline, 5+ - Spline
primitive_t_6 = 1; // Type of hex to tet splitting

Call primitive;

cylinder_lss += primitive_ss[0];
cylinder_nzss += primitive_ss[4];
cylinder_zss += primitive_ss[5];
cylinder_vs += primitive_vs[];

// X
primitive_xs = {
  cylinder_r/Sqrt(2), cylinder_k*cylinder_r, cylinder_k*cylinder_r, cylinder_r/Sqrt(2), 
  cylinder_r/Sqrt(2), cylinder_k*cylinder_r, cylinder_k*cylinder_r, cylinder_r/Sqrt(2), 
  0, 0, 0, 0,
  0, 0, 0, 0,
  0, 0, 0, 0
};
primitive_ys = {
  cylinder_r/Sqrt(2), cylinder_k*cylinder_r, -cylinder_k*cylinder_r, -cylinder_r/Sqrt(2),
  cylinder_r/Sqrt(2), cylinder_k*cylinder_r, -cylinder_k*cylinder_r, -cylinder_r/Sqrt(2),
  0, 0, 0, 0,
  0, 0, 0, 0,
  0, 0, 0, 0
};
primitive_zs = {
  -cylinder_h/2, -cylinder_h/2, -cylinder_h/2, -cylinder_h/2,
  cylinder_h/2, cylinder_h/2, cylinder_h/2, cylinder_h/2,
  0, 0, 0, 0,
  -cylinder_h/2, 0, 0, cylinder_h/2,
  0, 0, 0, 0
};
primitive_t_1 = cylinder_t_2; primitive_t_1_1 = cylinder_t_2_1; primitive_t_1_2 = cylinder_t_2_2; // Number of X nodes, progression, bump
primitive_t_2 = cylinder_t_1; primitive_t_2_1 = cylinder_t_1_1; primitive_t_2_2 = cylinder_t_1_2; // Number of Y nodes, progression, bump
primitive_t_5s = {0, 0, 0, 0, 1, 0, 0, 1, 0, 0, 0, 0}; // Type of lines: 0 - straight, 1 - circle, 2 - ellipse, 3 - Bezier, 4 - BSpline, 5+ - Spline
primitive_t_6 = 0; // Type of hex to tet splitting

Call primitive;

cylinder_lss += primitive_ss[1];
cylinder_nzss += primitive_ss[4];
cylinder_zss += primitive_ss[5];
cylinder_vs += primitive_vs[];

// NY
primitive_xs = {
  cylinder_k*cylinder_r, -cylinder_k*cylinder_r, -cylinder_r/Sqrt(2), cylinder_r/Sqrt(2),
  cylinder_k*cylinder_r, -cylinder_k*cylinder_r, -cylinder_r/Sqrt(2), cylinder_r/Sqrt(2), 
  0, 0, 0, 0,
  0, 0, 0, 0,
  0, 0, 0, 0
};
primitive_ys = {
  -cylinder_k*cylinder_r, -cylinder_k*cylinder_r, -cylinder_r/Sqrt(2), -cylinder_r/Sqrt(2),
  -cylinder_k*cylinder_r, -cylinder_k*cylinder_r, -cylinder_r/Sqrt(2), -cylinder_r/Sqrt(2),
  0, 0, 0, 0,
  0, 0, 0, 0,
  0, 0, 0, 0
};
primitive_zs = {
  -cylinder_h/2, -cylinder_h/2, -cylinder_h/2, -cylinder_h/2,
  cylinder_h/2, cylinder_h/2, cylinder_h/2, cylinder_h/2,
  0, 0, cylinder_h/2, -cylinder_h/2,
  0, 0, 0, 0,
  0, 0, 0, 0
};
primitive_t_1 = cylinder_t_1; primitive_t_1_1 = cylinder_t_1_1; primitive_t_1_2 = cylinder_t_1_2; // Number of X nodes, progression, bump
primitive_t_2 = cylinder_t_2; primitive_t_2_1 = cylinder_t_2_1; primitive_t_2_2 = cylinder_t_2_2; // Number of Y nodes, progression, bump
primitive_t_5s = {0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0}; // Type of lines: 0 - straight, 1 - circle, 2 - ellipse, 3 - Bezier, 4 - BSpline, 5+ - Spline
primitive_t_6 = 3; // Type of hex to tet splitting

Call primitive;

cylinder_lss += primitive_ss[2];
cylinder_nzss += primitive_ss[4];
cylinder_zss += primitive_ss[5];
cylinder_vs += primitive_vs[];

// Y
primitive_xs = {
  cylinder_r/Sqrt(2), -cylinder_r/Sqrt(2), -cylinder_k*cylinder_r, cylinder_k*cylinder_r,
  cylinder_r/Sqrt(2), -cylinder_r/Sqrt(2), -cylinder_k*cylinder_r, cylinder_k*cylinder_r,
  0, 0, 0, 0,
  0, 0, 0, 0,
  0, 0, 0, 0
};
primitive_ys = {
  cylinder_r/Sqrt(2), cylinder_r/Sqrt(2), cylinder_k*cylinder_r, cylinder_k*cylinder_r,
  cylinder_r/Sqrt(2), cylinder_r/Sqrt(2), cylinder_k*cylinder_r, cylinder_k*cylinder_r,
  0, 0, 0, 0,
  0, 0, 0, 0,
  0, 0, 0, 0
};
primitive_zs = {
  -cylinder_h/2, -cylinder_h/2, -cylinder_h/2, -cylinder_h/2,
  cylinder_h/2, cylinder_h/2, cylinder_h/2, cylinder_h/2,
  -cylinder_h/2,  cylinder_h/2, 0, 0,
  0, 0, 0, 0,
  0, 0, 0, 0
};
primitive_t_1 = cylinder_t_1; primitive_t_1_1 = cylinder_t_1_1; primitive_t_1_2 = cylinder_t_1_2; // Number of X nodes, progression, bump
primitive_t_2 = cylinder_t_2; primitive_t_2_1 = cylinder_t_2_1; primitive_t_2_2 = cylinder_t_2_2; // Number of Y nodes, progression, bump
primitive_t_5s = {1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0}; // Type of lines: 0 - straight, 1 - circle, 2 - ellipse, 3 - Bezier, 4 - BSpline, 5+ - Spline
primitive_t_6 = 0; // Type of hex to tet splitting

Call primitive;

cylinder_lss += primitive_ss[3];
cylinder_nzss += primitive_ss[4];
cylinder_zss += primitive_ss[5];
cylinder_vs += primitive_vs[];

Return

