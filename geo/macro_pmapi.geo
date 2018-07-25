Macro pmapi

pmapi_out[] = {};
pmapi_start_idx = 0;
For pmapi_i In {0 : #pmapi_in[]-1}
  If (pmapi_i == pmapi_start_idx)
    pmapi_n = pmapi_in[pmapi_i+1];
    pmapi_start_idx += 1+1+pmapi_n;
/*    Printf("%g, %g, %g", pmapi_in[pmapi_i], pmapi_in[pmapi_i+1], pmapi_start_idx);*/
    If (pmapi_in[pmapi_i] == pmapi_idx)
      For pmapi_j In {pmapi_i+2 : pmapi_i+2+pmapi_n-1}
        pmapi_out[] += pmapi_in[pmapi_j];
      EndFor // pmapi_j
    EndIf
  EndIf
EndFor // pmapi_i

Return

