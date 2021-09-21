from collections import deque
import copy
from pprint import pprint
import time

import gmsh

POINT_TOL = 8
POINTS = {}
CURVES = {}
CURVES_LOOPS = {}
SURFACES = {}
SURFACES_LOOPS = {}
VOLUMES = {}
POINT_TAG = 1
CURVE_TAG = 1
CURVE_LOOP_TAG = 1
SURFACE_TAG = 1
SURFACE_LOOP_TAG = 1
VOLUME_TAG = 1
RECOMBINED_SURFACES = set()
TRANSFINITED_CURVES = set()
TRANSFINITED_SURFACES = set()
TRANSFINITED_VOLUMES = set()

POINT_KWARGS = {
    'geo': {'tag': -1, 'meshSize': 0.},
    'occ': {'tag': -1, 'meshSize': 0.},
}

CURVE_KWARGS = {
    ('geo', 'line'): {'tag': -1},
    ('geo', 'circle_arc'): {'tag': -1, 'nx': 0., 'ny': 0., 'nz': 0.},
    ('geo', 'ellipse_arc'): {'tag': -1, 'nx': 0., 'ny': 0., 'nz': 0.},
    ('geo', 'spline'): {'tag': -1},
    ('geo', 'bspline'): {'tag': -1},
    ('geo', 'bezier'): {'tag': -1},
    ('geo', 'polyline'): {'tag': -1},
    ('occ', 'line'): {'tag': -1},
    ('occ', 'circle_arc'): {'tag': -1},
    ('occ', 'ellipse_arc'): {'tag': -1},
    ('occ', 'spline'): {'tag': -1},
    ('occ', 'bspline'): {'tag': -1, 'degree': 3, 'weights': [], 'knots': [], 'multiplicities': []},
    ('occ', 'bezier'): {'tag': -1},
    ('occ', 'polyline'): {'tag': -1}
}

CURVE_LOOP_KWARGS = {
    'geo': {'tag': -1, 'reorient': False},
    'occ': {'tag': -1}
}

SURFACE_KWARGS = {
    ('geo', 'fill'): {'tag': -1, 'sphereCenterTag': -1},
    ('geo', 'plane'): {'tag': -1},
    ('occ', 'fill'): {'tag': -1, 'pointTags': []},
    ('occ', 'plane'): {'tag': -1}
}

SURFACE_LOOP_KWARGS = {
    'geo': {'tag': -1},
    'occ': {'tag': -1, 'sewing': False}
}

VOLUME_KWARGS = {
    'geo': {'tag': -1},
    'occ': {'tag': -1}
}

RECOMBINE_KWARGS = {
    'geo': {'angle': 45.},
    'occ': {}
}

TRANSFINITE_CURVE_KWARGS = {
    'geo': {'meshType': "Progression",  # Bump
            'coef': 1.},
    'occ': {'meshType': "Progression",  # Bump, Beta
            'coef': 1.}
}

TRANSFINITE_SURFACE_KWARGS = {
    'geo': {'arrangement': "Left"},  # Left, Right, AlternateLeft, AlternateRight
    'occ': {'arrangement': "Left"},  # Left, Right, AlternateLeft, AlternateRight
}

TRANSFINITE_VOLUME_KWARGS = {
    'geo': {},
    'occ': {}
}

name2kwargs = {
    'point': POINT_KWARGS,
    'curve': CURVE_KWARGS,
    'curve_loop': CURVE_LOOP_KWARGS,
    'surface': SURFACE_KWARGS,
    'surface_loop': SURFACE_LOOP_KWARGS,
    'volume': VOLUME_KWARGS,
    'recombine': RECOMBINE_KWARGS,
    'transfinite_curve': TRANSFINITE_CURVE_KWARGS,
    'transfinite_surface': TRANSFINITE_SURFACE_KWARGS,
    'transfinite_volume': TRANSFINITE_VOLUME_KWARGS,
}


