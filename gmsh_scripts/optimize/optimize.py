import gmsh
import sys


class Optimize:
    """Abstract

    """

    def __init__(self):
        pass

    def __call__(self, block=None):
        pass


class NoOptimize(Optimize):

    def __init__(self):
        super().__init__()

    def __call__(self, block=None):
        pass


class OptimizeOne(Optimize):
    """Optimize once

    Args:
        method (str): Optimization method:
            "" for default tetrahedral mesh optimizer
            "Netgen" for Netgen optimizer,
            "HighOrder" for direct high-order mesh optimizer,
            "HighOrderElastic" for high-order elastic smoother,
            "HighOrderFastCurving" for fast curving algorithm,
            "Laplace2D" for Laplace smoothing,
            "Relocate2D" and "Relocate3D" for node relocation
        force (bool): Apply to discrete entities
        n_iterations (int): Number of iterations
        threshold (float): Optimize tetrahedra with quality below threshold
    """

    def __init__(self, method=None, force=False, n_iterations=1, threshold=.3):
        super().__init__()
        self.method = '' if method is None else method
        self.force = force
        self.n_iterations = n_iterations
        self.threshold = threshold

    def __call__(self, block=None):
        gmsh.option.setNumber("Mesh.OptimizeThreshold", self.threshold)
        if block is None:
            gmsh.model.mesh.optimize(method=self.method,
                                     force=self.force,
                                     niter=self.n_iterations)
        else:  # TODO get dim-tags from block?
            raise NotImplementedError()


class OptimizeMany(Optimize):
    """Optimize several times

    Args:
        optimizers (list): [[opt1, n_iter1], [opt2, n_iter2], ...]
        force (bool): Apply to discrete entities
        threshold (float): Optimize tetrahedra with quality below threshold

    """
    def __init__(self, optimizers=None, force=False, threshold=.3):
        super().__init__()
        self.optimizers = [] if optimizers is None else optimizers
        self.force = force
        self.threshold = threshold

    def __call__(self, block=None):
        gmsh.option.setNumber("Mesh.OptimizeThreshold", self.threshold)
        if block is None:
            for m, n in self.optimizers:
                gmsh.model.mesh.optimize(method=m,
                                         force=self.force,
                                         niter=n)
        else:  # TODO get dim-tags from block?
            raise NotImplementedError()


str2obj = {
    Optimize.__name__: Optimize,
    OptimizeOne.__name__: OptimizeOne,
    OptimizeMany.__name__: OptimizeMany,
    NoOptimize.__name__: NoOptimize
}

if __name__ == '__main__':
    print(f"script: {sys.argv[0]}")
    print(f"input: {sys.argv[1]}")
    print(f"output: {sys.argv[2]}")
    n = int(sys.argv[3]) if len(sys.argv) == 4 else 1
    print(f'iterations: {n}')
    gmsh.initialize()
    gmsh.option.setNumber("General.Terminal", 1)
    gmsh.open(sys.argv[1])
    gmsh.model.mesh.optimize("", force=True, niter=n)
    gmsh.write(sys.argv[2])
    gmsh.finalize()
