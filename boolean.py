"""Boolean operations on blocks

There are 3 entities after boolean operation on blocks B0 and B1:
1. Residual part of B0
2. Residual part of B1
3. Intersection of B0 and B1

After boolean intersection (3) could be moved to B0 (1) or B1 (2) or their union B0-B1 (1-2) or be removed (4 options).

Each residual could be removed (2 options).

There are 2*2*4 = 16 combinations of options that are represented in the table.

Table. Options and corresponding actions

+----+---------+-------------------+---------+---------------------------------------------------+
| n  | Block 0 | Block 0 & Block 1 | Block 1 |                      Actions                      |
+====+=========+===================+=========+===================================================+
|    |         |                   |         |                                                   |
|    |         |                   |         |                                                   |
| 1  |         |                   |         | B0.do_unregister         B1.do_unregister         |
|    |         |                   |         |                                                   |
|    |         |                   |         | B0.do_unregister_boolean B1.do_unregister_boolean |
+----+---------+-------------------+---------+---------------------------------------------------+
|    |         |                   |         |                                                   |
|    |         |                   |         |                                                   |
| 2  |   B0    |                   |         |                          B1.do_unregister         |
|    |         |                   |         |                                                   |
|    |         |                   |         | B0.do_unregister_boolean B1.do_unregister_boolean |
+----+---------+-------------------+---------+---------------------------------------------------+
|    |         |                   |         |                                                   |
|    |         |                   |         |                                                   |
| 3  |         |                   |    B1   | B0.do_unregister                                  |
|    |         |                   |         |                                                   |
|    |         |                   |         | B0.do_unregister_boolean B1.do_unregister_boolean |
+----+---------+-------------------+---------+---------------------------------------------------+
|    |         |                   |         |                                                   |
|    |         |                   |         |                                                   |
| 4  |   B0    |                   |   B1    |                                                   |
|    |         |                   |         |                                                   |
|    |         |                   |         | B0.do_unregister_boolean B1.do_unregister_boolean |
+----+---------+-------------------+---------+---------------------------------------------------+
|    |         |                   |         | B0.boolean_level   ==    B1.boolean_level         |
|    |         |                   |         |                                                   |
| 5  |         |       B0-B1       |         | B0.do_unregister         B1.do_unregister         |
|    |         |                   |         |                                                   |
|    |         |                   |         |                                                   |
+----+---------+-------------------+---------+---------------------------------------------------+
|    |         |                   |         | B0.boolean_level    >    B1.boolean_level         |
|    |         |                   |         |                                                   |
| 6  |         |        B0         |         | B0.do_unregister         B1.do_unregister         |
|    |         |                   |         |                                                   |
|    |         |                   |         |                                                   |
+----+---------+-------------------+---------+---------------------------------------------------+
|    |         |                   |         | B0.boolean_level    <    B1.boolean_level         |
|    |         |                   |         |                                                   |
| 7  |         |        B1         |         | B0.do_unregister         B1.do_unregister         |
|    |         |                   |         |                                                   |
|    |         |                   |         |                                                   |
+----+---------+-------------------+---------+---------------------------------------------------+
|    |         |                   |         | B0.boolean_level   ==    B1.boolean_level         |
|    |         |                   |         |                                                   |
| 8  |   B0    |       B0-B1       |         |                          B1.do_unregister         |
|    |         |                   |         |                                                   |
|    |         |                   |         |                                                   |
+----+---------+-------------------+---------+---------------------------------------------------+
|    |         |                   |         | B0.boolean_level   >     B1.boolean_level         |
|    |         |                   |         |                                                   |
| 9  |   B0    |        B0         |         |                          B1.do_unregister         |
|    |         |                   |         |                                                   |
|    |         |                   |         |                                                   |
+----+---------+-------------------+---------+---------------------------------------------------+
|    |         |                   |         | B0.boolean_level   <     B1.boolean_level         |
|    |         |                   |         |                                                   |
| 10 |   B0    |        B1         |         |                          B1.do_unregister         |
|    |         |                   |         |                                                   |
|    |         |                   |         |                                                   |
+----+---------+-------------------+---------+---------------------------------------------------+
|    |         |                   |         | B0.boolean_level   ==    B1.boolean_level         |
|    |         |                   |         |                                                   |
| 11 |         |       B0-B1       |   B1    | B0.do_unregister                                  |
|    |         |                   |         |                                                   |
|    |         |                   |         |                                                   |
+----+---------+-------------------+---------+---------------------------------------------------+
|    |         |                   |         | B0.boolean_level   >     B1.boolean_level         |
|    |         |                   |         |                                                   |
| 12 |         |        B0         |   B1    | B0.do_unregister                                  |
|    |         |                   |         |                                                   |
|    |         |                   |         |                                                   |
+----+---------+-------------------+---------+---------------------------------------------------+
|    |         |                   |         | B0.boolean_level   <     B1.boolean_level         |
|    |         |                   |         |                                                   |
| 13 |         |        B1         |   B1    | B0.do_unregister                                  |
|    |         |                   |         |                                                   |
|    |         |                   |         |                                                   |
+----+---------+-------------------+---------+---------------------------------------------------+
|    |         |                   |         | B0.boolean_level   ==    B1.boolean_level         |
|    |         |                   |         |                                                   |
| 14 |   B0    |       B0-B1       |   B1    |                                                   |
|    |         |                   |         |                                                   |
|    |         |                   |         |                                                   |
+----+---------+-------------------+---------+---------------------------------------------------+
|    |         |                   |         | B0.boolean_level    >    B1.boolean_level         |
|    |         |                   |         |                                                   |
| 15 |   B0    |        B0         |   B1    |                                                   |
|    |         |                   |         |                                                   |
|    |         |                   |         |                                                   |
+----+---------+-------------------+---------+---------------------------------------------------+
|    |         |                   |         | B0.boolean_level    <    B1.boolean_level         |
|    |         |                   |         |                                                   |
| 16 |   B0    |        B1         |   B1    |                                                   |
|    |         |                   |         |                                                   |
|    |         |                   |         |                                                   |
+----+---------+-------------------+---------+---------------------------------------------------+
"""
import itertools
import logging

