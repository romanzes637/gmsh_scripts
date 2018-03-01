Include "macro_borehole2.geo";
Include "macro_hexahedron.geo";

Geometry.AutoCoherence = 0;

borehole2_ox = 0; borehole2_oy = 0; borehole2_oz = 0; // Origin: x, y, z (bottom)
borehole2_rax = 0; borehole2_ray = 0; borehole2_raz = 0;  // Local Rotation Angle: x, y, z
borehole2_t1 = 13; // Number of circumferential nodes
borehole2_t2s = {
  3, 3, 3, 3, 3, 3, 3, // Cans cap void, MC cap void, MC cap, TC cap, TC cap, TC cap/IC cap
  3, 3, 3, 3, // Matrices, Cans width, MC void, MC width
  3, 3, 3, 3, // TC void, TC width, IC inner void, IC inner width
  3, 3, 3, 3, 3, 3, // Bentonite lateral, IC intermediate width, Concrete inner, IC ring, Concrete outer, IC outer width
  3 // Fill
}; // Number of radial nodes
borehole2_t2t1s = {
  0, 0, 0, 0, 0, 0, 0, // Cans cap void, MC cap void, MC cap, TC cap, TC cap, TC cap/IC cap
  0, 0, 0, 0, // Matrices, Cans width, MC void, MC width
  0, 0, 0, 0, // TC void, TC width, IC inner void, IC inner width
  0, 0, 0, 0, 0, 0, // Bentonite lateral, IC intermediate width, Concrete inner, IC ring, Concrete outer, IC outer width
  0 // Fill
}; // Radial nodes progression
borehole2_t2t2s = {
  0, 0, 0, 0, 0, 0, 0, // Cans cap void, MC cap void, MC cap, TC cap, TC cap, TC cap/IC cap
  0, 0, 0, 0, // Matrices, Cans width, MC void, MC width
  0, 0, 0, 0, // TC void, TC width, IC inner void, IC inner width
  0, 0, 0, 0, 0, 0, // Bentonite lateral, IC intermediate width, Concrete inner, IC ring, Concrete outer, IC outer width
  0 // Fill
}; // Radial nodes bump
borehole2_t3s = {
  3, // Bottom Gap
  3, // Isolation Container ring
  3, // Isolation Container bottom     
  3, // Bentonite bottom 
  3, // Transport Container bottom
  3, 3, 3, // Mayak Container bottom, anticap height, anticap width
  3, 3, 3, 3, 3, 3, // Can bottom, matrix, void, top, cap height, cap width
  3, 3, 3, 3, 3, 3, // Can bottom, matrix, void, top, cap height, cap width
  3, 3, 3, 3, 3, 3, // Can bottom, matrix, void, top, cap height, cap width
  3, 3, 3, 3, // Mayak Container void, top, cap height, cap width
  3, 3, 3, // Transport Container top, cap height, cap width
  3, // Bentonite top
  3, // Isolation Container top
  3, // Isolation Container cap height
  3, // Isolation Container cap width
  3, // Fill between Isolation Containers
  3, // Isolation Container cap height 
  3, // Isolation Container cap width
  3 // Top Gap height
}; // Number of height nodes
borehole2_t3t1s = {
  0, // Bottom Gap
  0, // Isolation Container ring
  0, // Isolation Container bottom     
  0, // Bentonite bottom 
  0, // Transport Container bottom
  0, 0, 0, // Mayak Container bottom, anticap height, anticap width
  0, 0, 0, 0, 0, 0, // Can bottom, matrix, void, top, cap height, cap width
  0, 0, 0, 0, 0, 0, // Can bottom, matrix, void, top, cap height, cap width
  0, 0, 0, 0, 0, 0, // Can bottom, matrix, void, top, cap height, cap width
  0, 0, 0, 0, // Mayak Container void, top, cap height, cap width
  0, 0, 0, // Transport Container top, cap height, cap width
  0, // Bentonite top
  0, // Isolation Container top
  0, // Isolation Container cap height
  0, // Isolation Container cap width
  0, // Fill between Isolation Containers
  0, // Isolation Container cap height 
  0, // Isolation Container cap width
  0 // Top Gap height
}; // Height nodes progression
borehole2_t3t2s = {
  0, // Bottom Gap
  0, // Isolation Container ring
  0, // Isolation Container bottom     
  0, // Bentonite bottom 
  0, // Transport Container bottom
  0, 0, 0, // Mayak Container bottom, anticap height, anticap width
  0, 0, 0, 0, 0, 0, // Can bottom, matrix, void, top, cap height, cap width
  0, 0, 0, 0, 0, 0, // Can bottom, matrix, void, top, cap height, cap width
  0, 0, 0, 0, 0, 0, // Can bottom, matrix, void, top, cap height, cap width
  0, 0, 0, 0, // Mayak Container void, top, cap height, cap width
  0, 0, 0, // Transport Container top, cap height, cap width
  0, // Bentonite top
  0, // Isolation Container top
  0, // Isolation Container cap height
  0, // Isolation Container cap width
  0, // Fill between Isolation Containers
  0, // Isolation Container cap height 
  0, // Isolation Container cap width
  0 // Top Gap height
}; // Height nodes progression bump
Call borehole2;

