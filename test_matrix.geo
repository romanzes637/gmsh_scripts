Include "macro_matrix.geo";

Geometry.AutoCoherence = 0;

matrix_x_starts = {-4,   -1,    0.5, 1.5,  3};
matrix_x_centers = {-2.5, -0.25, 1,   2.25, 4.5};
matrix_x_ends = {-1,   0.5,   1.5, 3,    6};
matrix_x_r = 1;

matrix_y_starts = {-4,   -1,    0.5, 1.5,  3};
matrix_y_centers = {-2.5, -0.25, 1,   2.25, 4.5};
matrix_y_ends = {-1,   0.5,   1.5, 3,    6};
matrix_y_r = 1;

matrix_z_starts = {-4.5, 0.5, 1.5};
matrix_z_centers = {-2,   1,   2};
matrix_z_ends = {0.5, 1.5,  2.5};
matrix_z_r = 1;

matrix_t_1s = {4, 3, 5, 3, 4}; matrix_t_1s_1s = {0, 0, 0, 0, 0}; matrix_t_1s_2s = {0, 0, 0, 0, 0};
matrix_t_2s = {4, 3, 5, 3, 4}; matrix_t_2s_1s = {0, 0, 0, 0, 0}; matrix_t_2s_2s = {0, 0, 0, 0, 0};
matrix_t_3s = {4, 3, 5, 3, 4}; matrix_t_3s_1s = {0, 0, 0, 0, 0}; matrix_t_3s_2s = {0, 0, 0, 0, 0};

matrix_lc = 1;
matrix_rox = 0; matrix_roy = 0; matrix_roz = 0;
matrix_rax = 0; matrix_ray = 0; matrix_raz = 0;
matrix_t_4 = 0;

//    NZ
//    NY
// NX    X
//    Y
//  LAYER1
//    NY
// NX    X
//    Y
//  LAYER2
//    NY
// NX    X
//    Y
//    Z
matrix_type_map = {
  0, 0, 9, 0, 0,
  0, 0, 5, 0, 0,
  8, 4, 1, 2, 6,
  0, 0, 3, 0, 0,
  0, 0, 7, 0, 0,
  
  0, 0, 9, 0, 0,
  0, 0, 5, 0, 0,
  8, 4, 1, 2, 6,
  0, 0, 3, 0, 0,
  0, 0, 7, 0, 0,
  
  0, 0, 9, 0, 0,
  0, 0, 5, 0, 0,
  8, 4, 1, 2, 6,
  0, 0, 3, 0, 0,
  0, 0, 7, 0, 0
};

dX = -1.5; dY = 0.2; dZ = -1;
originX = 0; originY = 0; originZ = 0;
angleX = Pi/18; angleY = 0; angleZ = 0;
For MatrixI In {0 : 32}
  primitive_t_9s_ro~{MatrixI} = {
    originX, originY, originZ, 
    originX, originY, originZ
  };
  primitive_t_9s_ra~{MatrixI} = {
    0, 0, 0, 
    angleX, angleY, angleZ
  };
  primitive_t_9s_d~{MatrixI} = {
    dX, dY, 0,
    0, 0, dZ
  };
EndFor


// 1, 2, 3,
// 4, 5, 6,
// 7, 8, 9,
// 10, 11, 12,
// 13, 14, 15,
// 16, 17, 18,
// 19, 20, 21,
// 22, 23, 24,
// 25, 26, 27
 matrix_deform_map = {
  0, 0, 11, 0, 0,
  0, 0, 14, 0, 0,
 13, 14, 14, 14, 15,
  0, 0, 14, 0, 0,
  0, 0, 17, 0, 0,
  
  0, 0, 11, 0, 0,
  0, 0, 14, 0, 0,
 13, 14, 14, 14, 15,
  0, 0, 14, 0, 0,
  0, 0, 17, 0, 0,
  
  0, 0, 11, 0, 0,
  0, 0, 14, 0, 0,
 13, 14, 14, 14, 15,
  0, 0, 14, 0, 0,
  0, 0, 17, 0, 0,

  0, 0, 2, 0, 0,
  0, 0, 5, 0, 0,
  4, 5, 5, 5, 6,
  0, 0, 5, 0, 0,
  0, 0, 8, 0, 0,
  
  0, 0, 11, 0, 0,
  0, 0, 14, 0, 0,
 13, 14, 14, 14, 15,
  0, 0, 14, 0, 0,
  0, 0, 17, 0, 0,
  
  0, 0, 20, 0, 0,
  0, 0, 23, 0, 0,
 22, 23, 23, 23, 24,
  0, 0, 23, 0, 0,
  0, 0, 26, 0, 0 
};


matrix_boundary_map = {
  0,   0, 433,   0,   0,
  0,   0, 443,   0,   0,
343, 443, 443, 443, 243,
  0,   0, 443,   0,   0,
  0,   0, 423,   0,   0,

  0,   0, 434,   0,   0,
  0,   0,   0,   0,   0,
344,   0,   0,   0, 244,
  0,   0,   0,   0,   0,
  0,   0, 424,   0,   0,

  0,   0, 432,   0,   0,
  0,   0, 442,   0,   0,
342, 442, 442, 442, 242,
  0,   0, 442,   0,   0,
  0,   0, 422,   0,   0
};

matrix_physical_map = {
  0, 0, 3, 0, 0,
  0, 0, 3, 0, 0,
  3, 3, 3, 3, 3,
  0, 0, 3, 0, 0,
  0, 0, 3, 0, 0,

  0, 0, 3, 0, 0,
  0, 0, 2, 0, 0,
  3, 2, 1, 2, 3,
  0, 0, 2, 0, 0,
  0, 0, 3, 0, 0,

  0, 0, 3, 0, 0,
  0, 0, 3, 0, 0,
  3, 3, 3, 3, 3,
  0, 0, 3, 0, 0,
  0, 0, 3, 0, 0
};

Call matrix;

pvns[] = Str("NONE", "A", "B", "C");
If(#matrix_pvs[] > 0)
  Printf("Global Physical Volumes = %g", #pvns[]);
  For pvnsi In {0 : #pvns[]-1}
    Printf(pvns[pvnsi]);
    vs = {};
    startIndex = 0;
    For pvsi In {0 : #matrix_pvs[]-1}
      If(pvsi == startIndex)
        nvs = matrix_pvs[pvsi+1];
        startIndex += 1 + nvs + 1;
        If(matrix_pvs[pvsi] == pvnsi)
          For pvsj In {pvsi+2 : pvsi+2+nvs-1}
            vs += matrix_pvs[pvsj];
          EndFor
        EndIf
      EndIf
    EndFor
    Physical Volume (Str(pvns[pvnsi])) = {vs[]};
  EndFor
EndIf

Physical Surface ("NX") = {matrix_nxss[]};
Physical Surface ("X") = {matrix_xss[]};
Physical Surface ("NY") = {matrix_nyss[]};
Physical Surface ("Y") = {matrix_yss[]};
Physical Surface ("NZ") = {matrix_nzss[]};
Physical Surface ("Z") = {matrix_zss[]};

bss = {};
bss += matrix_nxss[];
bss += matrix_xss[];
bss += matrix_nyss[];
bss += matrix_yss[];
bss += matrix_nzss[];
bss += matrix_zss[];

//Physical Surface ("BS") = {bss[]};

Coherence;
