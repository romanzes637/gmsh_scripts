Include "macro_cylshell.geo";

Geometry.AutoCoherence = 0;

cylshell_lc = 0.1; // Points characteristic length
cylshell_r1 = 1; // Inner radius
cylshell_r2 = 2; // Outer radius
cylshell_h = 1; // Height
cylshell_ox = 1; cylshell_oy = 3; cylshell_oz = 0; // Origin: x, y, z
cylshell_rox = 2; cylshell_roy = 0; cylshell_roz = 0; // Local Rotation Origin: x, y, z
cylshell_rax = 0; cylshell_ray = Pi/4; cylshell_raz = 0; // Local Rotation Angle: x, y, z
// Parameters
cylshell_t_1 = 10; cylshell_t_1_1 = 0; cylshell_t_1_2 = 0; // Number of circumferential nodes, progression, bump
cylshell_t_2 = 15; cylshell_t_2_1 = 0; cylshell_t_2_2 = 0; // Number of radial nodes, progression, bump
cylshell_t_3 = 20; cylshell_t_3_1 = 0; cylshell_t_3_2 = 0; // Number of height nodes, progression, bump
cylshell_t_4 = 0; // Hex (1) or tet (0) mesh?

Call cylshell;

Physical Surface ("I") = {cylshell_iss[]};
Physical Surface ("L") = {cylshell_lss[]};
Physical Surface ("NZ") = {cylshell_nzss[]};
Physical Surface ("Z") = {cylshell_zss[]};

Physical Volume ("V") = {cylshell_vs[]};

bss = {};
bss += cylshell_iss[];
bss += cylshell_lss[];
bss += cylshell_nzss[];
bss += cylshell_zss[];
//Physical Surface ("B") = {bss[]};

Coherence;

