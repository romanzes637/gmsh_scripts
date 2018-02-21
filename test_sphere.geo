Include "macro_sphere.geo";

Geometry.AutoCoherence = 0;

sphere_lc = 0.1; // Points characteristic length
sphere_k = 0.3; // Inner hexahedron edge length / Radius
sphere_r = 1; // Radius
sphere_ox = 0; sphere_oy = 0; sphere_oz = 0; // Origin: x, y, z
// Parameters
sphere_t_1 = 12; sphere_t_1_1 = 0; sphere_t_1_2 = 0; // Number of circumferential nodes, progression, bump
sphere_t_2 = 6; sphere_t_2_1 = 1.3; sphere_t_2_2 = 0; // Number of radial nodes, progression, bump
sphere_t_4 = 1; // Hex (1) or tet (0) mesh?

Call sphere;

Physical Surface ("L") = {sphere_lss[]};

Physical Volume ("V") = {sphere_vs[]};

bss = {};
bss += sphere_lss[];
//Physical Surface ("B") = {bss[]};

Coherence;