def reset():
    global POINTS
    global CURVES
    global CURVES_LOOPS
    global SURFACES
    global SURFACES_LOOPS
    global VOLUMES
    global POINT_TAG
    global CURVE_TAG
    global CURVE_LOOP_TAG
    global SURFACE_TAG
    global SURFACE_LOOP_TAG
    global VOLUME_TAG
    global RECOMBINED_SURFACES
    global TRANSFINITED_CURVES
    global TRANSFINITED_SURFACES
    global TRANSFINITED_VOLUMES
    POINTS = {}
    CURVES = {}
    CURVES_LOOPS = {}
    SURFACES = {}
    SURFACES_LOOPS = {}
    VOLUMES = {}
    POINT_TAG = 1
    CURVE_TAG = 1
    CURVE_LOOP_TAG = 1
    SURFACE_TAG = 1
    SURFACE_LOOP_TAG = 1
    VOLUME_TAG = 1
    RECOMBINED_SURFACES = set()
    TRANSFINITED_CURVES = set()
    TRANSFINITED_SURFACES = set()
    TRANSFINITED_VOLUMES = set()


def correct_kwargs(entity, factory, name):
    kwargs_dict = name2kwargs[name]
    if name in ['curve', 'surface']:
        default_kwargs = kwargs_dict[(factory, entity['name'])]
    else:
        default_kwargs = kwargs_dict[factory]
    if 'kwargs' not in entity:
        entity['kwargs'] = copy.deepcopy(default_kwargs)
    else:
        entity['kwargs'] = {k: v for k, v in entity['kwargs'].items()
                            if k in default_kwargs}
    return entity


add_point = {
    'geo': lambda point: gmsh.model.geo.addPoint(
        x=point['coordinates'][0],
        y=point['coordinates'][1],
        z=point['coordinates'][2],
        **point['kwargs']
    ),
    'occ': lambda point: gmsh.model.occ.addPoint(
        x=point['coordinates'][0],
        y=point['coordinates'][1],
        z=point['coordinates'][2],
        **point['kwargs']
    )
}

add_curve = {
    ('geo', 'line'): lambda curve: gmsh.model.geo.addLine(
        startTag=curve['points'][0]['kwargs']['tag'],
        endTag=curve['points'][-1]['kwargs']['tag'],
        **curve['kwargs']
    ),
    ('geo', 'circle_arc'): lambda curve: gmsh.model.geo.addCircleArc(
        startTag=curve['points'][0]['kwargs']['tag'],
        centerTag=curve['points'][1]['kwargs']['tag'],
        endTag=curve['points'][-1]['kwargs']['tag'],
        **curve['kwargs']
    ),
    ('geo', 'ellipse_arc'): lambda curve: gmsh.model.geo.addEllipseArc(
        startTag=curve['points'][0]['kwargs']['tag'],
        centerTag=curve['points'][1]['kwargs']['tag'],
        majorTag=curve['points'][2]['kwargs']['tag'],
        endTag=curve['points'][-1]['kwargs']['tag'],
        **curve['kwargs']
    ),
    ('geo', 'spline'): lambda curve: gmsh.model.geo.addSpline(
        pointTags=[x['kwargs']['tag'] for x in curve['points']],
        **curve['kwargs']
    ),
    # TODO gmsh warning
    ('geo', 'bspline'): lambda curve: gmsh.model.geo.addBSpline(
        pointTags=[x['kwargs']['tag'] for x in curve['points']],
        **curve['kwargs']
    ),
    ('geo', 'bezier'): lambda curve: gmsh.model.geo.addBezier(
        pointTags=[x['kwargs']['tag'] for x in curve['points']],
        **curve['kwargs']
    ),
    ('geo', 'polyline'): lambda curve: gmsh.model.geo.addPolyline(
        pointTags=[x['kwargs']['tag'] for x in curve['points']],
        **curve['kwargs']
    ),
    ('occ', 'line'): lambda curve: gmsh.model.occ.addLine(
        startTag=curve['points'][0]['kwargs']['tag'],
        endTag=curve['points'][-1]['kwargs']['tag'],
        **curve['kwargs']
    ),
    ('occ', 'circle_arc'): lambda curve: gmsh.model.occ.addCircleArc(
        startTag=curve['points'][0]['kwargs']['tag'],
        centerTag=curve['points'][1]['kwargs']['tag'],
        endTag=curve['points'][-1]['kwargs']['tag'],
        **curve['kwargs']
    ),
    ('occ', 'ellipse_arc'): lambda curve: gmsh.model.occ.addEllipseArc(
        startTag=curve['points'][0]['kwargs']['tag'],
        centerTag=curve['points'][1]['kwargs']['tag'],
        majorTag=curve['points'][2]['kwargs']['tag'],
        endTag=curve['points'][-1]['kwargs']['tag'],
        **curve['kwargs']
    ),
    ('occ', 'spline'): lambda curve: gmsh.model.occ.addSpline(
        pointTags=[x['kwargs']['tag'] for x in curve['points']],
        **curve['kwargs']
    ),
    ('occ', 'bspline'): lambda curve: gmsh.model.occ.addBSpline(
        pointTags=[x['kwargs']['tag'] for x in curve['points']],
        **curve['kwargs']
    ),
    ('occ', 'bezier'): lambda curve: gmsh.model.occ.addBezier(
        pointTags=[x['kwargs']['tag'] for x in curve['points']],
        **curve['kwargs']
    ),
    # FIXME Workaround bspline with degree 1 instead of polyline for occ factory
    ('occ', 'polyline'): lambda curve: gmsh.model.occ.addBSpline(
        pointTags=[x['kwargs']['tag'] for x in curve['points']],
        degree=1,
        **curve['kwargs']
    ),
}

