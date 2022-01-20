import gmsh


class Refine:
    """Abstract
    """

    def __init__(self):
        pass

    def __call__(self, block=None):
        pass


class NoRefine(Refine):

    def __init__(self):
        super().__init__()

    def __call__(self, block=None):
        pass


class RefineBySplit(Refine):
    """
    Args:
        n_iterations (int): Number of iterations
    """

    def __init__(self, n_iterations=1):
        super().__init__()
        self.n_iterations = n_iterations

    def __call__(self, block=None):
        for _ in range(self.n_iterations):
            gmsh.model.mesh.refine()


str2obj = {
    Refine.__name__: Refine,
    NoRefine.__name__: Refine,
    RefineBySplit.__name__: RefineBySplit,
}
