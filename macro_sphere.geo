Include "macro_primitive.geo";
Include "macro_hexahedron.geo";

Macro sphere

sphere_lss = {};
sphere_vs = {};

// Core
hexahedron_lc = sphere_lc; // Points characteristic length
hexahedron_a = 2*sphere_k*sphere_r; // X length
hexahedron_b = 2*sphere_k*sphere_r; // Y length
hexahedron_c = 2*sphere_k*sphere_r; // Z length
hexahedron_ox = sphere_ox; hexahedron_oy = sphere_oy; hexahedron_oz = sphere_oz; // Origin: x, y, z
hexahedron_rox = sphere_rox; hexahedron_roy = sphere_roy; hexahedron_roz = sphere_roz; // Local Rotation Origin: x, y, z
hexahedron_rax = sphere_rax; hexahedron_ray = sphere_ray; hexahedron_raz = sphere_raz; // Local Rotation Angle: x, y, z
// Parameters
hexahedron_t_1 = sphere_t_1; hexahedron_t_1_1 = 0; hexahedron_t_1_2 = 0; // Number of X nodes, progression, bump
hexahedron_t_2 = sphere_t_1; hexahedron_t_2_1 = 0; hexahedron_t_2_2 = 0; // Number of Y nodes, progression, bump
hexahedron_t_3 = sphere_t_1; hexahedron_t_3_1 = 0; hexahedron_t_3_2 = 0; // Number of Z nodes, progression, bump
hexahedron_t_4 = sphere_t_4; // Hex (1) or tet (0) mesh?
hexahedron_t_6 = 0; // Type of hex to tet splitting
hexahedron_t_7s = {}; // Inner Surfaces

Call hexahedron;

sphere_vs += hexahedron_vs[];

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
  sphere_lc, sphere_lc, sphere_lc, sphere_lc,
  sphere_lc, sphere_lc, sphere_lc, sphere_lc,
  sphere_lc, sphere_lc, sphere_lc, sphere_lc,
  sphere_lc, sphere_lc, sphere_lc, sphere_lc,
  sphere_lc, sphere_lc, sphere_lc, sphere_lc
};
primitive_ox = sphere_ox; primitive_oy = sphere_oy; primitive_oz = sphere_oz; // Origin: x, y, z
primitive_rox = sphere_rox; primitive_roy = sphere_roy; primitive_roz = sphere_roz; // Local Rotation Origin: x, y, z
primitive_rax = sphere_rax; primitive_ray = sphere_ray; primitive_raz = sphere_raz; // Local Rotation Angle: x, y, z
// Parameters
primitive_t_4 = sphere_t_4; // Hex (1) or tet (0) mesh?
primitive_t_7s = {}; // Inner Surfaces
primitive_t_8s = {0, 0, 0, 0, 0, 0}; // Surfaces for changes
primitive_t_9s = {}; // Rotations
primitive_t_10s = {0, 0, 0, 0, 0, 0}; // Plane Surface?

// NX
primitive_xs = {
  -sphere_k*sphere_r, -sphere_r/Sqrt(3), -sphere_r/Sqrt(3), -sphere_k*sphere_r,
  -sphere_k*sphere_r, -sphere_r/Sqrt(3), -sphere_r/Sqrt(3), -sphere_k*sphere_r, 
  0, 0, 0, 0,
  0, 0, 0, 0,
  0, 0, 0, 0
};
primitive_ys = {
  sphere_k*sphere_r, sphere_r/Sqrt(3), -sphere_r/Sqrt(3), -sphere_k*sphere_r,
  sphere_k*sphere_r, sphere_r/Sqrt(3), -sphere_r/Sqrt(3), -sphere_k*sphere_r,
  0, 0, 0, 0,
  0, 0, 0, 0,
  0, 0, 0, 0
};
primitive_zs = {
  -sphere_k*sphere_r, -sphere_r/Sqrt(3), -sphere_r/Sqrt(3), -sphere_k*sphere_r,
  sphere_k*sphere_r, sphere_r/Sqrt(3), sphere_r/Sqrt(3), sphere_k*sphere_r,
  0, 0, 0, 0,
  0, 0, 0, 0,
  0, 0, 0, 0
};
// Parameters
primitive_t_1 = sphere_t_2; 
If (sphere_t_2_1)
  primitive_t_1_1 = 1/sphere_t_2_1;
