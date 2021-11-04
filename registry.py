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
QUADRATED_SURFACES = set()
STRUCTURED_CURVES = set()
STRUCTURED_SURFACES = set()
STRUCTURED_VOLUMES = set()

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
    'geo': {'tag': None, 'dim': None, 'angle': 45.},
    'occ': {'tag': None, 'dim': None}
}

TRANSFINITE_CURVE_KWARGS = {
    'geo': {'tag': None, 'nPoints': 2, 'meshType': "Progression", 'coef': 1.},
    'occ': {'tag': None, 'numNodes': 2, 'meshType': "Progression", 'coef': 1.}
}

TRANSFINITE_CURVE_TYPES = ['Progression', 'Bump', 'Beta']

TRANSFINITE_SURFACE_KWARGS = {
    'geo': {'tag': None,
            'cornerTags': None,
            'arrangement': 'Left'},  # Left, Right, AlternateLeft, AlternateRight
    'occ': {'tag': None,
            'cornerTags': None,
            'arrangement': 'Left'},  # Left, Right, AlternateLeft, AlternateRight
}

TRANSFINITE_VOLUME_KWARGS = {
    'geo': {'tag': None, 'cornerTags': None},
    'occ': {'tag': None, 'cornerTags': None}
}

name2kwargs = {
    'point': POINT_KWARGS,
    'curve': CURVE_KWARGS,
    'curve_loop': CURVE_LOOP_KWARGS,
    'surface': SURFACE_KWARGS,
    'surface_loop': SURFACE_LOOP_KWARGS,
    'volume': VOLUME_KWARGS,
    'quadrate': RECOMBINE_KWARGS,
    'structure_curve': TRANSFINITE_CURVE_KWARGS,
    'structure_surface': TRANSFINITE_SURFACE_KWARGS,
    'structure_volume': TRANSFINITE_VOLUME_KWARGS,
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
    global QUADRATED_SURFACES
    global STRUCTURED_CURVES
    global STRUCTURED_SURFACES
    global STRUCTURED_VOLUMES
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
    QUADRATED_SURFACES = set()
    STRUCTURED_CURVES = set()
    STRUCTURED_SURFACES = set()
    STRUCTURED_VOLUMES = set()


def correct_kwargs(entity, factory, name):
    kwargs = {k: v for k, v in entity.__dict__.items() if not k.startswith('__')}
    if name in ['curve', 'surface']:
        default_kwargs = name2kwargs[name][(factory, entity.name)]
    else:
        default_kwargs = name2kwargs[name][factory]
    if 'kwargs' not in kwargs:
        kwargs['kwargs'] = copy.deepcopy(default_kwargs)
    else:
        kwargs['kwargs'] = {k: v for k, v in kwargs['kwargs'].items()
                            if k in default_kwargs}
    if name in ['structure_curve']:
        if 'nPoints' in kwargs['kwargs'] and factory == 'occ':
            kwargs['kwargs']['numNodes'] = kwargs['kwargs'].pop('nPoints')
        if isinstance(kwargs['kwargs']['meshType'], int):
            kwargs['kwargs']['meshType'] = TRANSFINITE_CURVE_TYPES[kwargs['kwargs']['meshType']]
    return kwargs


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
        startTag=curve['points'][0].tag,
        endTag=curve['points'][-1].tag,
        **curve['kwargs']
    ),
    ('geo', 'circle_arc'): lambda curve: gmsh.model.geo.addCircleArc(
        startTag=curve['points'][0].tag,
        centerTag=curve['points'][1].tag,
        endTag=curve['points'][-1].tag,
        **curve['kwargs']
    ),
    ('geo', 'ellipse_arc'): lambda curve: gmsh.model.geo.addEllipseArc(
        startTag=curve['points'][0].tag,
        centerTag=curve['points'][1].tag,
        majorTag=curve['points'][2].tag,
        endTag=curve['points'][-1].tag,
        **curve['kwargs']
    ),
    ('geo', 'spline'): lambda curve: gmsh.model.geo.addSpline(
        pointTags=[x.tag for x in curve['points']],
        **curve['kwargs']
    ),
    # TODO gmsh warning
    ('geo', 'bspline'): lambda curve: gmsh.model.geo.addBSpline(
        pointTags=[x.tag for x in curve['points']],
        **curve['kwargs']
    ),
    ('geo', 'bezier'): lambda curve: gmsh.model.geo.addBezier(
        pointTags=[x.tag for x in curve['points']],
        **curve['kwargs']
    ),
    ('geo', 'polyline'): lambda curve: gmsh.model.geo.addPolyline(
        pointTags=[x.tag for x in curve['points']],
        **curve['kwargs']
    ),
    ('occ', 'line'): lambda curve: gmsh.model.occ.addLine(
        startTag=curve['points'][0].tag,
        endTag=curve['points'][-1].tag,
        **curve['kwargs']
    ),
    ('occ', 'circle_arc'): lambda curve: gmsh.model.occ.addCircleArc(
        startTag=curve['points'][0].tag,
        centerTag=curve['points'][1].tag,
        endTag=curve['points'][-1].tag,
        **curve['kwargs']
    ),
    ('occ', 'ellipse_arc'): lambda curve: gmsh.model.occ.addEllipseArc(
        startTag=curve['points'][0].tag,
        centerTag=curve['points'][1].tag,
        majorTag=curve['points'][2].tag,
        endTag=curve['points'][-1].tag,
        **curve['kwargs']
    ),
    ('occ', 'spline'): lambda curve: gmsh.model.occ.addSpline(
        pointTags=[x.tag for x in curve['points']],
        **curve['kwargs']
    ),
    ('occ', 'bspline'): lambda curve: gmsh.model.occ.addBSpline(
        pointTags=[x.tag for x in curve['points']],
        **curve['kwargs']
    ),
    ('occ', 'bezier'): lambda curve: gmsh.model.occ.addBezier(
        pointTags=[x.tag for x in curve['points']],
        **curve['kwargs']
    ),
    # FIXME Workaround bspline with degree 1 instead of polyline for occ factory
    ('occ', 'polyline'): lambda curve: gmsh.model.occ.addBSpline(
        pointTags=[x.tag for x in curve['points']],
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
        wireTags=[x.tag for x in surface['curves_loops']],
        **surface['kwargs']
    ),
    ('geo', 'plane'): lambda surface: gmsh.model.geo.addPlaneSurface(
        wireTags=[x.tag for x in surface['curves_loops']],
        **surface['kwargs']
    ),
    ('occ', 'fill'): lambda surface: gmsh.model.occ.addSurfaceFilling(
        wireTag=[x.tag for x in surface['curves_loops']][0],
        **surface['kwargs']
    ),
    ('occ', 'plane'): lambda surface: gmsh.model.occ.addPlaneSurface(
        wireTags=[x.tag for x in surface['curve_loops']][0],
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
        shellTags=[x.tag for x in volume['surfaces_loops']], **volume['kwargs']
    ),
    'occ': lambda volume: gmsh.model.occ.addVolume(
        shellTags=[x.tag for x in volume['surfaces_loops']], **volume['kwargs']
    )
}

