import logging

import gmsh

from registry import reset as reset_registry
from support import timeit, plot_statistics
from boolean import boolean_with_bounding_boxes
from zone import BlockDirection
from size import BooleanPoint
from structure import StructureBlock
from quadrate import QuadrateBlock


class Strategy:
    def __init__(self):
        pass

    def __call__(self, factory, block, model_name):
        pass


class Simple(Strategy):
    """

    """

    def __init__(self, zone_function=BlockDirection(
                     dims=(2, 3), make_interface=False,
                     add_volume_tag=True, add_volume_zone=True,
                     add_surface_loop_tag=True, add_in_out_boundary=False),
                 size_function=BooleanPoint(),
                 structure_function=StructureBlock(),
                 quadrate_function=QuadrateBlock()):
        super().__init__()
        self.zone_function = zone_function
        self.size_function = size_function
        self.structure_function = structure_function
        self.quadrate_function = quadrate_function

    def __call__(self, factory, model_name, block):
        reset_registry()
        gmsh.model.add(model_name)
        timeit(block.transform)()
        timeit(block.register)()
        if factory == 'geo':
            timeit(gmsh.model.geo.synchronize)()
            timeit(block.unregister)()
            timeit(self.structure_function)(block)
            timeit(self.quadrate_function)(block)
            timeit(gmsh.model.geo.synchronize)()
        elif factory == 'occ':
            timeit(gmsh.model.occ.synchronize)()
            timeit(block.unregister)()
            timeit(self.structure_function)(block)
            timeit(self.quadrate_function)(block)
        else:
            raise ValueError(factory)
        timeit(self.size_function)(block)
        timeit(self.zone_function)(block)
        timeit(gmsh.write)(f'{model_name}.geo_unrolled')
        timeit(gmsh.model.mesh.generate)(3)
        plot_statistics()
        timeit(gmsh.write)(f'{model_name}.msh2')
        gmsh.model.remove()


class Boolean(Strategy):
    """

    """

    def __init__(self, boolean_function=boolean_with_bounding_boxes,
            zone_function=BlockDirection(
                dims=(2, 3), make_interface=False,
                add_volume_tag=True, add_volume_zone=True,
                add_surface_loop_tag=True, add_in_out_boundary=False),
            size_function=BooleanPoint(),
            structure_function=StructureBlock(),
            quadrate_function=QuadrateBlock()):
        super().__init__()
        self.boolean_function = boolean_function
        self.zone_function = zone_function
        self.size_function = size_function
        self.structure_function = structure_function
        self.quadrate_function = quadrate_function

    def __call__(self, factory, model_name, block):
        reset_registry()
        gmsh.model.add(model_name)
        timeit(block.transform)()
        timeit(block.register)()
        if factory == 'geo':
            timeit(gmsh.model.geo.synchronize)()
            timeit(self.zone_function)(block)
            timeit(gmsh.write)(f'{model_name}.geo_unrolled')
        elif factory == 'occ':
            timeit(gmsh.model.occ.synchronize)()  # for evaluation of bboxes
            timeit(self.boolean_function)(block)
            timeit(gmsh.model.occ.remove_all_duplicates)()
            timeit(block.unregister)()
            timeit(block.unregister_boolean)()
            logging.info([len(gmsh.model.getEntities(x)) for x in range(4)])
            timeit(gmsh.model.occ.synchronize)()
            logging.info([len(gmsh.model.getEntities(x)) for x in range(4)])
            timeit(self.structure_function)(block)
            timeit(self.quadrate_function)(block)
            timeit(self.size_function)(block)
            timeit(self.zone_function)(block)
            timeit(gmsh.write)(f'{model_name}.geo_unrolled')
            timeit(gmsh.model.mesh.generate)(3)
            plot_statistics()
            timeit(gmsh.write)(f'{model_name}.msh2')
        else:
            raise ValueError(factory)
        gmsh.model.remove()
