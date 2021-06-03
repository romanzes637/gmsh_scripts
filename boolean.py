import time
import itertools
import logging


def timing(f):
    def wrapper(*args, **kwargs):
        t0 = time.perf_counter()
        out = f(*args, **kwargs)
        logging.debug('{:.3f}s'.format(time.perf_counter() - t0))
        return out

    return wrapper


def sort_object_no_shared_tool_no_shared(
        factory, object_volumes, tool_volumes, shared_volumes):
    return object_volumes - shared_volumes, tool_volumes - shared_volumes, \
           shared_volumes


def sort_object_no_shared_tool_shared(
        factory, object_volumes, tool_volumes, shared_volumes):
    return object_volumes - shared_volumes, tool_volumes, shared_volumes


def sort_object_only_shared_tool_no_shared(
        factory, object_volumes, tool_volumes, shared_volumes):
    volumes_to_delete = object_volumes - shared_volumes
    volumes_dim_tags = [(3, x) for x in volumes_to_delete]
    factory.remove(volumes_dim_tags, recursive=True)
    return shared_volumes, tool_volumes - shared_volumes, shared_volumes


def sort_object_only_shared_no_tool(
        factory, object_volumes, tool_volumes, shared_volumes):
    # FIXME workaround OCC bug: if number of objects and tools = 1
    # and there is no shared volumes, OCC doesn't renumber volumes idxs,
    # it follows to removing existing tool volume
    if len(object_volumes) == 1 and len(tool_volumes) == 1 \
            and len(shared_volumes) == 0:
        pass
    else:
        volumes_to_delete = object_volumes ^ tool_volumes  # not shared
        volumes_dim_tags = [(3, x) for x in volumes_to_delete]
        factory.remove(volumes_dim_tags, recursive=True)
    return shared_volumes, set(), shared_volumes


def sort_object_no_shared_no_tool_no_shared(
        factory, object_volumes, tool_volumes, shared_volumes):
    # FIXME workaround OCC bug: if number of objects and tools = 1
    # and there is no shared volumes, OCC doesn't renumber volumes idxs,
    # it follows to removing existing tool volume
    if len(object_volumes) == 1 and len(tool_volumes) == 1 \
            and len(shared_volumes) == 0:
        pass
    else:
        volumes_to_delete = shared_volumes | tool_volumes  # shared and tool
        volumes_dim_tags = [(3, x) for x in volumes_to_delete]
        factory.remove(volumes_dim_tags, recursive=True)
    return object_volumes - shared_volumes, set(), set()


# @timing
def sorted_fragment(
        factory, object_volumes, tool_volumes,
        remove_object=True, remove_tool=True,
        sort_function=sort_object_no_shared_tool_no_shared):
    obj_dim_tags = [(3, x) for x in object_volumes]
    tool_dim_tags = [(3, x) for x in tool_volumes]
    out_dim_tags, map_old_index_to_new_dim_tags = factory.fragment(
        obj_dim_tags, tool_dim_tags, removeObject=remove_object,
        removeTool=remove_tool)
    new_object_volumes = set()
    for i in range(len(object_volumes)):
        new_dim_tags = map_old_index_to_new_dim_tags[i]
        for j in range(len(new_dim_tags)):
            new_object_volumes.add(new_dim_tags[j][1])
    new_tool_volumes = set()
    for i in range(len(object_volumes),
                   len(object_volumes) + len(tool_volumes)):
        new_dim_tags = map_old_index_to_new_dim_tags[i]
        for j in range(len(new_dim_tags)):
            new_tool_volumes.add(new_dim_tags[j][1])
    shared_volumes = new_object_volumes & new_tool_volumes
    return sort_function(factory, new_object_volumes, new_tool_volumes,
                         shared_volumes)


def primitive_pre_boolean(primitive_object, primitive_tool):
    result = True
    # Check intersection of bounding boxes first
    # (this operation less expensive than direct boolean)
    if primitive_object.bounding_box is not None \
            and primitive_tool.bounding_box is not None:
        if primitive_object.bounding_box[0] > primitive_tool.bounding_box[3]:
            # obj_x_min > tool_x_max
            result = False
        if primitive_object.bounding_box[1] > primitive_tool.bounding_box[4]:
            # obj_y_min > tool_y_max
            result = False
        if primitive_object.bounding_box[2] > primitive_tool.bounding_box[5]:
            # obj_z_min > tool_z_max
            result = False
        if primitive_object.bounding_box[3] < primitive_tool.bounding_box[0]:
            # obj_x_max < tool_x_min
            result = False
        if primitive_object.bounding_box[4] < primitive_tool.bounding_box[1]:
            # obj_y_max < tool_y_min
            result = False
        if primitive_object.bounding_box[5] < primitive_tool.bounding_box[2]:
            # obj_z_max < tool_z_min
            result = False
    if not result:
        logging.debug("No bounding box intersection")
    # Check on empty primitive_obj:
    if len(primitive_object.volumes) <= 0:
        result = False
        logging.warning("Warning! Empty object")
    # Check on empty primitive_tool:
    if len(primitive_tool.volumes) <= 0:
        result = False
        logging.warning("Warning! Empty tool")
    return result


