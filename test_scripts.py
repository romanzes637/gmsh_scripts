import unittest
import os
import json
import itertools
import math
import time
from pprint import pprint

import gmsh

from complex_factory import ComplexFactory
from environment import Environment
from boolean import complex_by_volumes, complex_by_complex, \
    primitive_by_complex, primitive_by_volumes, \
    primitive_by_primitive, sort_object_only_shared_tool_no_shared, \
    sort_object_only_shared_no_tool
from io import read_complex_type_1, read_complex_type_2, \
    read_complex_type_2_to_complex_primitives, write_json, \
    read_json
from complex_primitive import ComplexPrimitive
from occ_workarounds import correct_and_transfinite_primitive, \
    correct_and_transfinite_complex, \
    correct_and_transfinite_and_recombine_complex
from primitive import Primitive
from cylinder import Cylinder
from divided_cylinder import DividedCylinder
from support import auto_primitive_points_sizes_min_curve, \
    auto_complex_points_sizes_min_curve, \
    auto_complex_points_sizes_min_curve_in_volume, \
    auto_primitive_points_sizes_min_curve_in_volume, \
    volumes_surfaces_to_volumes_groups_surfaces, auto_volumes_groups_surfaces, \
    auto_points_sizes, \
    structure_cuboid, is_cuboid, get_volumes_geometry, check_geometry, \
    boundary_surfaces_to_six_side_groups, check_file


