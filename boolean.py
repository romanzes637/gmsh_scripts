"""Boolean operations on blocks

There are 3 entities after boolean operation on blocks B0 and B1:
1. Residual part of B0
2. Residual part of B1
3. Intersection of B0 and B1

There are 16 combinations of options that are represented in the table.

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
import logging

import gmsh

from support import timeit
from registry import register_boolean_new2olds, register_boolean_old2news


class Boolean:
    def __init__(self):
        pass

    def __call__(self, block):
        timeit(gmsh.model.occ.remove_all_duplicates)()


class NoBoolean(Boolean):
    def __init__(self):
        super().__init__()

    def __call__(self, block):
        pass


class BooleanAllBlock(Boolean):
    def __init__(self):
        super().__init__()

    def __call__(self, block):
        dts = [(3, b.volumes[0].tag) for b in block if b.do_register]
        logging.info(f'n_volumes: {len(dts)}')
        if len(dts) > 1:
            obj_dts, tool_dts = dts[:1], dts[1:]
            new_dts, old_id_to_new_dts = timeit(gmsh.model.occ.fragment)(
                objectDimTags=obj_dts, toolDimTags=tool_dts)
            new2olds, old2news = {}, {}  # New tag and old tags
            for old_id, new_dts in enumerate(old_id_to_new_dts):
                old_tag = dts[old_id][1]
                for new_dt in new_dts:
                    new_tag = new_dt[1]
                    new2olds.setdefault(new_tag, []).append(old_tag)
                    old2news.setdefault(old_tag, []).append(new_tag)
            register_boolean_new2olds(m=new2olds)
            register_boolean_old2news(m=old2news)


str2obj = {
    Boolean.__name__: Boolean,
    NoBoolean.__name__: NoBoolean,
    BooleanAllBlock.__name__: BooleanAllBlock
}
