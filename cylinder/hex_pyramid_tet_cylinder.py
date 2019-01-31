import gmsh

model = gmsh.model
factory = model.geo
gmsh.initialize()
gmsh.option.setNumber("General.Terminal", 1)
model.add("hex_pyramid_tet_cylinder")
lc = 1
r = 150
a = r / 3
# Points
factory.addPoint(0, 0, 0, lc, 1)
factory.addPoint(r, 0, 0, lc, 2)
factory.addPoint(0, r, 0, lc, 3)
factory.addPoint(-r, 0, 0, lc, 4)
factory.addPoint(0, -r, 0, lc, 5)
factory.addPoint(a, 0, 0, lc, 6)
factory.addPoint(0, a, 0, lc, 7)
factory.addPoint(-a, 0, 0, lc, 8)
factory.addPoint(0, -a, 0, lc, 9)
# Lines
factory.addCircleArc(2, 1, 3, 1)
factory.addCircleArc(3, 1, 4, 2)
factory.addCircleArc(4, 1, 5, 3)
factory.addCircleArc(5, 1, 2, 4)
factory.addLine(6, 7, 5)
factory.addLine(7, 8, 6)
factory.addLine(8, 9, 7)
factory.addLine(9, 6, 8)
factory.addLine(6, 2, 9)
factory.addLine(7, 3, 10)
factory.addLine(8, 4, 11)
factory.addLine(9, 5, 12)
# Surfaces
factory.addCurveLoop([5, 6, 7, 8], 1)
factory.addPlaneSurface([1], 1)
factory.addCurveLoop([1, -10, -5, 9], 2)
factory.addPlaneSurface([2], 2)
factory.addCurveLoop([2, -11, -6, 10], 3)
factory.addPlaneSurface([3], 3)
factory.addCurveLoop([3, -12, -7, 11], 4)
factory.addPlaneSurface([4], 4)
factory.addCurveLoop([4, -9, -8, 12], 5)
factory.addPlaneSurface([5], 5)
# Center surface -> quad mesh
factory.mesh.setRecombine(2, 1)
# Extrude
h = 3
n = 3
out_dim_tags_1 = factory.extrude([(2, 1)], 0, 0, h,
                                 numElements=[n], heights=[1], recombine=True)
out_dim_tags_2 = factory.extrude([(2, 2)], 0, 0, h,
                                 numElements=[], heights=[], recombine=True)
out_dim_tags_3 = factory.extrude([(2, 3)], 0, 0, h,
                                 numElements=[], heights=[], recombine=True)
out_dim_tags_4 = factory.extrude([(2, 4)], 0, 0, h,
                                 numElements=[], heights=[], recombine=True)
out_dim_tags_5 = factory.extrude([(2, 5)], 0, 0, h,
                                 numElements=[], heights=[], recombine=True)
# Physical
# Top
model.addPhysicalGroup(dim=2, tags=[
    out_dim_tags_1[0][1],
    out_dim_tags_2[0][1],
    out_dim_tags_3[0][1],
    out_dim_tags_4[0][1],
    out_dim_tags_5[0][1]
], tag=1)
model.setPhysicalName(dim=2, tag=1, name="Top")
# Bottom
model.addPhysicalGroup(dim=2, tags=[1, 2, 3, 4, 5], tag=2)
model.setPhysicalName(dim=2, tag=2, name="Bottom")
# Lateral
model.addPhysicalGroup(dim=2, tags=[
    out_dim_tags_2[2][1],
    out_dim_tags_3[2][1],
    out_dim_tags_4[2][1],
    out_dim_tags_5[2][1]
], tag=3)
model.setPhysicalName(dim=2, tag=3, name="Lateral")
# Volume
model.addPhysicalGroup(dim=3, tags=[
    out_dim_tags_1[1][1],
    out_dim_tags_2[1][1],
    out_dim_tags_3[1][1],
    out_dim_tags_4[1][1],
    out_dim_tags_5[1][1]
], tag=1)
model.setPhysicalName(dim=3, tag=1, name="Volume")
dim_tags = gmsh.model.getEntities(dim=0)
print(dim_tags)
gmsh.model.mesh.setSize(dim_tags, lc)
factory.synchronize()
model.mesh.generate(3)
gmsh.write("hex_pyramid_tet_cylinder.msh")
gmsh.finalize()
