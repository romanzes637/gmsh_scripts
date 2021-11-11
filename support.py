import os
import logging
import time

import numpy as np
import gmsh


# FIXME Bug with this approach:
# File "/share/home/butovr/gmsh_scripts/support.py", line 14,
# in get_volume_points_edges_data
# surfaces_dim_tags = gmsh.model.getBoundary([[3, volume]])
# File "/home/butovr/Programs/gmsh/api/gmsh.py", line 517,
# in getBoundary ierr.value)
# ValueError: ('gmshModelGetBoundary

def flatten(iterable, types=(list,)):
    """Flatten iterable through types

    Args:
        iterable: some iterable
        types: types to recurse

    Returns:
        generator of object: elements
    """
    if isinstance(iterable, types):
        for element in iterable:
            yield from flatten(element, types)
    else:
        yield iterable


class DataTree:
    """Volumes data tree
    # TODO add surfaces loops
    Args:
        vs_dt (list of tuple): Volumes dim-tags

    Attributes:
        vs_dt (list of tuple): Volumes dim-tags
        vs_ss_dt (list of tuple): Surfaces dim-tags of volumes
        vs_ss_cs_dt (list of tuple): Curves dim-tags of surfaces of volumes
        vs_ss_cs_ps_dt (list of tuple): Points dim-tags of curves of surfaces of volumes
        ps_dt_to_cs (dict): Points dim-tags to coordinates
    """

    def __init__(self, vs_dt):
        vs_ss_dt = []  # Surfaces dim-tags of volumes
        vs_ss_cs_dt = []  # Curves dim-tags of surfaces of volumes
        vs_ss_cs_ps_dt = []  # Points dim-tags of curves of surfaces of volumes
        for v_dt in vs_dt:
            # Surfaces dim-tags of the volume
            ss_dt = gmsh.model.getBoundary(dimTags=[v_dt], combined=False,
                                           oriented=True, recursive=False)
            ss_cs_dt = []  # Curves dim-tags of surfaces
            ss_cs_ps_dt = []  # Points dim-tags of curves of surfaces
            for s_dt in ss_dt:
                # Curves dim-tags of the surface
                cs_dt = gmsh.model.getBoundary(dimTags=[s_dt], combined=False,
                                               oriented=True, recursive=False)
                ss_cs_dt.append(cs_dt)
                cs_ps_dt = []  # Points dim-tags of curves
                for c_dt in cs_dt:
                    # Points of the the curve
                    ps_dt = gmsh.model.getBoundary(dimTags=[c_dt],
                                                   combined=False,
                                                   oriented=True,
                                                   recursive=False)
                    cs_ps_dt.append(ps_dt)
                ss_cs_ps_dt.append(cs_ps_dt)
            vs_ss_dt.append(ss_dt)
            vs_ss_cs_dt.append(ss_cs_dt)
            vs_ss_cs_ps_dt.append(ss_cs_ps_dt)
        ps_dt = set(flatten(vs_ss_cs_ps_dt))
        self.ps_dt_to_cs = {x: gmsh.model.getBoundingBox(*x)[:3] for x in ps_dt}
        self.vs_dt = vs_dt
        self.vs_ss_dt = vs_ss_dt
        self.vs_ss_cs_dt = vs_ss_cs_dt
        self.vs_ss_cs_ps_dt = vs_ss_cs_ps_dt
        self.b_sls, self.b_s2sl, self.i_sls, self.i_s2sl = self.evaluate_global_surfaces_loops(vs_ss_dt, vs_ss_cs_dt)

    @staticmethod
    def evaluate_boundary_surfaces(vs_ss_dt):
        b_ss = set()  # Boundary surfaces
        for ss_dt in vs_ss_dt:
            for s_dt in ss_dt:
                if s_dt in b_ss:
                    b_ss.remove(s_dt)
                else:
                    b_ss.add(s_dt)
        return b_ss

    @staticmethod
    def evaluate_global_surfaces_loops(vs_ss_dt, vs_ss_cs_dt):
        b_ss = DataTree.evaluate_boundary_surfaces(vs_ss_dt)
        b_sls, i_sls = [], []
        b_s2sl, i_s2sl = {}, {}
        ss_dt = set(flatten(vs_ss_dt))
        while len(ss_dt) > 0:
            sl, sl_cs, b = [], set(), True  # Surface loop, Curves of surface loop
            new_s = True
            while new_s:
                new_s = False
                for v_i, ss_cs_dt in enumerate(vs_ss_cs_dt):
                    for s_i, cs_dt in enumerate(ss_cs_dt):  # For each remaining surface
                        s_dt = vs_ss_dt[v_i][s_i]
                        if s_dt not in ss_dt:
                            continue
                        if len(sl) == 0:
                            b = s_dt in b_ss
                        else:
                            if (s_dt in b_ss) != b:
                                continue
                        for c_dt in cs_dt:  # For each curve of the surface
                            c_t = abs(c_dt[1])  # Curve tag
                            if len(sl_cs) == 0 or c_t in sl_cs:
                                new_s = True
                                # Add all curves of the surface
                                sl_cs.update(abs(x[1]) for x in ss_cs_dt[s_i])
                                ss_dt.remove(s_dt)  # Remove surface from iteration
                                sl.append(s_dt[1])  # Add surface to loop
                                if b:
                                    b_s2sl[s_dt[1]] = len(b_sls)
                                else:
                                    i_s2sl[s_dt[1]] = len(i_sls)
                                break
            if b:
                b_sls.append(sl)
            else:
                i_sls.append(sl)
        return b_sls, b_s2sl, i_sls, i_s2sl


