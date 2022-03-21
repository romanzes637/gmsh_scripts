import logging

import gmsh

from gmsh_scripts.support.support import timeit
from gmsh_scripts.registry import register_boolean_new2olds, register_boolean_old2news


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
        dts = [(3, b.volumes[0].tag) for b in block
               if b.volumes[0].tag is not None and b.boolean_level is not None]
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
