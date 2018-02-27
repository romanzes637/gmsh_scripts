Include "macro_cylitive.geo";

Macro borehole1

borehole1_bss = {};
borehole1_pvs = {};

cylitive_lcs = {1, 1, 1}; // Circumferential layers points characteristic length
cylitive_k = 0.3; // Inner hexahedron X, Y edge length / Radius
cylitive_rs = {0.281, 0.603, 0.650}; // Circumferential layers radii
/*cylitive_lvls = {0.553, 0.600, 0.922, 74.078, 74.400, 74.447, 75.000}; // Height layers levels*/
cylitive_lvls = {0.553, 0.600, 0.922, 74.078, 74.400, 74.447, 75.000}; // Height layers levels

cylitive_ox = borehole1_ox; cylitive_oy = borehole1_oy; cylitive_oz = borehole1_oz; // Origin: x, y, z (BOTTOM)
cylitive_rox = borehole1_ox; cylitive_roy = borehole1_oy; cylitive_roz = borehole1_oz; // Local Rotation Origin: x, y, z
cylitive_rax = borehole1_rax; cylitive_ray = borehole1_ray; cylitive_raz = borehole1_raz; // Local Rotation Angle: x, y, z

// Parameters
cylitive_t1 = 4; cylitive_t1t1 = 0; cylitive_t1t2 = 0; // Number of circumferential nodes, progression, bump
cylitive_t2s = {3, 3, 3}; // Number of radial nodes
cylitive_t2t1s = {0, 0, 0}; // Radial nodes progression
cylitive_t2t2s = {0, 0, 0}; // Radial nodes bump
cylitive_t3s = {5, 3, 3, 25, 3, 3, 5}; // Number of height nodes
cylitive_t3t1s = {0, 0, 0, 0, 0, 0, 0}; // Height nodes progression
cylitive_t3t2s = {0, 0, 0, 0.07, 0, 0, 0}; // Height nodes progression bump
cylitive_t4 = 0; // Hex (1) or tet (0) mesh?
cylitive_t5 = 3; // Create spherical shells (0 - not, 1 - bottom, 2 - top, 3 - top and bottom)?

borehole1_pvns[] = Str(
  "Matrix",
  "Container",
  "Fill",
  "Gap",
  "Environment"
);

borehole1_pvmap = {
  4, 4, 4,
  3, 3, 3,
  2, 2, 2,
  1, 1, 2,
  0, 1, 2,
  1, 1, 2,
  2, 2, 2,
  3, 3, 3,
  4, 4, 4
};

Call cylitive;

borehole1_bss = cylitive_bss[];

borehole1_new_tbl = 1;
borehole1_new_row = 0;
borehole1_row_cnt = 0;
borehole1_tbl_cnt = 0;
For borehole1_i In {0 : #cylitive_vs[]-1}
  If (borehole1_new_tbl > 0)
    borehole1_tbl_cnt += 1;
    tbl_len = cylitive_vs[borehole1_i];
    borehole1_tbl_vs = {};
    borehole1_new_tbl = 0;
    borehole1_new_row = 1;
    borehole1_row_cnt = 0;
  Else
    If(borehole1_new_row > 0)
      borehole1_row_len = cylitive_vs[borehole1_i];
      borehole1_row_vs = {};
      borehole1_row_cnt += 1;
      borehole1_new_row = 0;
    Else
      borehole1_row_vs += cylitive_vs[borehole1_i];
      If (#borehole1_row_vs[] == borehole1_row_len)
        borehole1_new_row = 1;
        borehole1_pvs += borehole1_pvmap[(borehole1_tbl_cnt-1)*#cylitive_rs[]+borehole1_row_cnt-1];
        borehole1_pvs += #borehole1_row_vs[];
        borehole1_pvs += borehole1_row_vs[];
      EndIf
    EndIf
    borehole1_tbl_vs += cylitive_vs[borehole1_i];
    If (#borehole1_tbl_vs[] == tbl_len)
      borehole1_new_tbl = 1;
    EndIf
  EndIf
EndFor // borehole1_i

Return

