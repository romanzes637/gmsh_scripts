from itertools import product

import numpy as np

from gmsh_scripts.support.support import beta_cdf, beta_pdf


def parse_row(row, sep_i=';', sep_si=':'):
    """Parse row of grid or layers

    Item types:
        1. 'v' - value
        2. 'i' - increment

    Row types:
        1. 'p' - product
        2. 's' - slice

    Types (first item of the row):
        1. 'v;p' - item value, row product
        2. 'v;s' - item value, row slice
        3. 'i;p' - item increment, row product
        4. 'i;s' - item increment, row slice

    Args:
        row (list): row to parse, [t, i0 (origin), i1, i2, ..., iN], where
            t - type, i - item
        sep_i (str): items separator
        sep_si (str): sub-items separator

    Returns:
        tuple:
            row (list): corrected row,
            values (list): [coordinates, mesh sizes, structures],
            maps (list): [o_b2is, o_is2b, n_b2is, n_is2b, n2o_i2i, n2o_b2b],
                where 2 - to, o - old, n - new, b - block, is - indices
    """
    # Check row
    if not isinstance(row, list):  # Non list row
        return row, [[], [], []], [[], {}, [], {}, [], []]
    if len(row) == 0:  # Empty row
        return row, [[], [], []], [[], {}, [], {}, [], []]
    # Correct row
    if row[0] in ['v', 'i']:  # Product type default
        row[0] = row[0] + ';p'
    if row[0] not in ['v;p', 'v;s', 'i;p', 'i;s']:  # Not in types
        row = ['v;p'] + row
    # Parse types
    ts, items = row[0], row[1:]  # types, items
    item_t, row_t = ts.split(sep_i)  # item type, row type
    # Old maps
    n_items, n_blocks = len(items), len(items) - 1
    o_b2is = [(x, x + 1) for x in range(n_blocks)]  # Old block to items
    o_is2b = {x: i for i, x in enumerate(o_b2is)}  # Old items to block
    # Parse row
    cs, ms, ss = [], [], []  # coordinates, mesh sizes, structures
    pc, pm, ps = 0, None, None  # previous (default) values
    n2o_i2i = []  # New item to old item map
    for o_i, item in enumerate(items):  # Old index, old item
        cs_i, ms_i, ss_i = parse_row_item(
            item, item_t, pc, pm, ps, sep_i, sep_si)
        # TODO interpolate between last context/ms/ss and first cs_i/ms_i/ss_i?
        cs.extend(cs_i[1:])
        ms.extend(ms_i[1:])
        ss.extend(ss_i[1:])
        for _ in cs_i[1:]:
            n2o_i2i.append(o_i)
        pc, pm, ps = cs[-1], ms[-1], ss[-1]
    # New maps
    n_n_items, n_n_blocks = len(n2o_i2i), len(n2o_i2i) - 1
    n_b2is = [(x, x + 1) for x in range(n_n_blocks)]  # New block to items
    n_is2b = {x: i for i, x in enumerate(n_b2is)}  # New items to block
    # New block to old block map
    n2o_b2b = []
    for n_bi in range(n_n_blocks):
        o_cs = (n2o_i2i[n_bi], n2o_i2i[n_bi + 1])
        while o_cs[0] == o_cs[1] and n_bi >= 0 and o_cs[0] != 0:  # new items can refer to same old items
            n_bi -= 1
            o_cs = (n2o_i2i[n_bi], o_cs[1])
        if o_cs[0] == o_cs[1] == 0:
            o_is2b.update({(0, 0): 0})  # TODO Workaround for layer
        old_bi = o_is2b[o_cs]
        n2o_b2b.append(old_bi)
    # Return
    values = [cs, ms, ss]
    maps = [o_b2is, o_is2b, n_b2is, n_is2b, n2o_i2i, n2o_b2b]
    return row, values, maps


def parse_row_item(item, item_t, pc, pm, ps, sep_i, sep_ii):
    cs, ms, ss = [], [], []
    if isinstance(item, (float, int)):
        c, m, s = item, None, None  # coordinate, mesh size, structure
        dc = c - pc if item_t == 'v' else c
        cs.extend([pc, pc + dc])
        ms.extend([m, m])
        ss.extend([s, s])
    elif isinstance(item, str):
        vs = item.split(sep_i)
        if len(vs) == 1:
            c, m, s = vs[0], None, None
        elif len(vs) == 2:
            c, m, s = vs[0], vs[1], None
        elif len(vs) == 3:
            c, m, s = vs
        else:
            raise ValueError(item)
        cs = parse_row_item_coordinate(c, pc, item_t, sep_ii)
        ms = parse_row_item_mesh_size(m, pm, cs, pc, sep_ii)
        ss = parse_row_item_structure(s, cs, sep_ii)
    else:
        raise ValueError(item)
    return cs, ms, ss


def parse_row_item_coordinate(c, pc, item_t, sep):
    """Parse coordinate item of grid row

    Args:
        c (str): col to parse, variants:
            1. "c:n" (uniform): coordinate (float), number of steps (int)
            2. "c:n:a:b" (Beta CDF): coordinate (float), number of steps (int),
                alpha (float), beta (float)
        pc (float): previous coordinate
        item_t (str): item type
        sep (str): values separator

    Returns:
        list of float: new coordinates
    """
    if c is None:
        raise ValueError(c)
    vs = c.split(sep)
    cs = []
    if len(vs) == 1:  # simple coordinate
        c = float(vs[0])
        dc = c - pc if item_t == 'v' else c
        cs = [pc, pc + dc]
    elif len(vs) == 2:  # uniform step
        c, n = float(vs[0]), int(vs[1])  # coordinate, number of steps
        dc = c - pc if item_t == 'v' else c
        for x in np.linspace(pc, pc + dc, n):
            cs.append(x)
    elif len(vs) == 4:
        c, n, a, b = float(vs[0]), int(vs[1]), float(vs[2]), float(vs[3])
        dc = c - pc if item_t == 'v' else c
        xs = beta_cdf(np.linspace(0, 1, n), a, b)
        for i, x in enumerate(xs):
            new_c = pc + dc * x
            cs.append(new_c)
    else:
        raise ValueError(vs)
    return cs


def parse_row_item_mesh_size(m, pm, cs, pc, sep):
    """Parse mesh size item of grid row

    Args:
        m (str): col to parse, variants:
            1. "m" (direct): mesh size (float)
            2. "m:w:a:b" (Beta PDF): mesh size (float), weight (float),
                alpha (float), beta (float)
        pm (float): previous mesh size
        cs (list of float): coordinates
        pc (float): previous coordinate
        sep (str): values separator

    Returns:
        list of float: mesh size for each coordinate
    """
    if m is None:
        return [None for _ in cs]
    if len(m) == 0:  # Empty string
        return [None for _ in cs]
    vs = m.split(sep)
    ms = []
    if len(vs) == 1:  # linear
        m = float(m)
        pm = m if pm is None else pm
        dm = m - pm
        dc = cs[-1] - pc
        for c in cs:
            rel_c = (c - pc) / dc if dc != 0 else 0
            new_m = rel_c * dm + pm
            ms.append(new_m)
    elif len(vs) == 4:
        m, w, a, b = float(vs[0]), float(vs[1]), float(vs[2]), float(vs[3])
        pm = m if pm is None else pm
        dm = m - pm
        dc = cs[-1] - pc
        for c in cs:
            rel_c = (c - pc) / dc if dc != 0 else 0
            k = beta_pdf(rel_c, a, b)
            k *= w
            k = k + 1 if k >= 0 else 1 / -k
            new_m = k * (rel_c * dm + pm)
            ms.append(new_m)
    else:
        raise ValueError(vs)
    return ms