class TestScripts(unittest.TestCase):
    def test_primitive(self):
        """
        Test Primitive
        """
        gmsh.initialize()
        gmsh.option.setNumber("General.Terminal", 1)
        # Geometry.AutoCoherence has no effect at gmsh.model.occ factory
        gmsh.option.setNumber('Geometry.AutoCoherence', 0)
        model_name = 'test_primitive'
        gmsh.model.add(model_name)
        print('Input')
        input_file_name = '_'.join(['input', model_name + '.json'])
        file_path = os.path.join('input', input_file_name)
        result = check_file(file_path)
        with open(result['path']) as f:
            d = json.load(f)
        pprint(d)
        if d['arguments']['factory'] == 'occ':
            factory = gmsh.model.occ
        else:
            factory = gmsh.model.geo
        print('Initialize')
        primitive = Primitive(**d['arguments'])
        print('Synchronize')
        factory.synchronize()
        print('Evaluate')
        primitive.evaluate_coordinates()  # for correct and transfinite
        primitive.evaluate_bounding_box()  # for boolean
        print('Remove All Duplicates')
        factory.removeAllDuplicates()
        print('Synchronize')
        factory.synchronize()
        print("Correct and Transfinite")
        ss = set()
        cs = set()
        correct_and_transfinite_primitive(primitive, ss, cs)
        print("Physical")
        vs = primitive.volumes
        tag = gmsh.model.addPhysicalGroup(3, vs)
        gmsh.model.setPhysicalName(3, tag, primitive.physical_name)
        for i, s in enumerate(primitive.surfaces):
            tag = gmsh.model.addPhysicalGroup(2, [s])
            gmsh.model.setPhysicalName(2, tag, primitive.surfaces_names[i])
        print('Mesh')
        gmsh.model.mesh.generate(3)
        gmsh.model.mesh.removeDuplicateNodes()
        gmsh.write(model_name + ".msh")
        gmsh.finalize()

    def test_cylinder(self):
        """
        Test Cylinder
        """
        gmsh.initialize()
        gmsh.option.setNumber("General.Terminal", 1)
        gmsh.option.setNumber('Geometry.AutoCoherence',
                              0)  # No effect at gmsh.model.occ factory
        model_name = 'test_cylinder'
        gmsh.model.add(model_name)
        print('Input')
        input_file_name = '_'.join(['input', model_name + '.json'])
        file_path = os.path.join('input', input_file_name)
        result = check_file(file_path)
        with open(result['path']) as f:
            d = json.load(f)
        pprint(d)
        if d['arguments']['factory'] == 'occ':
            factory = gmsh.model.occ
        else:
            factory = gmsh.model.geo
        print('Initialize')
        cylinder = Cylinder(**d['arguments'])
        print('Synchronize')
        factory.synchronize()
        print('Evaluate')
        cylinder.evaluate_coordinates()  # for correct and transfinite
        cylinder.evaluate_bounding_box()  # for boolean
        print('Remove All Duplicates')
        factory.removeAllDuplicates()
        print('Synchronize')
        factory.synchronize()
        print('Correct and Transfinite')
        ss = set()
        cs = set()
        correct_and_transfinite_complex(cylinder, ss, cs)
        print('Physical')
        for name in cylinder.map_physical_name_to_primitives_indices.keys():
            vs = cylinder.get_volumes_by_physical_name(name)
            tag = gmsh.model.addPhysicalGroup(3, vs)
            gmsh.model.setPhysicalName(3, tag, name)
        print("Mesh")
        gmsh.model.mesh.generate(3)
        gmsh.model.mesh.removeDuplicateNodes()
        gmsh.write(model_name + ".msh")
        gmsh.finalize()

    def test_divided_cylinder(self):
        """
        Test DividedCylinder
        """
        gmsh.initialize()
        gmsh.option.setNumber("General.Terminal", 1)
        gmsh.option.setNumber('Geometry.AutoCoherence',
                              0)  # No effect at gmsh.model.occ factory
        model_name = 'test_divided_cylinder'
        gmsh.model.add(model_name)
        print('Input')
        input_file_name = '_'.join(['input', model_name + '.json'])
        file_path = os.path.join('input', input_file_name)
        result = check_file(file_path)
        print(result['path'])
        with open(result['path']) as f:
            d = json.load(f)
        pprint(d)
        if d['arguments']['factory'] == 'occ':
            factory = gmsh.model.occ
        else:
            factory = gmsh.model.geo
        print('Initialize')
        cylinder = DividedCylinder(**d['arguments'])
        print('Synchronize')
        factory.synchronize()
        print('Evaluate')
        cylinder.evaluate_coordinates()  # for correct and transfinite
        cylinder.evaluate_bounding_box()  # for boolean
        print('Remove All Duplicates')
        factory.removeAllDuplicates()
        print('Synchronize')
        factory.synchronize()
        print('Correct and Transfinite')
        ss = set()
        cs = set()
        correct_and_transfinite_complex(cylinder, ss, cs)
        print('Physical')
        for name in cylinder.map_physical_name_to_primitives_indices.keys():
            vs = cylinder.get_volumes_by_physical_name(name)
            tag = gmsh.model.addPhysicalGroup(3, vs)
            gmsh.model.setPhysicalName(3, tag, name)
        print("Mesh")
        gmsh.model.mesh.generate(3)
        gmsh.model.mesh.removeDuplicateNodes()
        gmsh.write(model_name + ".msh")
        gmsh.finalize()

    def test_complex_primitive(self):
        """
        Test ComplexPrimitive
        """
        gmsh.initialize()
        gmsh.option.setNumber("General.Terminal", 1)
        gmsh.option.setNumber('Geometry.AutoCoherence',
                              0)  # No effect at gmsh.model.occ factory
        model_name = 'test_complex_primitive'
        gmsh.model.add(model_name)
        print('Input')
        input_file_name = '_'.join(['input', model_name + '.json'])
        file_path = os.path.join('input', input_file_name)
        result = check_file(file_path)
        with open(result['path']) as f:
            d = json.load(f)
        pprint(d)
        if d['arguments']['factory'] == 'occ':
            factory = gmsh.model.occ
        else:
            factory = gmsh.model.geo
        print('Initialize')
        cp = ComplexPrimitive(**d['arguments'])
        print('Synchronize')
        factory.synchronize()
        print('Evaluate')
        cp.evaluate_coordinates()  # for correct and transfinite
        cp.evaluate_bounding_box()  # for boolean
        print('Remove All Duplicates')
        factory.removeAllDuplicates()
        print('Synchronize')
        factory.synchronize()
        print('Correct and Transfinite')
        ss = set()
        cs = set()
        print(correct_and_transfinite_complex(cp, ss, cs))
        print('Physical')
        for name in cp.map_physical_name_to_primitives_indices.keys():
            vs = cp.get_volumes_by_physical_name(name)
            tag = gmsh.model.addPhysicalGroup(3, vs)
            gmsh.model.setPhysicalName(3, tag, name)
        print("Mesh")
        gmsh.model.mesh.generate(3)
        gmsh.model.mesh.removeDuplicateNodes()
        gmsh.write(model_name + ".msh")
        gmsh.finalize()

    def test_boolean(self):
        """
        Test complex boolean
        """
        # FIXME bug with input_test_environment.json "divide_data":
        # [1, 1, 1] then boolean at complex_by_volumes(factory, c1, evs,
        # remove_tool=False, sort_function=sort_object_only_shared_no_tool)
        model_name = "test_boolean"
        gmsh.initialize()
        gmsh.option.setNumber("General.Terminal", 1)
        gmsh.option.setNumber("Mesh.Algorithm3D", 1)
        gmsh.model.add(model_name)
        print('Input')
        input_file_name = '_'.join(['input', model_name + '.json'])
        file_path = os.path.join('input', input_file_name)
        result = check_file(file_path)
        print(result['path'])
        with open(result['path']) as f:
            d = json.load(f)
        pprint(d)
        is_test_mode = d['arguments']['test_mode']
        is_simple_environment = d['arguments']['simple_environment']
        is_simple_first = d['arguments']['simple_first']
        is_simple_second = d['arguments']['simple_second']
        is_simple_boundary = d['arguments']['simple_boundary']
        is_recombine = d['arguments']['recombine']
        with open(d['arguments']['first_complex_path']) as f1:
            d1 = json.load(f1)
        if is_simple_first:
            d1['arguments']["divide_data"] = [1, 1, 1]
        pprint(d1)
        with open(d['arguments']['second_complex_path']) as f2:
            d2 = json.load(f2)
        if is_simple_second:
            d2['arguments']["divide_data"] = [1, 1, 1]
        pprint(d2)
        with open(d['arguments']['environment_complex_path']) as fe:
            de = json.load(fe)
        if is_simple_environment:
            de['arguments']["divide_data"] = [1, 1, 1]
        pprint(de)
        if d['arguments']['factory'] == 'occ':
            factory = gmsh.model.occ
        else:
            factory = gmsh.model.geo
        print('Initialize')
        c1 = ComplexFactory.new(d1)
        c2 = ComplexFactory.new(d2)
        e = ComplexFactory.new(de)
        print('Synchronize')
        factory.synchronize()
        print('Evaluate')
        c1.evaluate_coordinates()  # for correct and transfinite
        c1.evaluate_bounding_box()  # for boolean
        c2.evaluate_coordinates()  # for correct and transfinite
        c2.evaluate_bounding_box()  # for boolean
        e.evaluate_coordinates()  # for correct and transfinite
        e.evaluate_bounding_box()  # for boolean
        if not is_test_mode:
            print("Boolean")
            print("First by Second")
            complex_by_complex(factory, c1, c2)
            if not is_simple_environment:
                print("Environment Volumes")
                evs = e.get_volumes()
                print("First by Environment Volumes")
                complex_by_volumes(factory, c1, evs, remove_tool=False,
                                   sort_function=sort_object_only_shared_no_tool)
                print("Second by Environment Volumes")
                complex_by_volumes(factory, c2, evs, remove_tool=False,
                                   sort_function=sort_object_only_shared_no_tool)
                print("Environment by First")
                complex_by_complex(factory, e, c1)
                print("Environment by Second")
                complex_by_complex(factory, e, c2)
            else:
                print("First By Environment")
                complex_by_complex(factory, c1, e,
                                   sort_function=sort_object_only_shared_tool_no_shared,
                                   pre_boolean=False)
                print("Second By Environment")
                complex_by_complex(factory, c2, e,
                                   sort_function=sort_object_only_shared_tool_no_shared,
                                   pre_boolean=False)
            print("Remove Duplicates")
            factory.removeAllDuplicates()
            print('Synchronize')
            factory.synchronize()
            print("Set Sizes")
            pss = dict()
            auto_complex_points_sizes_min_curve_in_volume(c1, pss)
            auto_complex_points_sizes_min_curve_in_volume(c2, pss)
            auto_complex_points_sizes_min_curve_in_volume(e, pss)
        if is_recombine:
            print("Correct and Transfinite and Recombine")
            cs = set()
            ss = set()
            correct_and_transfinite_and_recombine_complex(c1, ss, cs)
            correct_and_transfinite_and_recombine_complex(c2, ss, cs)
            correct_and_transfinite_and_recombine_complex(e, ss, cs)
        else:
            print("Correct and Transfinite")
            cs = set()
            ss = set()
            correct_and_transfinite_complex(c1, ss, cs)
            correct_and_transfinite_complex(c2, ss, cs)
            correct_and_transfinite_complex(e, ss, cs)
        print("Physical")
        print("First")
        for name in c1.map_physical_name_to_primitives_indices.keys():
            vs = c1.get_volumes_by_physical_name(name)
            tag = gmsh.model.addPhysicalGroup(3, vs)
            gmsh.model.setPhysicalName(3, tag, name)
        print("Second")
        for name in c2.map_physical_name_to_primitives_indices.keys():
            vs = c2.get_volumes_by_physical_name(name)
            tag = gmsh.model.addPhysicalGroup(3, vs)
            gmsh.model.setPhysicalName(3, tag, name)
        print("Environment")
        for name in e.map_physical_name_to_primitives_indices.keys():
            vs = e.get_volumes_by_physical_name(name)
            tag = gmsh.model.addPhysicalGroup(3, vs)
            gmsh.model.setPhysicalName(3, tag, name)
        if not is_test_mode:
            print('Surfaces')
            boundary_surfaces_groups = boundary_surfaces_to_six_side_groups()
            if not is_simple_boundary:
                map_surface_to_physical_name = dict()
                print("First")
                for physical_name in c1.map_physical_name_to_primitives_indices:
                    surfaces = c1.get_surfaces_by_physical_name(physical_name)
                    for s in surfaces:
                        map_surface_to_physical_name[s] = physical_name
                print("Second")
                for physical_name in c2.map_physical_name_to_primitives_indices:
                    surfaces = c2.get_surfaces_by_physical_name(physical_name)
                    for s in surfaces:
                        map_surface_to_physical_name[s] = physical_name
                print("Environment")
                for physical_name in e.map_physical_name_to_primitives_indices:
                    surfaces = e.get_surfaces_by_physical_name(physical_name)
                    for s in surfaces:
                        map_surface_to_physical_name[s] = physical_name
                for i, (name, ss) in enumerate(
                        boundary_surfaces_groups.items()):
                    map_expanded_physical_name_to_surfaces = dict()
                    for s in ss:
                        physical_name = '_'.join(
                            [name, map_surface_to_physical_name[s]])
                        map_expanded_physical_name_to_surfaces.setdefault(
                            physical_name, list()).append(s)
                    for j, (epn, ess) in enumerate(
                            map_expanded_physical_name_to_surfaces.items()):
                        tag = gmsh.model.addPhysicalGroup(2, ess)
                        gmsh.model.setPhysicalName(2, tag, epn)
            else:
                for i, (name, ss) in enumerate(
                        boundary_surfaces_groups.items()):
                    tag = gmsh.model.addPhysicalGroup(2, ss)
                    gmsh.model.setPhysicalName(2, tag, name)
        print('Mesh')
        gmsh.model.mesh.generate(3)
        gmsh.model.mesh.removeDuplicateNodes()
        gmsh.write(model_name + ".msh")
        gmsh.finalize()

    def test_read_complex_primitives_json(self):
        """
        Test read ComplexPrimitives json
        """
        gmsh.initialize()
        gmsh.option.setNumber('General.Terminal', 1)
        # (1=Delaunay, 2=New Delaunay, 4=Frontal, 5=Frontal Delaunay, 6=Frontal Hex, 7=MMG3D, 9=R-tree)
        gmsh.option.setNumber("Mesh.Algorithm3D", 4)
        model_name = 'test_complex_primitives'
        gmsh.model.add(model_name)
        factory = gmsh.model.occ
        print('Read')
        read_json(factory, os.path.join('input', model_name + '.json'))
        print("Remove Duplicates")
        factory.removeAllDuplicates()
        print('Synchronize')
        factory.synchronize()
        print('Sizes')
        sizes = auto_points_sizes(10000)
        pprint(sizes)
        print('Structure')
        structured_surfaces = set()
        structured_edges = dict()
        structured_volumes = set()
        volumes_dim_tags = gmsh.model.getEntities(3)
        for vdt in volumes_dim_tags:
            volume = vdt[1]
            result = is_cuboid(volume)
            if result:
                structured_volumes.add(volume)
                structure_cuboid(volume, structured_surfaces, structured_edges,
                                 5, 0.0001)
        pprint(structured_edges)
        pprint(structured_surfaces)
        pprint(structured_volumes)
        print('Mesh')
        gmsh.model.mesh.generate(3)
        gmsh.model.mesh.removeDuplicateNodes()
        gmsh.write(model_name + '.msh')
        gmsh.finalize()

    def test_read_complex_type_2_to_complex_primitives_json(self):
        """
        Test read complex type 2 to ComplexPrimitives to json
        """
        gmsh.initialize()
        gmsh.option.setNumber("General.Terminal", 1)
        model_name = 'test_complex_primitives'
        gmsh.model.add(model_name)
        factory = gmsh.model.occ
        print('Read')
        complex_primitives = read_complex_type_2_to_complex_primitives(
            factory,
            'Fractures_Peter/fracture_N=2_fmt=8f.txt',
            [1, 2, 1],
            1,
            [0, 0, 0],
            [[5, 0, 1], [5, 0, 1], [5, 0, 1]],
            "ComplexPrimitive"
        )
        print('Synchronize')
        factory.synchronize()
        for cp in complex_primitives:
            cp.evaluate_bounding_box()  # for boolean
        print('Boolean')
        combinations = list(
            itertools.combinations(range(len(complex_primitives)), 2))
        for i, c in enumerate(combinations):
            print(
                'Boolean: {}/{} (CP {} by CP {})'.format(i, len(combinations),
                                                         c[0],
                                                         c[1]))
            complex_by_complex(factory, complex_primitives[c[0]],
                               complex_primitives[c[1]])
        print('Remove all duplicates')
        factory.removeAllDuplicates()
        print('Synchronize')
        factory.synchronize()
        print('Check geometry')
        geo = get_volumes_geometry()
        check_geometry(geo)
        print('Write')
        write_json(model_name + '.json')
        gmsh.finalize()

    def test_read_json_boolean(self):
        gmsh.initialize()
        gmsh.option.setNumber('General.Terminal', 1)
        model_name = 'test_json_boolean'
        gmsh.model.add(model_name)
        factory = gmsh.model.occ
        print('Read')
        read_json(factory, model_name + '.json')
        print("Remove Duplicates")
        factory.removeAllDuplicates()
        print('Synchronize')
        factory.synchronize()
        print('Sizes')
        sizes = auto_points_sizes()
        pprint(sizes)
        print('Mesh')
        gmsh.model.mesh.generate(3)
        gmsh.model.mesh.removeDuplicateNodes()
        gmsh.write(model_name + '.msh')
        gmsh.finalize()

    def test_write_json_boolean(self):
        gmsh.initialize()
        gmsh.option.setNumber('General.Terminal', 1)
        model_name = 'test_json_boolean'
        gmsh.model.add(model_name)
        factory = gmsh.model.occ
        factory_str = 'occ'
        print('Geometry')
        primitive1 = Primitive(
            factory_str,
            [
                [5, 10, -15, 5],
                [-5, 10, -15, 5],
                [-5, -10, -15, 5],
                [5, -10, -15, 5],
                [5, 10, 15, 5],
                [-5, 10, 15, 5],
                [-5, -10, 15, 5],
                [5, -10, 15, 5],
            ],
            [0, 0, 0, 0, 0, 0, 0, 0, 0],
            [5, 0, 0, 0, 0, 0, 0, 1, 0, 0, 1, 0],
            # [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [
                [
                    [-2, 20, -20, 1],
                    [-1, 20, -20, 1],
                    [1, 20, -20, 1],
                    [2, 20, -20, 1]
                ],
                [],
                [],
                [],
                [],
                [],
                [],
                [[0, 0, 0, 0]],
                [],
                [],
                [[0, 0, 0, 0], [0, 0, 0, 0]],
                []
            ],
            [[5, 0, 1], [10, 0, 1], [15, 0, 1]],
            0,
            'Primitive'
        )
        primitive2 = Primitive(
            factory_str,
            [
                [5, 10, -15, 5],
                [-5, 10, -15, 5],
                [-5, -10, -15, 5],
                [5, -10, -15, 5],
                [5, 10, 15, 5],
                [-5, 10, 15, 5],
                [-5, -10, 15, 5],
                [5, -10, 15, 5],
            ],
            [3, 0, 0, 0, 0, 0, 3.14 / 4, 3.14 / 6, 3.14 / 8],
            # [3, 4, 5, 0, 0, 0, 0, 0, 0],
            [5, 0, 0, 0, 0, 0, 0, 1, 0, 0, 1, 0],
            # [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [
                [
                    [-2, 20, -20, 1],
                    [-1, 20, -20, 1],
                    [1, 20, -20, 1],
                    [2, 20, -20, 1]
                ],
                [],
                [],
                [],
                [],
                [],
                [],
                [[0, 0, 0, 0]],
                [],
                [],
                [[0, 0, 0, 0], [0, 0, 0, 0]],
                []
            ],
            [[5, 0, 1], [10, 0, 1], [15, 0, 1]],
            0,
            'Primitive2'
        )
        print('Boolean')
        primitive_by_primitive(factory, primitive1, primitive2)
        print("Remove Duplicates")
        factory.removeAllDuplicates()
        print('Synchronize')
        factory.synchronize()
        print('Write')
        write_json(model_name + '.json')
        print('Sizes')
        sizes = auto_points_sizes()
        pprint(sizes)
        print('Mesh')
        gmsh.model.mesh.generate(3)
        gmsh.model.mesh.removeDuplicateNodes()
        gmsh.write(model_name + '.msh')
        gmsh.finalize()

    def test_read_json(self):
        gmsh.initialize()
        gmsh.option.setNumber('General.Terminal', 1)
        model_name = 'test_json'
        gmsh.model.add(model_name)
        factory = gmsh.model.occ
        print('Read')
        read_json(factory, model_name + '.json')
        print('Synchronize')
        factory.synchronize()
        print('Mesh')
        gmsh.model.mesh.generate(3)
        gmsh.model.mesh.removeDuplicateNodes()
        gmsh.write(model_name + '.msh')
        gmsh.finalize()

    def test_write_json(self):
        gmsh.initialize()
        gmsh.option.setNumber('General.Terminal', 1)
        model_name = 'test_json'
        gmsh.model.add(model_name)
        factory = gmsh.model.occ
        factory_str = 'occ'
        print('Geometry')
        primitive = Primitive(
            factory_str,
            [
                [5, 10, -15, 5],
                [-5, 10, -15, 5],
                [-5, -10, -15, 5],
                [5, -10, -15, 5],
                [5, 10, 15, 5],
                [-5, 10, 15, 5],
                [-5, -10, 15, 5],
                [5, -10, 15, 5],
            ],
            [0, 0, 0, 0, 0, 0, 3.14 / 4, 3.14 / 6, 3.14 / 8],
            [5, 0, 0, 0, 0, 0, 0, 1, 0, 0, 1, 0],
            [
                [
                    [-2, 20, -20, 1],
                    [-1, 20, -20, 1],
                    [1, 20, -20, 1],
                    [2, 20, -20, 1]
                ],
                [],
                [],
                [],
                [],
                [],
                [],
                [[0, 0, 0, 0]],
                [],
                [],
                [[0, 0, 0, 0], [0, 0, 0, 0]],
                []
            ],
            [[5, 0, 1], [10, 0, 1], [15, 0, 1]],
            0,
            'Primitive'
        )
        print('Synchronize')
        factory.synchronize()
        print('Write')
        write_json(model_name + '.json')
        print('Mesh')
        gmsh.model.mesh.generate(3)
        gmsh.model.mesh.removeDuplicateNodes()
        gmsh.write(model_name + '.msh')
        gmsh.finalize()

    def test_import_brep_and_structured_cuboid(self):
        gmsh.initialize()
        gmsh.option.setNumber("Geometry.AutoCoherence",
                              0)  # No effect at gmsh.model.occ factory
        gmsh.option.setNumber("General.Terminal", 1)
        # (1=Delaunay, 2=New Delaunay, 4=Frontal, 5=Frontal Delaunay, 6=Frontal Hex, 7=MMG3D, 9=R-tree)
        gmsh.option.setNumber("Mesh.Algorithm3D", 1)
        model_name = 'test_import_brep_and_structured_cuboid'
        gmsh.model.add(model_name)
        factory = gmsh.model.occ
        vdts = factory.importShapes(
            'test_read_complex_type_2_to_complex_primitives.brep')
        pprint(vdts)
        print("Remove Duplicates")
        # factory.removeAllDuplicates()
        print('Synchronize')
        factory.synchronize()
        print('Structure')
        ss = set()
        for vdt in vdts:
            result = is_cuboid(vdt[1])
            if result:
                structure_cuboid(vdt[1], ss, 3, 0.001)
        # sizes = auto_points_sizes(1000)
        # print(sizes)
        print("Physical")
        # vdts = gmsh.model.getEntities(3)
        # for i, vdt in enumerate(vdts):
        #     tag = gmsh.model.addPhysicalGroup(3, [vdt[1]])
        #     gmsh.model.setPhysicalName(3, tag, 'V{}'.format(i))
        # sdts = gmsh.model.getBoundary([vdt])
        # for j, sdt in enumerate(sdts):
        #     tag = gmsh.model.addPhysicalGroup(2, [sdt[1]])
        #     gmsh.model.setPhysicalName(2, tag, 'V{}S{}'.format(i, j))
        gmsh.model.mesh.generate(3)
        gmsh.model.mesh.removeDuplicateNodes()
        gmsh.write(model_name + '.msh')
        gmsh.finalize()

    def test_structured_cuboid(self):
        gmsh.initialize()
        gmsh.option.setNumber('General.Terminal', 1)
        model_name = 'test_structured_cuboid'
        gmsh.model.add(model_name)
        factory = gmsh.model.occ
        factory_str = 'occ'
        primitive = Primitive(
            factory_str,
            [
                [5, 10, -15, 5],
                [-5, 10, -15, 5],
                [-5, -10, -15, 5],
                [5, -10, -15, 5],
                [5, 10, 15, 5],
                [-5, 10, 15, 5],
                [-5, -10, 15, 5],
                [5, -10, 15, 5],
            ],
            [0, 0, 0, 0, 0, 0, 3.14 / 4, 3.14 / 6, 3.14 / 8],
            [5, 0, 0, 0, 0, 0, 0, 1, 0, 0, 1, 0],
            [
                [
                    [-2, 20, -20, 1],
                    [-1, 20, -20, 1],
                    [1, 20, -20, 1],
                    [2, 20, -20, 1]
                ],
                [],
                [],
                [],
                [],
                [],
                [],
                [[0, 0, 0, 0]],
                [],
                [],
                [[0, 0, 0, 0], [0, 0, 0, 0]],
                []
            ],
            [
                [5, 0, 1],
                [5, 0, 1],
                [5, 0, 1],
                [5, 0, 1],
                [10, 0, 1],
                [10, 0, 1],
                [10, 0, 1],
                [10, 0, 1],
                [15, 0, 1],
                [15, 0, 1],
                [15, 0, 1],
                [15, 0, 1]
            ],
            0,
            'Primitive'
        )
        print('Synchronize')
        factory.synchronize()
        print('Check Cuboid')
        result = is_cuboid(primitive.volumes[0])
        print(result)
        print('Make Structured Cuboid')
        ss = set()
        structure_cuboid(primitive.volumes[0], ss, 10, 0.8)
        print("Physical")
        vdts = gmsh.model.getEntities(3)
        for i, vdt in enumerate(vdts):
            tag = gmsh.model.addPhysicalGroup(3, [vdt[1]])
            gmsh.model.setPhysicalName(3, tag, 'V{}'.format(i))
            sdts = gmsh.model.getBoundary([vdt])
            for j, sdt in enumerate(sdts):
                tag = gmsh.model.addPhysicalGroup(2, [sdt[1]])
                gmsh.model.setPhysicalName(2, tag, 'V{}S{}'.format(i, j))
        print('Mesh')
        gmsh.model.mesh.generate(3)
        gmsh.model.mesh.removeDuplicateNodes()
        gmsh.write(model_name + '.msh')
        gmsh.finalize()

    def test_import_brep(self):
        gmsh.initialize()
        gmsh.option.setNumber('General.Terminal', 1)
        model_name = 'test_import_brep'
        gmsh.model.add(model_name)
        factory = gmsh.model.occ
        dts = factory.importShapes(
            'test_read_complex_type_2_to_complex_primitives.brep')
        pprint(dts)
        factory.synchronize()
        sizes = auto_points_sizes(0.5)
        print(sizes)
        gmsh.model.mesh.generate(3)
        gmsh.model.mesh.removeDuplicateNodes()
        gmsh.write(model_name + '.msh')
        gmsh.finalize()

    def test_auto_points_sizes(self):
        gmsh.initialize()
        gmsh.option.setNumber('General.Terminal', 1)
        model_name = 'test_auto_points_sizes'
        gmsh.model.add(model_name)
        factory = gmsh.model.occ
        factory_str = 'occ'
        primitive = Primitive(
            factory_str,
            [
                [5, 10, -15, 1],
                [-5, 10, -15, 1],
                [-5, -10, -15, 1],
                [5, -10, -15, 1],
                [5, 10, 15, 1],
                [-5, 10, 15, 1],
                [-5, -10, 15, 1],
                [5, -10, 15, 1],
            ],
            [5, 5, 6, 0, 0, 0, 3.14 / 4, 3.14 / 6, 3.14 / 8],
            [5, 0, 0, 0, 0, 0, 0, 1, 0, 0, 1, 0],
            [
                [
                    [-2, 20, -20, 1],
                    [-1, 20, -20, 1],
                    [1, 20, -20, 1],
                    [2, 20, -20, 1]
                ],
                [],
                [],
                [],
                [],
                [],
                [],
                [[0, 0, 0, 0]],
                [],
                [],
                [[0, 0, 0, 0], [0, 0, 0, 0]],
                []
            ],
            [
                [5, 0, 1],
                [5, 0, 1],
                [5, 0, 1],
                [5, 0, 1],
                [10, 0, 1],
                [10, 0, 1],
                [10, 0, 1],
                [10, 0, 1],
                [15, 0, 1],
                [15, 0, 1],
                [15, 0, 1],
                [15, 0, 1]
            ],
            1,
            'Primitive'
        )
        factory.synchronize()
        sizes = auto_points_sizes(0.5)
        pprint(sizes)
        gmsh.model.mesh.generate(3)
        gmsh.model.mesh.removeDuplicateNodes()
        gmsh.write(model_name + '.msh')
        gmsh.finalize()

    def test_boundary(self):
        gmsh.initialize()
        gmsh.option.setNumber('General.Terminal', 1)
        model_name = 'test_boolean'
        gmsh.model.add(model_name)
        factory = gmsh.model.occ
        factory_str = 'occ'
        primitive = Primitive(
            factory_str,
            [
                [5, 10, -15, 5],
                [-5, 10, -15, 5],
                [-5, -10, -15, 5],
                [5, -10, -15, 5],
                [5, 10, 15, 5],
                [-5, 10, 15, 5],
                [-5, -10, 15, 5],
                [5, -10, 15, 5],
            ],
            [0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [[], [], [], [], [], [], [], [], [], [], [], []],
            [
                [5, 0, 1], [5, 0, 1], [5, 0, 1], [5, 0, 1],
                [10, 0, 1], [10, 0, 1], [10, 0, 1], [10, 0, 1],
                [15, 0, 1], [15, 0, 1], [15, 0, 1], [15, 0, 1]
            ],
            0,
            'Primitive'
        )
        factory.synchronize()
        print('All Volumes')
        volume_dts = gmsh.model.getEntities(3)
        print(volume_dts)
        for vdt in volume_dts:
            print(type(vdt))
            print(type(vdt[0]))
            print(type(vdt[1]))
            print('Volume {} surfaces'.format(vdt[1]))
            print('Combined')
            ss_dts = gmsh.model.getBoundary([vdt])
            print(ss_dts)
            print('Combined Tuple')
            ss_dts = gmsh.model.getBoundary([(vdt[0], vdt[1])])
            print(ss_dts)
            print('Uncombined')
            ss_dts = gmsh.model.getBoundary([vdt], combined=False)
            print(ss_dts)
            print('Uncombined Tuple')
            ss_dts = gmsh.model.getBoundary([(vdt[0], vdt[1])], combined=False)
            print(ss_dts)
        print('All Surfaces')
        ss_dts = gmsh.model.getEntities(2)
        print(ss_dts)
        for sdt in ss_dts:
            print('Surface {} lines'.format(sdt[1]))
            print('Combined')
            ls_dts = gmsh.model.getBoundary([sdt])
            print(ls_dts)
            print('Combined Tuple')
            ls_dts = gmsh.model.getBoundary([(sdt[0], sdt[1])])
            print(ls_dts)
            print('Uncombined')
            ls_dts = gmsh.model.getBoundary([sdt], combined=False)
            print(ls_dts)
            print('Uncombined Tuple')
            ls_dts = gmsh.model.getBoundary([(sdt[0], sdt[1])], combined=False)
            print(ls_dts)
        print('All Lines')
        ls_dts = gmsh.model.getEntities(1)
        print(ls_dts)
        for ldt in ls_dts:
            print('Line {} points'.format(ldt[1]))
            print('Combined')
            ps_dts = gmsh.model.getBoundary([ldt])
            print(ps_dts)
            print('Combined Tuple')
            ps_dts = gmsh.model.getBoundary([(ldt[0], ldt[1])])
            print(ps_dts)
            print('Uncombined')
            ps_dts = gmsh.model.getBoundary([ldt], combined=False)
            print(ps_dts)
            print('Uncombined Tuple')
            ps_dts = gmsh.model.getBoundary([(ldt[0], ldt[1])], combined=False)
            print(ps_dts)
        print('All Points')
        ps_dts = gmsh.model.getEntities(0)
        print(ps_dts)
        gmsh.finalize()

    def test_extend(self):
        n = int(1e4)
        m = int(1e4)
        item = range(m)
        print('Number of items:\t\t{}'.format(n))
        print('Item length:\t\t{}'.format(m))
        # Append Direct
        start_time = time.time()
        a = list()
        for i in range(n):
            for x in item:
                a.append(x)
        for x in a:  # Some operation
            pass
        print("Append Direct:\t\t{:.3f}s".format(time.time() - start_time))
        # Append + Comprehension
        start_time = time.time()
        a2 = list()
        for i in range(n):
            a2.append(item)
        flatten_a2 = [x for y in a2 for x in y]
        for x in flatten_a2:  # Some operation
            pass
        print("Append+Comprehension:\t{:.3f}s".format(time.time() - start_time))
        # Append + Chain
        start_time = time.time()
        a3 = list()
        for i in range(n):
            a3.append(item)
        flatten_a3 = list(itertools.chain.from_iterable(a3))
        for x in flatten_a3:  # Some operation
            pass
        print("Append+ListChain:\t{:.3f}s".format(time.time() - start_time))
        # Extend3
        start_time = time.time()
        e = list()
        for i in range(n):
            e.extend(item)
        for x in e:  # Some operation
            pass
        print("Extend:\t\t\t{:.3f}s".format(time.time() - start_time))
        # Extend Operator
        start_time = time.time()
        eo = list()
        for i in range(n):
            eo += item
        for x in eo:  # Some operation
            pass
        print("Extend Operator:\t{:.3f}s".format(time.time() - start_time))
        # Append + Append Chain
        start_time = time.time()
        a4 = list()
        for i in range(n):
            a4.append(item)
        for x in itertools.chain.from_iterable(a4):  # Some operation
            pass
        print("Append+Chain:\t\t{:.3f}s".format(time.time() - start_time))
        # Set + Update
        start_time = time.time()
        a5 = set()
        for i in range(n):
            a5.update(item)
        flatten_a5 = list(a5)
        for x in flatten_a5:  # Some operation
            pass
        print("Set+Update:\t\t{:.3f}s".format(time.time() - start_time))
        # Set + Union
        start_time = time.time()
        a6 = set()
        for i in range(n):
            a6.union(item)
        flatten_a6 = list(a6)
        for x in flatten_a6:  # Some operation
            pass
        print("Set+Union:\t\t{:.3f}s".format(time.time() - start_time))
        # self.assertItemsEqual(a, flatten_a2)
        # self.assertItemsEqual(a, flatten_a3)
        # self.assertItemsEqual(a, e)
        # self.assertItemsEqual(a, eo)

    def test_boolean_gmsh(self):
        gmsh.initialize()
        gmsh.option.setNumber('General.Terminal', 1)
        model_name = 'test_boolean_gmsh'
        gmsh.model.add(model_name)
        factory = gmsh.model.occ
        factory_str = 'occ'
        times = dict()
        booleans = {
            'Fuse': lambda objects, tools: factory.fuse(objects, tools),
            'Cut': lambda objects, tools: factory.cut(objects, tools),
            'Intersect': lambda objects, tools: factory.intersect(objects,
                                                                  tools),
            'Fragment': lambda objects, tools: factory.fragment(objects, tools),
            'FuseRemoveFalse': lambda objects, tools: factory.fuse(
                objects, tools, removeObject=False, removeTool=False),
            'CutRemoveFalse': lambda objects, tools: factory.cut(
                objects, tools, removeObject=False, removeTool=False),
            'IntersectRemoveFalse': lambda objects, tools: factory.intersect(
                objects, tools, removeObject=False, removeTool=False),
            'FragmentRemoveFalse': lambda objects, tools: factory.fragment(
                objects, tools, removeObject=False, removeTool=False),
        }
        print('Creation')
        primitives = list()
        for i, (k, v) in enumerate(booleans.items()):
            print(i)
            print(k)
            # print(v)
            obj = Primitive(
                factory_str,
                [
                    [5, 10, -15, 5],
                    [-5, 10, -15, 5],
                    [-5, -10, -15, 5],
                    [5, -10, -15, 5],
                    [5, 10, 15, 5],
                    [-5, 10, 15, 5],
                    [-5, -10, 15, 5],
                    [5, -10, 15, 5],
                ],
                [i * 30, 0, 0, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                [[], [], [], [], [], [], [], [], [], [], [], []],
                [
                    [5, 0, 1], [5, 0, 1], [5, 0, 1], [5, 0, 1],
                    [10, 0, 1], [10, 0, 1], [10, 0, 1], [10, 0, 1],
                    [15, 0, 1], [15, 0, 1], [15, 0, 1], [15, 0, 1]
                ],
                0,
                '{}Obj'.format(k)
            )
            tool = Primitive(
                factory_str,
                [
                    [5, 10, -15, 5],
                    [-5, 10, -15, 5],
                    [-5, -10, -15, 5],
                    [5, -10, -15, 5],
                    [5, 10, 15, 5],
                    [-5, 10, 15, 5],
                    [-5, -10, 15, 5],
                    [5, -10, 15, 5],
                ],
                [i * 30 + 5, 10, 15, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                [[], [], [], [], [], [], [], [], [], [], [], []],
                [
                    [5, 0, 1], [5, 0, 1], [5, 0, 1], [5, 0, 1],
                    [10, 0, 1], [10, 0, 1], [10, 0, 1], [10, 0, 1],
                    [15, 0, 1], [15, 0, 1], [15, 0, 1], [15, 0, 1]
                ],
                0,
                '{}Tool'.format(k)
            )
            primitives.append(obj)
            primitives.append(tool)
            start_time = time.time()
            out, out_map = booleans[k]([(3, obj.volumes[0])],
                                       [(3, tool.volumes[0])])
            times[k] = time.time() - start_time
            print(out)
            print(out_map)
            # print('Synchronize')
            # factory.synchronize()
            # for j, dt in enumerate(out):
            #     tag = gmsh.model.addPhysicalGroup(dt[0], [dt[1]])
            #     gmsh.model.setPhysicalName(3, tag, '{}{}'.format(k, j))
        print('Synchronize')
        factory.synchronize()
        print('Entities')
        vs = gmsh.model.getEntities(3)
        ss = gmsh.model.getEntities(2)
        ps = gmsh.model.getEntities(1)
        print('vs: {}, ss: {}, ps: {}'.format(len(vs), len(ss), len(ps)))
        print('Remove All Duplicates')
        start_time = time.time()
        factory.removeAllDuplicates()
        times['RemoveAllDuplicates'] = time.time() - start_time
        print('Synchronize')
        factory.synchronize()
        print('Entities')
        vs = gmsh.model.getEntities(3)
        ss = gmsh.model.getEntities(2)
        ps = gmsh.model.getEntities(1)
        print('vs: {}, ss: {}, ps: {}'.format(len(vs), len(ss), len(ps)))
        print('Physical')
        vs = gmsh.model.getEntities(3)  # all model volumes
        print('Number of volumes: {}'.format(len(vs)))
        for i, dt in enumerate(vs):
            tag = gmsh.model.addPhysicalGroup(3, [dt[1]])
            gmsh.model.setPhysicalName(3, tag, 'V{}'.format(i))
        gmsh.model.mesh.generate(3)
        gmsh.model.mesh.removeDuplicateNodes()
        gmsh.write(model_name + '.msh')
        gmsh.finalize()
        pprint(times)

    def test_factories(self):
        """
        Attempt to combine GEO and OCC factories (failed)
        """
        gmsh.initialize()
        gmsh.option.setNumber('Geometry.AutoCoherence',
                              0)  # No effect at gmsh.model.occ factory
        gmsh.option.setNumber('General.Terminal', 1)
        gmsh.model.add('test_factories')
        factory_occ = gmsh.model.occ
        factory_geo = gmsh.model.geo
        factory_occ_str = 'occ'
        factory_geo_str = 'geo'
        print('Creation')
        print("Primitive GEO")
        primitive_geo = Primitive(
            factory_geo_str,
            [
                [5, 10, -15, 5],
                [-5, 10, -15, 5],
                [-5, -10, -15, 5],
                [5, -10, -15, 5],
                [5, 10, 15, 5],
                [-5, 10, 15, 5],
                [-5, -10, 15, 5],
                [5, -10, 15, 5],
            ],
            [0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [[], [], [], [], [], [], [], [], [], [], [], []],
            [
                [5, 0, 1], [5, 0, 1], [5, 0, 1], [5, 0, 1],
                [10, 0, 1], [10, 0, 1], [10, 0, 1], [10, 0, 1],
                [15, 0, 1], [15, 0, 1], [15, 0, 1], [15, 0, 1]
            ],
            0,
            "PrimitiveGEO"
        )
        print("Synchronize")
        factory_geo.synchronize()
        print("Primitive OCC")
        primitive_occ = Primitive(
            factory_occ_str,
            [
                [5, 10, -15, 5],
                [-5, 10, -15, 5],
                [-5, -10, -15, 5],
                [5, -10, -15, 5],
                [5, 10, 15, 5],
                [-5, 10, 15, 5],
                [-5, -10, 15, 5],
                [5, -10, 15, 5],
            ],
            [50, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [[], [], [], [], [], [], [], [], [], [], [], []],
            [
                [5, 0, 1], [5, 0, 1], [5, 0, 1], [5, 0, 1],
                [10, 0, 1], [10, 0, 1], [10, 0, 1], [10, 0, 1],
                [15, 0, 1], [15, 0, 1], [15, 0, 1], [15, 0, 1]
            ],
            0,
            "PrimitiveOCC"
        )
        print("Synchronize")
        factory_occ.synchronize()
        print("Evaluate PrimitiveOCC Coordinates")
        primitive_occ.evaluate_coordinates()
        print("Correct and Transfinite")
        ss = set()
        cs = set()
        print(primitive_geo.transfinite(ss, cs))
        print(correct_and_transfinite_primitive(primitive_occ, ss, cs))
        print("Physical")
        tag = gmsh.model.addPhysicalGroup(3, primitive_geo.volumes)
        gmsh.model.setPhysicalName(3, tag, primitive_geo.physical_name)
        tag = gmsh.model.addPhysicalGroup(3, primitive_occ.volumes)
        gmsh.model.setPhysicalName(3, tag, primitive_occ.physical_name)
        gmsh.model.mesh.generate(3)
        gmsh.model.mesh.removeDuplicateNodes()
        gmsh.write("test_factories.msh")
        gmsh.finalize()

    def test_transfinite(self):
        gmsh.initialize()
        gmsh.option.setNumber("Geometry.AutoCoherence",
                              0)  # No effect at gmsh.model.occ factory
        gmsh.option.setNumber("General.Terminal", 1)
        gmsh.model.add("test_transfinite")
        factory = gmsh.model.geo
        factory_str = 'geo'
        print("Creation")
        start = time.time()
        primitives = []
        for i in range(4):
            primitives.append(Primitive(
                factory_str,
                [
                    [5, 10, -15, 1],
                    [-5, 10, -15, 1],
                    [-5, -10, -15, 1],
                    [5, -10, -15, 1],
                    [5, 10, 15, 1],
                    [-5, 10, 15, 1],
                    [-5, -10, 15, 1],
                    [5, -10, 15, 1],
                ],
                [30 + i * 15, 0, 0, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                [
                    [
                        [-2, 20, -20, 1],
                        [-1, 20, -20, 1],
                        [1, 20, -20, 1],
                        [2, 20, -20, 1]
                    ],
                    [],
                    [],
                    [],
                    [],
                    [],
                    [],
                    [[0, 0, 0, 0]],
                    [],
                    [],
                    [[0, 0, 0, 0], [0, 0, 0, 0]],
                    []
                ],
                [
                    [5, 0, 1],
                    [5, 0, 1],
                    [5, 0, 1],
                    [5, 0, 1],
                    [10, 0, 1],
                    [10, 0, 1],
                    [10, 0, 1],
                    [10, 0, 1],
                    [15, 0, 1],
                    [15, 0, 1],
                    [15, 0, 1],
                    [15, 0, 1]
                ],
                i
            ))
        for i in range(4):
            primitives.append(Primitive(
                factory_str,
                [
                    [10, 5, -15, 1],
                    [-10, 5, -15, 1],
                    [-10, -5, -15, 1],
                    [10, -5, -15, 1],
                    [10, 5, 15, 1],
                    [-10, 5, 15, 1],
                    [-10, -5, 15, 1],
                    [10, -5, 15, 1],
                ],
                [0, 30 + i * 15, 0, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                [
                    [
                        [-2, 20, -20, 1],
                        [-1, 20, -20, 1],
                        [1, 20, -20, 1],
                        [2, 20, -20, 1]
                    ],
                    [],
                    [],
                    [],
                    [],
                    [],
                    [],
                    [[0, 0, 0, 0]],
                    [],
                    [],
                    [[0, 0, 0, 0], [0, 0, 0, 0]],
                    []
                ],
                [
                    [10, 0, 1],
                    [10, 0, 1],
                    [10, 0, 1],
                    [10, 0, 1],
                    [5, 0, 1],
                    [5, 0, 1],
                    [5, 0, 1],
                    [5, 0, 1],
                    [15, 0, 1],
                    [15, 0, 1],
                    [15, 0, 1],
                    [15, 0, 1]
                ],
                i
            ))
        for i in range(4):
            primitives.append(Primitive(
                factory_str,
                [
                    [15, 10, -5, 1],
                    [-15, 10, -5, 1],
                    [-15, -10, -5, 1],
                    [15, -10, -5, 1],
                    [15, 10, 5, 1],
                    [-15, 10, 5, 1],
                    [-15, -10, 5, 1],
                    [15, -10, 5, 1],
                ],
                [0, 0, 30 + i * 15, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                [
                    [
                        [-2, 20, -20, 1],
                        [-1, 20, -20, 1],
                        [1, 20, -20, 1],
                        [2, 20, -20, 1]
                    ],
                    [],
                    [],
                    [],
                    [],
                    [],
                    [],
                    [[0, 0, 0, 0]],
                    [],
                    [],
                    [[0, 0, 0, 0], [0, 0, 0, 0]],
                    []
                ],
                [
                    [15, 0, 1],
                    [15, 0, 1],
                    [15, 0, 1],
                    [15, 0, 1],
                    [10, 0, 1],
                    [10, 0, 1],
                    [10, 0, 1],
                    [10, 0, 1],
                    [5, 0, 1],
                    [5, 0, 1],
                    [5, 0, 1],
                    [5, 0, 1]
                ],
                i
            ))
        print('{:.3f}s'.format(time.time() - start))
        print("Synchronize")
        factory.synchronize()
        print("Evaluate Coordinates")
        # start = time.time()
        # for p in primitives:
        #     p.evaluate_coordinates()
        # print('{:.3f}s'.format(time.time() - start))
        # print("Correct")
        # start = time.time()
        # for p in primitives:
        #     result = occ_ws.correct_primitive(p)
        #     print(result)
        print('{:.3f}s'.format(time.time() - start))
        print("Transfinite")
        start = time.time()
        ss = set()
        cs = set()
        for p in primitives:
            result = p.transfinite(ss, cs)
            print(result)
        print('{:.3f}s'.format(time.time() - start))
        print("Physical")
        for i, p in enumerate(primitives):
            tag = gmsh.model.addPhysicalGroup(3, p.volumes)
            gmsh.model.setPhysicalName(3, tag, "V{}".format(i))
            for j, s in enumerate(p.surfaces):
                tag = gmsh.model.addPhysicalGroup(2, [s])
                gmsh.model.setPhysicalName(2, tag,
                                           "{}{}".format(p.surfaces_names[j],
                                                         i))
        gmsh.model.mesh.generate(3)
        gmsh.model.mesh.removeDuplicateNodes()
        gmsh.write("test_transfinite.msh")
        gmsh.finalize()

    def test_boundary_surfaces(self):
        """
        Cylinder boundary surfaces
        """
        gmsh.initialize()
        # No effect at gmsh.model.occ factory
        gmsh.option.setNumber("Geometry.AutoCoherence", 0)
        gmsh.option.setNumber("General.Terminal", 1)
        model_name = "test_boundary_surfaces"
        gmsh.model.add(model_name)
        factory = gmsh.model.occ
        factory_str = 'occ'
        print("Cylinder")
        cylinder = Cylinder(
            factory_str,
            [10, 20, 30],
            [10, 20, 30],
            [[5, 5, 5], [7, 7, 7], [9, 9, 9]],
            [0, 0, 0, 0, 0, 0, 0, 0, 0],
            [["V0", "V1", "V2"], ["V3", "V4", "V5"], ["V6", "V7", "V8"]],
            [[3, 0, 1], [4, 0, 1], [5, 0, 1]],
            [[3, 0, 1], [4, 0, 1], [5, 0, 1]],
            [5, 0, 1]
        )
        print("Remove All Duplicates")
        factory.removeAllDuplicates()
        print("Synchronize")
        factory.synchronize()
        print("Universal Way")  # Doesn't works with many inner volumes
        v_dts = gmsh.model.getEntities(3)  # all model volumes
        print(len(v_dts))
        bs_dts = gmsh.model.getBoundary(v_dts)  # all model volumes boundary
        print(len(bs_dts))
        bs_u = map(lambda x: x[1], bs_dts)
        s_dts = gmsh.model.getEntities(2)  # all model surfaces boundary
        print(len(s_dts))
        print(bs_u)
        print("Good Way")
        vgs_ss = auto_volumes_groups_surfaces()
        print(vgs_ss)
        gmsh.finalize()

    def test_environment(self):
        """
        Cylinder in Environment
        """
        gmsh.initialize()
        # No effect at gmsh.model.occ factory
        gmsh.option.setNumber("Geometry.AutoCoherence", 0)
        gmsh.option.setNumber("General.Terminal", 1)
        # 1: Delaunay, 4: Frontal, 5: Frontal Delaunay, 6: Frontal Hex,
        # 7: MMG3D, 9: R-tree, 10: HXT
        gmsh.option.setNumber("Mesh.Algorithm3D", 1)
        model_name = "test_environment"
        gmsh.model.add(model_name)
        factory = gmsh.model.geo
        factory_str = 'geo'
        print("Primitive 1")
        primitive = Primitive(
            factory_str,
            [
                [5, 10, -15, 5],
                [-5, 10, -15, 5],
                [-5, -10, -15, 5],
                [5, -10, -15, 5],
                [5, 10, 15, 5],
                [-5, 10, 15, 5],
                [-5, -10, 15, 5],
                [5, -10, 15, 5],
            ],
            [0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [[], [], [], [], [], [], [], [], [], [], [], []],
            [
                [5, 0, 1], [5, 0, 1], [5, 0, 1], [5, 0, 1],
                [10, 0, 1], [10, 0, 1], [10, 0, 1], [10, 0, 1],
                [15, 0, 1], [15, 0, 1], [15, 0, 1], [15, 0, 1]
            ],
            0,
            "P1"
        )
        print("Primitive 2")
        primitive2 = Primitive(
            factory_str,
            [
                [5, 10, -15, 5],
                [-5, 10, -15, 5],
                [-5, -10, -15, 5],
                [5, -10, -15, 5],
                [5, 10, 15, 5],
                [-5, 10, 15, 5],
                [-5, -10, 15, 5],
                [5, -10, 15, 5],
            ],
            [-10, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [[], [], [], [], [], [], [], [], [], [], [], []],
            [
                [5, 0, 1], [5, 0, 1], [5, 0, 1], [5, 0, 1],
                [10, 0, 1], [10, 0, 1], [10, 0, 1], [10, 0, 1],
                [15, 0, 1], [15, 0, 1], [15, 0, 1], [15, 0, 1]
            ],
            0,
            "P2"
        )
        print("Primitive 3")
        primitive3 = Primitive(
            factory_str,
            [
                [5, 10, -15, 5],
                [-5, 10, -15, 5],
                [-5, -10, -15, 5],
                [5, -10, -15, 5],
                [5, 10, 15, 5],
                [-5, 10, 15, 5],
                [-5, -10, 15, 5],
                [5, -10, 15, 5],
            ],
            [-30, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [[], [], [], [], [], [], [], [], [], [], [], []],
            [
                [5, 0, 1], [5, 0, 1], [5, 0, 1], [5, 0, 1],
                [10, 0, 1], [10, 0, 1], [10, 0, 1], [10, 0, 1],
                [15, 0, 1], [15, 0, 1], [15, 0, 1], [15, 0, 1]
            ],
            0,
            "P3"
        )
        print("Cylinder")
        cylinder = Cylinder(
            factory_str,
            [10, 20, 30],
            [10, 20, 30],
            [[5, 5, 5], [7, 7, 7], [9, 9, 9]],
            [70, 0, 0, 0, 0, 0, 0, 0, 0],
            [["V0", "V1", "V2"], ["V3", "V4", "V5"], ["V6", "V7", "V8"]],
            [[3, 0, 1], [4, 0, 1], [5, 0, 1]],
            [[3, 0, 1], [4, 0, 1], [5, 0, 1]],
            [5, 0, 1]
        )
        print("Synchronize")
        factory.synchronize()
        print("Evaluate")
        cylinder.evaluate_coordinates()  # for correct and transfinite
        primitive.evaluate_coordinates()
        primitive2.evaluate_coordinates()
        primitive3.evaluate_coordinates()
        print("Remove All Duplicates")
        factory.removeAllDuplicates()
        print("Synchronize")
        factory.synchronize()
        print("Volumes Surfaces")
        vgs_ss = auto_volumes_groups_surfaces()
        # print(vgs_ss)
        print("Environment")
        environment = Environment(
            factory_str,
            300,
            300,
            300,
            50,
            [0, 0, 0, 0, 0, 0, 0, 0, 0],
            vgs_ss
        )
        print("Synchronize")
        factory.synchronize()
        print("Correct and Transfinite")
        ss = set()
        cs = set()
        correct_and_transfinite_complex(cylinder, ss, cs)
        print(correct_and_transfinite_primitive(primitive, ss, cs))
        print(correct_and_transfinite_primitive(primitive2, ss, cs))
        print(correct_and_transfinite_primitive(primitive3, ss, cs))
        print('Recombine')
        primitive.recombine()
        primitive2.recombine()
        primitive3.recombine()
        cylinder.recombine()
        print("Physical")
        tag = gmsh.model.addPhysicalGroup(3, primitive.volumes)
        gmsh.model.setPhysicalName(3, tag, primitive.physical_name)
        tag = gmsh.model.addPhysicalGroup(3, primitive2.volumes)
        gmsh.model.setPhysicalName(3, tag, primitive2.physical_name)
        tag = gmsh.model.addPhysicalGroup(3, primitive3.volumes)
        gmsh.model.setPhysicalName(3, tag, primitive3.physical_name)
        for name in cylinder.map_physical_name_to_primitives_indices.keys():
            vs = cylinder.get_volumes_by_physical_name(name)
            tag = gmsh.model.addPhysicalGroup(3, vs)
            gmsh.model.setPhysicalName(3, tag, name)
        tag = gmsh.model.addPhysicalGroup(3, environment.volumes)
        gmsh.model.setPhysicalName(3, tag, environment.physical_name)
        volumes_dim_tags = map(lambda x: (3, x), environment.volumes)
        surfaces_dim_tags = gmsh.model.getBoundary(volumes_dim_tags,
                                                   combined=False)
        if factory is not gmsh.model.geo:
            surfaces_names = ["X", "NY", "NX", "Y", "NZ", "Z"]
        else:
            surfaces_names = ["NX", "X", "NY", "Y", "NZ", "Z"]
        for i, n in enumerate(surfaces_names):
            tag = gmsh.model.addPhysicalGroup(surfaces_dim_tags[i][0],
                                              [surfaces_dim_tags[i][1]])
            gmsh.model.setPhysicalName(2, tag, n)
        print("Mesh")
        gmsh.model.mesh.generate(3)
        gmsh.model.mesh.removeDuplicateNodes()
        print("Write")
        gmsh.write(model_name + ".msh")
        gmsh.finalize()

    def test_read_complex_type_2(self):
        """
        Test read Complex Type 2
        """
        gmsh.initialize()
        gmsh.option.setNumber("General.Terminal", 1)
        # 1=Delaunay, 2=New Delaunay, 4=Frontal,
        # 5=Frontal Delaunay, 6=Frontal Hex, 7=MMG3D, 9=R-tree
        gmsh.option.setNumber("Mesh.Algorithm3D", 4)
        model_name = 'test_read_complex_type_2'
        gmsh.model.add(model_name)
        factory = gmsh.model.occ
        print('Read')
        c = read_complex_type_2(
            factory,
            'complex_type_2.json',
            1,
            [0, 0, 0],
            [[3, 0, 1], [3, 0, 1], [3, 0, 1]],
            "V"
        )
        print('Synchronize')
        factory.synchronize()
        c.evaluate_coordinates()  # for correct and transfinite
        c.evaluate_bounding_box()  # for boolean
        print('Boolean')
        c.inner_boolean()
        print('Remove all duplicates')
        factory.removeAllDuplicates()
        print('Synchronize')
        factory.synchronize()
        print('Correct and Transfinite')
        ss = set()
        cs = set()
        correct_and_transfinite_complex(c, ss, cs)
        print('Auto points sizes')
        sizes = auto_points_sizes()
        pprint(sizes)
        print('Mesh')
        gmsh.model.mesh.generate(3)
        gmsh.model.mesh.removeDuplicateNodes()
        gmsh.write(model_name + '.msh')
        gmsh.finalize()

    def test_read_complex_type_2_to_complex_primitives(self):
        """
        Test read Complex Type 2 to ComplexPrimitives
        """
        gmsh.initialize()
        gmsh.option.setNumber("Geometry.AutoCoherence",
                              0)  # No effect at gmsh.model.occ factory
        gmsh.option.setNumber("General.Terminal", 1)
        gmsh.option.setNumber("Mesh.Algorithm3D", 4)
        model_name = 'test_read_complex_type_2_to_complex_primitives'
        gmsh.model.add(model_name)
        factory = gmsh.model.occ
        print('Read')
        complex_primitives = read_complex_type_2_to_complex_primitives(
            factory,
            'complex_type_2.json',
            [2, 2, 2],
            1,
            [0, 0, 0],
            [[5, 0, 1], [5, 0, 1], [5, 0, 1]],
            "V"
        )
        print('Synchronize')
        factory.synchronize()
        for cp in complex_primitives:
            cp.evaluate_coordinates()  # for correct and transfinite
            cp.evaluate_bounding_box()  # for boolean
        print('Boolean')
        combinations = list(
            itertools.combinations(range(len(complex_primitives)), 2))
        for i, c in enumerate(combinations):
            print(
                'Boolean: {}/{} (CP {} by CP {})'.format(i, len(combinations),
                                                         c[0],
                                                         c[1]))
            complex_by_complex(factory, complex_primitives[c[0]],
                               complex_primitives[c[1]])
        print('Remove all duplicates')
        factory.removeAllDuplicates()
        print('Synchronize')
        factory.synchronize()
        print('Correct and Transfinite')
        ss = set()
        cs = set()
        for cp in complex_primitives:
            result = correct_and_transfinite_complex(cp, ss, cs)
            print(result)
        print('Auto points sizes')
        sizes = auto_points_sizes()
        pprint(sizes)
        print('Mesh')
        gmsh.model.mesh.generate(3)
        gmsh.model.mesh.removeDuplicateNodes()
        gmsh.write(model_name + '.msh')
        gmsh.finalize()

    def test_read_complex_type_2_to_complex_primitives_brep(self):
        """
        Test read Complex Type 2 to ComplexPrimitives
        """
        gmsh.initialize()
        gmsh.option.setNumber("General.Terminal", 1)
        model_name = 'test_read_complex_type_2_to_complex_primitives'
        gmsh.model.add(model_name)
        factory = gmsh.model.occ
        print('Read')
        complex_primitives = read_complex_type_2_to_complex_primitives(
            factory,
            'Fractures_Peter/fracture_N=2_fmt=8f.txt',
            [2, 2, 2],
            1,
            [0, 0, 0],
            [[5, 0, 1], [5, 0, 1], [5, 0, 1]],
            "V"
        )
        print('Synchronize')
        factory.synchronize()
        for cp in complex_primitives:
            cp.evaluate_bounding_box()  # for boolean
        print('Boolean')
        combinations = list(
            itertools.combinations(range(len(complex_primitives)), 2))
        for i, c in enumerate(combinations):
            print(
                'Boolean: {}/{} (CP {} by CP {})'.format(i, len(combinations),
                                                         c[0],
                                                         c[1]))
            complex_by_complex(factory, complex_primitives[c[0]],
                               complex_primitives[c[1]])
        print('Remove all duplicates')
        factory.removeAllDuplicates()
        print('Synchronize')
        factory.synchronize()
        gmsh.write(model_name + '.brep')
        gmsh.finalize()

    def test_read_complex_primitives(self):
        """
        Test read ComplexPrimitives
        """
        start_time = time.time()
        gmsh.initialize()
        gmsh.option.setNumber("General.Terminal", 1)
        gmsh.option.setNumber("Mesh.Algorithm3D", 4)
        gmsh.model.add("test_read_complex_primitives")
        factory = gmsh.model.occ
        factory_str = 'occ'
        int_name = "Intrusion"
        int_physical_tag = 0
        int_lc = 5
        int_center_x = 0
        int_center_y = 0
        int_center_z = 0
        int_n_x = 2
        int_n_y = 1
        int_n_z = 1
        int_tr_x = [5, 0, 1]
        int_tr_y = [5, 0, 1]
        int_tr_z = [5, 0, 1]
        int_rotation_x = math.pi / 4  # math.pi / 4
        int_rotation_y = -math.pi / 3  # -math.pi / 4
        int_rotation_z = 0
        print("Reading")
        start = time.time()
        complex_primitives = read_complex_type_2_to_complex_primitives(
            factory, "complex_type_2",
            [int_n_x, int_n_y, int_n_z],
            int_physical_tag, int_lc,
            [int_center_x, int_center_y, int_center_z],
            [int_tr_x, int_tr_y, int_tr_z])
        print('{:.3f}s'.format(time.time() - start))
        print("Creation")
        start = time.time()
        environment = Primitive(
            factory_str,
            [
                [100, 100, -100, 50],
                [-100, 100, -100, 50],
                [-100, -100, -100, 50],
                [100, -100, -100, 50],
                [100, 100, 100, 50],
                [-100, 100, 100, 50],
                [-100, -100, 100, 50],
                [100, -100, 100, 50]
            ],
            [0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [[], [], [], [], [], [], [], [], [], [], [], []]
        )
        print('{:.3f}s'.format(time.time() - start))
        print("ComplexPrimitives boolean")
        start = time.time()
        combinations = list(
            itertools.combinations(range(len(complex_primitives)), 2))
        for combination in combinations:
            print("Boolean %s by %s" % combination)
            complex_by_complex(factory, complex_primitives[combination[0]],
                               complex_primitives[combination[1]])
        print('{:.3f}s'.format(time.time() - start))
        print("Environment by Intrusion boolean")
        start = time.time()
        for cp in complex_primitives:
            primitive_by_complex(factory, environment, cp)
        print('{:.3f}s'.format(time.time() - start))
        print("Remove All Duplicates")
        start = time.time()
        factory.removeAllDuplicates()
        factory.synchronize()
        print('{:.3f}s'.format(time.time() - start))
        print("Correction and Transfinite")
        start = time.time()
        ss = set()
        cs = set()
        for cp in complex_primitives:
            correct_and_transfinite_complex(cp, ss, cs)
        print('{:.3f}s'.format(time.time() - start))
        print("Set Sizes")
        start = time.time()
        for cp in complex_primitives:
            cp.set_size()
        print('{:.3f}s'.format(time.time() - start))
        print("Physical Volumes")
        vs = []
        for cp in complex_primitives:
            vs += cp.get_volumes_by_physical_index(int_physical_tag)
        tag = gmsh.model.addPhysicalGroup(3, vs)
        gmsh.model.setPhysicalName(3, tag, int_name)
        print("Environment Physical")
        tag = gmsh.model.addPhysicalGroup(3, environment.volumes)
        gmsh.model.setPhysicalName(3, tag, "Environment")
        volumes_dim_tags = map(lambda x: (3, x), environment.volumes)
        surfaces_dim_tags = gmsh.model.getBoundary(volumes_dim_tags,
                                                   combined=False)
        surfaces_names = ["X", "Z", "NY", "NZ", "Y", "NX"]
        for i in range(len(surfaces_names)):
            tag = gmsh.model.addPhysicalGroup(surfaces_dim_tags[i][0],
                                              [surfaces_dim_tags[i][1]])
            gmsh.model.setPhysicalName(2, tag, surfaces_names[i])
            #     gmsh.model.setPhysicalName(2, tag, 'S%s' % i)
        gmsh.model.mesh.generate(3)
        gmsh.model.mesh.removeDuplicateNodes()
        gmsh.write("test_read_complex_primitives.msh")
        gmsh.finalize()
        print('\nElapsed time: {:.3f}s'.format(time.time() - start_time))

    def test_volume_points_curves_data(self):
        """
        Test auto_complex_points_sizes_min_curve_in_volume
        """
        start_time = time.time()
        model_name = "test_volume_points_curves_data"
        gmsh.initialize()
        gmsh.option.setNumber("General.Terminal", 1)
        # 1=Delaunay, 2=New Delaunay, 4=Frontal,
        #  5=Frontal Delaunay, 6=Frontal Hex, 7=MMG3D, 9=R-tree
        gmsh.option.setNumber("Mesh.Algorithm3D", 4)
        gmsh.model.add(model_name)
        factory = gmsh.model.occ
        factory_str = 'occ'
        repo_center_depth = 487.5  # repository center depth
        env_length_x = 1200
        env_length_y = 1000
        env_lc = 100
        environment = Primitive(
            factory_str,
            [
                [env_length_x / 2, env_length_y / 2, -repo_center_depth,
                 env_lc],
                [-env_length_x / 2, env_length_y / 2, -repo_center_depth,
                 env_lc],
                [-env_length_x / 2, -env_length_y / 2, -repo_center_depth,
                 env_lc],
                [env_length_x / 2, -env_length_y / 2, -repo_center_depth,
                 env_lc],
                [env_length_x / 2, env_length_y / 2, repo_center_depth, env_lc],
                [-env_length_x / 2, env_length_y / 2, repo_center_depth,
                 env_lc],
                [-env_length_x / 2, -env_length_y / 2, repo_center_depth,
                 env_lc],
                [env_length_x / 2, -env_length_y / 2, repo_center_depth, env_lc]
            ]
        )
        pss = dict()
        auto_primitive_points_sizes_min_curve_in_volume(environment, pss)
        print(pss)
        gmsh.model.mesh.generate(3)
        gmsh.model.mesh.removeDuplicateNodes()
        gmsh.write(model_name + ".msh")
        gmsh.finalize()
        print('\nElapsed time: {:.3f}s'.format(time.time() - start_time))


if __name__ == '__main__':
    unittest.main()
