import gmsh

from registry import reset as reset_registry
from support import timeit, plot_statistics
from boolean import boolean_with_bounding_boxes
from zone import BlockDirection
from size import BooleanEdge


class Strategy:
    def __init__(self):
        pass

    def __call__(self, block):
        pass


def boolean(factory, model_name, block,
            zone_function=BlockDirection(
                dims=(2, 3), make_interface=False,
                add_volume_tag=True, add_volume_zone=True,
                add_surface_loop_tag=True, add_in_out_boundary=False),
            size_function=BooleanEdge(function='max')):
    reset_registry()
    gmsh.model.add(model_name)
    timeit(block.transform)()
    timeit(block.register)()
    if factory == 'geo':
        timeit(gmsh.model.geo.synchronize)()
        zone_rule = BlockDirection(dims=(2, 3), make_interface=False,
                                   add_volume_tag=True, add_volume_zone=True,
                                   add_surface_loop_tag=True,
                                   add_in_out_boundary=False)
        timeit(zone_rule)(block)
        timeit(gmsh.write)(f'{model_name}.geo_unrolled')
    elif factory == 'occ':
        timeit(gmsh.model.occ.synchronize)()  # for evaluation of bboxes
        timeit(boolean_with_bounding_boxes)(block)
        timeit(gmsh.model.occ.remove_all_duplicates)()
        timeit(block.unregister)()
        timeit(block.unregister_boolean)()
        timeit(gmsh.model.occ.synchronize)()
        timeit(block.quadrate)()
        timeit(block.structure)()
        timeit(zone_function)(block)
        timeit(size_function)(block)
        timeit(gmsh.model.mesh.generate)(3)
        plot_statistics()
        timeit(gmsh.write)(f'{model_name}.msh2')
    else:
        raise ValueError(factory)
    gmsh.model.remove()
