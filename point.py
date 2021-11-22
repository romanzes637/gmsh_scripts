import logging
from itertools import product

import numpy as np

from coordinate_system import str2obj as cs_factory
from coordinate_system import CoordinateSystem, Cartesian, Cylindrical, \
    Spherical, Toroidal, Tokamak
from support import beta_cdf, beta_pdf


class Point:
    """Point
    Args:
        tag (int or None): unique id
        zone (str or None): zone
        coordinate_system (str or dict or CoordinateSystem or None): coordinate system
        coordinates (list of float or np.ndarray or None): coordinates values

    Attributes:
        tag (int or None): unique id
        zone (str or None): zone
        coordinate_system (CoordinateSystem): coordinate system
        coordinates (np.ndarray): coordinates values
        kwargs (dict or None): other keyword arguments (e.g. meshSize)
    """

    def __init__(self, *args, tag=None, zone=None, coordinate_system=None,
                 coordinates=None, **kwargs):
        if len(args) > 0:
            tag, zone, coordinate_system, coordinates, kwargs = self.parse_args(args)
        self.tag = tag
        self.zone = zone
        self.coordinate_system = self.parse_coordinate_system(coordinate_system)
        self.coordinates = self.parse_coordinates(coordinates, self.coordinate_system)
        self.kwargs = kwargs

    @staticmethod
    def parse_coordinate_system(coordinate_system, default=Cartesian(),
                                name_key='name'):
        if coordinate_system is None:
            coordinate_system = default
        elif isinstance(coordinate_system, CoordinateSystem):
            pass
        elif isinstance(coordinate_system, str):
            coordinate_system = cs_factory[coordinate_system]()
        elif isinstance(coordinate_system, dict):
            name = coordinate_system[name_key]
            coordinate_system = cs_factory[name](**coordinate_system)
        else:
            raise ValueError(coordinate_system)
        return coordinate_system

    @staticmethod
    def parse_coordinates(coordinates, coordinate_system):
        if coordinates is None:
            coordinates = np.zeros(coordinate_system.dim, dtype=np.float)
        elif isinstance(coordinates, np.ndarray):
            if coordinates.dtype != np.float:
                coordinates = coordinates.astype(np.float)
        elif isinstance(coordinates, list):
            coordinates = np.array(coordinates, dtype=np.float)
        else:
            raise ValueError(coordinates)
        return coordinates

    @staticmethod
    def parse_args(args):
        """Parse list
        Patterns:
        1. [coordinates]
        2. [coordinates, meshSize]
        3. [coordinates, coordinate_system]
        4. [coordinates, zone]
        5. [coordinates, meshSize, coordinate_system]
        5. [coordinates, coordinate_system, zone]
        5. [coordinates, meshSize, zone]
        5. [coordinates, meshSize, coordinate_system, zone]

        Args:
            args (list):

        Returns:
            int or None, str or None, CoordinateSystem or None, list of float, dict:
        """
        tag, zone = None, None
        coordinate_system, coordinates, kwargs = None, None, {}
        if len(args) == 1 and isinstance(args[0], list):  # init by list
            a = args[0]
            n_nums = 0  # number of numerical items in a
            for x in a:
                if isinstance(x, float) or isinstance(x, int):
                    n_nums += 1
                else:
                    break
            nums, others = a[:n_nums], a[n_nums:]
            # Process others
            if len(others) == 0:
                pass  # default
            elif len(others) == 1:  # coordinate system or zone
                o1 = others[0]
                if isinstance(o1, str):
                    if o1 in cs_factory:  # coordinate system
                        coordinate_system = Point.parse_coordinate_system(o1)
                        # logging.warning(f'May be a name conflict between zone and coordinate system: {o1}')
                    else:  # zone
                        zone = o1
                else:  # coordinate system
                    coordinate_system = Point.parse_coordinate_system(o1)
            elif len(others) == 2:  # coordinate system and zone
                o1, o2 = others
                coordinate_system = Point.parse_coordinate_system(o1)
                zone = o2
            else:
                raise ValueError(a)
            # Split nums into coordinates and meshSize
            dim = coordinate_system.dim if coordinate_system is not None else Cartesian().dim
            if n_nums == dim:  # coordinates, ...
                coordinates = nums
            elif n_nums - 1 == dim:  # coordinates, meshSize, ...
                coordinates = nums[:-1]
                kwargs['meshSize'] = nums[-1]
            else:
                raise ValueError(a)
        else:
            raise ValueError(args)
        return tag, zone, coordinate_system, coordinates, kwargs

    @staticmethod
    def parse_points(points=None, do_deg2rad=False):
        """Parse list of raw points
        Patterns
        1. [[], [], [], ...]
        2. [[], [], [], ..., meshSize]
        3. [[], [], [], ..., coordinate_system]
        4. [[], [], [], ..., zone]
        5. [[], [], [], ..., meshSize, coordinate_system]
        6. [[], [], [], ..., coordinate_system, zone]
        7. [[], [], [], ..., meshSize, zone]
        8. [[], [], [], ..., meshSize, coordinate_system, zone]
        9. [{}, {}, {}, ...]
        10. [{}, {}, {}, ..., meshSize]
        11. [{}, {}, {}, ..., coordinate_system]
        12. [{}, {}, {}, ..., zone]
        13. [{}, {}, {}, ..., meshSize, coordinate_system]
        14. [{}, {}, {}, ..., coordinate_system, zone]
        15. [{}, {}, {}, ..., meshSize, zone]
        16. [{}, {}, {}, ..., meshSize, coordinate_system, zone]

        Args:
            points (list or None): raw points
            do_deg2rad (bool): do degrees to radians conversion

        Returns:
            list of Point: points objects
        """
        points = [] if points is None else points
        # Evaluate number of points
        n_points = 0
        for p in points:
            if isinstance(p, list) or isinstance(p, dict):
                n_points += 1
            else:
                break
        # Split points and others
        points, others = points[:n_points], points[n_points:]
        if len(others) > 0:
            ms, cs, z = None, None, None  # meshSize, coordinate_system, zone
            if len(others) == 1:
                o1 = others[0]
                if isinstance(o1, float) or isinstance(o1, int):
                    ms = o1
                elif isinstance(o1, str):
                    if o1 in cs_factory:  # coordinate system
                        cs = o1
                        # logging.warning(f'May be a name conflict between zone and coordinate system: {o1}')
                    else:  # zone
                        z = o1
                elif isinstance(o1, CoordinateSystem):
                    cs = o1
                else:
                    raise ValueError(others, o1)
            elif len(others) == 2:
                o1, o2 = others
                if isinstance(o1, str) and isinstance(o2, str):
                    cs, z = o1, o2
                elif isinstance(o1, float) or isinstance(o1, int):
                    ms = o1
                    if o2 in cs_factory:  # coordinate system
                        cs = o2
                        # logging.warning(f'May be a name conflict between zone and coordinate system: {o2}')
                    else:  # zone
                        z = o2
                else:
                    raise ValueError(others)
            elif len(others) == 3:
                ms, cs, z = others
            else:
                raise ValueError(others)
            for i, p in enumerate(points):
                if isinstance(p, dict):
                    p.setdefault('coordinate_system', cs)
                    p.setdefault('zone', z)
                    if ms is not None:
                        p.setdefault('meshSize', ms)
                elif isinstance(p, list):
                    if ms is not None:
                        p += [ms]
                    if cs is not None:
                        p += [cs]
                    if z is not None:
                        p += [z]
                    tag, zone, coordinate_system, coordinates, kwargs = Point.parse_args([p])
                    p = {'tag': tag, 'coordinates': coordinates}
                    p['coordinate_system'] = coordinate_system if coordinate_system is not None else cs
                    p['zone'] = zone if zone is not None else z
                    p.update(kwargs)
                    if ms is not None:
                        p.setdefault('meshSize', ms)
                else:
                    raise ValueError(p)
                points[i] = p
        # Make objects
        for i, p in enumerate(points):
            if isinstance(p, dict):
                points[i] = Point(**p)
            elif isinstance(p, list):
                points[i] = Point(p)
            else:
                raise ValueError(p)
        # Change degrees to radians
        if do_deg2rad:
            for p in points:
                if isinstance(p.coordinate_system, Cylindrical):
                    p.coordinates[1] = np.deg2rad(p.coordinates[1])
                elif any([isinstance(p.coordinate_system, Spherical),
                          isinstance(p.coordinate_system, Toroidal),
                          isinstance(p.coordinate_system, Tokamak)]):
                    p.coordinates[1] = np.deg2rad(p.coordinates[1])
                    p.coordinates[2] = np.deg2rad(p.coordinates[2])
        return points


