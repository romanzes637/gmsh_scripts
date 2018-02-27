Include "macro_cylinder.geo";
Include "macro_hemisphere.geo";
Include "macro_cylshell.geo";
Include "macro_sphereshell.geo";

Geometry.AutoCoherence = 0;

ox = 1; oy = -2; oz = 3;
rox = 1; roy = 2; roz = -3;
rax = 0; ray = -Pi/3; raz = Pi/4;
t_1 = 15; // Number of circumferential nodes
t_2 = 10; // Number of radial nodes
t_3 = 5; // Number of height nodes

// Cylinder 1
cylinder_lc = 0.1; // Points characteristic length
cylinder_k = 0.3; // Inner hexahedron X, Y edge length / Radius
cylinder_r = 1; // Radius
cylinder_h = 1; // Height
cylinder_ox = ox; cylinder_oy = oy; cylinder_oz = oz; // Origin: x, y, z
cylinder_rox = rox; cylinder_roy = roy; cylinder_roz = roz; // Local Rotation Origin: x, y, z
cylinder_rax = rax; cylinder_ray = ray; cylinder_raz = raz; // Local Rotation Angle: x, y, z
// Parameters
cylinder_t_1 = t_1; cylinder_t_1_1 = 0; cylinder_t_1_2 = 0.3; // Number of circumferential nodes, progression, bump
cylinder_t_2 = t_2; cylinder_t_2_1 = 1.1; cylinder_t_2_2 = 0; // Number of radial nodes, progression, bump
cylinder_t_3 = t_3; cylinder_t_3_1 = 0; cylinder_t_3_2 = 0.5; // Number of height nodes, progression, bump
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


// Cylinder 2
cylinder_ox = ox; cylinder_oy = oy; cylinder_oz = oz+1; // Origin: x, y, z
cylinder_rox = rox; cylinder_roy = roy; cylinder_roz = roz-1; // Local Rotation Origin: x, y, z
Call cylinder;
Physical Volume ("V2") = {cylinder_vs[]};


// Hemisphere Up
hemisphere_lc = 0.1; // Points characteristic length
hemisphere_k = 0.3; // Inner hexahedron edge length / Radius
hemisphere_r = 1; // Radius
hemisphere_ox = ox; hemisphere_oy = oy; hemisphere_oz = oz+1+cylinder_h/2; // Origin: x, y, z
hemisphere_rox = rox; hemisphere_roy = roy; hemisphere_roz = roz-1-cylinder_h/2; // Local Rotation Origin: x, y, z
hemisphere_rax = rax; hemisphere_ray = ray; hemisphere_raz = raz; // Local Rotation Angle: x, y, z
// Parameters
hemisphere_t_1 = t_1; hemisphere_t_1_1 = 0; hemisphere_t_1_2 = 0.3; // Number of circumferential nodes, progression, bump
hemisphere_t_2 = t_2; hemisphere_t_2_1 = 1.1; hemisphere_t_2_2 = 0; // Number of radial nodes, progression, bump
hemisphere_t_3 = t_3; hemisphere_t_3_1 = 0; hemisphere_t_3_2 = 0.2; // Number of height nodes, progression, bump
hemisphere_t_4 = 0; // Hex (1) or tet (0) mesh?
hemisphere_t_5 = 1;
Call hemisphere;
//Physical Surface ("L") = {hemisphere_lss[]};
//Physical Surface ("NZ") = {hemisphere_zss[]};
Physical Volume ("V3") = {hemisphere_vs[]};
//bss = {};
//bss += hemisphere_lss[];
//bss += hemisphere_zss[];
//Physical Surface ("B") = {bss[]};


// Hemisphere Down
hemisphere_ox = ox; hemisphere_oy = oy; hemisphere_oz = oz-cylinder_h/2; // Origin: x, y, z
hemisphere_rox = rox; hemisphere_roy = roy; hemisphere_roz = roz+cylinder_h/2; // Local Rotation Origin: x, y, z
hemisphere_t_5 = 0;
Call hemisphere;
//Physical Surface ("L") = {hemisphere_lss[]};
//Physical Surface ("NZ") = {hemisphere_zss[]};
Physical Volume ("V4") = {hemisphere_vs[]};
//bss = {};
//bss += hemisphere_lss[];
//bss += hemisphere_zss[];
//Physical Surface ("B") = {bss[]};


