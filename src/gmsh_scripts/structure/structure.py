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

from gmsh_scripts.registry import get_curve_structure, register_structure_curve, \
    get_surface_structure, register_structure_surface, \
    get_volume_structure, register_structure_volume, \
    get_surface_quadrate, register_quadrate_surface, get_boolean_new2olds
from gmsh_scripts.support.support import DataTree, flatten
from gmsh_scripts.entity.point import Point
from gmsh_scripts.entity.curve import Curve
from gmsh_scripts.entity.surface import Surface
from gmsh_scripts.entity.volume import Volume


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
    def __init__(self, do_quadrate=True, do_structure=True):
        self.do_quadrate = do_quadrate
        self.do_structure = do_structure

    def __call__(self, block):
        if not self.do_structure:
            return
        v_dts = gmsh.model.getEntities(3)
        new_olds = get_boolean_new2olds()
        for vi, v_dt in enumerate(v_dts):  # Volumes
            # print(v_dt)
            # Check
            dt = DataTree([v_dt])
            vs_ps = set(flatten(dt.vs_ss_cs_ps_dt[0]))  # Points
            if len(vs_ps) != 8:  # 8 points in volume
                continue
            if len(dt.vs_ss_dt[0]) != 6:  # 6 surfaces in volume
                continue
            ss_st, ss_cs_st = [], []  # Surfaces, Surfaces curves structures
            ss_qu = []  # Surfaces quadrates
            # vs_ps_dt = set()  # Volume points dim-tags
            do_structure = True
            for si, cs_ps_dt in enumerate(dt.vs_ss_cs_ps_dt[0]):  # Surfaces
                if len(dt.vs_ss_cs_dt[0][si]) != 4:  # 4 curves on surface
                    do_structure = False
                    break
                cs_st = []  # Curves structures
                ss_ps_dt = set()  # Surfaces points dim-tags
                for ci, ps_dt in enumerate(cs_ps_dt):  # Curves
                    ss_ps_dt.update(ps_dt)
                    c_dt = dt.vs_ss_cs_dt[0][si][ci]
                    if c_dt[1] > 0:
                        ps_cs = [dt.ps_dt_to_cs[x] for x in ps_dt]
                    else:
                        ps_cs = [dt.ps_dt_to_cs[x] for x in ps_dt[::-1]]
                    c_ps = [Point(list(x)) for x in ps_cs]  # Curves points
                    c_st = get_curve_structure(c_ps)
                    if c_st is None:
                        do_structure = False
                        break
                    cs_st.append(c_st)
                if not do_structure:
                    break
                # vs_ps_dt.update(ss_ps_dt)
                ss_cs_st.append(cs_st)
                ss_ps_cs = [dt.ps_dt_to_cs[x] for x in ss_ps_dt]
                s_ps = [Point(list(x)) for x in ss_ps_cs]
                s_st = get_surface_structure(s_ps)  # Surfaces points
                ss_st.append(s_st)
                if s_st is None:
                    do_structure = False
                    break
                if self.do_quadrate:
                    s_qu = get_surface_quadrate(s_ps)
                    ss_qu.append(s_qu)
            if not do_structure:
                continue
            # Too long
            # if len(vs_ps_dt) != 8:  # 8 points in volume
            #     continue
            # vs_ps_cs = [dt.ps_dt_to_cs[x] for x in vs_ps_dt]
            # v_ps = [Point(list(x)) for x in vs_ps_cs]  # Volume points
            # v_st = timeit(get_volume_structure)(v_ps)  # Volume structure
            v_t = v_dt[1]
            old_vts = new_olds.get(v_t, None)
            if old_vts is None:
                old_vt = v_t
            else:
                old_vt = v_t if v_t in old_vts else None
            if v_t is not None:
                v_st = get_volume_structure(old_vt)  # Volume structure
                if v_st is None:
                    continue
                # print(v_t, old_vts)
                # Do structure
                v = Volume(tag=v_dt[1], structure=v_st)
                register_structure_volume(v)
                for si, s_st in enumerate(ss_st):
                    s_dt = dt.vs_ss_dt[0][si]
                    s = Surface(tag=s_dt[1], structure=s_st)
                    register_structure_surface(s)
                    if self.do_quadrate:
                        s_qu = ss_qu[si]
                        s = Surface(tag=s_dt[1], quadrate=s_qu)
                        register_quadrate_surface(s)
                    for ci, c_st in enumerate(ss_cs_st[si]):
                        c_dt = dt.vs_ss_cs_dt[0][si][ci]
                        c = Curve(tag=c_dt[1], structure=c_st)
                        register_structure_curve(c)


str2obj = {
    Structure.__name__: Structure,
    NoStructure.__name__: NoStructure,
    StructureAuto.__name__: StructureAuto,
    StructureBlock.__name__: StructureBlock
}
