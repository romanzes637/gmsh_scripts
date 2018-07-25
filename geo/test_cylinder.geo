Include "macro_cylinder.geo";

Geometry.AutoCoherence = 0;

cylinder_lc = 0.1; // Points characteristic length
cylinder_k = 0.3; // Inner hexahedron X, Y edge length / Radius
cylinder_r = 1; // Radius
cylinder_h = 1; // Height
cylinder_ox = 1; cylinder_oy = 3; cylinder_oz = 0; // Origin: x, y, z
cylinder_rox = 2; cylinder_roy = 0; cylinder_roz = 0; // Local Rotation Origin: x, y, z
cylinder_rax = 0; cylinder_ray = Pi/4; cylinder_raz = 0; // Local Rotation Angle: x, y, z
// Parameters
cylinder_t_1 = 10; cylinder_t_1_1 = 0; cylinder_t_1_2 = 0; // Number of circumferential nodes, progression, bump
cylinder_t_2 = 15; cylinder_t_2_1 = 0; cylinder_t_2_2 = 0; // Number of radial nodes, progression, bump
cylinder_t_3 = 20; cylinder_t_3_1 = 0; cylinder_t_3_2 = 0; // Number of height nodes, progression, bump
cylinder_t_4 = 1; // Hex (1) or tet (0) mesh?

Call cylinder;

Physical Surface ("L") = {cylinder_lss[]};
Physical Surface ("NZ") = {cylinder_nzss[]};
Physical Surface ("Z") = {cylinder_zss[]};

Physical Volume ("V") = {cylinder_vs[]};

bss = {};
bss += cylinder_lss[];
bss += cylinder_nzss[];
bss += cylinder_zss[];
//Physical Surface ("B") = {bss[]};

Coherence;

