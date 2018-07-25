Include "macro_borehole1.geo";
Include "macro_borehole2.geo";
Include "macro_hexahedron.geo";
Include "macro_pmapi.geo";
Include "macro_cylinder2.geo";

Geometry.AutoCoherence = 0;

// Physical Volumes Names
//pvns[] = Str();
// Physical Volumes {pvnsI, nVolumes, v1, v2, v3, ..., vn, pvnsI, ...}
//pvs = {};
// Physical Surfaces {psnsI, nSurfaces, s1, s2, s3, ..., sn, psnsI, ...}
pss[] = {};
// Boundary Surfaces
bss[] = {};
// Local Physical Volumes {pvnsI, nVolumes, v1, v2, v3, ..., vn, pvnsI, ...}
lpvs[] = {};

// borehole2
//pvns2[] = Str(); // Physical Volumes Names
lpvs2[] = {}; // Local Physical Volumes {pvnsI, nVolumes, v1, v2, v3, ..., vn, pvnsI, ...}
bss2[] = {}; // Boundary Surfaces
vs2[] = {}; // Smooth borehole2 environment volumes

// borehole1 parameters
borehole1_t1 = 4; // Number of circumferential nodes
borehole1_t2s[] = {3, 3, 3}; // Number of radial nodes
borehole1_t2t1s[] = {0, 0, 0}; // Radial nodes progression
borehole1_t2t2s[] = {0, 0, 0}; // Radial nodes bump
borehole1_t3s[] = {5, 3, 3, 25, 3, 3, 5}; // Number of height nodes
borehole1_t3t1s[] = {0, 0, 0, 0, 0, 0, 0}; // Height nodes progression
borehole1_t3t2s[] = {0, 0, 0, 0.07, 0, 0, 0}; // Height nodes progression bump

