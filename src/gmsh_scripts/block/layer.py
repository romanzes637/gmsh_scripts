import numpy as np

from gmsh_scripts.block.matrix import Matrix
from gmsh_scripts.coordinate_system.coordinate_system import Layer as LayerCS
from gmsh_scripts.coordinate_system.coordinate_system import str2obj as cs_str2obj
from gmsh_scripts.transform.transform import str2obj as tr_str2obj
from gmsh_scripts.support.support import flatten
from gmsh_scripts.parse.parse import parse_layers2grid


class Layer(Matrix):
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
        cs = LayerCS(layers=parsed_layers_cs,
                     layers_curves=parsed_layers_curves,
                     layers_types=parsed_layers_types)
        grid.append(cs)
        # Curves
        items_curves, items_curves_map = Layer.get_layers_curves(
            parsed_layers_curves, parsed_g2l_b2b_l2l, parsed_layers_cs)
        # Boolean
        items_boolean_level_map = Layer.parse_layers_block_map(
            items_boolean_level_map, None, g2l_b2b_g2g, (int,))
        # print(np.array(boolean_level_map).reshape((n_blocks_z, n_blocks_y, n_blocks_x)))
        # Register/Unregister
        items_default_do_register_map = [0 if x is None else 1
                                         for x in g2l_b2b_g2g]
        items_do_register_map = Layer.parse_layers_block_map(
            items_do_register_map, 1, g2l_b2b_g2g, (bool, int))
        items_do_register_mask = Layer.parse_layers_block_mask(
            items_do_register_mask, 1, g2l_b2b_g2g, (bool, int))
        items_do_register_children_map = Layer.parse_layers_block_map(
            items_do_register_children_map, 1, g2l_b2b_g2g, (bool, int))
        items_do_unregister_map = Layer.parse_layers_block_map(
            items_do_unregister_map, 0, g2l_b2b_g2g, (bool, int))
        items_do_unregister_children_map = Layer.parse_layers_block_map(
            items_do_unregister_children_map, 0, g2l_b2b_g2g, (bool, int))
        items_do_unregister_boolean_map = Layer.parse_layers_block_map(
            items_do_unregister_boolean_map, 0, g2l_b2b_g2g, (bool, int))
        items_do_register_map = [x*y*z for x, y, z in zip(
            items_default_do_register_map,
            items_do_register_map,
            items_do_register_mask)]
        items_do_register_children_map = [x * y for x, y in zip(
            items_default_do_register_map, items_do_register_children_map)]
        # Structure and Quadrate
        items_do_quadrate_map = Layer.parse_layers_block_map(
            items_do_quadrate_map, 0, g2l_b2b_g2g, (bool, int))
        items_do_structure_map = Layer.parse_layers_block_map(
            items_do_structure_map, 1, g2l_b2b_g2g, (bool, int))
        items_structure_type, items_structure_type_map = Layer.get_structure_type(
            parsed_g2l_b2b_l2l)
        # Zones
        items_zone = ['Layer'] if items_zone is None else items_zone
        items_zone_map = Layer.parse_layers_block_map(items_zone_map, 0, g2l_b2b_g2g, (int,))
        # Items Transforms
        if items_transforms is None:
            items_transforms = [None]
        items_transforms_map = Layer.parse_layers_block_map(
            items_transforms_map, 0, g2l_b2b_g2g, (int,))
        # Items Self Transforms
        if items_self_transforms is None:
            items_self_transforms = [None]
        lxy2car = tr_str2obj['LayerToCartesian']()
        any1some = tr_str2obj['AnyAsSome'](cs_to=coordinate_system)
        some2car = tr_str2obj[f'{type(coordinate_system).__name__}ToCartesian'](
            cs_from=coordinate_system)
        item_self_transforms = [lxy2car, any1some, some2car]
        items_self_transforms = [item_self_transforms + x
                                 if x is not None else item_self_transforms
                                 for x in items_transforms]
        items_self_transforms_map = Layer.parse_layers_block_map(
            items_self_transforms_map, 0, g2l_b2b_g2g, (int,))
        # Items Children
        items_children = [None] if items_children is None else items_children
        items_children_map = Layer.parse_layers_block_map(
            items_children_map, 0, g2l_b2b_g2g, (int,))
        # Items Children Transforms
        if items_children_transforms is None:
            items_children_transforms = [None]
        items_children_transforms_map = Layer.parse_layers_block_map(
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
    def parse_layers_map(old_layers, n2o_l2l_l2l, default=None):
        new_layers_n_items = [0 for _ in range(6)]  # X, Y, NX, NY, Z, NZ
        for old_li in n2o_l2l_l2l:
            old_n_items = new_layers_n_items[old_li[0]]
            new_n_items = old_li[1] + 1
            if new_n_items > old_n_items:
                new_layers_n_items[old_li[0]] = new_n_items
        if old_layers is None:
            new_layers = [[default for _ in range(x)] for x in new_layers_n_items]
        else:
            new_layers = []
            for i in range(6):
                new_layer_items = []
                new_n_items = new_layers_n_items[i]
                for j in range(new_n_items):
                    new_li = (i, j)
                    old_li = n2o_l2l_l2l[new_li]
                    new_item = old_layers[old_li[0]][old_li[1]]
                    new_layer_items.append(new_item)
                new_layers.append(new_layer_items)
        return new_layers

    @staticmethod
    def parse_layers_block_map(m, default, new2old, item_types=()):
        # Default value for all items if map is None
        if m is None:
            m = [default for _ in new2old]
            return m
        m = list(flatten(m)) if isinstance(m, list) else m
        # Check on single item of type in item_types
        for t in item_types:
            if isinstance(t, list) and isinstance(m, list):  # list of ...
                if all(isinstance(ti, mi) for ti in t for mi in m):
                    m = [m for _ in new2old]
                    return m
            elif isinstance(m, t):  # non list types
                m = [m for _ in new2old]
                return m
        # Old list to new list
        if isinstance(m, list):
            m = [m[x[0]] if x is not None else default for x in new2old]
            return m
        else:  # Something wrong
            raise ValueError(m)

    @staticmethod
    def parse_layers_block_mask(m, default, new2old, item_types=(), center_mask=None):
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
            masks = [int(x) for x in list(f'{mm:04b}')]  # NY, NX, X, Y
            # print(mm, nis, masks)
            if len(nis) == len(masks):  # layers
                for ni, mask in zip(nis, masks):
                    n[ni] = mask
            elif len(nis) == 1:  # center
                n[nis[0]] = masks[0]
        return n

    @staticmethod
    def get_layers_curves(parsed_layers_curves,
                          parsed_g2l_b2b_l2l,
                          parsed_layers_coordinates):
        """Parse layers curves

        Args:
            parsed_layers_curves (list of list): curves of layers
            parsed_g2l_b2b_l2l (dict): local index of a block of the matrix to
                local index of a block of the parsed layer
            parsed_layers_coordinates (list of list): layers

        Returns:
            tuple: curves (list) curves map of the matrix (list)
        """
        new_shape = np.array(list(parsed_g2l_b2b_l2l)).max(axis=0) + 1
        curves_map = np.full(new_shape, None)
        curves = []
        for gli, lli in parsed_g2l_b2b_l2l.items():
            if lli is None:
                s = None
            elif len(lli) == 4:  # Center
                for li in lli:
                    lt, zt, zi, ci = li  # layer type, Z type, Z index, coord. index
                    if zt == 0:  # Z
                        zs = [0] + parsed_layers_coordinates[4]
                        pzi = zi
                        zi = zi + 1
                    elif zt == 1:  # NZ
                        # zs = parsed_layers_coordinates[5][::-1] + [0]
                        zs = [0] + [-1 * x for x in parsed_layers_coordinates[5]]
                        pzi = zi + 1
                    else:
                        raise ValueError(li)
                    z, pz = zs[zi], zs[pzi]
                    cc = parsed_layers_curves[lt][ci]  # current curve
                    cn = cc[0]  # current curve name
                    c_ps = cc[1] if len(cc) > 1 else []  # current curve points
                    ccs = parsed_layers_coordinates[lt][ci]  # coordinates
                    if lt == 0:  # X layer
                        cx = ccs
                        cy1 = parsed_layers_coordinates[1][ci]
                        cy0 = -parsed_layers_coordinates[3][ci]
                        if cn == 'line':
                            c5, c8 = cc, cc
                        elif cn == 'circle_arc':
                            c5, c8 = [cn, [[0, 0, pz]]], [cn, [[0, 0, z]]]
                        else:
                            c5_ps, c8_ps = [], []
                            for p in c_ps:
                                ky, dx, dz = p
                                cy = cy0 + ky * (cy1 - cy0)
                                c5_ps.append([cx + dx, cy, pz + dz])
                                c8_ps.append([cx + dx, cy, z + dz])
                            c5, c8 = [cn] + [c5_ps], [cn] + [c8_ps]
                    elif lt == 1:  # Y layer
                        cy = ccs
                        cx1 = parsed_layers_coordinates[0][ci]
                        cx0 = -parsed_layers_coordinates[2][ci]
                        if cn == 'line':
                            c1, c2 = cc, cc
                        elif cn == 'circle_arc':
                            c1, c2 = [cn, [[0, 0, pz]]], [cn, [[0, 0, z]]]
                        else:
                            c1_ps, c2_ps = [], []
                            for p in c_ps:
                                kx, dy, dz = p
                                cx = cx0 + kx * (cx1 - cx0)
                                c1_ps.append([cx, cy + dy, pz + dz])
                                c2_ps.append([cx, cy + dy, z + dz])
                            c1, c2 = [cn] + [c1_ps], [cn] + [c2_ps]
                    elif lt == 2:  # NX layer
                        cx = -ccs
                        cy1 = parsed_layers_coordinates[1][ci]
                        cy0 = -parsed_layers_coordinates[3][ci]
                        if cn == 'line':
                            c6, c7 = cc, cc
                        elif cn == 'circle_arc':
                            c6, c7 = [cn, [[0, 0, pz]]], [cn, [[0, 0, z]]]
                        else:
                            c6_ps, c7_ps = [], []
                            for p in c_ps:
                                ky, dx, dz = p
                                cy = cy0 + ky * (cy1 - cy0)
                                c6_ps.append([cx - dx, cy, pz + dz])
                                c7_ps.append([cx - dx, cy, z + dz])
                            c6, c7 = [cn] + [c6_ps], [cn] + [c7_ps]
                    elif lt == 3:  # NY layer
                        cy = -ccs
                        cx1 = parsed_layers_coordinates[0][ci]
                        cx0 = -parsed_layers_coordinates[2][ci]
                        if cn == 'line':
                            c3, c4 = cc, cc
                        elif cn == 'circle_arc':
                            c3, c4 = [cn, [[0, 0, z]]], [cn, [[0, 0, pz]]]
                        else:
                            c3_ps, c4_ps = [], []
                            for p in c_ps:
                                kx, dy, dz = p
                                cx = cx0 + kx * (cx1 - cx0)
                                c3_ps.append([cx, cy - dy, z + dz])
                                c4_ps.append([cx, cy - dy, pz + dz])
                            c3, c4 = [cn] + [c3_ps], [cn] + [c4_ps]
                    else:
                        raise ValueError(lt)
                cs = [c1, c2, c3, c4, c5, c6, c7, c8,
                      ['line'], ['line'], ['line'], ['line']]
                curves.append(cs)
                s = len(curves) - 1
            else:
                li = lli[0]
                lt, zt, zi, ci = li  # layer type, Z type, Z index, coord. index
                if zt == 0:  # Z
                    zs = [0] + parsed_layers_coordinates[4]
                    pzi = zi
                    zi = zi + 1
                elif zt == 1:  # NZ
                    # zs = parsed_layers_coordinates[5][::-1] + [0]
                    zs = [0] + [-1 * x for x in parsed_layers_coordinates[5]]
                    pzi = zi + 1
                else:
                    raise ValueError(li)
                pci = ci - 1
                z, pz = zs[zi], zs[pzi]
                cc = parsed_layers_curves[lt][ci]  # current curve
                pc = parsed_layers_curves[lt][pci]  # previous curve
                cn = cc[0]  # current curve name
                pn = pc[0]  # previous curve name
                c_ps = cc[1] if len(cc) > 1 else []  # current curve points
                pc_ps = pc[1] if len(pc) > 1 else []  # previous curve points
                ccs = parsed_layers_coordinates[lt][ci]  # coordinates
                pcs = parsed_layers_coordinates[lt][pci]  # previous coordinates
                if lt == 0:  # X layer
                    cx, px = ccs, pcs
                    cy1 = parsed_layers_coordinates[1][ci]
                    cy0 = -parsed_layers_coordinates[3][ci]
                    py1 = parsed_layers_coordinates[1][pci]
                    py0 = -parsed_layers_coordinates[3][pci]
                    if cn == 'line':
                        c1, c4 = cc, cc
                    elif cn == 'circle_arc':
                        c1, c4 = [cn, [[0, 0, pz]]], [cn, [[0, 0, z]]]
                    else:
                        c1_ps, c4_ps = [], []
                        for p in c_ps:
                            ky, dx, dz = p
                            cy = cy0 + ky * (cy1 - cy0)
                            c1_ps.append([cx + dx, cy, pz + dz])
                            c4_ps.append([cx + dx, cy, z + dz])
                        c1, c4 = [cn] + [c1_ps], [cn] + [c4_ps]
                    if pn == 'line':
                        c2, c3 = pc, pc
                    elif pn == 'circle_arc':
                        c2, c3 = [pn, [[0, 0, pz]]], [pn, [[0, 0, z]]]
                    else:
                        c2_ps, c3_ps = [], []
                        for p in pc_ps:
                            ky, dx, dz = p
                            py = py0 + ky * (py1 - py0)
                            c2_ps.append([px + dx, py, pz + dz])
                            c3_ps.append([px + dx, py, z + dz])
                        c2, c3 = [pn] + [c2_ps], [pn] + [c3_ps]
                    cs = [['line'], ['line'], ['line'], ['line'],
                          c1, c2, c3, c4,
                          ['line'], ['line'], ['line'], ['line']]
                elif lt == 1:  # Y layer
                    cy, py = ccs, pcs
                    cx1 = parsed_layers_coordinates[0][ci]
                    cx0 = -parsed_layers_coordinates[2][ci]
                    px1 = parsed_layers_coordinates[0][pci]
                    px0 = -parsed_layers_coordinates[2][pci]
                    if cn == 'line':
                        c1, c2 = cc, cc
                    elif cn == 'circle_arc':
                        c1, c2 = [cn, [[0, 0, pz]]], [cn, [[0, 0, z]]]
                    else:
                        c1_ps, c2_ps = [], []
                        for p in c_ps:
                            kx, dy, dz = p
                            cx = cx0 + kx * (cx1 - cx0)
                            c1_ps.append([cx, cy + dy, pz + dz])
                            c2_ps.append([cx, cy + dy, z + dz])
                        c1, c2 = [cn] + [c1_ps], [cn] + [c2_ps]
                    if pn == 'line':
                        c3, c4 = pc, pc
                    elif pn == 'circle_arc':
                        c3, c4 = [pn, [[0, 0, z]]], [pn, [[0, 0, pz]]]
                    else:
                        c3_ps, c4_ps = [], []
                        for p in pc_ps:
                            kx, dy, dz = p
                            px = px0 + kx * (px1 - px0)
                            c3_ps.append([px, py + dy, z + dz])
                            c4_ps.append([px, py + dy, pz + dz])
                        c3, c4 = [pn] + [c3_ps], [pn] + [c4_ps]
                    cs = [c1, c2, c3, c4,
                          ['line'], ['line'], ['line'], ['line'],
                          ['line'], ['line'], ['line'], ['line']]
                elif lt == 2:  # NX layer
                    cx, px = -ccs, -pcs
                    cy1 = parsed_layers_coordinates[1][ci]
                    cy0 = -parsed_layers_coordinates[3][ci]
                    py1 = parsed_layers_coordinates[1][pci]
                    py0 = -parsed_layers_coordinates[3][pci]
                    if cn == 'line':
                        c2, c3 = cc, cc
                    elif cn == 'circle_arc':
                        c2, c3 = [cn, [[0, 0, pz]]], [cn, [[0, 0, z]]]
                    else:
                        c2_ps, c3_ps = [], []
                        for p in c_ps:
                            ky, dx, dz = p
                            cy = cy0 + ky * (cy1 - cy0)
                            c2_ps.append([cx - dx, cy, pz + dz])
                            c3_ps.append([cx - dx, cy, z + dz])
                        c2, c3 = [cn] + [c2_ps], [cn] + [c3_ps]
                    if pn == 'line':
                        c1, c4 = pc, pc
                    elif pn == 'circle_arc':
                        c1, c4 = [pn, [[0, 0, pz]]], [pn, [[0, 0, z]]]
                    else:
                        c1_ps, c4_ps = [], []
                        for p in pc_ps:
                            ky, dx, dz = p
                            py = py0 + ky * (py1 - py0)
                            c1_ps.append([px - dx, py, pz + dz])
                            c4_ps.append([px - dx, py, z + dz])
                        c1, c4 = [pn] + [c1_ps], [pn] + [c4_ps]
                    cs = [['line'], ['line'], ['line'], ['line'],
                          c1, c2, c3, c4,
                          ['line'], ['line'], ['line'], ['line']]
                elif lt == 3:  # NY
                    cy, py = -ccs, -pcs
                    cx1 = parsed_layers_coordinates[0][ci]
                    cx0 = -parsed_layers_coordinates[2][ci]
                    px1 = parsed_layers_coordinates[0][pci]
                    px0 = -parsed_layers_coordinates[2][pci]
                    if cn == 'line':
                        c3, c4 = cc, cc
                    elif cn == 'circle_arc':
                        c3, c4 = [cn, [[0, 0, z]]], [cn, [[0, 0, pz]]]
                    else:
                        c3_ps, c4_ps = [], []
                        for p in c_ps:
                            kx, dy, dz = p
                            cx = cx0 + kx * (cx1 - cx0)
                            c3_ps.append([cx, cy - dy, z + dz])
                            c4_ps.append([cx, cy - dy, pz + dz])
                        c3, c4 = [cn] + [c3_ps], [cn] + [c4_ps]
                    if pn == 'line':
                        c1, c2 = pc, pc
                    elif pn == 'circle_arc':
                        c1, c2 = [pn, [[0, 0, pz]]], [pn, [[0, 0, z]]]
                    else:
                        c1_ps, c2_ps = [], []
                        for p in pc_ps:
                            kx, dy, dz = p
                            px = px0 + kx * (px1 - px0)
                            c1_ps.append([px, py - dy, pz + dz])
                            c2_ps.append([px, py - dy, z + dz])
                        c1, c2 = [pn] + [c1_ps], [pn] + [c2_ps]
                    cs = [c1, c2, c3, c4,
                          ['line'], ['line'], ['line'], ['line'],
                          ['line'], ['line'], ['line'], ['line']]
                else:
                    raise ValueError(li)
                curves.append(cs)
                s = len(curves) - 1
            curves_map[gli] = s
        return curves, curves_map.tolist()

    @staticmethod
    def get_structure_type(parsed_g2l_b2b_l2l):
        new_shape = np.array(list(parsed_g2l_b2b_l2l)).max(axis=0) + 1
        structure_type_map = np.full(new_shape, None)
        for gli, lli in parsed_g2l_b2b_l2l.items():
            if lli is None:
                s = None
            elif len(lli) == 4:  # Center
                s = 0
            elif lli[0][0] == 0:  # X
                s = 0
            elif lli[0][0] == 1:  # Y
                s = 0
            elif lli[0][0] == 2:  # NX
                s = 1
            elif lli[0][0] == 3:  # NY
                s = 2
            else:
                raise ValueError(lli)
            structure_type_map[gli] = s
        structure_type = ['LLL', 'LRR', 'RLR', 'RRL']
        return structure_type, structure_type_map.tolist()


str2obj = {
    Layer.__name__: Layer
}
