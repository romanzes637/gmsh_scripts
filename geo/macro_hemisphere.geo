Include "macro_primitive.geo";
Include "macro_hexahedron.geo";

Macro hemisphere

hemisphere_nzss = {};
hemisphere_zss = {};
hemisphere_lss = {};
hemisphere_vs = {};

// Core
hexahedron_lc = hemisphere_lc; // Points characteristic length
hexahedron_a = 2*hemisphere_k*hemisphere_r; // X length
hexahedron_b = 2*hemisphere_k*hemisphere_r; // Y length
hexahedron_c = hemisphere_k*hemisphere_r; // Z length
If (hemisphere_t_5)
  hexahedron_ox = hemisphere_ox; hexahedron_oy = hemisphere_oy; hexahedron_oz = hemisphere_oz+hexahedron_c/2; // Origin: x, y, z
  hexahedron_rox = hemisphere_rox; hexahedron_roy = hemisphere_roy; hexahedron_roz = hemisphere_roz-hexahedron_c/2; // Local Rotation Origin: x, y, z
Else
  hexahedron_ox = hemisphere_ox; hexahedron_oy = hemisphere_oy; hexahedron_oz = hemisphere_oz-hexahedron_c/2; // Origin: x, y, z
  hexahedron_rox = hemisphere_rox; hexahedron_roy = hemisphere_roy; hexahedron_roz = hemisphere_roz+hexahedron_c/2; // Local Rotation Origin: x, y, z
EndIf
hexahedron_rax = hemisphere_rax; hexahedron_ray = hemisphere_ray; hexahedron_raz = hemisphere_raz; // Local Rotation Angle: x, y, z
// Parameters
hexahedron_t_1 = hemisphere_t_1; hexahedron_t_1_1 = 0; hexahedron_t_1_2 = 0; // Number of X nodes, progression, bump
hexahedron_t_2 = hemisphere_t_1; hexahedron_t_2_1 = 0; hexahedron_t_2_2 = 0; // Number of Y nodes, progression, bump
hexahedron_t_3 = hemisphere_t_3; hexahedron_t_3_1 = 0; hexahedron_t_3_2 = 0; // Number of Z nodes, progression, bump
hexahedron_t_4 = hemisphere_t_4; // Hex (1) or tet (0) mesh?
hexahedron_t_6 = 0; // Type of hex to tet splitting
hexahedron_t_7s = {}; // Inner Surfaces

Call hexahedron;

If (hemisphere_t_5)
  hemisphere_nzss += hexahedron_nzss[];
Else
  hemisphere_zss += hexahedron_zss[];
EndIf

hemisphere_vs += hexahedron_vs[];

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
  hemisphere_lc, hemisphere_lc, hemisphere_lc, hemisphere_lc,
  hemisphere_lc, hemisphere_lc, hemisphere_lc, hemisphere_lc,
  hemisphere_lc, hemisphere_lc, hemisphere_lc, hemisphere_lc,
  hemisphere_lc, hemisphere_lc, hemisphere_lc, hemisphere_lc,
  hemisphere_lc, hemisphere_lc, hemisphere_lc, hemisphere_lc
};
primitive_ox = hemisphere_ox; primitive_oy = hemisphere_oy; primitive_oz = hemisphere_oz; // Origin: x, y, z
primitive_rox = hemisphere_rox; primitive_roy = hemisphere_roy; primitive_roz = hemisphere_roz; // Local Rotation Origin: x, y, z
primitive_rax = hemisphere_rax; primitive_ray = hemisphere_ray; primitive_raz = hemisphere_raz; // Local Rotation Angle: x, y, z
// Parameters
primitive_t_4 = hemisphere_t_4; // Hex (1) or tet (0) mesh?
primitive_t_7s = {}; // Inner Surfaces
primitive_t_8s = {0, 0, 0, 0, 0, 0}; // Surfaces for changes
primitive_t_9s = {}; // Rotations
primitive_t_10s = {0, 0, 0, 0, 0, 0}; // Plane Surface?