def parse_row_item_structure(s, cs, sep=':'):
    """Parse structure col of grid row

    TODO interpolation of number of nodes between coordinates?
    Args:
        s (str): col to parse, variants:
            1. "n": number of nodes (int)
            2. "n:t": number of nodes (int), type (int):
                0 - Progression (default), 1 - Bump, 2 - Beta
            3. "n:t:k": number of nodes (int), type (int):
                0 - Progression (default), 1 - Bump, 2 - Beta,
                coefficient (float) from 0 to inf, default 1.0
        cs (list of float): coordinates,
        sep (str): values separator

    Returns:
        list of list: [[number of nodes, type, coefficient], ..., n coordinates]
    """
    if s is None:
        return [None for _ in cs]
    if len(s) == 0:  # Empty string
        return [None for _ in cs]
    vs = s.split(sep)
    if len(vs) == 1:
        n, t, k = int(vs[0]), 0, 1.
    elif len(vs) == 2:
        n, t, k = int(vs[0]), int(vs[1]), 1.
    elif len(vs) == 3:
        n, t, k = int(vs[0]), int(vs[1]), float(vs[2])
    else:
        raise ValueError(vs)
    ss = [[n, t, k] for _ in cs]
    return ss


def parse_grid(grid, sep_i=';', sep_si=':'):
    """Parse grid

    Args:
        grid (list of list): list of rows
        sep_i (str): items separator
        sep_si (str): sub-items separator

    Returns:
        tuple: grid, values, maps
    """
    # Parse grid rows
    new_grid, grid_values, grid_maps = [], [], []
    for row in grid:
        new_row, values, maps = parse_row(row, sep_i, sep_si)
        new_grid.append(new_row)
        grid_values.append(values)
        grid_maps.append(maps)
    # Split list rows into slice and product rows
    product_list_rows, slice_list_rows = [], []
    for i, row in enumerate(new_grid):
        if isinstance(row, list):
            ts, items = row[0], row[1:]  # types, items
            item_t, row_t = ts.split(sep_i)  # item type, row type
            if row_t == 'p':
                product_list_rows.append(i)
            elif row_t == 's':
                slice_list_rows.append(i)
            else:
                raise ValueError(row_t)
    if len(product_list_rows) != 0 and len(slice_list_rows) != 0:
        # Old maps
        old_b2is, old_is2b = [], {}  # Items indices to block
        old_b2b_g2l, old_b2b_l2g = [], {}  # Block global to local index
        slice_lens = {len(new_grid[x][1:]) for x in slice_list_rows}
        if len(slice_lens) != 1:
            raise ValueError(f'Length of slice rows should be equal: {slice_lens}')
        slice_len = list(slice_lens)[0]
        product_lens = [len(new_grid[x][1:]) for x in product_list_rows[::-1]]
        slice_row_is = [tuple(i for _ in slice_list_rows) for i in range(slice_len)]
        product_rows_is = list(product(*[range(x - 1) for x in product_lens]))
        for i, si in enumerate(slice_row_is):
            for pi in product_rows_is:
                items_local_index = (si, pi, tuple(x + 1 for x in pi))
                block_local_index = (i, *pi)
                old_b2b_g2l.append(block_local_index)
                old_b2is.append(items_local_index)
        old_is2b = {x: i for i, x in enumerate(old_b2is)}
        # old_b2b_l2g = {x: i for i, x in enumerate(old_b2b_g2l)}
        # New maps
        new_b2is, new_is2b = [], {}  # Items indices to block
        new_b2b_g2l, new_b2b_l2g = [], {}  # Block global to local index
        slice_lens = {len(grid_values[x][0]) for x in slice_list_rows}
        if len(slice_lens) != 1:
            raise ValueError(f'Length of slice rows should be equal: {slice_lens}')
        slice_len = list(slice_lens)[0]
        product_lens = [len(grid_values[x][0]) for x in product_list_rows[::-1]]
        slice_row_is = [tuple(i for _ in slice_list_rows) for i in range(slice_len)]
        product_rows_is = list(product(*[range(x - 1) for x in product_lens]))
        for i, si in enumerate(slice_row_is):
            for pi in product_rows_is:
                items_local_index = (si, pi, tuple(x + 1 for x in pi))
                block_local_index = (i, *pi)
                new_b2b_g2l.append(block_local_index)
                new_b2is.append(items_local_index)
        new_is2b = {x: i for i, x in enumerate(new_b2is)}
        # new_b2b_l2g = {x: i for i, x in enumerate(new_b2b_g2l)}
        # New to old maps
        new2old_b2b = []
        for new_is in new_is2b:
            sis, pi0s, pi1s = new_is  # slice, product first and last indices
            old_sis = []  # old slice indices
            for j, si in enumerate(sis):
                n2o = grid_maps[slice_list_rows[j]][-2]
                old_si = n2o[si]
                old_sis.append(old_si)
            old_sis = tuple(old_sis)
            pis = [(x, y) for x, y in zip(pi0s, pi1s)]
            old_pis = []
            for j, pi in enumerate(pis):
                row_j = product_list_rows[::-1][j]
                n2o = grid_maps[row_j][-2]
                i0, i1 = pi[0], pi[1]
                old_pi = (n2o[i0], n2o[i1])
                while old_pi[0] == old_pi[1]:
                    i0 -= 1
                    old_pi = (n2o[i0], old_pi[1])
                old_pis.append(old_pi)
            old_pi0s = tuple(x[0] for x in old_pis)
            old_pi1s = tuple(x[1] for x in old_pis)
            old_is = (old_sis, old_pi0s, old_pi1s)
            old_block = old_is2b[old_is]
            new2old_b2b.append(old_block)
        # Values
        # Coordinates
        slice_cs = [[grid_values[x][0][i] for x in slice_list_rows]
                    for i in range(slice_len)]
        product_cs = [grid_values[x][0] for x in product_list_rows]
        grid_cs = product_cs + [slice_cs]
        # Mesh sizes
        slice_ms = [[grid_values[x][1][i] for x in slice_list_rows]
                    for i in range(slice_len)]
        product_ms = [grid_values[x][1] for x in product_list_rows]
        grid_ms = product_ms + [slice_ms]
        # Structures
        slice_ss = [[grid_values[x][2][i] for x in slice_list_rows]
                    for i in range(slice_len)]
        product_ss = [grid_values[x][2] for x in product_list_rows]
        grid_ss = product_ss + [slice_ss]
    elif len(product_list_rows) != 0 and len(slice_list_rows) == 0:
        # Old maps
        old_b2is, old_is2b = [], {}  # Items indices to block
        old_b2b_g2l, old_b2b_l2g = [], {}  # Block global to local index
        product_lens = [len(new_grid[x][1:]) for x in product_list_rows[::-1]]
        product_rows_is = list(product(*[range(x - 1) for x in product_lens]))
        for pi in product_rows_is:
            items_local_index = (pi, tuple(x + 1 for x in pi))
            block_local_index = pi
            old_b2b_g2l.append(block_local_index)
            old_b2is.append(items_local_index)
        old_is2b = {x: i for i, x in enumerate(old_b2is)}
        # old_b2b_l2g = {x: i for i, x in enumerate(old_b2b_g2l)}
        # New maps
        new_b2is, new_is2b = [], {}  # Items indices to block
        new_b2b_g2l, new_b2b_l2g = [], {}  # Block global to local index
        product_lens = [len(grid_values[x][0]) for x in product_list_rows[::-1]]
        product_rows_is = list(product(*[range(x - 1) for x in product_lens]))
        for pi in product_rows_is:
            items_local_index = (pi, tuple(x + 1 for x in pi))
            block_local_index = pi
            new_b2b_g2l.append(block_local_index)
            new_b2is.append(items_local_index)
        new_is2b = {x: i for i, x in enumerate(new_b2is)}
        # new_b2b_l2g = {x: i for i, x in enumerate(new_b2b_g2l)}
        # New to old maps
        new2old_b2b = []
        for new_is in new_is2b:
            pi0s, pi1s = new_is  # slice, product first and last indices
            pis = [(x, y) for x, y in zip(pi0s, pi1s)]
            old_pis = []
            for j, pi in enumerate(pis):
                row_j = product_list_rows[::-1][j]
                n2o = grid_maps[row_j][-2]
                i0, i1 = pi[0], pi[1]
                old_pi = (n2o[i0], n2o[i1])
                while old_pi[0] == old_pi[1]:
                    i0 -= 1
                    old_pi = (n2o[i0], old_pi[1])
                old_pis.append(old_pi)
            old_pi0s = tuple(x[0] for x in old_pis)
            old_pi1s = tuple(x[1] for x in old_pis)
            old_is = (old_pi0s, old_pi1s)
            old_block = old_is2b[old_is]
            new2old_b2b.append(old_block)
        # Values
        grid_cs = [grid_values[x][0] for x in product_list_rows]  # Coordinates
        grid_ms = [grid_values[x][1] for x in product_list_rows]  # Mesh sizes
        grid_ss = [grid_values[x][2] for x in product_list_rows]  # Structures
    elif len(product_list_rows) == 0 and len(slice_list_rows) != 0:
        # Old maps
        old_b2is, old_is2b = [], {}  # Items indices to block
        old_b2b_g2l, old_b2b_l2g = [], {}  # Block global to local index
        slice_lens = {len(new_grid[x][1:]) for x in slice_list_rows}
        if len(slice_lens) != 1:
            raise ValueError(f'Length of slice rows should be equal: {slice_lens}')
        slice_len = list(slice_lens)[0]
        slice_row_is = [tuple(i for _ in slice_list_rows) for i in range(slice_len)]
        for i, si in enumerate(slice_row_is):
            items_local_index = si
            block_local_index = i
            old_b2b_g2l.append(block_local_index)
            old_b2is.append(items_local_index)
        old_is2b = {x: i for i, x in enumerate(old_b2is)}
        # old_b2b_l2g = {x: i for i, x in enumerate(old_b2b_g2l)}
        # New maps
        new_b2is, new_is2b = [], {}  # Items indices to block
        new_b2b_g2l, new_b2b_l2g = [], {}  # Block global to local index
        slice_lens = {len(grid_values[x][0]) for x in slice_list_rows}
        if len(slice_lens) != 1:
            raise ValueError(f'Length of slice rows should be equal: {slice_lens}')
        slice_len = list(slice_lens)[0]
        slice_row_is = [tuple(i for _ in slice_list_rows) for i in range(slice_len)]
        for i, si in enumerate(slice_row_is):
            items_local_index = si
            block_local_index = i
            new_b2b_g2l.append(block_local_index)
            new_b2is.append(items_local_index)
        new_is2b = {x: i for i, x in enumerate(new_b2is)}
        # new_b2b_l2g = {x: i for i, x in enumerate(new_b2b_g2l)}
        # New to old maps
        new2old_b2b = []
        for new_is in new_is2b:
            sis, pi0s, pi1s = new_is  # slice, product first and last indices
            old_sis = []  # old slice indices
            for j, si in enumerate(sis):
                n2o = grid_maps[slice_list_rows[j]][-2]
                old_si = n2o[si]
                old_sis.append(old_si)
            old_sis = tuple(old_sis)
            old_is = (old_sis)
            old_block = old_is2b[old_is]
            new2old_b2b.append(old_block)
        # Values
        # Coordinates
        grid_cs = [[grid_values[x][0][i] for x in slice_list_rows]
                   for i in range(slice_len)]
        # Mesh sizes
        grid_ms = [[grid_values[x][1][i] for x in slice_list_rows]
                   for i in range(slice_len)]
        # Structures
        grid_ss = [[grid_values[x][2][i] for x in slice_list_rows]
                   for i in range(slice_len)]
    else:
        raise ValueError(f'No list rows in the grid! {new_grid}')
    # Return
    grid_values = [grid_cs, grid_ms, grid_ss]
    # TODO Remove unnecessary maps?
    grid_maps = [old_b2is, old_b2b_g2l,  # Old
                 new_b2is, new_b2b_g2l,  # New
                 new2old_b2b]  # New to old
    return new_grid, grid_values, grid_maps


