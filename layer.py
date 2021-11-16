
from matrix import Matrix
from coordinate_system import LayerXY


class Layer(Matrix):
    def __init__(self, factory, layers=None, curves_names=None, layers_types=None):
        lxy = LayerXY(layers=[
            [1, 2, 3, 4],
            [1, 2, 3, 4],
            [1, 2, 3, 4],
            [1, 2, 3, 4]])
        points = [[1, 2], [1, 2], [1, 2], lxy]
        super().__init__(factory=factory,
                         points=points,
                         transforms=['lxy2car'])
