import gmsh


if __name__ == '__main__':
    gmsh.initialize()
    fn = 'test_cylinder_config.msh2'
    gmsh.open(fn)
    # "" for default tetrahedral mesh optimizer
    # "Netgen" for Netgen optimizer,
    # "HighOrder" for direct high-order mesh optimizer,
    # "HighOrderElastic" for high-order elastic smoother,
    # "HighOrderFastCurving" for fast curving algorithm,
    # "Laplace2D" for Laplace smoothing,
    # "Relocate2D" and "Relocate3D" for node relocation
    gmsh.model.mesh.optimize("", force=True, niter=1)
    gmsh.write('test_cylinder_config_opt.msh2')
    gmsh.finalize()