import gmsh
import numpy as np

from volume import Volume
from support import timeit


def boolean(block):
    n_blocks = 0
    for _ in block:
        n_blocks += 1
    logging.info(f'n_blocks: {n_blocks}')
    n_combinations = int(0.5 * (n_blocks * n_blocks - n_blocks))
    logging.info(f'n_combinations: {n_combinations}')
    cnt = 0
    for b0, b1 in itertools.combinations(block, 2):
        cnt += 1
        logging.info(f'{cnt}/{n_combinations}')
        timeit(block_by_block)(b0, b1)


def boolean_with_bounding_boxes(block):
    """Do boolean if there is bounding boxes intersection

    Bounding box [min_x, min_y, min_z, max_x, max_y, max_z]

    Args:
        block:

    Returns:
        None
    """

    def get_bb(b):
        if b.is_registered:
            bbs = np.array([gmsh.model.getBoundingBox(3, x.tag) for x in b.volumes])
            bb = np.concatenate([bbs[:, :3].min(axis=0), bbs[:, 3:].max(axis=0)])
        else:
            bb = np.array([-np.inf, -np.inf, -np.inf, np.inf, np.inf, np.inf])
        return bb

    b2bb = {}
    n_blocks = 0
    for b in block:
        b2bb[b] = get_bb(b)
        n_blocks += 1
    logging.info(f'n_blocks: {n_blocks}')
    n_combinations = int(0.5 * (n_blocks * n_blocks - n_blocks))
    logging.info(f'n_combinations: {n_combinations}')
    cnt = 0
    for b0, b1 in itertools.combinations(block, 2):
        cnt += 1
        logging.info(f'{cnt}/{n_combinations}')
        bb0 = b2bb[b0]
        bb1 = b2bb[b1]
        # Check bbox intersection
        do_boolean = True
        # for x, y, z: min > max, max < min
        if any((bb0[0] > bb1[3], bb0[3] < bb1[0], bb0[1] > bb1[4],
                bb0[1] > bb1[4], bb0[2] > bb1[5], bb0[2] > bb1[5])):
            do_boolean = False
        logging.info(f'bbox intersection: {do_boolean}')
        # Do boolean operation
        if do_boolean:
            timeit(block_by_block)(b0, b1)