// NX
If (hemisphere_t_5)
  primitive_xs = {
    -hemisphere_k*hemisphere_r, -hemisphere_r/Sqrt(2), -hemisphere_r/Sqrt(2), -hemisphere_k*hemisphere_r,
    -hemisphere_k*hemisphere_r, -hemisphere_r/Sqrt(3), -hemisphere_r/Sqrt(3), -hemisphere_k*hemisphere_r, 
    0, 0, 0, 0,
    0, 0, 0, 0,
    0, 0, 0, 0
  };
  primitive_ys = {
    hemisphere_k*hemisphere_r, hemisphere_r/Sqrt(2), -hemisphere_r/Sqrt(2), -hemisphere_k*hemisphere_r,
    hemisphere_k*hemisphere_r, hemisphere_r/Sqrt(3), -hemisphere_r/Sqrt(3), -hemisphere_k*hemisphere_r,
    0, 0, 0, 0,
    0, 0, 0, 0,
    0, 0, 0, 0
  };
  primitive_zs = {
    0, 0, 0, 0,
    hemisphere_k*hemisphere_r, hemisphere_r/Sqrt(3), hemisphere_r/Sqrt(3), hemisphere_k*hemisphere_r,
    0, 0, 0, 0,
    0, 0, 0, 0,
    0, 0, 0, 0
  };
Else
  primitive_xs = {
    -hemisphere_k*hemisphere_r, -hemisphere_r/Sqrt(3), -hemisphere_r/Sqrt(3), -hemisphere_k*hemisphere_r, 
    -hemisphere_k*hemisphere_r, -hemisphere_r/Sqrt(2), -hemisphere_r/Sqrt(2), -hemisphere_k*hemisphere_r,
    0, 0, 0, 0,
    0, 0, 0, 0,
    0, 0, 0, 0
  };
  primitive_ys = {
    hemisphere_k*hemisphere_r, hemisphere_r/Sqrt(3), -hemisphere_r/Sqrt(3), -hemisphere_k*hemisphere_r,
    hemisphere_k*hemisphere_r, hemisphere_r/Sqrt(2), -hemisphere_r/Sqrt(2), -hemisphere_k*hemisphere_r,
    0, 0, 0, 0,
    0, 0, 0, 0,
    0, 0, 0, 0
  };
  primitive_zs = {
    -hemisphere_k*hemisphere_r, -hemisphere_r/Sqrt(3), -hemisphere_r/Sqrt(3), -hemisphere_k*hemisphere_r,
    0, 0, 0, 0,
    0, 0, 0, 0,
    0, 0, 0, 0,
    0, 0, 0, 0
  };
EndIf
// Parameters
primitive_t_1 = hemisphere_t_2; 
If (hemisphere_t_2_1)
  primitive_t_1_1 = 1/hemisphere_t_2_1;
Else
  primitive_t_1_1 = hemisphere_t_2_1;
EndIf
primitive_t_1_2 = hemisphere_t_2_2; // Number of X nodes, progression, bump
primitive_t_2 = hemisphere_t_1; primitive_t_2_1 = hemisphere_t_1_1; primitive_t_2_2 = hemisphere_t_1_2; // Number of Y nodes, progression, bump
primitive_t_3 = hemisphere_t_3; primitive_t_3_1 = hemisphere_t_3_1; primitive_t_3_2 = hemisphere_t_3_2; // Number of Z nodes, progression, bump
primitive_t_5s = {0, 0, 0, 0, 0, 1, 1, 0, 0, 1, 1, 0}; // Type of lines: 0 - straight, 1 - circle, 2 - ellipse, 3 - Bezier, 4 - BSpline, 5+ - Spline
primitive_t_6 = 1; // Type of hex to tet splitting

Call primitive;

If (hemisphere_t_5)
  hemisphere_nzss += primitive_ss[4];
Else
  hemisphere_zss += primitive_ss[5];
EndIf

hemisphere_lss += primitive_ss[0];
hemisphere_vs += primitive_vs[];

