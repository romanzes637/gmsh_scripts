Include "macro_cylitive.geo";
Include "macro_pmap.geo";

Macro borehole2

borehole2_bss = {};
borehole2_pvs = {};
borehole2_lvl = borehole2_oz;




// Bottom
Printf("Container %g", 1);
cylitive_lcs = {
  1, 1, 1, 1, 1, 1, 1, 
  1, 1, 1, 1,
  1, 1, 1, 1,
  1, 1, 1, 1, 1, 1,
  1
}; // Circumferential layers points characteristic length
cylitive_k = 1/3; // Inner hexahedron X, Y edge length / Radius
cylitive_rs = {
  0.120, 0.124, 0.130, 0.135, 0.140, 0.145, 0.150,
  0.2835, 0.2875, 0.309, 0.315, 
  0.326, 0.332, 0.340, 0.343, 
  0.532, 0.535, 0.555, 0.575, 0.595, 0.600, 
  0.650
}; // Circumferential layers radii
cylitive_lvls = {
  0.500,
  0.547,

  0.552, 
  0.802, 
  0.817,
  0.827, 0.907, 0.917,
  0.921, 1.712, 1.829, 1.833, 1.912, 1.917,
  1.921, 2.712, 2.829, 2.833, 2.912, 2.917,
  2.921, 3.712, 3.829, 3.833, 3.912, 3.917,
  4.127, 4.132, 4.211, 4.217,
  4.232, 4.307, 4.322,
  4.572, 
  4.577
}; // Height layers levels
cylitive_ox = borehole2_ox; cylitive_oy = borehole2_oy; cylitive_oz = borehole2_oz; // Origin: x, y, z (BOTTOM)
cylitive_rox = borehole2_ox; cylitive_roy = borehole2_oy; cylitive_roz = borehole2_oz; // Local Rotation Origin: x, y, z
cylitive_rax = borehole2_rax; cylitive_ray = borehole2_ray; cylitive_raz = borehole2_raz; // Local Rotation Angle: x, y, z
// Parameters
cylitive_t1 = borehole2_t1; cylitive_t1t1 = 0; cylitive_t1t2 = 0; // Number of circumferential nodes, progression, bump
cylitive_t2s = borehole2_t2s[]; // Number of radial nodes
cylitive_t2t1s = borehole2_t2t1s[]; // Radial nodes progression
cylitive_t2t2s = borehole2_t2t2s[]; // Radial nodes bump
cylitive_t3s = {
  borehole2_t3s[0], // Bottom Gap
  borehole2_t3s[1], // Isolation Container ring

  borehole2_t3s[2], // Isolation Container bottom     
  borehole2_t3s[3], // Bentonite bottom 
  borehole2_t3s[4], // Transport Container bottom
  borehole2_t3s[5], borehole2_t3s[6], borehole2_t3s[7], // Mayak Container bottom, anticap height, anticap width
  borehole2_t3s[8], borehole2_t3s[9], borehole2_t3s[10], borehole2_t3s[11], borehole2_t3s[12], borehole2_t3s[13], // Can bottom, matrix, void, top, cap height, cap width
  borehole2_t3s[14], borehole2_t3s[15], borehole2_t3s[16], borehole2_t3s[17], borehole2_t3s[18], borehole2_t3s[19], // Can bottom, matrix, void, top, cap height, cap width
  borehole2_t3s[20], borehole2_t3s[21], borehole2_t3s[22], borehole2_t3s[23], borehole2_t3s[24], borehole2_t3s[25], // Can bottom, matrix, void, top, cap height, cap width
  borehole2_t3s[26], borehole2_t3s[27], borehole2_t3s[28], borehole2_t3s[29], // Mayak Container void, top, cap height, cap width
  borehole2_t3s[30], borehole2_t3s[31], borehole2_t3s[32], // Transport Container top, cap height, cap width
  borehole2_t3s[33], // Bentonite top
  borehole2_t3s[34] // Isolation Container top

//  3, // Isolation Container cap height
//  3, // Isolation Container cap width
//  3, // Fill between Isolation Containers

//  3, // Isolation Container cap height 
//  3, // Isolation Container cap width
//  3 // Top Gap height
}; // Number of height nodes
cylitive_t3t1s = {
  borehole2_t3t1s[0], // Bottom Gap
  borehole2_t3t1s[1], // Isolation Container ring
  borehole2_t3t1s[2], // Isolation Container bottom     
  borehole2_t3t1s[3], // Bentonite bottom 
  borehole2_t3t1s[4], // Transport Container bottom
  borehole2_t3t1s[5], borehole2_t3t1s[6], borehole2_t3t1s[7], // Mayak Container bottom, anticap height, anticap width
  borehole2_t3t1s[8], borehole2_t3t1s[9], borehole2_t3t1s[10], borehole2_t3t1s[11], borehole2_t3t1s[12], borehole2_t3t1s[13], // Can bottom, matrix, void, top, cap height, cap width
  borehole2_t3t1s[14], borehole2_t3t1s[15], borehole2_t3t1s[16], borehole2_t3t1s[17], borehole2_t3t1s[18], borehole2_t3t1s[19], // Can bottom, matrix, void, top, cap height, cap width
  borehole2_t3t1s[20], borehole2_t3t1s[21], borehole2_t3t1s[22], borehole2_t3t1s[23], borehole2_t3t1s[24], borehole2_t3t1s[25], // Can bottom, matrix, void, top, cap height, cap width
  borehole2_t3t1s[26], borehole2_t3t1s[27], borehole2_t3t1s[28], borehole2_t3t1s[29], // Mayak Container void, top, cap height, cap width
  borehole2_t3t1s[30], borehole2_t3t1s[31], borehole2_t3t1s[32], // Transport Container top, cap height, cap width
  borehole2_t3t1s[33], // Bentonite top
  borehole2_t3t1s[34] // Isolation Container top
//  3, // Isolation Container cap height
//  3, // Isolation Container cap width
//  3, // Fill between Isolation Containers
//  3, // Isolation Container cap height 
//  3, // Isolation Container cap width
//  3 // Top Gap height
}; // Height nodes progression
cylitive_t3t2s = {
  borehole2_t3t2s[0], // Bottom Gap
  borehole2_t3t2s[1], // Isolation Container ring
  borehole2_t3t2s[2], // Isolation Container bottom     
  borehole2_t3t2s[3], // Bentonite bottom 
  borehole2_t3t2s[4], // Transport Container bottom
  borehole2_t3t2s[5], borehole2_t3t2s[6], borehole2_t3t2s[7], // Mayak Container bottom, anticap height, anticap width
  borehole2_t3t2s[8], borehole2_t3t2s[9], borehole2_t3t2s[10], borehole2_t3t2s[11], borehole2_t3t2s[12], borehole2_t3t2s[13], // Can bottom, matrix, void, top, cap height, cap width
  borehole2_t3t2s[14], borehole2_t3t2s[15], borehole2_t3t2s[16], borehole2_t3t2s[17], borehole2_t3t2s[18], borehole2_t3t2s[19], // Can bottom, matrix, void, top, cap height, cap width
  borehole2_t3t2s[20], borehole2_t3t2s[21], borehole2_t3t2s[22], borehole2_t3t2s[23], borehole2_t3t2s[24], borehole2_t3t2s[25], // Can bottom, matrix, void, top, cap height, cap width
  borehole2_t3t2s[26], borehole2_t3t2s[27], borehole2_t3t2s[28], borehole2_t3t2s[29], // Mayak Container void, top, cap height, cap width
  borehole2_t3t2s[30], borehole2_t3t2s[31], borehole2_t3t2s[32], // Transport Container top, cap height, cap width
  borehole2_t3t2s[33], // Bentonite top
  borehole2_t3t2s[34] // Isolation Container top
//  3, // Isolation Container cap height
//  3, // Isolation Container cap width
//  3, // Fill between Isolation Containers
//  3, // Isolation Container cap height 
//  3, // Isolation Container cap width
//  3 // Top Gap height
}; // Height nodes progression bump
cylitive_t4 = 0; // Hex (1) or tet (0) mesh?
cylitive_t5 = 1; // Create spherical shells (0 - not, 1 - bottom, 2 - top, 3 - top and bottom)?
cylitive_t6 = 0; // Full boundary surfaces?
Call cylitive;
borehole2_bss += cylitive_bss[];
pmap_in = cylitive_vs[];
pmap_in_dim = 3;
pmap_map_dims = {
  1+#cylitive_lvls[], // bottom spherical shell + levels
  #cylitive_rs[]
};
pmap_map = { // Written from the bottom to top spherical shell vertically down, from the center to lateral surface horizontally right
 14,14,14,14,14,14,14,14,14,14,14,14,14,14,14,14,14,14,14,14,14,14,
 13,13,13,13,13,13,13,13,13,13,13,13,13,13,13,13,13,13,13,13,13,13,
  7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 4, 7, 7, 7,
  4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 7,
  5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 4, 5, 4, 6, 6, 6, 4, 7,
  3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3,11, 4, 5, 4, 6, 6, 6, 4, 7,
 10,10,10,10,10,10, 2, 2, 2, 2, 2,10, 3,11, 4, 5, 4, 6, 6, 6, 4, 7,
 10,10,10,10,10,10, 2, 9, 9, 9, 2,10, 3,11, 4, 5, 4, 6, 6, 6, 4, 7,
  2, 2, 2, 2, 2, 2, 2, 9, 9, 9, 2,10, 3,11, 4, 5, 4, 6, 6, 6, 4, 7,
  1, 1, 1, 1, 1, 1, 1, 1, 1, 9, 2,10, 3,11, 4, 5, 4, 6, 6, 6, 4, 7,
  0, 0, 0, 0, 0, 0, 0, 0, 1, 9, 2,10, 3,11, 4, 5, 4, 6, 6, 6, 4, 7,
  8, 8, 8, 8, 8, 8, 8, 8, 1, 9, 2,10, 3,11, 4, 5, 4, 6, 6, 6, 4, 7,
  1, 1, 1, 1, 1, 1, 1, 1, 1, 9, 2,10, 3,11, 4, 5, 4, 6, 6, 6, 4, 7,
 12, 1, 9, 9, 9, 9, 9, 9, 9, 9, 2,10, 3,11, 4, 5, 4, 6, 6, 6, 4, 7,
  1, 1, 9, 9, 9, 9, 9, 9, 9, 9, 2,10, 3,11, 4, 5, 4, 6, 6, 6, 4, 7,
  1, 1, 1, 1, 1, 1, 1, 1, 1, 9, 2,10, 3,11, 4, 5, 4, 6, 6, 6, 4, 7,
  0, 0, 0, 0, 0, 0, 0, 0, 1, 9, 2,10, 3,11, 4, 5, 4, 6, 6, 6, 4, 7,
  8, 8, 8, 8, 8, 8, 8, 8, 1, 9, 2,10, 3,11, 4, 5, 4, 6, 6, 6, 4, 7,
  1, 1, 1, 1, 1, 1, 1, 1, 1, 9, 2,10, 3,11, 4, 5, 4, 6, 6, 6, 4, 7,
 12, 1, 9, 9, 9, 9, 9, 9, 9, 9, 2,10, 3,11, 4, 5, 4, 6, 6, 6, 4, 7,
  1, 1, 9, 9, 9, 9, 9, 9, 9, 9, 2,10, 3,11, 4, 5, 4, 6, 6, 6, 4, 7,
  1, 1, 1, 1, 1, 1, 1, 1, 1, 9, 2,10, 3,11, 4, 5, 4, 6, 6, 6, 4, 7,
  0, 0, 0, 0, 0, 0, 0, 0, 1, 9, 2,10, 3,11, 4, 5, 4, 6, 6, 6, 4, 7,
  8, 8, 8, 8, 8, 8, 8, 8, 1, 9, 2,10, 3,11, 4, 5, 4, 6, 6, 6, 4, 7,
  1, 1, 1, 1, 1, 1, 1, 1, 1, 9, 2,10, 3,11, 4, 5, 4, 6, 6, 6, 4, 7,
 12, 1, 9, 9, 9, 9, 9, 9, 9, 9, 2,10, 3,11, 4, 5, 4, 6, 6, 6, 4, 7,
  1, 1, 9, 9, 9, 9, 9, 9, 9, 9, 2,10, 3,11, 4, 5, 4, 6, 6, 6, 4, 7,
  9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 2,10, 3,11, 4, 5, 4, 6, 6, 6, 4, 7,
  2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2,10, 3,11, 4, 5, 4, 6, 6, 6, 4, 7,
 12,12,12, 2,10,10,10,10,10,10,10,10, 3,11, 4, 5, 4, 6, 6, 6, 4, 7,
  2, 2, 2, 2,10,10,10,10,10,10,10,10, 3,11, 4, 5, 4, 6, 6, 6, 4, 7,
  3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3,11, 4, 5, 4, 6, 6, 6, 4, 7,
 12,12,12,12, 3, 3, 3, 5, 5, 5, 5, 5, 5, 5, 4, 5, 4, 6, 6, 6, 4, 7,
  3, 3, 3, 3, 3, 3, 3, 5, 5, 5, 5, 5, 5, 5, 4, 5, 4, 6, 6, 6, 4, 7,
  5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 4, 5, 4, 6, 6, 6, 4, 7,
  4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 8
};
Call pmap;
borehole2_pvs += pmap_out[];
borehole2_lvl += cylitive_lvls[#cylitive_lvls[]-1];



// Center
cylitive_lvls = {
  0.018, 
  0.023, 
  0.047, 

  0.052, 
  0.302, 
  0.317,
  0.327, 0.407, 0.417,
  0.421, 1.213, 1.329, 1.333, 1.413, 1.417,
  1.421, 2.213, 2.329, 2.333, 2.413, 2.417,
  2.421, 3.213, 3.329, 3.333, 3.413, 3.417,
  3.627, 3.632, 3.712, 3.717,
  3.732, 3.807, 3.822,
  4.072, 
  4.077
}; // Height layers levels
// Parameters
cylitive_t3s = {
//  borehole2_t3s[0], // Bottom Gap
//  borehole2_t3s[1], // Isolation Container ring

  borehole2_t3s[35], // Isolation Container cap height
  borehole2_t3s[36], // Isolation Container cap width
  borehole2_t3s[37], // Fill between Isolation Containers

  borehole2_t3s[2], // Isolation Container bottom     
  borehole2_t3s[3], // Bentonite bottom 
  borehole2_t3s[4], // Transport Container bottom
  borehole2_t3s[5], borehole2_t3s[6], borehole2_t3s[7], // Mayak Container bottom, anticap height, anticap width
  borehole2_t3s[8], borehole2_t3s[9], borehole2_t3s[10], borehole2_t3s[11], borehole2_t3s[12], borehole2_t3s[13], // Can bottom, matrix, void, top, cap height, cap width
  borehole2_t3s[14], borehole2_t3s[15], borehole2_t3s[16], borehole2_t3s[17], borehole2_t3s[18], borehole2_t3s[19], // Can bottom, matrix, void, top, cap height, cap width
  borehole2_t3s[20], borehole2_t3s[21], borehole2_t3s[22], borehole2_t3s[23], borehole2_t3s[24], borehole2_t3s[25], // Can bottom, matrix, void, top, cap height, cap width
  borehole2_t3s[26], borehole2_t3s[27], borehole2_t3s[28], borehole2_t3s[29], // Mayak Container void, top, cap height, cap width
  borehole2_t3s[30], borehole2_t3s[31], borehole2_t3s[32], // Transport Container top, cap height, cap width
  borehole2_t3s[33], // Bentonite top
  borehole2_t3s[34] // Isolation Container top

//  3, // Isolation Container cap height 
//  3, // Isolation Container cap width
//  3 // Top Gap height
}; // Number of height nodes
cylitive_t3t1s = {
//  borehole2_t3t1s[0], // Bottom Gap
//  borehole2_t3t1s[1], // Isolation Container ring

  borehole2_t3t1s[35], // Isolation Container cap height
  borehole2_t3t1s[36], // Isolation Container cap width
  borehole2_t3t1s[37], // Fill between Isolation Containers

  borehole2_t3t1s[2], // Isolation Container bottom     
  borehole2_t3t1s[3], // Bentonite bottom 
  borehole2_t3t1s[4], // Transport Container bottom
  borehole2_t3t1s[5], borehole2_t3t1s[6], borehole2_t3t1s[7], // Mayak Container bottom, anticap height, anticap width
  borehole2_t3t1s[8], borehole2_t3t1s[9], borehole2_t3t1s[10], borehole2_t3t1s[11], borehole2_t3t1s[12], borehole2_t3t1s[13], // Can bottom, matrix, void, top, cap height, cap width
  borehole2_t3t1s[14], borehole2_t3t1s[15], borehole2_t3t1s[16], borehole2_t3t1s[17], borehole2_t3t1s[18], borehole2_t3t1s[19], // Can bottom, matrix, void, top, cap height, cap width
  borehole2_t3t1s[20], borehole2_t3t1s[21], borehole2_t3t1s[22], borehole2_t3t1s[23], borehole2_t3t1s[24], borehole2_t3t1s[25], // Can bottom, matrix, void, top, cap height, cap width
  borehole2_t3t1s[26], borehole2_t3t1s[27], borehole2_t3t1s[28], borehole2_t3t1s[29], // Mayak Container void, top, cap height, cap width
  borehole2_t3t1s[30], borehole2_t3t1s[31], borehole2_t3t1s[32], // Transport Container top, cap height, cap width
  borehole2_t3t1s[33], // Bentonite top
  borehole2_t3t1s[34] // Isolation Container top

//  3, // Isolation Container cap height 
//  3, // Isolation Container cap width
//  3 // Top Gap height
}; // Height nodes progression
cylitive_t3t2s = {
//  borehole2_t3t2s[0], // Bottom Gap
//  borehole2_t3t2s[1], // Isolation Container ring

  borehole2_t3t2s[35], // Isolation Container cap height
  borehole2_t3t2s[36], // Isolation Container cap width
  borehole2_t3t2s[37], // Fill between Isolation Containers

  borehole2_t3t2s[2], // Isolation Container bottom     
  borehole2_t3t2s[3], // Bentonite bottom 
  borehole2_t3t2s[4], // Transport Container bottom
  borehole2_t3t2s[5], borehole2_t3t2s[6], borehole2_t3t2s[7], // Mayak Container bottom, anticap height, anticap width
  borehole2_t3t2s[8], borehole2_t3t2s[9], borehole2_t3t2s[10], borehole2_t3t2s[11], borehole2_t3t2s[12], borehole2_t3t2s[13], // Can bottom, matrix, void, top, cap height, cap width
  borehole2_t3t2s[14], borehole2_t3t2s[15], borehole2_t3t2s[16], borehole2_t3t2s[17], borehole2_t3t2s[18], borehole2_t3t2s[19], // Can bottom, matrix, void, top, cap height, cap width
  borehole2_t3t2s[20], borehole2_t3t2s[21], borehole2_t3t2s[22], borehole2_t3t2s[23], borehole2_t3t2s[24], borehole2_t3t2s[25], // Can bottom, matrix, void, top, cap height, cap width
  borehole2_t3t2s[26], borehole2_t3t2s[27], borehole2_t3t2s[28], borehole2_t3t2s[29], // Mayak Container void, top, cap height, cap width
  borehole2_t3t2s[30], borehole2_t3t2s[31], borehole2_t3t2s[32], // Transport Container top, cap height, cap width
  borehole2_t3t2s[33], // Bentonite top
  borehole2_t3t2s[34] // Isolation Container top

//  3, // Isolation Container cap height 
//  3, // Isolation Container cap width
//  3 // Top Gap height
}; // Height nodes progression bump
cylitive_t5 = 0; // Create spherical shells (0 - not, 1 - bottom, 2 - top, 3 - top and bottom)?
pmap_map_dims = {
  #cylitive_lvls[], // levels
  #cylitive_rs[]
};
pmap_in_dim = 3;
pmap_map = {
 12,12,12,12,12,12, 4, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 4, 7, 7, 7,
  4, 4, 4, 4, 4, 4, 4, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 4, 7, 7, 7,
  7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 4, 7, 7, 7,
  4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 7,
  5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 4, 5, 4, 6, 6, 6, 4, 7,
  3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3,11, 4, 5, 4, 6, 6, 6, 4, 7,
 10,10,10,10,10,10, 2, 2, 2, 2, 2,10, 3,11, 4, 5, 4, 6, 6, 6, 4, 7,
 10,10,10,10,10,10, 2, 9, 9, 9, 2,10, 3,11, 4, 5, 4, 6, 6, 6, 4, 7,
  2, 2, 2, 2, 2, 2, 2, 9, 9, 9, 2,10, 3,11, 4, 5, 4, 6, 6, 6, 4, 7,
  1, 1, 1, 1, 1, 1, 1, 1, 1, 9, 2,10, 3,11, 4, 5, 4, 6, 6, 6, 4, 7,
  0, 0, 0, 0, 0, 0, 0, 0, 1, 9, 2,10, 3,11, 4, 5, 4, 6, 6, 6, 4, 7,
  8, 8, 8, 8, 8, 8, 8, 8, 1, 9, 2,10, 3,11, 4, 5, 4, 6, 6, 6, 4, 7,
  1, 1, 1, 1, 1, 1, 1, 1, 1, 9, 2,10, 3,11, 4, 5, 4, 6, 6, 6, 4, 7,
 12, 1, 9, 9, 9, 9, 9, 9, 9, 9, 2,10, 3,11, 4, 5, 4, 6, 6, 6, 4, 7,
  1, 1, 9, 9, 9, 9, 9, 9, 9, 9, 2,10, 3,11, 4, 5, 4, 6, 6, 6, 4, 7,
  1, 1, 1, 1, 1, 1, 1, 1, 1, 9, 2,10, 3,11, 4, 5, 4, 6, 6, 6, 4, 7,
  0, 0, 0, 0, 0, 0, 0, 0, 1, 9, 2,10, 3,11, 4, 5, 4, 6, 6, 6, 4, 7,
  8, 8, 8, 8, 8, 8, 8, 8, 1, 9, 2,10, 3,11, 4, 5, 4, 6, 6, 6, 4, 7,
  1, 1, 1, 1, 1, 1, 1, 1, 1, 9, 2,10, 3,11, 4, 5, 4, 6, 6, 6, 4, 7,
 12, 1, 9, 9, 9, 9, 9, 9, 9, 9, 2,10, 3,11, 4, 5, 4, 6, 6, 6, 4, 7,
  1, 1, 9, 9, 9, 9, 9, 9, 9, 9, 2,10, 3,11, 4, 5, 4, 6, 6, 6, 4, 7,
  1, 1, 1, 1, 1, 1, 1, 1, 1, 9, 2,10, 3,11, 4, 5, 4, 6, 6, 6, 4, 7,
  0, 0, 0, 0, 0, 0, 0, 0, 1, 9, 2,10, 3,11, 4, 5, 4, 6, 6, 6, 4, 7,
  8, 8, 8, 8, 8, 8, 8, 8, 1, 9, 2,10, 3,11, 4, 5, 4, 6, 6, 6, 4, 7,
  1, 1, 1, 1, 1, 1, 1, 1, 1, 9, 2,10, 3,11, 4, 5, 4, 6, 6, 6, 4, 7,
 12, 1, 9, 9, 9, 9, 9, 9, 9, 9, 2,10, 3,11, 4, 5, 4, 6, 6, 6, 4, 7,
  1, 1, 9, 9, 9, 9, 9, 9, 9, 9, 2,10, 3,11, 4, 5, 4, 6, 6, 6, 4, 7,
  9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 2,10, 3,11, 4, 5, 4, 6, 6, 6, 4, 7,
  2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2,10, 3,11, 4, 5, 4, 6, 6, 6, 4, 7,
 12,12,12, 2,10,10,10,10,10,10,10,10, 3,11, 4, 5, 4, 6, 6, 6, 4, 7,
  2, 2, 2, 2,10,10,10,10,10,10,10,10, 3,11, 4, 5, 4, 6, 6, 6, 4, 7,
  3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3,11, 4, 5, 4, 6, 6, 6, 4, 7,
 12,12,12,12, 3, 3, 3, 5, 5, 5, 5, 5, 5, 5, 4, 5, 4, 6, 6, 6, 4, 7,
  3, 3, 3, 3, 3, 3, 3, 5, 5, 5, 5, 5, 5, 5, 4, 5, 4, 6, 6, 6, 4, 7,
  5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 4, 5, 4, 6, 6, 6, 4, 7,
  4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 8
};
For borehole2_i In {0 : 15}
  Printf("Container %g", borehole2_i+2);
  cylitive_ox = borehole2_ox; cylitive_oy = borehole2_oy; cylitive_oz = borehole2_lvl; // Origin: x, y, z (BOTTOM)
  cylitive_rox = borehole2_ox; cylitive_roy = borehole2_oy; cylitive_roz = -borehole2_lvl; // Local Rotation Origin: x, y, z
  Call cylitive;
  borehole2_bss += cylitive_bss[];
  borehole2_lvl += cylitive_lvls[#cylitive_lvls[]-1];
  pmap_in = cylitive_vs[];
  Call pmap;
  borehole2_pvs += pmap_out[];
EndFor




// Top
Printf("Container %g", 18);
cylitive_lvls = {
  0.018,
  0.023,
  0.047,

  0.052,
  0.302,
  0.317,
  0.327, 0.407, 0.417,
  0.421, 1.213, 1.329, 1.333, 1.413, 1.417,
  1.421, 2.213, 2.329, 2.333, 2.413, 2.417,
  2.421, 3.213, 3.329, 3.333, 3.413, 3.417,
  3.627, 3.632, 3.712, 3.717,
  3.732, 3.807, 3.822,
  4.072,
  4.077,

  4.095, 
  4.100,
  5.191
}; // Height layers levels
cylitive_ox = borehole2_ox; cylitive_oy = borehole2_oy; cylitive_oz = borehole2_lvl; // Origin: x, y, z (BOTTOM)
cylitive_rox = borehole2_ox; cylitive_roy = borehole2_oy; cylitive_roz = cylitive_roz-borehole2_lvl; // Local Rotation Origin: x, y, z
// Parameters
cylitive_t3s = {
//  borehole2_t3s[0], // Bottom Gap
//  borehole2_t3s[1], // Isolation Container ring

  borehole2_t3s[35], // Isolation Container cap height
  borehole2_t3s[36], // Isolation Container cap width
  borehole2_t3s[37], // Fill between Isolation Containers

  borehole2_t3s[2], // Isolation Container bottom     
  borehole2_t3s[3], // Bentonite bottom 
  borehole2_t3s[4], // Transport Container bottom
  borehole2_t3s[5], borehole2_t3s[6], borehole2_t3s[7], // Mayak Container bottom, anticap height, anticap width
  borehole2_t3s[8], borehole2_t3s[9], borehole2_t3s[10], borehole2_t3s[11], borehole2_t3s[12], borehole2_t3s[13], // Can bottom, matrix, void, top, cap height, cap width
  borehole2_t3s[14], borehole2_t3s[15], borehole2_t3s[16], borehole2_t3s[17], borehole2_t3s[18], borehole2_t3s[19], // Can bottom, matrix, void, top, cap height, cap width
  borehole2_t3s[20], borehole2_t3s[21], borehole2_t3s[22], borehole2_t3s[23], borehole2_t3s[24], borehole2_t3s[25], // Can bottom, matrix, void, top, cap height, cap width
  borehole2_t3s[26], borehole2_t3s[27], borehole2_t3s[28], borehole2_t3s[29], // Mayak Container void, top, cap height, cap width
  borehole2_t3s[30], borehole2_t3s[31], borehole2_t3s[32], // Transport Container top, cap height, cap width
  borehole2_t3s[33], // Bentonite top
  borehole2_t3s[34], // Isolation Container top

  borehole2_t3s[38], // Isolation Container cap height 
  borehole2_t3s[39], // Isolation Container cap width
  borehole2_t3s[40] // Top Gap height
}; // Number of height nodes
cylitive_t3t1s = {
//  borehole2_t3t1s[0], // Bottom Gap
//  borehole2_t3t1s[1], // Isolation Container ring

  borehole2_t3t1s[35], // Isolation Container cap height
  borehole2_t3t1s[36], // Isolation Container cap width
  borehole2_t3t1s[37], // Fill between Isolation Containers

  borehole2_t3t1s[2], // Isolation Container bottom     
  borehole2_t3t1s[3], // Bentonite bottom 
  borehole2_t3t1s[4], // Transport Container bottom
  borehole2_t3t1s[5], borehole2_t3t1s[6], borehole2_t3t1s[7], // Mayak Container bottom, anticap height, anticap width
  borehole2_t3t1s[8], borehole2_t3t1s[9], borehole2_t3t1s[10], borehole2_t3t1s[11], borehole2_t3t1s[12], borehole2_t3t1s[13], // Can bottom, matrix, void, top, cap height, cap width
  borehole2_t3t1s[14], borehole2_t3t1s[15], borehole2_t3t1s[16], borehole2_t3t1s[17], borehole2_t3t1s[18], borehole2_t3t1s[19], // Can bottom, matrix, void, top, cap height, cap width
  borehole2_t3t1s[20], borehole2_t3t1s[21], borehole2_t3t1s[22], borehole2_t3t1s[23], borehole2_t3t1s[24], borehole2_t3t1s[25], // Can bottom, matrix, void, top, cap height, cap width
  borehole2_t3t1s[26], borehole2_t3t1s[27], borehole2_t3t1s[28], borehole2_t3t1s[29], // Mayak Container void, top, cap height, cap width
  borehole2_t3t1s[30], borehole2_t3t1s[31], borehole2_t3t1s[32], // Transport Container top, cap height, cap width
  borehole2_t3t1s[33], // Bentonite top
  borehole2_t3t1s[34], // Isolation Container top

  borehole2_t3t1s[38], // Isolation Container cap height 
  borehole2_t3t1s[39], // Isolation Container cap width
  borehole2_t3t1s[40] // Top Gap height
}; // Height nodes progression
cylitive_t3t2s = {
//  borehole2_t3t2s[0], // Bottom Gap
//  borehole2_t3t2s[1], // Isolation Container ring

  borehole2_t3t2s[35], // Isolation Container cap height
  borehole2_t3t2s[36], // Isolation Container cap width
  borehole2_t3t2s[37], // Fill between Isolation Containers

  borehole2_t3t2s[2], // Isolation Container bottom     
  borehole2_t3t2s[3], // Bentonite bottom 
  borehole2_t3t2s[4], // Transport Container bottom
  borehole2_t3t2s[5], borehole2_t3t2s[6], borehole2_t3t2s[7], // Mayak Container bottom, anticap height, anticap width
  borehole2_t3t2s[8], borehole2_t3t2s[9], borehole2_t3t2s[10], borehole2_t3t2s[11], borehole2_t3t2s[12], borehole2_t3t2s[13], // Can bottom, matrix, void, top, cap height, cap width
  borehole2_t3t2s[14], borehole2_t3t2s[15], borehole2_t3t2s[16], borehole2_t3t2s[17], borehole2_t3t2s[18], borehole2_t3t2s[19], // Can bottom, matrix, void, top, cap height, cap width
  borehole2_t3t2s[20], borehole2_t3t2s[21], borehole2_t3t2s[22], borehole2_t3t2s[23], borehole2_t3t2s[24], borehole2_t3t2s[25], // Can bottom, matrix, void, top, cap height, cap width
  borehole2_t3t2s[26], borehole2_t3t2s[27], borehole2_t3t2s[28], borehole2_t3t2s[29], // Mayak Container void, top, cap height, cap width
  borehole2_t3t2s[30], borehole2_t3t2s[31], borehole2_t3t2s[32], // Transport Container top, cap height, cap width
  borehole2_t3t2s[33], // Bentonite top
  borehole2_t3t2s[34], // Isolation Container top

  borehole2_t3t2s[38], // Isolation Container cap height 
  borehole2_t3t2s[39], // Isolation Container cap width
  borehole2_t3t2s[40] // Top Gap height
}; // Height nodes progression bump
cylitive_t5 = 2; // Create spherical shells (0 - not, 1 - bottom, 2 - top, 3 - top and bottom)?
Call cylitive;
borehole2_bss += cylitive_bss[];
pmap_in = cylitive_vs[];
pmap_in_dim = 3;
pmap_map_dims = {
  #cylitive_lvls[]+1, // levels + top spherical shell
  #cylitive_rs[]
};
pmap_map = {
 12,12,12,12,12,12, 4, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 4, 7, 7, 7,
  4, 4, 4, 4, 4, 4, 4, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 4, 7, 7, 7,
  7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 4, 7, 7, 7,
  4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 7,
  5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 4, 5, 4, 6, 6, 6, 4, 7,
  3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3,11, 4, 5, 4, 6, 6, 6, 4, 7,
 10,10,10,10,10,10, 2, 2, 2, 2, 2,10, 3,11, 4, 5, 4, 6, 6, 6, 4, 7,
 10,10,10,10,10,10, 2, 9, 9, 9, 2,10, 3,11, 4, 5, 4, 6, 6, 6, 4, 7,
  2, 2, 2, 2, 2, 2, 2, 9, 9, 9, 2,10, 3,11, 4, 5, 4, 6, 6, 6, 4, 7,
  1, 1, 1, 1, 1, 1, 1, 1, 1, 9, 2,10, 3,11, 4, 5, 4, 6, 6, 6, 4, 7,
  0, 0, 0, 0, 0, 0, 0, 0, 1, 9, 2,10, 3,11, 4, 5, 4, 6, 6, 6, 4, 7,
  8, 8, 8, 8, 8, 8, 8, 8, 1, 9, 2,10, 3,11, 4, 5, 4, 6, 6, 6, 4, 7,
  1, 1, 1, 1, 1, 1, 1, 1, 1, 9, 2,10, 3,11, 4, 5, 4, 6, 6, 6, 4, 7,
 12, 1, 9, 9, 9, 9, 9, 9, 9, 9, 2,10, 3,11, 4, 5, 4, 6, 6, 6, 4, 7,
  1, 1, 9, 9, 9, 9, 9, 9, 9, 9, 2,10, 3,11, 4, 5, 4, 6, 6, 6, 4, 7,
  1, 1, 1, 1, 1, 1, 1, 1, 1, 9, 2,10, 3,11, 4, 5, 4, 6, 6, 6, 4, 7,
  0, 0, 0, 0, 0, 0, 0, 0, 1, 9, 2,10, 3,11, 4, 5, 4, 6, 6, 6, 4, 7,
  8, 8, 8, 8, 8, 8, 8, 8, 1, 9, 2,10, 3,11, 4, 5, 4, 6, 6, 6, 4, 7,
  1, 1, 1, 1, 1, 1, 1, 1, 1, 9, 2,10, 3,11, 4, 5, 4, 6, 6, 6, 4, 7,
 12, 1, 9, 9, 9, 9, 9, 9, 9, 9, 2,10, 3,11, 4, 5, 4, 6, 6, 6, 4, 7,
  1, 1, 9, 9, 9, 9, 9, 9, 9, 9, 2,10, 3,11, 4, 5, 4, 6, 6, 6, 4, 7,
  1, 1, 1, 1, 1, 1, 1, 1, 1, 9, 2,10, 3,11, 4, 5, 4, 6, 6, 6, 4, 7,
  0, 0, 0, 0, 0, 0, 0, 0, 1, 9, 2,10, 3,11, 4, 5, 4, 6, 6, 6, 4, 7,
  8, 8, 8, 8, 8, 8, 8, 8, 1, 9, 2,10, 3,11, 4, 5, 4, 6, 6, 6, 4, 7,
  1, 1, 1, 1, 1, 1, 1, 1, 1, 9, 2,10, 3,11, 4, 5, 4, 6, 6, 6, 4, 7,
 12, 1, 9, 9, 9, 9, 9, 9, 9, 9, 2,10, 3,11, 4, 5, 4, 6, 6, 6, 4, 7,
  1, 1, 9, 9, 9, 9, 9, 9, 9, 9, 2,10, 3,11, 4, 5, 4, 6, 6, 6, 4, 7,
  9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 2,10, 3,11, 4, 5, 4, 6, 6, 6, 4, 7,
  2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2,10, 3,11, 4, 5, 4, 6, 6, 6, 4, 7,
 12,12,12, 2,10,10,10,10,10,10,10,10, 3,11, 4, 5, 4, 6, 6, 6, 4, 7,
  2, 2, 2, 2,10,10,10,10,10,10,10,10, 3,11, 4, 5, 4, 6, 6, 6, 4, 7,
  3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3,11, 4, 5, 4, 6, 6, 6, 4, 7,
 12,12,12,12, 3, 3, 3, 5, 5, 5, 5, 5, 5, 5, 4, 5, 4, 6, 6, 6, 4, 7,
  3, 3, 3, 3, 3, 3, 3, 5, 5, 5, 5, 5, 5, 5, 4, 5, 4, 6, 6, 6, 4, 7,
  5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 4, 5, 4, 6, 6, 6, 4, 7,
  4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 8,
 12,12,12,12,12,12, 4, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7,
  4, 4, 4, 4, 4, 4, 4, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7,
 13,13,13,13,13,13,13,13,13,13,13,13,13,13,13,13,13,13,13,13,13,13,
 14,14,14,14,14,14,14,14,14,14,14,14,14,14,14,14,14,14,14,14,14,14
};
Call pmap;
borehole2_pvs += pmap_out[];




borehole2_pvns[] = Str( // borehole2_pvns[i] indices correspond to pmap_map[] values
  "Matrices",
  "Cans",
  "MayakContainer",
  "TransportContainer",
  "IsolationContainer",
  "Bentonite",
  "Concrete",
  "Fill",
  "CansVoid",
  "MayakContainerVoid",
  "TransportContainerVoid",
  "IsolationContainerVoid",
  "Void",
  "Gap",
  "Environment"
);

Return

