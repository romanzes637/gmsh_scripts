Include "macro_cylitive.geo";
Include "macro_pmap.geo";

Macro borehole1

borehole1_bss = {};
borehole1_pvs = {};

cylitive_lcs = {0.100, 0.100, 0.100}; // Circumferential layers points characteristic length
cylitive_k = 1/3; // Inner hexahedron X, Y edge length / Radius
cylitive_rs = {0.281, 0.603, 0.650}; // Circumferential layers radii
cylitive_lvls = {0.553, 0.600, 0.922, 74.078, 74.400, 74.447, 75.000}; // Height layers levels
cylitive_ox = borehole1_ox; cylitive_oy = borehole1_oy; cylitive_oz = borehole1_oz; // Origin: x, y, z (BOTTOM)
cylitive_rox = borehole1_ox; cylitive_roy = borehole1_oy; cylitive_roz = borehole1_oz; // Local Rotation Origin: x, y, z
cylitive_rax = borehole1_rax; cylitive_ray = borehole1_ray; cylitive_raz = borehole1_raz; // Local Rotation Angle: x, y, z
// Parameters
cylitive_t1 = borehole1_t1; cylitive_t1t1 = 0; cylitive_t1t2 = 0; // Number of circumferential nodes, progression, bump
cylitive_t2s = borehole1_t2s[]; // Number of radial nodes
cylitive_t2t1s = borehole1_t2t1s[]; // Radial nodes progression
cylitive_t2t2s = borehole1_t2t2s[]; // Radial nodes bump
cylitive_t3s = borehole1_t3s[]; // Number of height nodes
cylitive_t3t1s = borehole1_t3t1s[]; // Height nodes progression
cylitive_t3t2s = borehole1_t3t2s[]; // Height nodes progression bump
cylitive_t4 = 0; // Hex (1) or tet (0) mesh?
cylitive_t5 = 3; // Create spherical shells (0 - not, 1 - bottom, 2 - top, 3 - top and bottom)?
cylitive_t6 = 1; // Full boundary surfaces?
Call cylitive;

borehole1_bss = cylitive_bss[];

pmap_in = cylitive_vs[];
pmap_in_dim = 3;
pmap_map_dims = {
  1+#cylitive_lvls[]+1, // bottom spherical shell + levels + top spherical shell
  #cylitive_rs[]
};
pmap_map = { // Written from the bottom to top spherical shell vertically down, from the center to lateral surface horizontally right
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
Call pmap;
borehole1_pvs = pmap_out[];

borehole1_pvns[] = Str( // borehole1_pvns[i] indices correspond to pmap_map[] values
  "Matrix",
  "Container",
  "Fill",
  "Gap",
  "Environment"
);

Return