def parse_grid(grid, sep_i=';', sep_si=':'):
    """Parse grid

    Args:
        grid (list of list): grid
        sep_i (str): items separator
        sep_si (str): sub-items separator

    Returns:
        tuple: grid, values, maps
    """
    # Parse grid rows
    new_grid, grid_values, grid_maps = [], [], []
    for row in grid:
        new_row, values, maps = parse_grid_row(row, sep_i, sep_si)
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


def parse_grid_row(row, sep_i=';', sep_si=':'):
    """Parse a row of the grid

    Args:
        row (list): row to parse, [type, i0 (origin), i1, i2, ..., cN]
        sep_i (str): items separator
        sep_si (str): sub-items separator

    Returns:
        tuple: row, values, maps
    """
    # Skip non list rows
    if not isinstance(row, list):
        return row, None, None
    # Default types
    if row[0] not in ['v;p', 'v;s', 'i;p', 'i;s']:
        row = ['v;p'] + row
    # Parse types
    ts, items = row[0], row[1:]  # types, items
    item_t, row_t = ts.split(sep_i)  # item type, row type
    # Old maps
    n_items, n_blocks = len(items), len(items) - 1
    old_b2is = [(x, x + 1) for x in range(n_blocks)]  # Block to items
    old_is2b = {x: i for i, x in enumerate(old_b2is)}  # Items to block
    # Parse row
    cs, ms, ss = [], [], []  # coordinates, mesh sizes, structures
    pc, pm, ps = 0, None, None  # previous (default) values
    new2old_i2i = []  # New item to old item map
    for old_i, item in enumerate(items):
        item_cs, item_ms, item_ss = parse_grid_row_item(
            item, item_t, pc, pm, ps, sep_i, sep_si)
        # TODO interpolate between last cs/ms/ss and first item_cs/ms/ss?
        cs.extend(item_cs[1:])
        ms.extend(item_ms[1:])
        ss.extend(item_ss[1:])
        for _ in item_cs[1:]:
            new2old_i2i.append(old_i)
        pc, pm, ps = cs[-1], ms[-1], ss[-1]
    # New maps
    mew_n_items, new_n_blocks = len(new2old_i2i), len(new2old_i2i) - 1
    new_b2is = [(x, x + 1) for x in range(n_blocks)]  # Block to items
    new_is2b = {x: i for i, x in enumerate(old_b2is)}  # Items to block
    new2old_b2b = []  # New block to old block map
    for new_bi in range(new_n_blocks):
        old_cs = (new2old_i2i[new_bi], new2old_i2i[new_bi + 1])
        while old_cs[0] == old_cs[1]:  # new items can refer to same old items
            new_bi -= 1
            old_cs = (new2old_i2i[new_bi], old_cs[1])
        old_bi = old_is2b[old_cs]
        new2old_b2b.append(old_bi)
    values = [cs, ms, ss]
    maps = [old_b2is, old_is2b, new_b2is, new_is2b, new2old_i2i, new2old_b2b]
    return row, values, maps


