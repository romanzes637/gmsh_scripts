"""
# see https://gitlab.onelab.info/gmsh/gmsh/blob/gmsh_4_8_4/tutorial/python/x2.py
# Set this to True to build a fully hex mesh:
#transfinite = True
transfinite = False
transfiniteAuto = False

if transfinite:
    NN = 30
    for c in gmsh.model.getEntities(1):
        gmsh.model.mesh.setTransfiniteCurve(c[1], NN)
    for s in gmsh.model.getEntities(2):
        gmsh.model.mesh.setTransfiniteSurface(s[1])
        gmsh.model.mesh.setRecombine(s[0], s[1])
        gmsh.model.mesh.setSmoothing(s[0], s[1], 100)
    gmsh.model.mesh.setTransfiniteVolume(v1)
elif transfiniteAuto:
    gmsh.option.setNumber('Mesh.MeshSizeMin', 0.5)
    gmsh.option.setNumber('Mesh.MeshSizeMax', 0.5)
    # setTransfiniteAutomatic() uses the sizing constraints to set the number
    # of points
    gmsh.model.mesh.setTransfiniteAutomatic()
else:
    gmsh.option.setNumber('Mesh.MeshSizeMin', 0.05)
    gmsh.option.setNumber('Mesh.MeshSizeMax', 0.05)

def setTransfiniteAutomatic(dimTags=[], cornerAngle=2.35, recombine=True):

Set transfinite meshing constraints on the model entities in `dimTag'.
Transfinite meshing constraints are added to the curves of the quadrangular
surfaces and to the faces of 6-sided volumes. Quadragular faces with a
corner angle superior to `cornerAngle' (in radians) are ignored. The number
of points is automatically determined from the sizing constraints. If
`dimTag' is empty, the constraints are applied to all entities in the
model. If `recombine' is true, the recombine flag is automatically set on
the transfinite surfaces.

"""

import gmsh
import numpy as np

from registry import get_curve_structure, register_structure_curve, \
    get_surface_structure, register_structure_surface, \
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


class NoStructure:
    def __init__(self):
        pass

    def __call__(self, block):
        pass


class StructureAuto:
    """

    Args:
        corner_angle (float): Quadrangular faces with a corner angle superior
         to corner_angle (in degree) are ignored
        quadrate (bool): Quadrate surfaces

    """
    def __init__(self, corner_angle=np.rad2deg(2.35), quadrate=True):
        self.corner_angle = corner_angle
        self.quadrate = quadrate

    def __call__(self, block):
        # TODO get dim-tags from block
        # TODO generates bad mesh
        gmsh.model.mesh.setTransfiniteAutomatic(
            cornerAngle=np.deg2rad(self.corner_angle), recombine=self.quadrate)


class StructureBlock:
    def __init__(self, quadrate=True):
        self.quadrate = quadrate

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
                    if self.quadrate:
                        s_qu = get_surface_quadrate(points)
                        ss_st.append(s_st)
                        ss_qu.append(s_qu)
                vs_ss_st.append(ss_st)
                vs_ss_cs_st.append(ss_cs_st)
                vs_ps_cs = [dt.ps_dt_to_cs[x] for x in vs_ps_dt]
                points = [Point(list(x)) for x in vs_ps_cs]
                v_st = get_volume_structure(points)
                vs_st.append(v_st)
            # Do Structure
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
                        if self.quadrate:
                            s_qu = ss_qu[si]
                            s = Surface(tag=s_dt[1], quadrate=s_qu)
                            register_quadrate_surface(s)
                        for ci, c_st in enumerate(vs_ss_cs_st[vi][si]):
                            c_dt = dt.vs_ss_cs_dt[vi][si][ci]
                            c = Curve(tag=c_dt[1], structure=c_st)
                            register_structure_curve(c)


str2obj = {
    Structure.__name__: Structure,
    NoStructure.__name__: NoStructure,
    StructureAuto.__name__: StructureAuto,
    StructureBlock.__name__: StructureBlock
}