def parse_layers2grid(layers, sep_i=';', sep_si=':'):
    """Parse layers

    0. From list of rows (2D ragged array 6xNI), where
        NI - number of items/blocks by each direction (type item excluded!).
        First item of Z/NZ rows implicitly set to 0
        [
            [0  1  2  3] X
            [4  5  6]    Y
            [7  8]       NX
            [9]          NY
            [10 11]      Z
            [12 13]      NZ
        ] layers

    1. Corrected layers

    2. To layers block map (4D ragged array 4x2xNJxNI), where
        NJ - number of items/blocks by Z/NZ respectively,
        NI - number of items/blocks by X/Y/NX/NY respectively
    [
        [
            [
                [ 0  1  2  3] Z0
                [ 4  5  6  7] Z1
                 X0 X1 X2 X3
            ] Z
            [
                [ 8  9 10 11] NZ0
                [12 13 14 15] NZ1
                 X0 X1 X2 X3
            ] NZ
        ] X
        [
            [
                [16 17 18] Z0
                [19 20 21] Z1
                 Y0 Y1 Y2
            ] Z
            [
                [22 23 24] NZ0
                [25 26 27] NZ1
                 Y0 Y1 Y2
            ] NZ
        ] Y
        [
            [
                [ 28  29] Z0
                [ 30  31] Z1
                 NX0 NX1
            ] Z
            [
                [ 32  33] NZ0
                [ 34  35] NZ1
                 NX0 NX1
            ] - NZ
        ] NX
        [
            [
                [ 36] Z0
                [ 37] Z1
                 NY0
            ] Z
            [
                [ 38] NZ0
                [ 39] NZ1
                 NY0
            ] NZ
        ] NY
    ] - layers block map

    To grid (3D array, 3xNI), NI - number of items by X/Y/Z respectively
    [
        NX + X                    - X, where NX is negated and reversed
        NY + Y                    - Y, where NY is negated and reversed
        NZ + [0] + Z              - Z, where NZ is negated and reversed
    ] - grid

    To block map of the grid (3D array, NZN+ZN x NYN+YN-1 x NXN+XN-1)
    [
        [
            [  0    1    2  3  4] NY0/Y0
            [  5    6    7  8  9] Y1
            [ 10   11   12 13 14] Y2
             NX1 NX0/X0 X1 X2 X3
        ] NZ1
        [
            [ 15   16   17 18 19] NY0/Y0
            [ 20   21   22 23 24] Y1
            [ 25   26   27 28 29] Y2
             NX1 NX0/X0 X1 X2 X3
        ] NZ0
        [
            [ 30   31   32 33 34] NY0/Y0
            [ 35   36   37 38 39] Y1
            [ 40   41   42 43 44] Y2
             NX1 NX0/X0 X1 X2 X3
        ] Z0
        [
            [ 45   46   47 48 49] NY0/Y0
            [ 50   51   52 53 54] Y1
            [ 55   56   57 58 59] Y2
             NX1 NX0/X0 X1 X2 X3
        ] Z1
    ] grid block map

    Global indexes of layers block map at grid block map
    [
        [
            [ 35 12/25/34/39 13 14 15] NY0/Y0
            [ -       26      -  -  -] Y1
            [ -       27      -  -  -] Y2
             NX1    NX0/X0   X1 X2 X3
        ] NZ1
        [
            [ 33  8/22/32/38  9 10 11] NY0/Y0
            [ -       23      -  -  -] Y1
            [ -       24      -  -  -] Y2
             NX1    NX0/X0   X1 X2 X3
        ] NZ0
        [
            [ 29  0/16/28/36  1  2  3] NY0/Y0
            [ -       17      -  -  -] Y1
            [ -       18      -  -  -] Y2
             NX1    NX0/X0   X1 X2 X3
        ] Z0
        [
            [31   4/19/30/37  5  6  7] NY0/Y0
            [ -       20      -  -  -] Y1
            [ -       21      -  -  -] Y2
             NX1    NX0/X0   X1 X2 X3
        ] Z1
    ] block map of the grid

    Args:
        layers (list of list): list of rows
        sep_i (str): items separator
        sep_si (str): sub-items separator

    Returns:
        tuple: new_layers, values, maps
    """
    new_layers, values, maps = [], [], []
    # Correct
    corrected_layers, corrected_maps = correct_layers(layers)
    new_layers.append(corrected_layers)
    maps.extend(corrected_maps)
    # Parse
    parsed_layers, parsed_values, parsed_maps = parse_layers(corrected_layers)
    new_layers.append(parsed_layers)
    values.extend(parsed_values)
    maps.extend(parsed_maps)
    parsed_layers_cs = [x[0] for x in parsed_values]
    parsed_mesh_sizes = [x[1] for x in parsed_values]
    parsed_structures = [x[2] for x in parsed_values]
    # Grid
    # Layers coordinates
    c_xs = parsed_layers_cs[0]
    c_ys = parsed_layers_cs[1]
    c_zs = parsed_layers_cs[4]
    c_nxs = [-x for x in parsed_layers_cs[2][::-1]]  # reverse and negate
    c_nys = [-x for x in parsed_layers_cs[3][::-1]]  # reverse and negate
    c_nzs = [-x for x in parsed_layers_cs[5][::-1]]  # reverse and negate
    # Layers mesh sizes
    m_xs = parsed_mesh_sizes[0]
    m_ys = parsed_mesh_sizes[1]
    m_zs = parsed_mesh_sizes[4]
    m_nxs = parsed_mesh_sizes[2][::-1]  # reverse
    m_nys = parsed_mesh_sizes[3][::-1]  # reverse
    m_nzs = parsed_mesh_sizes[5][::-1]  # reverse
    # Layers structures
    s_xs = parsed_structures[0]
    s_ys = parsed_structures[1]
    s_zs = parsed_structures[4]
    s_nxs = [None] + parsed_structures[2][::-1]  # reverse and move right
    s_nys = [None] + parsed_structures[3][::-1]  # reverse and move right
    s_nzs = [None] + parsed_structures[5][::-1]  # reverse and move right
    # Grid coordinates
    c_xs_g = c_nxs + c_xs  # NX + X
    c_ys_g = c_nys + c_ys  # NY + Y
    c_zs_g = c_nzs + [0] + c_zs  # NZ + 0 + Z
    # Grid mesh sizes
    m_xs_g = m_nxs + m_xs  # NX + X
    m_ys_g = m_nys + m_ys  # NY + Y
    last_m_nz = m_nzs[-1] if len(m_nzs) > 0 else None
    first_m_z = m_zs[-1] if len(m_zs) > 0 else None
    if last_m_nz is not None and first_m_z is not None:
        m_z0_g = 0.5 * (last_m_nz + first_m_z)
    elif last_m_nz is not None:
        m_z0_g = last_m_nz
    elif first_m_z is not None:
        m_z0_g = first_m_z
    else:
        m_z0_g = None
    m_zs_g = m_nzs + [m_z0_g] + m_zs  # NZ + 0 +  Z
    # Grid structures TODO inverse bug with curves
    s_nxs = [x if x is None or len(x) == 1 or x[1] != 0 else [x[0], x[1], 1 / x[2]]
             for x in s_nxs]
    s_nys = [x if x is None or len(x) == 1 or x[1] != 0 else [x[0], x[1], 1 / x[2]]
             for x in s_nys]
    s_xs_g = s_nxs[:-1] + s_xs  # NX + X
    s_ys_g = s_nys[:-1] + s_ys  # NY + Y
    last_s_nz = s_nzs[-1] if len(s_nzs) > 0 else None
    first_s_z = s_zs[-1] if len(s_zs) > 0 else None
    if last_s_nz is not None and first_s_z is not None:
        s_z0_g = first_s_z  # Get from first of Z
    elif last_s_nz is not None:
        s_z0_g = last_s_nz
    elif first_s_z is not None:
        s_z0_g = first_s_z
    else:
        s_z0_g = None
    s_zs_g = s_nzs[:-1] + [s_z0_g] + s_zs  # NZ + 0 +  Z
    # Points
    p_xs_g = [sep_i.join([
        str(c) if c is not None else '',
        str(m) if m is not None else '',
        sep_si.join(str(x) for x in s) if s is not None else ''])
        for c, m, s in zip(c_xs_g, m_xs_g, s_xs_g)]
    p_ys_g = [sep_i.join([
        str(c) if c is not None else '',
        str(m) if m is not None else '',
        sep_si.join(str(x) for x in s) if s is not None else ''])
        for c, m, s in zip(c_ys_g, m_ys_g, s_ys_g)]
    p_zs_g = [sep_i.join([
        str(c) if c is not None else '',
        str(m) if m is not None else '',
        sep_si.join(str(x) for x in s) if s is not None else ''])
        for c, m, s in zip(c_zs_g, m_zs_g, s_zs_g)]
    grid = [p_xs_g, p_ys_g, p_zs_g]
    new_layers.append(grid)
    # Map grid block to layers block
    nbx, nby, nbz = [len(x) - 1 for x in grid]  # number of blocks
    nx, ny, nnx, nny, nz, nnz = [len(x) for x in parsed_layers_cs]  # lengths of layers
    gcx, gcy, gcz = nnx - 1, nny - 1, nnz  # grid center block index
    glis = product(*(range(nbz), range(nby), range(nbx)))  # grid local indices
    g2l_b2b_l2l, g2l_b2b_g2g = {}, []  # local to local, global to global
    for ggi, gli in enumerate(glis):  # global, local grid index
        gzi, gyi, gxi = gli  # grid z, y, x local indices
        g2l_b2b_l2l[gli] = []
        g2l_b2b_g2g.append([])
        if gxi >= gcx and gyi == gcy:  # X layer
            lxi = gxi - gcx  # Layer X local item index
            if gzi >= gcz:  # Z layer
                lzi = gzi - gcz  # Layer Z local item index
                lli = (0, 0, lzi, lxi)  # Layer local index
                lgi = nx * lzi + lxi  # Layer global index
            else:  # NZ layer
                lzi = gcz - gzi - 1  # Layer NZ local item index
                lli = (0, 1, lzi, lxi)  # Layer local index
                lgi = nx * (nz + lzi) + lxi  # Layer global index
            g2l_b2b_l2l[gli].append(lli)
            g2l_b2b_g2g[ggi].append(lgi)
        if gyi >= gcy and gxi == gcx:  # Y layer
            lyi = gyi - gcy  # Layer Y local item index
            if gzi >= gcz:  # Z layer
                lzi = gzi - gcz  # Layer Z local item index
                lli = (1, 0, lzi, lyi)  # Layer local index
                lgi = nx * (nz + nnz) + ny * lzi + lyi  # Layer global index
            else:  # NZ layer
                lzi = gcz - gzi - 1  # Layer NZ local item index
                lli = (1, 1, lzi, lyi)  # Layer local index
                lgi = nx * (nz + nnz) + ny * (nz + lzi) + lyi
            g2l_b2b_l2l[gli].append(lli)
            g2l_b2b_g2g[ggi].append(lgi)
        if gxi <= gcx and gyi == gcy:  # NX layer
            lnxi = gcx - gxi  # Layer NX local item index
            if gzi >= gcz:  # Z layer
                lzi = gzi - gcz  # Layer Z local item index
                lli = (2, 0, lzi, lnxi)  # Layer local index
                lgi = (nx + ny) * (nz + nnz) + nnx * lzi + lnxi
            else:  # NZ layer
                lzi = gcz - gzi - 1  # Layer NZ local item index
                lli = (2, 1, lzi, lnxi)  # Layer local index
                lgi = (nx + ny) * (nz + nnz) + nnx * (nz + lzi) + lnxi
            g2l_b2b_l2l[gli].append(lli)
            g2l_b2b_g2g[ggi].append(lgi)
        if gyi <= gcy and gxi == gcx:  # NY layer
            lnyi = gcy - gyi  # Layer NY local item index
            if gzi >= gcz:  # Z
                lzi = gzi - gcz  # Layer Z local item index
                lli = (3, 0, lzi, lnyi)  # Layer local index
                lgi = (nx + ny + nnx) * (nz + nnz) + nny * lzi + lnyi
            else:  # NZ
                lzi = gcz - gzi - 1  # Layer NZ local item index
                lli = (3, 1, lzi, lnyi)  # Layer local index
                lgi = (nx + ny + nnx) * (nz + nnz) + nny * (nz + lzi) + lnyi
            g2l_b2b_l2l[gli].append(lli)
            g2l_b2b_g2g[ggi].append(lgi)
        if len(g2l_b2b_l2l[gli]) == 0:
            g2l_b2b_l2l[gli] = None
        if len(g2l_b2b_g2g[ggi]) == 0:
            g2l_b2b_g2g[ggi] = None
    maps.append(g2l_b2b_l2l)
    maps.append(g2l_b2b_g2g)
    # Combined maps
    # Corrected -> Original
    c_n2o_l2l_l2l, c_n2o_l2l_g2g = maps[0], maps[1]
    c_n2o_b2b_l2l, c_n2o_b2b_g2g = maps[2], maps[3]
    # Parsed -> Corrected
    p_n2o_l2l_l2l, p_n2o_l2l_g2g = maps[4], maps[5]
    p_n2o_b2b_l2l, p_n2o_b2b_g2g = maps[6], maps[7]
    # Parsed -> Corrected -> Original
    n2o_l2l_l2l = {k: c_n2o_l2l_l2l[v] for k, v in p_n2o_l2l_l2l.items()}
    n2o_l2l_g2g = [c_n2o_l2l_g2g[x] for x in p_n2o_l2l_g2g]
    n2o_b2b_l2l = {k: c_n2o_b2b_l2l[v] for k, v in p_n2o_b2b_l2l.items()}
    n2o_b2b_g2g = [c_n2o_b2b_g2g[x] for x in p_n2o_b2b_g2g]
    maps.append(n2o_l2l_l2l)
    maps.append(n2o_l2l_g2g)
    maps.append(n2o_b2b_l2l)
    maps.append(n2o_b2b_g2g)
    # Grid -> Parsed -> Corrected -> Original
    g2o_b2b_l2l = {k: [n2o_b2b_l2l[x] for x in v] if v is not None else None
                   for k, v in g2l_b2b_l2l.items()}  # Center block from X layer
    g2o_b2b_g2g = [[n2o_b2b_g2g[y] for y in x] if x is not None else None
                   for x in g2l_b2b_g2g]  # Center block from X layer
    maps.append(g2o_b2b_l2l)
    maps.append(g2o_b2b_g2g)
    return new_layers, values, maps


