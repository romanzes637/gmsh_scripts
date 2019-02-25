def read(path):
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


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument('path', help='carcass file')
    args = parser.parse_args()
    print(args)
    ps, ts = read(args.path)
