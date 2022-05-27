from collections import deque
from itertools import permutations
import copy

import gmsh

FACTORY = 'geo'
POINT_TOL = 12
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
CURVE_STRUCTURE = {}
SURFACE_STRUCTURE = {}
VOLUME_STRUCTURE = {}
SURFACE_QUADRATE = {}
BOOLEAN_NEW2OLDS = {}
BOOLEAN_OLD2NEWS = {}
VOLUME2BLOCK = {}
USE_REGISTRY_TAG = True
UNREGISTERED_VOLUMES = set()

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


def reset(factory='geo', point_tol=8):
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
    global CURVE_STRUCTURE
    global SURFACE_STRUCTURE
    global SURFACE_QUADRATE
    global VOLUME_STRUCTURE
    global FACTORY
    global POINT_TOL
    global BOOLEAN_NEW2OLDS
    global BOOLEAN_OLD2NEWS
    global VOLUME2BLOCK
    global USE_REGISTRY_TAG
    global UNREGISTERED_VOLUMES
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
    CURVE_STRUCTURE = {}
    SURFACE_STRUCTURE = {}
    SURFACE_QUADRATE = {}
    VOLUME_STRUCTURE = {}
    FACTORY = factory
    POINT_TOL = point_tol
    BOOLEAN_NEW2OLDS = {}
    BOOLEAN_OLD2NEWS = {}
    VOLUME2BLOCK = {}
    USE_REGISTRY_TAG = True
    UNREGISTERED_VOLUMES = set()


def correct_kwargs(entity, name):
    kwargs = {k: v for k, v in entity.__dict__.items() if not k.startswith('__')}
    if name in ['curve', 'surface']:
        default_kwargs = name2kwargs[name][(FACTORY, entity.name)]
    else:
        default_kwargs = name2kwargs[name][FACTORY]
    if 'kwargs' not in kwargs:
        kwargs['kwargs'] = copy.deepcopy(default_kwargs)
    if name in ['structure_curve']:
        if 'nPoints' in kwargs['kwargs'] and FACTORY == 'occ':
            kwargs['kwargs']['numNodes'] = kwargs['kwargs'].pop('nPoints')
        if isinstance(kwargs['kwargs']['meshType'], int):
            kwargs['kwargs']['meshType'] = TRANSFINITE_CURVE_TYPES[kwargs['kwargs']['meshType']]
    kwargs['kwargs'] = {k: v for k, v in kwargs['kwargs'].items()
                        if k in default_kwargs}
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
        wireTags=[x.tag for x in surface['curves_loops']],
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


def register_point(point):
    for i, c in enumerate(point.coordinates):
        point.coordinates[i] = round(c, POINT_TOL)
    key = tuple(point.coordinates)
    tag = POINTS.get(key, None)
    if tag is None:
        point_kwargs = correct_kwargs(point, 'point')
        if USE_REGISTRY_TAG:
            global POINT_TAG
            point_kwargs['kwargs']['tag'] = POINT_TAG
            tag = add_point[FACTORY](point_kwargs)
            POINT_TAG += 1
        else:
            point_kwargs['kwargs']['tag'] = -1
            tag = add_point[FACTORY](point_kwargs)
        POINTS[key] = tag
    point.tag = tag
    return point


def register_curve(curve):
    name = curve.name
    ps = [x.tag for x in curve.points]
    key = tuple([name] + ps)
    tag = CURVES.get(key, None)
    if tag is None:
        curve_kwargs = correct_kwargs(curve, 'curve')
        if USE_REGISTRY_TAG:
            global CURVE_TAG
            curve_kwargs['kwargs']['tag'] = CURVE_TAG
            tag = add_curve[(FACTORY, name)](curve_kwargs)
            CURVE_TAG += 1
        else:
            curve_kwargs['kwargs']['tag'] = -1
            tag = add_curve[(FACTORY, name)](curve_kwargs)
        CURVES[key] = tag
        rev_key = tuple([name] + list(reversed(ps)))
        CURVES[rev_key] = -tag
    curve.tag = tag
    return curve