// X
If (hemisphere_t_5)
  primitive_xs = {
    hemisphere_r/Sqrt(2), hemisphere_k*hemisphere_r, hemisphere_k*hemisphere_r, hemisphere_r/Sqrt(2), 
    hemisphere_r/Sqrt(3), hemisphere_k*hemisphere_r, hemisphere_k*hemisphere_r, hemisphere_r/Sqrt(3), 
    0, 0, 0, 0,
    0, 0, 0, 0,
    0, 0, 0, 0
  };
  primitive_ys = {
    hemisphere_r/Sqrt(2), hemisphere_k*hemisphere_r, -hemisphere_k*hemisphere_r, -hemisphere_r/Sqrt(2),
    hemisphere_r/Sqrt(3), hemisphere_k*hemisphere_r, -hemisphere_k*hemisphere_r, -hemisphere_r/Sqrt(3),
    0, 0, 0, 0,
    0, 0, 0, 0,
    0, 0, 0, 0,
    0, 0, 0, 0
  };
  primitive_zs = {
    0, 0, 0, 0,
    hemisphere_r/Sqrt(3), hemisphere_k*hemisphere_r, hemisphere_k*hemisphere_r, hemisphere_r/Sqrt(3),
    0, 0, 0, 0,
    0, 0, 0, 0,
    0, 0, 0, 0
  };
Else
  primitive_xs = {
    hemisphere_r/Sqrt(3), hemisphere_k*hemisphere_r, hemisphere_k*hemisphere_r, hemisphere_r/Sqrt(3),
    hemisphere_r/Sqrt(2), hemisphere_k*hemisphere_r, hemisphere_k*hemisphere_r, hemisphere_r/Sqrt(2),
    0, 0, 0, 0,
    0, 0, 0, 0,
    0, 0, 0, 0
  };
  primitive_ys = {
    hemisphere_r/Sqrt(3), hemisphere_k*hemisphere_r, -hemisphere_k*hemisphere_r, -hemisphere_r/Sqrt(3),
    hemisphere_r/Sqrt(2), hemisphere_k*hemisphere_r, -hemisphere_k*hemisphere_r, -hemisphere_r/Sqrt(2),
    0, 0, 0, 0,
    0, 0, 0, 0,
    0, 0, 0, 0,
    0, 0, 0, 0
  };
  primitive_zs = {
    -hemisphere_r/Sqrt(3), -hemisphere_k*hemisphere_r, -hemisphere_k*hemisphere_r, -hemisphere_r/Sqrt(3),
    0, 0, 0, 0,
    0, 0, 0, 0,
    0, 0, 0, 0,
    0, 0, 0, 0
  };
EndIf
primitive_t_1 = hemisphere_t_2; primitive_t_1_1 = hemisphere_t_2_1; primitive_t_1_2 = hemisphere_t_2_2; // Number of X nodes, progression, bump
primitive_t_2 = hemisphere_t_1; primitive_t_2_1 = hemisphere_t_1_1; primitive_t_2_2 = hemisphere_t_1_2; // Number of Y nodes, progression, bump
primitive_t_3 = hemisphere_t_3; primitive_t_3_1 = hemisphere_t_3_1; primitive_t_3_2 = hemisphere_t_3_2; // Number of Z nodes, progression, bump
primitive_t_5s = {0, 0, 0, 0, 1, 0, 0, 1, 1, 0, 0, 1}; // Type of lines: 0 - straight, 1 - circle, 2 - ellipse, 3 - Bezier, 4 - BSpline, 5+ - Spline
primitive_t_6 = 0; // Type of hex to tet splitting

Call primitive;

If (hemisphere_t_5)
  hemisphere_nzss += primitive_ss[4];
Else
  hemisphere_zss += primitive_ss[5];
EndIf

hemisphere_lss += primitive_ss[1];
hemisphere_vs += primitive_vs[];

