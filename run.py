import json
import os
import argparse
import logging

from support import check_on_file, LoggingDecorator, GmshDecorator, GmshOptionsDecorator
from factory import FACTORY as FACTORY


def init_walk(obj):
    if isinstance(obj, dict):
        for k, v in obj.items():
            if k == 'class':
                continue
            if isinstance(v, dict):
                init_walk(v)
            elif isinstance(v, list):
                init_walk(v)
            elif isinstance(v, str):
                result, real_path = check_on_file(v)
                if real_path is not None:
                    with open(real_path) as f:
                        v = json.load(f)['data']
                    init_walk(v)
                    v['path'] = real_path
            try:
                obj[k] = FACTORY(v)
            except ValueError as e:  # Bad v
                pass
            except KeyError as e:  # Bad k
                pass
    elif isinstance(obj, list):
        for i, x in enumerate(obj):
            if isinstance(x, dict):
                init_walk(x)
            elif isinstance(x, list):
                init_walk(x)
            elif isinstance(x, str):
                result, real_path = check_on_file(x)
                if real_path is not None:
                    with open(real_path) as f:
                        x = json.load(f)['data']
                    init_walk(x)
                    x['path'] = real_path
            try:
                obj[i] = FACTORY(x)
            except ValueError as e:  # Bad v
                pass
            except KeyError as e:  # Bad x
                pass


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
    cmd_args = vars(parser.parse_args())
    # Check input path
    result, path = check_on_file(cmd_args['input_path'])
    if result is None:
        raise FileNotFoundError(cmd_args['input_path'])
    # Update args from input file metadata
    with open(path) as f:
        data = json.load(f)
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
    # args.setdefault('log_path', args['model_name'] + '.log')
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


if __name__ == '__main__':
    args = parse_arguments()

    @LoggingDecorator(filename=args['log_path'], level=args['log_level'])
    @GmshDecorator()
    @GmshOptionsDecorator(options=args['options'])
    def pipeline(args):
        run(args)

    pipeline(args)

