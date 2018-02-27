Include "macro_primitive.geo";

Macro sphereshell

sphereshell_nzss = {};
sphereshell_zss = {};
sphereshell_iss = {};
sphereshell_lss = {};
sphereshell_vs = {};

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
  sphereshell_lc, sphereshell_lc, sphereshell_lc, sphereshell_lc,
  sphereshell_lc, sphereshell_lc, sphereshell_lc, sphereshell_lc,
  sphereshell_lc, sphereshell_lc, sphereshell_lc, sphereshell_lc,
  sphereshell_lc, sphereshell_lc, sphereshell_lc, sphereshell_lc,
  sphereshell_lc, sphereshell_lc, sphereshell_lc, sphereshell_lc
};
primitive_ox = sphereshell_ox; primitive_oy = sphereshell_oy; primitive_oz = sphereshell_oz; // Origin: x, y, z
primitive_rox = sphereshell_rox; primitive_roy = sphereshell_roy; primitive_roz = sphereshell_roz; // Local Rotation Origin: x, y, z
primitive_rax = sphereshell_rax; primitive_ray = sphereshell_ray; primitive_raz = sphereshell_raz; // Local Rotation Angle: x, y, z
// Parameters
primitive_t_3 = sphereshell_t_3; primitive_t_3_1 = sphereshell_t_3_1; primitive_t_3_2 = sphereshell_t_3_2; // Number of Z nodes, progression, bump
primitive_t_4 = sphereshell_t_4; // Hex (1) or tet (0) mesh?
primitive_t_7s = {}; // Inner Surfaces
primitive_t_8s = {0, 0, 0, 0, 0, 0}; // Surfaces for changes
primitive_t_9s = {}; // Rotations
primitive_t_10s = {0, 0, 0, 0, 0, 0}; // Plane Surface?

// NX
If (sphereshell_t_5)
  primitive_xs = {
    -sphereshell_r1/Sqrt(2), -sphereshell_r2/Sqrt(2), -sphereshell_r2/Sqrt(2), -sphereshell_r1/Sqrt(2),
    -sphereshell_r1/Sqrt(3), -sphereshell_r2/Sqrt(3), -sphereshell_r2/Sqrt(3), -sphereshell_r1/Sqrt(3),
    0, 0, 0, 0,
    0, 0, 0, 0,
    0, 0, 0, 0
  };
  primitive_ys = {
    sphereshell_r1/Sqrt(2), sphereshell_r2/Sqrt(2), -sphereshell_r2/Sqrt(2), -sphereshell_r1/Sqrt(2),
    sphereshell_r1/Sqrt(3), sphereshell_r2/Sqrt(3), -sphereshell_r2/Sqrt(3), -sphereshell_r1/Sqrt(3),
    0, 0, 0, 0,
    0, 0, 0, 0,
    0, 0, 0, 0
  };
  primitive_zs = {
    0, 0, 0, 0,
    sphereshell_r1/Sqrt(3), sphereshell_r2/Sqrt(3), sphereshell_r2/Sqrt(3), sphereshell_r1/Sqrt(3),
    0, 0, 0, 0,
    0, 0, 0, 0,
    0, 0, 0, 0
  };
Else
  primitive_xs = {
    -sphereshell_r1/Sqrt(3), -sphereshell_r2/Sqrt(3), -sphereshell_r2/Sqrt(3), -sphereshell_r1/Sqrt(3),
    -sphereshell_r1/Sqrt(2), -sphereshell_r2/Sqrt(2), -sphereshell_r2/Sqrt(2), -sphereshell_r1/Sqrt(2),
    0, 0, 0, 0,
    0, 0, 0, 0,
    0, 0, 0, 0
  };
  primitive_ys = {
    sphereshell_r1/Sqrt(3), sphereshell_r2/Sqrt(3), -sphereshell_r2/Sqrt(3), -sphereshell_r1/Sqrt(3),
    sphereshell_r1/Sqrt(2), sphereshell_r2/Sqrt(2), -sphereshell_r2/Sqrt(2), -sphereshell_r1/Sqrt(2),
    0, 0, 0, 0,
    0, 0, 0, 0,
    0, 0, 0, 0
  };
  primitive_zs = {
    -sphereshell_r1/Sqrt(3), -sphereshell_r2/Sqrt(3), -sphereshell_r2/Sqrt(3), -sphereshell_r1/Sqrt(3),
    0, 0, 0, 0,
    0, 0, 0, 0,
    0, 0, 0, 0,
    0, 0, 0, 0
  };
