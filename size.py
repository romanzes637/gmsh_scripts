import gmsh
import numpy as np


class Size:
    def __init__(self):
        pass

    def evaluate_map(self, block):
        volume2size = {}
        return volume2size

    def __call__(self, block):
        volume2size = self.evaluate_map(block)
        from pprint import pprint
        pprint(volume2size)
        for v, s in volume2size.items():
            gmsh.model.mesh.setSize(gmsh.model.get_boundary(
                [(3, v)], recursive=True), s)


class BooleanPoint(Size):
    def __init__(self, function='min', factor=1., min_size=0., max_size=1e22):
        super().__init__()
        self.function = function
        self.factor, self.min_size, self.max_size = factor, min_size, max_size

    def evaluate_map(self, block):
        volume2size = {}
        f = getattr(np, self.function)
        for b in block:
            if not b.is_booleaned:
                continue
            mesh_sizes = [x.kwargs.get('meshSize', None) for x in b.points]
            mesh_sizes = [x for x in mesh_sizes if x is not None]
            size = f(mesh_sizes) if len(mesh_sizes) > 0 else None
            if size is None:
                continue
            size *= self.factor
            size = np.clip(size, self.min_size, self.max_size)
            for v in b.volumes:
                if v.tag is not None:
                    volume2size[v.tag] = size
        return volume2size

    def __call__(self, block):
        super().__call__(block)


class BooleanEdge(Size):
    def __init__(self, function='min', factor=1., min_size=0., max_size=1e22):
        super().__init__()
        self.function = function
        self.factor, self.min_size, self.max_size = factor, min_size, max_size

    def evaluate_map(self, block):
        volume2size = {}
        f = getattr(np, self.function)
        for b in block:
            if not b.is_booleaned:
                continue
            for v in b.volumes:
                if v.tag is None:
                    continue
                volume_dim_tag = (3, v.tag)
                # Surfaces
                surfaces_dim_tags = gmsh.model.getBoundary([volume_dim_tag])
                # Edges
                edges = set()
                for sdt in surfaces_dim_tags:
                    edges_dim_tags = gmsh.model.getBoundary([sdt])
                    for edt in edges_dim_tags:
                        edges.add(abs(edt[1]))
                # Lengths
                lengths = []
                for e in edges:
                    edge_dim_tag = (1, e)
                    points_dim_tags = gmsh.model.getBoundary([edge_dim_tag])
                    ps = [x[1] for x in points_dim_tags]
                    bb0 = gmsh.model.getBoundingBox(0, ps[0])
                    bb1 = gmsh.model.getBoundingBox(0, ps[1])
                    cs0 = [bb0[0], bb0[1], bb0[2]]
                    cs1 = [bb1[0], bb1[1], bb1[2]]
                    vector = [cs1[0] - cs0[0], cs1[1] - cs0[1], cs1[2] - cs0[2]]
                    length = np.linalg.norm(vector)
                    lengths.append(length)
                size = f(lengths) if len(lengths) > 0 else None
                if size is None:
                    continue
                size *= self.factor
                size = np.clip(size, self.min_size, self.max_size)
                volume2size[v.tag] = size
        return volume2size

    def __call__(self, block):
        super().__call__(block)


class Bagging(Size):
    def __init__(self, sizes=(), function='mean'):
        super().__init__()
        self.sizes, self.function = sizes, function

    def evaluate_map(self, block):
        volume2size = {}
        f = getattr(np, self.function)
        for size in self.sizes:
            v2s = size.evaluate_map(block)
            for v, s in v2s.items():
                volume2size.setdefault(v, []).append(s)
        for v, ss in volume2size.items():
            volume2size[v] = f(ss)
        return volume2size

    def __call__(self, block):
        super().__call__(block)
