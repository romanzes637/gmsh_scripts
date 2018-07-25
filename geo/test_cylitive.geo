Include "macro_cylitive.geo";

Geometry.AutoCoherence = 0;

cylitive_lcs = {0.1, 0.2, 0.3}; // Circumferential layers points characteristic length
cylitive_k = 0.3; // Inner hexahedron X, Y edge length / Radius
cylitive_rs = {1, 2, 3}; // Circumferential layers radii
cylitive_lvls = {1, 2, 3}; // Height layers levels

cylitive_ox = 1; cylitive_oy = -3; cylitive_oz = 4; // Origin: x, y, z (BOTTOM OF THE FIRST HEIGHT LAYER)
cylitive_rox = -3; cylitive_roy = 2; cylitive_roz = 5; // Local Rotation Origin: x, y, z
cylitive_rax = Pi/3; cylitive_ray = -Pi/6; cylitive_raz = Pi/4; // Local Rotation Angle: x, y, z

// Parameters
cylitive_t1 = 5; cylitive_t1t1 = 0; cylitive_t1t2 = 0; // Number of circumferential nodes, progression, bump
cylitive_t2s = {7, 8, 9}; // Number of radial nodes
cylitive_t2t1s = {1.1, 1.1, 1.1}; // Radial nodes progression
cylitive_t2t2s = {0, 0, 0}; // Radial nodes bump
cylitive_t3s = {5, 5, 5}; // Number of height nodes
cylitive_t3t1s = {0, 0, 0}; // Height nodes progression
cylitive_t3t2s = {0, 0, 0}; // Height nodes progression bump
cylitive_t4 = 0; // Hex (1) or tet (0) mesh?
cylitive_t5 = 3; // Create spherical shells (0 - not, 1 - bottom, 2 - top, 3 - top and bottom)?
cylitive_t6 = 1; // Full boundary surfaces?

Call cylitive;

