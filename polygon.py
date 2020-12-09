import itertools
import time
from pprint import pprint

import gmsh

from connection import micromine
from complex import Complex
from primitive import Primitive
from support import check_file


class Polygon(Complex):
    def __init__(self, factory, inputs, physical_names, reader, reader_kwargs,
                 coordinates_transform, mesh_size_coefficients):

        if factory == 'occ':
            factory_object = gmsh.model.occ
        else:
            factory_object = gmsh.model.geo
        primitives = list()
        for i, path in enumerate(inputs):
            result = check_file(path)
            reader_kwargs["path"] = result['path']
            points, polygons = readers[reader](**reader_kwargs)
            print('Transform coordinates')
            points = transform_coordinates(points, coordinates_transform)
            print('last point: {}'.format(points[-1]))
            print('Evaluate groups')
            groups_points, groups_polygons = evaluate_groups(points, polygons)
            print('Number of groups points: {}\nNumber of groups polygons: {}'
                  .format([len(x) for x in groups_points],
                          [len(x) for x in groups_polygons]))
            print('Groups: {}'.format(len(groups_points)))
            print('Check closed volumes')
            result = check_closed_volume(polygons, groups_polygons)
            print('Closed volumes {}'.format(sum(result)))
            print(result)
            # Leave only closed volumes
            closed_groups_points = list(
                itertools.compress(groups_points, result))
            closed_groups_polygons = list(
                itertools.compress(groups_polygons, result))
            print('Evaluate sizes')
            sizes = evaluate_groups_points_mesh_sizes(points, polygons,
                                                      closed_groups_polygons)
            print(sizes)
            print('Correct sizes by coefficient')
            k = mesh_size_coefficients[i]
            print('Coefficient: {}'.format(k))
            sizes = [k * x for x in sizes]
            print(sizes)
            print('Create closed volumes only')
            vs = create_volumes(factory_object, points, polygons,
                                closed_groups_points, closed_groups_polygons,
                                sizes)
            name = physical_names[i]
            p = Primitive(factory, volume_name=name, inner_volumes=vs)
            primitives.append(p)
        Complex.__init__(self, factory, primitives)


def transform_coordinates(points, transform):
    dx, dy, dz, k = transform
    for i, p in enumerate(points):
        x, y, z = p
        points[i] = (k * x + dx, k * y + dy, k * z + dz)
    return points


def evaluate_groups(points, polygons):
    # Points neighbours
    points_neighbours = dict()
    points_polygons = dict()
    report = dict()
    for i, polygon in enumerate(polygons):
        for point in polygon:
            neighbours = [x for x in polygon if x != point]
            points_neighbours.setdefault(point, set()).update(neighbours)
            points_polygons.setdefault(point, list()).append(i)
    n_neighbours = len(points_neighbours)
    points_n_neighbours = [len(x) for x in points_neighbours.values()]
    ns_avg = float(sum(points_n_neighbours)) / n_neighbours
    ns_max = max(points_n_neighbours)
    ns_min = min(points_n_neighbours)
    report['n_points_neighbours'] = n_neighbours
    report['point_neighbours_avg'] = ns_avg
    report['point_neighbours_max'] = ns_max
    report['point_neighbours_min'] = ns_min
    # Points groups
    points_groups = set()
    # time_left = 0
    # time_spent = 0
    for i, p in enumerate(points):
        # print('Point {}/{}'.format(i + 1, len(points)))
        # start_time = time.time()
        in_group = False
        for g in points_groups:
            if i in g:
                in_group = True
                break
        # print('Already in the group: {}'.format(in_group))
        if not in_group:
            have_been = set()
            to_go = points_neighbours[i]
            while len(to_go) > 0:
                have_been.update(to_go)
                new_to_go = set()
                for n in to_go:
                    n_neighbours = points_neighbours[n]
                    have_not_been = n_neighbours.difference(have_been)
                    new_to_go.update(have_not_been)
                to_go = new_to_go
            points_groups.add(frozenset(have_been))
        # time_per_point = time.time() - start_time
        # time_spent += time_per_point
        # time_left = time_per_point * (len(points) - (i + 1))
        # print('Groups: {}'.format(len(points_groups)))
        # print('Lengths: {}'.format([len(x) for x in points_groups]))
        # print('Time point: {}s'.format(time_per_point))
        # print('Time spent: {}s'.format(time_spent))
        # print('Time left: {}s'.format(time_left))
    # with open('check_carcass.json', 'w') as f:
    #     data = dict()
    #     data['points_groups'] = [list(x) for x in points_groups]
    #     json.dump(data, f)
    n_points_groups = len(points_groups)
    groups_n_points = [len(x) for x in points_groups]
    ps_avg = float(sum(groups_n_points)) / n_points_groups
    ps_max = max(groups_n_points)
    ps_min = min(groups_n_points)
    report['n_points_groups'] = n_points_groups
    report['group_points_avg'] = ps_avg
    report['group_points_max'] = ps_max
    report['group_points_min'] = ps_min
    # Group's points and polygons
    groups_points = list(points_groups)
    groups_polygons = list()
    for group in groups_points:
        group_polygons = set()
        for point in group:
            point_polygons = points_polygons[point]
            group_polygons.update(point_polygons)
        groups_polygons.append(group_polygons)
    pprint(report)
    return groups_points, groups_polygons


