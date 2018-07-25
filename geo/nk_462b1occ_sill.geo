SetFactory("OpenCASCADE");

Geometry.AutoCoherence = 0;
// Geometry.OCCParallel = 0;
// Mesh.CharacteristicLengthExtendFromBoundary = 1;
// Mesh.CharacteristicLengthFactor = 1;
// Mesh.CharacteristicLengthMin = 0;
// Mesh.CharacteristicLengthMax = 1e+22;
// Mesh.CharacteristicLengthFromCurvature = 0;
// Mesh.CharacteristicLengthFromPoints = 1;

Include "macro_borehole1occ.geo";
Include "macro_sill.geo";
Include "macro_hexahedron.geo";
Include "macro_pmapi.geo";

x_start = 0;

// Boreholes Parameters
//borehole1occ_lcs[] = {0.3, 0.3, 0.3};
//borehole1occ_rs[] = {0.281, 0.603, 0.650};
//borehole1occ_hs[] = {73.800, 74.444, 74.538};
//borehole1occ_pvns[] = Str("Matrix", "Container", "Fill");
borehole1occ_lcs[] = {1.000};
borehole1occ_rs[] = {0.650};
borehole1occ_hs[] = {75.000};
borehole1occ_pvns[] = Str("Borehole");


// ILW Boreholes
Printf("ILW Boreholes");
dx = 23; nx = 14; // Interval 23, Number of x boreholes 14
dy = 15; ny = 1; // Interval 15, Number of y boreholes 20
ilw_vs[] = {};
n_ilw = nx*ny;
y_start = -dy*(ny-1)/2;
For k In {0 : nx-1}
  borehole1occ_ox = x_start+k*dx;
  For j In {0 : ny-1}
    borehole1occ_oy = y_start+j*dy; borehole1occ_oz = 0; // Origin: x, y, z
    Call borehole1occ;
    ilw_vs[] += borehole1occ_out[];
    name = StrCat(Sprintf("ILW %g/", k*ny+j+1), Sprintf("%g ", n_ilw), Sprintf("X%g", k+1), Sprintf("Y%g", j+1));
    Printf(name);
  EndFor
EndFor
x_start += nx*dx;


// HLW Boreholes
Printf("HLW Boreholes");
hlw_vs[] = {};
dx = 26; nx = 14; // Interval 26, Number of x boreholes 14
dy = 23; ny = 1; // Interval 23, Number of y boreholes 13
n_hlw = nx*ny;
y_start = -dy*(ny-1)/2;
For k In {0 : nx-1}
  borehole1occ_ox = x_start+k*dx;
  For j In {0 : ny-1}
    borehole1occ_oy = y_start+j*dy; borehole1occ_oz = 0; // Origin: x, y, z
    Call borehole1occ;
    hlw_vs[] += borehole1occ_out[];
    name = StrCat(Sprintf("HLW %g/", k*ny+j+1), Sprintf("%g ", n_hlw), Sprintf("X%g", k+1), Sprintf("Y%g", j+1));
    Printf(name);
  EndFor
EndFor
x_start += nx*dx-dx;
y_rng = ny*dy-dy;


// Sill
Printf("Sill");
sill_lcs[] = {
  25, 25, 25, 25,
  25, 25, 25, 25
};
sill_kx = 350; sill_ky = 175; sill_kz = 25;
sill_ox = 0; sill_oy = 0; sill_oz = 0; // Origin: x, y, z
Call sill;


