SetFactory("OpenCASCADE");

Include "macro_primitive.geo";

/*Geometry.AutoCoherence = 0;*/
//Mesh.CharacteristicLengthFromCurvature = 1;
//Mesh.CharacteristicLengthFromPoints = 0;
//Mesh.CharacteristicLengthMin = 0.1;
//Mesh.CharacteristicLengthMax = 0.5;


// X-Y-NZ point, NX-Y-NZ, NX-NY-NZ, X-NY-NZ, (X - X axis, NX - negative X axis, etc)
// X-Y-Z, NX-Y-Z, NX-NY-Z, X-NY-Z,
// X1 line circle center, X2, X3, X4, (Line numeration by right hand rule from line contains X-Y-NZ point)
// Y1, Y2, Y3, Y4,
// Z1, Z2, Z3, Z4,
// X1 line ellipse point, X2, X3, X4,
// Y1, Y2, Y3, Y4,
// Z1, Z2, Z3, Z4
primitive_lcs = {
1, 1, 1, 1,
1, 1, 1, 1,
1, 1, 1, 1,
1, 1, 1, 1,
1, 1, 1, 1,
1, 1, 1, 1,
1, 1, 1, 1,
1, 1, 1, 1
};
primitive_xs = {
0.25, -0.25, -0.25, 0.25, 
0.25, -0.25, -0.25, 0.25, 
0, 0, 0, 0,
0, 0, 0, 0,
0, 0, 0, 0,
0, 0, 0, 0,
0, 0, 0, 0,
0, 0, 0, 0
};
primitive_ys = {
0.25, 0.25, -0.25, -0.25,
0.25, 0.25, -0.25, -0.25,
0, 0, 0, 0,
0, 0, 0, 0,
0, 0, 0, 0,
0, 0, 0, 0,
0, 0, 0, 0,
0, 0, 0, 0
};
primitive_zs = {
-4, -4, -4, -4,
4, 4, 4, 4,
0, 0, 0, 0,
0, 0, 0, 0,
0, 0, 0, 0,
0, 0, 0, 0,
0, 0, 0, 0,
0, 0, 0, 0
};
primitive_ox = 0; primitive_oy = 0; primitive_oz = 0; // Origin: x, y, z
primitive_rox = 0; primitive_roy = 0; primitive_roz = 0; // Local Rotation Origin: x, y, z
primitive_rax = 0; primitive_ray = 0; primitive_raz = 0; // Local Rotation Angle: x, y, z
// Parameters
primitive_t_1 = 0; primitive_t_1_1 = 0; primitive_t_1_2 = 0; // Number of X nodes, progression, bump
primitive_t_2 = 0; primitive_t_2_1 = 0; primitive_t_2_2 = 0; // Number of Y nodes, progression, bump
primitive_t_3 = 0; primitive_t_3_1 = 0; primitive_t_3_2 = 0; // Number of Z nodes, progression, bump
primitive_t_4 = 0; // Hex (1) or tet (0) mesh?
primitive_t_5s = {0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0}; // Type of lines: 0 - straight, 1 - circle, 2 - ellipse, 3 - Bezier, 4 - BSpline, 5+ - Spline
primitive_t_6 = 0; // Type of hex to tet splitting
primitive_t_7s = {}; // Inner Surfaces
primitive_t_8s = {0, 0, 0, 0, 0, 0}; // Surfaces for changes
primitive_t_9s = {}; // Rotations
primitive_t_10s = {0, 0, 0, 0, 0, 0}; // Plane Surface?

Call primitive;
vvs[] = primitive_vs[];

primitive_xs = {
1, -1, -1, 1, 
1, -1, -1, 1, 
0, 0, 0, 0,
0, 0, 0, 0,
0, 0, 0, 0,
0, 0, 0, 0,
0, 0, 0, 0,
0, 0, 0, 0
};
primitive_ys = {
1, 1, -1, -1,
1, 1, -1, -1,
0, 0, 0, 0,
0, 0, 0, 0,
0, 0, 0, 0,
0, 0, 0, 0,
0, 0, 0, 0,
0, 0, 0, 0
};
primitive_zs = {
-5, -5, -5, -5,
5, 5, 5, 5,
0, 0, 0, -0.5,
-1, 0, 0, 0,
0, 0, 0, 0,
0, 0, 0, 0,
0, 0, 0, 0,
0, 0, 0, 0
};

Call primitive;
out1[] = BooleanFragments{ Volume{primitive_vs[], vvs[]}; Delete; } {};
vs[] += out1[];

primitive_ox = 5; primitive_oy = 0; primitive_oz = 0; // Origin: x, y, z
Call primitive;
vs[] += primitive_vs[];

primitive_ox = 5; primitive_oy = 5; primitive_oz = 0; // Origin: x, y, z
Call primitive;
vs[] += primitive_vs[];

