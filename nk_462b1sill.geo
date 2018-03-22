SetFactory("OpenCASCADE");

Geometry.AutoCoherence = 0;
Geometry.OCCParallel = 0;
// Mesh.CharacteristicLengthExtendFromBoundary = 1;
// Mesh.CharacteristicLengthFactor = 1;
// Mesh.CharacteristicLengthMin = 0;
// Mesh.CharacteristicLengthMax = 1e+22;
// Mesh.CharacteristicLengthFromCurvature = 0;
// Mesh.CharacteristicLengthFromPoints = 1;

Include "macro_borehole1occ.geo";
Include "macro_sill.geo";
Include "macro_hexahedron.geo";

vs[] = {};
x_start = 0;

Printf("ILW Boreholes");
// ILW Boreholes
dx = 23; nx = 1; // Interval 23, Number of x boreholes 14
dy = 15; ny = 1; // Interval 15, Number of y boreholes 20
n_ilw = nx*ny;
y_start = -dy*(ny-1)/2;
borehole1occ_lcs[] = {0.3, 0.3, 0.3};
For k In {0 : nx-1}
  borehole1occ_ox = x_start+k*dx;
  For j In {0 : ny-1}
    borehole1occ_oy = y_start+j*dy; borehole1occ_oz = 0; // Origin: x, y, z
    Call borehole1occ;
    vs[] += borehole1occ_out[];
    name = StrCat(Sprintf("ILW %g/", k*nx+j+1), Sprintf("%g ", n_ilw), Sprintf("X%g", k+1), Sprintf("Y%g", j+1));
    Printf(name);
  EndFor
EndFor
x_start += nx*dx;

Printf("HLW Boreholes");
// HLW
dx = 26; nx = 1; // Interval 26, Number of x boreholes 14
dy = 23; ny = 1; // Interval 23, Number of y boreholes 13
n_hlw = nx*ny;
y_start = -dy*(ny-1)/2;
borehole1occ_lcs = {0.3, 0.3, 0.3};
For k In {0 : nx-1}
  borehole1occ_ox = x_start+k*dx;
  For j In {0 : ny-1}
    borehole1occ_oy = y_start+j*dy; borehole1occ_oz = 0; // Origin: x, y, z
    Call borehole1occ;
    vs[] += borehole1occ_out[];
    name = StrCat(Sprintf("HLW %g/", k*nx+j+1), Sprintf("%g ", n_hlw), Sprintf("X%g", k+1), Sprintf("Y%g", j+1));
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
sill_kx = 250; sill_ky = 250; sill_kz = 5;
sill_ox = 0; sill_oy = 0; sill_oz = 0; // Origin: x, y, z
Call sill;
Printf("Boreholes/Sill Physical Volumes");
out[] = BooleanFragments{ Volume{vs[], sill_vs[]}; Delete; } {};
Physical Volume ("Sill") = {out[#out[]-1]};
// Borehole physical volumes
m_ilw_vs[] = {};
m_hlw_vs[] = {};
c_vs[] = {};
f_vs[] = {};
b_cnt = 0;
For i In {0 : #out[]-2 : 9}
  b_cnt += 1;
  For j In {0 : 2}
    If (b_cnt <= n_ilw)
      m_ilw_vs[] += out[i+j];
    Else
      m_hlw_vs[] += out[i+j];
    EndIf
  EndFor
  For j In {3 : 5}
    c_vs[] += out[i+j];
  EndFor
  For j In {6 : 8}
    f_vs[] += out[i+j];
  EndFor
EndFor
ps[] = PointsOf{ Volume{f_vs[]}; };
Characteristic Length {ps[]} = borehole1occ_lcs[2];
ps[] = PointsOf{ Volume{c_vs[]}; };
Characteristic Length {ps[]} = borehole1occ_lcs[1];
ps[] = PointsOf{ Volume{m_ilw_vs[]}; };
Characteristic Length {ps[]} = borehole1occ_lcs[0];
ps[] = PointsOf{ Volume{m_hlw_vs[]}; };
Characteristic Length {ps[]} = borehole1occ_lcs[0];
Physical Volume ("MatrixILW") = {m_ilw_vs[]};
Physical Volume ("MatrixHLW") = {m_hlw_vs[]};
Physical Volume ("Container") = {c_vs[]};
Physical Volume ("Fill") = {f_vs[]};
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
hexahedron_t_7s[] = {}; // Inner Surfaces
Call hexahedron;
Printf("Rock Physical Volumes");
out2[] = BooleanFragments{ Volume{hexahedron_vs[], out[]}; Delete; } {};
Physical Volume ("Rock") = {out2[#out2[]-1]};
ss[] = Unique(Abs(Boundary{ Volume{out2[#out2[]-1]}; }));
Physical Surface ("NX") = {ss[#ss[]-6]};
Physical Surface ("X") = {ss[#ss[]-1]};
Physical Surface ("NY") = {ss[#ss[]-4]};
Physical Surface ("Y") = {ss[#ss[]-3]};
Physical Surface ("NZ") = {ss[#ss[]-5]};
Physical Surface ("Z") = {ss[#ss[]-2]};
Printf("End");
