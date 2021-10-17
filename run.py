import json
import os
import argparse
import socket
import sys
import time
import logging
import copy
import getpass
from pprint import pprint

import gmsh

import block

from support import boundary_surfaces_to_six_side_groups, \
    get_boundary_surfaces, check_file, \
    auto_complex_points_sizes_min_curve_in_volume, set_boundary_points_sizes, \
    auto_boundary_points_sizes_min_edge_in_surface, \
    set_points_sizes, get_interior_surfaces
from boolean import boolean, boolean_with_bounding_boxes
from zone import BlockSimple


block_factory = {
    'Block': block.Block
}


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
            real_path = check_file(block_path)['path']
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


def init_block_tree(block_tree, top_block_path, factory):
    def recurse(parent, parent_path, blocks):
        blocks.append(parent)
        children_paths = block_tree['blocks_children'].get(parent_path, [])
        for i, child_path in enumerate(children_paths):
            child_kwargs = copy.deepcopy(block_tree['blocks_kwargs'][child_path])
            child_class_name = child_kwargs['metadata']['class']
            child_kwargs['data']['factory'] = factory
            child_kwargs['data']['parent'] = parent
            child_kwargs['data']['file_name'] = child_path
            child = block_factory[child_class_name](**child_kwargs['data'])
            parent.children[i] = child
            recurse(child, child_path, blocks)  # now child is a new parent

    blocks = []
    parent_path = top_block_path
    parent_kwargs = copy.deepcopy(block_tree['blocks_kwargs'][parent_path])
    parent_kwargs['data']['factory'] = factory
    parent_class_name = parent_kwargs['metadata']['class']
    parent_kwargs['data']['file_name'] = parent_path
    parent = block_factory[parent_class_name](**parent_kwargs['data'])
    recurse(parent, parent_path, blocks)
    return blocks


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('config', help='config file', nargs='?')
    parser.add_argument('-i', '--input_path', help='input filename',
                        default='input/test_block.json')
    parser.add_argument('-o', '--output_path', help='output filename',
                        default='test_block.geo_unrolled')
    parser.add_argument('-l', '--log_path', help='log filename')
    parser.add_argument('-L', '--log_level', default='INFO',
                        choices=logging._nameToLevel.keys())
    parser.add_argument('-T', '--test', help='test mode', action='store_true')
    parser.add_argument('-r', '--recombine', help='recombine',
                        action='store_true')
    parser.add_argument('-b', '--boolean', help='boolean', default=None,
                        choices=['without-bboxes', 'with-bboxes'])
    parser.add_argument('-B', '--boundary_type',
                        help='boundary type: 6, primitive, all, '
                             'path_to_file_with_surfaces_map',
                        default='primitive')
    parser.add_argument('-s', '--auto_size', type=float, metavar=1.0,
                        help='mesh auto size factor', default=None,
                        nargs='?', const=1.0)
    parser.add_argument('-S', '--size', type=float, metavar=5.0,
                        help='points mesh size', default=None)
    parser.add_argument('-z', '--boundary_auto_size', type=float, metavar=1.0,
                        help='boundary mesh auto size factor',
                        default=None, nargs='?', const=1.0)
    parser.add_argument('-Z', '--boundary_size', type=float, metavar=10.0,
                        help='boundary points mesh size',
                        default=None)
    parser.add_argument('-O', '--optimize',
                        help='optimize mesh after generation',
                        action='store_true')
    parser.add_argument('-m', '--mesh_algorithm', type=int, default=1,
                        help='gmsh 3D mesh algorithm: 1: Delaunay, 4: Frontal, '
                             '7: MMG3D, 9: R-tree, 10: HXT')
    parser.add_argument('-M', '--mesh_algorithm_2d', type=int, default=6,
                        help='gmsh 2D mesh algorithm: 1: MeshAdapt,'
                             '2: Automatic, 5: Delaunay, 6: Frontal-Delaunay,'
                             '7: BAMG, 8: Frontal-Delaunay for Quads,'
                             '9: Packing of Parallelograms')
    parser.add_argument('-I', '--in_surfaces', help='make inner surfaces',
                        action='store_true')
    parser.add_argument('-t', '--transfinite', help='transfinite surfaces',
                        action='store_true')
    parser.add_argument('-f', '--factory', help='gmsh factory',
                        default=None, choices=['geo', 'occ'])
    cmd_args = vars(parser.parse_args())
    args = copy.deepcopy(cmd_args)
    config_args = None
    if cmd_args['config'] is not None:
        result = check_file(cmd_args['config'])
        with open(result['path']) as f:
            data = json.load(f)
        config_args = data['arguments']
        args.update(config_args)
    root, extension = os.path.splitext(args['input_path'])
    basename = os.path.basename(root)
    # Test mode
    if not args['test']:
        if args['output_path'] is None:
            args['output_path'] = basename + '.msh2'
    else:
        args['output_path'] = basename + '.brep'
    # Explicit boundaries
    if args['boundary_type'] not in ['6', 'primitive', 'all']:
        result = check_file(args['boundary_type'])
        with open(result['path']) as f:
            physical_surfaces_input = json.load(f)
        physical_surfaces_map = physical_surfaces_input['arguments']
    # Logging
    if args['log_path'] is None:
        args['log_path'] = basename + '.log'
    log_level_int = logging._nameToLevel[args['log_level']]
    tz = time.strftime('%z')
    user = getpass.getuser()
    hostname = socket.gethostname()
    ip = socket.gethostbyname(hostname)
    logging.basicConfig(
        filename=args['log_path'],
        filemode='a',
        format='%(asctime)s.%(msecs)03d' + tz + f'|{hostname}|{ip}|{user}' +
               '|%(process)d|%(levelname)s|%(filename)s|%(lineno)d|%(message)s',
        datefmt='%Y-%m-%dT%H:%M:%S',
        level=log_level_int)
    # Log
    logging.info(f'hostname: {socket.gethostname()}')
    logging.info(f'ip: {socket.gethostbyname(socket.gethostname())}')
    logging.info(f'user: {getpass.getuser()}')
    logging.info(f'pid: {os.getpid()}')
    logging.info(f'python: {sys.executable}')
    logging.info(f'script: {__file__}')
    logging.info(f'working directory: {os.getcwd()}')
    logging.info(f'cmd args: {cmd_args}')
    logging.info(f'config args: {config_args}')
    logging.info(f'args: {args}')
    logging.info('gmsh')
    t00 = time.perf_counter()
    t0 = time.perf_counter()
    gmsh.initialize()
    if args['log_level'] == "NOTSET":
        gmsh.option.setNumber("General.Terminal", 1)
    else:
        gmsh.option.setNumber("General.Terminal", 0)
    gmsh.option.setNumber('Geometry.AutoCoherence', 0)  # No effect at occ
    gmsh.option.setNumber('Mesh.Optimize', 0)  # resolving further
    gmsh.option.setNumber('Mesh.Algorithm', args['mesh_algorithm_2d'])
    gmsh.option.setNumber('Mesh.Algorithm3D', args['mesh_algorithm'])
    model_name = basename
    gmsh.model.add(model_name)
    logging.info(f'gmsh: {time.perf_counter() - t0:.3f}s')
    t0 = time.perf_counter()
    top_block_path = args['input_path']
    block_tree = make_block_tree(top_block_path)
    logging.info(f'Tree: {time.perf_counter() - t0:.3f}s')
    t0 = time.perf_counter()
    top_block_kwargs = block_tree['blocks_kwargs'][top_block_path]
    pprint(block_tree['blocks_children'])
    if args['factory'] is not None:
        factory = args['factory']
        top_block_kwargs['data']['factory'] = factory
    else:
        factory = top_block_kwargs['data']['factory']
    blocks = init_block_tree(block_tree=block_tree,
                             top_block_path=top_block_path,
                             factory=factory)
    top_block = blocks[0]
    t0 = time.perf_counter()
    top_block.plot_tree(file_name=model_name, label_type='volume_zone',
                        group_type='file_name', title_type='type')
    logging.info(f'Tree: {time.perf_counter() - t0:.3f}s')
    logging.info(f'Initialize: {time.perf_counter() - t0:.3f}s')
    t0 = time.perf_counter()
    top_block.transform()
    logging.info(f'Transform: {time.perf_counter() - t0:.3f}s')
    t0 = time.perf_counter()
    top_block.register()
    logging.info(f'Register: {time.perf_counter() - t0:.3f}s')
    if factory == 'geo':
        t0 = time.perf_counter()
        top_block.quadrate()
        logging.info(f'Recombine: {time.perf_counter() - t0:.3f}s')
        t0 = time.perf_counter()
        top_block.structure()
        logging.info(f'Transfinite: {time.perf_counter() - t0:.3f}s')
    if factory == 'occ':
        if args['boolean'] is not None:
            for b in blocks:  # TODO Do it or not?
                if b.boolean_level is None:
                    b.boolean_level = 0
            t0 = time.perf_counter()
            if args['boolean'] == 'without-bboxes':
                boolean(top_block)
            elif args['boolean'] == 'with-bboxes':
                gmsh.model.occ.synchronize()  # for evaluation of bboxes
                boolean_with_bounding_boxes(top_block)
            gmsh.model.occ.removeAllDuplicates()
            logging.info(f'Boolean: {time.perf_counter() - t0:.3f}s')
    t0 = time.perf_counter()
    if factory == 'geo':
        gmsh.model.geo.synchronize()
    elif factory == 'occ':
        gmsh.model.occ.synchronize()
    else:
        raise ValueError(factory)
    logging.info(f'Synchronize: {time.perf_counter() - t0:.3f}s')
    if factory == 'occ':
        t0 = time.perf_counter()
        top_block.quadrate()
        logging.info(f'Recombine: {time.perf_counter() - t0:.3f}s')
        t0 = time.perf_counter()
        top_block.structure()
        logging.info(f'Transfinite: {time.perf_counter() - t0:.3f}s')
    t0 = time.perf_counter()
    if args['boolean'] is None:
        t0 = time.perf_counter()
        z2tg = BlockSimple()(top_block)
        for zone, tags in z2tg.items():
            dims, tags = [x[0] for x in tags], [x[1] for x in tags]
            dim = dims[0]
            tag = gmsh.model.addPhysicalGroup(dim, tags)
            gmsh.model.setPhysicalName(dim, tag, zone)
    else:
        pass
    logging.info(f'zones: {time.perf_counter() - t0}')
    t0 = time.perf_counter()
    gmsh.model.mesh.generate(3)
    logging.info(f'Mesh: {time.perf_counter() - t0:.3f}s')
    t0 = time.perf_counter()
    gmsh.write(args['output_path'])
    logging.info(f'Write: {time.perf_counter() - t0:.3f}s')
    gmsh.finalize()

    # if not args['test']:
    # if args['boolean']:
    #     if input_data['arguments']['factory'] != 'occ':
    #         logging.critical('Boolean is only available in the occ factory!')
    #         raise ValueError('Boolean is only available in the occ factory!')
    #     logging.info('Bounding Box')  # for boolean speedup
    #     t0 = time.perf_counter()
    #     c.evaluate_bounding_box()
    #     logging.info(f'Bounding Box: {time.perf_counter() - t0:.3f}s')
    #     logging.info("Boolean")
    #     t0 = time.perf_counter()
    #     complex_self(factory, c)
    #     logging.info(f'Boolean: {time.perf_counter() - t0:.3f}s')
    #     logging.info('Synchronize')
    #     t0 = time.perf_counter()
    #     factory.synchronize()
    #     logging.info(f'Synchronize: {time.perf_counter() - t0:.3f}s')
    # if args['transfinite']:
    #     logging.info('Transfinite')
    #     t0 = time.perf_counter()
    #     ss, cs = set(), set()  # surfaces, curves
    #     c.transfinite(ss, cs)
    #     logging.info(f'Transfinite: {time.perf_counter() - t0:.3f}s')
    # if args['recombine']:
    #     logging.info('Recombine')
    #     t0 = time.perf_counter()
    #     c.recombine()
    #     logging.info(f'Recombine: {time.perf_counter() - t0:.3f}s')
    # if args['auto_size'] is not None:
    #     logging.info('Auto Size: {}'.format(args['auto_size']))
    #     t0 = time.perf_counter()
    #     pss = dict()
    #     auto_complex_points_sizes_min_curve_in_volume(c, pss,
    #                                                   args['auto_size'])
    #     logging.info(f'Auto Size: {time.perf_counter() - t0:.3f}s')
    # if args['size'] is not None:
    #     logging.info('Set Size: {}'.format(args['size']))
    #     t0 = time.perf_counter()
    #     set_points_sizes(args['size'])
    #     logging.info(f'Set Size {time.perf_counter() - t0:.3f}s')
    # if args['boundary_auto_size'] is not None:
    #     logging.info('Boundary Auto Size: {}'.format(args['boundary_auto_size']))
    #     t0 = time.perf_counter()
    #     auto_boundary_points_sizes_min_edge_in_surface(
    #         args['boundary_auto_size'])
    #     logging.info(f'Boundary Auto Size {time.perf_counter() - t0:.3f}s')
    # if args['boundary_size'] is not None:
    #     logging.info('Set Boundary Size: {}'.format(args['boundary_size']))
    #     t0 = time.perf_counter()
    #     set_boundary_points_sizes(args['boundary_size'])
    #     logging.info(f'Set Boundary Size: {time.perf_counter() - t0:.3f}s')
    # logging.info("Volumes")
    # t0 = time.perf_counter()
    # ns_to_vs = c.get_map_names_to_volumes()
    # for n, vs in ns_to_vs.items():
    #     tag = gmsh.model.addPhysicalGroup(3, vs)
    #     gmsh.model.setPhysicalName(3, tag, n)
    # vs_to_e = c.get_map_vol_to_exists()
    # to_remove = [(3, x) for x, y in vs_to_e.items() if not y]
    # gmsh.model.removeEntities(to_remove, recursive=False)
    # logging.info(f'Volumes: {time.perf_counter() - t0:.3f}s')
    # logging.info("Surfaces")
    # t0 = time.perf_counter()
    # if args['boundary_type'] == '6':
    #     logging.info("by 6 surfaces")
    #     boundary_surfaces_groups = boundary_surfaces_to_six_side_groups()
    #     for n, ss in boundary_surfaces_groups.items():
    #         tag = gmsh.model.addPhysicalGroup(2, ss)
    #         gmsh.model.setPhysicalName(2, tag, n)
    # elif args['boundary_type'] == 'primitive':
    #     logging.info("by primitives surfaces")
    #     n2s = dict()  # surface name to surface global index
    #     s2psi = c.get_map_surface_to_primitives_surfaces_indices()
    #     bs = get_boundary_surfaces()
    #     for s in bs:
    #         sn = None
    #         psi = s2psi.get(s, [])  # [(primitive, surf local index)]
    #         if len(psi) != 0:
    #             pi, si = psi[0]  # from first primitive
    #             sn = c.primitives[pi].surfaces_names[si]
    #         else:  # After boolean
    #             sn = 'S'
    #         n2s.setdefault(sn, []).append(s)
    #     for n, ss in n2s.items():
    #         tag = gmsh.model.addPhysicalGroup(2, ss)
    #         gmsh.model.setPhysicalName(2, tag, n)
    # elif args['boundary_type'] == 'all':
    #     logging.info("by all surfaces")
    #     boundary_surfaces = get_boundary_surfaces()
    #     for i, s in enumerate(boundary_surfaces):
    #         name = 'S{0}'.format(s)
    #         tag = gmsh.model.addPhysicalGroup(2, [s])
    #         gmsh.model.setPhysicalName(2, tag, name)
    # else:
    #     logging.info("by surfaces map")
    #     for name, surfaces in physical_surfaces_map.items():
    #         tag = gmsh.model.addPhysicalGroup(2, surfaces)
    #         gmsh.model.setPhysicalName(2, tag, name)
    # logging.info(f'Surfaces: {time.perf_counter() - t0:.3f}s')
    # if args['in_surfaces']:
    #     t0 = time.perf_counter()
    #     logging.info('Inner Surfaces')
    #     n2s = {}  # surface name to surface global index
    #     if 's2psi' not in locals():  # s2i not exists
    #         s2psi = c.get_map_surface_to_primitives_surfaces_indices()
    #     in_surfaces = get_interior_surfaces()
    #     for s in in_surfaces:
    #         sn = None
    #         psi = s2psi.get(s, [])
    #         if len(psi) != 0:
    #             for pi, si in psi:
    #                 mask = c.primitives[pi].in_surf_mask
    #                 if not mask[si]:
    #                     sn = c.primitives[pi].in_surfaces_names[si]
    #                     break
    #         else:  # After boolean or masked
    #             sn = 'SI'
    #         if sn is not None:
    #             n2s.setdefault(sn, []).append(s)
    #     for n, ss in n2s.items():
    #         tag = gmsh.model.addPhysicalGroup(2, ss)
    #         gmsh.model.setPhysicalName(2, tag, n)
    #     logging.info(f'Inner Surfaces: {time.perf_counter() - t0:.3f}s')
    # logging.info("Mesh")
    # t0 = time.perf_counter()
    # gmsh.model.mesh.generate(3)
    # logging.info(f'Mesh: {time.perf_counter() - t0:.3f}s')
    # logging.info(f'nodes: {len(gmsh.model.mesh.getNodes()[0])}')
    # if args['optimize']:
    #     logging.info("Optimize")
    #     t0 = time.perf_counter()
    #     gmsh.model.mesh.optimize('', True)
    #     logging.info(f'Optimize: {time.perf_counter() - t0:.3f}s')
    # logging.info("Write: {}".format(args['output_path']))
    # t0 = time.perf_counter()
    # gmsh.write(args['output_path'])
    # logging.info(f'Write: {time.perf_counter() - t0:.3f}s')
    # gmsh.finalize()
    # logging.info(f'Time spent: {time.perf_counter() - t00:.3f}s')