primitive_ox = 0; primitive_oy = 5; primitive_oz = 0; // Origin: x, y, z
Call primitive;
vs[] += primitive_vs[];

primitive_xs = {
5, -5, -5, 5, 
5, -5, -5, 5, 
0, 0, 0, 0,
0, 0, 0, 0,
0, 0, 0, 0,
0, 0, 0, 0,
0, 0, 0, 0,
0, 0, 0, 0
};
primitive_ys = {
5, 5, -5, -5,
5, 5, -5, -5,
0, 0, 0, 0,
0, 0, 0, 0,
0, 0, 0, 0,
0, 0, 0, 0,
0, 0, 0, 0,
0, 0, 0, 0
};
primitive_zs = {
-1, -1, -1, -1,
3, 1, 1, 1,
0, 0, 0, -0.5,
-1, 0, 0, 0,
0, 0, 0, 0,
0, 0, 0, 0,
0, 0, 0, 0,
0, 0, 0, 0
};
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

primitive_t_5s = {3, 0, 0, 1, 1, 0, 0, 0, 0, 1, 0, 0}; // Type of lines: 0 - straight, 1 - circle, 2 - ellipse, 3 - Bezier, 4 - BSpline, 5+ - Spline

primitive_ox = 0; primitive_oy = 0; primitive_oz = 0; // Origin: x, y, z
primitive_rax = 0; primitive_ray = Pi/10; primitive_raz = 0; // Local Rotation Angle: x, y, z
Call primitive;






//BooleanFragments{ Surface{primitive_ss[0]}; Delete; }{ Surface{ss[1]}; Delete;}
//BooleanUnion{ Surface{primitive_ss[0]}; Delete; }{ Surface{ss[1]}; Delete; }
//BooleanUnion{ Volume{primitive_vs[]}; Delete; }{ Volume{vs[]}; Delete; }
out[] = BooleanFragments{ Volume{primitive_vs[], vs[]}; Delete; } {};
//out[] = BooleanFragments{ Volume{primitive_vs[]}; Volume{vs[]}; Delete; } {};
//out[] = BooleanFragments{ Surface{primitive_ss[0]}; Volume{vs[]}; Delete; } {};
//BooleanFragments{ Surface{primitive_ss[]}; Delete; }{ Volume{vs[]}; Delete; }
Physical Volume ("Sill") = {out[0]};

cvs[] = {};
mvs[] = {};
For i In {1 : #out[]-1}
  If (i != 5 && i != 6 && i != 7)
      cvs[] += out[i];
  Else
      mvs[] += out[i];
  EndIf
EndFor
Physical Volume ("Container") = {cvs[]};
Physical Volume ("Matrix") = {mvs[]};

// For i In {0 : #out[]-1}
  // Physical Volume (Sprintf("V%g", i)) = {out[i]};
// EndFor



primitive_xs = {
10, -10, -10, 10, 
10, -10, -10, 10, 
0, 0, 0, 0,
0, 0, 0, 0,
0, 0, 0, 0,
0, 0, 0, 0,
0, 0, 0, 0,
0, 0, 0, 0
};
primitive_ys = {
10, 10, -10, -10,
10, 10, -10, -10,
0, 0, 0, 0,
0, 0, 0, 0,
0, 0, 0, 0,
0, 0, 0, 0,
0, 0, 0, 0,
0, 0, 0, 0
};
primitive_zs = {
-10, -10, -10, -10,
10, 10, 10, 10,
0, 0, 0, -0.5,
-1, 0, 0, 0,
0, 0, 0, 0,
0, 0, 0, 0,
0, 0, 0, 0,
0, 0, 0, 0
};
primitive_t_5s = {0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0}; // Type of lines: 0 - straight, 1 - circle, 2 - ellipse, 3 - Bezier, 4 - BSpline, 5+ - Spline

primitive_rax = 0; primitive_ray = 0; primitive_raz = 0; // Local Rotation Angle: x, y, z

Call primitive;

out2[] = BooleanFragments{ Volume{primitive_vs[], out[]}; Delete; } {};
Physical Volume ("Rock") = {out2[#out2[]-1]};
ss[] = Unique(Abs(Boundary{ Volume{out2[#out2[]-1]}; }));
Physical Surface ("NX") = {ss[#ss[]-6]};
Physical Surface ("X") = {ss[#ss[]-1]};
Physical Surface ("NY") = {ss[#ss[]-4]};
Physical Surface ("Y") = {ss[#ss[]-3]};
Physical Surface ("NZ") = {ss[#ss[]-5]};
Physical Surface ("Z") = {ss[#ss[]-2]};
// Physical Surface ("B") = {primitive_ss[]};
// Physical Volume ("V") = {primitive_vs[]};

//Coherence;