EndIf
// Parameters
primitive_t_1 = sphereshell_t_2; 
If (sphereshell_t_2_1)
  primitive_t_1_1 = 1/sphereshell_t_2_1;
Else
  primitive_t_1_1 = sphereshell_t_2_1;
EndIf
primitive_t_1_2 = sphereshell_t_2_2; // Number of X nodes, progression, bump
primitive_t_2 = sphereshell_t_1; primitive_t_2_1 = sphereshell_t_1_1; primitive_t_2_2 = sphereshell_t_1_2; // Number of Y nodes, progression, bump
primitive_t_5s = {0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1}; // Type of lines: 0 - straight, 1 - circle, 2 - ellipse, 3 - Bezier, 4 - BSpline, 5+ - Spline
primitive_t_6 = 1; // Type of hex to tet splitting

Call primitive;

If (sphereshell_t_5)
  sphereshell_nzss += primitive_ss[4];
Else
  sphereshell_zss += primitive_ss[5];
EndIf

sphereshell_iss += primitive_ss[1];
sphereshell_lss += primitive_ss[0];
sphereshell_vs += primitive_vs[];

// X
If (sphereshell_t_5)
primitive_xs = {
  sphereshell_r2/Sqrt(2), sphereshell_r1/Sqrt(2), sphereshell_r1/Sqrt(2), sphereshell_r2/Sqrt(2),
  sphereshell_r2/Sqrt(3), sphereshell_r1/Sqrt(3), sphereshell_r1/Sqrt(3), sphereshell_r2/Sqrt(3),
  0, 0, 0, 0,
  0, 0, 0, 0,
  0, 0, 0, 0
};
primitive_ys = {
  sphereshell_r2/Sqrt(2), sphereshell_r1/Sqrt(2), -sphereshell_r1/Sqrt(2), -sphereshell_r2/Sqrt(2),
  sphereshell_r2/Sqrt(3), sphereshell_r1/Sqrt(3), -sphereshell_r1/Sqrt(3), -sphereshell_r2/Sqrt(3),
  0, 0, 0, 0,
  0, 0, 0, 0,
  0, 0, 0, 0
};
primitive_zs = {
  0, 0, 0, 0,
  sphereshell_r2/Sqrt(3), sphereshell_r1/Sqrt(3), sphereshell_r1/Sqrt(3), sphereshell_r2/Sqrt(3),
  0, 0, 0, 0,
  0, 0, 0, 0,
  0, 0, 0, 0
};
Else
primitive_xs = {
  sphereshell_r2/Sqrt(3), sphereshell_r1/Sqrt(3), sphereshell_r1/Sqrt(3), sphereshell_r2/Sqrt(3),
  sphereshell_r2/Sqrt(2), sphereshell_r1/Sqrt(2), sphereshell_r1/Sqrt(2), sphereshell_r2/Sqrt(2),
  0, 0, 0, 0,
  0, 0, 0, 0,
  0, 0, 0, 0
};
primitive_ys = {
  sphereshell_r2/Sqrt(3), sphereshell_r1/Sqrt(3), -sphereshell_r1/Sqrt(3), -sphereshell_r2/Sqrt(3),
  sphereshell_r2/Sqrt(2), sphereshell_r1/Sqrt(2), -sphereshell_r1/Sqrt(2), -sphereshell_r2/Sqrt(2),
  0, 0, 0, 0,
  0, 0, 0, 0,
  0, 0, 0, 0
};
primitive_zs = {
  -sphereshell_r2/Sqrt(3), -sphereshell_r1/Sqrt(3), -sphereshell_r1/Sqrt(3), -sphereshell_r2/Sqrt(3),
  0, 0, 0, 0,
  0, 0, 0, 0,
  0, 0, 0, 0,
  0, 0, 0, 0
};
EndIf
primitive_t_1 = sphereshell_t_2; primitive_t_1_1 = sphereshell_t_2_1; primitive_t_1_2 = sphereshell_t_2_2; // Number of X nodes, progression, bump
primitive_t_2 = sphereshell_t_1; primitive_t_2_1 = sphereshell_t_1_1; primitive_t_2_2 = sphereshell_t_1_2; // Number of Y nodes, progression, bump
primitive_t_5s = {0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1}; // Type of lines: 0 - straight, 1 - circle, 2 - ellipse, 3 - Bezier, 4 - BSpline, 5+ - Spline
primitive_t_6 = 0; // Type of hex to tet splitting

