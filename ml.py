import json
import os
import argparse
import logging
from pathlib import Path

from src.support.support import check_on_file, LoggingDecorator
from src.factory import FACTORY as FACTORY
from src.factory import FactoryKeyError, FactoryValueError, FactoryClassError


def init_walk(u):
    if isinstance(u, dict):
        for k, v in u.items():
            if k == 'class':
                continue
            if isinstance(v, dict):
                init_walk(v)
            elif isinstance(v, list):
                init_walk(v)
            elif isinstance(v, str):
                if v.startswith('/'):
                    p = Path(v[1:]).resolve()
                    if p.exists() and p.suffix == '.json':
                        with open(p) as f:
                            d = json.load(f)
                        x = d['data']
                        init_walk(x)
            try:
                u[k] = FACTORY(v)
            except FactoryValueError:
                pass
            except FactoryKeyError:
                pass
            except FactoryClassError:
                pass
    elif isinstance(u, list):
        for i, x in enumerate(u):
            if isinstance(x, dict):
                init_walk(x)
            elif isinstance(x, list):
                init_walk(x)
            elif isinstance(x, str):
                if x.startswith('/'):
                    p = Path(x[1:]).resolve()
                    if p.exists() and p.suffix == '.json':
                        with open(p) as f:
                            d = json.load(f)
                        x = d['data']
                        init_walk(x)
            try:
                u[i] = FACTORY(x)
            except FactoryValueError:
                pass
            except FactoryKeyError:
                pass
            except FactoryClassError:
                pass


def parse_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument('input_path', help='input path')
    parser.add_argument('-l', '--log_path', help='log file path',
                        default=argparse.SUPPRESS)
    parser.add_argument('-v', '--log_level', default=argparse.SUPPRESS,
                        choices=['CRITICAL', 'FATAL', 'ERROR', 'WARNING',
                                 'WARN', 'INFO', 'DEBUG', 'NOTSET'])
    cmd_args = vars(parser.parse_args())
    # Check input path
    result, path = check_on_file(cmd_args['input_path'])
    if result is None:
        raise FileNotFoundError(cmd_args['input_path'])
    # Update args from input file metadata
    with open(path) as f:
        data = json.load(f)
    args = data.get('metadata', {}).get('ml', {})
    args['data'] = data.get('data', {})
    args.update(cmd_args)
    # Model name
    root, extension = os.path.splitext(args['input_path'])
    basename = os.path.basename(root)
    args['model_name'] = basename
    # Other
    args.setdefault('log_path', args['model_name'] + '.log')
    args.setdefault('log_level', 'INFO')
    return args


def run(args):
    logging.info(f'args: {args}')
    top_kwargs = args['data']
    init_walk(top_kwargs)
    top = FACTORY(top_kwargs)
    top()


if __name__ == '__main__':
    args = parse_arguments()

    @LoggingDecorator(filename=args['log_path'], level=args['log_level'])
    def pipeline(args):
        run(args)

    pipeline(args)
