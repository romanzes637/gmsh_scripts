Include "macro_hexahedron.geo";

Geometry.AutoCoherence = 0;

hexahedron_lc = 0.1; // Points characteristic length
hexahedron_a = 2; // X length
hexahedron_b = 1; // Y length
hexahedron_c = 1; // Z length
hexahedron_ox = 1; hexahedron_oy = 3; hexahedron_oz = 0; // Origin: x, y, z
hexahedron_rox = 2; hexahedron_roy = 0; hexahedron_roz = 0; // Local Rotation Origin: x, y, z
hexahedron_rax = 1; hexahedron_ray = 4; hexahedron_raz = 1; // Local Rotation Angle: x, y, z
// Parameters
hexahedron_t_1 = 10; hexahedron_t_1_1 = 0; hexahedron_t_1_2 = 0; // Number of X nodes, progression, bump
hexahedron_t_2 = 15; hexahedron_t_2_1 = 0; hexahedron_t_2_2 = 0; // Number of Y nodes, progression, bump
hexahedron_t_3 = 20; hexahedron_t_3_1 = 0; hexahedron_t_3_2 = 0; // Number of Z nodes, progression, bump
hexahedron_t_4 = 0; // Hex (1) or tet (0) mesh?
hexahedron_t_6 = 0; // Type of hex to tet splitting
hexahedron_t_7s = {}; // Inner Surfaces

Call hexahedron;

Physical Surface ("NX") = {hexahedron_nxss[]};
Physical Surface ("X") = {hexahedron_xss[]};
Physical Surface ("NY") = {hexahedron_nyss[]};
Physical Surface ("Y") = {hexahedron_yss[]};
Physical Surface ("NZ") = {hexahedron_nzss[]};
Physical Surface ("Z") = {hexahedron_zss[]};

Physical Volume ("V") = {hexahedron_vs[]};

bss = {};
bss += hexahedron_nxss[];
bss += hexahedron_xss[];
bss += hexahedron_nyss[];
bss += hexahedron_yss[];
bss += hexahedron_nzss[];
bss += hexahedron_zss[];
//Physical Surface ("B") = {bss[]};

Coherence;

