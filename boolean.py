"""Boolean operations on blocks

There are 3 entities after boolean operation on blocks B0 and B1:
1. Residual part of B0
2. Residual part of B1
3. Intersection of B0 and B1

After boolean intersection (3) could be moved to B0 (1) or B1 (2) or their union B0-B1 (1-2) or be removed (4 options).

Each residual could be removed (2 options).

There are 2*2*4 = 16 combinations of options that are represented in the table.

Table. Options and corresponding actions

+----+---------+-------------------+---------+---------------------------------------------------+
| n  | Block 0 | Block 0 & Block 1 | Block 1 |                      Actions                      |
+====+=========+===================+=========+===================================================+
|    |         |                   |         |                                                   |
|    |         |                   |         |                                                   |
| 1  |         |                   |         | B0.do_unregister         B1.do_unregister         |
|    |         |                   |         |                                                   |
|    |         |                   |         | B0.do_unregister_boolean B1.do_unregister_boolean |
+----+---------+-------------------+---------+---------------------------------------------------+
|    |         |                   |         |                                                   |
|    |         |                   |         |                                                   |
| 2  |   B0    |                   |         |                          B1.do_unregister         |
|    |         |                   |         |                                                   |
|    |         |                   |         | B0.do_unregister_boolean B1.do_unregister_boolean |
+----+---------+-------------------+---------+---------------------------------------------------+
|    |         |                   |         |                                                   |
|    |         |                   |         |                                                   |
| 3  |         |                   |    B1   | B0.do_unregister                                  |
|    |         |                   |         |                                                   |
|    |         |                   |         | B0.do_unregister_boolean B1.do_unregister_boolean |
+----+---------+-------------------+---------+---------------------------------------------------+
|    |         |                   |         |                                                   |
|    |         |                   |         |                                                   |
| 4  |   B0    |                   |   B1    |                                                   |
|    |         |                   |         |                                                   |
|    |         |                   |         | B0.do_unregister_boolean B1.do_unregister_boolean |
+----+---------+-------------------+---------+---------------------------------------------------+
|    |         |                   |         | B0.boolean_level   ==    B1.boolean_level         |
|    |         |                   |         |                                                   |
| 5  |         |       B0-B1       |         | B0.do_unregister         B1.do_unregister         |
|    |         |                   |         |                                                   |
|    |         |                   |         |                                                   |
+----+---------+-------------------+---------+---------------------------------------------------+
|    |         |                   |         | B0.boolean_level    >    B1.boolean_level         |
|    |         |                   |         |                                                   |
| 6  |         |        B0         |         | B0.do_unregister         B1.do_unregister         |
|    |         |                   |         |                                                   |
|    |         |                   |         |                                                   |
+----+---------+-------------------+---------+---------------------------------------------------+
|    |         |                   |         | B0.boolean_level    <    B1.boolean_level         |
|    |         |                   |         |                                                   |
| 7  |         |        B1         |         | B0.do_unregister         B1.do_unregister         |
|    |         |                   |         |                                                   |
|    |         |                   |         |                                                   |
+----+---------+-------------------+---------+---------------------------------------------------+
|    |         |                   |         | B0.boolean_level   ==    B1.boolean_level         |
|    |         |                   |         |                                                   |
| 8  |   B0    |       B0-B1       |         |                          B1.do_unregister         |
|    |         |                   |         |                                                   |
|    |         |                   |         |                                                   |
+----+---------+-------------------+---------+---------------------------------------------------+
|    |         |                   |         | B0.boolean_level   >     B1.boolean_level         |
|    |         |                   |         |                                                   |
| 9  |   B0    |        B0         |         |                          B1.do_unregister         |
|    |         |                   |         |                                                   |
|    |         |                   |         |                                                   |
+----+---------+-------------------+---------+---------------------------------------------------+
|    |         |                   |         | B0.boolean_level   <     B1.boolean_level         |
|    |         |                   |         |                                                   |
| 10 |   B0    |        B1         |         |                          B1.do_unregister         |
|    |         |                   |         |                                                   |
|    |         |                   |         |                                                   |
+----+---------+-------------------+---------+---------------------------------------------------+
|    |         |                   |         | B0.boolean_level   ==    B1.boolean_level         |
|    |         |                   |         |                                                   |
| 11 |         |       B0-B1       |   B1    | B0.do_unregister                                  |
|    |         |                   |         |                                                   |
|    |         |                   |         |                                                   |
+----+---------+-------------------+---------+---------------------------------------------------+
|    |         |                   |         | B0.boolean_level   >     B1.boolean_level         |
|    |         |                   |         |                                                   |
| 12 |         |        B0         |   B1    | B0.do_unregister                                  |
|    |         |                   |         |                                                   |
|    |         |                   |         |                                                   |
+----+---------+-------------------+---------+---------------------------------------------------+
|    |         |                   |         | B0.boolean_level   <     B1.boolean_level         |
|    |         |                   |         |                                                   |
| 13 |         |        B1         |   B1    | B0.do_unregister                                  |
|    |         |                   |         |                                                   |
|    |         |                   |         |                                                   |
+----+---------+-------------------+---------+---------------------------------------------------+
|    |         |                   |         | B0.boolean_level   ==    B1.boolean_level         |
|    |         |                   |         |                                                   |
| 14 |   B0    |       B0-B1       |   B1    |                                                   |
|    |         |                   |         |                                                   |
|    |         |                   |         |                                                   |
+----+---------+-------------------+---------+---------------------------------------------------+
|    |         |                   |         | B0.boolean_level    >    B1.boolean_level         |
|    |         |                   |         |                                                   |
| 15 |   B0    |        B0         |   B1    |                                                   |
|    |         |                   |         |                                                   |
|    |         |                   |         |                                                   |
+----+---------+-------------------+---------+---------------------------------------------------+
|    |         |                   |         | B0.boolean_level    <    B1.boolean_level         |
|    |         |                   |         |                                                   |
| 16 |   B0    |        B1         |   B1    |                                                   |
|    |         |                   |         |                                                   |
|    |         |                   |         |                                                   |
+----+---------+-------------------+---------+---------------------------------------------------+
"""
import itertools
import logging

