import time
import itertools


def timing(f):
    def wrapper(*args, **kwargs):
        start_time = time.time()
        out = f(*args, **kwargs)
        print('{:.3f}s'.format(time.time() - start_time))
        return out

    return wrapper


def sort_object_no_shared_tool_no_shared(factory, object_volumes, tool_volumes, shared_volumes):
    return object_volumes - shared_volumes, tool_volumes - shared_volumes, shared_volumes


def sort_object_shared_tool_shared(factory, object_volumes, tool_volumes, shared_volumes):
    return object_volumes, tool_volumes, shared_volumes


def sort_object_no_shared_tool_shared(factory, object_volumes, tool_volumes, shared_volumes):
    return object_volumes - shared_volumes, tool_volumes, shared_volumes


def sort_object_only_shared_tool_no_shared(factory, object_volumes, tool_volumes, shared_volumes):
    volumes_to_delete = object_volumes - shared_volumes
    volumes_dim_tags = map(lambda x: [3, x], volumes_to_delete)
    factory.remove(volumes_dim_tags, recursive=True)
    return shared_volumes, tool_volumes - shared_volumes, shared_volumes


def sort_object_only_shared_no_tool(factory, object_volumes, tool_volumes, shared_volumes):
    volumes_to_delete = object_volumes ^ tool_volumes  # not shared
    volumes_dim_tags = map(lambda x: [3, x], volumes_to_delete)
    factory.remove(volumes_dim_tags, recursive=True)
    return shared_volumes, set(), shared_volumes


@timing
def sorted_fragment(factory, object_volumes, tool_volumes, remove_object=True, remove_tool=True,
                    sort_function=sort_object_no_shared_tool_no_shared):
    obj_dim_tags = map(lambda x: [3, x], object_volumes)
    tool_dim_tags = map(lambda x: [3, x], tool_volumes)
    out_dim_tags, map_old_index_to_new_dim_tags = factory.fragment(
        obj_dim_tags, tool_dim_tags, removeObject=remove_object, removeTool=remove_tool)
    new_object_volumes = set()
    for i in range(len(object_volumes)):
        new_dim_tags = map_old_index_to_new_dim_tags[i]
        for j in range(len(new_dim_tags)):
            new_object_volumes.add(new_dim_tags[j][1])
    new_tool_volumes = set()
    for i in range(len(object_volumes), len(object_volumes) + len(tool_volumes)):
        new_dim_tags = map_old_index_to_new_dim_tags[i]
        for j in range(len(new_dim_tags)):
            new_tool_volumes.add(new_dim_tags[j][1])
    shared_volumes = new_object_volumes & new_tool_volumes
    return sort_function(factory, new_object_volumes, new_tool_volumes, shared_volumes)


def primitive_pre_boolean(primitive_object, primitive_tool):
    result = True
    # Check intersection of bounding boxes first (this operation less expensive than direct boolean)
    if primitive_object.bounding_box is not None and primitive_tool.bounding_box is not None:
        if primitive_object.bounding_box[0] > primitive_tool.bounding_box[3]:  # obj_x_min > tool_x_max
            result = False
        if primitive_object.bounding_box[1] > primitive_tool.bounding_box[4]:  # obj_y_min > tool_y_max
            result = False
        if primitive_object.bounding_box[2] > primitive_tool.bounding_box[5]:  # obj_z_min > tool_z_max
            result = False
        if primitive_object.bounding_box[3] < primitive_tool.bounding_box[0]:  # obj_x_max < tool_x_min
            result = False
        if primitive_object.bounding_box[4] < primitive_tool.bounding_box[1]:  # obj_y_max < tool_y_min
            result = False
        if primitive_object.bounding_box[5] < primitive_tool.bounding_box[2]:  # obj_z_max < tool_z_min
            result = False
    if not result:
        print("No bounding box intersection")
    # Check on empty primitive_obj:
    if len(primitive_object.volumes) <= 0:
        result = False
        print("Empty object")
    # Check on empty primitive_tool:
    if len(primitive_tool.volumes) <= 0:
        result = False
        print("Empty tool")
    print(result)
    return result


