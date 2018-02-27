Include "macro_borehole1.geo";
Include "macro_hexahedron.geo";

Geometry.AutoCoherence = 0;

// Physical Volumes Names
pvns[] = Str();
// Physical Volumes {pvnsI, nVolumes, v1, v2, v3, ..., vn, pvnsI, ...}
pvs = {};
// Physical Surfaces {psnsI, nSurfaces, s1, s2, s3, ..., sn, psnsI, ...}
pss = {};
// Boundary Surfaces
bss = {};
// Local Physical Volumes {pvnsI, nVolumes, v1, v2, v3, ..., vn, pvnsI, ...}
lpvs = {};

centerDepth = 487.5; // Repository center Z depth
centerY = 0; // Repository Y center
centerZ = 0; // Repository Z center

lengthX = 0; // Repository X length
lengthY = 0; // Repository Y length

// ILW
lpvs = {};
startX = 0;
dX = 23; // Interval of x boreholes
dY = 15; // Interval of y boreholes
nBoreholesX = 14; // Number of x boreholes 14
nBoreholesY = 20; // Number of y boreholes 20
startY = centerY - dY * (nBoreholesY - 1) / 2;
lengthY = dY * (nBoreholesY - 1);
lengthX += dX * (nBoreholesX - 1);
For NkI In {0 : nBoreholesX-1}
  borehole1_ox = startX + dX * NkI; // Bottom X coordinate
  For NkJ In {0 : nBoreholesY-1}
    Printf("ILW %g %g", NkI+1, NkJ+1);
    borehole1_oy = startY + dY * NkJ; // Bottom Y coordinate
    borehole1_oz = centerZ - 37.5; // Bottom Z coordinate
    borehole1_rax = 0; borehole1_ray = 0; borehole1_raz = 0;  // Local Rotation Angle: x, y, z
    Call borehole1;
    lpvs += borehole1_pvs[];
    pvs += borehole1_pvs[];
    pvns[] = Str();
    For NkK In {0 : #borehole1_pvns[]-1}
      pvns[] += Str(borehole1_pvns[NkK]);
    EndFor // NkK
/*        pss += ContainerPhysicalSurfaces[];*/
    bss += borehole1_bss[];
  EndFor // NkJ
EndFor // NkI

// Boreholes 1
//pvnsIdxs = {};
pvnsIdxs = {0, 1, 2, 3};
//For NkI In {0 : #pvns[]-1}
//  pvnsIdxs += NkI;
//EndFor // NkI
If(#lpvs[] > 0)
  Printf("ILW Physical Volumes = %g", #pvnsIdxs[]);
  For NkI In {0 : #pvnsIdxs[]-1}
    pvnsi = pvnsIdxs[NkI];
    Printf(pvns[pvnsi]);
    vs = {};
    startIndex = 0;
    For pvsi In {0 : #lpvs[]-1}
      If(pvsi == startIndex)
        nvs = lpvs[pvsi+1];
        startIndex += 1 + nvs + 1;
        If(lpvs[pvsi] == pvnsi)
          For pvsj In {pvsi+2 : pvsi+2+nvs-1}
            vs += lpvs[pvsj];
          EndFor
        EndIf
      EndIf
    EndFor
    Physical Volume (StrCat("ILW", pvns[pvnsi])) = {vs[]};
  EndFor
EndIf

// Distance between ILW and HLW zones
lengthX += dX;

// HLW
lpvs = {};
startX = dX * nBoreholesX;
dX = 26; // Interval of x boreholes
dY = 23; // Interval of y boreholes
nBoreholesX = 14; // Number of x boreholes 14
nBoreholesY = 13; // Number of y boreholes 13
startY = centerY - dY * (nBoreholesY - 1) / 2;
lengthX += dX * (nBoreholesX - 1);
For NkI In {0 : nBoreholesX-1}
  borehole1_ox = startX + dX * NkI; // Bottom X coordinate
  For NkJ In {0 : nBoreholesY-1}
    Printf("HLW %g %g", NkI+1, NkJ+1);
    borehole1_oy = startY + dY * NkJ; // Bottom Y coordinate
    borehole1_oz = centerZ - 37.5; // Bottom Z coordinate
    Call borehole1;
    lpvs += borehole1_pvs[];
    pvs += borehole1_pvs[];
/*        pss += ContainerPhysicalSurfaces[];*/
    bss += borehole1_bss[];
  EndFor // NkJ
EndFor // NkI

pvnsIdxs = {0, 1, 2, 3};
//pvnsIdxs = {};
//For NkI In {0 : #pvns[]-1}
//    pvnsIdxs += NkI;
//EndFor // NkI
If(#lpvs[] > 0)
    Printf("HLW Physical Volumes = %g", #pvnsIdxs[]);
    For NkI In {0 : #pvnsIdxs[]-1}
      pvnsi = pvnsIdxs[NkI];
      Printf(pvns[pvnsi]);
      vs = {};
      startIndex = 0;
      For pvsi In {0 : #lpvs[]-1}
        If(pvsi == startIndex)
          nvs = lpvs[pvsi+1];
          startIndex += 1 + nvs + 1;
          If(lpvs[pvsi] == pvnsi)
            For pvsj In {pvsi+2 : pvsi+2+nvs-1}
              vs += lpvs[pvsj];
            EndFor
          EndIf
        EndIf
      EndFor
      Physical Volume (StrCat("HLW", pvns[pvnsi])) = {vs[]};
    EndFor
EndIf

hexahedron_lc = 75; // Points characteristic length
hexahedron_a = lengthX + 1000; // X length
hexahedron_b = lengthY + 1000; // Y length
hexahedron_c = centerDepth*2; // Z length
hexahedron_ox = lengthX/2; hexahedron_oy = centerY; hexahedron_oz = centerZ; // Origin: x, y, z
hexahedron_rox = 0; hexahedron_roy = 0; hexahedron_roz = 0; // Local Rotation Origin: x, y, z
hexahedron_rax = 0; hexahedron_ray = 0; hexahedron_raz = 0; // Local Rotation Angle: x, y, z
// Parameters
hexahedron_t_1 = 0; hexahedron_t_1_1 = 0; hexahedron_t_1_2 = 0; // Number of X nodes, progression, bump
hexahedron_t_2 = 0; hexahedron_t_2_1 = 0; hexahedron_t_2_2 = 0; // Number of Y nodes, progression, bump
hexahedron_t_3 = 0; hexahedron_t_3_1 = 0; hexahedron_t_3_2 = 0; // Number of Z nodes, progression, bump
hexahedron_t_4 = 0; // Hex (1) or tet (0) mesh?
hexahedron_t_6 = 0; // Type of hex to tet splitting
hexahedron_t_7s = {bss[]}; // Inner Surfaces

Call hexahedron;

Physical Surface ("NX") = {hexahedron_nxss[]};
Physical Surface ("X") = {hexahedron_xss[]};
Physical Surface ("NY") = {hexahedron_nyss[]};
Physical Surface ("Y") = {hexahedron_yss[]};
Physical Surface ("NZ") = {hexahedron_nzss[]};
Physical Surface ("Z") = {hexahedron_zss[]};

GlobalPhysicalIdxs = {4}; // Global Physcal Volumes
Printf("Global Physical Volumes = %g", #GlobalPhysicalIdxs[]);
For ContainerI In {0 : #GlobalPhysicalIdxs[]-1}
  Printf(borehole1_pvns[GlobalPhysicalIdxs[ContainerI]]);
  ContainerVs = {};
  ContainerStartIndex = 0;
  For ContainerJ In {0 : #pvs[]-1}
    If(ContainerJ == ContainerStartIndex)
      ContainerNVs = pvs[ContainerJ+1];
      ContainerStartIndex += 2 + ContainerNVs;
      If(pvs[ContainerJ] == GlobalPhysicalIdxs[ContainerI])
        For ContainerK In {ContainerJ+2 : ContainerJ+2+ContainerNVs-1}
          ContainerVs += pvs[ContainerK];
        EndFor // ContainerK
      EndIf
    EndIf
  EndFor // ContainerJ
  If (StrCmp(Str(borehole1_pvns[GlobalPhysicalIdxs[ContainerI]]), "Environment") == 0) // If physical name is "Environment"
    Physical Volume (Str(borehole1_pvns[GlobalPhysicalIdxs[ContainerI]])) = {ContainerVs[], hexahedron_vs[]};
  Else
    Physical Volume (Str(borehole1_pvns[GlobalPhysicalIdxs[ContainerI]])) = {ContainerVs[]};
  EndIf
EndFor // ContainerI

/*Printf("Global Physical Surfaces = %g", #ContainerPhysicalNames[]*#ContainerSurfacePhysicalNames[]);*/
/*For ContainerI In {0 : #ContainerPhysicalNames[]-1}*/
/*    For ContainerL In {0 : #ContainerSurfacePhysicalNames[]-1}*/
/*        Printf(StrCat(Str(ContainerPhysicalNames[ContainerI]), Str(ContainerSurfacePhysicalNames[ContainerL])));*/
/*        ContainerSs = {};*/
/*        ContainerStartIndex = 0;*/
/*        For ContainerJ In {0 : #pss[]-1}*/
/*            If(ContainerJ == ContainerStartIndex)*/
/*                ContainerNVs = pss[ContainerJ+2];*/
/*                ContainerStartIndex += 3 + ContainerNVs;*/
/*                If(pss[ContainerJ] == ContainerI && pss[ContainerJ+1] == ContainerL)*/
/*                    For ContainerK In {ContainerJ+3 : ContainerJ+3+ContainerNVs-1}*/
/*                        ContainerSs += pss[ContainerK];*/
/*                    EndFor // ContainerK*/
/*                EndIf*/
/*            EndIf*/
/*        EndFor // ContainerJ*/
/*        Physical Surface (StrCat(Str(ContainerPhysicalNames[ContainerI]), Str(ContainerSurfacePhysicalNames[ContainerL]))) = {ContainerSs[]};*/
/*    EndFor // ContainerL*/
/*EndFor // ContainerI*/

Coherence;

