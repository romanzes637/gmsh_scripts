import json
import os
import argparse
import logging
from pathlib import Path

from gmsh_scripts.load import load
from gmsh_scripts.support.support import LoggingDecorator, GmshDecorator, GmshOptionsDecorator
from gmsh_scripts.factory import FACTORY as FACTORY
from gmsh_scripts.factory import FactoryKeyError, FactoryValueError


def init_walk(obj, prev_obj=None, prev_indices=None, prev_keys=None):
    prev_indices = [[]] if prev_indices is None else prev_indices
    prev_keys = [] if prev_keys is None else prev_keys
    if isinstance(obj, dict):
        # Update object from previous object children fields
        if prev_obj is not None:
            for k, v in prev_obj.items():
                prev_index = prev_indices[-1]
                if all([k.startswith('children_'),
                        k != 'children_transforms',
                        prev_keys[-1] == 'children']):
                    obj_k = k[9:]
                    obj_v = v[prev_index[0]]
                    if obj_v is not None:
                        obj[obj_k] = obj_v
                elif all([k.startswith('items_children_'),
                          k != 'items_children_map',
                          k != 'items_children_transforms',
                          k != 'items_children_transforms_map',
                          prev_keys[-1] == 'items_children']):
                    prev_index = prev_indices[-1]
                    obj_k = k[15:]
                    obj_v = v[prev_index[0]][prev_index[1]]
                    if obj_v is not None:
                        obj[obj_k] = obj_v
        # Walk
        for k, v in obj.items():
            if k == 'class':
                continue
            if isinstance(v, dict):
                prev_keys.append(k)
                init_walk(v, obj, prev_indices, prev_keys)
                prev_keys.append(k)
            elif isinstance(v, list):
                prev_keys.append(k)
                init_walk(v, obj, prev_indices, prev_keys)
                prev_keys.append(k)
            elif isinstance(v, str) and v.startswith('/'):
                p = Path(v[1:]).resolve()
                v = load(p)['data']
                prev_keys.append(k)
                init_walk(v, obj, prev_indices, prev_keys)
                prev_keys.append(k)
                v['path'] = str(p)
            try:
                obj[k] = FACTORY(v)
            except FactoryValueError:
                pass
            except FactoryKeyError:
                pass
        # Remove children fields
        if obj is not None:
            for k in list(obj.keys()):
                if k.startswith('children_') and k != 'children_transforms':
                    obj.pop(k)
                if all([k.startswith('items_children_'),
                        k != 'items_children_map',
                        k != 'items_children_transforms',
                        k != 'items_children_transforms_map']):
                    obj.pop(k)
    elif isinstance(obj, list):
        prev_index = prev_indices[-1]
        for i, x in enumerate(obj):
            cur_index = prev_index + [i]
            if isinstance(x, dict):
                prev_indices.append(cur_index)
                prev_key = None if len(prev_keys) == 0 else prev_keys[-1]
                init_walk(x, prev_obj, prev_indices, prev_keys)
                if prev_key is not None:
                    prev_keys.append(prev_key)
                prev_indices.append(cur_index)
            elif isinstance(x, list):
                prev_indices.append(cur_index)
                init_walk(x, prev_obj, prev_indices, prev_keys)
                prev_indices.append(cur_index)
            elif isinstance(x, str) and x.startswith('/'):
                p = Path(x[1:]).resolve()
                x = load(p)['data']
                prev_indices.append(cur_index)
                prev_key = None if len(prev_keys) == 0 else prev_keys[-1]
                init_walk(x, prev_obj, prev_indices, prev_keys)
                if prev_key is not None:
                    prev_keys.append(prev_key)
                prev_indices.append(cur_index)
                x['path'] = str(p)
            try:
                obj[i] = FACTORY(x)
            except FactoryValueError:
                pass
            except FactoryKeyError:
                pass
        if len(prev_index) == 0:  # End of the list
            prev_indices.append([])


def set_parent(parent):
    children = parent.children
    for child in children:
        child.parent = parent
        set_parent(child)  # now child is a new parent


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
    cmd_args = vars(parser.parse_known_args()[0])
    # Check input path
    p = Path(cmd_args['input_path'])
    # Update args from input file metadata
    data = load(p)
    args = data.get('metadata', {}).get('run', {})
    args['data'] = data.get('data', {})
    args.update(cmd_args)
    # Model name
    root, extension = os.path.splitext(args['input_path'])
    basename = os.path.basename(root)
    args['model_name'] = basename
    # Other
    args.setdefault('output_path', args['model_name'])
    args.setdefault('output_formats', ['geo_unrolled', 'msh2'])
    args.setdefault('log_path', args['model_name'] + '.log')
    args.setdefault('log_path', None)
    args.setdefault('log_level', 'INFO')
    args.setdefault('factory', 'geo')
    args.setdefault('strategy', 'strategy.Base')
    args.setdefault('options', {})
    if isinstance(args['strategy'], str):
        args['strategy'] = {'class': args['strategy']}
    args['strategy'].setdefault("factory", args["factory"])
    args['strategy'].setdefault("model_name", args["model_name"])
    args['strategy'].setdefault("output_path", args["output_path"])
    args['strategy'].setdefault("output_formats", args["output_formats"])
    return args


def run(args):
    logging.info(f'args: {args}')
    # Initialize
    top_kwargs = args['data']
    init_walk(top_kwargs)
    top_kwargs['path'] = args['input_path']
    top_block = FACTORY(top_kwargs)
    set_parent(top_block)
    # Strategy
    init_walk(args['strategy'])
    strategy = FACTORY(args['strategy'])
    strategy(top_block)


def main():
    args = parse_arguments()

    @LoggingDecorator(filename=args['log_path'], level=args['log_level'])
    @GmshDecorator()
    @GmshOptionsDecorator(options=args['options'])
    def pipeline(args):
        run(args)

    pipeline(args)


if __name__ == '__main__':
    main()