def primitive_by_primitive(factory, primitive_object, primitive_tool, remove_object=True, remove_tool=True,
                           sort_function=sort_object_no_shared_tool_shared):
    result = primitive_pre_boolean(primitive_object, primitive_tool)
    if result:
        object_volumes, tool_volumes, shared_volumes = sorted_fragment(
            factory, primitive_object.volumes, primitive_tool.volumes, remove_object, remove_tool, sort_function)
        primitive_object.volumes = list(object_volumes)
        primitive_tool.volumes = list(tool_volumes)


def complex_by_complex(factory, complex_object, complex_tool, remove_object=True, remove_tool=True,
                       sort_function=sort_object_no_shared_tool_shared):
    for i, primitive_object in enumerate(complex_object.primitives):
        for j, primitive_tool in enumerate(complex_tool.primitives):
            print("{}/{} {} by {}/{} {}".format(
                i + 1, len(complex_object.primitives), primitive_object.physical_name,
                j + 1, len(complex_tool.primitives), primitive_tool.physical_name))
            primitive_by_primitive(factory, primitive_object, primitive_tool, remove_object, remove_tool, sort_function)


def complex_self(factory, complex_object):
    n_primitives = len(complex_object.primitives)
    combinations = list(itertools.combinations(range(n_primitives), 2))
    for i, c in enumerate(combinations):
        print("{}/{} ({} {} by {} {})".format(
            i + 1, len(combinations),
            c[0], complex_object.primitives[c[0]].physical_name,
            c[1], complex_object.primitives[c[1]].physical_name)
        )
        primitive_by_primitive(factory, complex_object.primitives[c[0]], complex_object.primitives[c[1]])


def primitive_by_complex(factory, primitive_object, complex_tool, remove_object=True, remove_tool=True,
                         sort_function=sort_object_no_shared_tool_shared):
    for i, primitive_tool in enumerate(complex_tool.primitives):
        print("{} by {}/{} {}".format(
            primitive_object.physical_name, i + 1, len(complex_tool.primitives), primitive_tool.physical_name))
        primitive_by_primitive(factory, primitive_object, primitive_tool, remove_object, remove_tool, sort_function)


def complex_by_primitive(factory, complex_object, primitive_tool, remove_object=True, remove_tool=True,
                         sort_function=sort_object_no_shared_tool_shared):
    for i, primitive_object in enumerate(complex_object.primitives):
        print("{}/{} {} by {}".format(
            i + 1, len(complex_object.primitives), primitive_object.physical_name, primitive_tool.physical_name))
        primitive_by_primitive(factory, primitive_object, primitive_tool, remove_object, remove_tool, sort_function)


def primitive_by_volumes(factory, primitive_object, volumes, remove_object=True, remove_tool=True,
                         sort_function=sort_object_no_shared_tool_shared):
    object_volumes, tool_volumes, shared_volumes = sorted_fragment(
        factory, primitive_object.volumes, volumes, remove_object, remove_tool, sort_function)
    primitive_object.volumes = list(object_volumes)


def complex_by_volumes(factory, complex_object, volumes, remove_object=True, remove_tool=True,
                       sort_function=sort_object_no_shared_tool_shared):
    for i, primitive_object in enumerate(complex_object.primitives):
        print("{}/{} {} by volumes {}".format(
            i + 1, len(complex_object.primitives), primitive_object.physical_name, volumes))
        primitive_by_volumes(factory, primitive_object, volumes, remove_object, remove_tool, sort_function)


@timing
def complex_to_union_volume(factory, complex_object):
    volumes = complex_object.get_volumes()
    dim_tags = map(lambda x: [3, x], volumes)
    out_dim_tags, out_dim_tags_map = factory.fuse(
        dim_tags[:1], dim_tags[1:], tag=-1, removeObject=False, removeTool=False)
    volume = out_dim_tags[0][1]
    return volume