Else
  primitive_t_1_1 = sphere_t_2_1;
EndIf
primitive_t_2_2 = sphere_t_2_2; // Number of X nodes, progression, bump
primitive_t_2 = sphere_t_1; primitive_t_2_1 = sphere_t_1_1; primitive_t_2_2 = sphere_t_1_2; // Number of Y nodes, progression, bump
primitive_t_3 = sphere_t_1; primitive_t_3_1 = 0; primitive_t_3_2 = 0; // Number of Z nodes, progression, bump
primitive_t_5s = {0, 0, 0, 0, 0, 1, 1, 0, 0, 1, 1, 0}; // Type of lines: 0 - straight, 1 - circle, 2 - ellipse, 3 - Bezier, 4 - BSpline, 5+ - Spline
primitive_t_6 = 1; // Type of hex to tet splitting

Call primitive;

sphere_lss += primitive_ss[0];
sphere_vs += primitive_vs[];

// X
primitive_xs = {
  sphere_r/Sqrt(3), sphere_k*sphere_r, sphere_k*sphere_r, sphere_r/Sqrt(3), 
  sphere_r/Sqrt(3), sphere_k*sphere_r, sphere_k*sphere_r, sphere_r/Sqrt(3), 
  0, 0, 0, 0,
  0, 0, 0, 0,
  0, 0, 0, 0
};
primitive_ys = {
  sphere_r/Sqrt(3), sphere_k*sphere_r, -sphere_k*sphere_r, -sphere_r/Sqrt(3),
  sphere_r/Sqrt(3), sphere_k*sphere_r, -sphere_k*sphere_r, -sphere_r/Sqrt(3),
  0, 0, 0, 0,
  0, 0, 0, 0,
  0, 0, 0, 0
};
primitive_zs = {
  -sphere_r/Sqrt(3), -sphere_k*sphere_r, -sphere_k*sphere_r, -sphere_r/Sqrt(3),
  sphere_r/Sqrt(3), sphere_k*sphere_r, sphere_k*sphere_r, sphere_r/Sqrt(3),
  0, 0, 0, 0,
  0, 0, 0, 0,
  0, 0, 0, 0
};
primitive_t_1 = sphere_t_2; primitive_t_1_1 = sphere_t_2_1; primitive_t_1_2 = sphere_t_2_2; // Number of X nodes, progression, bump
primitive_t_2 = sphere_t_1; primitive_t_2_1 = sphere_t_1_1; primitive_t_2_2 = sphere_t_1_2; // Number of Y nodes, progression, bump
primitive_t_3 = sphere_t_1; primitive_t_3_1 = 0; primitive_t_3_2 = 0; // Number of Z nodes, progression, bump
primitive_t_5s = {0, 0, 0, 0, 1, 0, 0, 1, 1, 0, 0, 1}; // Type of lines: 0 - straight, 1 - circle, 2 - ellipse, 3 - Bezier, 4 - BSpline, 5+ - Spline
primitive_t_6 = 0; // Type of hex to tet splitting

Call primitive;

sphere_lss += primitive_ss[1];
sphere_vs += primitive_vs[];

