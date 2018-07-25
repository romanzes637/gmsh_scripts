Include "macro_pmap.geo";
Include "macro_pmapi.geo";

pmap_in[] = {
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

pmap_in[] = {
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

pmap_in[] = {
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

pmap_in[] = {
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

pmap_in[] = {
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

pmap_in[] = {
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

Printf("pmap_in length = %g", #pmap_in[]);
For i In {0 : #pmap_in[]-1}
  Printf("%g", pmap_in[i]);
EndFor

pmap_in_dim = 3;
Printf("pmap_in_dim = %g", pmap_in_dim);

pmap_map_dims[] = {3, 2};
Printf("pmap_map_dims length = %g", #pmap_map_dims[]);
For i In {0 : #pmap_map_dims[]-1}
  Printf("%g", pmap_map_dims[i]);
EndFor

pmap_map[] = {
  0, 1,
  1, 2,
  2, 3
};
Printf("pmap_map length = %g", #pmap_map[]);
For i In {0 : #pmap_map[]-1}
  Printf("%g", pmap_map[i]);
EndFor

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

pmapi_in[] = pmap_out[];
idcs[] = {0, 1, 2, 3};
For i In {0 : #idcs[]-1}
  Printf(pns[idcs[i]]);
  pmapi_idx = idcs[i];
  Call pmapi;
  For j In {0 : #pmapi_out[]-1}
    Printf("%g", pmapi_out[j]);
  EndFor
EndFor