hexahedron_lc = 50; // Points characteristic length
hexahedron_a = 1000; // X length
hexahedron_b = 1000; // Y length
hexahedron_c = 487.5*2; // Z length
hexahedron_ox = borehole2_ox; hexahedron_oy = borehole2_oy; hexahedron_oz = borehole2_oz+37.5; // Origin: x, y, z
hexahedron_rox = 0; hexahedron_roy = 0; hexahedron_roz = 0; // Local Rotation Origin: x, y, z
hexahedron_rax = 0; hexahedron_ray = 0; hexahedron_raz = 0; // Local Rotation Angle: x, y, z
// Parameters
hexahedron_t_1 = 0; hexahedron_t_1_1 = 0; hexahedron_t_1_2 = 0; // Number of X nodes, progression, bump
hexahedron_t_2 = 0; hexahedron_t_2_1 = 0; hexahedron_t_2_2 = 0; // Number of Y nodes, progression, bump
hexahedron_t_3 = 0; hexahedron_t_3_1 = 0; hexahedron_t_3_2 = 0; // Number of Z nodes, progression, bump
hexahedron_t_4 = 0; // Hex (1) or tet (0) mesh?
hexahedron_t_6 = 0; // Type of hex to tet splitting
hexahedron_t_7s = {borehole2_bss[]}; // Inner Surfaces
Call hexahedron;

Physical Surface ("NX") = {hexahedron_nxss[]};
Physical Surface ("X") = {hexahedron_xss[]};
Physical Surface ("NY") = {hexahedron_nyss[]};
Physical Surface ("Y") = {hexahedron_yss[]};
Physical Surface ("NZ") = {hexahedron_nzss[]};
Physical Surface ("Z") = {hexahedron_zss[]};
If(#borehole2_pvs[] > 0)
  Printf("Global Physical Volumes = %g", #borehole2_pvns[]);
  For pvns_i In {0 : #borehole2_pvns[]-1}
    Printf(borehole2_pvns[pvns_i]);
    vs = {};
    start_idx = 0;
    For pvs_i In {0 : #borehole2_pvs[]-1}
      If (pvs_i == start_idx)
        nvs = borehole2_pvs[pvs_i+1];
        start_idx += 1+nvs+1;
        If (borehole2_pvs[pvs_i] == pvns_i)
          For pvsj In {pvs_i+2 : pvs_i+2+nvs-1}
            vs += borehole2_pvs[pvsj];
          EndFor
        EndIf
      EndIf
    EndFor
    If (StrCmp(Str(borehole2_pvns[pvns_i]), "Environment") == 0) // If physical name is "Environment"
      Physical Volume (Str(borehole2_pvns[pvns_i])) = {vs[], hexahedron_vs[]};
    Else
      Physical Volume (Str(borehole2_pvns[pvns_i])) = {vs[]};
    EndIf
  EndFor
EndIf
//Physical Surface ("B") = {borehole2_bss[]};

Coherence;

