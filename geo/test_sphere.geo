Include "macro_sphere.geo";

Geometry.AutoCoherence = 0;

sphere_lc = 0.1; // Points characteristic length
sphere_k = 0.3; // Inner hexahedron edge length / Radius
sphere_r = 1; // Radius
sphere_ox = 0; sphere_oy = -2; sphere_oz = 0; // Origin: x, y, z
sphere_rox = 2; sphere_roy = 0; sphere_roz = 0; // Local Rotation Origin: x, y, z
sphere_rax = 0; sphere_ray = Pi/4; sphere_raz = 0; // Local Rotation Angle: x, y, z
// Parameters
sphere_t_1 = 12; sphere_t_1_1 = 0; sphere_t_1_2 = 0; // Number of circumferential nodes, progression, bump
sphere_t_2 = 6; sphere_t_2_1 = 1.3; sphere_t_2_2 = 0; // Number of radial nodes, progression, bump
sphere_t_4 = 0; // Hex (1) or tet (0) mesh?

Call sphere;

Physical Surface ("L") = {sphere_lss[]};

Physical Volume ("V") = {sphere_vs[]};

bss = {};
bss += sphere_lss[];
//Physical Surface ("B") = {bss[]};

Coherence;

