import gmsh
import logging


class Smooth:
    """Abstract

    """

    def __init__(self):
        pass

    def __call__(self, block=None):
        pass


class NoSmooth:
    def __init__(self):
        super().__init__()

    def __call__(self, block=None):
        gmsh.option.setNumber("Mesh.Smoothing", 0)
        gmsh.option.setNumber("Mesh.SmoothNormals", 0)
        gmsh.option.setNumber("Mesh.SmoothCrossField", 0)


class SmoothByDim(Smooth):
    """

    Args:
        dims (list): Dims to smooth
        n_iterations (int): Number of iterations
        smooth_normals (bool): Do smooth normals?
        smooth_cross_field (bool): Do smooth cross fields?

    """
    def __init__(self, dims=None, n_iterations=1, smooth_normals=False,
                 smooth_cross_field=False):
        super().__init__()
        self.dims = [0, 1, 2, 3] if dims is None else dims
        self.n_iterations = n_iterations
        self.smooth_normals = smooth_normals
        self.smooth_cross_field = smooth_cross_field

    def __call__(self, block=None):
        gmsh.option.setNumber("Mesh.Smoothing", self.n_iterations)
        gmsh.option.setNumber("Mesh.SmoothNormals", int(self.smooth_normals))
        gmsh.option.setNumber("Mesh.SmoothCrossField", int(self.smooth_cross_field))
        if self.n_iterations > 0:
            for d in self.dims:
                logging.info(f'Smoothing dim {d} with {self.n_iterations} iterations')
                dts = gmsh.model.getEntities(d)
                for dt in dts:
                    gmsh.model.mesh.setSmoothing(d, dt[1], self.n_iterations)


str2obj = {
    Smooth.__name__: Smooth,
    NoSmooth.__name__: NoSmooth,
    SmoothByDim.__name__: SmoothByDim,
}
