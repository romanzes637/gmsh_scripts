Include "macro_primitive.geo";

Geometry.AutoCoherence = 0;

// Inner Primitive
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
0, 0, 0, -1,
0.3, 0, 0, 0,
0, 0, 0, 0,
0, 0, 0, 0,
0, 0, 0, 0,
0, 0, 0, 0
};
primitive_zs = {
-1, -1, -1, -1,
1, 1, 1, 1,
0, 0, 0, 0,
-0.2, 0, 0, 0,
0, 0, 0, 0,
0, 0, 0, 0,
0, 0, 0, 0,
0, 0, 0, 0
};
primitive_ox = 1; primitive_oy = 3; primitive_oz = 0; // Origin: x, y, z
primitive_rox = 2; primitive_roy = 0; primitive_roz = 0; // Local Rotation Origin: x, y, z
primitive_rax = 1; primitive_ray = 4; primitive_raz = 1; // Local Rotation Angle: x, y, z
// Parameters
primitive_t_1 = 10; primitive_t_1_1 = 0; primitive_t_1_2 = 0; // Number of X nodes, progression, bump
primitive_t_2 = 10; primitive_t_2_1 = 0; primitive_t_2_2 = 0; // Number of Y nodes, progression, bump
primitive_t_3 = 10; primitive_t_3_1 = 0; primitive_t_3_2 = 0; // Number of Z nodes, progression, bump
primitive_t_4 = 0; // Hex (1) or tet (0) mesh?
primitive_t_5s = {3, 0, 0, 1, 2, 0, 0, 0, 0, 0, 0, 0}; // Type of lines: 0 - straight, 1 - circle, 2 - ellipse, 3 - Bezier, 4 - BSpline, 5+ - Spline
primitive_t_6 = 0; // Type of hex to tet splitting
primitive_t_7s = {}; // Inner Surfaces
primitive_t_8s = {0, 0, 0, 0, 0, 0}; // Surfaces for changes
primitive_t_9s = {}; // Rotations
primitive_t_10s = {0, 0, 0, 0, 0, 0}; // Plane Surface?

// Curve 0
r1 = Sqrt(2);
r2 = 0.4;
h = 0.01;
primitive_t_5s_lcs_0 = {};
primitive_t_5s_xs_0 = {};
primitive_t_5s_ys_0 = {};
primitive_t_5s_zs_0 = {};
angle = 0;
For i In {-100 : 100}
    angle += Pi/4*h;
    primitive_t_5s_lcs_0 += 0.1;
    primitive_t_5s_xs_0 += r1*Sin(Pi/4*i*h);
    primitive_t_5s_zs_0 += -r1*Cos(Pi/4*i*h);
    local_y = 2*Pi*r1*angle/2/Pi;
    If (local_y < r2 || local_y > 3*r2)
        primitive_t_5s_ys_0 += 1;
    ElseIf (local_y >= r2 && local_y < 2*r2)
        primitive_t_5s_ys_0 += 1-Sqrt(r2*r2-(r2-(local_y-r2))*(r2-(local_y-r2)));
    ElseIf (local_y >= 2*r2 && local_y <= 3*r2)
        primitive_t_5s_ys_0 += 1-Sqrt(r2*r2-(local_y-2*r2)*(local_y-2*r2));  
    EndIf
EndFor

Call primitive;

Physical Surface ("NX") = {primitive_ss[0]};
Physical Surface ("X") = {primitive_ss[1]};
Physical Surface ("NY") = {primitive_ss[2]};
Physical Surface ("Y") = {primitive_ss[3]};
Physical Surface ("NZ") = {primitive_ss[4]};
Physical Surface ("Z") = {primitive_ss[5]};

Physical Volume ("V") = {primitive_vs[]};


// Outer Primitive
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
2, -2, -2, 2, 
2, -2, -2, 2, 
0, 0, 0, 0,
0, 0, 0, 0,
0, 0, 0, 0,
0, 0, 0, 0,
0, 0, 0, 0,
0, 0, 0, 0
};
primitive_ys = {
2, 2, -2, -2,
2, 2, -2, -2,
0, 0, 0, -1,
0.3, 0, 0, 0,
0, 0, 0, 0,
0, 0, 0, 0,
0, 0, 0, 0,
0, 0, 0, 0
};
primitive_zs = {
-2, -2, -2, -2,
2, 2, 2, 2,
0, 0, 0, 0,
-0.2, 0, 0, 0,
0, 0, 0, 0,
0, 0, 0, 0,
0, 0, 0, 0,
0, 0, 0, 0
};
primitive_ox = 1; primitive_oy = 3; primitive_oz = 0; // Origin: x, y, z
primitive_rox = 2; primitive_roy = 0; primitive_roz = 0; // Local Rotation Origin: x, y, z
primitive_rax = 1; primitive_ray = 4; primitive_raz = 1; // Local Rotation Angle: x, y, z
// Parameters
primitive_t_1 = 10; primitive_t_1_1 = 0; primitive_t_1_2 = 0; // Number of X nodes, progression, bump
primitive_t_2 = 10; primitive_t_2_1 = 0; primitive_t_2_2 = 0; // Number of Y nodes, progression, bump
primitive_t_3 = 10; primitive_t_3_1 = 0; primitive_t_3_2 = 0; // Number of Z nodes, progression, bump
primitive_t_4 = 0; // Hex (1) or tet (0) mesh?
primitive_t_5s = {2, 0, 0, 1, 2, 0, 0, 0, 0, 0, 0, 0}; // Type of lines: 0 - straight, 1 - circle, 2 - ellipse, 3 - Bezier, 4 - BSpline, 5+ - Spline
primitive_t_6 = 0; // Type of hex to tet splitting
primitive_t_7s = primitive_ss[]; // Inner Surfaces
primitive_t_8s = {0, 0, 0, 0, 0, 0}; // Surfaces for changes
primitive_t_9s = {}; // Rotations
primitive_t_10s = {0, 0, 0, 0, 0, 0}; // Plane Surface?

Call primitive;

Physical Surface ("NX2") = {primitive_ss[0]};
Physical Surface ("X2") = {primitive_ss[1]};
Physical Surface ("NY2") = {primitive_ss[2]};
Physical Surface ("Y2") = {primitive_ss[3]};
Physical Surface ("NZ2") = {primitive_ss[4]};
Physical Surface ("Z2") = {primitive_ss[5]};

Physical Volume ("V2") = {primitive_vs[]};

Coherence;