def parse_grid_row_item(item, item_t, pc, pm, ps, sep_i, sep_ii):
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
        cs = parse_grid_row_item_coordinate(c, pc, item_t, sep_ii)
        ms = parse_grid_row_item_mesh_size(m, pm, cs, pc, sep_ii)
        ss = parse_grid_row_item_structure(s, cs, sep_ii)
    else:
        raise ValueError(item)
    return cs, ms, ss


def parse_grid_row_item_coordinate(c, pc, item_t, sep):
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


def parse_grid_row_item_mesh_size(m, pm, cs, pc, sep):
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
    vs = m.split(sep)
    ms = []
    if len(vs) == 1:  # linear
        m = float(m)
        pm = m if pm is None else pm
        dm = m - pm
        dc = cs[-1] - pc
        for c in cs:
            rel_c = (c - pc) / dc
            new_m = rel_c * dm + pm
            ms.append(new_m)
    elif len(vs) == 4:
        m, w, a, b = float(vs[0]), float(vs[1]), float(vs[2]), float(vs[3])
        pm = m if pm is None else pm
        dm = m - pm
        dc = cs[-1] - pc
        for c in cs:
            rel_c = (c - pc) / dc
            k = beta_pdf(rel_c, a, b)
            k *= w
            k = k + 1 if k >= 0 else 1 / -k
            new_m = k * (rel_c * dm + pm)
            ms.append(new_m)
    else:
        raise ValueError(vs)
    return ms


def parse_grid_row_item_structure(s, cs, sep=':'):
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


str2obj = {
    Point.__name__: Point,
    Point.__name__.lower(): Point
}