add_curve_loop = {
    'geo': lambda curve_loop: gmsh.model.geo.addCurveLoop(
        curveTags=curve_loop['curves_tags'], **curve_loop['kwargs']),
    'occ': lambda curve_loop: gmsh.model.occ.addCurveLoop(
        curveTags=curve_loop['curves_tags'], **curve_loop['kwargs']),
}

add_surface = {
    ('geo', 'fill'): lambda surface: gmsh.model.geo.addSurfaceFilling(
        wireTags=[x['kwargs']['tag'] for x in surface['curve_loops']],
        **surface['kwargs']
    ),
    ('geo', 'plane'): lambda surface: gmsh.model.geo.addPlaneSurface(
        wireTags=[x['kwargs']['tag'] for x in surface['curve_loops']],
        **surface['kwargs']
    ),
    ('occ', 'fill'): lambda surface: gmsh.model.occ.addSurfaceFilling(
        wireTag=[x['kwargs']['tag'] for x in surface['curve_loops']][0],
        **surface['kwargs']
    ),
    ('occ', 'plane'): lambda surface: gmsh.model.occ.addPlaneSurface(
        wireTags=[x['kwargs']['tag'] for x in surface['curve_loops']][0],
        **surface['kwargs']
    )
}

add_surface_loop = {
    'geo': lambda surface_loop: gmsh.model.geo.addSurfaceLoop(
        surfaceTags=surface_loop['surfaces_tags'], **surface_loop['kwargs']),
    'occ': lambda surface_loop: gmsh.model.occ.addSurfaceLoop(
        surfaceTags=surface_loop['surfaces_tags'], **surface_loop['kwargs']),
}

add_volume = {
    'geo': lambda volume: gmsh.model.geo.addVolume(
        shellTags=[x['kwargs']['tag'] for x in volume['surfaces_loops']],
        **volume['kwargs']
    ),
    'occ': lambda volume: gmsh.model.occ.addVolume(
        shellTags=[x['kwargs']['tag'] for x in volume['surfaces_loops']],
        **volume['kwargs']
    )
}

add_recombine = {
    'geo': lambda rec: gmsh.model.geo.mesh.setRecombine(
        dim=rec['dim'], tag=rec['tag'], **rec['kwargs']),
    'occ': lambda rec: gmsh.model.mesh.setRecombine(
        dim=rec['dim'], tag=rec['tag'], **rec['kwargs'])
}

