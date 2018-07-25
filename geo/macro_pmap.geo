Macro pmap

pmap_out[] = {};

If (pmap_in_dim == 3 && #pmap_map_dims[] == 2) // scalar pmap_map[i][j] to array pmap_in[i][j][]
  pmap_new_tbl = 1;
  pmap_new_row = 0;
  pmap_row_cnt = 0;
  pmap_tbl_cnt = 0;
  For pmap_i In {0 : #pmap_in[]-1}
    If (pmap_new_tbl > 0)
      pmap_tbl_cnt += 1;
      pmap_row_cnt = 0;
      pmap_tbl_vs[] = {};
      pmap_tbl_len = pmap_in[pmap_i];
      If (pmap_tbl_len > 0)
        pmap_new_tbl = 0;
        pmap_new_row = 1;
      EndIf
    Else
      If (pmap_new_row > 0)
        pmap_row_cnt += 1;
        pmap_row_vs[] = {};
        pmap_row_len = pmap_in[pmap_i];
        If (pmap_row_len > 0)
          pmap_new_row = 0;
        EndIf
      Else
        pmap_row_vs[] += pmap_in[pmap_i];
        If (#pmap_row_vs[] == pmap_row_len)
          // Write the row to the corresponding physical zone from pmap_map
          pmap_out[] += pmap_map[(pmap_tbl_cnt-1)*pmap_map_dims[1]+pmap_row_cnt-1];
          pmap_out[] += #pmap_row_vs[];
          pmap_out[] += pmap_row_vs[];
          pmap_new_row = 1;
        EndIf
      EndIf
      pmap_tbl_vs[] += pmap_in[pmap_i];
      If (#pmap_tbl_vs[] == pmap_tbl_len)
        pmap_new_tbl = 1;
      EndIf
    EndIf
  EndFor // pmap_i
EndIf

Return