// NY
If (hemisphere_t_5)
  primitive_xs = {
    hemisphere_k*hemisphere_r, -hemisphere_k*hemisphere_r, -hemisphere_r/Sqrt(2), hemisphere_r/Sqrt(2),
    hemisphere_k*hemisphere_r, -hemisphere_k*hemisphere_r, -hemisphere_r/Sqrt(3), hemisphere_r/Sqrt(3), 
    0, 0, 0, 0,
    0, 0, 0, 0,
    0, 0, 0, 0
  };
  primitive_ys = {
    -hemisphere_k*hemisphere_r, -hemisphere_k*hemisphere_r, -hemisphere_r/Sqrt(2), -hemisphere_r/Sqrt(2),
    -hemisphere_k*hemisphere_r, -hemisphere_k*hemisphere_r, -hemisphere_r/Sqrt(3), -hemisphere_r/Sqrt(3),
    0, 0, 0, 0,
    0, 0, 0, 0,
    0, 0, 0, 0
  };
  primitive_zs = {
    0, 0, 0, 0,
    hemisphere_k*hemisphere_r, hemisphere_k*hemisphere_r, hemisphere_r/Sqrt(3), hemisphere_r/Sqrt(3),
    0, 0, 0, 0,
    0, 0, 0, 0,
    0, 0, 0, 0
  };
Else
  primitive_xs = {
    hemisphere_k*hemisphere_r, -hemisphere_k*hemisphere_r, -hemisphere_r/Sqrt(3), hemisphere_r/Sqrt(3), 
    hemisphere_k*hemisphere_r, -hemisphere_k*hemisphere_r, -hemisphere_r/Sqrt(2), hemisphere_r/Sqrt(2),
    0, 0, 0, 0,
    0, 0, 0, 0,
    0, 0, 0, 0
  };
  primitive_ys = {
    -hemisphere_k*hemisphere_r, -hemisphere_k*hemisphere_r, -hemisphere_r/Sqrt(3), -hemisphere_r/Sqrt(3),
    -hemisphere_k*hemisphere_r, -hemisphere_k*hemisphere_r, -hemisphere_r/Sqrt(2), -hemisphere_r/Sqrt(2),
    0, 0, 0, 0,
    0, 0, 0, 0,
    0, 0, 0, 0
  };
  primitive_zs = {
    -hemisphere_k*hemisphere_r, -hemisphere_k*hemisphere_r, -hemisphere_r/Sqrt(3), -hemisphere_r/Sqrt(3),
    0, 0, 0, 0,
    0, 0, 0, 0,
    0, 0, 0, 0,
    0, 0, 0, 0
  };
EndIf
primitive_t_1 = hemisphere_t_1; primitive_t_1_1 = hemisphere_t_1_1; primitive_t_1_2 = hemisphere_t_1_2; // Number of X nodes, progression, bump
primitive_t_2 = hemisphere_t_2; 
If (hemisphere_t_2_1)
  primitive_t_2_1 = 1/hemisphere_t_2_1;
Else
  primitive_t_2_1 = hemisphere_t_2_1;
EndIf
primitive_t_2_2 = hemisphere_t_2_2; // Number of Y nodes, progression, bump
primitive_t_3 = hemisphere_t_3; primitive_t_3_1 = hemisphere_t_3_1; primitive_t_3_2 = hemisphere_t_3_2; // Number of Z nodes, progression, bump
primitive_t_5s = {0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 1, 1}; // Type of lines: 0 - straight, 1 - circle, 2 - ellipse, 3 - Bezier, 4 - BSpline, 5+ - Spline
primitive_t_6 = 3; // Type of hex to tet splitting

Call primitive;

If (hemisphere_t_5)
  hemisphere_nzss += primitive_ss[4];
Else
  hemisphere_zss += primitive_ss[5];
EndIf

hemisphere_lss += primitive_ss[2];
hemisphere_vs += primitive_vs[];

// Y
If (hemisphere_t_5)
  primitive_xs = {
    hemisphere_r/Sqrt(2), -hemisphere_r/Sqrt(2), -hemisphere_k*hemisphere_r, hemisphere_k*hemisphere_r,
    hemisphere_r/Sqrt(3), -hemisphere_r/Sqrt(3), -hemisphere_k*hemisphere_r, hemisphere_k*hemisphere_r,
    0, 0, 0, 0,
    0, 0, 0, 0,
    0, 0, 0, 0
  };
  primitive_ys = {
    hemisphere_r/Sqrt(2), hemisphere_r/Sqrt(2), hemisphere_k*hemisphere_r, hemisphere_k*hemisphere_r,
    hemisphere_r/Sqrt(3), hemisphere_r/Sqrt(3), hemisphere_k*hemisphere_r, hemisphere_k*hemisphere_r,
    0, 0, 0, 0,
    0, 0, 0, 0,
    0, 0, 0, 0
  };
  primitive_zs = {
    0, 0, 0, 0,
    hemisphere_r/Sqrt(3), hemisphere_r/Sqrt(3), hemisphere_k*hemisphere_r, hemisphere_k*hemisphere_r,
    0, 0, 0, 0,
    0, 0, 0, 0,
    0, 0, 0, 0
  };