def register_curve_loop(curve_loop):
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
        curve_loop_kwargs = correct_kwargs(curve_loop, 'curve_loop')
        curve_loop_kwargs['curves_tags'] = curves
        if USE_REGISTRY_TAG:
            global CURVE_LOOP_TAG
            curve_loop_kwargs['kwargs']['tag'] = CURVE_LOOP_TAG
            tag = add_curve_loop[FACTORY](curve_loop_kwargs)
            CURVE_LOOP_TAG += 1
        else:
            curve_loop_kwargs['kwargs']['tag'] = -1
            tag = add_curve_loop[FACTORY](curve_loop_kwargs)
        for k in keys:
            CURVES_LOOPS[k] = tag
    curve_loop.tag = tag
    return curve_loop


def register_surface(surface):
    name = surface.name
    key = tuple(x.tag for x in surface.curves_loops)
    tag = SURFACES.get(key, None)
    if tag is None:
        surface_kwargs = correct_kwargs(surface, 'surface')
        if USE_REGISTRY_TAG:
            global SURFACE_TAG
            surface_kwargs['kwargs']['tag'] = SURFACE_TAG
            # t0 = time.perf_counter()  # FIXME Too long in occ factory!
            tag = add_surface[(FACTORY, name)](surface_kwargs)
            # print(time.perf_counter() - t0)
            SURFACE_TAG += 1
            # FIXME Workaround occ auto increment curve loop and surface tags
            if FACTORY == 'occ':
                global CURVE_LOOP_TAG
                CURVE_LOOP_TAG += 1
        else:
            surface_kwargs['kwargs']['tag'] = -1
            # t0 = time.perf_counter()  # FIXME Too long in occ factory!
            tag = add_surface[(FACTORY, name)](surface_kwargs)
            # print(time.perf_counter() - t0)
        SURFACES[key] = tag
    surface.tag = tag
    return surface


def register_surface_loop(surface_loop):
    key = tuple(x.tag for x in surface_loop.surfaces)  # TODO use deque? 12x more keys
    tag = SURFACES_LOOPS.get(key, None)
    if tag is None:
        surface_loop_kwargs = correct_kwargs(surface_loop, 'surface_loop')
        surface_loop_kwargs['surfaces_tags'] = key
        # FIXME Workaround of occ returns only -1 tag
        if USE_REGISTRY_TAG or FACTORY == 'occ':
            global SURFACE_LOOP_TAG
            surface_loop_kwargs['kwargs']['tag'] = SURFACE_LOOP_TAG
            tag = add_surface_loop[FACTORY](surface_loop_kwargs)
            SURFACE_LOOP_TAG += 1
        else:
            surface_loop_kwargs['kwargs']['tag'] = -1
            tag = add_surface_loop[FACTORY](surface_loop_kwargs)
        SURFACES_LOOPS[key] = tag
    surface_loop.tag = tag
    return surface_loop


def register_volume(volume):
    key = tuple(x.tag for x in volume.surfaces_loops)
    tag = VOLUMES.get(key, None)
    if tag is None:
        volume_kwargs = correct_kwargs(volume, 'volume')
        if USE_REGISTRY_TAG:
            global VOLUME_TAG
            volume_kwargs['kwargs']['tag'] = VOLUME_TAG
            tag = add_volume[FACTORY](volume_kwargs)
            VOLUME_TAG += 1
        else:
            volume_kwargs['kwargs']['tag'] = -1
            tag = add_volume[FACTORY](volume_kwargs)
        VOLUMES[key] = tag
    volume.tag = tag
    return volume


def register_quadrate_surface(surface):
    if surface.quadrate is None:
        return surface
    tag = surface.tag
    if tag not in QUADRATED_SURFACES:
        rec = correct_kwargs(surface.quadrate, 'quadrate')
        rec['kwargs']['dim'] = 2
        rec['kwargs']['tag'] = tag
        add_quadrate[FACTORY](rec)
        QUADRATED_SURFACES.add(tag)
    return surface


def register_structure_curve(curve):
    if curve.structure is None:
        return curve
    tag = curve.tag
    if tag not in STRUCTURED_CURVES:
        tr = correct_kwargs(curve.structure, 'structure_curve')
        tr['kwargs']['tag'] = tag
        add_structure_curve[FACTORY](tr)
        STRUCTURED_CURVES.add(tag)
    return curve


