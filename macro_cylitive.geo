Include "macro_cylinder.geo";
Include "macro_hemisphere.geo";
Include "macro_cylshell.geo";
Include "macro_sphereshell.geo";

Macro cylitive

cylitive_nzss = {}; // 3D array
cylitive_zss = {}; // 3D array
cylitive_lss = {}; // 3D array
cylitive_iss = {}; // 3D array
cylitive_vs = {}; // 3D array
cylitive_bss = {}; // 1D array


// BOTTOM SHERICAL SHELL
If (cylitive_t5 == 1 || cylitive_t5 == 3)
  cylitive_nzss_i = {}; // 2D array
  cylitive_zss_i = {}; // 2D array
  cylitive_lss_i = {}; // 2D array
  cylitive_iss_i = {}; // 2D array
  cylitive_vs_i = {}; // 2D array
  // CORE
  hemisphere_lc = cylitive_lcs[0]; // Points characteristic length
  hemisphere_k = cylitive_k; // Inner hexahedron edge length / Radius
  hemisphere_r = cylitive_rs[0]; // Radius
  hemisphere_ox = cylitive_ox; hemisphere_oy = cylitive_oy; hemisphere_oz = cylitive_oz; // Origin: x, y, z
  hemisphere_rox = cylitive_rox; hemisphere_roy = cylitive_roy; hemisphere_roz = cylitive_roz; // Local Rotation Origin: x, y, z
  hemisphere_rax = cylitive_rax; hemisphere_ray = cylitive_ray; hemisphere_raz = cylitive_raz; // Local Rotation Angle: x, y, z
  // Parameters
  hemisphere_t_1 = cylitive_t1; hemisphere_t_1_1 = cylitive_t1t1; hemisphere_t_1_2 = cylitive_t1t2; // Number of circumferential nodes, progression, bump
  hemisphere_t_2 = cylitive_t2s[0]; hemisphere_t_2_1 = cylitive_t2t1s[0]; hemisphere_t_2_2 = cylitive_t2t2s[0]; // Number of radial nodes, progression, bump
  hemisphere_t_3 = cylitive_t1; hemisphere_t_3_1 = cylitive_t1t1; hemisphere_t_3_2 = cylitive_t1t2; // Number of height nodes, progression, bump
  hemisphere_t_4 = cylitive_t4; // Hex (1) or tet (0) mesh?
  hemisphere_t_5 = 0; // Up (1) or Down (0) part?
  Call hemisphere;
  cylitive_nzss_i += #hemisphere_nzss[];
  cylitive_nzss_i += hemisphere_nzss[];
  cylitive_zss_i += #hemisphere_zss[];
  cylitive_zss_i += hemisphere_zss[];
  cylitive_lss_i += #hemisphere_lss[];
  cylitive_lss_i += hemisphere_lss[];
  cylitive_iss_i += 0;
  cylitive_vs_i += #hemisphere_vs[];
  cylitive_vs_i += hemisphere_vs[];
  For cylitive_j In {1 : #cylitive_rs[]-1}
    sphereshell_lc = cylitive_lcs[cylitive_j]; // Points characteristic length
    sphereshell_r1 = cylitive_rs[cylitive_j-1]; // Inner radius
    sphereshell_r2 = cylitive_rs[cylitive_j]; // Outer radius
    sphereshell_ox = cylitive_ox; sphereshell_oy = cylitive_oy; sphereshell_oz = cylitive_oz; // Origin: x, y, z
    sphereshell_rox = cylitive_rox; sphereshell_roy = cylitive_roy; sphereshell_roz = cylitive_roz; // Local Rotation Origin: x, y, z
    sphereshell_rax = cylitive_rax; sphereshell_ray = cylitive_ray; sphereshell_raz = cylitive_raz; // Local Rotation Angle: x, y, z
    // Parameters
    sphereshell_t_1 = cylitive_t1; sphereshell_t_1_1 = cylitive_t1t1; sphereshell_t_1_2 = cylitive_t1t2; // Number of circumferential nodes, progression, bump
    sphereshell_t_2 = cylitive_t2s[cylitive_j]; sphereshell_t_2_1 = cylitive_t2t1s[cylitive_j]; sphereshell_t_2_2 = cylitive_t2t2s[cylitive_j]; // Number of radial nodes, progression, bump
    sphereshell_t_3 = cylitive_t1; sphereshell_t_3_1 = cylitive_t1t1; sphereshell_t_3_2 = cylitive_t1t2; // Number of height nodes, progression, bump
    sphereshell_t_4 = cylitive_t4; // Hex (1) or tet (0) mesh?
    sphereshell_t_5 = 0; // Up (1) or Down (0) part?
    Call sphereshell;
    cylitive_nzss_i += #sphereshell_nzss[];
    cylitive_nzss_i += sphereshell_nzss[];
    cylitive_zss_i += #sphereshell_zss[];
    cylitive_zss_i += sphereshell_zss[];
    cylitive_lss_i += #sphereshell_lss[];
    cylitive_lss_i += sphereshell_lss[];
    cylitive_iss_i += #sphereshell_iss[];
    cylitive_iss_i += sphereshell_iss[];
    cylitive_vs_i += #sphereshell_vs[];
    cylitive_vs_i += sphereshell_vs[];
  EndFor
  cylitive_nzss += #cylitive_nzss_i[];
  cylitive_nzss += cylitive_nzss_i[];
  cylitive_zss += #cylitive_zss_i[];
  cylitive_zss += cylitive_zss_i[];
  cylitive_lss += #cylitive_lss_i[];
  cylitive_lss += cylitive_lss_i[];
  cylitive_iss += #cylitive_iss_i[];
  cylitive_iss += cylitive_iss_i[];
  cylitive_vs += #cylitive_vs_i[];
  cylitive_vs += cylitive_vs_i[];
  If (#cylitive_rs[] > 1)
    cylitive_bss += sphereshell_lss[];
  Else
    cylitive_bss += hemisphere_lss[];
  EndIf
EndIf

// CYLINDER
For cylitive_i In {0 : #cylitive_lvls[]-1}
  cylitive_nzss_i = {}; // 2D array
  cylitive_zss_i = {}; // 2D array
  cylitive_lss_i = {}; // 2D array
  cylitive_iss_i = {}; // 2D array
  cylitive_vs_i = {}; // 2D array
  If (cylitive_i) // UPPER HEIGHT LEVELS
    cylitive_h_i = cylitive_lvls[cylitive_i]-cylitive_lvls[cylitive_i-1];
    cylitive_oz_i = cylitive_oz+cylitive_lvls[cylitive_i-1]+cylitive_h_i/2;
    cylitive_roz_i = cylitive_roz-cylitive_lvls[cylitive_i-1]-cylitive_h_i/2;
  Else // FIRST HEIGHT LEVEL
    cylitive_h_i = cylitive_lvls[cylitive_i];
    cylitive_oz_i = cylitive_oz+cylitive_h_i/2;
    cylitive_roz_i = cylitive_roz-cylitive_h_i/2;
  EndIf
  cylitive_t3s_i = cylitive_t3s[cylitive_i]; cylitive_t3t1s_i = cylitive_t3t1s[cylitive_i]; cylitive_t3t2s_i = cylitive_t3t2s[cylitive_i];
  // CORE
  cylinder_lc = cylitive_lcs[0]; // Points characteristic length
  cylinder_k = cylitive_k; // Inner hexahedron X, Y edge length / Radius
  cylinder_r = cylitive_rs[0]; // Radius
  cylinder_h = cylitive_h_i; // Height
  cylinder_ox = cylitive_ox; cylinder_oy = cylitive_oy; cylinder_oz = cylitive_oz_i; // Origin: x, y, z
  cylinder_rox = cylitive_rox; cylinder_roy = cylitive_roy; cylinder_roz = cylitive_roz_i; // Local Rotation Origin: x, y, z
  cylinder_rax = cylitive_rax; cylinder_ray = cylitive_ray; cylinder_raz = cylitive_raz; // Local Rotation Angle: x, y, z
  // Parameters
  cylinder_t_1 = cylitive_t1; cylinder_t_1_1 = cylitive_t1t1; cylinder_t_1_2 = cylitive_t1t2; // Number of circumferential nodes, progression, bump
  cylinder_t_2 = cylitive_t2s[0]; cylinder_t_2_1 = cylitive_t2t1s[0]; cylinder_t_2_2 = cylitive_t2t2s[0]; // Number of radial nodes, progression, bump
  cylinder_t_3 = cylitive_t3s_i; cylinder_t_3_1 = cylitive_t3t1s_i; cylinder_t_3_2 = cylitive_t3t2s_i; // Number of height nodes, progression, bump
  cylinder_t_4 = cylitive_t4; // Hex (1) or tet (0) mesh?
  Call cylinder;
  cylitive_nzss_i += #cylinder_nzss[];
  cylitive_nzss_i += cylinder_nzss[];
  cylitive_zss_i += #cylinder_zss[];
  cylitive_zss_i += cylinder_zss[];
  cylitive_lss_i += #cylinder_lss[];
  cylitive_lss_i += cylinder_lss[];
  cylitive_iss_i += 0;
  cylitive_vs_i += #cylinder_vs[];
  cylitive_vs_i += cylinder_vs[];
  If (cylitive_i == 0)
    If (cylitive_t5 == 0 || cylitive_t5 == 2)
      cylitive_bss += cylinder_nzss[];
    EndIf
  EndIf
  If (cylitive_i == #cylitive_lvls[]-1)
    If (cylitive_t5 == 0 || cylitive_t5 == 1)
      cylitive_bss += cylinder_zss[];
    EndIf
  EndIf
  // SHELLS
  For cylitive_j In {1 : #cylitive_rs[]-1}
    cylshell_lc = cylitive_lcs[cylitive_j]; // Points characteristic length
    cylshell_r1 = cylitive_rs[cylitive_j-1]; // Inner radius
    cylshell_r2 = cylitive_rs[cylitive_j]; // Outer radius
    cylshell_h = cylitive_h_i; // Height
    cylshell_ox = cylitive_ox; cylshell_oy = cylitive_oy; cylshell_oz = cylitive_oz_i; // Origin: x, y, z
    cylshell_rox = cylitive_rox; cylshell_roy = cylitive_roy; cylshell_roz = cylitive_roz_i; // Local Rotation Origin: x, y, z
    cylshell_rax = cylitive_rax; cylshell_ray = cylitive_ray; cylshell_raz = cylitive_raz; // Local Rotation Angle: x, y, z
    // Parameters
    cylshell_t_1 = cylitive_t1; cylshell_t_1_1 = cylitive_t1t1; cylshell_t_1_2 = cylitive_t1t2; // Number of circumferential nodes, progression, bump
    cylshell_t_2 = cylitive_t2s[cylitive_j]; cylshell_t_2_1 = cylitive_t2t1s[cylitive_j]; cylshell_t_2_2 = cylitive_t2t2s [cylitive_j]; // Number of radial nodes, progression, bump
    cylshell_t_3 = cylitive_t3s_i; cylshell_t_3_1 = cylitive_t3t1s_i; cylshell_t_3_2 = cylitive_t3t2s_i; // Number of height nodes, progression, bump
    cylshell_t_4 = cylitive_t4; // Hex (1) or tet (0) mesh?
    Call cylshell;
    cylitive_nzss_i += #cylshell_nzss[];
    cylitive_nzss_i += cylshell_nzss[];
    cylitive_zss_i += #cylshell_zss[];
    cylitive_zss_i += cylshell_zss[];
    cylitive_lss_i += #cylshell_lss[];
    cylitive_lss_i += cylshell_lss[];
    cylitive_iss_i += #cylshell_iss[];
    cylitive_iss_i += cylshell_iss[];
    cylitive_vs_i += #cylshell_vs[];
    cylitive_vs_i += cylshell_vs[];
    If (cylitive_i == 0)
      If (cylitive_t5 == 0 || cylitive_t5 == 2)
        cylitive_bss += cylshell_nzss[];
      EndIf
    EndIf
    If (cylitive_i == #cylitive_lvls[]-1)
      If (cylitive_t5 == 0 || cylitive_t5 == 1)
        cylitive_bss += cylshell_zss[];
      EndIf
    EndIf
  EndFor
  cylitive_nzss += #cylitive_nzss_i[];
  cylitive_nzss += cylitive_nzss_i[];
  cylitive_zss += #cylitive_zss_i[];
  cylitive_zss += cylitive_zss_i[];
  cylitive_lss += #cylitive_lss_i[];
  cylitive_lss += cylitive_lss_i[];
  cylitive_iss += #cylitive_iss_i[];
  cylitive_iss += cylitive_iss_i[];
  cylitive_vs += #cylitive_vs_i[];
  cylitive_vs += cylitive_vs_i[];
  If (#cylitive_rs[] > 1)
    cylitive_bss += cylshell_lss[];
  Else
    cylitive_bss += cylinder_lss[];
  EndIf
EndFor


// TOP SHERICAL SHELL
If (cylitive_t5 == 2 || cylitive_t5 == 3) 
  cylitive_nzss_i = {}; // 2D array
  cylitive_zss_i = {}; // 2D array
  cylitive_lss_i = {}; // 2D array
  cylitive_iss_i = {}; // 2D array
  cylitive_vs_i = {}; // 2D array
  // CORE
  hemisphere_lc = cylitive_lcs[0]; // Points characteristic length
  hemisphere_k = cylitive_k; // Inner hexahedron edge length / Radius
  hemisphere_r = cylitive_rs[0]; // Radius
  hemisphere_ox = cylitive_ox; hemisphere_oy = cylitive_oy; hemisphere_oz = cylitive_oz+cylitive_lvls[#cylitive_lvls[]-1]; // Origin: x, y, z
  hemisphere_rox = cylitive_rox; hemisphere_roy = cylitive_roy; hemisphere_roz = cylitive_roz-cylitive_lvls[#cylitive_lvls[]-1]; // Local Rotation Origin: x, y, z
  hemisphere_rax = cylitive_rax; hemisphere_ray = cylitive_ray; hemisphere_raz = cylitive_raz; // Local Rotation Angle: x, y, z
  // Parameters
  hemisphere_t_1 = cylitive_t1; hemisphere_t_1_1 = cylitive_t1t1; hemisphere_t_1_2 = cylitive_t1t2; // Number of circumferential nodes, progression, bump
  hemisphere_t_2 = cylitive_t2s[0]; hemisphere_t_2_1 = cylitive_t2t1s[0]; hemisphere_t_2_2 = cylitive_t2t2s[0]; // Number of radial nodes, progression, bump
  hemisphere_t_3 = cylitive_t1; hemisphere_t_3_1 = cylitive_t1t1; hemisphere_t_3_2 = cylitive_t1t2; // Number of height nodes, progression, bump
  hemisphere_t_4 = cylitive_t4; // Hex (1) or tet (0) mesh?
  hemisphere_t_5 = 1; // Up (1) or Down (0) part?
  Call hemisphere;
  cylitive_nzss_i += #hemisphere_nzss[];
  cylitive_nzss_i += hemisphere_nzss[];
  cylitive_zss_i += #hemisphere_zss[];
  cylitive_zss_i += hemisphere_zss[];
  cylitive_lss_i += #hemisphere_lss[];
  cylitive_lss_i += hemisphere_lss[];
  cylitive_iss_i += 0;
  cylitive_vs_i += #hemisphere_vs[];
  cylitive_vs_i += hemisphere_vs[];
  For cylitive_j In {1 : #cylitive_rs[]-1}
    sphereshell_lc = cylitive_lcs[cylitive_j]; // Points characteristic length
    sphereshell_r1 = cylitive_rs[cylitive_j-1]; // Inner radius
    sphereshell_r2 = cylitive_rs[cylitive_j]; // Outer radius
    sphereshell_ox = cylitive_ox; sphereshell_oy = cylitive_oy; sphereshell_oz = cylitive_oz+cylitive_lvls[#cylitive_lvls[]-1]; // Origin: x, y, z
    sphereshell_rox = cylitive_rox; sphereshell_roy = cylitive_roy; sphereshell_roz = cylitive_roz-cylitive_lvls[#cylitive_lvls[]-1]; // Local Rotation Origin: x, y, z
    sphereshell_rax = cylitive_rax; sphereshell_ray = cylitive_ray; sphereshell_raz = cylitive_raz; // Local Rotation Angle: x, y, z
    // Parameters
    sphereshell_t_1 = cylitive_t1; sphereshell_t_1_1 = cylitive_t1t1; sphereshell_t_1_2 = cylitive_t1t2; // Number of circumferential nodes, progression, bump
    sphereshell_t_2 = cylitive_t2s[cylitive_j]; sphereshell_t_2_1 = cylitive_t2t1s[cylitive_j]; sphereshell_t_2_2 = cylitive_t2t2s[cylitive_j]; // Number of radial nodes, progression, bump
    sphereshell_t_3 = cylitive_t1; sphereshell_t_3_1 = cylitive_t1t1; sphereshell_t_3_2 = cylitive_t1t2; // Number of height nodes, progression, bump
    sphereshell_t_4 = cylitive_t4; // Hex (1) or tet (0) mesh?
    sphereshell_t_5 = 1; // Up (1) or Down (0) part?
    Call sphereshell;
    cylitive_nzss_i += #sphereshell_nzss[];
    cylitive_nzss_i += sphereshell_nzss[];
    cylitive_zss_i += #sphereshell_zss[];
    cylitive_zss_i += sphereshell_zss[];
    cylitive_lss_i += #sphereshell_lss[];
    cylitive_lss_i += sphereshell_lss[];
    cylitive_iss_i += #sphereshell_iss[];
    cylitive_iss_i += sphereshell_iss[];
    cylitive_vs_i += #sphereshell_vs[];
    cylitive_vs_i += sphereshell_vs[];
  EndFor
  cylitive_nzss += #cylitive_nzss_i[];
  cylitive_nzss += cylitive_nzss_i[];
  cylitive_zss += #cylitive_zss_i[];
  cylitive_zss += cylitive_zss_i[];
  cylitive_lss += #cylitive_lss_i[];
  cylitive_lss += cylitive_lss_i[];
  cylitive_iss += #cylitive_iss_i[];
  cylitive_iss += cylitive_iss_i[];
  cylitive_vs += #cylitive_vs_i[];
  cylitive_vs += cylitive_vs_i[];
  If (#cylitive_rs[] > 1)
    cylitive_bss += sphereshell_lss[];
  Else
    cylitive_bss += hemisphere_lss[];
  EndIf
EndIf

Return

