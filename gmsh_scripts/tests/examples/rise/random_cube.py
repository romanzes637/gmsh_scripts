import yaml
import numpy as np

if __name__ == '__main__':
    n_children = 10
    seed = 42
    with open('cube.yml') as f:
        cube = yaml.safe_load(f)
    rng = np.random.default_rng(seed)
    cylinder_origins = rng.uniform(low=-1, high=1, size=(n_children, 3))
    cylinder_origins[:, 2] -= 0.5  # Optional move origin to cylinders centers
    cube['data']['children'] = ['/cylinder.yml' for _ in cylinder_origins]
    cube['data']['children_transforms'] = [[x.tolist()] for x in cylinder_origins]
    with open('random_cube.yml', 'w') as f:
        yaml.safe_dump(cube, f)
