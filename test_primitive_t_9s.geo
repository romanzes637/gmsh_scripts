Include "macro_primitive.geo";

Geometry.AutoCoherence = 0;

bvs = {};
bss = {};

dX = -0.4;
dY = 0.9;
dZ = 0.3;
originX = 0;
originY = 0;
originZ = 3;
angleX = Pi/36;
angleY = Pi/18;
angleZ = 0;

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
3, -3, -3, 3, 
3, -3, -3, 3, 
0, 0, 0, 0,
0, 0, 0, 0,
0, 0, 0, 0,
0, 0, 0, 0,
0, 0, 0, 0,
0, 0, 0, 0
};
primitive_ys = {
3, 3, -3, -3,
3, 3, -3, -3,
0, 0, 0, 0,
0, 0, 0, 0,
0, 0, 0, 0,
0, 0, 0, 0,
0, 0, 0, 0,
0, 0, 0, 0
};
primitive_zs = {
3, 3, 3, 3,
6, 6, 6, 6,
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
primitive_t_1 = 10; primitive_t_1_1 = 0; primitive_t_1_2 = 0; // Number of X nodes, progression, bump
primitive_t_2 = 10; primitive_t_2_1 = 0; primitive_t_2_2 = 0; // Number of Y nodes, progression, bump
primitive_t_3 = 10; primitive_t_3_1 = 0; primitive_t_3_2 = 0; // Number of Z nodes, progression, bump
primitive_t_4 = 0; // Hex (1) or tet (0) mesh?
primitive_t_5s = {0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0}; // Type of lines: 0 - straight, 1 - circle, 2 - ellipse, 3 - Bezier, 4 - BSpline, 5+ - Spline
primitive_t_6 = 0; // Type of hex to tet splitting
primitive_t_7s = {}; // Inner Surfaces
primitive_t_8s = {0, 0, 0, 0, 0, 0}; // Surfaces for changes
primitive_t_9s = {}; // Rotations
primitive_t_9s = {
0, 0, 0, 0,
1, 1, 1, 1,
0, 1, 1, 0,
0, 0, 1, 1,
0, 0, 0, 0,
0, 0, 0, 0,
0, 0, 0, 0,
0, 0, 0, 0
};
primitive_t_9s_ro_0 = {originX, originY, originZ}; 
primitive_t_9s_ra_0 = {angleX, angleY, angleZ}; 
primitive_t_9s_d_0 = {dX, dY, dZ};
primitive_t_9s_ro_1 = {originX, originY, originZ}; 
primitive_t_9s_ra_1 = {angleX, angleY, angleZ}; 
primitive_t_9s_d_1 = {dX, dY, dZ};
primitive_t_9s_ro_2 = {originX, originY, originZ}; 
primitive_t_9s_ra_2 = {angleX, angleY, angleZ};
primitive_t_9s_d_2 = {dX, dY, dZ};
primitive_t_9s_ro_3 = {originX, originY, originZ}; 
primitive_t_9s_ra_3 = {angleX, angleY, angleZ};
primitive_t_9s_d_3 = {dX, dY, dZ};
primitive_t_9s_ro_4 = {originX, originY, originZ}; 
primitive_t_9s_ra_4 = {angleX, angleY, angleZ};
primitive_t_9s_d_4 = {dX, dY, dZ};
primitive_t_9s_ro_5 = {originX, originY, originZ};
primitive_t_9s_ra_5 = {angleX, angleY, angleZ}; 
primitive_t_9s_d_5 = {dX, dY, dZ};
primitive_t_9s_ro_6 = {originX, originY, originZ};
primitive_t_9s_ra_6 = {angleX, angleY, angleZ};
primitive_t_9s_d_6 = {dX, dY, dZ};
primitive_t_9s_ro_7 = {originX, originY, originZ}; 
primitive_t_9s_ra_7 = {angleX, angleY, angleZ};
primitive_t_9s_d_7 = {dX, dY, dZ};
primitive_t_9s_ro_8 = {originX, originY, originZ}; 
primitive_t_9s_ra_8 = {angleX, angleY, angleZ}; 
primitive_t_9s_d_8 = {dX, dY, dZ};
primitive_t_9s_ro_9 = {originX, originY, originZ}; 
primitive_t_9s_ra_9 = {angleX, angleY, angleZ}; 
primitive_t_9s_d_9 = {dX, dY, dZ};
primitive_t_9s_ro_10 = {originX, originY, originZ}; 
primitive_t_9s_ra_10 = {angleX, angleY, angleZ};
primitive_t_9s_d_10 = {dX, dY, dZ};
primitive_t_9s_ro_11 = {originX, originY, originZ}; 
primitive_t_9s_ra_11 = {angleX, angleY, angleZ};
primitive_t_9s_d_11 = {dX, dY, dZ};
primitive_t_9s_ro_12 = {originX, originY, originZ}; 
primitive_t_9s_ra_12 = {angleX, angleY, angleZ}; 
primitive_t_9s_d_12 = {dX, dY, dZ};
primitive_t_9s_ro_13 = {originX, originY, originZ}; 
primitive_t_9s_ra_13 = {angleX, angleY, angleZ};
primitive_t_9s_d_13 = {dX, dY, dZ};
primitive_t_9s_ro_14 = {originX, originY, originZ}; 
primitive_t_9s_ra_14 = {angleX, angleY, angleZ}; 
primitive_t_9s_d_14 = {dX, dY, dZ};
primitive_t_9s_ro_15 = {originX, originY, originZ}; 
primitive_t_9s_ra_15 = {angleX, angleY, angleZ};
primitive_t_9s_d_15 = {dX, dY, dZ};
primitive_t_10s = {0, 0, 0, 0, 0, 0}; // Plane Surface?
Call primitive;
bvs += primitive_vs[];
bss += primitive_ss[4];

primitive_zs = {
6, 6, 6, 6,
9, 9, 9, 9,
6, 9, 9, 6,
6, 6, 9, 9,
0, 0, 0, 0,
0, 0, 0, 0,
0, 0, 0, 0,
0, 0, 0, 0
};
primitive_t_9s = {
1, 1, 1, 1,
1, 1, 1, 1,
1, 1, 1, 1,
1, 1, 1, 1,
0, 0, 0, 0,
0, 0, 0, 0,
0, 0, 0, 0,
0, 0, 0, 0
};
Call primitive;


primitive_zs = {
9, 9, 9, 9,
12, 12, 12, 12,
9, 12, 12, 9,
9, 9, 12, 12,
0, 0, 0, 0,
0, 0, 0, 0,
0, 0, 0, 0,
0, 0, 0, 0
};
primitive_t_9s = {
1, 1, 1, 1,
0, 0, 0, 0,
1, 0, 0, 1,
1, 1, 0, 0,
0, 0, 0, 0,
0, 0, 0, 0,
0, 0, 0, 0,
0, 0, 0, 0
};
Call primitive;
bvs += primitive_vs[];
bss += primitive_ss[5];

// X
primitive_xs = {
4, 3, 3, 4,
4, 3, 3, 4,
0, 0, 0, 0,
0, 0, 0, 0,
0, 0, 0, 0,
0, 0, 0, 0,
0, 0, 0, 0,
0, 0, 0, 0
};
primitive_ys = {
4, 3, -3, -4,
4, 3, -3, -4,
0, 0, 0, 0,
0, 0, 0, 0,
0, 0, 0, 0,
0, 0, 0, 0,
0, 0, 0, 0,
0, 0, 0, 0
};
primitive_zs = {
3, 3, 3, 3,
6, 6, 6, 6,
3, 6, 6, 3,
3, 3, 6, 6,
0, 0, 0, 0,
0, 0, 0, 0,
0, 0, 0, 0,
0, 0, 0, 0
};
primitive_t_9s = {
0, 0, 0, 0,
0, 1, 1, 0,
0, 0, 0, 0,
0, 0, 1, 0,
0, 0, 0, 0,
0, 0, 0, 0,
0, 0, 0, 0,
0, 0, 0, 0
};
Call primitive;
bvs += primitive_vs[];
bss += primitive_ss[4];
bss += primitive_ss[1];

primitive_zs = {
6, 6, 6, 6,
9, 9, 9, 9,
6, 9, 9, 6,
6, 6, 9, 9,
0, 0, 0, 0,
0, 0, 0, 0,
0, 0, 0, 0,
0, 0, 0, 0
};
primitive_t_9s = {
0, 1, 1, 0,
0, 1, 1, 0,
0, 0, 0, 0,
0, 1, 1, 0,
0, 0, 0, 0,
0, 0, 0, 0,
0, 0, 0, 0,
0, 0, 0, 0
};
Call primitive;
bvs += primitive_vs[];
bss += primitive_ss[1];

primitive_zs = {
9, 9, 9, 9,
12, 12, 12, 12,
9, 12, 12, 9,
9, 9, 12, 12,
0, 0, 0, 0,
0, 0, 0, 0,
0, 0, 0, 0,
0, 0, 0, 0
};
primitive_t_9s = {
0, 1, 1, 0,
0, 0, 0, 0,
0, 0, 0, 0,
0, 1, 0, 0,
0, 0, 0, 0,
0, 0, 0, 0,
0, 0, 0, 0,
0, 0, 0, 0
};
Call primitive;

bvs += primitive_vs[];
bss += primitive_ss[5];
bss += primitive_ss[1];

// Y
primitive_xs = {
4, -4, -3, 3,
4, -4, -3, 3,
0, 0, 0, 0,
0, 0, 0, 0,
0, 0, 0, 0,
0, 0, 0, 0,
0, 0, 0, 0,
0, 0, 0, 0
};
primitive_ys = {
4, 4, 3, 3,
4, 4, 3, 3,
0, 0, 0, 0,
0, 0, 0, 0,
0, 0, 0, 0,
0, 0, 0, 0,
0, 0, 0, 0,
0, 0, 0, 0
};
primitive_zs = {
3, 3, 3, 3,
6, 6, 6, 6,
3, 6, 6, 3,
3, 3, 6, 6,
0, 0, 0, 0,
0, 0, 0, 0,
0, 0, 0, 0,
0, 0, 0, 0
};
primitive_t_9s = {
0, 0, 0, 0,
0, 0, 1, 1,
0, 0, 1, 0,
0, 0, 0, 0,
0, 0, 0, 0,
0, 0, 0, 0,
0, 0, 0, 0,
0, 0, 0, 0
};
Call primitive;
bvs += primitive_vs[];
bss += primitive_ss[4];
bss += primitive_ss[3];

primitive_zs = {
6, 6, 6, 6,
9, 9, 9, 9,
6, 9, 9, 6,
6, 6, 9, 9,
0, 0, 0, 0,
0, 0, 0, 0,
0, 0, 0, 0,
0, 0, 0, 0
};
primitive_t_9s = {
0, 0, 1, 1,
0, 0, 1, 1,
0, 0, 1, 1,
0, 0, 0, 0,
0, 0, 0, 0,
0, 0, 0, 0,
0, 0, 0, 0,
0, 0, 0, 0
};
Call primitive;
bvs += primitive_vs[];
bss += primitive_ss[3];

primitive_zs = {
9, 9, 9, 9,
12, 12, 12, 12,
9, 12, 12, 9,
9, 9, 12, 12,
0, 0, 0, 0,
0, 0, 0, 0,
0, 0, 0, 0,
0, 0, 0, 0
};
primitive_t_9s = {
0, 0, 1, 1,
0, 0, 0, 0,
0, 0, 0, 1,
0, 0, 0, 0,
0, 0, 0, 0,
0, 0, 0, 0,
0, 0, 0, 0,
0, 0, 0, 0
};
Call primitive;
bvs += primitive_vs[];
bss += primitive_ss[5];
bss += primitive_ss[3];

// NX
primitive_xs = {
-3, -4, -4, -3,
-3, -4, -4, -3,
0, 0, 0, 0,
0, 0, 0, 0,
0, 0, 0, 0,
0, 0, 0, 0,
0, 0, 0, 0,
0, 0, 0, 0
};
primitive_ys = {
3, 4, -4, -3,
3, 4, -4, -3,
0, 0, 0, 0,
0, 0, 0, 0,
0, 0, 0, 0,
0, 0, 0, 0,
0, 0, 0, 0,
0, 0, 0, 0
};
primitive_zs = {
3, 3, 3, 3,
6, 6, 6, 6,
3, 6, 6, 3,
3, 3, 6, 6,
0, 0, 0, 0,
0, 0, 0, 0,
0, 0, 0, 0,
0, 0, 0, 0
};
primitive_t_9s = {
0, 0, 0, 0,
1, 0, 0, 1,
0, 0, 0, 0,
0, 0, 0, 1,
0, 0, 0, 0,
0, 0, 0, 0,
0, 0, 0, 0,
0, 0, 0, 0
};
Call primitive;
bvs += primitive_vs[];
bss += primitive_ss[4];
bss += primitive_ss[0];

primitive_zs = {
6, 6, 6, 6,
9, 9, 9, 9,
6, 9, 9, 6,
6, 6, 9, 9,
0, 0, 0, 0,
0, 0, 0, 0,
0, 0, 0, 0,
0, 0, 0, 0
};
primitive_t_9s = {
1, 0, 0, 1,
1, 0, 0, 1,
0, 0, 0, 0,
1, 0, 0, 1,
0, 0, 0, 0,
0, 0, 0, 0,
0, 0, 0, 0,
0, 0, 0, 0
};
Call primitive;
bvs += primitive_vs[];
bss += primitive_ss[0];

primitive_zs = {
9, 9, 9, 9,
12, 12, 12, 12,
9, 12, 12, 9,
9, 9, 12, 12,
0, 0, 0, 0,
0, 0, 0, 0,
0, 0, 0, 0,
0, 0, 0, 0
};
primitive_t_9s = {
1, 0, 0, 1,
0, 0, 0, 0,
0, 0, 0, 0,
1, 0, 0, 0,
0, 0, 0, 0,
0, 0, 0, 0,
0, 0, 0, 0,
0, 0, 0, 0
};
Call primitive;
bvs += primitive_vs[];
bss += primitive_ss[5];
bss += primitive_ss[0];

// NY
primitive_xs = {
3, -3, -4, 4,
3, -3, -4, 4,
0, 0, 0, 0,
0, 0, 0, 0,
0, 0, 0, 0,
0, 0, 0, 0,
0, 0, 0, 0,
0, 0, 0, 0
};
primitive_ys = {
-3, -3, -4, -4,
-3, -3, -4, -4,
0, 0, 0, 0,
0, 0, 0, 0,
0, 0, 0, 0,
0, 0, 0, 0,
0, 0, 0, 0,
0, 0, 0, 0
};
primitive_zs = {
3, 3, 3, 3,
6, 6, 6, 6,
3, 6, 6, 3,
3, 3, 6, 6,
0, 0, 0, 0,
0, 0, 0, 0,
0, 0, 0, 0,
0, 0, 0, 0
};
primitive_t_9s = {
0, 0, 0, 0,
1, 1, 0, 0,
0, 1, 0, 0,
0, 0, 0, 0,
0, 0, 0, 0,
0, 0, 0, 0,
0, 0, 0, 0,
0, 0, 0, 0
};
Call primitive;
bvs += primitive_vs[];
bss += primitive_ss[4];
bss += primitive_ss[2];

primitive_zs = {
6, 6, 6, 6,
9, 9, 9, 9,
6, 9, 9, 6,
6, 6, 9, 9,
0, 0, 0, 0,
0, 0, 0, 0,
0, 0, 0, 0,
0, 0, 0, 0
};
primitive_t_9s = {
1, 1, 0, 0,
1, 1, 0, 0,
1, 1, 0, 0,
0, 0, 0, 0,
0, 0, 0, 0,
0, 0, 0, 0,
0, 0, 0, 0,
0, 0, 0, 0
};
Call primitive;
bvs += primitive_vs[];
bss += primitive_ss[2];

primitive_zs = {
9, 9, 9, 9,
12, 12, 12, 12,
9, 12, 12, 9,
9, 9, 12, 12,
0, 0, 0, 0,
0, 0, 0, 0,
0, 0, 0, 0,
0, 0, 0, 0
};
primitive_t_9s = {
1, 1, 0, 0,
0, 0, 0, 0,
1, 0, 0, 0,
0, 0, 0, 0,
0, 0, 0, 0,
0, 0, 0, 0,
0, 0, 0, 0,
0, 0, 0, 0
};
Call primitive;
bvs += primitive_vs[];
bss += primitive_ss[5];
bss += primitive_ss[2];

Physical Volume ("BV") = {bvs[]};
Physical Surface ("BS") = {bss[]};

Coherence;
