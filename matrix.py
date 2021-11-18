from itertools import product

import numpy as np

from block import Block
from support import beta_pdf, beta_cdf


class Matrix(Block):
    """Matrix

    Args:
    """

    def __init__(self, points,
                 curves=None,
                 curves_map=None,
                 parent=None,
                 transforms=None, use_register_tag=False,
                 do_register_map=None,
                 structure_map=None,
                 quadrate_map=None,
                 boolean_level_map=None,
                 zone_map=None,
                 structure_type=None,
                 structure_type_map=None,
                 # ts=None, txs=None, tys=None, tzs=None,
                 # lcs=None, lcs_map=None,
                 # types=None, type_map=None,
                 # volumes_names=None, volumes_map=None,
                 # surfaces_names=None, surfaces_map=None,
                 # in_surfaces_names=None, in_surfaces_map=None,
                 # in_surfaces_masks=None, in_surfaces_masks_map=None,
                 # transforms=None, transforms_map=None,
                 # inputs=None, inputs_map=None,
                 # kws=None, kws_map=None,
                 # recs_map=None, trans_map=None, trans_type_map=None,
                 # curve_types=None, curve_types_map=None,
                 # curve_data=None, curve_data_map=None,
                 # curve_data_coord_sys=None, curve_data_coord_sys_map=None,
                 # inputs_transforms=None, inputs_transforms_map=None,
                 # inputs_transforms_coord_sys=None,
                 # inputs_transforms_coord_sys_map=None,
                 # boolean_level_map=None,
                 # exists_map=None
                 ):
        blocks_points, new2old = Matrix.parse_matrix_points(points)
        curves_map = Matrix.parse_map(m=curves_map, default=0,
                                      new2old=new2old, item_types=(int,))
        transforms = [] if transforms is None else transforms
        curves = [None] if curves is None else curves
        do_register_map = Matrix.parse_map(do_register_map, True, new2old,
                                           item_types=(bool, int))
        structure_map = Matrix.parse_map(
            structure_map, None, new2old, item_types=(bool, [list]))
        quadrate_map = Matrix.parse_map(quadrate_map, None, new2old)
        boolean_level_map = Matrix.parse_map(boolean_level_map, None, new2old)
        zone_map = Matrix.parse_map(zone_map, None, new2old)
        structure_type = ['LLL'] if structure_type is None else structure_type
        structure_type_map = Matrix.parse_map(structure_type_map, 0, new2old)
        # TODO Optimized version
        children = [Block(points=x,
                          curves=curves[curves_map[i]],
                          use_register_tag=use_register_tag,
                          do_register=do_register_map[i],
                          structure=structure_map[i],
                          quadrate=quadrate_map[i],
                          boolean_level=boolean_level_map[i],
                          zone=zone_map[i],
                          structure_type=structure_type[structure_type_map[i]],
                          parent=self) for i, x in enumerate(blocks_points)
                    if do_register_map[i]]
        # children = [Block(points=x,
        #                   use_register_tag=use_register_tag,
        #                   do_register=do_register_map[i],
        #                   structure=structure_map[i],
        #                   quadrate=quadrate_map[i],
        #                   boolean_level=boolean_level_map[i],
        #                   zone=zone_map[i],
        #                   parent=self) for i, x in enumerate(blocks_points)]
        super().__init__(parent=parent,
                         do_register=False,
                         children=children, transforms=transforms,
                         use_register_tag=use_register_tag)

    @staticmethod
    def parse_grid(grid):
        """Parse coordinates and mesh size grid

        Args:
            grid (list of list or np.ndarray):
                [[type1, coordinate and/or mesh size 1,
                coordinate and/or mesh size 2, ...],
                 [type2, coordinate and/or mesh size 1,
                 coordinate and/or mesh size 2, ...],
                 ...]
                 if type == 'increment', first coordinate is origin
                 where type (str): type of row: 'value' or 'increment',
                 coordinate + mesh size (str or int or float):
                 coordinate and/or mesh size values like:
                 * 1.2 - coordinate
                 * '1.2;3' - coordinate and mesh size
                 * '1.2:3' - 3 coordinates from previous coordinate to 1.2
                 with equal step
                 * '1.2:3;3' - 3 coordinates from previous coordinate to 1.2
                 with equal step and mesh size from previous mesh size to 3
                 with equal step
                 * '1.2:7:0.5:0.7' - 7 coordinates from previous coordinate
                 to 1.2 with step by cumulative distribution function (CDF)
                 of Beta distribution with alpha = 0.5 and beta = 0.7
                 * '1.2:7:0.5:0.7;3:2:1.2:1.3' - 7 coordinates from previous
                 coordinate to 1.2 with step by Cumulative Distribution Function
                 (CDF) of Beta distribution with alpha = 0.5 and beta = 0.7
                 and mesh size by weighted Probability Density Function (PDF)
                 of Beta distribution with alpha = 1.2, beta = 1.3, weight = 2
                 and mean mesh size value = 3

        Returns:
            tuple: tuple containing:
                grid (list of list): corrected grid
                coordinates (list of list of float): coordinates
                mesh_sizes (list of list of float): mesh_sizes
                new2old (list of list if int): new_id to old_id
                old2new (list of dict): old_id to new_ids
        """
        # Correct grid
        for row_i, row in enumerate(grid):
            if isinstance(row, list):
                if row[0] not in ['value', 'increment']:  # 'value' by default
                    row = ['value'] + row
                grid[row_i] = row
            else:
                raise ValueError(row_i, row, grid)
        # Parse grid and evaluate new to old maps for each row
        coordinates, mesh_sizes = [], []
        new2old, old2new = [], []
        for row_i, row in enumerate(grid):
            new2old_i, old2new_i = {}, {}
            row_type = row[0]
            if row_type == 'value':
                cur_c, cur_ms, cs = 0, None, row[1:]
            elif row_type == 'increment':
                if isinstance(row[1], str):
                    vs_ms = row[1].split(';')  # values and mesh size
                    v = float(vs_ms[0])
                    ms = float(vs_ms[1]) if len(vs_ms) > 1 else None
                else:
                    v, ms = row[1], None
                cur_c, cur_ms, cs = v, ms, [0] + row[2:]
            else:
                raise ValueError(row_type)
            cs_i, mss_i = [], []
            for col_i, c in enumerate(cs):  # coordinate
                if isinstance(c, (float, int)):
                    dc = c - cur_c if row_type == 'value' else c
                    cur_c += dc
                    new_i, old_i = len(cs_i), col_i
                    cs_i.append(cur_c)
                    mss_i.append(cur_ms)
                    old2new_i.setdefault(old_i, []).append(new_i)
                    new2old_i[new_i] = old_i
                elif isinstance(c, str):
                    vs_ms = c.split(';')  # values and mesh size
                    vs = vs_ms[0].split(':')
                    ms = vs_ms[1].split(':') if len(vs_ms) > 1 else [None]
                    new_ms = float(ms[0]) if ms[0] is not None else None
                    prev_ms = float(cur_ms) if cur_ms is not None else None
                    if len(ms) == 1:  # linear
                        if prev_ms is None and new_ms is not None:
                            prev_ms = new_ms
                            if len(mss_i) > 0:
                                mss_i[-1] = prev_ms
                        elif prev_ms is not None and new_ms is None:
                            new_ms = prev_ms

                        def get_ms(rel_x):
                            if prev_ms is not None and new_ms is not None:
                                return rel_x * (new_ms - prev_ms) + prev_ms
                            else:
                                return None
                    elif len(ms) == 4:  # Beta with weight
                        w_ms = float(ms[1])
                        a_ms, b_ms = float(ms[2]), float(ms[3])
                        if prev_ms is None and new_ms is not None:
                            k = beta_pdf(0, a_ms, b_ms)
                            k *= w_ms  # Weight
                            k = k + 1 if k >= 0 else 1 / -k
                            prev_ms = new_ms
                            if len(mss_i) > 0:
                                mss_i[-1] = prev_ms * k
                        elif prev_ms is not None and new_ms is None:
                            new_ms = prev_ms

                        def get_ms(rel_x):
                            kx = beta_pdf(rel_x, a_ms, b_ms)
                            kx *= w_ms  # Weight
                            kx = kx + 1 if kx >= 0 else 1 / -kx
                            if prev_ms is not None and new_ms is not None:
                                return kx * (rel_x * (new_ms - prev_ms) + prev_ms)
                            else:
                                return None
                    else:
                        raise ValueError(ms)
                    if len(vs) == 1:  # One step
                        c = float(vs[0])
                        dc = c - cur_c if row_type == 'value' else c
                        cur_c += dc
                        cur_ms = get_ms(1)
                        new_i, old_i = len(cs_i), col_i
                        cs_i.append(cur_c)
                        mss_i.append(cur_ms)
                        old2new_i.setdefault(old_i, []).append(new_i)
                        new2old_i[new_i] = old_i
                    elif len(vs) == 2:  # Uniform step
                        c, n = float(vs[0]), int(vs[1])
                        dc = c - cur_c if row_type == 'value' else c
                        prev_c = cur_c
                        for x in np.linspace(cur_c, cur_c + dc, n)[1:]:
                            cur_c = x
                            rel_c = (cur_c - prev_c) / dc
                            cur_ms = get_ms(rel_c)
                            new_i, old_i = len(cs_i), col_i
                            cs_i.append(x)
                            mss_i.append(cur_ms)
                            old2new_i.setdefault(old_i, []).append(new_i)
                            new2old_i[new_i] = old_i
                    elif len(vs) == 4:  # Beta distribution step
                        c, n, = float(vs[0]), int(vs[1])
                        a, b = float(vs[2]), float(vs[3])
                        dc = c - cur_c if row_type == 'value' else c
                        xs = beta_cdf(np.linspace(0, 1, n), a, b)
                        for i, x in enumerate(xs[1:], start=1):
                            dx = xs[i] - xs[i - 1]
                            cur_c += dc * dx
                            cur_ms = get_ms(x)
                            new_i, old_i = len(cs_i), col_i
                            cs_i.append(cur_c)
                            mss_i.append(cur_ms)
                            old2new_i.setdefault(old_i, []).append(new_i)
                            new2old_i[new_i] = old_i
                    else:
                        raise ValueError(col_i, c, grid)
            coordinates.append(cs_i)
            mesh_sizes.append(mss_i)
            new2old.append(new2old_i)
            old2new.append(old2new_i)
        return grid, coordinates, mesh_sizes, new2old, old2new

    @staticmethod
    def parse_matrix_points(points):
        # Split rows by type
        list_rows = [x for x in points if isinstance(x, list)]
        num_rows = [x for x in points if isinstance(x, (int, float))]
        str_rows = [x for x in points if isinstance(x, str)]
        other_rows = [x for x in points
                      if not isinstance(x, (list, int, str, float))]
        # Parse list rows and evaluate new to old maps for each row
        grid, rows_coords, rows_mesh_sizes, rows_new2old, rows_old2new = Matrix.parse_grid(list_rows)
        # Parse str rows
        coordinate_system = str_rows[0] if len(str_rows) > 0 else 'cartesian'
        params_expand_type = str_rows[1] if len(str_rows) > 1 else 'trace'
        # Parse num rows
        global_mesh_size = num_rows[0] if len(num_rows) > 0 else None
        # Parse other rows
        coordinate_system = other_rows[0] if len(other_rows) > 0 else coordinate_system
        # Split points into coordinates and parameters
        coords, params = rows_coords[:3], rows_coords[3:]
        mesh_sizes, params_mesh_sizes = rows_mesh_sizes[:3], rows_mesh_sizes[3:]
        if len(params) > 0:
            if params_expand_type == 'trace':
                min_len = min(len(x) for x in params)
                params = [[x[i] for x in params] for i in range(min_len)]
            elif params_expand_type == 'product':
                params = [list(x) for x in product(*params)]
            else:
                raise ValueError(params_expand_type)
        else:
            params = [[]]
        # Old global to old local
        old_grid = [x[2:] for x in grid]  # remove type and first/start point
        old_grid += params
        old_l2g, old_g2l = Matrix.local_global_maps(old_grid)
        # Evaluate blocks points and new global to new local
        new_grid = [x[1:] for x in coords]  # remove first point
        new_grid += params
        new_l2g, new_g2l = Matrix.local_global_maps(new_grid)
        # New to old
        # Move rows maps on 1 step (due to first/start point remove above)
        rows_new2old_maps = [{k - 1: v - 1 for k, v in x.items() if v != 0}
                             for x in rows_new2old[:3]]
        rows_new2old_maps += [{i: i for i, _ in enumerate(params)}]
        print(rows_new2old_maps)
        n2o_g2g, o2n_g2g = Matrix.new_old_maps(old_grid, new_grid,
                                               rows_new2old_maps)
        # Block points
        blocks_points = []
        for gi, li in enumerate(new_g2l):
            pi, zi, yi, xi = li
            p = params[pi]
            cur_z, prev_z = coords[2][zi+1], coords[2][zi]
            cur_y, prev_y = coords[1][yi+1], coords[1][yi]
            cur_x, prev_x = coords[0][xi+1], coords[0][xi]
            cur_z_ms, prev_z_ms = mesh_sizes[2][zi+1], mesh_sizes[2][zi]
            cur_y_ms, prev_y_ms = mesh_sizes[1][yi+1], mesh_sizes[1][yi]
            cur_x_ms, prev_x_ms = mesh_sizes[0][xi+1], mesh_sizes[0][xi]
            block_mesh_sizes = [
                [cur_x_ms, cur_y_ms, prev_z_ms],
                [prev_x_ms, cur_y_ms, prev_z_ms],
                [prev_x_ms, prev_y_ms, prev_z_ms],
                [cur_x_ms, prev_y_ms, prev_z_ms],
                [cur_x_ms, cur_y_ms, cur_z_ms],
                [prev_x_ms, cur_y_ms, cur_z_ms],
                [prev_x_ms, prev_y_ms, cur_z_ms],
                [cur_x_ms, prev_y_ms, cur_z_ms]]
            ms = [np.mean([y for y in x if y is not None])
                  for x in block_mesh_sizes]
            # Replace np.nan with global_mesh_size
            ms = [x if not np.isnan(x) else global_mesh_size for x in ms]
            # Convert to lists (empty list if ms == 0)
            ms = [[x] if x is not None else [] for x in ms]
            # Points
            block_points = [
                [cur_x, cur_y, prev_z] + p + ms[0],
                [prev_x, cur_y, prev_z] + p + ms[1],
                [prev_x, prev_y, prev_z] + p + ms[2],
                [cur_x, prev_y, prev_z] + p + ms[3],
                [cur_x, cur_y, cur_z] + p + ms[4],
                [prev_x, cur_y, cur_z] + p + ms[5],
                [prev_x, prev_y, cur_z] + p + ms[6],
                [cur_x, prev_y, cur_z] + p + ms[7],
                coordinate_system]
            blocks_points.append(block_points)
        return blocks_points, n2o_g2g

    @staticmethod
    def parse_map(m, default, new2old, item_types=(bool, str, int, float)):
        # Default value for all items if map is None
        if m is None:
            m = [default for _ in new2old]
            return m
        # Check on single item of type in item_types
        for t in item_types:
            if isinstance(t, list):  # list of ...
                if isinstance(m, list):
                    if all(isinstance(m2, t2) for t2 in t for m2 in m):
                        m = [m for _ in new2old]
                        return m
            elif isinstance(m, t):  # non list types
                m = [m for _ in new2old]
                return m
        # Old list to new list
        if isinstance(m, list):
            m = [m[old_i] for old_i in new2old]
            return m
        else:  # Something wrong
            raise ValueError(m)

    @staticmethod
    def local_global_maps(grid):
        """Local to global and global to local maps for 2D grid

        Grid
            Local ids:
                1, 2, 3, 4  - by 1 row
                1, 2, 3     - by 2 row
                1, 2        - by 3 row

            Global ids:
                1, 2, ..., 24 - global ids

        Maps:
            g  - (l3, l2, l1)
            0  - (1,  1,  1)
            1  - (1,  1,  2)
            2  - (1,  1,  3)
            3  - (1,  1,  4)
            4  - (1,  2,  1)
            5  - (1,  2,  2)
            6  - (1,  2,  3)
            7  - (1,  2,  4)
            ...
            16 - (2,  2,  1)
            17 - (2,  2,  2)
            18 - (2,  2,  3)
            19 - (2,  2,  4)
            20 - (2,  3,  1)
            21 - (2,  3,  2)
            22 - (2,  3,  3)
            23 - (2,  3,  4)
        """
        l2g, g2l = {}, []
        lens = [len(x) for x in reversed(grid)]
        ids = [range(x) if x != 0 else [0] for x in lens]
        for l in product(*ids):
            g = int(np.sum([np.prod(lens[i + 1:]) * x for i, x in enumerate(l)]))
            l2g[l] = g
            g2l.append(l)
        return l2g, g2l

    @staticmethod
    def new_old_maps(old_grid, new_grid, new2old_rows):
        """New to old and old to new blocks indices map

            0    1    2    - old blocks
            | \ / \ / |
            0  1   2  3    - old row
            | / \ / \ |
            0 1 2 3 4 5    - new row
            |/|/|/|/|/
            0 1 2 3 4      - new blocks
        """
        n2o_g2g, o2n_g2g = [], {}
        o_l2g, o_g2l = Matrix.local_global_maps(old_grid)
        n_l2g, n_g2l = Matrix.local_global_maps(new_grid)
        for n_g, n_l in enumerate(n_g2l):
            o_l = tuple(new2old_rows[::-1][i][x] for i, x in enumerate(n_l))
            o_g = o_l2g[o_l]
            n2o_g2g.append(o_g)
            o2n_g2g.setdefault(o_g, []).append(n_g)
        return n2o_g2g, o2n_g2g


str2obj = {
    Matrix.__name__: Matrix,
    Matrix.__name__.lower(): Matrix
}
