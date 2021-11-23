import numpy as np

from block import Block
from point import parse_grid
from coordinate_system import str2obj as cs_str2obj


class Matrix(Block):
    """Matrix

    Args:
    """

    def __init__(self,
                 points,
                 curves=None,
                 curves_map=None,
                 parent=None,
                 transforms=None, use_register_tag=False,
                 do_register_map=None,
                 quadrate_map=None,
                 boolean_level_map=None,
                 zone_map=None,
                 structure_type=None,
                 structure_type_map=None,
                 # types=None, type_map=None,
                 # volumes_names=None, volumes_map=None,
                 # surfaces_names=None, surfaces_map=None,
                 # in_surfaces_names=None, in_surfaces_map=None,
                 # in_surfaces_masks=None, in_surfaces_masks_map=None,
                 # transforms=None, transforms_map=None,
                 # inputs=None, inputs_map=None,
                 # recs_map=None, trans_map=None, trans_type_map=None,
                 # curve_types=None, curve_types_map=None,
                 # curve_data=None, curve_data_map=None,
                 # curve_data_coord_sys=None, curve_data_coord_sys_map=None,
                 # inputs_transforms=None, inputs_transforms_map=None,
                 # inputs_transforms_coord_sys=None,
                 # inputs_transforms_coord_sys_map=None,
                 # boolean_level_map=None,
                 ):
        # Parse grid
        new_grid, values, maps = parse_grid(points)
        old_b2is, old_b2b_g2l, new_b2is, new_b2b_g2l, new2old_b2b = maps
        str_rows = [x for x in new_grid if isinstance(x, str)]
        num_rows = [x for x in new_grid if isinstance(x, (int, float))]
        global_coordinate_system = 'cartesian'
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
        blocks_points, blocks_structures = Matrix.evaluate_block_values(
            values, new_b2is, gcs=global_coordinate_system, gm=global_mesh_size)
        # Evaluate maps
        curves_map = Matrix.parse_map(m=curves_map, default=0,
                                      new2old=new2old_b2b, item_types=(int,))
        transforms = [] if transforms is None else transforms
        curves = [None] if curves is None else curves
        do_register_map = Matrix.parse_map(do_register_map, True, new2old_b2b,
                                           item_types=(bool, int))
        quadrate_map = Matrix.parse_map(quadrate_map, None, new2old_b2b)
        boolean_level_map = Matrix.parse_map(boolean_level_map, None, new2old_b2b)
        zone_map = Matrix.parse_map(zone_map, None, new2old_b2b)
        structure_type = ['LLL'] if structure_type is None else structure_type
        structure_type_map = Matrix.parse_map(structure_type_map, 0, new2old_b2b)
        # TODO Optimized version
        children = [Block(points=x,
                          curves=curves[curves_map[i]],
                          use_register_tag=use_register_tag,
                          do_register=do_register_map[i],
                          structure=blocks_structures[i],
                          quadrate=quadrate_map[i],
                          boolean_level=boolean_level_map[i],
                          zone=zone_map[i],
                          transforms=transforms,
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
                         children=children,
                         transforms=transforms,
                         use_register_tag=use_register_tag)

    @staticmethod
    def evaluate_block_values(values, b2ids, gm=0., gs=None, gcs='cartesian'):
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
            # sx0, sy0, sz0 = [ss[i][x] for i, x in enumerate(p_ids0[-3:][::-1])]
            sx1, sy1, sz1 = [ss[i][x] for i, x in enumerate(p_ids1[-3:][::-1])]
            block_structure = [sx1, sy1, sz1]
            block_structure = [gs if x is None else x
                               for x in block_structure]
            blocks_points.append(block_points)
            blocks_structures.append(block_structure)
        return blocks_points, blocks_structures

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


str2obj = {
    Matrix.__name__: Matrix,
    Matrix.__name__.lower(): Matrix
}
