import gmsh


class Complex:
    def __init__(self, factory, primitives):
        """
        Object consisting of primitives
        :param str factory: see Primitive Factory
        :param list of Primitive primitives: [primitive 1, primitive 2, ..., primitive N]
        """
        if factory == 'occ':
            self.factory = gmsh.model.occ
        else:
            self.factory = gmsh.model.geo
        self.primitives = primitives
        self.map_physical_name_to_primitives_indices = dict()
        for i, p in enumerate(self.primitives):
            key = p.physical_name
            value = i
            self.map_physical_name_to_primitives_indices.setdefault(key, list()).append(value)

    def set_size(self, size):
        for p in self.primitives:
            p.set_size(size)

    def transfinite(self, transfinited_surfaces, transfinited_curves):
        results = list()
        for p in self.primitives:
            result = p.transfinite(transfinited_surfaces, transfinited_curves)
            results.append(result)
        return results

    def get_volumes(self):
        vs = list()
        for p in self.primitives:
            vs.extend(p.volumes)
        return vs

    def get_volumes_by_physical_name(self, name):
        vs = list()
        primitive_idxs = self.map_physical_name_to_primitives_indices.get(name)
        if primitive_idxs is not None:
            for i in primitive_idxs:
                vs.extend(self.primitives[i].volumes)
        return vs

    def get_surfaces_by_physical_name(self, name, combined=True):
        ss = list()
        primitive_idxs = self.map_physical_name_to_primitives_indices.get(name)
        if primitive_idxs is not None:
            for i in primitive_idxs:
                ss.extend(self.primitives[i].get_surfaces(combined))
        return ss

    def evaluate_coordinates(self):
        for p in self.primitives:
            p.evaluate_coordinates()

    def evaluate_bounding_box(self):
        for p in self.primitives:
            p.evaluate_bounding_box()

    def smooth(self, dim, n):
        for p in self.primitives:
            p.smooth(dim, n)
