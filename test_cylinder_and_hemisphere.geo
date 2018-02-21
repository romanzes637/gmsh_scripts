Include "macro_cylinder.geo";
Include "macro_hemisphere.geo";

Geometry.AutoCoherence = 0;

cylinder_lc = 0.1; // Points characteristic length
cylinder_k = 0.3; // Inner hexahedron X, Y edge length / Radius
cylinder_r = 1; // Radius
cylinder_h = 1; // Height
cylinder_ox = 0; cylinder_oy = 0; cylinder_oz = 0; // Origin: x, y, z
cylinder_rox = 2; cylinder_roy = 0; cylinder_roz = 0; // Local Rotation Origin: x, y, z
cylinder_rax = 0; cylinder_ray = 0; cylinder_raz = 0; // Local Rotation Angle: x, y, z
// Parameters
cylinder_t_1 = 10; cylinder_t_1_1 = 0; cylinder_t_1_2 = 0; // Number of circumferential nodes, progression, bump
cylinder_t_2 = 10; cylinder_t_2_1 = 0; cylinder_t_2_2 = 0; // Number of radial nodes, progression, bump
cylinder_t_3 = 10; cylinder_t_3_1 = 0; cylinder_t_3_2 = 0; // Number of height nodes, progression, bump
cylinder_t_4 = 0; // Hex (1) or tet (0) mesh?

Call cylinder;

//Physical Surface ("L") = {cylinder_lss[]};
//Physical Surface ("NZ") = {cylinder_nzss[]};
//Physical Surface ("Z") = {cylinder_zss[]};

Physical Volume ("V1") = {cylinder_vs[]};

//bss = {};
//bss += cylinder_lss[];
//bss += cylinder_nzss[];
//bss += cylinder_zss[];
//Physical Surface ("B") = {bss[]};


hemisphere_lc = 0.1; // Points characteristic length
hemisphere_k = 0.3; // Inner hexahedron edge length / Radius
hemisphere_r = 1; // Radius
hemisphere_ox = 0; hemisphere_oy = 0; hemisphere_oz = 0.5; // Origin: x, y, z
// Parameters
hemisphere_t_1 = 10; hemisphere_t_1_1 = 0; hemisphere_t_1_2 = 0; // Number of nodes, progression, bump
hemisphere_t_4 = 0; // Hex (1) or tet (0) mesh?

Call hemisphere;

//Physical Surface ("L") = {hemisphere_lss[]};
//Physical Surface ("NZ") = {hemisphere_nzss[]};

Physical Volume ("V2") = {hemisphere_vs[]};

//bss = {};
//bss += hemisphere_lss[];
//bss += hemisphere_nzss[];
//Physical Surface ("B") = {bss[]};

Coherence;

