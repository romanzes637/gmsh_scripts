from registry import get_curve_structure, register_structure_curve, \
    get_surface_structure, register_structure_surface,\
    get_volume_structure, register_structure_volume, \
    get_surface_quadrate, register_quadrate_surface
from support import DataTree
from point import Point
from curve import Curve
from surface import Surface
from volume import Volume


class Structure:
    def __init__(self, name=None, **kwargs):
        self.name = name
        self.kwargs = kwargs


class StructureBlock:
    def __init__(self):
        pass

    def __call__(self, block):
        for b in block:
            vs_dt = [(3, v.tag) for v in b.volumes if v.tag is not None]
            dt = DataTree(vs_dt=vs_dt)
            # Collect Structure
            vs_st, vs_ss_st, vs_ss_cs_st = [], [], []
            ss_qu = []
            for vi, ss_cs_ps_dt in enumerate(dt.vs_ss_cs_ps_dt):  # Volumes
                ss_st, ss_cs_st = [], []
                vs_ps_dt = set()
                for si, cs_ps_dt in enumerate(ss_cs_ps_dt):  # Surfaces
                    cs_st = []
                    ss_ps_dt = set()
                    for ci, ps_dt in enumerate(cs_ps_dt):  # Curves
                        ss_ps_dt.update(ps_dt)
                        ps_cs = [dt.ps_dt_to_cs[x] for x in ps_dt]
                        points = [Point(list(x)) for x in ps_cs]
                        c_st = get_curve_structure(points)
                        cs_st.append(c_st)
                    vs_ps_dt.update(ss_ps_dt)
                    ss_cs_st.append(cs_st)
                    ss_ps_cs = [dt.ps_dt_to_cs[x] for x in ss_ps_dt]
                    points = [Point(list(x)) for x in ss_ps_cs]
                    s_st = get_surface_structure(points)
                    s_qu = get_surface_quadrate(points)
                    ss_st.append(s_st)
                    ss_qu.append(s_qu)
                vs_ss_st.append(ss_st)
                vs_ss_cs_st.append(ss_cs_st)
                vs_ps_cs = [dt.ps_dt_to_cs[x] for x in vs_ps_dt]
                points = [Point(list(x)) for x in vs_ps_cs]
                v_st = get_volume_structure(points)
                vs_st.append(v_st)
            # Do Structure TODO Triangles orientation http://onelab.info/pipermail/gmsh/2018/012407.html
            for vi, v_st in enumerate(vs_st):
                v_dt = dt.vs_dt[vi]
                all_ss_st = all(x is not None for x in vs_ss_st[vi])
                all_cs_st = all(y is not None for x in vs_ss_cs_st[vi] for y in x)
                if all_ss_st and all_cs_st:
                    v = Volume(tag=v_dt[1], structure=v_st)
                    register_structure_volume(v)
                    for si, s_st in enumerate(vs_ss_st[vi]):
                        s_dt = dt.vs_ss_dt[vi][si]
                        s = Surface(tag=s_dt[1], structure=s_st)
                        register_structure_surface(s)
                        s_qu = ss_qu[si]
                        s = Surface(tag=s_dt[1], quadrate=s_qu)
                        register_quadrate_surface(s)
                        for ci, c_st in enumerate(vs_ss_cs_st[vi][si]):
                            c_dt = dt.vs_ss_cs_dt[vi][si][ci]
                            c = Curve(tag=c_dt[1], structure=c_st)
                            register_structure_curve(c)