def primitive_by_primitive(factory, primitive_object, primitive_tool,
                           remove_object=True, remove_tool=True,
                           sort_function=sort_object_no_shared_tool_shared,
                           pre_boolean=True):
    if pre_boolean:
        result = primitive_pre_boolean(primitive_object, primitive_tool)
    else:
        result = True
    logging.debug(f'pre_boolean result: {result}')
    if result:
        logging.debug(f'boolean levels: {primitive_object.boolean_level}, '
                      f'{primitive_tool.boolean_level}')
        if primitive_object.boolean_level >= primitive_tool.boolean_level:
            logging.debug('Forward')
            object_volumes, tool_volumes, shared_volumes = sorted_fragment(
                factory, primitive_object.volumes, primitive_tool.volumes,
                remove_object, remove_tool, sort_function)
            primitive_object.volumes = list(object_volumes)
            primitive_tool.volumes = list(tool_volumes)
        else:
            logging.debug('Reverse')
            object_volumes, tool_volumes, shared_volumes = sorted_fragment(
                factory, primitive_tool.volumes, primitive_object.volumes,
                remove_object, remove_tool, sort_function)
            primitive_tool.volumes = list(object_volumes)
            primitive_object.volumes = list(tool_volumes)


def primitive_by_primitive_return_shared(
        factory, primitive_object, primitive_tool,
        remove_object=True, remove_tool=True,
        sort_function=sort_object_no_shared_tool_shared,
        pre_boolean=True):
    if pre_boolean:
        result = primitive_pre_boolean(primitive_object, primitive_tool)
    else:
        result = True
    logging.debug(f'pre_boolean result: {result}')
    if result:
        object_volumes, tool_volumes, shared_volumes = sorted_fragment(
            factory, primitive_object.volumes, primitive_tool.volumes,
            remove_object, remove_tool, sort_function)
        primitive_object.volumes = list(object_volumes)
        primitive_tool.volumes = list(tool_volumes)
        return shared_volumes
    else:
        return set()


def complex_by_complex(factory, complex_object, complex_tool,
                       remove_object=True, remove_tool=True,
                       sort_function=sort_object_no_shared_tool_shared,
                       pre_boolean=True):
    for i, primitive_object in enumerate(complex_object.primitives):
        for j, primitive_tool in enumerate(complex_tool.primitives):
            logging.debug(f"{i + 1}/{len(complex_object.primitives)} "
                          f"{primitive_object.volume_name} "
                          f"by {j + 1}/{len(complex_tool.primitives)} "
                          f"{primitive_tool.volume_name}")
            primitive_by_primitive(factory, primitive_object, primitive_tool,
                                   remove_object, remove_tool, sort_function,
                                   pre_boolean)


def complex_by_complex_return_shared(
        factory, complex_object, complex_tool,
        remove_object=True, remove_tool=True,
        sort_function=sort_object_no_shared_tool_shared,
        pre_boolean=True):
    shared_volumes = set()
    for i, primitive_object in enumerate(complex_object.primitives):
        for j, primitive_tool in enumerate(complex_tool.primitives):
            logging.debug("{}/{} {} by {}/{} {}".format(
                            i + 1, len(complex_object.primitives),
                            primitive_object.volume_name,
                            j + 1, len(complex_tool.primitives),
                            primitive_tool.volume_name))
            shared_volumes.union(
                primitive_by_primitive_return_shared(factory, primitive_object,
                                                     primitive_tool,
                                                     remove_object, remove_tool,
                                                     sort_function,
                                                     pre_boolean))
    return shared_volumes


def complex_self(factory, complex_object, pre_boolean=True):
    n_primitives = len(complex_object.primitives)
    combinations = list(itertools.combinations(range(n_primitives), 2))
    for i, c in enumerate(combinations):
        t0 = time.perf_counter()
        logging.debug(f"{i + 1}/{len(combinations)} "
                      f"({c[0]} {complex_object.primitives[c[0]].volume_name} by "
                      f"{c[1]} {complex_object.primitives[c[1]].volume_name})")
        primitive_by_primitive(factory, complex_object.primitives[c[0]],
                               complex_object.primitives[c[1]],
                               pre_boolean=pre_boolean)
        logging.debug(f'{time.perf_counter() - t0:.3f}s')