add_transfinite_curve = {
    'geo': lambda tr: gmsh.model.geo.mesh.setTransfiniteCurve(
        tag=tr['tag'], nPoints=tr['nPoints'], **tr['kwargs']),
    'occ': lambda tr: gmsh.model.mesh.setTransfiniteCurve(
        tag=tr['tag'], numNodes=tr['nPoints'], **tr['kwargs']),
}


add_transfinite_surface = {
    'geo': lambda tr: gmsh.model.geo.mesh.setTransfiniteSurface(
        tag=tr['tag'], cornerTags=tr['cornerTags'], **tr['kwargs']),
    'occ': lambda tr: gmsh.model.mesh.setTransfiniteSurface(
        tag=tr['tag'], cornerTags=tr['cornerTags'], **tr['kwargs']),
}

add_transfinite_volume = {
    'geo': lambda tr: gmsh.model.geo.mesh.setTransfiniteVolume(
        tag=tr['tag'], cornerTags=tr['cornerTags'], **tr['kwargs']),
    'occ': lambda tr: gmsh.model.mesh.setTransfiniteVolume(
        tag=tr['tag'], cornerTags=tr['cornerTags'], **tr['kwargs']),
}


def register_point(factory, point, register_tag):
    point = correct_kwargs(point, factory, 'point')
    key = tuple(round(x, POINT_TOL) for x in point['coordinates'])
    tag = POINTS.get(key, None)
    if tag is None:
        if register_tag:
            global POINT_TAG
            point['kwargs']['tag'] = POINT_TAG
            tag = add_point[factory](point)
            POINT_TAG += 1
        else:
            point['kwargs']['tag'] = -1
            tag = add_point[factory](point)
        POINTS[key] = tag
    point['kwargs']['tag'] = tag
    return point


def register_curve(factory, curve, register_tag):
    curve = correct_kwargs(curve, factory, 'curve')
    name = curve['name']
    ps = [x['kwargs']['tag'] for x in curve['points']]
    key = tuple([name] + ps)
    tag = CURVES.get(key, None)
    if tag is None:
        if register_tag:
            global CURVE_TAG
            curve['kwargs']['tag'] = CURVE_TAG
            tag = add_curve[(factory, name)](curve)
            CURVE_TAG += 1
        else:
            curve['kwargs']['tag'] = -1
            tag = add_curve[(factory, name)](curve)
        CURVES[key] = tag
        rev_key = tuple([name] + list(reversed(ps)))
        CURVES[rev_key] = -tag
    curve['kwargs']['tag'] = tag
    return curve


def register_curve_loop(factory, curve_loop, register_tag):
    curve_loop = correct_kwargs(curve_loop, factory, 'curve_loop')
    curves = curve_loop['curves_tags']
    deq = deque(curves)
    keys = []
    for _ in range(len(deq)):
        deq.rotate(1)
        keys.append(tuple(deq))
    deq = deque([-1 * x for x in reversed(curves)])
    for _ in range(len(deq)):
        deq.rotate(1)
        keys.append(tuple(deq))
    tag = None
    for k in keys:
        tag = CURVES_LOOPS.get(k, None)
        if tag is not None:
            break
    if tag is None:
        if register_tag:
            global CURVE_LOOP_TAG
            curve_loop['kwargs']['tag'] = CURVE_LOOP_TAG
            tag = add_curve_loop[factory](curve_loop)
            CURVE_LOOP_TAG += 1
        else:
            tag = add_curve_loop[factory](curve_loop)
            curve_loop['kwargs']['tag'] = tag
        for k in keys:
            CURVES_LOOPS[k] = tag
    curve_loop['kwargs']['tag'] = tag
    return curve_loop


def register_surface(factory, surface, register_tag):
    surface = correct_kwargs(surface, factory, 'surface')
    name = surface['name']
    key = tuple(x['kwargs']['tag'] for x in surface['curve_loops'])
    tag = SURFACES.get(key, None)
    if tag is None:
        if register_tag:
            global SURFACE_TAG
            surface['kwargs']['tag'] = SURFACE_TAG
            t0 = time.perf_counter()
            tag = add_surface[(factory, name)](surface)
            print(f'ADD {factory} {time.perf_counter() - t0}')
            SURFACE_TAG += 1
            # FIXME Workaround occ auto increment curve loop and surface tags
            if factory == 'occ':
                global CURVE_LOOP_TAG
                CURVE_LOOP_TAG += 1
        else:
            surface['kwargs']['tag'] = -1
            t0 = time.perf_counter()
            tag = add_surface[(factory, name)](surface)
            print(f'ADD {factory} {time.perf_counter() - t0}')
        SURFACES[key] = tag
    surface['kwargs']['tag'] = tag
    return surface


