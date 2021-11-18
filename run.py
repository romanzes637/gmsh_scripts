import json
import os
import argparse
import logging
import copy

from support import check_on_file, timeit, \
    LoggingDecorator, GmshDecorator, GmshOptionsDecorator
from factory import FACTORY as FACTORY


def make_block_tree(top_block_path):
    block_real_paths = {}
    blocks_children = {}
    blocks_kwargs = {}
    blocks_paths = {top_block_path}
    while len(blocks_paths) > 0:
        new_blocks_paths = set()
        for block_path in blocks_paths:
            if block_path in block_real_paths:
                continue
            result, real_path = check_on_file(block_path)
            block_real_paths[block_path] = real_path
            with open(real_path) as f:
                block_kwargs = json.load(f)
            blocks_kwargs[block_path] = block_kwargs
            children_paths = block_kwargs['data'].get('children', [])
            blocks_children[block_path] = children_paths
            new_blocks_paths.update(children_paths)
        blocks_paths = new_blocks_paths
    return {'block_real_paths': block_real_paths,
            'blocks_children': blocks_children,
            'blocks_kwargs': blocks_kwargs}


def init_block_tree(block_tree, top_block_path):
    def recurse(parent, parent_path, blocks):
        blocks.append(parent)
        children_paths = block_tree['blocks_children'].get(parent_path, [])
        for i, child_path in enumerate(children_paths):
            child_kwargs = copy.deepcopy(block_tree['blocks_kwargs'][child_path])
            child_kwargs['data']['parent'] = parent
            child_kwargs['data']['path'] = child_path
            child = FACTORY(kwargs=child_kwargs['data'])
            parent.children[i] = child
            recurse(child, child_path, blocks)  # now child is a new parent

    blocks = []
    parent_path = top_block_path
    parent_kwargs = copy.deepcopy(block_tree['blocks_kwargs'][parent_path])
    parent_kwargs['data']['path'] = parent_path
    parent = FACTORY(kwargs=parent_kwargs['data'])
    recurse(parent, parent_path, blocks)
    return blocks


def parse_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument('input_path', help='input path')
    parser.add_argument('-o', '--output_path',
                        help='output file path without extension',
                        default=argparse.SUPPRESS)
    parser.add_argument('-f', '--output_formats', nargs='*',
                        help='output file extension(s)',
                        default=argparse.SUPPRESS,
                        choices=['auto', 'msh1', 'msh2', 'msh22', 'msh3',
                                 'msh4', 'msh40', 'msh41', 'msh', 'unv', 'vtk',
                                 'wrl', 'mail', 'stl', 'p3d', 'mesh', 'bdf',
                                 'cgns', 'med', 'diff', 'ir3', 'inp', 'ply2',
                                 'celum', 'su2', 'x3d', 'dat', 'neu', 'm', 'key'])
    parser.add_argument('-l', '--log_path', help='log file path',
                        default=argparse.SUPPRESS)
    parser.add_argument('-v', '--log_level', default=argparse.SUPPRESS,
                        choices=['CRITICAL', 'FATAL', 'ERROR', 'WARNING',
                                 'WARN', 'INFO', 'DEBUG', 'NOTSET'])
    parser.add_argument('-g', '--factory', help='gmsh factory',
                        default=argparse.SUPPRESS, choices=['geo', 'occ'])
    parser.add_argument('-s', '--strategy', default=argparse.SUPPRESS,
                        choices=[x for x in FACTORY.str2obj
                                 if isinstance(x, str)
                                 and x.split('.')[0] == 'strategy'])
    cmd_args = vars(parser.parse_args())
    # Check input path
    result, path = check_on_file(cmd_args['input_path'])
    if result is None:
        raise FileNotFoundError(cmd_args['input_path'])
    # Update args from input file metadata
    with open(path) as f:
        data = json.load(f)
    args = data.get('metadata', {}).get('run', {})
    args.update(cmd_args)
    # Model name
    root, extension = os.path.splitext(args['input_path'])
    basename = os.path.basename(root)
    args['model_name'] = basename
    # Other
    args.setdefault('output_path', args['model_name'])
    args.setdefault('output_formats', ['geo_unrolled', 'msh2'])
    # args.setdefault('log_path', args['model_name'] + '.log')
    args.setdefault('log_path', None)
    args.setdefault('log_level', 'INFO')
    args.setdefault('factory', 'geo')
    args.setdefault('strategy', 'strategy.simple')
    args.setdefault('options', {})
    return args


def run(args):
    logging.info(f'args: {args}')
    block_tree = timeit(make_block_tree)(args['input_path'])
    logging.info(block_tree['blocks_children'])
    blocks = timeit(init_block_tree)(block_tree, args['input_path'])
    strategy = FACTORY(args['strategy'])
    strategy(factory=args['factory'],
             model_name=args['model_name'],
             output_path=args['output_path'],
             output_formats=args['output_formats'],
             block=blocks[0])


if __name__ == '__main__':
    args = parse_arguments()

    @LoggingDecorator(filename=args['log_path'], level=args['log_level'])
    @GmshDecorator()
    @GmshOptionsDecorator(options=args['options'])
    def pipeline(args):
        run(args)

    pipeline(args)