def block_by_block(b0, b1, zone_separator='-'):
    if not b0.is_registered or not b1.is_registered:
        return
    if b0.boolean_level is None or b1.boolean_level is None:
        return
    if len(b0.volumes) == 0 or len(b1.volumes) == 0:
        return
    logging.info(f'b0 {id(b0)} - {b0.boolean_level} level, '
                 f'{" ".join(sorted(set([x for x in b0.volumes_zones])))} zones, '
                 f'{len(b0.volumes)} volumes and '
                 f'b1 {id(b1)} - {b1.boolean_level} level, '
                 f'{" ".join(sorted(set([x for x in b1.volumes_zones])))} zones, '
                 f'{len(b1.volumes)} volumes')
    # Boolean operation
    obj_dts = [(3, x.tag) for x in b0.volumes]
    tool_dts = [(3, x.tag) for x in b1.volumes]
    new_dts, old_id_to_new_dts = timeit(gmsh.model.occ.fragment)(
        objectDimTags=obj_dts, toolDimTags=tool_dts)
    # New dim-tag to old indices map
    new_dt_to_old_ids = {}
    for old_id, dts in enumerate(old_id_to_new_dts):
        for dt in dts:
            new_dt_to_old_ids.setdefault(dt, []).append(old_id)
    # logging.info(new_dts)
    # logging.info(old_id_to_new_dts)
    # logging.info(new_dt_to_old_ids)
    # New volumes
    # new_obj_vs = old_to_new[:len(obj_vs)]  # dim, tag
    # new_tool_vs = old_to_new[len(obj_vs):]  # dim, tag
    # Set is_booleaned flag
    # if not obj.is_booleaned:
    #     obj.is_booleaned = True
    #     if len(obj_vs) == 1 and len(new_obj_vs[0]) == 1:
    #         old_tag, new_tag = obj_vs[0][1], new_obj_vs[0][0][1]
    #         if old_tag == new_tag and is_cuboid(new_tag):
    #             if is_compatible(obj, new_tag):
    #                 obj.is_booleaned = False
    # if not tool.is_booleaned:
    #     tool.is_booleaned = True
    #     if len(tool_vs) == 1 and len(new_tool_vs[0]) == 1:
    #         old_tag, new_tag = tool_vs[0][1], new_tool_vs[0][0][1]
    #         if old_tag == new_tag and is_cuboid(new_tag):
    #             if is_compatible(tool, new_tag):
    #                 tool.is_booleaned = False
    # Update object volumes
    new_b0_volumes, new_b1_volumes = [], []
    for new_dt, old_is in new_dt_to_old_ids.items():
        new_tag = new_dt[1]
        if len(old_is) == 1:  # Non intersected volume (Update tag only)
            old_i = old_is[0]
            if old_i < len(b0.volumes):  # Update b0 volume
                old_v = b0.volumes[old_i]
                old_v.tag = new_tag
                new_b0_volumes.append(old_v)
            else:  # Update b1 volume
                old_v = b1.volumes[old_i - len(b0.volumes)]
                old_v.tag = new_tag
                new_b1_volumes.append(old_v)
        else:  # Intersected volume
            if b1.boolean_level > b0.boolean_level:  # Add volume to b1
                new_v = Volume(tag=new_tag, zone=b1.volumes_zones[0])  # TODO Other fields?
                new_b1_volumes.append(new_v)
            elif b0.boolean_level > b1.boolean_level:  # Add volume to b0
                new_v = Volume(tag=new_tag, zone=b0.volumes_zones[0])  # TODO Other fields?
                new_b0_volumes.append(new_v)
            else:  # No tool and object (TODO ADD volume to b1?)
                zones = set(x for x in [b0.volumes_zones[0], b1.volumes_zones[0]] if x is not None)
                new_zone = zone_separator.join(sorted(zones)) if len(zones) > 0 else zones
                new_v = Volume(tag=new_tag, zone=new_zone)  # TODO Other fields?
                new_b1_volumes.append(new_v)
    b0.volumes = new_b0_volumes
    b1.volumes = new_b1_volumes


def is_cuboid(volume):
    if volume is None:
        return False
    surfaces = gmsh.model.getBoundary([(3, volume)])
    if len(surfaces) != 6:
        return False
    for s in surfaces:
        edges = gmsh.model.getBoundary([s])
        if len(edges) != 4:
            return False
    return True


def is_compatible(block, tag):
    # Surfaces
    ss = [x[1] for x in gmsh.model.getBoundary([(3, tag)])]
    old_ss = [x.tag for x in block.surfaces]
    if len(ss) != len(old_ss) and set(ss) != set(old_ss):
        return False
    # Edges
    old_edges = [x.tag for x in block.curves]
    es = set()
    for s in ss:
        edges = [x[1] for x in gmsh.model.getBoundary([(2, s)], oriented=False)]
        es.update(edges)
    if len(es) != len(old_edges) and es != set(old_edges):
        return False
    # Points
    old_ps = [x.tag for x in block.points]
    ps = [x[1] for x in gmsh.model.getBoundary([(3, tag)], recursive=True)]
    if len(ps) != len(old_ps) and set(ps) != set(old_ps):
        return False
    # Ok
    return True