// sphere NY
primitive_xs = {
  sphere_k*sphere_r, -sphere_k*sphere_r, -sphere_r/Sqrt(3), sphere_r/Sqrt(3),
  sphere_k*sphere_r, -sphere_k*sphere_r, -sphere_r/Sqrt(3), sphere_r/Sqrt(3), 
  0, 0, 0, 0,
  0, 0, 0, 0,
  0, 0, 0, 0
};
primitive_ys = {
  -sphere_k*sphere_r, -sphere_k*sphere_r, -sphere_r/Sqrt(3), -sphere_r/Sqrt(3),
  -sphere_k*sphere_r, -sphere_k*sphere_r, -sphere_r/Sqrt(3), -sphere_r/Sqrt(3),
  0, 0, 0, 0,
  0, 0, 0, 0,
  0, 0, 0, 0
};
primitive_zs = {
  -sphere_k*sphere_r, -sphere_k*sphere_r, -sphere_r/Sqrt(3), -sphere_r/Sqrt(3),
  sphere_k*sphere_r, sphere_k*sphere_r, sphere_r/Sqrt(3), sphere_r/Sqrt(3),
  0, 0, 0, 0,
  0, 0, 0, 0,
  0, 0, 0, 0
};
primitive_t_1 = sphere_t_1; primitive_t_1_1 = sphere_t_1_1; primitive_t_1_2 = sphere_t_1_2; // Number of X nodes, progression, bump
primitive_t_2 = sphere_t_2;
If (sphere_t_2_1)
  primitive_t_2_1 = 1/sphere_t_2_1;
Else
  primitive_t_2_1 = sphere_t_2_1;
EndIf
primitive_t_2_2 = sphere_t_2_2; // Number of Y nodes, progression, bump
primitive_t_3 = sphere_t_1; primitive_t_3_1 = sphere_t_1_1; primitive_t_3_2 = sphere_t_1_2; // Number of Z nodes, progression, bump
primitive_t_5s = {0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 1, 1}; // Type of lines: 0 - straight, 1 - circle, 2 - ellipse, 3 - Bezier, 4 - BSpline, 5+ - Spline
primitive_t_6 = 3; // Type of hex to tet splitting

Call primitive;

sphere_lss += primitive_ss[2];
sphere_vs += primitive_vs[];

// Y
primitive_xs = {
  sphere_r/Sqrt(3), -sphere_r/Sqrt(3), -sphere_k*sphere_r, sphere_k*sphere_r,
  sphere_r/Sqrt(3), -sphere_r/Sqrt(3), -sphere_k*sphere_r, sphere_k*sphere_r,
  0, 0, 0, 0,
  0, 0, 0, 0,
  0, 0, 0, 0
};
primitive_ys = {
  sphere_r/Sqrt(3), sphere_r/Sqrt(3), sphere_k*sphere_r, sphere_k*sphere_r,
  sphere_r/Sqrt(3), sphere_r/Sqrt(3), sphere_k*sphere_r, sphere_k*sphere_r,
  0, 0, 0, 0,
  0, 0, 0, 0,
  0, 0, 0, 0
};
primitive_zs = {
  -sphere_r/Sqrt(3), -sphere_r/Sqrt(3), -sphere_k*sphere_r, -sphere_k*sphere_r,
  sphere_r/Sqrt(3), sphere_r/Sqrt(3), sphere_k*sphere_r, sphere_k*sphere_r,
  0,  0, 0, 0,
  0, 0, 0, 0,
  0, 0, 0, 0
};
primitive_t_1 = sphere_t_1; primitive_t_1_1 = sphere_t_1_1; primitive_t_1_2 = sphere_t_1_2; // Number of X nodes, progression, bump
primitive_t_2 = sphere_t_2; primitive_t_2_1 = sphere_t_2_1; primitive_t_2_2 = sphere_t_2_2; // Number of Y nodes, progression, bump
primitive_t_3 = sphere_t_1; primitive_t_3_1 = sphere_t_1_1; primitive_t_3_2 = sphere_t_1_2; // Number of Z nodes, progression, bump
primitive_t_5s = {1, 1, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0}; // Type of lines: 0 - straight, 1 - circle, 2 - ellipse, 3 - Bezier, 4 - BSpline, 5+ - Spline
primitive_t_6 = 0; // Type of hex to tet splitting

Call primitive;

sphere_lss += primitive_ss[3];
sphere_vs += primitive_vs[];