def plot_statistics():
    message = 'statistics - '
    types_names = ["points", "lines", "triangles", "quadrangles",
                   "tetrahedra", "hexaheda", "prisms", "pyramids", "trihedra"]
    element_types, element_tags, node_tags = gmsh.model.mesh.get_elements(3)
    n_elements, nodes = 0, set()
    for i, et in enumerate(element_types):
        name, ets, nts = types_names[et], element_tags[i], node_tags[i]
        message += f'{len(ets)} {name}, '
        n_elements += len(ets)
        nodes.update(nts)
    message += f'total {n_elements} elements and {len(nodes)} nodes'
    logging.info(message)


def timeit(f):
    def wrapper(*args, **kwargs):
        t = time.perf_counter()
        out = f(*args, **kwargs)
        try:
            name = f.__name__
        except Exception:
            name = f.__class__.__name__
        logging.info(f'{name} - {time.perf_counter() - t:.3f}s')
        return out

    return wrapper


def beta_function(xs, a, b, n=10000):
    """Beta function

    https://en.wikipedia.org/wiki/Beta_function#Incomplete_beta_function

    Args:
        xs (float, np.ndarray): argument(s)
        a (float): alpha
        b (float): beta
        n (int): number of integration steps

    Returns:
        float, np.ndarray: value
    """
    ts, dt = np.linspace(0, xs, n, retstep=True)
    ts = np.ma.masked_values(ts, 0)  # leads to inf
    ts = np.ma.masked_values(ts, 1)  # leads to inf
    vs = ts ** (a - 1) * (1 - ts) ** (b - 1) * dt
    vs = vs.filled(0)
    return np.sum(vs, axis=0)


def beta_pdf(xs, a, b, n=10000):
    """Beta probability density function

    https://en.wikipedia.org/wiki/Beta_distribution#Probability_density_function

    Args:
        xs (float, np.ndarray): argument(s)
        a (float): alpha
        b (float): beta
        n (int): number of integration steps

    Returns:
        float, np.ndarray: value
    """
    t = beta_function(1, a, b, n)
    if a < 1 or b < 1:  # Correct 0 and 1
        _, dt = np.linspace(0, 1, n, retstep=True)
        if isinstance(xs, np.ndarray):
            xs[np.isclose(xs, 0)] = dt
            xs[np.isclose(xs, 1)] = 1 - dt
        else:
            xs = dt if np.isclose(xs, 0) else xs
            xs = 1 - dt if np.isclose(xs, 1) else xs
    return xs ** (a - 1) * (1 - xs) ** (b - 1) / t


