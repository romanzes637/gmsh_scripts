import gmsh

from matrix import Matrix


class RegularBoundMatrix(Matrix):
    def __init__(self, factory='geo', transform_data=None,
                 nxi=3, nyj=2, nzk=1,
                 dx0=1, dy0=3, dz0=3,
                 dxi=1, dyj=2, dzk=3,
                 dx1=1, dy1=3, dz1=3,
                 inputs=None,
                 x0_y0_z0=None, xi_y0_z0=None, x1_y0_z0=None,
                 x0_yj_z0=None, xi_yj_z0=None, x1_yj_z0=None,
                 x0_y1_z0=None, xi_y1_z0=None, x1_y1_z0=None,
                 x0_y0_zk=None, xi_y0_zk=None, x1_y0_zk=None,
                 x0_yj_zk=None, xi_yj_zk=None, x1_yj_zk=None,
                 x0_y1_zk=None, xi_y1_zk=None, x1_y1_zk=None,
                 x0_y0_z1=None, xi_y0_z1=None, x1_y0_z1=None,
                 x0_yj_z1=None, xi_yj_z1=None, x1_yj_z1=None,
                 x0_y1_z1=None, xi_y1_z1=None, x1_y1_z1=None):
        transform_data = [] if transform_data is None else transform_data
        coordinates_type = 'delta'
        # n = (nxi + 2)*(nyj + 2)*(nzk + 2)
        # print(nxi, nyj, nzk, n)
        xs = [dx0] + [dxi for _ in range(nxi)] + [dx1]
        ys = [dy0] + [dyj for _ in range(nyj)] + [dy1]
        zs = [dz0] + [dzk for _ in range(nzk)] + [dz1]
        global_index_map = {
            (-1, -1, -1): x0_y0_z0,
            (0, -1, -1): xi_y0_z0,
            (1, -1, -1): x1_y0_z0,
            (-1, 0, -1): x0_yj_z0,
            (0, 0, -1): xi_yj_z0,
            (1, 0, -1): x1_yj_z0,
            (-1, 1, -1): x0_y1_z0,
            (0, 1, -1): xi_y1_z0,
            (1, 1, -1): x1_y1_z0,
            (-1, -1, 0): x0_y0_zk,
            (0, -1, 0): xi_y0_zk,
            (1, -1, 0): x1_y0_zk,
            (-1, 0, 0): x0_yj_zk,
            (0, 0, 0): xi_yj_zk,
            (1, 0, 0): x1_yj_zk,
            (-1, 1, 0): x0_y1_zk,
            (0, 1, 0): xi_y1_zk,
            (1, 1, 0): x1_y1_zk,
            (-1, -1, 1): x0_y0_z1,
            (0, -1, 1): xi_y0_z1,
            (1, -1, 1): x1_y0_z1,
            (-1, 0, 1): x0_yj_z1,
            (0, 0, 1): xi_yj_z1,
            (1, 0, 1): x1_yj_z1,
            (-1, 1, 1): x0_y1_z1,
            (0, 1, 1): xi_y1_z1,
            (1, 1, 1): x1_y1_z1}
        inputs = [] if inputs is None else inputs
        inputs_map, type_map = [], []
        for k in range(-1, nzk + 2 - 1):
            for j in range(-1, nyj + 2 - 1):
                for i in range(-1, nxi + 2 - 1):
                    gi = (i // nxi, j // nyj, k // nzk)
                    # print(gi)
                    item = global_index_map[gi]
                    if item is not None:
                        if isinstance(item[0], str):
                            inputs.append(item[0])
                            inputs_map.append(len(inputs) - 1)
                        else:
                            inputs_map.append(item[0])
                        type_map.append(item[1])
                    else:
                        inputs_map.append(0)
                        type_map.append(0)
        Matrix.__init__(self, factory, xs, ys, zs, lcs=None,
                        coordinates_type=coordinates_type,
                        transform_data=transform_data,
                        txs=None, tys=None, tzs=None,
                        type_map=type_map, inputs=inputs,
                        volumes_map=None, volumes_names=None,
                        surfaces_map=None, surfaces_names=None,
                        inputs_map=inputs_map,
                        recs_map=None, trans_map=None)