add_quadrate = {
    'geo': lambda x: gmsh.model.geo.mesh.setRecombine(**x['kwargs']),
    'occ': lambda x: gmsh.model.mesh.setRecombine(**x['kwargs'])
}

add_structure_curve = {
    'geo': lambda x: gmsh.model.geo.mesh.setTransfiniteCurve(**x['kwargs']),
    'occ': lambda x: gmsh.model.mesh.setTransfiniteCurve(**x['kwargs'])
}

add_structure_surface = {
    'geo': lambda x: gmsh.model.geo.mesh.setTransfiniteSurface(**x['kwargs']),
    'occ': lambda x: gmsh.model.mesh.setTransfiniteSurface(**x['kwargs']),
}

add_structure_volume = {
    'geo': lambda x: gmsh.model.geo.mesh.setTransfiniteVolume(**x['kwargs']),
    'occ': lambda x: gmsh.model.mesh.setTransfiniteVolume(**x['kwargs']),
}


def register_point(factory, point, register_tag):
    key = tuple(round(x, POINT_TOL) for x in point.coordinates)
    tag = POINTS.get(key, None)
    if tag is None:
        point_kwargs = correct_kwargs(point, factory, 'point')
        if register_tag:
            global POINT_TAG
            point_kwargs['kwargs']['tag'] = POINT_TAG
            tag = add_point[factory](point_kwargs)
            POINT_TAG += 1
        else:
            point_kwargs['kwargs']['tag'] = -1
            tag = add_point[factory](point_kwargs)
        POINTS[key] = tag
    point.tag = tag
    return point


def register_curve(factory, curve, register_tag):
    name = curve.name
    ps = [x.tag for x in curve.points]
    key = tuple([name] + ps)
    tag = CURVES.get(key, None)
    if tag is None:
        curve_kwargs = correct_kwargs(curve, factory, 'curve')
        if register_tag:
            global CURVE_TAG
            curve_kwargs['kwargs']['tag'] = CURVE_TAG
            tag = add_curve[(factory, name)](curve_kwargs)
            CURVE_TAG += 1
        else:
            curve_kwargs['kwargs']['tag'] = -1
            tag = add_curve[(factory, name)](curve_kwargs)
        CURVES[key] = tag
        rev_key = tuple([name] + list(reversed(ps)))
        CURVES[rev_key] = -tag
    curve.tag = tag
    return curve


