from cylinder import Cylinder


class Borehole(Cylinder):
    def __init__(self, factory, primitives_lcs, transform_data,
                 transfinite_r_data, transfinite_h_data, transfinite_phi_data, n_h_layers=1):
        """
        Type 1 borehole. Simple borehole with 3 layers:
        Radioactive Waste (RW), Engineering barrier system (EBS), Grout and two Plugs
        :param factory: gmsh factory (currently: gmsh.model.geo or gmsh.model.occ)
        :param primitives_lcs: characteristic lengths of layers [[h1_r1, h1_r2, ...], [h2_r1, h2_r2 ...], ...]
        :param transform_data: [displacement x, y, z] or
        [displacement x, y, z, rotation origin x, y, z, rotation angle x, y, z] or
        [displacement x, y, z, rotation vector x, y, z, rotation angle] or
        [displacement x, y, z, rotation angle x, y, z]
        :param transfinite_r_data: [[r1 number of nodes, type (0 - Progression, 1 - Bump), coefficient], [r2 ...], ...]
        :param transfinite_h_data: [[h1 number of nodes, type (0 - Progression, 1 - Bump), coefficient], [h2 ...], ...]
        :param transfinite_phi_data: [circumferential number of nodes, type, coefficient]
        :param n_h_layers: Number of parts of main section of borehole (73.800 m). Then intrusion
        intersects the borehole, unstructured mesh created in intersected Primitives. If we divide
        main section into parts, unstructured mesh will be created only in those parts there
        have been intersections, in other parts will be created structured mesh.
        """
        radii = [0.2835, 0.600, 0.650]
        heights = [0.600, 73.800, 0.600]
        layers_physical_data = [[3, 3, 3], [0, 1, 2], [3, 3, 3]]
        if n_h_layers > 1:  # Divide main borehole part into n_h_layers parts
            dh = heights[1] / n_h_layers
            new_heights = []
            new_heights.append(heights[0])
            new_layers_physical_data = []
            new_layers_physical_data.append(layers_physical_data[0])
            new_lcs = []
            new_lcs.append(primitives_lcs[0])
            new_transfinite_h_data = []
            new_transfinite_h_data.append(transfinite_h_data[0])
            for i in range(n_h_layers):
                new_heights.append(dh)
                new_layers_physical_data.append(layers_physical_data[1])
                new_lcs.append(primitives_lcs[1])
                new_transfinite_h_data.append(transfinite_h_data[1])
            new_heights.append(heights[2])
            new_layers_physical_data.append(layers_physical_data[2])
            new_lcs.append(primitives_lcs[2])
            new_transfinite_h_data.append(transfinite_h_data[2])
            heights = new_heights
            layers_physical_data = new_layers_physical_data
            primitives_lcs = new_lcs
            transfinite_h_data = new_transfinite_h_data
        Cylinder.__init__(self, factory, radii, heights, primitives_lcs, transform_data, layers_physical_data,
                          transfinite_r_data, transfinite_h_data, transfinite_phi_data)

    physical_names = ["RW", "EBS", "Grout", "Plug"]
