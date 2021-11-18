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


class Boolean:
    def __init__(self):
        pass

    def __call__(self, block):
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
            timeit(self.block_by_block)(b0, b1)

    @staticmethod
    def block_by_block(b0, b1, zone_separator='-'):
        if not b0.is_registered or not b1.is_registered:
            return
        if b0.boolean_level is None or b1.boolean_level is None:
            return
        if len(b0.volumes) == 0 or len(b1.volumes) == 0:
            return
        logging.info(f'b0 {id(b0)} - {b0.boolean_level} level, '
                     f'{" ".join(sorted(set([x for x in b0.volumes_zones])))} zones, '
                     f'{len(b0.volumes)} volumes and '
                     f'b1 {id(b1)} - {b1.boolean_level} level, '
                     f'{" ".join(sorted(set([x for x in b1.volumes_zones])))} zones, '
                     f'{len(b1.volumes)} volumes')
        # Boolean operation
        obj_dts = [(3, x.tag) for x in b0.volumes]
        tool_dts = [(3, x.tag) for x in b1.volumes]
        new_dts, old_id_to_new_dts = timeit(gmsh.model.occ.fragment)(
            objectDimTags=obj_dts, toolDimTags=tool_dts)
        # New dim-tag to old indices map
        new_dt_to_old_ids = {}
        for old_id, dts in enumerate(old_id_to_new_dts):
            for dt in dts:
                new_dt_to_old_ids.setdefault(dt, []).append(old_id)
        # Update object volumes
        new_b0_volumes, new_b1_volumes = [], []
        for new_dt, old_is in new_dt_to_old_ids.items():
            new_tag = new_dt[1]
            if len(old_is) == 1:  # Non intersected volume (Update tag only)
                old_i = old_is[0]
                if old_i < len(b0.volumes):  # Update b0 volume
                    old_v = b0.volumes[old_i]
                    old_v.tag = new_tag
                    new_b0_volumes.append(old_v)
                else:  # Update b1 volume
                    old_v = b1.volumes[old_i - len(b0.volumes)]
                    old_v.tag = new_tag
                    new_b1_volumes.append(old_v)
            else:  # Intersected volume
                if b1.boolean_level > b0.boolean_level:  # Add volume to b1
                    new_v = Volume(tag=new_tag, zone=b1.volumes_zones[0])  # TODO Other fields?
                    new_b1_volumes.append(new_v)
                elif b0.boolean_level > b1.boolean_level:  # Add volume to b0
                    new_v = Volume(tag=new_tag, zone=b0.volumes_zones[0])  # TODO Other fields?
                    new_b0_volumes.append(new_v)
                else:  # No tool and object (TODO ADD volume to b1?)
                    zones = set(x for x in [b0.volumes_zones[0], b1.volumes_zones[0]] if x is not None)
                    new_zone = zone_separator.join(sorted(zones)) if len(zones) > 0 else zones
                    new_v = Volume(tag=new_tag, zone=new_zone)  # TODO Other fields?
                    new_b1_volumes.append(new_v)
        b0.volumes = new_b0_volumes
        b1.volumes = new_b1_volumes


class BooleanBoundingBox(Boolean):
    """Do boolean if there is bounding boxes intersection

    Bounding box [min_x, min_y, min_z, max_x, max_y, max_z]
    """
    def __init__(self):
        super().__init__()

    def __call__(self, block):
        b2bb = {}
        n_blocks = 0
        for b in block:
            b2bb[b] = self.get_bb(b)
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
                timeit(self.block_by_block)(b0, b1)

    @staticmethod
    def get_bb(block):
        if block.is_registered:
            bbs = np.array([gmsh.model.getBoundingBox(3, x.tag) for x in block.volumes])
            bb = np.concatenate([bbs[:, :3].min(axis=0), bbs[:, 3:].max(axis=0)])
        else:
            bb = np.array([-np.inf, -np.inf, -np.inf, np.inf, np.inf, np.inf])
        return bb


str2obj = {
    Boolean.__name__: Boolean,
    Boolean.__name__.lower(): Boolean,
    BooleanBoundingBox.__name__: BooleanBoundingBox,
    BooleanBoundingBox.__name__.lower(): BooleanBoundingBox,
}
