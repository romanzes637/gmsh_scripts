import json
import argparse


def main(lines):
    points = [list(map(float, x.split()[1:4])) for x in lines if x.startswith('v')]
    polygons = [[int(y) - 1 for y in x.split()[1:]] for x in lines if x.startswith('f')]
    return {'data': {'class': 'block.Polyhedron',
                     'points': points,
                     'polygons': polygons}}


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--input', help='obj file', default='test.obj')
    parser.add_argument('-o', '--output', help='gmsh json file', default='gmsh.json')
    args = vars(parser.parse_args())
    with open(args['input']) as f:
        obj = f.readlines()
    output = main(obj)
    print(f'points: {len(output["data"]["points"])}')
    print(f'polygons: {len(output["data"]["polygons"])}')
    with open(args['output'], 'w') as f:
        json.dump(output, f, indent=2)
