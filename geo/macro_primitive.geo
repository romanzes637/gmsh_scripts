Macro primitive

// Points
primitive_ps[] = {};
For primitive_i In {0 : #primitive_lcs[]-1}
  primitive_ps[primitive_i] = newp;
  Point (primitive_ps[primitive_i]) = {
    primitive_xs[primitive_i],
    primitive_ys[primitive_i], 
    primitive_zs[primitive_i],
    primitive_lcs[primitive_i]
  };
EndFor // primitive_i

// Local Rotation and Translation
Rotate { {1, 0, 0}, {primitive_rox, primitive_roy, primitive_roz}, primitive_rax } { Point{ primitive_ps[] }; }
Rotate { {0, 1, 0}, {primitive_rox, primitive_roy, primitive_roz}, primitive_ray } { Point{ primitive_ps[] }; }
Rotate { {0, 0, 1}, {primitive_rox, primitive_roy, primitive_roz}, primitive_raz } { Point{ primitive_ps[] }; }
Translate {primitive_ox, primitive_oy, primitive_oz} { Point{ primitive_ps[] }; }
 
/* Global Rotation and Translation (primitive_t_9s parameter)
  primitive_t_9s - toggle array for points deformations, size = n_points*n_deformations
  Arrays:
  primitive_t_9s_ra_[point_idx] - Rotation Angles,
  primitive_t_9s_ro_[point_idx] - Rotation Origins coordinates,
  primitive_t_9s_d_[point_idx] - Displacement coordinates,
  must be declared.
  Arrays sizes = 3*N (X1, Y1, Z1, X2, Y2, Z2, ..., XN, YN, ZN),
  where N = n_deformations
*/
If (#primitive_t_9s[])
  For primitive_i In {0 : #primitive_lcs[]-1}
    For primitive_j In {0 : #primitive_t_9s[]/#primitive_lcs[]-1}
      If (primitive_t_9s[primitive_i + primitive_j*#primitive_lcs[]]) // If primitive_t_9s[point_index + deformation_index*n_points] > 0
        Rotate { {1, 0, 0}, {
            primitive_t_9s_ro~{primitive_i}[0+3*primitive_j], 
            primitive_t_9s_ro~{primitive_i}[1+3*primitive_j],
            primitive_t_9s_ro~{primitive_i}[2+3*primitive_j]
          },
          primitive_t_9s_ra~{primitive_i}[0+3*primitive_j] 
        } { Point{ primitive_ps[primitive_i] }; }
        Rotate { {0, 1, 0}, {
            primitive_t_9s_ro~{primitive_i}[0+3*primitive_j], 
            primitive_t_9s_ro~{primitive_i}[1+3*primitive_j],
            primitive_t_9s_ro~{primitive_i}[2+3*primitive_j]
          },
          primitive_t_9s_ra~{primitive_i}[1+3*primitive_j] 
        } { Point{ primitive_ps[primitive_i] }; }
        Rotate { {0, 0, 1}, {
            primitive_t_9s_ro~{primitive_i}[0+3*primitive_j], 
            primitive_t_9s_ro~{primitive_i}[1+3*primitive_j],
            primitive_t_9s_ro~{primitive_i}[2+3*primitive_j]
          },
          primitive_t_9s_ra~{primitive_i}[2+3*primitive_j]
        } { Point{ primitive_ps[primitive_i] }; }
        Translate {
          primitive_t_9s_d~{primitive_i}[0+3*primitive_j], 
          primitive_t_9s_d~{primitive_i}[1+3*primitive_j], 
          primitive_t_9s_d~{primitive_i}[2+3*primitive_j]
        } { Point{ primitive_ps[primitive_i] }; }
      EndIf
    EndFor // primitive_j
  EndFor // primitive_i
EndIf

// Lines
primitive_ls[] = {};
// Map for each line: startPoint, endPoint, circleCenterPoint, ellipseShiftPoint
primitive_ps_to_ls[] = {
  // X Lines Counterclockwise
  1, 0, 8, 20,
  5, 4 ,9, 21,
  6, 7, 10, 22,
  2, 3, 11, 23,
  // Y Lines Counterclockwise
  3, 0, 12, 24,
  2, 1, 13, 25,
  6, 5, 14, 26,
  7, 4, 15, 27,
  // Z Lines Counterclockwise
  0, 4 ,16, 28,
  1, 5, 17, 29,
  2, 6, 18, 30,
  3, 7, 19, 31 
};
For primitive_i In {0 : 11}
  primitive_ls[primitive_i] = newl;
  If (primitive_t_5s[primitive_i] == 0)
    Line (primitive_ls[primitive_i]) = {
      primitive_ps[primitive_ps_to_ls[primitive_i*4]], 
      primitive_ps[primitive_ps_to_ls[primitive_i*4+1]]
    };
  ElseIf (primitive_t_5s[primitive_i] == 1)
    Circle (primitive_ls[primitive_i]) = {
      primitive_ps[primitive_ps_to_ls[primitive_i*4]], 
      primitive_ps[primitive_ps_to_ls[primitive_i*4+2]], 
      primitive_ps[primitive_ps_to_ls[primitive_i*4+1]]
    };
  ElseIf (primitive_t_5s[primitive_i] == 2)
    Ellipse (primitive_ls[primitive_i]) = {
      primitive_ps[primitive_ps_to_ls[primitive_i*4]],
      primitive_ps[primitive_ps_to_ls[primitive_i*4+2]], 
//      primitive_ps[primitive_ps_to_ls[primitive_i*4+3]], FIXME WORKAROUND FOR OPENCASCADE KERNEL
      primitive_ps[primitive_ps_to_ls[primitive_i*4+1]]
    };
  ElseIf (primitive_t_5s[primitive_i] > 2)
    /* Curve points
      Arrays:
      primitive_t_5s_lcs_[line_index] - points Characteristic Lengths,
      primitive_t_5s_xs_[line_index] - points X coordinates,
      primitive_t_5s_ys_[line_index] - points Y coordinates,
      primitive_t_5s_zs_[line_index] - points Z coordinates,
      must be declared.
    */
    primitive_curve_points[] = {};
    For primitive_j In {0 : #primitive_t_5s_lcs~{primitive_i}[]-1}
     primitive_curve_points[] += newp;
     Point (primitive_curve_points[primitive_j]) = {
       primitive_t_5s_xs~{primitive_i}[primitive_j], 
       primitive_t_5s_ys~{primitive_i}[primitive_j], 
       primitive_t_5s_zs~{primitive_i}[primitive_j], 
       primitive_t_5s_lcs~{primitive_i}[primitive_j]
     };
    EndFor // primitive_j
//    Printf(Sprintf("%g", #primitive_curve_points[]));
//    For primitive_j In {0 : #primitive_curve_points[]-1}
//      Printf(Sprintf("%g", primitive_curve_points[primitive_j]));
//    EndFor

    // Local Rotation and Translation
    Rotate { {1, 0, 0}, {primitive_rox, primitive_roy, primitive_roz}, primitive_rax } { Point{ primitive_curve_points[] }; }
    Rotate { {0, 1, 0}, {primitive_rox, primitive_roy, primitive_roz}, primitive_ray } { Point{ primitive_curve_points[] }; }
    Rotate { {0, 0, 1}, {primitive_rox, primitive_roy, primitive_roz}, primitive_raz } { Point{ primitive_curve_points[] }; }
    Translate {primitive_ox, primitive_oy, primitive_oz} { Point{ primitive_curve_points[] }; }

    // TODO Global Rotation and Translation

    If (primitive_t_5s[primitive_i] == 3) // OpenCASCADE Max Bezier points = 26
      Bezier (primitive_ls[primitive_i]) = {
        primitive_ps[primitive_ps_to_ls[primitive_i*4]], 
        primitive_curve_points[], 
        primitive_ps[primitive_ps_to_ls[primitive_i*4+1]]
      };
    ElseIf (primitive_t_5s[primitive_i] == 4) // Only Built-in kernel
      BSpline (primitive_ls[primitive_i]) = {
        primitive_ps[primitive_ps_to_ls[primitive_i*4]], 
        primitive_curve_points[], 
        primitive_ps[primitive_ps_to_ls[primitive_i*4+1]]
      };
    ElseIf (primitive_t_5s[primitive_i] > 4)
      Spline (primitive_ls[primitive_i]) = {
        primitive_ps[primitive_ps_to_ls[primitive_i*4]], 
        primitive_curve_points[], 
        primitive_ps[primitive_ps_to_ls[primitive_i*4+1]]
      };
    EndIf
  EndIf
EndFor // primitive_i

// Line Loops
primitive_lls[] = {};
primitive_lls[0] = newll; // NX
Line Loop (primitive_lls[0]) = {primitive_ls[5], primitive_ls[9], -primitive_ls[6], -primitive_ls[10]};
primitive_lls[1] = newll; // X
Line Loop (primitive_lls[1]) = {-primitive_ls[4], primitive_ls[11], primitive_ls[7], -primitive_ls[8]};
primitive_lls[2] = newll; // NY
Line Loop (primitive_lls[2]) = {-primitive_ls[3], primitive_ls[10], primitive_ls[2], -primitive_ls[11]};
primitive_lls[3] = newll; // Y
Line Loop (primitive_lls[3]) = {primitive_ls[0], primitive_ls[8], -primitive_ls[1], -primitive_ls[9]};
primitive_lls[4] = newll; // NZ
Line Loop (primitive_lls[4]) = {-primitive_ls[0], -primitive_ls[5], primitive_ls[3], primitive_ls[4]};
primitive_lls[5] = newll; // Z
Line Loop (primitive_lls[5]) = {primitive_ls[1], -primitive_ls[7], -primitive_ls[2], primitive_ls[6]};

// Surfaces
primitive_ss[] = {};
primitive_is_surface_changed = 0;
For primitive_i In {0 : #primitive_lls[]-1}
  If (!primitive_t_8s[primitive_i])
    primitive_ss[] += news;
    If (!primitive_t_10s[primitive_i])
      Surface (news) = {primitive_lls[primitive_i]};
    Else
      Plane Surface (news) = {primitive_lls[primitive_i]};
    EndIf
    If (primitive_t_4)
      Recombine Surface {primitive_ss[#primitive_ss[]-1]};
    EndIf
  Else
   // Array with name primitive_t_8s_[surface_index] must be declared
   primitive_ss[] += primitive_t_8s~{primitive_i}[];
   primitive_is_surface_changed = 1;
  EndIf
EndFor // primitive_i

// Surface Loops
primitive_sls[] = {};
primitive_sls[0] = newsl;
Surface Loop (primitive_sls[0]) = {primitive_ss[]};
If (#primitive_t_7s[])
  primitive_sls[1] = newsl;
  Surface Loop (primitive_sls[1]) = {primitive_t_7s[]};
EndIf

// Volumes
primitive_vs[] = {};
primitive_vs[0] += newv;
If (!#primitive_t_7s[])
  Volume (primitive_vs[0]) = {primitive_sls[0]};
Else
  Volume (primitive_vs[0]) = {primitive_sls[0], primitive_sls[1]};
EndIf


// FIXME WORKAROUND OpenCASCADE bug (duplicate surfaces while volume ctreation)
BooleanFragments{ Surface{primitive_ss[], primitive_t_7s[]}; Delete; }{ Volume{primitive_vs[]}; Delete; }
//primitive_ss[] = Unique(Abs(Boundary{ Volume{primitive_vs[]}; }));
//primitive_ps[] = Unique(Abs(Boundary{ Line{primitive_ls[]}; }));
//primitive_ls[] = Unique(Abs(Boundary{ Surface{primitive_ss[]}; }));

// Transfinite
If (primitive_t_1 || primitive_t_2 || primitive_t_3)
  primitive_ls[] = Unique(Abs(Boundary{ Surface{primitive_ss[]}; })); // New ls
  // Sorting as built-in array
  primitive_ls_1[] = {};
  primitive_ls_2[] = {};
  primitive_ls_3[] = {};
  For primitive_i In {0 : #primitive_ls[]-1}
    // Printf(Sprintf("%g", primitive_ls[primitive_i]));
    primitive_l_ps[] = Boundary{ Line{primitive_ls[primitive_i]}; };
    // Printf(Sprintf("%g, %g", primitive_l_ps[0], primitive_l_ps[1]));
    If (
      primitive_l_ps[0] == primitive_ps[0]+1 && primitive_l_ps[1] == primitive_ps[0] ||
      primitive_l_ps[0] == primitive_ps[0]+2 && primitive_l_ps[1] == primitive_ps[0]+3 ||
      primitive_l_ps[0] == primitive_ps[0]+5 && primitive_l_ps[1] == primitive_ps[0]+4 ||
      primitive_l_ps[0] == primitive_ps[0]+6 && primitive_l_ps[1] == primitive_ps[0]+7
      )
      primitive_ls_1[] += primitive_ls[primitive_i];
    ElseIf (
      primitive_l_ps[0] == primitive_ps[0]+3 && primitive_l_ps[1] == primitive_ps[0] ||
      primitive_l_ps[0] == primitive_ps[0]+2 && primitive_l_ps[1] == primitive_ps[0]+1 ||
      primitive_l_ps[0] == primitive_ps[0]+6 && primitive_l_ps[1] == primitive_ps[0]+5 ||
      primitive_l_ps[0] == primitive_ps[0]+7 && primitive_l_ps[1] == primitive_ps[0]+4
      )
      primitive_ls_2[] += primitive_ls[primitive_i];
    Else
      primitive_ls_3[] += primitive_ls[primitive_i];
    EndIf
  EndFor
  primitive_ls[] = {};
  primitive_ls[] += primitive_ls_1[];
  primitive_ls[] += primitive_ls_2[];
  primitive_ls[] += primitive_ls_3[];
  // Printf("New");
  For primitive_i In {0 : #primitive_ls[]-1}
  // Printf(Sprintf("%g", primitive_ls[primitive_i]));
  EndFor
  // Lines
  If (primitive_t_1)
    For primitive_i In {0 : 3}
      If (primitive_t_1_1)
        Transfinite Line primitive_ls[primitive_i] = primitive_t_1 Using Progression primitive_t_1_1;
      ElseIf (primitive_t_1_2)
        Transfinite Line primitive_ls[primitive_i] = primitive_t_1 Using Bump primitive_t_1_2;
      Else
        Transfinite Line primitive_ls[primitive_i] = primitive_t_1;
      EndIf
    EndFor
  EndIf
  If (primitive_t_2)
    For primitive_i In {4 : 7}
      If (primitive_t_2_1)
        Transfinite Line primitive_ls[primitive_i] = primitive_t_2 Using Progression primitive_t_2_1;
      ElseIf (primitive_t_2_2)
        Transfinite Line primitive_ls[primitive_i] = primitive_t_2 Using Bump primitive_t_2_2;
      Else
        Transfinite Line primitive_ls[primitive_i] = primitive_t_2;
      EndIf
    EndFor
  EndIf
  If (primitive_t_3)
    For primitive_i In {8 : 11}
      If (primitive_t_3_1)
        Transfinite Line primitive_ls[primitive_i] = primitive_t_3 Using Progression primitive_t_3_1;
      ElseIf (primitive_t_3_2)
        Transfinite Line primitive_ls[primitive_i] = primitive_t_3 Using Bump primitive_t_3_2;
      Else
        Transfinite Line primitive_ls[primitive_i] = primitive_t_3;
      EndIf
    EndFor
  EndIf
  // Surfaces
  If (primitive_t_1 && primitive_t_2 && primitive_t_3 && !primitive_is_surface_changed)
    If (primitive_t_6 == 0)
      Transfinite Surface {primitive_ss[0]} = {primitive_ps[2], primitive_ps[1], primitive_ps[5], primitive_ps[6]} Right;
      Transfinite Surface {primitive_ss[1]} = {primitive_ps[0], primitive_ps[3], primitive_ps[7], primitive_ps[4]};
      Transfinite Surface {primitive_ss[2]} = {primitive_ps[3], primitive_ps[2], primitive_ps[6], primitive_ps[7]};
      Transfinite Surface {primitive_ss[3]} = {primitive_ps[1], primitive_ps[0], primitive_ps[4], primitive_ps[5]} Right;
      Transfinite Surface {primitive_ss[4]} = {primitive_ps[0], primitive_ps[1], primitive_ps[2], primitive_ps[3]};
      Transfinite Surface {primitive_ss[5]} = {primitive_ps[5], primitive_ps[4], primitive_ps[7], primitive_ps[6]} Right;
    ElseIf (primitive_t_6 == 1)
      Transfinite Surface {primitive_ss[0]} = {primitive_ps[2], primitive_ps[1], primitive_ps[5], primitive_ps[6]} Right;
      Transfinite Surface {primitive_ss[1]} = {primitive_ps[0], primitive_ps[3], primitive_ps[7], primitive_ps[4]};
      Transfinite Surface {primitive_ss[2]} = {primitive_ps[3], primitive_ps[2], primitive_ps[6], primitive_ps[7]} Right;
      Transfinite Surface {primitive_ss[3]} = {primitive_ps[1], primitive_ps[0], primitive_ps[4], primitive_ps[5]};
      Transfinite Surface {primitive_ss[4]} = {primitive_ps[0], primitive_ps[1], primitive_ps[2], primitive_ps[3]} Right;
      Transfinite Surface {primitive_ss[5]} = {primitive_ps[5], primitive_ps[4], primitive_ps[7], primitive_ps[6]};
    ElseIf (primitive_t_6 == 2)
      Transfinite Surface {primitive_ss[0]} = {primitive_ps[2], primitive_ps[1], primitive_ps[5], primitive_ps[6]};
      Transfinite Surface {primitive_ss[1]} = {primitive_ps[0], primitive_ps[3], primitive_ps[7], primitive_ps[4]} Right;
      Transfinite Surface {primitive_ss[2]} = {primitive_ps[3], primitive_ps[2], primitive_ps[6], primitive_ps[7]} Right;
      Transfinite Surface {primitive_ss[3]} = {primitive_ps[1], primitive_ps[0], primitive_ps[4], primitive_ps[5]};
      Transfinite Surface {primitive_ss[4]} = {primitive_ps[0], primitive_ps[1], primitive_ps[2], primitive_ps[3]};
      Transfinite Surface {primitive_ss[5]} = {primitive_ps[5], primitive_ps[4], primitive_ps[7], primitive_ps[6]} Right;
    Else
      Transfinite Surface {primitive_ss[0]} = {primitive_ps[2], primitive_ps[1], primitive_ps[5], primitive_ps[6]};
      Transfinite Surface {primitive_ss[1]} = {primitive_ps[0], primitive_ps[3], primitive_ps[7], primitive_ps[4]} Right;
      Transfinite Surface {primitive_ss[2]} = {primitive_ps[3], primitive_ps[2], primitive_ps[6], primitive_ps[7]};
      Transfinite Surface {primitive_ss[3]} = {primitive_ps[1], primitive_ps[0], primitive_ps[4], primitive_ps[5]} Right;
      Transfinite Surface {primitive_ss[4]} = {primitive_ps[0], primitive_ps[1], primitive_ps[2], primitive_ps[3]} Right;
      Transfinite Surface {primitive_ss[5]} = {primitive_ps[5], primitive_ps[4], primitive_ps[7], primitive_ps[6]};
    EndIf
  EndIf
  // Volume
  If (primitive_t_1 && primitive_t_2 && primitive_t_3 && !#primitive_t_7s[] && !primitive_is_surface_changed)
    If (primitive_t_6 == 0)
      Transfinite Volume {primitive_vs[0]} = {
        primitive_ps[0], primitive_ps[1], primitive_ps[2], primitive_ps[3],
        primitive_ps[4], primitive_ps[5], primitive_ps[6], primitive_ps[7]
      };
    ElseIf (primitive_t_6 == 1)
      Transfinite Volume {primitive_vs[0]} = {
        primitive_ps[1], primitive_ps[2], primitive_ps[3], primitive_ps[0], 
        primitive_ps[5], primitive_ps[6], primitive_ps[7], primitive_ps[4]
      };
    ElseIf (primitive_t_6 == 2)
      Transfinite Volume {primitive_vs[0]} = {
        primitive_ps[2], primitive_ps[3], primitive_ps[0], primitive_ps[1],
        primitive_ps[6], primitive_ps[7], primitive_ps[4], primitive_ps[5]
      };
    Else
      Transfinite Volume {primitive_vs[0]} = {
        primitive_ps[3], primitive_ps[0], primitive_ps[1], primitive_ps[2],
        primitive_ps[7], primitive_ps[4], primitive_ps[5], primitive_ps[6]
      };
    EndIf
    If (primitive_t_4) // TODO Algorithm doesn't work
      TransfQuadTri {primitive_vs[0]};
    EndIf
  EndIf
EndIf

Return