// Cylshell 1
cylshell_lc = 0.1; // Points characteristic length
cylshell_r1 = 1; // Inner radius
cylshell_r2 = 2; // Outer radius
cylshell_h = 1; // Height
cylshell_ox = ox; cylshell_oy = oy; cylshell_oz = oz; // Origin: x, y, z
cylshell_rox = rox; cylshell_roy = roy; cylshell_roz = roz; // Local Rotation Origin: x, y, z
cylshell_rax = rax; cylshell_ray = ray; cylshell_raz = raz; // Local Rotation Angle: x, y, z
// Parameters
cylshell_t_1 = t_1; cylshell_t_1_1 = 0; cylshell_t_1_2 = 0.3; // Number of circumferential nodes, progression, bump
cylshell_t_2 = t_2; cylshell_t_2_1 = 1.2; cylshell_t_2_2 = 0; // Number of radial nodes, progression, bump
cylshell_t_3 = t_3; cylshell_t_3_1 = 0; cylshell_t_3_2 = 0.5; // Number of height nodes, progression, bump
cylshell_t_4 = 0; // Hex (1) or tet (0) mesh?
Call cylshell;
//Physical Surface ("I") = {cylshell_iss[]};
//Physical Surface ("L") = {cylshell_lss[]};
//Physical Surface ("NZ") = {cylshell_nzss[]};
//Physical Surface ("Z") = {cylshell_zss[]};
Physical Volume ("V5") = {cylshell_vs[]};
//bss = {};
//bss += cylshell_iss[];
//bss += cylshell_lss[];
//bss += cylshell_nzss[];
//bss += cylshell_zss[];
//Physical Surface ("B") = {bss[]};


// Cylshell 2
cylshell_ox = ox; cylshell_oy = oy; cylshell_oz = oz+1; // Origin: x, y, z
cylshell_rox = rox; cylshell_roy = roy; cylshell_roz = roz-1; // Local Rotation Origin: x, y, z
Call cylshell;
Physical Volume ("V6") = {cylshell_vs[]};


// Sphereshell Up
sphereshell_lc = 0.1; // Points characteristic length
sphereshell_r1 = 1; // Inner radius
sphereshell_r2 = 2; // Outer radius
sphereshell_h = 1; // Height
sphereshell_ox = ox; sphereshell_oy = oy; sphereshell_oz = oz+1+cylinder_h/2; // Origin: x, y, z
sphereshell_rox = rox; sphereshell_roy = roy; sphereshell_roz = roz-1-cylinder_h/2; // Local Rotation Origin: x, y, z
sphereshell_rax = rax; sphereshell_ray = ray; sphereshell_raz = raz; // Local Rotation Angle: x, y, z
// Parameters
sphereshell_t_1 = t_1; sphereshell_t_1_1 = 0; sphereshell_t_1_2 = 0.3; // Number of circumferential nodes, progression, bump
sphereshell_t_2 = t_2; sphereshell_t_2_1 = 1.2; sphereshell_t_2_2 = 0; // Number of radial nodes, progression, bump
sphereshell_t_3 = t_3; sphereshell_t_3_1 = 0; sphereshell_t_3_2 = 0.2; // Number of height nodes, progression, bump
sphereshell_t_4 = 0; // Hex (1) or tet (0) mesh?
sphereshell_t_5 = 1; // Up (1) or Down (0) part?
Call sphereshell;
//Physical Surface ("I") = {sphereshell_iss[]};
//Physical Surface ("L") = {sphereshell_lss[]};
//Physical Surface ("NZ") = {sphereshell_zss[]};
Physical Volume ("V7") = {sphereshell_vs[]};
//bss = {};
//bss += sphereshell_iss[];
//bss += sphereshell_lss[];
//bss += sphereshell_zss[];
//Physical Surface ("B") = {bss[]};


// Sphereshell Down
sphereshell_ox = ox; sphereshell_oy = oy; sphereshell_oz = oz-cylinder_h/2; // Origin: x, y, z
sphereshell_rox = rox; sphereshell_roy = roy; sphereshell_roz = roz+cylinder_h/2; // Local Rotation Origin: x, y, z
sphereshell_t_5 = 0; // Up (1) or Down (0) part?
Call sphereshell;
//Physical Surface ("I") = {sphereshell_iss[]};
//Physical Surface ("L") = {sphereshell_lss[]};
//Physical Surface ("NZ") = {sphereshell_zss[]};
Physical Volume ("V8") = {sphereshell_vs[]};
//bss = {};
//bss += sphereshell_iss[];
//bss += sphereshell_lss[];
//bss += sphereshell_zss[];
//Physical Surface ("B") = {bss[]};

Coherence;

