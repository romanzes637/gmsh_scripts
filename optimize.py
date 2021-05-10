import gmsh
import sys


if __name__ == '__main__':
    print(f"script: {sys.argv[0]}")
    print(f"input: {sys.argv[1]}")
    print(f"output: {sys.argv[2]}")
    n_i = int(sys.argv[3]) if len(sys.argv) == 4 else 1
    print(f'iterations: {n_i}')
    gmsh.initialize()
    gmsh.option.setNumber("General.Terminal", 1)
    gmsh.open(sys.argv[1])
    # "" for default tetrahedral mesh optimizer
    # "Netgen" for Netgen optimizer,
    # "HighOrder" for direct high-order mesh optimizer,
    # "HighOrderElastic" for high-order elastic smoother,
    # "HighOrderFastCurving" for fast curving algorithm,
    # "Laplace2D" for Laplace smoothing,
    # "Relocate2D" and "Relocate3D" for node relocation
    gmsh.model.mesh.optimize("", force=True, niter=n_i)
    gmsh.write(sys.argv[2])
    gmsh.finalize()