// NZ
primitive_xs = {
  sphere_r/Sqrt(3), -sphere_r/Sqrt(3), -sphere_r/Sqrt(3), sphere_r/Sqrt(3), 
  sphere_k*sphere_r, -sphere_k*sphere_r, -sphere_k*sphere_r, sphere_k*sphere_r,
  0, 0, 0, 0,
  0, 0, 0, 0,
  0, 0, 0, 0
};
primitive_ys = {
  sphere_r/Sqrt(3), sphere_r/Sqrt(3), -sphere_r/Sqrt(3), -sphere_r/Sqrt(3),
  sphere_k*sphere_r, sphere_k*sphere_r, -sphere_k*sphere_r, -sphere_k*sphere_r,
  0, 0, 0, 0,
  0, 0, 0, 0,
  0, 0, 0, 0
};
primitive_zs = {
  -sphere_r/Sqrt(3), -sphere_r/Sqrt(3), -sphere_r/Sqrt(3), -sphere_r/Sqrt(3),
  -sphere_k*sphere_r, -sphere_k*sphere_r, -sphere_k*sphere_r, -sphere_k*sphere_r,
  0, 0, 0, 0,
  0, 0, 0, 0,
  0, 0, 0, 0
};
primitive_t_1 = sphere_t_2; primitive_t_1_1 = sphere_t_2_1; primitive_t_1_2 = sphere_t_2_2; // Number of X nodes, progression, bump
primitive_t_2 = sphere_t_2; primitive_t_2_1 = sphere_t_2_1; primitive_t_2_2 = sphere_t_2_2; // Number of Y nodes, progression, bump
primitive_t_3 = sphere_t_1;
If (sphere_t_1_1)
  primitive_t_3_1 = 1/sphere_t_1_1;
Else
  primitive_t_3_1 = sphere_t_1_1;
EndIf
primitive_t_3_2 = sphere_t_1_2; // Number of Z nodes, progression, bump
primitive_t_5s = {1, 0, 0, 1, 1, 1, 0, 0, 0, 0, 0, 0}; // Type of lines: 0 - straight, 1 - circle, 2 - ellipse, 3 - Bezier, 4 - BSpline, 5+ - Spline
primitive_t_6 = 0; // Type of hex to tet splitting

Call primitive;

sphere_lss += primitive_ss[4];
sphere_vs += primitive_vs[];

// Z
primitive_xs = {
  sphere_k*sphere_r, -sphere_k*sphere_r, -sphere_k*sphere_r, sphere_k*sphere_r,
  sphere_r/Sqrt(3), -sphere_r/Sqrt(3), -sphere_r/Sqrt(3), sphere_r/Sqrt(3), 
  0, 0, 0, 0,
  0, 0, 0, 0,
  0, 0, 0, 0
};
primitive_ys = {
  sphere_k*sphere_r, sphere_k*sphere_r, -sphere_k*sphere_r, -sphere_k*sphere_r,
  sphere_r/Sqrt(3), sphere_r/Sqrt(3), -sphere_r/Sqrt(3), -sphere_r/Sqrt(3),
  0, 0, 0, 0,
  0, 0, 0, 0,
  0, 0, 0, 0
};
primitive_zs = {
  sphere_k*sphere_r, sphere_k*sphere_r, sphere_k*sphere_r, sphere_k*sphere_r,
  sphere_r/Sqrt(3), sphere_r/Sqrt(3), sphere_r/Sqrt(3), sphere_r/Sqrt(3),
  0, 0, 0, 0,
  0, 0, 0, 0,
  0, 0, 0, 0
};
primitive_t_1 = sphere_t_1; primitive_t_1_1 = sphere_t_1_1; primitive_t_1_2 = sphere_t_1_2; // Number of X nodes, progression, bump
primitive_t_2 = sphere_t_1; primitive_t_2_1 = sphere_t_1_1; primitive_t_2_2 = sphere_t_1_2; // Number of Y nodes, progression, bump
primitive_t_3 = sphere_t_2; primitive_t_3_1 = sphere_t_2_1; primitive_t_3_2 = sphere_t_2_2; // Number of Z nodes, progression, bump
primitive_t_5s = {0, 1, 1, 0, 0, 0, 1, 1, 0, 0, 0, 0}; // Type of lines: 0 - straight, 1 - circle, 2 - ellipse, 3 - Bezier, 4 - BSpline, 5+ - Spline
primitive_t_6 = 2; // Type of hex to tet splitting

Call primitive;

sphere_lss += primitive_ss[5];
sphere_vs += primitive_vs[];

Return

