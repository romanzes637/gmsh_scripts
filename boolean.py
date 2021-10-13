import time
import itertools
import logging

import gmsh
import numpy as np

from volume import Volume


def boolean(block):
    blocks = block.get_all_blocks()
    n_blocks = len(blocks)
    logging.info(f'n_blocks: {n_blocks}')
    n_combinations = int(0.5 * (n_blocks * n_blocks - n_blocks))
    logging.info(f'n_combinations: {n_combinations}')
    cnt = 0
    for b0, b1 in itertools.combinations(blocks, 2):
        cnt += 1
        logging.info(f'{cnt}/{n_combinations}')
        block_by_block(b0, b1)


def boolean_with_bounding_boxes(block):
    blocks = block.get_all_blocks()
    n_blocks = len(blocks)
    logging.info(f'n_blocks: {n_blocks}')
    bbs = []
    for b in blocks:
        # FIXME wrong bounding boxes!
        vs_bbs = np.array([gmsh.model.getBoundingBox(3, x.tag) for x in b.volumes])
        bbox = np.concatenate([vs_bbs[:, :3].min(axis=0),
                               vs_bbs[:, 3:].max(axis=0)])
        bbs.append(bbox)
    n_combinations = int(0.5 * (n_blocks * n_blocks - n_blocks))
    logging.info(f'n_combinations: {n_combinations}')
    cnt = 0
    for i0, i1 in itertools.combinations(range(n_blocks), 2):
        cnt += 1
        logging.info(f'{cnt}/{n_combinations}')
        bb0, bb1 = bbs[i0], bbs[i1]
        # Check bbox intersection
        do_boolean = True
        # for x, y, z: min > max, max < min
        if any((bb0[0] > bb1[3], bb0[3] < bb1[0], bb0[1] > bb1[4],
                bb0[1] > bb1[4], bb0[2] > bb1[5], bb0[2] > bb1[5])):
            do_boolean = False
        logging.info(f'bbox intersection: {do_boolean}')
        # Do boolean operation
        if do_boolean:
            b0, b1 = blocks[i0], blocks[i1]
            block_by_block(b0, b1)


def block_by_block(b0, b1, zone_separator='-'):
    # Object/Tool choice
    if b0.boolean_level is None or b1.boolean_level is None:
        return
    elif b0.boolean_level > b1.boolean_level:
        obj, tool = b1, b0
    elif b0.boolean_level < b1.boolean_level:
        obj, tool = b0, b1
    else:  # equal
        obj, tool = b1, b0
    # Old volumes
    obj_vs = [(3, x.tag) for x in obj.volumes]  # dim, tag
    tool_vs = [(3, x.tag) for x in tool.volumes]  # dim, tag
    if len(obj_vs) == 0 or len(tool_vs) == 0:
        return
    # Old zones
    obj_zs = [x.zone for x in obj.volumes]  # zones
    tool_zs = [x.zone for x in tool.volumes]  # zones
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
    # Update object volumes
    new_volumes = []
    for i, v in enumerate(obj.volumes):
        vs = new_obj_vs[i]
        for new_v in vs:
            new_tag = new_v[1]
            old_ids = new_to_old[new_tag]
            if len(old_ids) == 1:
                v = Volume(tag=new_tag,
                           zone=v.zone,
                           name=v.name,
                           structure=v.structure,
                           quadrate=v.quadrate)
                new_volumes.append(v)
            elif b0.boolean_level == b1.boolean_level:
                new_zs = {zs[x] for x in old_ids}
                if None not in new_zs:
                    v = Volume(tag=new_tag,
                               zone=zone_separator.join(sorted(new_zs)),
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
