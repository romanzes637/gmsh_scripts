Include "macro_nk_container.geo";
Include "macro_hexahedron.geo";
Include "macro_pmapi.geo";

Geometry.AutoCoherence = 0;

nkcontainer_ox = 0; nkcontainer_oy = 0; nkcontainer_oz = 0; // Origin: x, y, z (bottom)
nkcontainer_rax = 0; nkcontainer_ray = 0; nkcontainer_raz = 0;  // Local Rotation Angle: x, y, z
nkcontainer_t1 = 13; // Number of circumferential nodes (for sphere cap: <= 13)
nkcontainer_t2s = {
3, 3, 3, 3, 3, 3, 3, 3, 3, 5
}; // Number of radial nodes
nkcontainer_t2t1s = {
0, 0, 0, 0, 0, 0, 0, 0, 0, 0
}; // Radial nodes progression
nkcontainer_t2t2s = {
0, 0, 0, 0, 0, 0, 0, 0, 0, 0
}; // Radial nodes bump
nkcontainer_t3s = {
3, 3, 7, 3,
3, 3, 5, 3,
3, 3, 30, 3,
7, 3, 3, 3,
3, 3, 7, 5
}; // Number of height nodes
nkcontainer_t3t1s = {
0, 0, 0, 0,
0, 0, 0, 0,
0, 0, 0, 0,
0, 0, 0, 0,
0, 0, 0, 0
}; // Height nodes progression
nkcontainer_t3t2s = {
0, 0, 0, 0,
0, 0, 0, 0,
0, 0, 0, 0,
0, 0, 0, 0,
0, 0, 0, 0
}; // Height nodes progression bump

Call nkcontainer;

//Physical Surface ("NZ") = {cylitive_nzss[]};
//Physical Surface ("Z") = {cylitive_zss[]};
//Physical Surface ("L") = {cylitive_lss[]};
//Physical Surface ("B") = {cylitive_bss[]};

hexahedron_lc = 1; // Points characteristic length
hexahedron_a = 23; // X length
hexahedron_b = 23; // Y length
hexahedron_c = 23; // Z length
hexahedron_ox = nkcontainer_ox; hexahedron_oy = nkcontainer_oy; hexahedron_oz = nkcontainer_oz+0.700; // Origin: x, y, z
hexahedron_rox = 0; hexahedron_roy = 0; hexahedron_roz = 0; // Local Rotation Origin: x, y, z
hexahedron_rax = 0; hexahedron_ray = 0; hexahedron_raz = 0; // Local Rotation Angle: x, y, z
// Parameters
hexahedron_t_1 = 0; hexahedron_t_1_1 = 0; hexahedron_t_1_2 = 0; // Number of X nodes, progression, bump
hexahedron_t_2 = 0; hexahedron_t_2_1 = 0; hexahedron_t_2_2 = 0; // Number of Y nodes, progression, bump
hexahedron_t_3 = 0; hexahedron_t_3_1 = 0; hexahedron_t_3_2 = 0; // Number of Z nodes, progression, bump
hexahedron_t_4 = 0; // Hex (1) or tet (0) mesh?
hexahedron_t_6 = 0; // Type of hex to tet splitting
hexahedron_t_7s = {nkcontainer_bss[]}; // Inner Surfaces

Call hexahedron;

Physical Surface ("NX") = {hexahedron_nxss[]};
Physical Surface ("X") = {hexahedron_xss[]};
Physical Surface ("NY") = {hexahedron_nyss[]};
Physical Surface ("Y") = {hexahedron_yss[]};
Physical Surface ("NZ") = {hexahedron_nzss[]};
Physical Surface ("Z") = {hexahedron_zss[]};

pmapi_in = nkcontainer_pvs[];
//idcs[] = {0, 1, 2, 3}; // nkcontainer_pvns array indices
idcs[] = {};
For i In {0 : #nkcontainer_pvns[]-1-1}
  idcs[] += i;
EndFor
Printf("Physical Volumes = %g", #idcs[]);
For i In {0 : #idcs[]-1}
  Printf(nkcontainer_pvns[idcs[i]]);
  pmapi_idx = idcs[i];
  Call pmapi;
  Physical Volume (Str(nkcontainer_pvns[idcs[i]])) = {pmapi_out[]};
EndFor

// Environment
idcs[] = {10}; // nkcontainer_pvns array indices
Printf("Environment Physical Volumes = %g", #idcs[]);
For i In {0 : #idcs[]-1}
  Printf(nkcontainer_pvns[idcs[i]]);
  pmapi_idx = idcs[i];
  Call pmapi;
  Physical Volume (Str(nkcontainer_pvns[idcs[i]])) = {pmapi_out[], hexahedron_vs[]};
EndFor
//Physical Volume ("Environment") = {hexahedron_vs[]};

Coherence;