// borehole2 parameters
borehole2_t1 = 13; // Number of circumferential nodes
borehole2_t2s[] = {
  5, 3, 3, 3, 3, 3, 3, // Cans cap void, MC cap void, MC cap, TC cap, TC cap, TC cap/IC cap
  5, 3, 3, 3, // Matrices, Cans width, MC void, MC width
  3, 3, 3, 3, // TC void, TC width, IC inner void, IC inner width
  5, 3, 3, 3, 3, 3, // Bentonite lateral, IC intermediate width, Concrete inner, IC ring, Concrete outer, IC outer width
  3 // Fill
}; // Number of radial nodes
borehole2_t2t1s[] = {
  0, 0, 0, 0, 0, 0, 0, // Cans cap void, MC cap void, MC cap, TC cap, TC cap, TC cap/IC cap
  0, 0, 0, 0, // Matrices, Cans width, MC void, MC width
  0, 0, 0, 0, // TC void, TC width, IC inner void, IC inner width
  0, 0, 0, 0, 0, 0, // Bentonite lateral, IC intermediate width, Concrete inner, IC ring, Concrete outer, IC outer width
  0 // Fill
}; // Radial nodes progression
borehole2_t2t2s[] = {
  0, 0, 0, 0, 0, 0, 0, // Cans cap void, MC cap void, MC cap, TC cap, TC cap, TC cap/IC cap
  0, 0, 0, 0, // Matrices, Cans width, MC void, MC width
  0, 0, 0, 0, // TC void, TC width, IC inner void, IC inner width
  0, 0, 0, 0, 0, 0, // Bentonite lateral, IC intermediate width, Concrete inner, IC ring, Concrete outer, IC outer width
  0 // Fill
}; // Radial nodes bump
borehole2_t3s[] = {
  9, // Bottom Gap
  3, // Isolation Container ring
  3, // Isolation Container bottom     
  3, // Bentonite bottom 
  3, // Transport Container bottom
  3, 3, 3, // Mayak Container bottom, anticap height, anticap width
  3, 5, 3, 3, 3, 3, // Can bottom, matrix, void, top, cap height, cap width
  3, 5, 3, 3, 3, 3, // Can bottom, matrix, void, top, cap height, cap width
  3, 5, 3, 3, 3, 3, // Can bottom, matrix, void, top, cap height, cap width
  3, 3, 3, 3, // Mayak Container void, top, cap height, cap width
  3, 3, 3, // Transport Container top, cap height, cap width
  3, // Bentonite top
  3, // Isolation Container top
  3, // Isolation Container cap height
  3, // Isolation Container cap width
  3, // Fill between Isolation Containers
  3, // Isolation Container cap height 
  3, // Isolation Container cap width
  9 // Top Gap height
}; // Number of height nodes
borehole2_t3t1s[] = {
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
borehole2_t3t2s[] = {
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

center_depth = 487.5; // Repository center Z depth
center_y = 0; // Repository Y center
center_z = 0; // Repository Z center

len_x = 0; // Repository X length
len_y = 0; // Repository Y length




// ILW
lpvs[] = {};
start_x = 0;
dx = 23; // Interval of x boreholes
dy = 15; // Interval of y boreholes
nb_x = 14; // Number of x boreholes 14
nb_y = 20; // Number of y boreholes 20
start_y = center_y - dy * (nb_y - 1) / 2;
len_y = dy * (nb_y - 1);
len_x += dx * (nb_x - 1);
borehole1_rax = 0; borehole1_ray = 0; borehole1_raz = 0;  // Local Rotation Angle: x, y, z
borehole2_rax = 0; borehole2_ray = 0; borehole2_raz = 0;  // Local Rotation Angle: x, y, z
borehole1_oz = center_z - 37.5; // Bottom Z coordinate
For i In {0 : nb_x-1}
  borehole1_ox = start_x + dx * i; // Bottom X coordinate
  For j In {0 : nb_y-1}
    Printf("ILW %g %g", i+1, j+1);
    borehole1_oy = start_y + dy * j; // Bottom Y coordinate
    If (i == 6 && j == 9) //If (i == 6 && j == 9) // borehole2
      borehole2_ox = borehole1_ox; borehole2_oy = borehole1_oy; borehole2_oz = borehole1_oz; // Origin: x, y, z (bottom)
      Call borehole2;
      lpvs2[] += borehole2_pvs[];
      bss2[] += borehole2_bss[];
      // Smooth Environment for borehole2
      Printf("Smooth Environment");
      cylinder2_lc = 1; // Points characteristic length
      cylinder2_r = 1.650; // Radius
      cylinder2_h = 75+0.650*2+1.000*2; // Height
      cylinder2_ox = borehole1_ox; cylinder2_oy = borehole1_oy; cylinder2_oz = center_z; // Origin: x, y, z
      cylinder2_rox = 0; cylinder2_roy = 0; cylinder2_roz = -37.5; // Local Rotation Origin: x, y, z
      cylinder2_rax = borehole2_rax; cylinder2_ray = borehole2_ray; cylinder2_raz = borehole2_raz; // Local Rotation Angle: x, y, z
      // Parameters
      cylinder2_t1 = 0; cylinder2_t1t1 = 0; cylinder2_t1t2 = 0; // Number of X nodes, progression, bump
      cylinder2_t2 = 0; cylinder2_t2t1 = 0; cylinder2_t2t2 = 0; // Number of Y nodes, progression, bump
      cylinder2_t3 = 0; cylinder2_t3t1 = 0; cylinder2_t3t2 = 0; // Number of Z nodes, progression, bump
      cylinder2_t4 = 0; // Hex (1) or tet (0) mesh?
      cylinder2_t6 = 0; // Type of hex to tet splitting
      cylinder2_t7s = {bss2[]}; // Inner Surfaces
      Call cylinder2;
      vs2[] = cylinder2_vs[];
      bss[] += cylinder2_bss[];
    Else // borehole1
      Call borehole1;
      lpvs[] += borehole1_pvs[];
      bss[] += borehole1_bss[];
    EndIf
  EndFor // j
EndFor // i

// Boreholes 1
pmapi_in[] = lpvs[];
idcs[] = {0, 1, 2, 3}; // borehole1_pvns array indices
Printf("ILW Borehole 1 Physical Volumes = %g", #idcs[]);
For i In {0 : #idcs[]-1}
  Printf(borehole1_pvns[idcs[i]]);
  pmapi_idx = idcs[i];
  Call pmapi;
  Physical Volume (StrCat("ILW", borehole1_pvns[idcs[i]])) = {pmapi_out[]};
EndFor

// borehole2
pmapi_in[] = lpvs2[];
idcs[] = {0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13}; // borehole_pvns array indices
Printf("ILW Borehole 2 Physical Volumes = %g", #idcs[]);
For i In {0 : #idcs[]-1}
  Printf(borehole2_pvns[idcs[i]]);
  pmapi_idx = idcs[i];
  Call pmapi;
  Physical Volume (StrCat("ILW", "Two", borehole2_pvns[idcs[i]])) = {pmapi_out[]};
EndFor




// Distance between ILW and HLW zones
len_x += dx;




// HLW
lpvs3[] = {};
start_x = dx * nb_x;
dx = 26; // Interval of x boreholes
dy = 23; // Interval of y boreholes
nb_x = 14; // Number of x boreholes 14
nb_y = 13; // Number of y boreholes 13
start_y = center_y - dy * (nb_y - 1) / 2;
len_x += dx * (nb_x - 1);
borehole1_oz = center_z - 37.5; // Bottom Z coordinate
For i In {0 : nb_x-1}
  borehole1_ox = start_x + dx * i; // Bottom X coordinate
  For j In {0 : nb_y-1}
    Printf("HLW %g %g", i+1, j+1);
    borehole1_oy = start_y + dy * j; // Bottom Y coordinate
    Call borehole1;
    lpvs3[] += borehole1_pvs[];
    bss[] += borehole1_bss[];
  EndFor // j
EndFor // i

// Boreholes 1
pmapi_in[] = lpvs3[];
idcs[] = {0, 1, 2, 3}; // borehole1_pvns array indices
Printf("HLW Physical Volumes = %g", #idcs[]);
For i In {0 : #idcs[]-1}
  Printf(borehole1_pvns[idcs[i]]);
  pmapi_idx = idcs[i];
  Call pmapi;
  Physical Volume (StrCat("HLW", borehole1_pvns[idcs[i]])) = {pmapi_out[]};
EndFor




// Global Environment
Printf("Global Environment");
env_vs[] = {}; // Environment volumes

// Hexahedron
hexahedron_lc = 75; // Points characteristic length
hexahedron_a = len_x + 1000; // X length
hexahedron_b = len_y + 1000; // Y length
hexahedron_c = center_depth*2; // Z length
hexahedron_ox = len_x/2; hexahedron_oy = center_y; hexahedron_oz = center_z; // Origin: x, y, z
hexahedron_rox = 0; hexahedron_roy = 0; hexahedron_roz = 0; // Local Rotation Origin: x, y, z
hexahedron_rax = 0; hexahedron_ray = 0; hexahedron_raz = 0; // Local Rotation Angle: x, y, z
// Parameters
hexahedron_t_1 = 0; hexahedron_t_1_1 = 0; hexahedron_t_1_2 = 0; // Number of X nodes, progression, bump
hexahedron_t_2 = 0; hexahedron_t_2_1 = 0; hexahedron_t_2_2 = 0; // Number of Y nodes, progression, bump
hexahedron_t_3 = 0; hexahedron_t_3_1 = 0; hexahedron_t_3_2 = 0; // Number of Z nodes, progression, bump
hexahedron_t_4 = 0; // Hex (1) or tet (0) mesh?
hexahedron_t_6 = 0; // Type of hex to tet splitting
hexahedron_t_7s[] = {bss[]}; // Inner Surfaces

Call hexahedron;

env_vs[] += hexahedron_vs[];

Physical Surface ("NX") = {hexahedron_nxss[]};
Physical Surface ("X") = {hexahedron_xss[]};
Physical Surface ("NY") = {hexahedron_nyss[]};
Physical Surface ("Y") = {hexahedron_yss[]};
Physical Surface ("NZ") = {hexahedron_nzss[]};
Physical Surface ("Z") = {hexahedron_zss[]};

// borehole1 ILW
pmapi_in[] = lpvs[];
idcs[] = {4}; // borehole1_pvns array "Environment" zone indices
For i In {0 : #idcs[]-1}
  Printf(StrCat("Borehole 1 ILW", borehole1_pvns[idcs[i]]));
  pmapi_idx = idcs[i];
  Call pmapi;
  env_vs[] += pmapi_out[];
EndFor

// borehole1 HLW
pmapi_in[] = lpvs3[];
idcs[] = {4}; // borehole1_pvns array "Environment" zone indices
For i In {0 : #idcs[]-1}
  Printf(StrCat("Borehole 1 HLW", borehole1_pvns[idcs[i]]));
  pmapi_idx = idcs[i];
  Call pmapi;
  env_vs[] += pmapi_out[];
EndFor

// borehole2
pmapi_in[] = lpvs2[];
idcs[] = {14}; // borehole2_pvns array "Environment" zone indices
For i In {0 : #idcs[]-1}
  Printf(StrCat("Borehole 2 ", borehole2_pvns[idcs[i]]));
  pmapi_idx = idcs[i];
  Call pmapi;
  env_vs[] += pmapi_out[];
EndFor

// Smooth borehole2 environment volumes
env_vs[] += vs2[];

Physical Volume ("Environment") = {env_vs[]};




Coherence;