def register_surface_loop(factory, surface_loop, register_tag):
    surface_loop = correct_kwargs(surface_loop, factory, 'surface_loop')
    key = tuple(surface_loop['surfaces_tags'])  # TODO use deque? 12x more keys
    tag = SURFACES_LOOPS.get(key, None)
    if tag is None:
        # FIXME Workaround occ return only -1 tag
        if register_tag or factory == 'occ':
            global SURFACE_LOOP_TAG
            surface_loop['kwargs']['tag'] = SURFACE_LOOP_TAG
            tag = add_surface_loop[factory](surface_loop)
            SURFACE_LOOP_TAG += 1
        else:
            surface_loop['kwargs']['tag'] = -1
            tag = add_surface_loop[factory](surface_loop)
        SURFACES_LOOPS[key] = tag
    surface_loop['kwargs']['tag'] = tag
    return surface_loop


def register_volume(factory, volume, register_tag):
    volume = correct_kwargs(volume, factory, 'volume')
    key = tuple(x['kwargs']['tag'] for x in volume['surfaces_loops'])
    tag = VOLUMES.get(key, None)
    if tag is None:
        if register_tag:
            global VOLUME_TAG
            volume['kwargs']['tag'] = VOLUME_TAG
            tag = add_volume[factory](volume)
            VOLUME_TAG += 1
        else:
            volume['kwargs']['tag'] = -1
            tag = add_volume[factory](volume)
        VOLUMES[key] = tag
    volume['kwargs']['tag'] = tag
    return volume


def register_recombine_surface(surface, factory):
    tag = surface['kwargs']['tag']
    if tag not in RECOMBINED_SURFACES:
        rec = copy.deepcopy(surface['recombine'])
        rec = correct_kwargs(rec, factory, 'recombine')
        rec['dim'] = 2
        rec['tag'] = tag
        add_recombine[factory](rec)
        RECOMBINED_SURFACES.add(tag)
        surface['recombine'] = rec
    return surface


def register_transfinite_curve(curve, factory):
    tag = curve['kwargs']['tag']
    if tag not in TRANSFINITED_CURVES:
        tr = copy.deepcopy(curve['transfinite'])
        tr = correct_kwargs(tr, factory, 'transfinite_curve')
        tr['tag'] = tag
        add_transfinite_curve[factory](tr)
        TRANSFINITED_CURVES.add(tag)
        curve['transfinite'] = tr
    return curve


def register_transfinite_surface(surface, factory):
    tag = surface['kwargs']['tag']
    if tag not in TRANSFINITED_SURFACES:
        tr = copy.deepcopy(surface['transfinite'])
        tr = correct_kwargs(tr, factory, 'transfinite_surface')
        tr['tag'] = tag
        add_transfinite_surface[factory](tr)
        TRANSFINITED_SURFACES.add(tag)
        surface['transfinite'] = tr
    return surface


def register_transfinite_volume(volume, factory):
    tag = volume['kwargs']['tag']
    if tag not in TRANSFINITED_VOLUMES:
        tr = copy.deepcopy(volume['transfinite'])
        tr = correct_kwargs(tr, factory, 'transfinite_volume')
        tr['tag'] = tag
        add_transfinite_volume[factory](tr)
        TRANSFINITED_VOLUMES.add(tag)
        volume['transfinite'] = tr
    return volume


# TODO remove from registry
def unregister_volume(factory, volume, register_tag):
    tag = volume['kwargs']['tag']
    dim_tag = [3, tag]
    gmsh.model.removeEntities([dim_tag], recursive=True)
    del volume['kwargs']['tag']
    return volume
