Include "macro_hemisphere.geo";

Geometry.AutoCoherence = 0;

hemisphere_lc = 0.1; // Points characteristic length
hemisphere_k = 0.3; // Inner hexahedron edge length / Radius
hemisphere_r = 1; // Radius
hemisphere_ox = 0; hemisphere_oy = 0; hemisphere_oz = 0; // Origin: x, y, z
// Parameters
hemisphere_t_1 = 12; hemisphere_t_1_1 = 0; hemisphere_t_1_2 = 0; // Number of circumferential nodes, progression, bump
hemisphere_t_2 = 6; hemisphere_t_2_1 = 1.3; hemisphere_t_2_2 = 0; // Number of radial nodes, progression, bump
hemisphere_t_4 = 0; // Hex (1) or tet (0) mesh?

Call hemisphere;

Physical Surface ("L") = {hemisphere_lss[]};
Physical Surface ("NZ") = {hemisphere_nzss[]};

Physical Volume ("V") = {hemisphere_vs[]};

bss = {};
bss += hemisphere_lss[];
bss += hemisphere_nzss[];
//Physical Surface ("B") = {bss[]};

Coherence;

