from cylinder import Cylinder


class Borehole(Cylinder):
    def __init__(self, factory, lcs, transform_data, transfinite_r_data, transfinite_h_data, transfinite_phi_data):
        radii = [0.2835, 0.600, 0.650]
        heights = [0.600, 73.800, 0.600]
        layers_physical_data = [[3, 3, 3], [0, 1, 2], [3, 3, 3]]
        Cylinder.__init__(self, factory, radii, heights, lcs, transform_data, layers_physical_data,
                          transfinite_r_data, transfinite_h_data, transfinite_phi_data)

    physical_names = ["RW", "EBS", "Grout", "Plug"]