def parse_halflayers2grid(layers, sep_i=';', sep_si=':'):
    """Parse layers

    0. From list of rows (2D ragged array 6xNI), where
        NI - number of items/blocks by each direction (type item excluded!).
        First item of Z/NZ rows implicitly set to 0
        [
            [0  1  2  3] X
            [4  5  6]    Y
            [7  8]       NX
            [9]          NY
            [10 11]      Z
            [12 13]      NZ
        ] layers

    1. Corrected layers

    2. To layers block map (4D ragged array 4x2xNJxNI), where
        NJ - number of items/blocks by Z/NZ respectively,
        NI - number of items/blocks by X/Y/NX/NY respectively
    [
        [
            [
                [ 0  1  2  3] Z0
                [ 4  5  6  7] Z1
                 X0 X1 X2 X3
            ] Z
            [
                [ 8  9 10 11] NZ0
                [12 13 14 15] NZ1
                 X0 X1 X2 X3
            ] NZ
        ] X
        [
            [
                [16 17 18] Z0
                [19 20 21] Z1
                 Y0 Y1 Y2
            ] Z
            [
                [22 23 24] NZ0
                [25 26 27] NZ1
                 Y0 Y1 Y2
            ] NZ
        ] Y
        [
            [
                [ 28  29] Z0
                [ 30  31] Z1
                 NX0 NX1
            ] Z
            [
                [ 32  33] NZ0
                [ 34  35] NZ1
                 NX0 NX1
            ] - NZ
        ] NX
        [
            [
                [ 36] Z0
                [ 37] Z1
                 NY0
            ] Z
            [
                [ 38] NZ0
                [ 39] NZ1
                 NY0
            ] NZ
        ] NY
    ] - layers block map

    To grid (3D array, 3xNI), NI - number of items by X/Y/Z respectively
    [
        NX + X                    - X, where NX is negated and reversed
        NY + Y                    - Y, where NY is negated and reversed
        NZ + [0] + Z              - Z, where NZ is negated and reversed
    ] - grid

    To block map of the grid (3D array, NZN+ZN x NYN+YN-1 x NXN+XN-1)
    [
        [
            [  0    1    2  3  4] NY0/Y0
            [  5    6    7  8  9] Y1
            [ 10   11   12 13 14] Y2
             NX1 NX0/X0 X1 X2 X3
        ] NZ1
        [
            [ 15   16   17 18 19] NY0/Y0
            [ 20   21   22 23 24] Y1
            [ 25   26   27 28 29] Y2
             NX1 NX0/X0 X1 X2 X3
        ] NZ0
        [
            [ 30   31   32 33 34] NY0/Y0
            [ 35   36   37 38 39] Y1
            [ 40   41   42 43 44] Y2
             NX1 NX0/X0 X1 X2 X3
        ] Z0
        [
            [ 45   46   47 48 49] NY0/Y0
            [ 50   51   52 53 54] Y1
            [ 55   56   57 58 59] Y2
             NX1 NX0/X0 X1 X2 X3
        ] Z1
    ] grid block map

    Global indexes of layers block map at grid block map
    [
        [
            [ 35 12/25/34/39 13 14 15] NY0/Y0
            [ -       26      -  -  -] Y1
            [ -       27      -  -  -] Y2
             NX1    NX0/X0   X1 X2 X3
        ] NZ1
        [
            [ 33  8/22/32/38  9 10 11] NY0/Y0
            [ -       23      -  -  -] Y1
            [ -       24      -  -  -] Y2
             NX1    NX0/X0   X1 X2 X3
        ] NZ0
        [
            [ 29  0/16/28/36  1  2  3] NY0/Y0
            [ -       17      -  -  -] Y1
            [ -       18      -  -  -] Y2
             NX1    NX0/X0   X1 X2 X3
        ] Z0
        [
            [31   4/19/30/37  5  6  7] NY0/Y0
            [ -       20      -  -  -] Y1
            [ -       21      -  -  -] Y2
             NX1    NX0/X0   X1 X2 X3
        ] Z1
    ] block map of the grid

    Args:
        layers (list of list): list of rows
        sep_i (str): items separator
        sep_si (str): sub-items separator

    Returns:
        tuple: new_layers, values, maps
    """
    new_layers, values, maps = [], [], []
    # Correct
    corrected_layers, corrected_maps = correct_layers(layers)
    new_layers.append(corrected_layers)
    maps.extend(corrected_maps)
    # Parse
    parsed_layers, parsed_values, parsed_maps = parse_layers(corrected_layers)
    new_layers.append(parsed_layers)
    values.extend(parsed_values)
    maps.extend(parsed_maps)
    parsed_layers_cs = [x[0] for x in parsed_values]
    parsed_mesh_sizes = [x[1] for x in parsed_values]
    parsed_structures = [x[2] for x in parsed_values]
    # Grid
    # Layers coordinates
    c_xs = parsed_layers_cs[0]
    c_ys = parsed_layers_cs[1]
    c_zs = parsed_layers_cs[4]
    c_nxs = [-x for x in parsed_layers_cs[2][::-1]]  # reverse and negate
    c_nys = [-x for x in parsed_layers_cs[3][::-1]]  # reverse and negate
    c_nzs = [-x for x in parsed_layers_cs[5][::-1]]  # reverse and negate
    # Layers mesh sizes
    m_xs = parsed_mesh_sizes[0]
    m_ys = parsed_mesh_sizes[1]
    m_zs = parsed_mesh_sizes[4]
    m_nxs = parsed_mesh_sizes[2][::-1]  # reverse
    m_nys = parsed_mesh_sizes[3][::-1]  # reverse
    m_nzs = parsed_mesh_sizes[5][::-1]  # reverse
    # Layers structures
    s_xs = parsed_structures[0]
    s_ys = parsed_structures[1]
    s_zs = parsed_structures[4]
    s_nxs = [None] + parsed_structures[2][::-1]  # reverse and move right
    s_nys = [None] + parsed_structures[3][::-1]  # reverse and move right
    s_nzs = [None] + parsed_structures[5][::-1]  # reverse and move right
    # Half Layer Correction
    s_xs = [[2*y if i == 0 and j == 0 else y for j, y in enumerate(x)] for i, x in enumerate(s_xs)]
    # Grid coordinates
    c_xs_g = c_nxs + c_xs  # NX + X
    c_ys_g = c_nys + c_ys  # NY + Y
    c_zs_g = c_nzs + [0] + c_zs  # NZ + 0 + Z
    # Grid mesh sizes
    m_xs_g = m_nxs + m_xs  # NX + X
    m_ys_g = m_nys + m_ys  # NY + Y
    last_m_nz = m_nzs[-1] if len(m_nzs) > 0 else None
    first_m_z = m_zs[-1] if len(m_zs) > 0 else None
    if last_m_nz is not None and first_m_z is not None:
        m_z0_g = 0.5 * (last_m_nz + first_m_z)
    elif last_m_nz is not None:
        m_z0_g = last_m_nz
    elif first_m_z is not None:
        m_z0_g = first_m_z
    else:
        m_z0_g = None
    m_zs_g = m_nzs + [m_z0_g] + m_zs  # NZ + 0 +  Z
    # Grid structures TODO inverse bug with curves
    s_nxs = [x if x is None or len(x) == 1 or x[1] != 0 else [x[0], x[1], 1 / x[2]]
             for x in s_nxs]
    s_nys = [x if x is None or len(x) == 1 or x[1] != 0 else [x[0], x[1], 1 / x[2]]
             for x in s_nys]
    s_xs_g = s_nxs[:-1] + s_xs  # NX + X
    s_ys_g = s_nys[:-1] + s_ys  # NY + Y
    last_s_nz = s_nzs[-1] if len(s_nzs) > 0 else None
    first_s_z = s_zs[-1] if len(s_zs) > 0 else None
    if last_s_nz is not None and first_s_z is not None:
        s_z0_g = first_s_z  # Get from first of Z
    elif last_s_nz is not None:
        s_z0_g = last_s_nz
    elif first_s_z is not None:
        s_z0_g = first_s_z
    else:
        s_z0_g = None
    s_zs_g = s_nzs[:-1] + [s_z0_g] + s_zs  # NZ + 0 +  Z
    # Points
    p_xs_g = [sep_i.join([
        str(c) if c is not None else '',
        str(m) if m is not None else '',
        sep_si.join(str(x) for x in s) if s is not None else ''])
        for c, m, s in zip(c_xs_g, m_xs_g, s_xs_g)]
    p_ys_g = [sep_i.join([
        str(c) if c is not None else '',
        str(m) if m is not None else '',
        sep_si.join(str(x) for x in s) if s is not None else ''])
        for c, m, s in zip(c_ys_g, m_ys_g, s_ys_g)]
    p_zs_g = [sep_i.join([
        str(c) if c is not None else '',
        str(m) if m is not None else '',
        sep_si.join(str(x) for x in s) if s is not None else ''])
        for c, m, s in zip(c_zs_g, m_zs_g, s_zs_g)]
    grid = [p_xs_g, p_ys_g, p_zs_g]
    new_layers.append(grid)
    # Map grid block to layers block
    nbx, nby, nbz = [len(x) - 1 for x in grid]  # number of blocks
    nx, ny, nnx, nny, nz, nnz = [len(x) for x in parsed_layers_cs]  # lengths of layers
    gcx, gcy, gcz = nnx - 1, nny - 1, nnz  # grid center block index
    glis = product(*(range(nbz), range(nby), range(nbx)))  # grid local indices
    g2l_b2b_l2l, g2l_b2b_g2g = {}, []  # local to local, global to global
    for ggi, gli in enumerate(glis):  # global, local grid index
        gzi, gyi, gxi = gli  # grid z, y, x local indices
        g2l_b2b_l2l[gli] = []
        g2l_b2b_g2g.append([])
        if gxi >= gcx and gyi == gcy:  # X layer
            lxi = gxi - gcx  # Layer X local item index
            if gzi >= gcz:  # Z layer
                lzi = gzi - gcz  # Layer Z local item index
                lli = (0, 0, lzi, lxi)  # Layer local index
                lgi = nx * lzi + lxi  # Layer global index
            else:  # NZ layer
                lzi = gcz - gzi - 1  # Layer NZ local item index
                lli = (0, 1, lzi, lxi)  # Layer local index
                lgi = nx * (nz + lzi) + lxi  # Layer global index
            g2l_b2b_l2l[gli].append(lli)
            g2l_b2b_g2g[ggi].append(lgi)
        if gyi >= gcy and gxi == gcx:  # Y layer
            lyi = gyi - gcy  # Layer Y local item index
            if gzi >= gcz:  # Z layer
                lzi = gzi - gcz  # Layer Z local item index
                lli = (1, 0, lzi, lyi)  # Layer local index
                lgi = nx * (nz + nnz) + ny * lzi + lyi  # Layer global index
            else:  # NZ layer
                lzi = gcz - gzi - 1  # Layer NZ local item index
                lli = (1, 1, lzi, lyi)  # Layer local index
                lgi = nx * (nz + nnz) + ny * (nz + lzi) + lyi
            g2l_b2b_l2l[gli].append(lli)
            g2l_b2b_g2g[ggi].append(lgi)
        if gxi <= gcx and gyi == gcy:  # NX layer
            lnxi = gcx - gxi  # Layer NX local item index
            if gzi >= gcz:  # Z layer
                lzi = gzi - gcz  # Layer Z local item index
                lli = (2, 0, lzi, lnxi)  # Layer local index
                lgi = (nx + ny) * (nz + nnz) + nnx * lzi + lnxi
            else:  # NZ layer
                lzi = gcz - gzi - 1  # Layer NZ local item index
                lli = (2, 1, lzi, lnxi)  # Layer local index
                lgi = (nx + ny) * (nz + nnz) + nnx * (nz + lzi) + lnxi
            g2l_b2b_l2l[gli].append(lli)
            g2l_b2b_g2g[ggi].append(lgi)
        if gyi <= gcy and gxi == gcx:  # NY layer
            lnyi = gcy - gyi  # Layer NY local item index
            if gzi >= gcz:  # Z
                lzi = gzi - gcz  # Layer Z local item index
                lli = (3, 0, lzi, lnyi)  # Layer local index
                lgi = (nx + ny + nnx) * (nz + nnz) + nny * lzi + lnyi
            else:  # NZ
                lzi = gcz - gzi - 1  # Layer NZ local item index
                lli = (3, 1, lzi, lnyi)  # Layer local index
                lgi = (nx + ny + nnx) * (nz + nnz) + nny * (nz + lzi) + lnyi
            g2l_b2b_l2l[gli].append(lli)
            g2l_b2b_g2g[ggi].append(lgi)
        if len(g2l_b2b_l2l[gli]) == 0:
            g2l_b2b_l2l[gli] = None
        if len(g2l_b2b_g2g[ggi]) == 0:
            g2l_b2b_g2g[ggi] = None
    maps.append(g2l_b2b_l2l)
    maps.append(g2l_b2b_g2g)
    # Combined maps
    # Corrected -> Original
    c_n2o_l2l_l2l, c_n2o_l2l_g2g = maps[0], maps[1]
    c_n2o_b2b_l2l, c_n2o_b2b_g2g = maps[2], maps[3]
    # Parsed -> Corrected
    p_n2o_l2l_l2l, p_n2o_l2l_g2g = maps[4], maps[5]
    p_n2o_b2b_l2l, p_n2o_b2b_g2g = maps[6], maps[7]
    # Parsed -> Corrected -> Original
    n2o_l2l_l2l = {k: c_n2o_l2l_l2l[v] for k, v in p_n2o_l2l_l2l.items()}
    n2o_l2l_g2g = [c_n2o_l2l_g2g[x] for x in p_n2o_l2l_g2g]
    n2o_b2b_l2l = {k: c_n2o_b2b_l2l[v] for k, v in p_n2o_b2b_l2l.items()}
    n2o_b2b_g2g = [c_n2o_b2b_g2g[x] for x in p_n2o_b2b_g2g]
    maps.append(n2o_l2l_l2l)
    maps.append(n2o_l2l_g2g)
    maps.append(n2o_b2b_l2l)
    maps.append(n2o_b2b_g2g)
    # Grid -> Parsed -> Corrected -> Original
    g2o_b2b_l2l = {k: [n2o_b2b_l2l[x] for x in v] if v is not None else None
                   for k, v in g2l_b2b_l2l.items()}  # Center block from X layer
    g2o_b2b_g2g = [[n2o_b2b_g2g[y] for y in x] if x is not None else None
                   for x in g2l_b2b_g2g]  # Center block from X layer
    maps.append(g2o_b2b_l2l)
    maps.append(g2o_b2b_g2g)
    return new_layers, values, maps