def beta_cdf(xs, a, b, n=10000):
    """Beta cumulative distribution function

    https://en.wikipedia.org/wiki/Beta_distribution#Cumulative_distribution_function
    https://en.wikipedia.org/wiki/Beta_function#Incomplete_beta_function

    Args:
        xs (float, np.ndarray): argument(s)
        a (float): alpha
        b (float): beta
        n (int): number of integration steps

    Returns:
        float, np.ndarray: value
    """
    t = beta_function(1, a, b, n)
    # Different integrations steps by x value
    if isinstance(xs, np.ndarray):
        tx = np.array([beta_function(x, a, b, int(np.ceil(n * x))) for x in xs])
    else:
        nx = int(np.ceil(n * xs))
        tx = beta_function(xs, a, b, nx)  # Incomplete beta function
    return tx / t


def check_file(path):
    """
    Check path on the existing file in the order:
    0. If file at absolute path
    1. Else if file at relative to current working directory path
    2. Else if file at relative to running script directory path
    3. Else if file at relative to real running script directory path
    (with eliminating all symbolics links)
    -1. Else no file
    :param str path:
    :return dict: {'type': int, 'path': str}
    """
    # Expand path
    path_expand_vars = os.path.expandvars(path)
    path_expand_vars_user = os.path.expanduser(path_expand_vars)
    # Get directories
    wd_path = os.getcwd()
    script_dir_path = os.path.dirname(os.path.abspath(__file__))
    # Set paths to file check
    clear_path = path_expand_vars_user
    rel_wd_path = os.path.join(wd_path, path_expand_vars_user)
    rel_script_path = os.path.join(script_dir_path, path_expand_vars_user)
    real_rel_script_path = os.path.realpath(rel_script_path)
    # Check on file:
    result = dict()
    if os.path.isfile(clear_path):
        result['type'] = 0
        result['path'] = clear_path
    elif os.path.isfile(rel_wd_path):
        result['type'] = 1
        result['path'] = rel_wd_path
    elif os.path.isfile(rel_script_path):
        result['type'] = 2
        result['path'] = rel_script_path
    elif os.path.isfile(real_rel_script_path):
        result['type'] = 3
        result['path'] = real_rel_script_path
    else:  # No file
        result['type'] = -1
        result['path'] = path
    return result


def volumes_surfaces_to_volumes_groups_surfaces(volumes_surfaces):
    """
    For Environment object. For each distinct inner volume in Environment
    should exist the surface loop. If inner volumes touch each other they unite
    to volume group and have common surface loop.
    :param volumes_surfaces: [[v1_s1, ..., v1_si], ..., [vj_s1, ..., vj_si]]
    :return: volumes_groups_surfaces [[vg1_s1, ..., vg1_si], ...]
    """
    vs_indexes = set(range(len(volumes_surfaces)))
    while len(vs_indexes) != 0:
        current_index = list(vs_indexes)[0]
        current_surfaces = set(volumes_surfaces[current_index])
        other_indexes = {x for x in vs_indexes if x != current_index}
        is_intersection = True
        while is_intersection:
            is_intersection = False
            new_other_indexes = {x for x in other_indexes}
            for i in other_indexes:
                surfaces_i = set(volumes_surfaces[i])
                intersection = current_surfaces.intersection(surfaces_i)
                if len(intersection) > 0:
                    is_intersection = True
                    # Update current
                    current_surfaces.symmetric_difference_update(surfaces_i)
                    new_other_indexes.remove(i)
                    vs_indexes.remove(i)
                    # Update global
                    volumes_surfaces[current_index] = list(current_surfaces)
                    volumes_surfaces[i] = list()
            other_indexes = new_other_indexes
        vs_indexes.remove(current_index)
    volumes_surfaces_groups = [x for x in volumes_surfaces if len(x) != 0]
    return volumes_surfaces_groups
