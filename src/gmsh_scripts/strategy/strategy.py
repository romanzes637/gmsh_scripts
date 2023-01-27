import logging
import uuid

import gmsh

from gmsh_scripts.registry import reset as reset_registry
from gmsh_scripts.registry import synchronize as synchronize_registry
from gmsh_scripts.support.support import timeit, plot_statistics, plot_quality
from gmsh_scripts.boolean.boolean import BooleanAllBlock
from gmsh_scripts.zone.zone import DirectionByNormal
from gmsh_scripts.zone.zone import Block as BlockZone
from gmsh_scripts.size.size import NoSize
from gmsh_scripts.structure.structure import StructureBlock
from gmsh_scripts.quadrate.quadrate import  NoQuadrate
from gmsh_scripts.optimize.optimize import OptimizeOne
from gmsh_scripts.smooth.smooth import NoSmooth
from gmsh_scripts.refine.refine import NoRefine


class Strategy:
    """Abstract strategy"""
    def __init__(self, factory=None, model_name=None, output_path=None,
                 output_formats=None):
        factory = 'geo' if factory is None else factory
        model_name = str(uuid.uuid1()) if model_name is None else model_name
        output_path = model_name if output_path is None else output_path
        output_formats = ['geo_unrolled', 'msh2'] if output_formats is None else output_formats
        self.factory = factory
        self.model_name = model_name
        self.output_path = output_path
        self.output_formats = output_formats
        logging.info(f'factory: {factory}')
        logging.info(f'model_name: {model_name}')
        logging.info(f'output_path: {output_path}')
        logging.info(f'output_formats: {output_formats}')

    def __call__(self, block):
        reset_registry(factory=self.factory)
        logging.info(f'number of blocks: {len(block)}')


class Base(Strategy):
    """Default strategy"""
    def __init__(
            self,
            factory=None,
            model_name=None,
            output_path=None,
            output_formats=None,
            boolean_function=BooleanAllBlock(),
            zone_function=DirectionByNormal(),
            size_function=NoSize(),
            structure_function=StructureBlock(),
            quadrate_function=NoQuadrate(),
            optimize_function=OptimizeOne(),
            refine_function=NoRefine(),
            smooth_function=NoSmooth(),
    ):
        super().__init__(factory, model_name, output_path, output_formats)
        self.boolean_function = boolean_function
        self.zone_function = zone_function
        self.size_function = size_function
        self.structure_function = structure_function
        self.quadrate_function = quadrate_function
        self.optimize_function = optimize_function
        self.refine_function = refine_function
        self.smooth_function = smooth_function

    def __call__(self, block):
        super().__call__(block)
        gmsh.logger.start()
        gmsh.model.add(self.model_name)
        timeit(block.transform)()
        timeit(block.register)()
        if self.factory == 'geo':
            timeit(synchronize_registry)()
            timeit(self.structure_function)(block)  # Must be after synchronize!
            timeit(self.quadrate_function)(block)
            timeit(synchronize_registry)()  # Must be after structure!
            timeit(block.pre_unregister)()  # Must be after synchronize!
            timeit(self.zone_function)(block)  # Must be after unregister!
            timeit(block.unregister)()  # Must be after synchronize!
            if 'geo_unrolled' in self.output_formats:
                timeit(gmsh.write)(f'{self.model_name}.geo_unrolled')
        elif self.factory == 'occ':
            timeit(self.boolean_function)(block)
            timeit(synchronize_registry)()
            timeit(self.structure_function)(block)
            timeit(self.quadrate_function)(block)
            timeit(self.smooth_function)()
            timeit(self.size_function)(block)
            timeit(block.pre_unregister)()
            timeit(self.zone_function)(block)
            timeit(block.unregister)()
            if 'geo_unrolled' in self.output_formats:
                path = f'{self.output_path}-boolean.geo_unrolled'
                logging.info(f'Writing {path}')
                timeit(gmsh.write)(path)
            timeit(gmsh.model.mesh.generate)(3)
            timeit(self.refine_function)()
            timeit(self.optimize_function)()
            plot_statistics()
            plot_quality()
            for f in self.output_formats:
                if f != 'geo_unrolled':
                    path = f'{self.output_path}.{f}'
                    logging.info(f'Writing {path}')
                    timeit(gmsh.write)(path)
            gmsh.logger.stop()
        else:
            raise ValueError(self.factory)
        gmsh.model.remove()


