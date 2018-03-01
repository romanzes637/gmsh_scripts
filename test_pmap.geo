Include "macro_pmap.geo";

pmap_in = {
  5,
  1, 0,
  2, 1, 2, 
  9,
  3, 3, 4, 5,
  4, 6, 7, 8, 9,
  13,
  5, 10, 11, 12, 13, 14,
  6, 15, 16, 17, 18, 19, 20
};

pmap_in = {
  5,
  1, 0,
  2, 1, 2, 
  0, //9,
  //3, 3, 4, 5,
  //4, 6, 7, 8, 9,
  13,
  5, 10, 11, 12, 13, 14,
  6, 15, 16, 17, 18, 19, 20
};

pmap_in = {
  5,
  1, 0,
  2, 1, 2, 
  5, //9,
  3, 3, 4, 5,
  0, //4, 6, 7, 8, 9,
  13,
  5, 10, 11, 12, 13, 14,
  6, 15, 16, 17, 18, 19, 20
};

pmap_in = {
  0, //5,
  //1, 0,
  //2, 1, 2, 
  6, //9,
  //3, 3, 4, 5,
  4, 6, 7, 8, 9,
  13,
  5, 10, 11, 12, 13, 14,
  6, 15, 16, 17, 18, 19, 20
};

pmap_in = {
  0, //5,
  //1, 0,
  //2, 1, 2, 
  0, //9,
  //3, 3, 4, 5,
  //4, 6, 7, 8, 9,
  0 //13,
  //5, 10, 11, 12, 13, 14,
  //6, 15, 16, 17, 18, 19, 20
};

pmap_in = {
  0, //5,
  //1, 0,
  //2, 1, 2, 
  2, //9,
  0, //3, 3, 4, 5,
  0, //4, 6, 7, 8, 9,
  0 //13,
  //5, 10, 11, 12, 13, 14,
  //6, 15, 16, 17, 18, 19, 20
};

pmap_in_dim = 3;
pmap_map_dims = {3, 2};
pmap_map = {
  0, 1,
  1, 2,
  2, 3
};

Call pmap;

Printf("pmap_out length = %g", #pmap_out[]);
For i In {0 : #pmap_out[]-1}
  Printf("%g", pmap_out[i]);
EndFor

pns[] = Str(
  "Null",
  "One",
  "Two",
  "Three"
);

Printf("Number of physical names = %g", #pns[]);
For i In {0 : #pns[]-1}
  Printf(pns[i]);
  vs = {};
  start_idx = 0;
  For j In {0 : #pmap_out[]-1}
    If (j == start_idx)
      nvs = pmap_out[j+1];
      start_idx += 1+1+nvs;
      If (pmap_out[j] == i)
        For k In {j+2 : j+2+nvs-1}
          vs += pmap_out[k];
        EndFor // k
      EndIf
    EndIf
  EndFor // j
  For j In {0 : #vs[]-1}
    Printf("%g", vs[j]);
  EndFor // j
EndFor // i

