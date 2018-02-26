Include "macro_sphereshell.geo";

Geometry.AutoCoherence = 0;

sphereshell_lc = 0.1; // Points characteristic length
sphereshell_r1 = 1; // Inner radius
sphereshell_r2 = 2; // Outer radius
sphereshell_h = 1; // Height
sphereshell_ox = 0; sphereshell_oy = 0; sphereshell_oz = 0; // Origin: x, y, z
sphereshell_rox = 0; sphereshell_roy = 0; sphereshell_roz = 0; // Local Rotation Origin: x, y, z
sphereshell_rax = 0; sphereshell_ray = 0; sphereshell_raz = 0; // Local Rotation Angle: x, y, z
// Parameters
sphereshell_t_1 = 10; sphereshell_t_1_1 = 0; sphereshell_t_1_2 = 0; // Number of circumferential nodes, progression, bump
sphereshell_t_2 = 15; sphereshell_t_2_1 = 0; sphereshell_t_2_2 = 0; // Number of radial nodes, progression, bump
sphereshell_t_3 = 20; sphereshell_t_3_1 = 0; sphereshell_t_3_2 = 0; // Number of height nodes, progression, bump
sphereshell_t_4 = 0; // Hex (1) or tet (0) mesh?
sphereshell_t_5 = 0; // Up (1) or Down (0) part?

Call sphereshell;

Physical Surface ("I") = {sphereshell_iss[]};
Physical Surface ("L") = {sphereshell_lss[]};
Physical Surface ("Z") = {sphereshell_zss[]};

Physical Volume ("V") = {sphereshell_vs[]};

bss = {};
bss += sphereshell_iss[];
bss += sphereshell_lss[];
bss += sphereshell_zss[];
//Physical Surface ("B") = {bss[]};

Coherence;

