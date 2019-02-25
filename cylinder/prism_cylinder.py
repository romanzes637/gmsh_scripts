import gmsh

model = gmsh.model
factory = model.geo
gmsh.initialize()
gmsh.option.setNumber("General.Terminal", 1)
model.add("prism_cylinder")
lc = 3
r = 150
factory.addPoint(0, 0, 0, lc, 1)
factory.addPoint(r, 0, 0, lc, 2)
factory.addPoint(0, r, 0, lc, 3)
factory.addPoint(-r, 0, 0, lc, 4)
factory.addPoint(0, -r, 0, lc, 5)
factory.addCircleArc(2, 1, 3, 1)
factory.addCircleArc(3, 1, 4, 2)
factory.addCircleArc(4, 1, 5, 3)
factory.addCircleArc(5, 1, 2, 4)
factory.addCurveLoop([1, 2, 3, 4], 1)
factory.addPlaneSurface([1], 1)
h = 30
n = 10
out_dim_tags = factory.extrude([(2, 1)], 0, 0, h, [n], [1], recombine=True)
model.addPhysicalGroup(dim=2, tags=[1], tag=1)
model.setPhysicalName(2, 1, "Bottom")
model.addPhysicalGroup(dim=2, tags=[13, 17, 21, 25], tag=2)
model.addPhysicalGroup(dim=2, tags=[26], tag=3)
model.addPhysicalGroup(dim=3, tags=[1], tag=1)
model.setPhysicalName(dim=3, tag=1, name="Volume")
model.setPhysicalName(dim=2, tag=3, name="Top")
model.setPhysicalName(dim=2, tag=2, name="Lateral")
factory.synchronize()
model.mesh.generate(3)
gmsh.write("prism_cylinder.msh")
gmsh.finalize()