Else
  primitive_xs = {
    hemisphere_r/Sqrt(3), -hemisphere_r/Sqrt(3), -hemisphere_k*hemisphere_r, hemisphere_k*hemisphere_r,
    hemisphere_r/Sqrt(2), -hemisphere_r/Sqrt(2), -hemisphere_k*hemisphere_r, hemisphere_k*hemisphere_r,
    0, 0, 0, 0,
    0, 0, 0, 0,
    0, 0, 0, 0
  };
  primitive_ys = {
    hemisphere_r/Sqrt(3), hemisphere_r/Sqrt(3), hemisphere_k*hemisphere_r, hemisphere_k*hemisphere_r,
    hemisphere_r/Sqrt(2), hemisphere_r/Sqrt(2), hemisphere_k*hemisphere_r, hemisphere_k*hemisphere_r,
    0, 0, 0, 0,
    0, 0, 0, 0,
    0, 0, 0, 0
  };
  primitive_zs = {
    -hemisphere_r/Sqrt(3), -hemisphere_r/Sqrt(3), -hemisphere_k*hemisphere_r, -hemisphere_k*hemisphere_r,
    0, 0, 0, 0,
    0, 0, 0, 0,
    0, 0, 0, 0,
    0, 0, 0, 0
  };
EndIf
primitive_t_1 = hemisphere_t_1; primitive_t_1_1 = hemisphere_t_1_1; primitive_t_1_2 = hemisphere_t_1_2; // Number of X nodes, progression, bump
primitive_t_2 = hemisphere_t_2; primitive_t_2_1 = hemisphere_t_2_1; primitive_t_2_2 = hemisphere_t_2_2; // Number of Y nodes, progression, bump
primitive_t_3 = hemisphere_t_3; primitive_t_3_1 = hemisphere_t_3_1; primitive_t_3_2 = hemisphere_t_3_2; // Number of Z nodes, progression, bump
primitive_t_5s = {1, 1, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0}; // Type of lines: 0 - straight, 1 - circle, 2 - ellipse, 3 - Bezier, 4 - BSpline, 5+ - Spline
primitive_t_6 = 0; // Type of hex to tet splitting

Call primitive;

If (hemisphere_t_5)
  hemisphere_nzss += primitive_ss[4];
Else
  hemisphere_zss += primitive_ss[5];
EndIf

hemisphere_lss += primitive_ss[3];
hemisphere_vs += primitive_vs[];