import gmsh
import numpy as np

from volume import Volume
from support import timeit


def boolean(block):
    n_blocks = 0
    for _ in block:
        n_blocks += 1
    logging.info(f'n_blocks: {n_blocks}')
    n_combinations = int(0.5 * (n_blocks * n_blocks - n_blocks))
    logging.info(f'n_combinations: {n_combinations}')
    cnt = 0
    for b0, b1 in itertools.combinations(block, 2):
        cnt += 1
        logging.info(f'{cnt}/{n_combinations}')
        timeit(block_by_block)(b0, b1)


def boolean_with_bounding_boxes(block):
    """Do boolean if there is bounding boxes intersection

    Bounding box [min_x, min_y, min_z, max_x, max_y, max_z]

    Args:
        block:

    Returns:
        None
    """
    def get_bb(b):
        if b.is_registered:
            bbs = np.array([gmsh.model.getBoundingBox(3, x.tag) for x in b.volumes])
            bb = np.concatenate([bbs[:, :3].min(axis=0), bbs[:, 3:].max(axis=0)])
        else:
            bb = np.array([-np.inf, -np.inf, -np.inf, np.inf, np.inf, np.inf])
        return bb

    b2bb = {}
    n_blocks = 0
    for b in block:
        b2bb[b] = get_bb(b)
        n_blocks += 1
    logging.info(f'n_blocks: {n_blocks}')
    n_combinations = int(0.5 * (n_blocks * n_blocks - n_blocks))
    logging.info(f'n_combinations: {n_combinations}')
    cnt = 0
    for b0, b1 in itertools.combinations(block, 2):
        cnt += 1
        logging.info(f'{cnt}/{n_combinations}')
        bb0 = b2bb[b0]
        bb1 = b2bb[b1]
        # Check bbox intersection
        do_boolean = True
        # for x, y, z: min > max, max < min
        if any((bb0[0] > bb1[3], bb0[3] < bb1[0], bb0[1] > bb1[4],
                bb0[1] > bb1[4], bb0[2] > bb1[5], bb0[2] > bb1[5])):
            do_boolean = False
        logging.info(f'bbox intersection: {do_boolean}')
        # Do boolean operation
        if do_boolean:
            timeit(block_by_block)(b0, b1)