def register_curve_loop(factory, curve_loop, use_register_tag):
    curves = [x.tag * y for (x, y) in zip(curve_loop.curves,
                                          curve_loop.curves_signs)]
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
        curve_loop_kwargs = correct_kwargs(curve_loop, factory, 'curve_loop')
        curve_loop_kwargs['curves_tags'] = curves
        if use_register_tag:
            global CURVE_LOOP_TAG
            curve_loop_kwargs['kwargs']['tag'] = CURVE_LOOP_TAG
            tag = add_curve_loop[factory](curve_loop_kwargs)
            CURVE_LOOP_TAG += 1
        else:
            curve_loop_kwargs['kwargs']['tag'] = -1
            tag = add_curve_loop[factory](curve_loop_kwargs)
        for k in keys:
            CURVES_LOOPS[k] = tag
    curve_loop.tag = tag
    return curve_loop


def register_surface(factory, surface, use_register_tag):
    name = surface.name
    key = tuple(x.tag for x in surface.curves_loops)
    tag = SURFACES.get(key, None)
    if tag is None:
        surface_kwargs = correct_kwargs(surface, factory, 'surface')
        if use_register_tag:
            global SURFACE_TAG
            surface_kwargs['kwargs']['tag'] = SURFACE_TAG
            # t0 = time.perf_counter()  # FIXME Too long in occ factory!
            tag = add_surface[(factory, name)](surface_kwargs)
            # print(time.perf_counter() - t0)
            SURFACE_TAG += 1
            # FIXME Workaround occ auto increment curve loop and surface tags
            if factory == 'occ':
                global CURVE_LOOP_TAG
                CURVE_LOOP_TAG += 1
        else:
            surface_kwargs['kwargs']['tag'] = -1
            # t0 = time.perf_counter()  # FIXME Too long in occ factory!
            tag = add_surface[(factory, name)](surface_kwargs)
            # print(time.perf_counter() - t0)
        SURFACES[key] = tag
    surface.tag = tag
    return surface


def register_surface_loop(factory, surface_loop, register_tag):
    key = tuple(x.tag for x in surface_loop.surfaces)  # TODO use deque? 12x more keys
    tag = SURFACES_LOOPS.get(key, None)
    if tag is None:
        surface_loop_kwargs = correct_kwargs(surface_loop, factory, 'surface_loop')
        surface_loop_kwargs['surfaces_tags'] = key
        # FIXME Workaround occ return only -1 tag
        if register_tag or factory == 'occ':
            global SURFACE_LOOP_TAG
            surface_loop_kwargs['kwargs']['tag'] = SURFACE_LOOP_TAG
            tag = add_surface_loop[factory](surface_loop_kwargs)
            SURFACE_LOOP_TAG += 1
        else:
            surface_loop_kwargs['kwargs']['tag'] = -1
            tag = add_surface_loop[factory](surface_loop_kwargs)
        SURFACES_LOOPS[key] = tag
    surface_loop.tag = tag
    return surface_loop


def register_volume(factory, volume, use_register_tag):
    key = tuple(x.tag for x in volume.surfaces_loops)
    tag = VOLUMES.get(key, None)
    if tag is None:
        volume_kwargs = correct_kwargs(volume, factory, 'volume')
        if use_register_tag:
            global VOLUME_TAG
            volume_kwargs['kwargs']['tag'] = VOLUME_TAG
            tag = add_volume[factory](volume_kwargs)
            VOLUME_TAG += 1
        else:
            volume_kwargs['kwargs']['tag'] = -1
            tag = add_volume[factory](volume_kwargs)
        VOLUMES[key] = tag
    volume.tag = tag
    return volume


def register_quadrate_surface(surface, factory):
    tag = surface.tag
    if tag not in QUADRATED_SURFACES:
        rec = correct_kwargs(surface.quadrate, factory, 'quadrate')
        rec['kwargs']['dim'] = 2
        rec['kwargs']['tag'] = tag
        add_quadrate[factory](rec)
        QUADRATED_SURFACES.add(tag)
    return surface


def register_structure_curve(curve, factory):
    tag = curve.tag
    if tag not in STRUCTURED_CURVES:
        tr = correct_kwargs(curve.structure, factory, 'structure_curve')
        tr['kwargs']['tag'] = tag
        add_structure_curve[factory](tr)
        STRUCTURED_CURVES.add(tag)
    return curve


def register_structure_surface(surface, factory):
    tag = surface.tag
    if tag not in STRUCTURED_SURFACES:
        tr = correct_kwargs(surface.structure, factory, 'structure_surface')
        tr['kwargs']['tag'] = tag
        add_structure_surface[factory](tr)
        STRUCTURED_SURFACES.add(tag)
    return surface


def register_structure_volume(volume, factory):
    tag = volume.tag
    if tag not in STRUCTURED_VOLUMES:
        tr = correct_kwargs(volume.structure, factory, 'structure_volume')
        tr['kwargs']['tag'] = tag
        add_structure_volume[factory](tr)
        STRUCTURED_VOLUMES.add(tag)
    return volume


# TODO remove from registry
def unregister_volume(factory, volume, register_tag):
    tag = volume.tag
    gmsh.model.removeEntities([(3, tag)], recursive=True)
    volume.tag = None
    return volume