// Z or NZ
If (hemisphere_t_5) // Z
  primitive_xs = {
    hemisphere_k*hemisphere_r, -hemisphere_k*hemisphere_r, -hemisphere_k*hemisphere_r, hemisphere_k*hemisphere_r,
    hemisphere_r/Sqrt(3), -hemisphere_r/Sqrt(3), -hemisphere_r/Sqrt(3), hemisphere_r/Sqrt(3), 
    0, 0, 0, 0,
    0, 0, 0, 0,
    0, 0, 0, 0
  };
  primitive_ys = {
    hemisphere_k*hemisphere_r, hemisphere_k*hemisphere_r, -hemisphere_k*hemisphere_r, -hemisphere_k*hemisphere_r,
    hemisphere_r/Sqrt(3), hemisphere_r/Sqrt(3), -hemisphere_r/Sqrt(3), -hemisphere_r/Sqrt(3),
    0, 0, 0, 0,
    0, 0, 0, 0,
    0, 0, 0, 0
  };
  primitive_zs = {
    hemisphere_k*hemisphere_r, hemisphere_k*hemisphere_r, hemisphere_k*hemisphere_r,  hemisphere_k*hemisphere_r,
    hemisphere_r/Sqrt(3), hemisphere_r/Sqrt(3), hemisphere_r/Sqrt(3), hemisphere_r/Sqrt(3),
    0, 0, 0, 0,
    0, 0, 0, 0,
    0, 0, 0, 0
  };
  primitive_t_1 = hemisphere_t_1; primitive_t_1_1 = hemisphere_t_1_1; primitive_t_1_2 = hemisphere_t_1_2; // Number of X nodes, progression, bump
  primitive_t_2 = hemisphere_t_1; primitive_t_2_1 = hemisphere_t_1_1; primitive_t_2_2 = hemisphere_t_1_2; // Number of Y nodes, progression, bump
  primitive_t_3 = hemisphere_t_2; primitive_t_3_1 = hemisphere_t_2_1; primitive_t_3_2 = hemisphere_t_2_2; // Number of Z nodes, progression, bump
  primitive_t_5s = {0, 1, 1, 0, 0, 0, 1, 1, 0, 0, 0, 0}; // Type of lines: 0 - straight, 1 - circle, 2 - ellipse, 3 - Bezier, 4 - BSpline, 5+ - Spline
  primitive_t_6 = 2; // Type of hex to tet splitting

  Call primitive;


  hemisphere_lss += primitive_ss[5];
  hemisphere_vs += primitive_vs[];
Else // NZ
  primitive_xs = {
    hemisphere_r/Sqrt(3), -hemisphere_r/Sqrt(3), -hemisphere_r/Sqrt(3), hemisphere_r/Sqrt(3), 
    hemisphere_k*hemisphere_r, -hemisphere_k*hemisphere_r, -hemisphere_k*hemisphere_r, hemisphere_k*hemisphere_r,
    0, 0, 0, 0,
    0, 0, 0, 0,
    0, 0, 0, 0
  };
  primitive_ys = {
    hemisphere_r/Sqrt(3), hemisphere_r/Sqrt(3), -hemisphere_r/Sqrt(3), -hemisphere_r/Sqrt(3),
    hemisphere_k*hemisphere_r, hemisphere_k*hemisphere_r, -hemisphere_k*hemisphere_r, -hemisphere_k*hemisphere_r,
    0, 0, 0, 0,
    0, 0, 0, 0,
    0, 0, 0, 0
  };
  primitive_zs = {
    -hemisphere_r/Sqrt(3), -hemisphere_r/Sqrt(3), -hemisphere_r/Sqrt(3), -hemisphere_r/Sqrt(3),
    -hemisphere_k*hemisphere_r, -hemisphere_k*hemisphere_r, -hemisphere_k*hemisphere_r, -hemisphere_k*hemisphere_r,
    0, 0, 0, 0,
    0, 0, 0, 0,
    0, 0, 0, 0
  };
  primitive_t_1 = hemisphere_t_1; primitive_t_1_1 = hemisphere_t_1_1; primitive_t_1_2 = hemisphere_t_1_2; // Number of X nodes, progression, bump
  primitive_t_2 = hemisphere_t_1; primitive_t_2_1 = hemisphere_t_1_1; primitive_t_2_2 = hemisphere_t_1_2; // Number of Y nodes, progression, bump
  primitive_t_3 = hemisphere_t_2;
  If (hemisphere_t_2_1)
    primitive_t_3_1 = 1/hemisphere_t_2_1;
  Else
    primitive_t_3_1 = hemisphere_t_2_1;
  EndIf
  primitive_t_3_2 = hemisphere_t_2_2; // Number of Z nodes, progression, bump
  primitive_t_5s = {1, 0, 0, 1, 1, 1, 0, 0, 0, 0, 0, 0}; // Type of lines: 0 - straight, 1 - circle, 2 - ellipse, 3 - Bezier, 4 - BSpline, 5+ - Spline
  primitive_t_6 = 0; // Type of hex to tet splitting

  Call primitive;

  hemisphere_lss += primitive_ss[4];
  hemisphere_vs += primitive_vs[];
EndIf

Return