class Fast(Strategy):
    """Generates geometry only (.geo_unrolled file)"""
    def __init__(self, factory=None, model_name=None, output_path=None,
                 output_formats=None):
        super().__init__(factory, model_name, output_path, output_formats)

    def __call__(self, block):
        super().__call__(block)
        gmsh.logger.start()
        gmsh.model.add(self.model_name)
        timeit(block.transform)()
        timeit(block.register)()
        if self.factory == 'geo':
            timeit(synchronize_registry)()
            timeit(block.unregister)()
            timeit(synchronize_registry)()
        elif self.factory == 'occ':
            timeit(synchronize_registry)()
            timeit(block.unregister)()
        else:
            raise ValueError(self.factory)
        if 'geo_unrolled' in self.output_formats:
            path = f'{self.output_path}.geo_unrolled'
            logging.info(f'Writing {path}')
            timeit(gmsh.write)(path)
        timeit(gmsh.model.mesh.generate)(3)
        plot_statistics()
        plot_quality()
        for f in self.output_formats:
            if f != 'geo_unrolled':
                path = f'{self.output_path}.{f}'
                logging.info(f'Writing {path}')
                timeit(gmsh.write)(path)
        log = gmsh.logger.get()
        for x in log:
            logging.info(x)
        gmsh.logger.stop()
        gmsh.model.remove()


class NoBoolean(Strategy):
    """Doesn't use boolean operations"""
    def __init__(
            self,
            factory=None,
            model_name=None,
            output_path=None,
            output_formats=None,
            zone_function=BlockZone(),
            size_function=NoSize(),
            structure_function=StructureBlock(),
            quadrate_function=NoQuadrate(),
            optimize_function=OptimizeOne(),
            refine_function=NoRefine(),
            smooth_function=NoSmooth(),
    ):
        super().__init__(factory, model_name, output_path, output_formats)
        self.zone_function = zone_function
        self.size_function = size_function
        self.structure_function = structure_function
        self.quadrate_function = quadrate_function
        self.optimize_function = optimize_function
        self.refine_function = refine_function
        self.smooth_function = smooth_function

    def __call__(self, block):
        super().__call__(block)
        gmsh.logger.start()
        gmsh.model.add(self.model_name)
        timeit(block.transform)()
        timeit(block.register)()
        timeit(synchronize_registry)()
        timeit(self.structure_function)(block)  # Must be after synchronize!
        timeit(self.quadrate_function)(block)
        timeit(self.smooth_function)()
        timeit(self.size_function)(block)
        timeit(synchronize_registry)()  # Must be after structure!
        timeit(block.pre_unregister)()  # Must be after synchronize!
        timeit(self.zone_function)(block)  # Must be after unregister!
        timeit(block.unregister)()  # Must be after synchronize!
        if 'geo_unrolled' in self.output_formats:
            timeit(gmsh.write)(f'{self.model_name}.geo_unrolled')
        timeit(gmsh.model.mesh.generate)(3)
        timeit(self.refine_function)()
        timeit(self.optimize_function)()
        plot_statistics()
        plot_quality()
        for f in self.output_formats:
            if f != 'geo_unrolled':
                path = f'{self.output_path}.{f}'
                logging.info(f'Writing {path}')
                timeit(gmsh.write)(path)
        gmsh.logger.stop()
        gmsh.model.remove()


str2obj = {
    Base.__name__: Base,
    Fast.__name__: Fast,
    NoBoolean.__name__: NoBoolean
}
