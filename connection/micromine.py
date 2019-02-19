import json
import time


def read_carcass(path):
    with open(path) as f:
        n_points, n_triangles = tuple(int(x) for x in f.readline().split())
        print('points: {}\ntriangles: {}'.format(n_points, n_triangles))
        points = [tuple(float(x) for x in f.readline().split()) for _ in
                  range(n_points)]
        triangles = [tuple(int(x) for x in f.readline().split()) for _ in
                     range(n_triangles)]
        print('last point: {}'.format(points[-1]))
        print('last triangle: {}'.format(triangles[-1]))
    return points, triangles


def check_carcass(points, triangles):
    # Points neighbours
    points_neighbours = dict()
    report = dict()
    for t in triangles:
        p1, p2, p3 = t
        p1_ns = (p2, p3)
        p2_ns = (p1, p3)
        p3_ns = (p2, p1)
        points_neighbours.setdefault(p1, set()).update(p1_ns)
        points_neighbours.setdefault(p2, set()).update(p2_ns)
        points_neighbours.setdefault(p3, set()).update(p3_ns)
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
    time_left = 0
    time_spent = 0
    for i, p in enumerate(points):
        print('Point {}/{}'.format(i + 1, len(points)))
        start_time = time.time()
        in_group = False
        for g in points_groups:
            if i in g:
                in_group = True
                break
        print('Already in the group: {}'.format(in_group))
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
        time_per_point = time.time() - start_time
        time_spent += time_per_point
        time_left = time_per_point * (len(points) - (i + 1))
        print('Groups: {}'.format(len(points_groups)))
        print('Lengths: {}'.format([len(x) for x in points_groups]))
        print('Time point: {}s'.format(time_per_point))
        print('Time spent: {}s'.format(time_spent))
        print('Time left: {}s'.format(time_left))
    with open('check_carcass.json', 'w') as f:
        data = dict()
        data['points_groups'] = [list(x) for x in points_groups]
        json.dump(data, f)
    n_points_groups = len(points_groups)
    groups_n_points = [len(x) for x in points_groups]
    ps_avg = float(sum(groups_n_points)) / n_points_groups
    ps_max = max(groups_n_points)
    ps_min = min(groups_n_points)
    report['n_points_groups'] = n_points_groups
    report['group_points_avg'] = ps_avg
    report['group_points_max'] = ps_max
    report['group_points_min'] = ps_min
    return report


def volume_from_carcass(points, triangles):
    print('gmsh')
    import gmsh

    model = gmsh.model
    factory = model.geo
    gmsh.initialize()
    gmsh.option.setNumber("General.Terminal", 1)
    model.add("carcass")
    with open('check_carcass.json') as f:
        data = json.load(f)
        points_groups = data['points_groups']
    volumes_tags = list()
    for j, group in enumerate(points_groups):
        print('Group: {}\nLength: {}'.format(j + 1, len(group)))
        print('Points')
        lc = 100
        point_index_to_tag = dict()
        for i, p in enumerate(points):
            if i in group:
                c1, c2, c3 = p
                tag = factory.addPoint(c1, c2, c3, lc)
                point_index_to_tag[i] = tag
        print('Lines and Surfaces')
        surfaces = list()
        for t in triangles:
            i1, i2, i3 = t
            if i1 in point_index_to_tag and i2 in point_index_to_tag and i3 in point_index_to_tag:
                p1 = point_index_to_tag[i1]
                p2 = point_index_to_tag[i2]
                p3 = point_index_to_tag[i3]
                # Direct order
                l1 = factory.addLine(p1, p2)
                l2 = factory.addLine(p2, p3)
                l3 = factory.addLine(p3, p1)
                # Reverse order, so no differences...
                # l1 = factory.addLine(p1, p3)
                # l2 = factory.addLine(p3, p2)
                # l3 = factory.addLine(p2, p1)
                curve_loop_tag = factory.addCurveLoop([l1, l2, l3])
                surface_tag = factory.addSurfaceFilling([curve_loop_tag])
                surfaces.append(surface_tag)
        # Surfaces
        print('Volumes')
        surface_loop_tag = factory.addSurfaceLoop(surfaces)
        volume_tag = factory.addVolume([surface_loop_tag])
        volumes_tags.append(volume_tag)
    print('Synchronizing')
    factory.synchronize()
    # Mesh
    model.mesh.generate(3)
    # Write
    gmsh.write("carcass.msh2")
    gmsh.finalize()
    return volumes_tags


if __name__ == '__main__':
    import argparse
    from pprint import pprint

    parser = argparse.ArgumentParser()
    parser.add_argument('carcass', help='carcass file')
    args = parser.parse_args()
    print(args)
    ps, ts = read_carcass(args.carcass)
    r = check_carcass(ps, ts)
    pprint(r)
    vs = volume_from_carcass(ps, ts)
    print(vs)