def evaluate_groups_points_mesh_sizes(points, polygons, polygons_groups):
    """
    Mesh size at points as min edge length
    :param points:
    :param polygons:
    :param polygons_groups:
    :return: mesh size at points
    """
    sizes = list()
    edges_square_lengths = dict()
    for group in polygons_groups:
        for polygon_index in group:
            polygon = polygons[polygon_index]
            for i in range(len(polygon) - 1):
                start = polygon[i]
                end = polygon[i + 1]
                edge = frozenset([start, end])
                if edge not in edges_square_lengths:
                    start_cs = points[start]
                    end_cs = points[end]
                    square_length = sum(
                        [(x[0] - x[1]) ** 2 for x in zip(end_cs, start_cs)])
                    edges_square_lengths[edge] = square_length
        min_edge = min(edges_square_lengths, key=edges_square_lengths.get)
        min_edge_length = edges_square_lengths[min_edge] ** 0.5
        sizes.append(min_edge_length)
    return sizes


def check_closed_volume(polygons, groups_polygons):
    result = list()
    # opened = set()
    for group in groups_polygons:
        number_of_edges = dict()
        for polygon_index in group:
            polygon = polygons[polygon_index]
            # Edge loop
            for i in range(len(polygon) - 1):
                start = polygon[i]
                end = polygon[i + 1]
                edge = frozenset([start, end])
                number_of_edges.setdefault(edge, 0)
                number_of_edges[edge] += 1
            # Close loop
            start = polygon[-1]
            end = polygon[0]
            edge = frozenset([start, end])
            number_of_edges.setdefault(edge, 0)
            number_of_edges[edge] += 1
        closed = True
        for key, value in number_of_edges.items():
            if value != 2:  # Has no opposite edge
                # print(key, value)
                closed = False
                break
                # opened.add(key)
        result.append(closed)
    # print(opened)
    return result


def create_volumes(factory_object, points, polygons, groups_points,
                   groups_polygons, points_mesh_sizes):
    volumes = list()
    for j, group_points in enumerate(groups_points):
        group_polygons = groups_polygons[j]
        print('Group: {}\nPoints: {}\nPolygons: {}'.format(
            j + 1, len(group_points), len(group_polygons)))
        print('Points')
        lc = points_mesh_sizes[j]
        point_index_to_tag = dict()
        for point_index in group_points:
            c1, c2, c3 = points[point_index]
            tag = factory_object.addPoint(c1, c2, c3, lc)
            point_index_to_tag[point_index] = tag
        print('Lines and Surfaces')
        surfaces = list()
        pair_points_to_tag = dict()
        for polygon_index in group_polygons:
            curves = list()
            polygon = polygons[polygon_index]
            # Edges loop
            for i in range(len(polygon) - 1):
                point_index_0 = polygon[i]
                point_index_1 = polygon[i + 1]
                # Move forward the numbering by 1, because 0 cannot be negative
                # Note: minus for second point is for distinguish 1 to 2 from
                # 2 to 1 line in non ordered frozenset as
                # (1, 2) set for 1 -> 2 line # and (1, -2) set for 2 -> 1 line
                pair_points = frozenset(
                    [point_index_0 + 1, -(point_index_1 + 1)])
                if pair_points not in pair_points_to_tag:
                    tag_0 = point_index_to_tag[point_index_0]
                    tag_1 = point_index_to_tag[point_index_1]
                    tag = factory_object.addLine(tag_0, tag_1)
                    pair_points_to_tag[pair_points] = tag
                else:
                    tag = pair_points_to_tag[pair_points]
                curves.append(tag)
            # Close loop
            point_index_0 = polygon[-1]
            point_index_1 = polygon[0]
            pair_points = frozenset([point_index_0 + 1, -(point_index_1 + 1)])
            if pair_points not in pair_points_to_tag:
                tag_0 = point_index_to_tag[point_index_0]
                tag_1 = point_index_to_tag[point_index_1]
                tag = factory_object.addLine(tag_0, tag_1)
                pair_points_to_tag[pair_points] = tag
            else:
                tag = pair_points_to_tag[pair_points]
            curves.append(tag)
            # Surfaces
            loop_tag = factory_object.addCurveLoop(curves)
            if len(curves) <= 4:
                if factory_object == gmsh.model.geo:
                    surface_tag = factory_object.addSurfaceFilling([loop_tag])
                else:
                    surface_tag = factory_object.addSurfaceFilling(loop_tag)
            else:
                surface_tag = factory_object.addPlaneSurface([loop_tag])
            surfaces.append(surface_tag)
        # Surfaces
        print('Volumes')
        loop_tag = factory_object.addSurfaceLoop(surfaces)
        volume_tag = factory_object.addVolume([loop_tag])
        volumes.append(volume_tag)
    return volumes


readers = {
    "micromine": micromine.read
}
