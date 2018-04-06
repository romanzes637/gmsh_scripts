Include "macro_cylitive.geo";
Include "macro_pmap.geo";

Macro nkcontainer

nkcontainer_bss = {};
nkcontainer_pvs = {};

//r = {0.281, 0.287, 0.335, 0.343, 0.535, 0.538, 0.598, 0.603, 0.650, 1.150};
//h = {3.000, 3.100, 3.836, 3.839, 4.031, 4.035, 4.095, 4.100, 4.600, 4.800};
//z = {0.050, 0.000, -0.012, -0.015, -0.207, -0.210, -0.270, -0.275, -0.600, -0.700};

cylitive_lcs = {
0.05, 0.07, 0.05, 0.04, 0.05, 0.03, 0.05, 0.05, 0.1, 0.07
}; // Circumferential layers points characteristic length
cylitive_k = 1/3; // Inner hexahedron X, Y edge length / Radius
cylitive_rs = {
//0.281, 0.287, 0.335, 0.343, 0.535, 0.538, 0.598, 0.603, 0.650, 1.150
0.281, 0.287, 0.335, 0.343, 0.535, 0.538, 0.598, 0.603, 0.650, 11.500
}; // Circumferential layers radii
cylitive_lvls = {
0.100, 0.425, 0.430,
0.490, 0.493, 0.685, 0.688,
0.700, 0.750, 3.700, 3.800,
4.536, 4.539, 4.731, 4.735,
4.795, 4.800, 5.400
}; // Height layers levels
cylitive_ox = nkcontainer_ox; cylitive_oy = nkcontainer_oy; cylitive_oz = nkcontainer_oz-0.700; // Origin: x, y, z (BOTTOM)
cylitive_rox = nkcontainer_ox; cylitive_roy = nkcontainer_oy; cylitive_roz = nkcontainer_oz; // Local Rotation Origin: x, y, z
cylitive_rax = nkcontainer_rax; cylitive_ray = nkcontainer_ray; cylitive_raz = nkcontainer_raz; // Local Rotation Angle: x, y, z
// Parameters
cylitive_t1 = nkcontainer_t1; cylitive_t1t1 = 0; cylitive_t1t2 = 0; // Number of circumferential nodes, progression, bump
cylitive_t2s = nkcontainer_t2s[]; // Number of radial nodes
cylitive_t2t1s = nkcontainer_t2t1s[]; // Radial nodes progression
cylitive_t2t2s = nkcontainer_t2t2s[]; // Radial nodes bump
cylitive_t3s = nkcontainer_t3s[]; // Number of height nodes
cylitive_t3t1s = nkcontainer_t3t1s[]; // Height nodes progression
cylitive_t3t2s = nkcontainer_t3t2s[]; // Height nodes progression bump
cylitive_t4 = 0; // Hex (1) or tet (0) mesh?
cylitive_t5 = 0; // Create spherical shells (0 - not, 1 - bottom, 2 - top, 3 - top and bottom)?
cylitive_t6 = 1; // Full boundary surfaces?
Call cylitive;

nkcontainer_bss = cylitive_bss[];

pmap_in = cylitive_vs[];
pmap_in_dim = 3;
pmap_map_dims = {
  1+#cylitive_lvls[]+1, // bottom spherical shell + levels + top spherical shell
  #cylitive_rs[]
};
pmap_map = { // Written from the bottom to top spherical shell vertically down, from the center to lateral surface horizontally right
//    10, 10, 10, 10, 10, 10, 10, 10, 10, 10,
    9, 9, 9, 9, 9, 9, 9, 9, 9, 9,
    8, 8, 8, 8, 8, 8, 8, 8, 8, 9,
    7, 7, 7, 7, 7, 7, 7, 7, 8, 9,
    6, 6, 6, 6, 6, 6, 6, 7, 8, 9,
    5, 5, 5, 5, 5, 5, 6, 7, 8, 9,
    4, 4, 4, 4, 4, 5, 6, 7, 8, 9,
    3, 3, 3, 3, 4, 5, 6, 7, 8, 9,
    2, 2, 2, 3, 4, 5, 6, 7, 8, 9,
    1, 1, 2, 3, 4, 5, 6, 7, 8, 9,
    0, 1, 2, 3, 4, 5, 6, 7, 8, 9,
    0, 1, 2, 3, 4, 5, 6, 7, 8, 9,
    1, 1, 2, 3, 4, 5, 6, 7, 8, 9,
    2, 2, 2, 3, 4, 5, 6, 7, 8, 9,
    2, 2, 2, 3, 4, 5, 6, 7, 8, 9,
    2, 2, 2, 3, 4, 5, 6, 7, 8, 9,
    2, 2, 2, 3, 4, 5, 6, 7, 8, 9,
    2, 2, 2, 3, 4, 5, 6, 7, 8, 9,
    2, 2, 2, 3, 4, 5, 6, 7, 8, 9,
    2, 2, 2, 3, 4, 5, 6, 7, 8, 9,
    9, 9, 9, 9, 9, 9, 9, 9, 9, 9
//    10, 10, 10, 10, 10, 10, 10, 10, 10, 10
};
Call pmap;
nkcontainer_pvs = pmap_out[];

nkcontainer_pvns[] = Str( // nkcontainer_pvns[i] indices correspond to pmap_map[] values
  "stekla3",
  "bidona3",
  "tolshina_vnutrenego_stakana",
  "vnutrinnii_stakan",
  "pressovanyi_bentonit",
  "promejutochnyi_stakan",
  "alyminat",
  "vneshnii_stakan",
  "tiksotropnyi_shliker",
  "Poroda"
//  "Environment"
);

Return

