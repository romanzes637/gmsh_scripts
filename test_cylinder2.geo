Include "macro_cylinder2.geo";

Geometry.AutoCoherence = 0;

cylinder2_lc = 0.5; // Points characteristic length
cylinder2_r = 2; // Radius
cylinder2_h = 1; // Height
cylinder2_ox = 1; cylinder2_oy = 2; cylinder2_oz = -1; // Origin: x, y, z
cylinder2_rox = 3; cylinder2_roy = -1; cylinder2_roz = 0; // Local Rotation Origin: x, y, z
cylinder2_rax = 0; cylinder2_ray = Pi/3; cylinder2_raz = -Pi/3; // Local Rotation Angle: x, y, z
// Parameters
cylinder2_t1 = 5; cylinder2_t1t1 = 1.2; cylinder2_t1t2 = 0; // Number of X nodes, progression, bump
cylinder2_t2 = 10; cylinder2_t2t1 = 0; cylinder2_t2t2 = 0.3; // Number of Y nodes, progression, bump
cylinder2_t3 = 15; cylinder2_t3t1 = 0; cylinder2_t3t2 = 0; // Number of Z nodes, progression, bump
cylinder2_t4 = 0; // Hex (1) or tet (0) mesh?
cylinder2_t6 = 0; // Type of hex to tet splitting
cylinder2_t7s = {}; // Inner Surfaces

Call cylinder2;

Physical Surface ("NX") = {cylinder2_nxss[]};
Physical Surface ("X") = {cylinder2_xss[]};
Physical Surface ("NY") = {cylinder2_nyss[]};
Physical Surface ("Y") = {cylinder2_yss[]};
Physical Surface ("NZ") = {cylinder2_nzss[]};
Physical Surface ("Z") = {cylinder2_zss[]};
Physical Surface ("B") = {cylinder2_bss[]};

Physical Volume ("V") = {cylinder2_vs[]};

Coherence;