def block_by_block(b0, b1, zone_separator='-'):
    # Object/Tool choice
    if b0.boolean_level is None or b1.boolean_level is None:
        return
    elif b0.boolean_level > b1.boolean_level:
        obj, tool = b1, b0
    elif b0.boolean_level < b1.boolean_level:
        obj, tool = b0, b1
    else:  # equal (random choice)
        obj, tool = b1, b0
    # Old volumes
    obj_vs = [(3, x.tag) for x in obj.volumes]  # dim, tag
    tool_vs = [(3, x.tag) for x in tool.volumes]  # dim, tag
    if len(obj_vs) == 0 or len(tool_vs) == 0:
        return
    # Old zones
    obj_zs = [x.zone for x in obj.volumes]  # zones
    tool_zs = [x.zone for x in tool.volumes]  # zones
    logging.info(f'{" and ".join(set(obj_zs))} by {" and ".join(set(tool_zs))}')
    zs = obj_zs + tool_zs  # all zones
    # Boolean operation
    new_vs, old_to_new = gmsh.model.occ.fragment(
        objectDimTags=obj_vs,
        toolDimTags=tool_vs,
        removeObject=True,
        removeTool=True)
    # New volumes
    new_obj_vs = old_to_new[:len(obj_vs)]  # dim, tag
    new_tool_vs = old_to_new[len(obj_vs):]  # dim, tag
    # New tag to old index
    new_to_old = {}
    for i, vs in enumerate(old_to_new):
        for v in vs:
            tag = v[1]
            new_to_old.setdefault(tag, []).append(i)
    # Set is_booleaned flag
    if not obj.is_booleaned:
        obj.is_booleaned = True
        if len(obj_vs) == 1 and len(new_obj_vs[0]) == 1:
            old_tag, new_tag = obj_vs[0][1], new_obj_vs[0][0][1]
            if old_tag == new_tag:
                obj.is_booleaned = False
    if not tool.is_booleaned:
        tool.is_booleaned = True
        if len(tool_vs) == 1 and len(new_tool_vs[0]) == 1:
            old_tag, new_tag = tool_vs[0][1], new_tool_vs[0][0][1]
            if old_tag == new_tag:
                tool.is_booleaned = False
    # Update object volumes
    new_volumes = []
    for i, v in enumerate(obj.volumes):
        vs = new_obj_vs[i]
        for new_v in vs:
            new_tag = new_v[1]
            old_ids = new_to_old[new_tag]
            # Add shared volume only if boolean levels are equal
            if len(old_ids) == 1 or b0.boolean_level == b1.boolean_level:
                new_zone = zone_separator.join(sorted({zs[x] for x in old_ids}))
                v = Volume(tag=new_tag,
                           zone=new_zone,
                           name=v.name,
                           structure=v.structure,
                           quadrate=v.quadrate)
                new_volumes.append(v)
    obj.volumes = new_volumes
    # Update tool volumes
    new_volumes = []
    for i, v in enumerate(tool.volumes):
        vs = new_tool_vs[i]
        for new_v in vs:
            new_tag = new_v[1]
            old_ids = new_to_old[new_tag]
            # Add shared volume only if boolean levels are different
            if len(old_ids) == 1 or b0.boolean_level != b1.boolean_level:
                v = Volume(tag=new_tag,
                           zone=v.zone,
                           name=v.name,
                           structure=v.structure,
                           quadrate=v.quadrate)
                new_volumes.append(v)
    tool.volumes = new_volumes