// V
new_tbl = 1; new_row = 0; row_cnt = 0; tbl_cnt = 0;
For i In {0 : #cylitive_vs[]-1}
  If (new_tbl)
    tbl_cnt += 1;
    tbl_len = cylitive_vs[i];
    If (tbl_len)
      new_tbl = 0; tbl_vls = {}; new_row = 1; row_cnt = 0;
    EndIf
  Else
    If(new_row)
      row_cnt += 1;
      row_len = cylitive_vs[i];
      If (row_len)
        new_row = 0; row_vls = {};
      EndIf
    Else
      row_vls += cylitive_vs[i];
      If (#row_vls[] == row_len)
        new_row = 1;
        Physical Volume (Sprintf("V_%g_%g", tbl_cnt, row_cnt)) = {row_vls[]};
      EndIf
    EndIf
    tbl_vls += cylitive_vs[i];
    If (#tbl_vls[] == tbl_len)
      new_tbl = 1;
    EndIf
  EndIf
EndFor // i

/*// NZ*/
/*new_tbl = 1; new_row = 0; row_cnt = 0; tbl_cnt = 0;*/
/*For i In {0 : #cylitive_nzss[]-1}*/
/*  If (new_tbl)*/
/*    tbl_cnt += 1;*/
/*    tbl_len = cylitive_nzss[i];*/
/*    If (tbl_len)*/
/*      new_tbl = 0; tbl_vls = {}; new_row = 1; row_cnt = 0;*/
/*    EndIf*/
/*  Else*/
/*    If(new_row)*/
/*      row_cnt += 1;*/
/*      row_len = cylitive_nzss[i];*/
/*      If (row_len)*/
/*        new_row = 0; row_vls = {};*/
/*      EndIf*/
/*    Else*/
/*      row_vls += cylitive_nzss[i];*/
/*      If (#row_vls[] == row_len)*/
/*        new_row = 1;*/
/*        Physical Surface (Sprintf("NZ_%g_%g", tbl_cnt, row_cnt)) = {row_vls[]};*/
/*      EndIf*/
/*    EndIf*/
/*    tbl_vls += cylitive_nzss[i];*/
/*    If (#tbl_vls[] == tbl_len)*/
/*      new_tbl = 1;*/
/*    EndIf*/
/*  EndIf*/
/*EndFor // i*/

/*// Z*/
/*new_tbl = 1; new_row = 0; row_cnt = 0; tbl_cnt = 0;*/
/*For i In {0 : #cylitive_zss[]-1}*/
/*  If (new_tbl)*/
/*    tbl_cnt += 1;*/
/*    tbl_len = cylitive_zss[i];*/
/*    If (tbl_len)*/
/*      new_tbl = 0; tbl_vls = {}; new_row = 1; row_cnt = 0;*/
/*    EndIf*/
/*  Else*/
/*    If(new_row)*/
/*      row_cnt += 1;*/
/*      row_len = cylitive_zss[i];*/
/*      If (row_len)*/
/*        new_row = 0; row_vls = {};*/
/*      EndIf*/
/*    Else*/
/*      row_vls += cylitive_zss[i];*/
/*      If (#row_vls[] == row_len)*/
/*        new_row = 1;*/
/*        Physical Surface (Sprintf("Z_%g_%g", tbl_cnt, row_cnt)) = {row_vls[]};*/
/*      EndIf*/
/*    EndIf*/
/*    tbl_vls += cylitive_zss[i];*/
/*    If (#tbl_vls[] == tbl_len)*/
/*      new_tbl = 1;*/
/*    EndIf*/
/*  EndIf*/
/*EndFor // i*/

/*// L*/
/*new_tbl = 1; new_row = 0; row_cnt = 0; tbl_cnt = 0;*/
/*For i In {0 : #cylitive_lss[]-1}*/
/*  If (new_tbl)*/
/*    tbl_cnt += 1;*/
/*    tbl_len = cylitive_lss[i];*/
/*    If (tbl_len)*/
/*      new_tbl = 0; tbl_vls = {}; new_row = 1; row_cnt = 0;*/
/*    EndIf*/
/*  Else*/
/*    If(new_row)*/
/*      row_cnt += 1;*/
/*      row_len = cylitive_lss[i];*/
/*      If (row_len)*/
/*        new_row = 0; row_vls = {};*/
/*      EndIf*/
/*    Else*/
/*      row_vls += cylitive_lss[i];*/
/*      If (#row_vls[] == row_len)*/
/*        new_row = 1;*/
/*        Physical Surface (Sprintf("L_%g_%g", tbl_cnt, row_cnt)) = {row_vls[]};*/
/*      EndIf*/
/*    EndIf*/
/*    tbl_vls += cylitive_lss[i];*/
/*    If (#tbl_vls[] == tbl_len)*/
/*      new_tbl = 1;*/
/*    EndIf*/
/*  EndIf*/
/*EndFor // i*/

/*// I*/
/*new_tbl = 1; new_row = 0; row_cnt = 0; tbl_cnt = 0;*/
/*For i In {0 : #cylitive_iss[]-1}*/
/*  If (new_tbl)*/
/*    tbl_cnt += 1;*/
/*    tbl_len = cylitive_iss[i];*/
/*    If (tbl_len)*/
/*      new_tbl = 0; tbl_vls = {}; new_row = 1; row_cnt = 0;*/
/*    EndIf*/
/*  Else*/
/*    If(new_row)*/
/*      row_cnt += 1;*/
/*      row_len = cylitive_iss[i];*/
/*      If (row_len)*/
/*        new_row = 0; row_vls = {};*/
/*      EndIf*/
/*    Else*/
/*      row_vls += cylitive_iss[i];*/
/*      If (#row_vls[] == row_len)*/
/*        new_row = 1;*/
/*        Physical Surface (Sprintf("I_%g_%g", tbl_cnt, row_cnt)) = {row_vls[]};*/
/*      EndIf*/
/*    EndIf*/
/*    tbl_vls += cylitive_iss[i];*/
/*    If (#tbl_vls[] == tbl_len)*/
/*      new_tbl = 1;*/
/*    EndIf*/
/*  EndIf*/
/*EndFor // i*/

Physical Surface ("B") = {cylitive_bss[]};

Coherence;

