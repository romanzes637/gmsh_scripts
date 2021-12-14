from itertools import product
import csv
import json
import time

import gmsh

params = {
    # 'factory_type': ['geo', 'occ'],
    'factory_type': ['occ'],
    # # 'interface_type' = ['flat', 'curved'],
    'interface_type': ['curved'],
    # # 'surface_type' = ['plane', 'filling']
    'surface_type': ['filling'],
    'dx': [0.3],
    'mesh_size': [None, 1.0, 0.1],
    'mesh_size_curvature': [0, 20],
    'mesh_size_boundary': [0, 1, 2],
    'mesh_size_points': [0, 1],
    'mesh_refine': [0, 1],
    'mesh_optimize': [None, "", "Netgen",
                      "HighOrder", "HighOrderElastic", "HighOrderFastCurving",
                      "Laplace2D", "Relocate2D", "Relocate3D"],
    'mesh_optimize_number_of_iterations': [None, 1, 10]
}
prod = list(product(*params.values()))
results = []

gmsh.initialize()

cnt = 0
for values in prod:
    t0 = time.perf_counter()
    cnt += 1
    print(f'{cnt}/{len(prod)}')
    gmsh.option.setNumber('General.Terminal', 0)
    gmsh.option.setNumber('Mesh.Optimize', 0)
    gmsh.logger.start()
    factory_type, interface_type, surface_type, dx, \
    mesh_size, mesh_size_curvature, mesh_size_boundary, mesh_size_points, \
    mesh_refine, mesh_optimize, mesh_optimize_number_of_iterations = values
    ps = dict(zip(params, values))
    ps['id'] = cnt
    model_name_suffix = '__'.join(
        f'{k}-{v}' if not isinstance(v, list)
        else f'{k}-{"_".join(str(x) for x in v)}'
        for k, v in ps.items())
    model_name = "test_hex" + '__' + model_name_suffix
    file_name = f"test_hex_{cnt}"
    ps['file_name'] = file_name
    print(ps)
    if interface_type == 'curved' and surface_type == 'plane':
        continue
    if interface_type == 'curved' and dx is None:
        continue
    if interface_type == 'flat' and dx is not None:
        continue
    if mesh_optimize is None and mesh_optimize_number_of_iterations is not None:
        continue

    gmsh.model.add(model_name)

    factory = gmsh.model.geo if factory_type == 'geo' else gmsh.model.occ

    # Volume 1
    if mesh_size is not None:
        p1 = factory.addPoint(0, 0, 0, mesh_size)
        p2 = factory.addPoint(1, 0, 0, mesh_size)
        p3 = factory.addPoint(1, 1, 0, mesh_size)
        p4 = factory.addPoint(0, 1, 0, mesh_size)
        p5 = factory.addPoint(0, 0, 1, mesh_size)
        p6 = factory.addPoint(1, 0, 1, mesh_size)
        p7 = factory.addPoint(1, 1, 1, mesh_size)
        p8 = factory.addPoint(0, 1, 1, mesh_size)
    else:  # default
        p1 = factory.addPoint(0, 0, 0)
        p2 = factory.addPoint(1, 0, 0)
        p3 = factory.addPoint(1, 1, 0)
        p4 = factory.addPoint(0, 1, 0)
        p5 = factory.addPoint(0, 0, 1)
        p6 = factory.addPoint(1, 0, 1)
        p7 = factory.addPoint(1, 1, 1)
        p8 = factory.addPoint(0, 1, 1)
    l1 = factory.addLine(p1, p2)
    if interface_type == 'curved':
        l2_p1 = factory.addPoint(1. - dx, 0.3, 0)
        l2_p2 = factory.addPoint(1. + dx, 0.7, 0)
        l2 = factory.addSpline([p2, l2_p1, l2_p2, p3])
    else:
        l2 = factory.addLine(p2, p3)
    l3 = factory.addLine(p3, p4)
    l4 = factory.addLine(p4, p1)
    l5 = factory.addLine(p5, p6)
    if interface_type == 'curved':
        l6_p1 = factory.addPoint(1. + dx, 0.3, 1)
        l6_p2 = factory.addPoint(1. - dx, 0.7, 1)
        l6 = factory.addSpline([p6, l6_p1, l6_p2, p7])
    else:
        l6 = factory.addLine(p6, p7)
    l7 = factory.addLine(p7, p8)
    l8 = factory.addLine(p8, p5)
    l9 = factory.addLine(p1, p5)
    if interface_type == 'curved':
        l10_p1 = factory.addPoint(1. + dx, 0, 0.3)
        l10_p2 = factory.addPoint(1. - dx, 0, 0.7)
        l10 = factory.addSpline([p2, l10_p1, l10_p2, p6])
        l11_p1 = factory.addPoint(1. - dx, 1, 0.3)
        l11_p2 = factory.addPoint(1. + dx, 1, 0.7)
        l11 = factory.addSpline([p3, l11_p1, l11_p2, p7])
    else:
        l10 = factory.addLine(p2, p6)
        l11 = factory.addLine(p3, p7)
    l12 = factory.addLine(p4, p8)
    cl1 = factory.addCurveLoop([l1, l2, l3, l4])
    cl2 = factory.addCurveLoop([l5, l6, l7, l8])
    cl3 = factory.addCurveLoop([-l4, l12, l8, -l9])
    cl4 = factory.addCurveLoop([l2, l11, -l6, -l10])
    cl5 = factory.addCurveLoop([-l1, l9, l5, -l10])
    cl6 = factory.addCurveLoop([l3, l12, -l7, -l11])
    if surface_type == 'filling':
        s1 = factory.addSurfaceFilling([cl1] if factory_type == 'geo' else cl1)
        s2 = factory.addSurfaceFilling([cl2] if factory_type == 'geo' else cl2)
        s3 = factory.addSurfaceFilling([cl3] if factory_type == 'geo' else cl3)
        s4 = factory.addSurfaceFilling([cl4] if factory_type == 'geo' else cl4)
        s5 = factory.addSurfaceFilling([cl5] if factory_type == 'geo' else cl5)
        s6 = factory.addSurfaceFilling([cl6] if factory_type == 'geo' else cl6)
    else:
        s1 = factory.addPlaneSurface([cl1])
        s2 = factory.addPlaneSurface([cl2])
        s3 = factory.addPlaneSurface([cl3])
        s4 = factory.addPlaneSurface([cl4])
        s5 = factory.addPlaneSurface([cl5])
        s6 = factory.addPlaneSurface([cl6])
    sl1 = factory.addSurfaceLoop([s1, s2, s3, s4, s5, s6])
    # print(sl1)  # FIXME occ factory always return -1
    v1 = factory.addVolume([sl1])

    # Volume 2
    if mesh_size is not None:
        p9 = factory.addPoint(2, 0, 0, mesh_size)
        p10 = factory.addPoint(2, 1, 0, mesh_size)
        p11 = factory.addPoint(2, 0, 1, mesh_size)
        p12 = factory.addPoint(2, 1, 1, mesh_size)
    else:  # default
        p9 = factory.addPoint(2, 0, 0)
        p10 = factory.addPoint(2, 1, 0)
        p11 = factory.addPoint(2, 0, 1)
        p12 = factory.addPoint(2, 1, 1)
    l13 = factory.addLine(p2, p9)
    l14 = factory.addLine(p9, p10)
    l15 = factory.addLine(p10, p3)
    l16 = factory.addLine(p6, p11)
    l17 = factory.addLine(p11, p12)
    l18 = factory.addLine(p12, p7)
    l19 = factory.addLine(p9, p11)
    l20 = factory.addLine(p10, p12)
    cl7 = factory.addCurveLoop([l13, l14, l15, -l2])
    cl8 = factory.addCurveLoop([l16, l17, l18, -l6])
    cl9 = factory.addCurveLoop([l14, l20, -l17, -l19])
    cl10 = factory.addCurveLoop([l10, l16, -l19, -l13])
    cl11 = factory.addCurveLoop([l11, -l18, -l20, l15])
    if surface_type == 'filling':
        s7 = factory.addSurfaceFilling([cl7] if factory_type == 'geo' else cl7)
        s8 = factory.addSurfaceFilling([cl8] if factory_type == 'geo' else cl8)
        s9 = factory.addSurfaceFilling([cl9] if factory_type == 'geo' else cl9)
        s10 = factory.addSurfaceFilling([cl10] if factory_type == 'geo' else cl10)
        s11 = factory.addSurfaceFilling([cl11] if factory_type == 'geo' else cl11)
    else:
        s7 = factory.addPlaneSurface([cl7])
        s8 = factory.addPlaneSurface([cl8])
        s9 = factory.addPlaneSurface([cl9])
        s10 = factory.addPlaneSurface([cl10])
        s11 = factory.addPlaneSurface([cl11])
    sl2 = factory.addSurfaceLoop([s4, s7, s8, s9, s10, s11])
    # print(sl2)  # FIXME occ factory always return -1
    v2 = factory.addVolume([sl2])

    # Synchronize
    if factory_type == 'geo':
        gmsh.model.geo.synchronize()
    else:
        gmsh.model.occ.synchronize()

    # Physical groups
    pg1 = gmsh.model.addPhysicalGroup(2, [s1, s2, s3, s5, s6])
    gmsh.model.setPhysicalName(2, pg1, 'Boundary1')
    pg2 = gmsh.model.addPhysicalGroup(2, [s7, s8, s9, s10, s11])
    gmsh.model.setPhysicalName(2, pg2, 'Boundary2')
    pg3 = gmsh.model.addPhysicalGroup(2, [s4])
    gmsh.model.setPhysicalName(2, pg3, 'Interface')
    pg4 = gmsh.model.addPhysicalGroup(3, [v1])
    gmsh.model.setPhysicalName(3, pg4, 'Volume1')
    pg5 = gmsh.model.addPhysicalGroup(3, [v2])
    gmsh.model.setPhysicalName(3, pg5, 'Volume2')

    # Mesh
    gmsh.option.setNumber("Mesh.SubdivisionAlgorithm", 2)
    # gmsh.option.setNumber("Mesh.Algorithm", 6)
    # gmsh.option.setNumber("Mesh.Algorithm3D", 1)
    # gmsh.option.setNumber("Mesh.MeshSizeFactor", 1)
    # gmsh.option.setNumber("Mesh.MeshSizeMin", 0)
    # gmsh.option.setNumber("Mesh.MeshSizeMax", 1e20)
    gmsh.option.setNumber("Mesh.MeshSizeFromCurvature", mesh_size_curvature)
    gmsh.option.setNumber("Mesh.MeshSizeExtendFromBoundary", mesh_size_boundary)
    gmsh.option.setNumber("Mesh.MeshSizeFromPoints", mesh_size_points)
    # gmsh.option.setNumber("Mesh.MeshSizeFromCurvatureIsotropic", 0)
    # gmsh.option.setNumber("Mesh.MeshSizeFromParametricPoints", 0)
    # Generate
    try:
        gmsh.model.mesh.generate(3)
        for _ in range(mesh_refine):
            gmsh.model.mesh.refine()
        if mesh_optimize is not None and mesh_optimize_number_of_iterations is not None:
            gmsh.model.mesh.optimize(method=mesh_optimize,
                                     niter=mesh_optimize_number_of_iterations)
    except Exception as e:
        print(e)
        ps['errors'] = [str(e)]
        gmsh.finalize()
        gmsh.initialize()
    else:
        # Statistics
        ps['number_of_elements_2d'] = sum(len(x) for x in gmsh.model.mesh.get_elements(2)[1])
        ps['number_of_elements_3d'] = sum(len(x) for x in gmsh.model.mesh.get_elements(3)[1])
        # https://gmsh.info/doc/texinfo/gmsh.html#Post_002dprocessing-plugins
        gmsh.plugin.setNumber('AnalyseMeshQuality', 'JacobianDeterminant', 1)
        gmsh.plugin.setNumber('AnalyseMeshQuality', 'IGEMeasure', 1)
        gmsh.plugin.setNumber('AnalyseMeshQuality', 'ICNMeasure', 1)
        gmsh.plugin.setNumber('AnalyseMeshQuality', 'Recompute', 1)
        gmsh.plugin.setNumber('AnalyseMeshQuality', 'DimensionOfElements', -1)
        gmsh.plugin.run('AnalyseMeshQuality')
        try:
            log = gmsh.logger.get()
            for message in log:
                if any([message.startswith(x) for x in [
                    'Info: minJ', 'Info: minJ/maxJ', 'Info: IGE', 'Info: ICN']]):
                    metric = message.split('=')[0].strip()[6:]
                    vs = message.split('=')[1].split('(')[0].strip()
                    vs = [float(x.strip()) for x in vs.split(',')]
                    ks = message.split('=')[1].split('(')[1].strip(')')
                    ks = [x.strip() for x in ks.split(',')]
                    for k, v in zip(ks, vs):
                        ps[f'{metric}_{k}'] = v
            # Warnings
            log = gmsh.logger.get()
            for message in log:
                if 'Warning' in message:
                    print(message)
                    ps.setdefault('warnings', []).append(message)
        except Exception as e:
            print(e)
            ps['errors'] = [str(e)]
            gmsh.finalize()
            gmsh.initialize()
        else:
            pass
            # if 'warnings' not in ps:
            #     gmsh.write(file_name + '.msh2')
            # else:
            #     gmsh.write(file_name + '_warning' + '.msh2')
    finally:
        gmsh.logger.stop()
    ps['dt'] = time.perf_counter() - t0
    with open(file_name + '.json', 'w') as f:
        json.dump(ps, f, indent=2, sort_keys=True)
    results.append(ps)

gmsh.finalize()

keys = sorted({y for x in results for y in x.keys()})
results = [{k: x.get(k, None) for k in keys} for x in results]
with open('test_hex.csv', 'w', newline='') as f:
    dict_writer = csv.DictWriter(f, keys)
    dict_writer.writeheader()
    dict_writer.writerows(results)