# def structure_cuboid(volume, structured_surfaces, structured_edges,
#                      min_edge_nodes, c=1.0):
#     volume_dt = (3, volume)
#     surfaces_dts = gmsh.model.getBoundary([volume_dt])
#     surfaces_edges = dict()
#     surfaces_points = dict()
#     edges = set()
#     for surface_dt in surfaces_dts:
#         edges_dts = gmsh.model.getBoundary([surface_dt],
#                                            combined=False)  # Save order
#         surface = surface_dt[1]
#         surfaces_edges[surface] = list()
#         surfaces_points[surface] = list()
#         for edge_dt in edges_dts:
#             edge = abs(edge_dt[1])
#             surfaces_edges[surface].append(edge)
#             edges.add(edge)
#             points_dts = gmsh.model.getBoundary([edge_dt],
#                                                 combined=False)  # Save order
#             p0 = points_dts[0][1]
#             p1 = points_dts[1][1]
#             if p0 not in surfaces_points[surface]:
#                 surfaces_points[surface].append(p0)
#             if p1 not in surfaces_points[surface]:
#                 surfaces_points[surface].append(p1)
#     # pprint(surfaces_points)
#     min_point = min(min(x) for x in surfaces_points.values())
#     first_point = min_point
#     diagonal_surfaces = list()
#     for k, v in surfaces_points.items():
#         if first_point not in v:
#             diagonal_surfaces.append(k)
#     diagonal_point = None
#     diagonal_point_set = set()
#     for s in diagonal_surfaces:
#         diagonal_point_set.update(set(surfaces_points[s]))
#     for s in diagonal_surfaces:
#         diagonal_point_set.intersection_update(set(surfaces_points[s]))
#     for p in diagonal_point_set:
#         diagonal_point = p
#     circular_permutations = {
#         0: [0, 1, 2, 3],
#         1: [3, 0, 1, 2],
#         2: [2, 3, 0, 1],
#         3: [1, 2, 3, 0]
#     }
#     for k, v in surfaces_points.items():
#         if first_point in v:
#             point = first_point
#         else:
#             point = diagonal_point
#         for p in circular_permutations.values():
#             new_v = [v[x] for x in p]
#             if new_v[0] == point:
#                 surfaces_points[k] = new_v
#                 break
#     # pprint(surfaces_points)
#     edges_groups = dict()
#     groups_edges = dict()
#     for i in range(3):
#         groups_edges[i] = list()
#         start_edge = None
#         for e in edges:
#             if e not in edges_groups:
#                 start_edge = e
#                 break
#         edges_groups[start_edge] = i
#         groups_edges[i].append(start_edge)
#         start_edge_surfaces = list()
#         for k, v in surfaces_edges.items():
#             if start_edge in v:
#                 start_edge_surfaces.append(k)
#         get_opposite_edge_index = {
#             0: 2,
#             1: 3,
#             2: 0,
#             3: 1
#         }
#         opposite_edge = None
#         for s in start_edge_surfaces:
#             surface_edges = surfaces_edges[s]
#             start_edge_index = surface_edges.index(start_edge)
#             opposite_edge_index = get_opposite_edge_index[start_edge_index]
#             opposite_edge = surface_edges[opposite_edge_index]
#             edges_groups[opposite_edge] = i
#             groups_edges[i].append(opposite_edge)
#         for k, v in surfaces_edges.items():
#             if k not in start_edge_surfaces:
#                 if opposite_edge in v:
#                     last_opposite_edge_index = v.index(opposite_edge)
#                     diagonal_edge_index = get_opposite_edge_index[
#                         last_opposite_edge_index]
#                     diagonal_edge = v[diagonal_edge_index]
#                     edges_groups[diagonal_edge] = i
#                     groups_edges[i].append(diagonal_edge)
#                     break
#     # pprint(edges_groups)
#     # pprint(groups_edges)
#     edges_lengths = get_volume_edges_lengths(volume)
#     groups_min_lengths = dict()
#     for group, edges in groups_edges.items():
#         lengths = [edges_lengths[x] for x in edges]
#         groups_min_lengths[group] = min(lengths)
#     # pprint(groups_min_lengths)
#     min_length = min(groups_min_lengths.values())
#     # number of nodes
#     groups_n_nodes = dict()
#     for group, length in groups_min_lengths.items():
#         a = max(c * length / min_length, 1)
#         n_nodes = int(min_edge_nodes * a)
#         groups_n_nodes[group] = n_nodes
#     # correct number of nodes from already structured edges
#     for edge, group in edges_groups.items():
#         if edge in structured_edges:
#             groups_n_nodes[group] = structured_edges[edge]
#     # pprint(groups_n_nodes)
#     # Structure
#     for edge, group in edges_groups.items():
#         if edge not in structured_edges:
#             n_nodes = groups_n_nodes[group]
#             gmsh.model.mesh.setTransfiniteCurve(edge, n_nodes, "Progression", 1)
#             structured_edges[edge] = n_nodes
#     for surface, points in surfaces_points.items():
#         if surface not in structured_surfaces:
#             gmsh.model.mesh.setTransfiniteSurface(surface, cornerTags=points)
#             structured_surfaces.add(surface)
#     gmsh.model.mesh.setTransfiniteVolume(volume)