Call primitive;

If (sphereshell_t_5)
  sphereshell_nzss += primitive_ss[4];
Else
  sphereshell_zss += primitive_ss[5];
EndIf

sphereshell_iss += primitive_ss[0];
sphereshell_lss += primitive_ss[1];
sphereshell_vs += primitive_vs[];

// NY
If (sphereshell_t_5)
  primitive_xs = {
    sphereshell_r1/Sqrt(2), -sphereshell_r1/Sqrt(2), -sphereshell_r2/Sqrt(2), sphereshell_r2/Sqrt(2),
    sphereshell_r1/Sqrt(3), -sphereshell_r1/Sqrt(3), -sphereshell_r2/Sqrt(3), sphereshell_r2/Sqrt(3),
    0, 0, 0, 0,
    0, 0, 0, 0,
    0, 0, 0, 0
  };
  primitive_ys = {
    -sphereshell_r1/Sqrt(2), -sphereshell_r1/Sqrt(2), -sphereshell_r2/Sqrt(2), -sphereshell_r2/Sqrt(2),
    -sphereshell_r1/Sqrt(3), -sphereshell_r1/Sqrt(3), -sphereshell_r2/Sqrt(3), -sphereshell_r2/Sqrt(3),
    0, 0, 0, 0,
    0, 0, 0, 0,
    0, 0, 0, 0
  };
  primitive_zs = {
    0, 0, 0, 0,
    sphereshell_r1/Sqrt(3), sphereshell_r1/Sqrt(3), sphereshell_r2/Sqrt(3), sphereshell_r2/Sqrt(3),
    0, 0, 0, 0,
    0, 0, 0, 0,
    0, 0, 0, 0
  };
Else
  primitive_xs = {
    sphereshell_r1/Sqrt(3), -sphereshell_r1/Sqrt(3), -sphereshell_r2/Sqrt(3), sphereshell_r2/Sqrt(3),
    sphereshell_r1/Sqrt(2), -sphereshell_r1/Sqrt(2), -sphereshell_r2/Sqrt(2), sphereshell_r2/Sqrt(2),
    0, 0, 0, 0,
    0, 0, 0, 0,
    0, 0, 0, 0
  };
  primitive_ys = {
    -sphereshell_r1/Sqrt(3), -sphereshell_r1/Sqrt(3), -sphereshell_r2/Sqrt(3), -sphereshell_r2/Sqrt(3),
    -sphereshell_r1/Sqrt(2), -sphereshell_r1/Sqrt(2), -sphereshell_r2/Sqrt(2), -sphereshell_r2/Sqrt(2),
    0, 0, 0, 0,
    0, 0, 0, 0,
    0, 0, 0, 0
  };
  primitive_zs = {
    -sphereshell_r1/Sqrt(3), -sphereshell_r1/Sqrt(3), -sphereshell_r2/Sqrt(3), -sphereshell_r2/Sqrt(3),
    0, 0, 0, 0,
    0, 0, 0, 0,
    0, 0, 0, 0,
    0, 0, 0, 0
  };
EndIf
primitive_t_1 = sphereshell_t_1; primitive_t_1_1 = sphereshell_t_1_1; primitive_t_1_2 = sphereshell_t_1_2; // Number of X nodes, progression, bump
primitive_t_2 = sphereshell_t_2; primitive_t_2_1 = sphereshell_t_2_1; primitive_t_2_2 = sphereshell_t_2_2; // Number of Y nodes, progression, bump
primitive_t_5s = {1, 1, 1, 1, 0, 0, 0, 0, 1, 1, 1, 1}; // Type of lines: 0 - straight, 1 - circle, 2 - ellipse, 3 - Bezier, 4 - BSpline, 5+ - Spline
primitive_t_6 = 3; // Type of hex to tet splitting

Call primitive;

If (sphereshell_t_5)
  sphereshell_nzss += primitive_ss[4];
Else
  sphereshell_zss += primitive_ss[5];
EndIf

sphereshell_iss += primitive_ss[3];
sphereshell_lss += primitive_ss[2];
sphereshell_vs += primitive_vs[];

