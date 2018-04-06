Include "macro_nk_container_cut.geo";
Include "macro_hexahedron.geo";
Include "macro_pmapi.geo";

Geometry.AutoCoherence = 0;

nkcontainer_ox = 0; nkcontainer_oy = 0; nkcontainer_oz = 0; // Origin: x, y, z (bottom)
nkcontainer_rax = 0; nkcontainer_ray = 0; nkcontainer_raz = 0;  // Local Rotation Angle: x, y, z
nkcontainer_t1 = 13; // Number of circumferential nodes (for sphere cap: <= 13)
nkcontainer_t2s = {
5, 5, 5, 5, 5, 5, 5, 5, 5, 20
}; // Number of radial nodes
nkcontainer_t2t1s = {
0, 0, 0, 0, 0, 0, 0, 0, 0, 1.3
}; // Radial nodes progression
nkcontainer_t2t2s = {
0, 0, 0, 0, 0, 0, 0, 0, 0, 0
}; // Radial nodes bump
nkcontainer_t3s = {
5, 9, 5,
5, 5, 7, 5,
5, 5, 32, 5,
9, 5, 5, 5,
5, 5, 9
}; // Number of height nodes
nkcontainer_t3t1s = {
0, 0, 0,
0, 0, 0, 0,
0, 0, 0, 0,
0, 0, 0, 0,
0, 0, 0
}; // Height nodes progression
nkcontainer_t3t2s = {
0, 0, 0,
0, 0, 0, 0,
0, 0, 0, 0,
0, 0, 0, 0,
0, 0, 0
}; // Height nodes progression bump

Call nkcontainer;

Physical Surface ("NZ") = {cylitive_bnzss[]};
Physical Surface ("Z") = {cylitive_bzss[]};
Physical Surface ("L") = {cylitive_blss[]};
//Physical Surface ("B") = {cylitive_bss[]};

pmapi_in = nkcontainer_pvs[];
//idcs[] = {0, 1, 2, 3}; // nkcontainer_pvns array indices
idcs[] = {};
For i In {0 : #nkcontainer_pvns[]-1}
  idcs[] += i;
EndFor
Printf("Physical Volumes = %g", #idcs[]);
For i In {0 : #idcs[]-1}
  Printf(nkcontainer_pvns[idcs[i]]);
  pmapi_idx = idcs[i];
  Call pmapi;
  Physical Volume (Str(nkcontainer_pvns[idcs[i]])) = {pmapi_out[]};
EndFor

Coherence;
