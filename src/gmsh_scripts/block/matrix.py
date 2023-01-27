import copy

import numpy as np

from gmsh_scripts.block.block import Block
from gmsh_scripts.parse.parse import parse_grid
from gmsh_scripts.coordinate_system.coordinate_system import str2obj as cs_str2obj
from gmsh_scripts.support.support import flatten


class Matrix(Block):
    """Matrix

    Args:
    """

    def __init__(
            # Matrix
            self,
            matrix=None,
            # points (from matrix)
            items_curves=None, items_curves_map=None,
            # surfaces (default)
            # volumes (default)
            items_do_register_map=None, items_do_register_children_map=None,
            items_do_unregister_map=None, items_do_unregister_children_map=None,
            items_do_unregister_boolean_map=None,
            items_transforms=None, items_transforms_map=None,
            items_self_transforms=None, items_self_transforms_map=None,
            items_do_quadrate_map=None,
            items_do_structure_map=None,
            # structure (from matrix)
            items_structure_type=None, items_structure_type_map=None,
            items_zone=None, items_zone_map=None,
            items_boolean_level_map=None,
            # Items Children
            items_children=None, items_children_map=None,
            items_children_transforms=None, items_children_transforms_map=None,
            # TODO path?
            # Block
            points=None, curves=None, surfaces=None, volume=None,
            do_register=False, do_register_children=True,
            do_unregister=False, do_unregister_children=True,
            do_unregister_boolean=False,
            transforms=None, self_transforms=None,
            do_quadrate=False,
            do_structure=True, structure=None, structure_type='LLL',
            zone=None,
            boolean_level=None,
            path=None,
            parent=None, children=None, children_transforms=None
    ):
        # Parse grid
        new_grid, values, maps = parse_grid(matrix)
        old_b2is, old_b2b_g2l, new_b2is, new_b2b_g2l, new2old_b2b = maps
        str_rows = [x for x in new_grid if isinstance(x, str)]
        num_rows = [x for x in new_grid if isinstance(x, (int, float))]
        global_coordinate_system = 'Cartesian'
        for row in str_rows:
            if row in cs_str2obj:
                global_coordinate_system = row
                break
        for row in new_grid:
            if isinstance(row, tuple(cs_str2obj.values())):
                global_coordinate_system = row
                break
        global_mesh_size = num_rows[0] if len(num_rows) > 0 else 0
        # Evaluate blocks points and structures
        items_points, items_structures = Matrix.evaluate_items_values(
            values, new_b2is, gcs=global_coordinate_system, gm=global_mesh_size)
        # Evaluate maps
        items_curves = [None] if items_curves is None else items_curves
        items_curves_map = Matrix.parse_matrix_items_map(
            items_curves_map, 0, new2old_b2b, (int,))
        # Register
        items_do_register_map = Matrix.parse_matrix_items_map(
            items_do_register_map, 1, new2old_b2b, (bool, int))
        items_do_register_children_map = Matrix.parse_matrix_items_map(
            items_do_register_children_map, 1, new2old_b2b, (bool, int))
        items_do_unregister_map = Matrix.parse_matrix_items_map(
            items_do_unregister_map, 0, new2old_b2b, (bool, int))
        items_do_unregister_children_map = Matrix.parse_matrix_items_map(
            items_do_unregister_children_map, 1, new2old_b2b, (bool, int))
        items_do_unregister_boolean_map = Matrix.parse_matrix_items_map(
            items_do_unregister_boolean_map, 0, new2old_b2b, (bool, int))
        # Structure and Quadrate
        items_do_structure_map = Matrix.parse_matrix_items_map(
            items_do_structure_map, 1, new2old_b2b)  # Do structure by default
        items_do_quadrate_map = Matrix.parse_matrix_items_map(
            items_do_quadrate_map, 0, new2old_b2b)
        if items_structure_type is None:
            items_structure_type = ['LLL']
        items_structure_type_map = Matrix.parse_matrix_items_map(
            items_structure_type_map, 0, new2old_b2b, (int,))
        # Boolean
        items_boolean_level_map = Matrix.parse_matrix_items_map(
            items_boolean_level_map, None, new2old_b2b, (int,))
        # Zones
        items_zone = ['Matrix'] if items_zone is None else items_zone
        items_zone_map = Matrix.parse_matrix_items_map(
            items_zone_map, 0, new2old_b2b, (int,))
        # Transforms
        transforms = [] if transforms is None else transforms
        # Items Transforms
        if items_transforms is None:
            items_transforms = [None]
        items_transforms_map = Matrix.parse_matrix_items_map(
            items_transforms_map, 0, new2old_b2b, (int,))
        # Items Self Transforms
        if items_self_transforms is None:
            items_self_transforms = [None]
        items_self_transforms_map = Matrix.parse_matrix_items_map(
            items_self_transforms_map, 0, new2old_b2b, (int,))
        # Items Children
        items_children = [None] if items_children is None else items_children
        items_children_map = Matrix.parse_matrix_items_map(
            items_children_map, 0, new2old_b2b, (int,))
        # Items Children Transforms TODO bugs...
        if items_children_transforms is None:
            items_children_transforms = [None]
        items_children_transforms_map = Matrix.parse_matrix_items_map(
            items_children_transforms_map, 0, new2old_b2b, (int,))
        t = {"name": "CartesianToCartesianByBlock",
             "block_coordinates": [0, 0, 0]}
        if len(items_children_transforms) == 1:
            ts = items_children_transforms[0]
            if ts is not None:
                items_children_transforms[0] = [[copy.deepcopy(t)] + x
                                                if x is not None else [copy.deepcopy(t)] for x in ts]
            else:
                pass
        else:
            for i, ts in enumerate(items_children_transforms):
                if ts is not None:
                    new_ts = [[copy.deepcopy(t)] + x
                              if x is not None else [copy.deepcopy(t)] for x in ts]
                else:
                    new_ts = ts
                items_children_transforms[i] = new_ts
        # Items
        items = [Block(
            points=x,
            curves=items_curves[items_curves_map[i]]
            if items_curves_map[i] is not None else None,
            do_register=items_do_register_map[i],
            do_register_children=items_do_register_children_map[i],
            do_unregister=items_do_unregister_map[i],
            do_unregister_children=items_do_unregister_children_map[i],
            do_unregister_boolean=items_do_unregister_boolean_map[i],
            transforms=copy.deepcopy(
                items_transforms[items_transforms_map[i]]),
            self_transforms=copy.deepcopy(
                items_self_transforms[items_self_transforms_map[i]]),
            do_quadrate=items_do_quadrate_map[i],
            do_structure=items_do_structure_map[i],
            structure=items_structures[i],
            structure_type=items_structure_type[items_structure_type_map[i]]
            if items_structure_type_map[i] is not None else None,
            zone=items_zone[items_zone_map[i]],
            boolean_level=items_boolean_level_map[i],
            parent=self,
            children=copy.deepcopy(
                items_children[items_children_map[i]]),
            children_transforms=copy.deepcopy(
                items_children_transforms[items_children_transforms_map[i]]))
            for i, x in enumerate(items_points)]
        # All Children (Items + Children)
        children = [] if children is None else children
        all_children = children + items
        # All Children Transforms
        children_items_transforms = [[] for _ in items]
        if children_transforms is None:
            children_transforms = [[] for _ in children]
        all_children_transforms = children_transforms + children_items_transforms
        super().__init__(
            points=points, curves=curves, surfaces=surfaces, volume=volume,
            do_register=do_register,
            do_register_children=do_register_children,
            do_unregister=do_unregister,
            do_unregister_children=do_unregister_children,
            do_unregister_boolean=do_unregister_boolean,
            transforms=transforms,
            self_transforms=self_transforms,
            do_quadrate=do_quadrate,
            do_structure=do_structure,
            structure=structure,
            structure_type=structure_type,
            zone=zone,
            boolean_level=boolean_level,
            path=path,
            parent=parent,
            children=all_children,
            children_transforms=all_children_transforms)

    @staticmethod
    def evaluate_items_values(values, b2ids, gm=0., gs=None, gcs='Cartesian'):
        cs, ms, ss = values
        blocks_points, blocks_structures = [], []
        for bi, ids in enumerate(b2ids):
            if len(ids) == 1:
                s_ids, p_ids0, p_ids1 = ids[0], [], []
            elif len(ids) == 2:
                s_ids, p_ids0, p_ids1 = [], ids[0], ids[1]
            elif len(ids) == 3:
                s_ids, p_ids0, p_ids1 = ids
            else:
                raise ValueError(bi, ids)
            len_s, len_p = len(s_ids), len(p_ids0)
            # Mesh sizes
            mx0, my0, mz0 = [ms[i][x] for i, x in enumerate(p_ids0[-3:][::-1])]
            mx1, my1, mz1 = [ms[i][x] for i, x in enumerate(p_ids1[-3:][::-1])]
            mcs0 = [ms[i + 3][x] for i, x in enumerate(p_ids0[:-3][::-1])]
            mcs1 = [ms[i + 3][x] for i, x in enumerate(p_ids1[:-3][::-1])]
            mcs01 = ms[len_p][int(list(set(s_ids))[0])] if len_s > 0 else []
            block_mesh_sizes = [
                [mx1, my1, mz0] + mcs0 + mcs01,
                [mx0, my1, mz0] + mcs0 + mcs01,
                [mx0, my0, mz0] + mcs0 + mcs01,
                [mx1, my0, mz0] + mcs0 + mcs01,
                [mx1, my1, mz1] + mcs1 + mcs01,
                [mx0, my1, mz1] + mcs1 + mcs01,
                [mx0, my0, mz1] + mcs1 + mcs01,
                [mx1, my0, mz1] + mcs1 + mcs01]
            bms = [[y for y in x if y is not None] for x in block_mesh_sizes]
            bms = [np.mean(x) if len(x) > 0 else gm for x in bms]
            # Coordinates
            x0, y0, z0 = [cs[i][x] for i, x in enumerate(p_ids0[-3:][::-1])]
            x1, y1, z1 = [cs[i][x] for i, x in enumerate(p_ids1[-3:][::-1])]
            cs0 = [cs[i + 3][x] for i, x in enumerate(p_ids0[:-3][::-1])]
            cs1 = [cs[i + 3][x] for i, x in enumerate(p_ids1[:-3][::-1])]
            cs01 = cs[len_p][int(list(set(s_ids))[0])] if len_s > 0 else []
            block_points = [
                [x1, y1, z0] + cs0 + cs01 + [bms[0]],
                [x0, y1, z0] + cs0 + cs01 + [bms[1]],
                [x0, y0, z0] + cs0 + cs01 + [bms[2]],
                [x1, y0, z0] + cs0 + cs01 + [bms[3]],
                [x1, y1, z1] + cs1 + cs01 + [bms[4]],
                [x0, y1, z1] + cs1 + cs01 + [bms[5]],
                [x0, y0, z1] + cs1 + cs01 + [bms[6]],
                [x1, y0, z1] + cs1 + cs01 + [bms[7]],
                gcs]
            # from pprint import pprint
            # pprint(block_points)
            # Structures  TODO Interpolation?
            sx0, sy0, sz0 = [ss[i][x] for i, x in enumerate(p_ids0[-3:][::-1])]
            sx1, sy1, sz1 = [ss[i][x] for i, x in enumerate(p_ids1[-3:][::-1])]
            block_structure = [sx1, sy1, sz1]
            block_structure = [gs if x is None else x
                               for x in block_structure]
            blocks_points.append(block_points)
            blocks_structures.append(block_structure)
        return blocks_points, blocks_structures

    @staticmethod
    def parse_matrix_items_map(m, default, new2old,
                               item_types=(bool, str, int, float)):
        # Default value for all items if map is None
        if m is None:
            m = [default for _ in new2old]
            return m
        m = list(flatten(m)) if isinstance(m, list) else m
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


str2obj = {
    Matrix.__name__: Matrix,
    Matrix.__name__.lower(): Matrix
}