// Y
If (sphereshell_t_5)
  primitive_xs = {
    sphereshell_r2/Sqrt(2), -sphereshell_r2/Sqrt(2), -sphereshell_r1/Sqrt(2), sphereshell_r1/Sqrt(2),
    sphereshell_r2/Sqrt(3), -sphereshell_r2/Sqrt(3), -sphereshell_r1/Sqrt(3), sphereshell_r1/Sqrt(3),
    0, 0, 0, 0,
    0, 0, 0, 0,
    0, 0, 0, 0
  };
  primitive_ys = {
    sphereshell_r2/Sqrt(2), sphereshell_r2/Sqrt(2), sphereshell_r1/Sqrt(2), sphereshell_r1/Sqrt(2),
    sphereshell_r2/Sqrt(3), sphereshell_r2/Sqrt(3), sphereshell_r1/Sqrt(3), sphereshell_r1/Sqrt(3),
    0, 0, 0, 0,
    0, 0, 0, 0,
    0, 0, 0, 0
  };
  primitive_zs = {
    0, 0, 0, 0,
    sphereshell_r2/Sqrt(3), sphereshell_r2/Sqrt(3), sphereshell_r1/Sqrt(3), sphereshell_r1/Sqrt(3),
    0, 0, 0, 0,
    0, 0, 0, 0,
    0, 0, 0, 0
  };
Else
  primitive_xs = {
    sphereshell_r2/Sqrt(3), -sphereshell_r2/Sqrt(3), -sphereshell_r1/Sqrt(3), sphereshell_r1/Sqrt(3),
    sphereshell_r2/Sqrt(2), -sphereshell_r2/Sqrt(2), -sphereshell_r1/Sqrt(2), sphereshell_r1/Sqrt(2),
    0, 0, 0, 0,
    0, 0, 0, 0,
    0, 0, 0, 0
  };
  primitive_ys = {
    sphereshell_r2/Sqrt(3), sphereshell_r2/Sqrt(3), sphereshell_r1/Sqrt(3), sphereshell_r1/Sqrt(3),
    sphereshell_r2/Sqrt(2), sphereshell_r2/Sqrt(2), sphereshell_r1/Sqrt(2), sphereshell_r1/Sqrt(2),
    0, 0, 0, 0,
    0, 0, 0, 0,
    0, 0, 0, 0
  };
  primitive_zs = {
    -sphereshell_r2/Sqrt(3), -sphereshell_r2/Sqrt(3), -sphereshell_r1/Sqrt(3), -sphereshell_r1/Sqrt(3),
    0, 0, 0, 0,
    0, 0, 0, 0,
    0, 0, 0, 0,
    0, 0, 0, 0
  };
EndIf
primitive_t_1 = sphereshell_t_1; primitive_t_1_1 = sphereshell_t_1_1; primitive_t_1_2 = sphereshell_t_1_2; // Number of X nodes, progression, bump
primitive_t_2 = sphereshell_t_2; primitive_t_2_1 = sphereshell_t_2_1; primitive_t_2_2 = sphereshell_t_2_2; // Number of Y nodes, progression, bump
primitive_t_5s = {1, 1, 1, 1, 0, 0, 0, 0, 1, 1, 1, 1}; // Type of lines: 0 - straight, 1 - circle, 2 - ellipse, 3 - Bezier, 4 - BSpline, 5+ - Spline
primitive_t_6 = 0; // Type of hex to tet splitting

Call primitive;

If (sphereshell_t_5)
  sphereshell_nzss += primitive_ss[4];
Else
  sphereshell_zss += primitive_ss[5];
EndIf

sphereshell_iss += primitive_ss[2];
sphereshell_lss += primitive_ss[3];
sphereshell_vs += primitive_vs[];