def complex_self_return_shared(factory, complex_object, pre_boolean=True):
    shared_volumes = set()
    n_primitives = len(complex_object.primitives)
    combinations = list(itertools.combinations(range(n_primitives), 2))
    for i, c in enumerate(combinations):
        logging.debug("{}/{} ({} {} by {} {})".format(
                        i + 1, len(combinations),
                        c[0], complex_object.primitives[c[0]].volume_name,
                        c[1], complex_object.primitives[c[1]].volume_name))
        shared_volumes.union(primitive_by_primitive_return_shared(
            factory,
            complex_object.primitives[c[0]],
            complex_object.primitives[c[1]],
            pre_boolean=pre_boolean)
        )
    return shared_volumes


def primitive_by_complex(factory, primitive_object, complex_tool,
                         remove_object=True, remove_tool=True,
                         sort_function=sort_object_no_shared_tool_shared,
                         pre_boolean=True):
    for i, primitive_tool in enumerate(complex_tool.primitives):
        logging.debug("{} by {}/{} {}".format(
            primitive_object.volume_name, i + 1, len(complex_tool.primitives),
            primitive_tool.volume_name))
        primitive_by_primitive(factory, primitive_object, primitive_tool,
                               remove_object,
                               remove_tool, sort_function, pre_boolean)


def primitive_by_complex_return_shared(
        factory, primitive_object, complex_tool,
        remove_object=True, remove_tool=True,
        sort_function=sort_object_no_shared_tool_shared,
        pre_boolean=True):
    shared_volumes = set()
    for i, primitive_tool in enumerate(complex_tool.primitives):
        logging.debug("{} by {}/{} {}".format(
            primitive_object.volume_name, i + 1, len(complex_tool.primitives),
            primitive_tool.volume_name))
        shared_volumes.union(primitive_by_primitive_return_shared(
            factory, primitive_object, primitive_tool, remove_object,
            remove_tool, sort_function, pre_boolean))
    return shared_volumes


def complex_by_primitive(factory, complex_object, primitive_tool,
                         remove_object=True, remove_tool=True,
                         sort_function=sort_object_no_shared_tool_shared,
                         pre_boolean=True):
    for i, primitive_object in enumerate(complex_object.primitives):
        logging.debug("{}/{} {} by {}".format(
            i + 1, len(complex_object.primitives),
            primitive_object.volume_name, primitive_tool.volume_name))
        primitive_by_primitive(factory, primitive_object, primitive_tool,
                               remove_object, remove_tool, sort_function,
                               pre_boolean)


def complex_by_primitive_return_shared(
        factory, complex_object, primitive_tool,
        remove_object=True, remove_tool=True,
        sort_function=sort_object_no_shared_tool_shared,
        pre_boolean=True):
    shared_volumes = set()
    for i, primitive_object in enumerate(complex_object.primitives):
        logging.debug("{}/{} {} by {}".format(
            i + 1, len(complex_object.primitives),
            primitive_object.volume_name, primitive_tool.volume_name))
        shared_volumes.union(primitive_by_primitive_return_shared(
            factory, primitive_object, primitive_tool, remove_object,
            remove_tool, sort_function, pre_boolean))
    return shared_volumes


def primitive_by_volumes(
        factory, primitive_object, volumes,
        remove_object=True, remove_tool=True,
        sort_function=sort_object_no_shared_tool_shared):
    object_volumes, tool_volumes, shared_volumes = sorted_fragment(
        factory, primitive_object.volumes, volumes, remove_object, remove_tool,
        sort_function)
    primitive_object.volumes = list(object_volumes)


def complex_by_volumes(
        factory, complex_object, volumes,
        remove_object=True, remove_tool=True,
        sort_function=sort_object_no_shared_tool_shared):
    for i, primitive_object in enumerate(complex_object.primitives):
        logging.debug("{}/{} {} by volumes {}".format(
            i + 1, len(complex_object.primitives),
            primitive_object.volume_name, volumes))
        primitive_by_volumes(factory, primitive_object, volumes, remove_object,
                             remove_tool, sort_function)


@timing
def complex_to_union_volume(factory, complex_object):
    volumes = complex_object.get_volumes()
    dim_tags = [(3, x) for x in volumes]
    out_dim_tags, out_dim_tags_map = factory.fuse(
        dim_tags[:1], dim_tags[1:],
        tag=-1, removeObject=False, removeTool=False)
    volume = out_dim_tags[0][1]
    return volume