def correct_layers(layers):
    """Correct layers

    [
        [0  1  2  3] X
        [4  5  6]    Y
        [7  8]       NX
        [9]          NY
        [10 11]      Z
        [12 13]      NZ
    ] layers
    with variants:
        1. X/Z (2xN)
            [
                [0  1  2  3] X
                [4  5]       Z
            ] layers
        2. X/Y/Z (3xN)
            [
                [0  1  2  3] X
                [4  5  6]    Y
                [7  8]       Z
            ] layers
        3. X/Y/Z/NZ (4xN)
            [
                [0  1  2  3] X
                [4  5  6]    Y
                [7  8]       Z
                [9 10]       NZ
            ] layers
        4. X/Y/NX/NY/Z (5xN)
            [
                [0  1  2  3] X
                [4  5  6]    Y
                [7  8]       NX
                [9]          NY
                [10 11]      Z
            ] layers
    Args:
        layers (list of list): layers

    Returns:

    """
    n2o_l2l_l2l, n2o_l2l_g2g = {}, []
    n2o_b2b_l2l, n2o_b2b_g2g = {}, []
    if len(layers) == 6:  # X, Y, NX, NY, Z, NZ
        # Layer to Layer
        new_layers = [x for x in layers]
        for ni, layer in enumerate(new_layers):
            for nj, item in enumerate(layer):
                oi, oj = ni, nj
                nl, ol = (ni, nj), (oi, oj)
                og = sum([len(x) for x in layers[:oi]]) + oj
                n2o_l2l_l2l[nl] = ol
                n2o_l2l_g2g.append(og)
        # Block to Block
        n_bgi = 0
        for i, layer_r in enumerate(new_layers[:4]):  # X/Y/NX/NY
            for j, layer_h in enumerate(new_layers[4:]):  # Z/NZ
                for zi, _ in enumerate(layer_h):  # For each Z/NZ
                    for ci, _ in enumerate(layer_r):  # For each X/Y/NX/NY
                        n_bli = (i, j, zi, ci)
                        o_bli = n_bli
                        o_bgi = n_bgi
                        n2o_b2b_l2l[n_bli] = o_bli
                        n2o_b2b_g2g.append(o_bgi)
                        n_bgi += 1
    elif len(layers) == 2:  # X -> X, Y, NX, NY; Z -> Z; NZ = []
        # Layer to Layer
        new_layers = [layers[0] for _ in range(4)] + [layers[1]] + [[]]
        for ni, layer in enumerate(new_layers):
            for nj, item in enumerate(layer):
                oi, oj = 0 if ni in [0, 1, 2, 3] else 1, nj
                nl, ol = (ni, nj), (oi, oj),
                og = sum([len(x) for x in layers[:oi]]) + oj
                n2o_l2l_l2l[nl] = ol
                n2o_l2l_g2g.append(og)
        # Block to Block
        nc = len(layers[0])
        for i, layer_r in enumerate(new_layers[:4]):  # X/Y/NX/NY
            for j, layer_h in enumerate(new_layers[4:]):  # Z/NZ
                for zi, _ in enumerate(layer_h):  # For each Z/NZ
                    for ci, _ in enumerate(layer_r):  # For each X/Y/NX/NY
                        n_bli, o_bli = (i, j, zi, ci), (zi, ci)
                        o_bgi = zi * nc + ci
                        n2o_b2b_l2l[n_bli] = o_bli
                        n2o_b2b_g2g.append(o_bgi)
    elif len(layers) == 3:  # X -> X, NX, Y -> Y, NY; Z -> Z; NZ = []
        # Layer to Layer
        new_layers = layers[:2] + layers[:2] + [layers[2]] + [[]]
        for ni, layer in enumerate(new_layers):
            for nj, item in enumerate(layer):
                if ni in [0, 2]:  # X
                    oi = 0
                elif ni in [1, 3]:  # Y
                    oi = 1
                else:  # Z
                    oi = 2
                oj = nj
                nl, ol = (ni, nj), (oi, oj),
                og = sum([len(x) for x in layers[:oi]]) + oj
                n2o_l2l_l2l[nl] = ol
                n2o_l2l_g2g.append(og)
        # Block to Block
        nx, ny, nz = len(layers[0]), len(layers[1]), len(layers[2])
        for i, layer_r in enumerate(new_layers[:4]):  # X/Y/NX/NY
            for j, layer_h in enumerate(new_layers[4:]):  # Z/NZ
                for zi, _ in enumerate(layer_h):  # For each Z/NZ
                    for ci, _ in enumerate(layer_r):  # For each X/Y/NX/NY
                        oi = 0 if i in [0, 2] else 1  # X, NX else Y, NY
                        n_bli, o_bli = (i, j, zi, ci), (oi, zi, ci)
                        if oi == 0:  # X, NX
                            o_bgi = zi * nx + ci
                        else:  # Y, NY
                            o_bgi = nx * nz + zi * ny + ci
                        n2o_b2b_l2l[n_bli] = o_bli
                        n2o_b2b_g2g.append(o_bgi)
    elif len(layers) == 5:  # X -> X, Y -> Y, NX -> NX, NY -> NY, Z -> Z; NZ = []
        # Layer to Layer
        new_layers = layers + [[]]
        for ni, layer in enumerate(new_layers):
            for nj, item in enumerate(layer):
                oi, oj = ni if ni in [0, 1, 2, 3, 4] else 4, nj
                nl, ol = (ni, nj), (oi, oj),
                og = sum([len(x) for x in layers[:oi]]) + oj
                n2o_l2l_l2l[nl] = ol
                n2o_l2l_g2g.append(og)
        # Block to Block
        nx, ny, nnx, nny, nz = [len(x) for x in layers]
        for i, layer_r in enumerate(new_layers[:4]):  # X/Y/NX/NY
            for j, layer_h in enumerate(new_layers[4:]):  # Z/NZ
                for zi, _ in enumerate(layer_h):  # For each Z/NZ
                    for ci, _ in enumerate(layer_r):  # For each X/Y/NX/NY
                        # oi = 0 if i in [0, 2] else 1  # X, NX else Y, NY
                        oi = i
                        n_bli, o_bli = (i, j, zi, ci), (oi, zi, ci)
                        if oi == 0:  # X, NX
                            o_bgi = zi * nx + ci
                        elif oi == 1:  # Y
                            o_bgi = nx * nz + ny * zi + ci
                        elif oi == 2:  # NX
                            o_bgi = (nx + ny) * nz + nnx * zi + ci
                        else:  # NY
                            o_bgi = (nx + ny + nnx) * nz + nny * zi + ci
                        n2o_b2b_l2l[n_bli] = o_bli
                        n2o_b2b_g2g.append(o_bgi)
    else:
        raise NotImplementedError(layers)
    # Return
    maps = [n2o_l2l_l2l, n2o_l2l_g2g, n2o_b2b_l2l, n2o_b2b_g2g]
    return new_layers, maps