def register_structure_surface(surface):
    if surface.structure is None:
        return surface
    tag = surface.tag
    if tag not in STRUCTURED_SURFACES:
        tr = correct_kwargs(surface.structure, 'structure_surface')
        tr['kwargs']['tag'] = tag
        add_structure_surface[FACTORY](tr)
        STRUCTURED_SURFACES.add(tag)
    return surface


def register_structure_volume(volume):
    if volume.structure is None:
        return volume
    tag = volume.tag
    if tag not in STRUCTURED_VOLUMES:
        tr = correct_kwargs(volume.structure, 'structure_volume')
        tr['kwargs']['tag'] = tag
        add_structure_volume[FACTORY](tr)
        STRUCTURED_VOLUMES.add(tag)
    return volume


def pre_unregister_volume(volume):
    tag = volume.tag
    UNREGISTERED_VOLUMES.add(tag)
    volume.tag = None
    return volume


def unregister_volumes():
    gmsh.model.removeEntities([(3, x) for x in UNREGISTERED_VOLUMES],
                              recursive=True)


def get_unregistered_volumes():
    return UNREGISTERED_VOLUMES


def register_curve_structure(points, structure):
    # TODO Using only first and last points
    # key = tuple(y for x in points for y in x.coordinates)
    key = tuple(y for x in [points[0], points[-1]] for y in x.coordinates)
    # CURVE_STRUCTURE.setdefault(key, structure)
    CURVE_STRUCTURE.setdefault(key, structure)


def register_surface_structure(points, structure):
    if len(points) != 4:
        return
    key = tuple(y for x in points for y in x.coordinates)
    SURFACE_STRUCTURE.setdefault(key, structure)


# def register_volume_structure(points, structure):
#     if len(points) != 8:
#         return
#     key = tuple(y for x in points for y in x.coordinates)
#     VOLUME_STRUCTURE.setdefault(key, structure)


def register_volume_structure(tag, structure):
    VOLUME_STRUCTURE.setdefault(tag, structure)


def register_surface_quadrate(points, quadrate):
    if len(points) != 4:
        return
    key = tuple(y for x in points for y in x.coordinates)
    SURFACE_QUADRATE.setdefault(key, quadrate)


def get_curve_structure(points):
    # TODO Using only first and last points
    # p = deque(points)
    p = deque([points[0], points[1]])
    for _ in range(len(p)):
        key = tuple(y for x in p for y in x.coordinates)
        structure = CURVE_STRUCTURE.get(key, None)
        if structure is not None:
            return structure
        p.rotate(1)
    return None


def get_surface_structure(points):
    if len(points) != 4:
        return None
    for p in permutations(points):
        key = tuple(y for x in p for y in x.coordinates)
        structure = SURFACE_STRUCTURE.get(key, None)
        if structure is not None:
            return structure
    return None


# def get_volume_structure(points):
#     if len(points) != 8:
#         return None
#     for p in permutations(points):
#         key = tuple(y for x in p for y in x.coordinates)
#         structure = VOLUME_STRUCTURE.get(key, None)
#         if structure is not None:
#             return structure
#     return None


def get_volume_structure(tag):
    return VOLUME_STRUCTURE.get(tag, None)


def get_surface_quadrate(points):
    if len(points) != 4:
        return None
    for p in permutations(points):
        key = tuple(y for x in p for y in x.coordinates)
        structure = SURFACE_QUADRATE.get(key, None)
        if structure is not None:
            return structure
    return None


def register_boolean_new2olds(m):
    global BOOLEAN_NEW2OLDS
    BOOLEAN_NEW2OLDS = m


def register_boolean_old2news(m):
    global BOOLEAN_OLD2NEWS
    BOOLEAN_OLD2NEWS = m


def get_boolean_new2olds():
    return BOOLEAN_NEW2OLDS


def get_boolean_old2news():
    return BOOLEAN_OLD2NEWS


def register_volume2block(volume_tag, block):
    VOLUME2BLOCK[volume_tag] = block


def get_volume2block():
    return VOLUME2BLOCK


def synchronize():
    if FACTORY == 'geo':
        gmsh.model.geo.synchronize()
    elif FACTORY == 'occ':
        gmsh.model.occ.synchronize()
    else:
        raise ValueError(FACTORY)
