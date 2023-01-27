import gmsh
import numpy as np


class Size:
    def __init__(self):
        pass

    def evaluate_map(self, block):
        point2size = {}
        return point2size

    def __call__(self, block):
        point2size = self.evaluate_map(block)
        for p, s in point2size.items():
            gmsh.model.mesh.setSize([(0, p)], s)


class NoSize(Size):
    def __init__(self):
        super().__init__()
        pass

    def __call__(self, block):
        pass


class BooleanPoint(Size):
    def __init__(self, intra_function='min', inter_function='min',
                 factor=1., min_size=0., max_size=1e22):
        super().__init__()
        self.intra_function = intra_function
        self.inter_function = inter_function
        self.factor, self.min_size, self.max_size = factor, min_size, max_size

    def evaluate_map(self, block):
        point2size = {}
        intra_function = getattr(np, self.intra_function)
        for b in block:
            # if not b.is_booleaned:
            #     continue
            mesh_sizes = [x.kwargs.get('meshSize', None) for x in b.points]
            mesh_sizes = [x for x in mesh_sizes if x is not None]
            size = intra_function(mesh_sizes) if len(mesh_sizes) > 0 else None
            if size is None:
                continue
            size *= self.factor
            size = np.clip(size, self.min_size, self.max_size)
            for v in b.volumes:
                if v.tag is not None:
                    ps = gmsh.model.get_boundary([(3, v.tag)], recursive=True)
                    for p in ps:
                        point2size.setdefault(p[1], []).append(size)
        inter_function = getattr(np, self.inter_function)
        for p, ss in point2size.items():
            point2size[p] = inter_function(ss)
        return point2size

    def __call__(self, block):
        super().__call__(block)


class BooleanEdge(Size):
    def __init__(self, intra_function='min', inter_function='min',
                 factor=1., min_size=0., max_size=1e22):
        super().__init__()
        self.intra_function = intra_function
        self.inter_function = inter_function
        self.factor, self.min_size, self.max_size = factor, min_size, max_size

    def evaluate_map(self, block):
        point2size = {}
        intra_function = getattr(np, self.intra_function)
        for b in block:
            # if not b.is_booleaned:
            #     continue
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
                size = intra_function(lengths) if len(lengths) > 0 else None
                if size is None:
                    continue
                size *= self.factor
                size = np.clip(size, self.min_size, self.max_size)
                ps = gmsh.model.get_boundary([(3, v.tag)], recursive=True)
                for p in ps:
                    point2size.setdefault(p[1], []).append(size)
        inter_function = getattr(np, self.inter_function)
        for p, ss in point2size.items():
            point2size[p] = inter_function(ss)
        return point2size

    def __call__(self, block):
        super().__call__(block)


class Bagging(Size):
    def __init__(self, sizes=(), inter_function='mean'):
        super().__init__()
        self.sizes, self.inter_function = sizes, inter_function

    def evaluate_map(self, block):
        point2size = {}
        for size in self.sizes:
            p2s = size.evaluate_map(block)
            for p, s in p2s.items():
                point2size.setdefault(p, []).append(s)
        inter_function = getattr(np, self.inter_function)
        for p, ss in point2size.items():
            point2size[p] = inter_function(ss)
        return point2size

    def __call__(self, block):
        super().__call__(block)


str2obj = {
    Size.__name__: Size,
    BooleanPoint.__name__: BooleanPoint,
    BooleanEdge.__name__: BooleanEdge,
    Bagging.__name__: Bagging,
    NoSize.__name__: NoSize
}
