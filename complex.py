import gmsh


class Complex:
    def __init__(self, factory, primitives):
        """
        Object consisting of primitives
        :param str factory: see Primitive Factory
        :param list of Primitive primitives: [primitive 1, primitive 2, ...,
         primitive N]
        """
        if factory == 'occ':
            self.factory = gmsh.model.occ
        else:
            self.factory = gmsh.model.geo
        self.primitives = primitives

    def set_size(self, size):
        for p in self.primitives:
            p.set_size(size)

    def transfinite(self, transfinited_surfaces, transfinited_curves):
        # results = list()
        for p in self.primitives:
            p.structure(transfinited_surfaces, transfinited_curves)
            # result = p.transfinite(transfinited_surfaces, transfinited_curves)
            # results.append(result)
        # return results

    def get_volumes(self):
        vs = list()
        for p in self.primitives:
            vs.extend(p.volumes)
        return vs

    def get_map_names_to_volumes(self):
        ns_to_vs = dict()
        for p in self.primitives:
            n = p.volume_name
            vs = p.volumes
            for v in vs:
                ns_to_vs.setdefault(n, list()).append(v)
        return ns_to_vs

    def get_map_vol_to_exists(self):
        vs_to_e = dict()
        for p in self.primitives:
            e = p.exists
            vs = p.volumes
            for v in vs:
                vs_to_e[v] = e
        return vs_to_e

    def get_map_surface_to_primitives_indices(self):
        s_to_is = dict()
        for i, p in enumerate(self.primitives):
            ss = p.get_surfaces()
            for s in ss:
                s_to_is.setdefault(s, list()).append(i)
        return s_to_is

    def get_map_surface_to_primitives_surfaces_indices(self):
        s_to_is = dict()
        for i, p in enumerate(self.primitives):
            ss = p.get_surfaces()
            if len(ss) == 6:
                for j, s in enumerate(ss):
                    s_to_is.setdefault(s, list()).append((i, j))
        return s_to_is

    def evaluate_coordinates(self):
        for p in self.primitives:
            p.evaluate_coordinates()

    def evaluate_bounding_box(self):
        for p in self.primitives:
            p.evaluate_bounding_box()

    def smooth(self, dim, n):
        for p in self.primitives:
            p.smooth(dim, n)

    def recombine(self):
        for p in self.primitives:
            p.quadrate()