def parse_layers(layers, sep_i=';', sep_si=':'):
    """Parse layers

    """
    n2o_l2l_l2l, n2o_l2l_g2g = {}, []
    n2o_b2b_l2l, n2o_b2b_g2g = {}, []
    parsed_rows, parsed_values, parsed_maps = [], [], []
    for layer in layers:
        r, vs, ms = parse_row(layer, sep_i, sep_si)
        parsed_rows.append(r)
        parsed_values.append(vs)
        parsed_maps.append(ms)  # o_b2is, o_is2b, n_b2is, n_is2b, n2o_i2i, n2o_b2b
    # Parsed maps
    new_layers = [x[0] for x in parsed_values]
    # Layer to Layer
    for ni, layer in enumerate(new_layers):  # new layer index, new layer
        n2o_i2i = parsed_maps[ni][4]  # new to old layer item index map
        for nj, item in enumerate(layer):  # new item index, new item of new layer
            oi, oj = ni, n2o_i2i[nj]  # old layer index, old item index
            nl, ol = (ni, nj), (oi, oj)  # new, old local index
            og = sum([len(x) for x in layers[:oi]]) + oj  # old global index
            n2o_l2l_l2l[nl] = ol
            n2o_l2l_g2g.append(og)
    # Block to Block
    n_bgi = 0
    nx, ny, nnx, nny, nz, nnz = [len(x) for x in layers]
    for i, layer_r in enumerate(new_layers[:4]):  # X/Y/NX/NY
        n2o_i2i_r = parsed_maps[i][4]  # new to old layer item index map
        for j, layer_h in enumerate(new_layers[4:]):  # Z/NZ
            n2o_i2i_h = parsed_maps[j + 4][4]  # new to old layer item index map
            for zi, _ in enumerate(layer_h):  # For each Z/NZ
                for ci, _ in enumerate(layer_r):  # For each X/Y/NX/NY
                    n_bli = (i, j, zi, ci)  # new local index
                    o_zi, o_ci = n2o_i2i_h[zi], n2o_i2i_r[ci]  # old z, c index
                    o_bli = (i, j, o_zi, o_ci)  # old local index
                    if i == 0:  # X
                        if j == 0:  # Z
                            o_bgi = nx * o_zi + o_ci
                        else:  # NZ (j == 1)
                            o_bgi = nx * nz + nx * o_zi + o_ci
                    elif i == 1:  # Y
                        if j == 0:  # Z
                            o_bgi = nx * (nz + nnz) + ny * o_zi + o_ci
                        else:  # NZ (j == 1)
                            o_bgi = nx * (nz + nnz) + ny * nz + ny * o_zi + o_ci
                    elif i == 2:  # NX
                        if j == 0:  # Z
                            o_bgi = (nx + ny) * (nz + nnz) + nnx * o_zi + o_ci
                        else:  # NZ (j == 1)
                            o_bgi = (nx + ny) * (nz + nnz) + nnx * nz + nnx * o_zi + o_ci
                    else:  # NY (i == 3)
                        if j == 0:  # Z
                            o_bgi = (nx + ny + nnx) * (nz + nnz) + nny * o_zi + o_ci
                        else:  # NZ (j == 1)
                            o_bgi = (nx + ny + nnx) * (nz + nnz) + nny * nz + nny * o_zi + o_ci
                    n2o_b2b_l2l[n_bli] = o_bli
                    n2o_b2b_g2g.append(o_bgi)
                    n_bgi += 1
    # Return
    values = parsed_values
    maps = [n2o_l2l_l2l, n2o_l2l_g2g, n2o_b2b_l2l, n2o_b2b_g2g]
    return parsed_rows, values, maps
