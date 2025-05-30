import numpy as np

from gmsh_scripts.block.layer import Layer
from gmsh_scripts.block.matrix import Matrix
from gmsh_scripts.coordinate_system.coordinate_system import Layer as LayerCS
from gmsh_scripts.coordinate_system.coordinate_system import HalfLayer as HalfLayerCS
from gmsh_scripts.coordinate_system.coordinate_system import str2obj as cs_str2obj
from gmsh_scripts.transform.transform import str2obj as tr_str2obj
from gmsh_scripts.support.support import flatten
from gmsh_scripts.parse.parse import parse_layers2grid


class HalfLayer(Matrix):
    def __init__(
            # Layer
            self, layer=None, layer_curves=None, layer_types=None,
            items_do_register_map=None, items_do_register_children_map=None,
            items_do_register_mask=None,
            items_do_unregister_map=None,
            items_do_unregister_children_map=None,
            items_do_unregister_boolean_map=None,
            items_do_quadrate_map=None,
            items_do_structure_map=None,
            items_boolean_level_map=None,
            items_zone=None, items_zone_map=None,
            items_transforms=None, items_transforms_map=None,
            items_self_transforms=None, items_self_transforms_map=None,
            items_children=None, items_children_map=None,
            items_children_transforms=None,
            items_children_transforms_map=None,
            # Block
            points=None, curves=None, surfaces=None, volume=None,
            do_register=False, do_unregister=False,
            do_register_children=True, do_unregister_children=True,
            do_unregister_boolean=False,
            transforms=None,
            self_transforms=None,
            do_quadrate=False,
            do_structure=True, structure=None, structure_type='LLL',
            zone=None, parent=None, children=None, children_transforms=None,
            boolean_level=None, path=None
    ):
        # super().__init__(layer=layer, layer_curves=layer_curves, layer_types=layer_types,
        #                  items_do_register_map=items_do_register_map,
        #                  items_do_register_children_map=items_do_register_children_map,
        #                  items_do_register_mask=items_do_register_mask,
        #                  items_do_unregister_map=items_do_unregister_map,
        #                  items_do_unregister_children_map=items_do_unregister_children_map,
        #                  items_do_unregister_boolean_map=items_do_unregister_boolean_map,
        #                  items_do_quadrate_map=items_do_quadrate_map,
        #                  items_do_structure_map=items_do_structure_map,
        #                  items_boolean_level_map=items_boolean_level_map,
        #                  items_zone=items_zone, items_zone_map=items_zone_map,
        #                  items_transforms=items_transforms, items_transforms_map=items_transforms_map,
        #                  items_self_transforms=items_self_transforms,
        #                  items_self_transforms_map=items_self_transforms_map,
        #                  items_children=items_children, items_children_map=items_children_map,
        #                  items_children_transforms=items_children_transforms,
        #                  items_children_transforms_map=items_children_transforms_map,
        #                  points=points, curves=curves, surfaces=surfaces, volume=volume,
        #                  do_register=do_register, do_unregister=do_unregister,
        #                  do_register_children=do_register_children, do_unregister_children=do_unregister_children,
        #                  do_unregister_boolean=do_unregister_boolean,
        #                  transforms=transforms,
        #                  self_transforms=self_transforms,
        #                  do_quadrate=do_quadrate,
        #                  do_structure=do_structure, structure=structure, structure_type=structure_type,
        #                  zone=zone, parent=parent, children=children, children_transforms=children_transforms,
        #                  boolean_level=boolean_level, path=boolean_level)
        str_layers = [x for x in layer if isinstance(x, str)]
        other_layers = [x for x in layer if not isinstance(x, (int, float, str, list))]
        coordinate_system = str_layers[0] if len(str_layers) > 0 else 'Cartesian'
        coordinate_system = cs_str2obj[coordinate_system]()
        for l in other_layers:
            if isinstance(l, tuple(cs_str2obj.values())):
                coordinate_system = l
                break
        list_layers = [x for x in layer if isinstance(x, list)]
        new_layers, values, maps = parse_layers2grid(list_layers)
        parsed_layers, grid = new_layers[1], new_layers[2]
        parsed_layers_cs = [x[0] for x in values]
        n2o_l2l_l2l, n2o_l2l_g2g = maps[10], maps[11]
        g2l_b2b_l2l, g2l_b2b_g2g = maps[14], maps[15]
        parsed_g2l_b2b_l2l = maps[8]
        parsed_layers_types = Layer.parse_layers_map(layer_types, n2o_l2l_l2l,
                                                     default='in')
        parsed_layers_curves = Layer.parse_layers_map(layer_curves, n2o_l2l_l2l,
                                                      default='line')
        for i, l in enumerate(parsed_layers_curves):
            for j, c in enumerate(l):
                parsed_layers_curves[i][j] = [c] if isinstance(c, str) else c
        cs = HalfLayerCS(layers=parsed_layers_cs,
                            layers_curves=parsed_layers_curves,
                            layers_types=parsed_layers_types)
        grid.append(cs)
        # Curves
        items_curves, items_curves_map = Layer.get_layers_curves(
            parsed_layers_curves, parsed_g2l_b2b_l2l, parsed_layers_cs)
        # Boolean
        items_boolean_level_map = HalfLayer.parse_layers_block_map(
            items_boolean_level_map, None, g2l_b2b_g2g, (int,))
        # print(np.array(boolean_level_map).reshape((n_blocks_z, n_blocks_y, n_blocks_x)))
        # Register/Unregister
        items_default_do_register_map = [0 if x is None else 1
                                         for x in g2l_b2b_g2g]
        items_do_register_map = HalfLayer.parse_layers_block_map(
            items_do_register_map, 1, g2l_b2b_g2g, (bool, int))
        items_do_register_mask = 7  # 1110
        items_do_register_mask = Layer.parse_layers_block_mask(
            items_do_register_mask, 1, g2l_b2b_g2g, (bool, int), center_mask=15)
        items_do_register_children_map = HalfLayer.parse_layers_block_map(
            items_do_register_children_map, 1, g2l_b2b_g2g, (bool, int))
        items_do_unregister_map = HalfLayer.parse_layers_block_map(
            items_do_unregister_map, 0, g2l_b2b_g2g, (bool, int))
        items_do_unregister_children_map = HalfLayer.parse_layers_block_map(
            items_do_unregister_children_map, 0, g2l_b2b_g2g, (bool, int))
        items_do_unregister_boolean_map = HalfLayer.parse_layers_block_map(
            items_do_unregister_boolean_map, 0, g2l_b2b_g2g, (bool, int))
        items_do_register_map = [x*y*z for x, y, z in zip(
            items_default_do_register_map,
            items_do_register_map,
            items_do_register_mask)]
        items_do_register_children_map = [x * y for x, y in zip(
            items_default_do_register_map, items_do_register_children_map)]
        # Structure and Quadrate
        items_do_quadrate_map = HalfLayer.parse_layers_block_map(
            items_do_quadrate_map, 0, g2l_b2b_g2g, (bool, int))
        items_do_structure_map = HalfLayer.parse_layers_block_map(
            items_do_structure_map, 1, g2l_b2b_g2g, (bool, int))
        items_structure_type, items_structure_type_map = Layer.get_structure_type(
            parsed_g2l_b2b_l2l)
        # Zones
        items_zone = ['Layer'] if items_zone is None else items_zone
        items_zone_map = HalfLayer.parse_layers_block_map(items_zone_map, 0, g2l_b2b_g2g, (int,))
        # Items Transforms
        if items_transforms is None:
            items_transforms = [None]
        items_transforms_map = HalfLayer.parse_layers_block_map(
            items_transforms_map, 0, g2l_b2b_g2g, (int,))
        # Items Self Transforms
        if items_self_transforms is None:
            items_self_transforms = [None]
        lxy2car = tr_str2obj['HalfLayerToCartesian']()
        any1some = tr_str2obj['AnyAsSome'](cs_to=coordinate_system)
        some2car = tr_str2obj[f'{type(coordinate_system).__name__}ToCartesian'](
            cs_from=coordinate_system)
        item_self_transforms = [lxy2car, any1some, some2car]
        items_self_transforms = [item_self_transforms + x
                                 if x is not None else item_self_transforms
                                 for x in items_transforms]
        items_self_transforms_map = HalfLayer.parse_layers_block_map(
            items_self_transforms_map, 0, g2l_b2b_g2g, (int,))
        # Items Children
        items_children = [None] if items_children is None else items_children
        items_children_map = HalfLayer.parse_layers_block_map(
            items_children_map, 0, g2l_b2b_g2g, (int,))
        # Items Children Transforms
        if items_children_transforms is None:
            items_children_transforms = [None]
        items_children_transforms_map = HalfLayer.parse_layers_block_map(
            items_children_transforms_map, 0, g2l_b2b_g2g, (int,))
        super().__init__(
            matrix=grid,
            items_curves=items_curves,
            items_curves_map=items_curves_map,
            items_do_register_map=items_do_register_map,
            items_do_register_children_map=items_do_register_children_map,
            items_do_unregister_map=items_do_unregister_map,
            items_do_unregister_children_map=items_do_unregister_children_map,
            items_do_unregister_boolean_map=items_do_unregister_boolean_map,
            items_do_quadrate_map=items_do_quadrate_map,
            items_do_structure_map=items_do_structure_map,
            items_structure_type=items_structure_type,
            items_structure_type_map=items_structure_type_map,
            items_boolean_level_map=items_boolean_level_map,
            items_zone=items_zone,
            items_zone_map=items_zone_map,
            items_transforms=items_transforms,
            items_transforms_map=items_transforms_map,
            items_self_transforms=items_self_transforms,
            items_self_transforms_map=items_self_transforms_map,
            items_children=items_children,
            items_children_map=items_children_map,
            items_children_transforms=items_children_transforms,
            items_children_transforms_map=items_children_transforms_map,
            # Block
            points=points, curves=curves, surfaces=surfaces, volume=volume,
            do_register=do_register,
            do_register_children=do_register_children,
            do_unregister=do_unregister,
            do_unregister_children=do_unregister_children,
            do_unregister_boolean=do_unregister_boolean,
            transforms=transforms,
            self_transforms=self_transforms,
            do_quadrate=do_quadrate,
            do_structure=do_structure,
            structure=structure,
            structure_type=structure_type,
            zone=zone, parent=parent, children=children, children_transforms=children_transforms,
            boolean_level=boolean_level, path=path
        )

    @staticmethod
    def parse_layers_block_map(m, default, new2old, item_types=(), center_mask=None):
        # Default value for all items if map is None
        if m is None:
            n = [default for _ in new2old]
            return n
        m = list(flatten(m)) if isinstance(m, list) else m
        # Old list to new list
        old2new = {}
        for new, old in enumerate(new2old):
            if old is not None:
                old2new.setdefault(old[0], []).append(new)
        # Check on single item of type in item_types
        for t in item_types:
            if isinstance(t, list) and isinstance(m, list):  # list of ...
                if all(isinstance(ti, mi) for ti in t for mi in m):
                    max_old = max(x[0] for x in new2old if x is not None)
                    m = [m for _ in range(max_old + 1)]
                    break
            elif isinstance(m, t):  # non list types
                max_old = max(x[0] for x in new2old if x is not None)
                m = [m for _ in range(max_old + 1)]
                break
        n = [default for _ in new2old]
        for mi, mm in enumerate(m):
            nis = old2new[mi]
            if len(nis) == 1 and center_mask is not None:  # center
                mm = center_mask
            if isinstance(mm, str):
                if float in item_types:
                    mm = [float(x) for x in mm.split(',')]
                elif int in item_types:
                    mm = [int(x) for x in mm.split(',')]
                elif bool in item_types:
                    mm = [bool(x) for x in mm.split(',')]
                else:
                    mm = [x for x in mm.split(',')]
            else:
                mm = [mm for _ in range(4)]
            masks = [mm[2], mm[0], mm[1], mm[3]]  # NX, X, NY, Y -> NY, NX, X, Y
            if len(nis) == len(masks):  # layers
                for ni, mask in zip(nis, masks):
                    n[ni] = mask
            elif len(nis) == 1:  # center
                n[nis[0]] = masks[0]
        return n


str2obj = {
    HalfLayer.__name__: HalfLayer
}