// Z or NZ
If (sphereshell_t_5) // Z
  primitive_xs = {
    sphereshell_r1/Sqrt(3), -sphereshell_r1/Sqrt(3), -sphereshell_r1/Sqrt(3), sphereshell_r1/Sqrt(3),
    sphereshell_r2/Sqrt(3), -sphereshell_r2/Sqrt(3), -sphereshell_r2/Sqrt(3), sphereshell_r2/Sqrt(3),
    0, 0, 0, 0,
    0, 0, 0, 0,
    0, 0, 0, 0
  };
  primitive_ys = {
    sphereshell_r1/Sqrt(3), sphereshell_r1/Sqrt(3), -sphereshell_r1/Sqrt(3), -sphereshell_r1/Sqrt(3),
    sphereshell_r2/Sqrt(3), sphereshell_r2/Sqrt(3), -sphereshell_r2/Sqrt(3), -sphereshell_r2/Sqrt(3),
    0, 0, 0, 0,
    0, 0, 0, 0,
    0, 0, 0, 0
  };
  primitive_zs = {
    sphereshell_r1/Sqrt(3), sphereshell_r1/Sqrt(3), sphereshell_r1/Sqrt(3), sphereshell_r1/Sqrt(3),
    sphereshell_r2/Sqrt(3), sphereshell_r2/Sqrt(3), sphereshell_r2/Sqrt(3), sphereshell_r2/Sqrt(3),
    0, 0, 0, 0,
    0, 0, 0, 0,
    0, 0, 0, 0
  };
  primitive_t_1 = sphereshell_t_1; primitive_t_1_1 = sphereshell_t_1_1; primitive_t_1_2 = sphereshell_t_1_2; // Number of X nodes, progression, bump
  primitive_t_2 = sphereshell_t_1; primitive_t_2_1 = sphereshell_t_1_1; primitive_t_2_2 = sphereshell_t_1_2; // Number of Y nodes, progression, bump
  primitive_t_3 = sphereshell_t_2; primitive_t_3_1 = sphereshell_t_2_1; primitive_t_3_2 = sphereshell_t_2_2; // Number of Z nodes, progression, bump
  primitive_t_5s = {1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0}; // Type of lines: 0 - straight, 1 - circle, 2 - ellipse, 3 - Bezier, 4 - BSpline, 5+ - Spline
  primitive_t_6 = 2; // Type of hex to tet splitting

  Call primitive;

  sphereshell_iss += primitive_ss[4];
  sphereshell_lss += primitive_ss[5];
  sphereshell_vs += primitive_vs[];
Else // NZ
  primitive_xs = {
    sphereshell_r2/Sqrt(3), -sphereshell_r2/Sqrt(3), -sphereshell_r2/Sqrt(3), sphereshell_r2/Sqrt(3),
    sphereshell_r1/Sqrt(3), -sphereshell_r1/Sqrt(3), -sphereshell_r1/Sqrt(3), sphereshell_r1/Sqrt(3),
    0, 0, 0, 0,
    0, 0, 0, 0,
    0, 0, 0, 0
  };
  primitive_ys = {
    sphereshell_r2/Sqrt(3), sphereshell_r2/Sqrt(3), -sphereshell_r2/Sqrt(3), -sphereshell_r2/Sqrt(3),
    sphereshell_r1/Sqrt(3), sphereshell_r1/Sqrt(3), -sphereshell_r1/Sqrt(3), -sphereshell_r1/Sqrt(3),
    0, 0, 0, 0,
    0, 0, 0, 0,
    0, 0, 0, 0
  };
  primitive_zs = {
    -sphereshell_r2/Sqrt(3), -sphereshell_r2/Sqrt(3), -sphereshell_r2/Sqrt(3), -sphereshell_r2/Sqrt(3),
    -sphereshell_r1/Sqrt(3), -sphereshell_r1/Sqrt(3), -sphereshell_r1/Sqrt(3), -sphereshell_r1/Sqrt(3),
    0, 0, 0, 0,
    0, 0, 0, 0,
    0, 0, 0, 0
  };
  primitive_t_1 = sphereshell_t_1; primitive_t_1_1 = sphereshell_t_1_1; primitive_t_1_2 = sphereshell_t_1_2; // Number of X nodes, progression, bump
  primitive_t_2 = sphereshell_t_1; primitive_t_2_1 = sphereshell_t_1_1; primitive_t_2_2 = sphereshell_t_1_2; // Number of Y nodes, progression, bump
  primitive_t_3 = sphereshell_t_2;
  If (sphereshell_t_2_1)
    primitive_t_3_1 = 1/sphereshell_t_2_1;
  Else
    primitive_t_3_1 = sphereshell_t_2_1;
  EndIf
  primitive_t_3_2 = sphereshell_t_2_2; // Number of Z nodes, progression, bump
  primitive_t_5s = {1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0}; // Type of lines: 0 - straight, 1 - circle, 2 - ellipse, 3 - Bezier, 4 - BSpline, 5+ - Spline
  primitive_t_6 = 0; // Type of hex to tet splitting

  Call primitive;

  sphereshell_iss += primitive_ss[5];
  sphereshell_lss += primitive_ss[4];
  sphereshell_vs += primitive_vs[];
EndIf


Return

