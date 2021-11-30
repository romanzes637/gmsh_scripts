import logging
import uuid

import gmsh

from registry import reset as reset_registry
from registry import synchronize as synchronize_registry
from support import timeit, plot_statistics
from boolean import BooleanAllBlock
from zone import BlockVolumes
from size import BooleanPoint, NoSize
from structure import StructureBlock, StructureAuto
from quadrate import QuadrateBlock, NoQuadrate
from optimize import OptimizeOne
from smooth import NoSmooth
from refine import NoRefine


class Strategy:
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
    """

    """

    def __init__(
            self,
            factory=None,
            model_name=None,
            output_path=None,
            output_formats=None,
            boolean_function=BooleanAllBlock(),
            zone_function=BlockVolumes(),
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
            timeit(self.zone_function)(block)
            timeit(gmsh.write)(f'{self.model_name}.geo_unrolled')
        elif self.factory == 'occ':
            if 'geo_unrolled' in self.output_formats:
                path = f'{self.output_path}-pre_boolean.geo_unrolled'
                logging.info(f'Writing {path}')
                timeit(gmsh.write)(path)
            timeit(self.boolean_function)(block)
            timeit(synchronize_registry)()
            timeit(self.structure_function)(block)
            timeit(self.quadrate_function)(block)
            timeit(self.smooth_function)()
            timeit(self.size_function)(block)
            timeit(block.unregister)()
            timeit(self.zone_function)(block)
            if 'geo_unrolled' in self.output_formats:
                path = f'{self.output_path}-post_boolean.geo_unrolled'
                logging.info(f'Writing {path}')
                timeit(gmsh.write)(path)
            timeit(gmsh.model.mesh.generate)(3)
            timeit(self.refine_function)()
            timeit(self.optimize_function)()
            for f in self.output_formats:
                if f != 'geo_unrolled':
                    path = f'{self.output_path}.{f}'
                    logging.info(f'Writing {path}')
                    timeit(gmsh.write)(path)
            log = gmsh.logger.get()
            for message in log:
                logging.debug(message)
            gmsh.logger.stop()
            plot_statistics()
        else:
            raise ValueError(self.factory)
        gmsh.model.remove()


class Fast(Strategy):
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
        for f in self.output_formats:
            if f != 'geo_unrolled':
                path = f'{self.output_path}.{f}'
                logging.info(f'Writing {path}')
                timeit(gmsh.write)(path)
        log = gmsh.logger.get()
        for x in log:
            logging.info(x)
        plot_statistics()
        gmsh.logger.stop()
        gmsh.model.remove()


str2obj = {
    Base.__name__: Base,
    Fast.__name__: Fast
}
