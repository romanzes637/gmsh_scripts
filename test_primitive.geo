SetFactory("OpenCASCADE");

Include "macro_primitive.geo";

/*Geometry.AutoCoherence = 0;*/

// X-Y-NZ point, NX-Y-NZ, NX-NY-NZ, X-NY-NZ, (X - X axis, NX - negative X axis, etc)
// X-Y-Z, NX-Y-Z, NX-NY-Z, X-NY-Z,
// X1 line circle center, X2, X3, X4, (Line numeration by right hand rule from line contains X-Y-NZ point)
// Y1, Y2, Y3, Y4,
// Z1, Z2, Z3, Z4,
// X1 line ellipse point, X2, X3, X4,
// Y1, Y2, Y3, Y4,
// Z1, Z2, Z3, Z4
primitive_lcs = {
0.1, 0.1, 0.1, 0.1,
0.1, 0.1, 0.1, 0.1,
1, 1, 1, 1,
1, 1, 1, 1,
1, 1, 1, 1,
1, 1, 1, 1,
1, 1, 1, 1,
1, 1, 1, 1
};
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
-1, -1, -1, -1,
1, 1, 1, 1,
0, 0, 0, -0.5,
-1, 0, 0, 0,
0, 0, 0, 0,
0, 0, 0, 0,
0, 0, 0, 0,
0, 0, 0, 0
};
primitive_ox = 0; primitive_oy = 0; primitive_oz = 0; // Origin: x, y, z
primitive_rox = 0; primitive_roy = 0; primitive_roz = 0; // Local Rotation Origin: x, y, z
primitive_rax = 0; primitive_ray = 0; primitive_raz = 0; // Local Rotation Angle: x, y, z
// Parameters
primitive_t_1 = 5; primitive_t_1_1 = 0; primitive_t_1_2 = 0; // Number of X nodes, progression, bump
primitive_t_2 = 10; primitive_t_2_1 = 0; primitive_t_2_2 = 0; // Number of Y nodes, progression, bump
primitive_t_3 = 15; primitive_t_3_1 = 0; primitive_t_3_2 = 0; // Number of Z nodes, progression, bump
primitive_t_4 = 0; // Hex (1) or tet (0) mesh?
primitive_t_5s = {0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0}; // Type of lines: 0 - straight, 1 - circle, 2 - ellipse, 3 - Bezier, 4 - BSpline, 5+ - Spline
primitive_t_6 = 0; // Type of hex to tet splitting
primitive_t_7s = {}; // Inner Surfaces
primitive_t_8s = {0, 0, 0, 0, 0, 0}; // Surfaces for changes
primitive_t_9s = {}; // Rotations
primitive_t_10s = {0, 0, 0, 0, 0, 0}; // Plane Surface?

// Curve 0 (point 1 -> point 2)
primitive_t_5s_lcs_0[] = {};
primitive_t_5s_xs_0[] = {};
primitive_t_5s_ys_0[] = {};
primitive_t_5s_zs_0[] = {};
n = 24; // Number of curve points
dy = 0.25; // Delta Y
dx = (n-1)/n*(primitive_xs[0]-primitive_xs[1]); // Delta X
For i In {1 : n}
  primitive_t_5s_lcs_0[] += 0.1;
  primitive_t_5s_xs_0[] += primitive_xs[1] + i/n*dx;
  primitive_t_5s_ys_0[] += primitive_ys[1] + Sin(i/n*2*Pi)*dy;
  primitive_t_5s_zs_0[] += primitive_zs[1];
EndFor

Call primitive;

Physical Surface ("NX1") = {primitive_ss[0]};
Physical Surface ("X1") = {primitive_ss[1]};
Physical Surface ("NY1") = {primitive_ss[2]};
Physical Surface ("Y1") = {primitive_ss[3]};
Physical Surface ("NZ1") = {primitive_ss[4]};
Physical Surface ("Z1") = {primitive_ss[5]};
//Physical Surface ("B") = {primitive_ss[]};

ss[] = primitive_ss[];
vs[] = primitive_vs[];

/*Physical Volume ("V") = {primitive_vs[]};*/


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
primitive_ox = 2; primitive_oy = 0; primitive_oz = 0; // Origin: x, y, z

Call primitive;

//BooleanFragments{ Surface{primitive_ss[0]}; Delete; }{ Surface{ss[1]}; Delete;}
//BooleanUnion{ Surface{primitive_ss[0]}; Delete; }{ Surface{ss[1]}; Delete; }
//BooleanUnion{ Volume{primitive_vs[]}; Delete; }{ Volume{vs[]}; Delete; }
//BooleanFragments{ Volume{primitive_vs[]}; }{ Volume{vs[]}; }

