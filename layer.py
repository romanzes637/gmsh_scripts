from matrix import Matrix
from coordinate_system import LayerXY

import numpy as np


class Layer(Matrix):
    def __init__(self, layers=None, layers_curves_names=None, layers_types=None,
                 do_register_map=None):
        if len(layers) != 2:
            raise NotImplementedError(layers)
        coords, n2o_g2g = self.parse_layers(layers)
        print(n2o_g2g)
        # Points and Coordinate system
        xys = [-1*x for x in reversed(coords[0][1:])] + coords[0][1:]
        zs = coords[1]
        lxy = LayerXY(layers=layers[:-1],
                      curves_names=layers_curves_names[:-1],
                      layers_types=layers_types[:-1])
        points = [xys, xys, zs, lxy]
        # new_do_register_map
        do_register_map = [do_register_map[x] for x in n2o_g2g]
        print(do_register_map)
        n_xy = int(len(do_register_map) / 2)
        print(n_xy)
        n_z = len(layers[-1])
        new_do_register_map = []
        for i in range(n_z):
            xs = do_register_map[i * n_xy:(i + 1) * n_xy]
            xs = xs[::-1] + xs[1:]
            new_do_register_map.append(xs)
        print(new_do_register_map)
        reg_map = np.zeros([len(x) - 1 for x in reversed(points[:3])], dtype=int)
        mean_xy = int((len(xys) - 1) / 2)
        print(mean_xy)
        for i, x in np.ndenumerate(reg_map):
            print(i, x)
            zi, yi, xi = i
            if yi == mean_xy:
                reg_map[i] = 1
                # reg_map[i] = new_do_register_map[zi][xi]
            if xi == mean_xy:
                reg_map[i] = 1
                # reg_map[i] = new_do_register_map[zi][yi]
        print(reg_map)
        print(reg_map.flatten())
        print(points)
        do_register_map = reg_map.flatten().tolist()

        super().__init__(points=points,
                         transforms=[LayerXY.__name__],
                         do_register_map=do_register_map)

    @staticmethod
    def parse_layers(layers):
        layers = [[0] + x for x in layers]
        grid, coordinates, _, new2old, _ = Matrix.parse_grid(layers)
        print(grid)
        print(coordinates)
        # Old global to old local
        old_grid = [x[2:] for x in grid]  # remove type and first/start point
        old_l2g, old_g2l = Matrix.local_global_maps(old_grid)
        print(old_g2l)
        # Evaluate blocks points and new global to new local
        new_grid = [x[1:] for x in coordinates]  # remove first point
        print(new_grid)
        new_l2g, new_g2l = Matrix.local_global_maps(new_grid)
        rows_new2old_maps = [{k - 1: v - 1 for k, v in x.items() if v != 0}
                             for x in new2old]
        n2o_g2g, o2n_g2g = Matrix.new_old_maps(old_grid, new_grid,
                                               rows_new2old_maps)
        return coordinates, n2o_g2g
        # blocks_points, new2old = Matrix.parse_matrix_points(layers)
        # print(coordinates)
        # print(do_register_map)
        # do_register_map = Matrix.parse_map(do_register_map, 1, new2old,
        #                                    item_types=(bool, int))
        # print(do_register_map)

        # lxy = LayerXY(layers=layers_xy, curves_names=curves_names_xy,
        #               layers_types=layers_types_xy)

        # points = [[-4, -3, -2, -1, 1, 2, 3, 4],
        #           [-4, -3, -2, -1, 1, 2, 3, 4],
        #           layer_z,
        #           lxy]
        # layers_xy, layer_z = layers[:-1], layers[-1]
        # curves_names_xy, curves_names_z = curves_names[:-1], curves_names[-1]
        # layers_types_xy, layers_types_z = layers_types[:-1], layers_types[-1]
        #
        # if len(layers_xy) == 1:  # X = Y = NX = NY
        #     layers_xy = [layers_xy[0] for _ in range(4)]
        #     curves_names_xy = [curves_names_xy[0] for _ in range(4)]
        #     layers_types_xy = [layers_types_xy[0] for _ in range(4)]
        # else:
        #     raise NotImplementedError(layers_xy)
        # lxy = LayerXY(layers=layers_xy, curves_names=curves_names_xy,
        #               layers_types=layers_types_xy)
        # curves_names = [[curves_names[i][new2old[i][j]] for j, y in enumerate(x)]
        #                 for i, x in enumerate(coordinates)]
        # for i in [2, 3]:  # Negative NX, NY
        #     coordinates[i] = [-x for x in coordinates[i]]
        # points = [[-4, -3, -2, -1, 1, 2, 3, 4],
        #           [-4, -3, -2, -1, 1, 2, 3, 4],
        #           layer_z,
        #           lxy]

        # do_register_map = [
        #         0, 0, 0, 1, 0, 0, 0,
        #         0, 0, 0, 1, 0, 0, 0,
        #         0, 0, 0, 1, 0, 0, 0,
        #         1, 1, 1, 1, 1, 1, 1,
        #         0, 0, 0, 1, 0, 0, 0,
        #         0, 0, 0, 1, 0, 0, 0,
        #         0, 0, 0, 1, 0, 0, 0,
        #
        #         0, 0, 0, 1, 0, 0, 0,
        #         0, 0, 0, 1, 0, 0, 0,
        #         0, 0, 0, 1, 0, 0, 0,
        #         1, 1, 1, 1, 1, 1, 1,
        #         0, 0, 0, 1, 0, 0, 0,
        #         0, 0, 0, 1, 0, 0, 0,
        #         0, 0, 0, 1, 0, 0, 0,
        #     ],
        # structure_type=['LLL', 'LRR', 'RLR', 'RRL'],
        # structure_type_map=[
        #     0, 0, 0, 2, 0, 0, 0,
        #     0, 0, 0, 2, 0, 0, 0,
        #     0, 0, 0, 2, 0, 0, 0,
        #     1, 1, 1, 0, 0, 0, 0,
        #     0, 0, 0, 0, 0, 0, 0,
        #     0, 0, 0, 0, 0, 0, 0,
        #     0, 0, 0, 0, 0, 0, 0,
        #
        #     0, 0, 0, 2, 0, 0, 0,
        #     0, 0, 0, 2, 0, 0, 0,
        #     0, 0, 0, 2, 0, 0, 0,
        #     1, 1, 1, 0, 0, 0, 0,
        #     0, 0, 0, 0, 0, 0, 0,
        #     0, 0, 0, 0, 0, 0, 0,
        #     0, 0, 0, 0, 0, 0, 0,
        # ],

        # b = BlockObject(factory=factory, do_register=False)
        # m = Matrix(
        #     points=[[-4, -3, -2, -1, 1, 2, 3, 4],
        #             [-4, -3, -2, -1, 1, 2, 3, 4],
        #             [0, 1, 2], lxy],
        #     curves=[
        #         # 0 L1 Center
        #         [['line'], ['line'], ['line'], ['line'],
        #          ['line'], ['line'], ['line'], ['line'],
        #          ['line'], ['line'], ['line'], ['line']],
        #         # TODO Bug surface filling of all circle_arc with GEO factory
        #         # [['circle_arc', [[0, 0, 0]]],
        #         #  ['circle_arc', [[0, 0, 1]]],
        #         #  ['circle_arc', [[0, 0, 1]]],
        #         #  ['circle_arc', [[0, 0, 0]]],
        #         #  ['circle_arc', [[0, 0, 0]]],
        #         #  ['circle_arc', [[0, 0, 0]]],
        #         #  ['circle_arc', [[0, 0, 1]]],
        #         #  ['circle_arc', [[0, 0, 1]]],
        #         #  ['line'], ['line'], ['line'], ['line']],
        #         # 1 L2 X1
        #         [['line'], ['line'], ['line'], ['line'],
        #          ['circle_arc', [[0, 0, 0]]],
        #          ['line'],
        #          ['line'],
        #          ['circle_arc', [[0, 0, 1]]],
        #          ['line'], ['line'], ['line'], ['line']],
        #         # 2 L2 X2
        #         [['line'], ['line'], ['line'], ['line'],
        #          ['circle_arc', [[0, 0, 1]]],
        #          ['line'],
        #          ['line'],
        #          ['circle_arc', [[0, 0, 2]]],
        #          ['line'], ['line'], ['line'], ['line']],
        #         # 3 L2 Y1
        #         [['circle_arc', [[0, 0, 0]]],
        #          ['circle_arc', [[0, 0, 1]]],
        #          ['line'],
        #          ['line'],
        #          ['line'], ['line'], ['line'], ['line'],
        #          ['line'], ['line'], ['line'], ['line']],
        #         # 4 L2 Y2
        #         [['circle_arc', [[0, 0, 1]]],
        #          ['circle_arc', [[0, 0, 2]]],
        #          ['line'],
        #          ['line'],
        #          ['line'], ['line'], ['line'], ['line'],
        #          ['line'], ['line'], ['line'], ['line']],
        #         # 5 L2 NX1
        #         [['line'], ['line'], ['line'], ['line'],
        #          ['line'],
        #          ['circle_arc', [[0, 0, 0]]],
        #          ['circle_arc', [[0, 0, 1]]],
        #          ['line'],
        #          ['line'], ['line'], ['line'], ['line']],
        #         # 6 L2 NX2
        #         [['line'], ['line'], ['line'], ['line'],
        #          ['line'],
        #          ['circle_arc', [[0, 0, 1]]],
        #          ['circle_arc', [[0, 0, 2]]],
        #          ['line'],
        #          ['line'], ['line'], ['line'], ['line']],
        #         # 7 L2 NY1
        #         [['line'],
        #          ['line'],
        #          ['circle_arc', [[0, 0, 1]]],
        #          ['circle_arc', [[0, 0, 0]]],
        #          ['line'], ['line'], ['line'], ['line'],
        #          ['line'], ['line'], ['line'], ['line']],
        #         # 8 L2 NY2
        #         [['line'],
        #          ['line'],
        #          ['circle_arc', [[0, 0, 2]]],
        #          ['circle_arc', [[0, 0, 1]]],
        #          ['line'], ['line'], ['line'], ['line'],
        #          ['line'], ['line'], ['line'], ['line']],
        #         # 9 L3 X1
        #         [['line'], ['line'], ['line'], ['line'],
        #          ['circle_arc', [[0, 0, 0]]],
        #          ['circle_arc', [[0, 0, 0]]],
        #          ['circle_arc', [[0, 0, 1]]],
        #          ['circle_arc', [[0, 0, 1]]],
        #          ['line'], ['line'], ['line'], ['line']],
        #         # 10 L3 X2
        #         [['line'], ['line'], ['line'], ['line'],
        #          ['circle_arc', [[0, 0, 1]]],
        #          ['circle_arc', [[0, 0, 1]]],
        #          ['circle_arc', [[0, 0, 2]]],
        #          ['circle_arc', [[0, 0, 2]]],
        #          ['line'], ['line'], ['line'], ['line']],
        #         # 11 L3 Y1
        #         [['circle_arc', [[0, 0, 0]]],
        #          ['circle_arc', [[0, 0, 1]]],
        #          ['circle_arc', [[0, 0, 1]]],
        #          ['circle_arc', [[0, 0, 0]]],
        #          ['line'], ['line'], ['line'], ['line'],
        #          ['line'], ['line'], ['line'], ['line']],
        #         # 12 L3 Y2
        #         [['circle_arc', [[0, 0, 1]]],
        #          ['circle_arc', [[0, 0, 2]]],
        #          ['circle_arc', [[0, 0, 2]]],
        #          ['circle_arc', [[0, 0, 1]]],
        #          ['line'], ['line'], ['line'], ['line'],
        #          ['line'], ['line'], ['line'], ['line']],
        #         # 13 L3 NX1
        #         [['line'], ['line'], ['line'], ['line'],
        #          ['circle_arc', [[0, 0, 0]]],
        #          ['circle_arc', [[0, 0, 0]]],
        #          ['circle_arc', [[0, 0, 1]]],
        #          ['circle_arc', [[0, 0, 1]]],
        #          ['line'], ['line'], ['line'], ['line']],
        #         # 14 L3 NX2
        #         [['line'], ['line'], ['line'], ['line'],
        #          ['circle_arc', [[0, 0, 1]]],
        #          ['circle_arc', [[0, 0, 1]]],
        #          ['circle_arc', [[0, 0, 2]]],
        #          ['circle_arc', [[0, 0, 2]]],
        #          ['line'], ['line'], ['line'], ['line']],
        #         # 15 L3 NY1
        #         [['circle_arc', [[0, 0, 0]]],
        #          ['circle_arc', [[0, 0, 1]]],
        #          ['circle_arc', [[0, 0, 1]]],
        #          ['circle_arc', [[0, 0, 0]]],
        #          ['line'], ['line'], ['line'], ['line'],
        #          ['line'], ['line'], ['line'], ['line']],
        #         # 16 L3 NY2
        #         [['circle_arc', [[0, 0, 1]]],
        #          ['circle_arc', [[0, 0, 2]]],
        #          ['circle_arc', [[0, 0, 2]]],
        #          ['circle_arc', [[0, 0, 1]]],
        #          ['line'], ['line'], ['line'], ['line'],
        #          ['line'], ['line'], ['line'], ['line']],
        #         # 17 L4 X1
        #         [['line'], ['line'], ['line'], ['line'],
        #          ['line'],
        #          ['circle_arc', [[0, 0, 0]]],
        #          ['circle_arc', [[0, 0, 1]]],
        #          ['line'],
        #          ['line'], ['line'], ['line'], ['line']],
        #         # 18 L4 X2
        #         [['line'], ['line'], ['line'], ['line'],
        #          ['line'],
        #          ['circle_arc', [[0, 0, 1]]],
        #          ['circle_arc', [[0, 0, 2]]],
        #          ['line'],
        #          ['line'], ['line'], ['line'], ['line']],
        #         # 19 L4 Y1
        #         [['line'],
        #          ['line'],
        #          ['circle_arc', [[0, 0, 1]]],
        #          ['circle_arc', [[0, 0, 0]]],
        #          ['line'], ['line'], ['line'], ['line'],
        #          ['line'], ['line'], ['line'], ['line']],
        #         # 20 L4 Y2
        #         [['line'],
        #          ['line'],
        #          ['circle_arc', [[0, 0, 2]]],
        #          ['circle_arc', [[0, 0, 1]]],
        #          ['line'], ['line'], ['line'], ['line'],
        #          ['line'], ['line'], ['line'], ['line']],
        #         # 21 L4 NX1
        #         [['line'], ['line'], ['line'], ['line'],
        #          ['circle_arc', [[0, 0, 0]]],
        #          ['line'],
        #          ['line'],
        #          ['circle_arc', [[0, 0, 1]]],
        #          ['line'], ['line'], ['line'], ['line']],
        #         # 22 L4 NX2
        #         [['line'], ['line'], ['line'], ['line'],
        #          ['circle_arc', [[0, 0, 1]]],
        #          ['line'],
        #          ['line'],
        #          ['circle_arc', [[0, 0, 2]]],
        #          ['line'], ['line'], ['line'], ['line']],
        #         # 23 L4 NY1
        #         [['circle_arc', [[0, 0, 0]]],
        #          ['circle_arc', [[0, 0, 1]]],
        #          ['line'],
        #          ['line'],
        #          ['line'], ['line'], ['line'], ['line'],
        #          ['line'], ['line'], ['line'], ['line']],
        #         # 24 L4 NY2
        #         [['circle_arc', [[0, 0, 1]]],
        #          ['circle_arc', [[0, 0, 2]]],
        #          ['line'],
        #          ['line'],
        #          ['line'], ['line'], ['line'], ['line'],
        #          ['line'], ['line'], ['line'], ['line']],
        #     ],
        #     curves_map=[
        #         0, 0, 0, 23, 0, 0, 0,
        #         0, 0, 0, 15, 0, 0, 0,
        #         0, 0, 0, 7, 0, 0, 0,
        #         21, 13, 5, 0, 1, 9, 17,
        #         0, 0, 0, 3, 0, 0, 0,
        #         0, 0, 0, 11, 0, 0, 0,
        #         0, 0, 0, 19, 0, 0, 0,
        #
        #         0, 0, 0, 24, 0, 0, 0,
        #         0, 0, 0, 16, 0, 0, 0,
        #         0, 0, 0, 8, 0, 0, 0,
        #         22, 14, 6, 0, 2, 10, 18,
        #         0, 0, 0, 4, 0, 0, 0,
        #         0, 0, 0, 12, 0, 0, 0,
        #         0, 0, 0, 20, 0, 0, 0,
        #     ],
        #     transforms=['lxy2car'],
        #     do_register_map=[
        #         0, 0, 0, 1, 0, 0, 0,
        #         0, 0, 0, 1, 0, 0, 0,
        #         0, 0, 0, 1, 0, 0, 0,
        #         1, 1, 1, 1, 1, 1, 1,
        #         0, 0, 0, 1, 0, 0, 0,
        #         0, 0, 0, 1, 0, 0, 0,
        #         0, 0, 0, 1, 0, 0, 0,
        #
        #         0, 0, 0, 1, 0, 0, 0,
        #         0, 0, 0, 1, 0, 0, 0,
        #         0, 0, 0, 1, 0, 0, 0,
        #         1, 1, 1, 1, 1, 1, 1,
        #         0, 0, 0, 1, 0, 0, 0,
        #         0, 0, 0, 1, 0, 0, 0,
        #         0, 0, 0, 1, 0, 0, 0,
        #     ],
        #     structure_type=['LLL', 'LRR', 'RLR', 'RRL'],
        #     structure_type_map=[
        #         0, 0, 0, 2, 0, 0, 0,
        #         0, 0, 0, 2, 0, 0, 0,
        #         0, 0, 0, 2, 0, 0, 0,
        #         1, 1, 1, 0, 0, 0, 0,
        #         0, 0, 0, 0, 0, 0, 0,
        #         0, 0, 0, 0, 0, 0, 0,
        #         0, 0, 0, 0, 0, 0, 0,
        #
        #         0, 0, 0, 2, 0, 0, 0,
        #         0, 0, 0, 2, 0, 0, 0,
        #         0, 0, 0, 2, 0, 0, 0,
        #         1, 1, 1, 0, 0, 0, 0,
        #         0, 0, 0, 0, 0, 0, 0,
        #         0, 0, 0, 0, 0, 0, 0,
        #         0, 0, 0, 0, 0, 0, 0,
        #     ],
        #     structure_map=[[5, 0, 1], [5, 0, 1], [3, 0, 1]],
        #     boolean_level_map=0,
        #     quadrate_map=0)

        # super().__init__(points=points,
        #                  transforms=[LayerXY.__name__])


str2obj = {
    Layer.__name__: Layer,
    Layer.__name__.lower(): Layer
}