// Booleans
vs[] = {};
// ILW-Sill boolean
Printf("ILW-Sill Boolean");
pvs[] = {};
For i In {0 : #ilw_vs[]-1 : #borehole1occ_rs[]}
  bvs[] = {};
  For j In {0 : #borehole1occ_rs[]-1}
    bvs[] += ilw_vs[i+j];
  EndFor
  out[] = BooleanFragments{ Volume{bvs[], sill_vs[]}; Delete; } {};
  sill_vs[] = out[#out[]-1];
  If (#out[] == 4) // Sill divides each borehole's layer by 3 parts
    For j In {0 : #out[]-2 : 3}
      pvs[] += j/3;
      pvs[] += 3;
      pvs[] += out[j];
      pvs[] += out[j+1];
      pvs[] += out[j+2];
    EndFor
  ElseIf (#out[] == 3) // Sill divides each borehole's layer by 2 parts TODO layers partially dividing
    For j In {0 : #out[]-2 : 2}
      pvs[] += j/3;
      pvs[] += 2;
      pvs[] += out[j];
      pvs[] += out[j+1];
    EndFor
  Else // Sill doesn't divede borehole
    For j In {0 : #out[]-2 : 1}
      pvs[] += j/3;
      pvs[] += 1;
      pvs[] += out[j];
    EndFor
  EndIf
EndFor
// ILW physical volumes
Printf("ILW Physical Volumes");
pmapi_in[] = pvs[];
//idcs[] = {0, 1, 2};
idcs[] = {};
For i In {0 : #borehole1occ_pvns[]-1}
  idcs[] += i;
EndFor
For i In {0 : #idcs[]-1}
  Printf(borehole1occ_pvns[idcs[i]]);
  pmapi_idx = idcs[i];
  Call pmapi;
  For j In {0 : #pmapi_out[]-1}
/*    Printf("%g", pmapi_out[j]);*/
  EndFor
  vs[] += pmapi_out[];
  ps[] = PointsOf{ Volume{pmapi_out[]}; };
  Characteristic Length {ps[]} = borehole1occ_lcs[i];
  Physical Volume (StrCat("ILW", borehole1occ_pvns[idcs[i]])) = {pmapi_out[]};
EndFor
Printf("HLW-Sill Boolean");
// HLW-Sill boolean
pvs[] = {};
For i In {0 : #hlw_vs[]-1 : #borehole1occ_rs[]}
  bvs[] = {};
  For j In {0 : #borehole1occ_rs[]-1}
    bvs[] += hlw_vs[i+j];
  EndFor
  out[] = BooleanFragments{ Volume{bvs[], sill_vs[]}; Delete; } {};
  sill_vs[] = out[#out[]-1];
  If (#out[] == 4) // Sill divides each borehole's layer by 3 parts
    For j In {0 : #out[]-2 : 3}
      pvs[] += j/3;
      pvs[] += 3;
      pvs[] += out[j];
      pvs[] += out[j+1];
      pvs[] += out[j+2];
    EndFor
  ElseIf (#out[] == 3) // Sill divides each borehole's layer by 2 parts TODO layers partially dividing
    For j In {0 : #out[]-2 : 2}
      pvs[] += j/3;
      pvs[] += 2;
      pvs[] += out[j];
      pvs[] += out[j+1];
    EndFor
  Else // Sill doesn't divede borehole
    For j In {0 : #out[]-2 : 1}
      pvs[] += j/3;
      pvs[] += 1;
      pvs[] += out[j];
    EndFor
  EndIf
EndFor
// HLW physical volumes*/
Printf("HLW Physical Volumes");
pmapi_in[] = pvs[];
//idcs[] = {0, 1, 2};
idcs[] = {};
For i In {0 : #borehole1occ_pvns[]-1}
  idcs[] += i;
EndFor
For i In {0 : #idcs[]-1}
  Printf(borehole1occ_pvns[idcs[i]]);
  pmapi_idx = idcs[i];
  Call pmapi;
  For j In {0 : #pmapi_out[]-1}
/*    Printf("%g", pmapi_out[j]);*/
  EndFor
  vs[] += pmapi_out[];
  ps[] = PointsOf{ Volume{pmapi_out[]}; };
  Characteristic Length {ps[]} = borehole1occ_lcs[i];
  Physical Volume (StrCat("HLW", borehole1occ_pvns[idcs[i]])) = {pmapi_out[]};
EndFor
// Sill physical volume
Printf("Sill Physical Volumes");
vs[] += sill_vs[];
Physical Volume ("Sill") = {sill_vs[]};


// Boundary Surfaces
// ss[] = Boundary{ Volume{out[]}; };
// bss[] = {};
// add = 1;
// For i In {0 : #ss[]-1}
  // add = 1;
  // For j In {0 : #ss[]-1}
    // If (i != j)
      // If (ss[i] == ss[j])
        // add = 0;
      // EndIf
    // EndIf
  // EndFor
  // If (add == 1)
    // bss[] += ss[i];
  // EndIf
// EndFor
// Physical Surface ("BS") = {bss[]};
// Printf("ss");
// For i In {0 : #ss[]-1}
  // Printf("%g", ss[i]);
// EndFor
// Printf("bss");
// For i In {0 : #bss[]-1}
  // Printf("%g", bss[i]);
// EndFor
// Borehole points
// For i In {0 : #out[]-2}
  // Printf("v%g", out[i]);
  // ps[] = PointsOf{ Volume{out[i]}; };
  // For j In {0 : #ps[]-1}
    // Printf("p%g", ps[j]);
  // EndFor
  // Characteristic Length {ps[]} = 0.3;
// EndFor
// Sill points
// ps[] = PointsOf{ Volume{out[#out[]-1]}; };
// For i In {0 : 7}
  // Printf("sill p%g", ps[#ps[]-1-7+i]);
  // Characteristic Length {ps[#ps[]-1-7+i]} = sill_lcs[i];
// EndFor
// Characteristic Length {ps[]} = 5;
// ss[] = Unique(Abs(Boundary{ Volume{out[#out[]-1]}; }));
// ls[] = Unique(Abs(Boundary{ Surface{ss[]}; }));
// ps[] = Unique(Abs(Boundary{ Line{ls[]}; }));
// For i In {0 : 7}
  // Characteristic Length {primitive_ps[i]} = sill_lcs[i];
// EndFor


// Rock
Printf("Rock");
hexahedron_lc = 80; // Points characteristic length
hexahedron_a = x_start+1000; // X length
hexahedron_b = y_rng+1000; // Y length
hexahedron_c = 975; // Z length
hexahedron_ox = x_start/2; hexahedron_oy = y_rng/2; hexahedron_oz = 0; // Origin: x, y, z
hexahedron_rox = 0; hexahedron_roy = 0; hexahedron_roz = 0; // Local Rotation Origin: x, y, z
hexahedron_rax = 0; hexahedron_ray = 0; hexahedron_raz = 0; // Local Rotation Angle: x, y, z
// Parameters
hexahedron_t_1 = 0; hexahedron_t_1_1 = 0; hexahedron_t_1_2 = 0; // Number of X nodes, progression, bump
hexahedron_t_2 = 0; hexahedron_t_2_1 = 0; hexahedron_t_2_2 = 0; // Number of Y nodes, progression, bump
hexahedron_t_3 = 0; hexahedron_t_3_1 = 0; hexahedron_t_3_2 = 0; // Number of Z nodes, progression, bump
hexahedron_t_4 = 0; // Hex (1) or tet (0) mesh?
hexahedron_t_6 = 0; // Type of hex to tet splitting
//hexahedron_t_7s[] = {bss[]}; // Inner Surfaces // Old variant
hexahedron_t_7s[] = {}; // Inner Surfaces
Call hexahedron;
// Old variant could not preserve tags from Built-in to OpenCASCADE so Waiting Fix...
// Physical Surface ("NX") = {hexahedron_nxss[]};
// Physical Surface ("X") = {hexahedron_xss[]};
// Physical Surface ("NY") = {hexahedron_nyss[]};
// Physical Surface ("Y") = {hexahedron_yss[]};
// Physical Surface ("NZ") = {hexahedron_nzss[]};
// Physical Surface ("Z") = {hexahedron_zss[]};
// Physical Volume ("Rock") = {hexahedron_vs[]};
Printf("Rock Boolean");
// Boolean variant VEEERY SLOW...
//out2[] = BooleanFragments{ Volume{hexahedron_vs[], vs[]}; Delete; } {};
// Boolean variant with modification SLOW...
out2[] = hexahedron_vs[];
For i In {0 : #vs[]-1}
  Printf(StrCat(Sprintf("Volume %g/", i+1), Sprintf("%g ", #vs[])));
  out2[] = BooleanFragments{ Volume{out2[#out2[]-1], vs[i]}; Delete; } {};
EndFor
Printf("Rock Physical Volume");
Physical Volume ("Rock") = {out2[#out2[]-1]};
Printf("Rock Physical Surfaces");
ss[] = Unique(Abs(Boundary{ Volume{out2[#out2[]-1]}; }));
Physical Surface ("NX") = {ss[#ss[]-6]};
Physical Surface ("X") = {ss[#ss[]-1]};
Physical Surface ("NY") = {ss[#ss[]-4]};
Physical Surface ("Y") = {ss[#ss[]-3]};
Physical Surface ("NZ") = {ss[#ss[]-5]};
Physical Surface ("Z") = {ss[#ss[]-2]};

Printf("End");