Physical Surface ("NX") = {primitive_ss[0]};
Physical Surface ("X") = {primitive_ss[1]};
Physical Surface ("NY") = {primitive_ss[2]};
Physical Surface ("Y") = {primitive_ss[3]};
Physical Surface ("NZ") = {primitive_ss[4]};
Physical Surface ("Z") = {primitive_ss[5]};

//Coherence;

//SetFactory("Built-in");



/*C = -0.5;*/
/*D = 2;*/
/*Block(2) = {C,C,C, D,D,D};*/

/*v() = BooleanFragments{ Volume{2}; Delete; }{ Volume{primitive_vs[]}; Delete; };*/
/*For i In {0 : #v()-1}*/
/*  Physical Volume (Sprintf("V%g", i)) = {v(i)};*/
/*EndFor*/
/*s() = Unique(Abs(Boundary{ Volume{v()}; }));*/
/*For i In {0 : #s()-1}*/
/*  Physical Surface (Sprintf("S%g", i)) = {s(i)};*/
/*EndFor*/

/*s() = Unique(Abs(Boundary{ Volume{2, 3}; }));*/
/*l() = Unique(Abs(Boundary{ Surface{s()}; }));*/
/*p() = Unique(Abs(Boundary{ Line{l()}; }));*/
/*Characteristic Length{p()} = 0.2;*/

/*A = -1;*/
/*B = 2;*/
/*C = -3;*/
/*D = 6;*/
/*Block(1) = {A,A,A, B,B,B};*/
/*Block(2) = {C,C,C, D,D,D};*/
/*v() = BooleanFragments{ Volume{1}; Delete; }{ Volume{2}; Delete; };*/




/*For i In {0 : #v()-1}*/
/*  Physical Volume (Sprintf("V%g", i)) = {v(i)};*/
/*EndFor*/

/*Transfinite Line{1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12} = 5;*/
/*Transfinite Surface{1, 2, 3, 4, 5, 6};*/
/*Transfinite Volume{1};*/

/*Block(1) = {0,0,0, 1,1,1};*/
/*Block(2) = {0,0,0, 0.5,0.5,0.5};*/
/*BooleanDifference(3) = { Volume{1}; Delete; }{ Volume{2}; Delete; };*/
/*x = 0 ; y = 0.75 ; z = 0 ; r = 0.09 ;*/
/*For t In {1:5}*/
/*  x += 0.166 ;*/
/*  z += 0.166 ;*/
/*  Sphere(3 + t) = {x,y,z,r};*/
/*EndFor*/
/*v() = BooleanFragments{ Volume{3}; Delete; }{ Volume{3+1:3+5}; Delete; };*/

/*s() = Unique(Abs(Boundary{ Volume{v()}; }));*/
/*l() = Unique(Abs(Boundary{ Surface{s()}; }));*/
/*p() = Unique(Abs(Boundary{ Line{l()}; }));*/
/*Characteristic Length{p()} = 0.055;*/



/*R = 5;*/
/*R2 = 3;*/
/*Rs = 1;*/
/*Rt = 1;*/
/*Box(1) = {-R,-R,-R, 2*R,2*R,2*R};*/
/*Box(2) = {-R2,-R2,-R2, 2*R2,2*R2,2*R2};*/

/*/*booleans = BooleanFragments { Volume{1}; }{ Volume{2}; };*/

/*/*For i In {0 : #booleans[]-1}*/
/*/*  Physical Volume (Sprintf("V_%g", i)) = {booleans[i]};*/
/*/*EndFor*/

/*bnd() = Abs(Boundary{ Volume{1}; });*/

/*Transfinite Surface{bnd()} = 5;*/


//l() = Unique(Abs(Boundary{ Surface{s()}; }));

//N = DefineNumber[ 10, Name "Parameters/N" ];

// simple transfinite mesh
//Transfinite Line {l()} = 5;
/*Transfinite Surface{s[0]} = 5;*/

// transfinite mesh with explicit corners
//Transfinite Line {9} = 2*N-1;
//l4() = Abs(Boundary{ Surface{4}; });
//p4() = Unique(Abs(Boundary{ Line{l4()}; }));
//Transfinite Surface{4} = {p4({0:3})};


/*booleans = BooleanFragments { Volume{primitive_vs[]}; }{ Volume{primitive_vs[]}; };*/

/*Sphere(2) = {0,0,0,Rt};*/

/*BooleanIntersection(3) = { Volume{1}; Delete; }{ Volume{2}; Delete; };*/

/*Cylinder(4) = {-2*R,0,0, 4*R,0,0, Rs};*/
/*Cylinder(5) = {0,-2*R,0, 0,4*R,0, Rs};*/
/*Cylinder(6) = {0,0,-2*R, 0,0,4*R, Rs};*/

/*BooleanUnion(7) = { Volume{4}; Delete; }{ Volume{5,6}; Delete; };*/
/*BooleanDifference(8) = { Volume{3}; Delete; }{ Volume{7}; Delete; };*/
//+
