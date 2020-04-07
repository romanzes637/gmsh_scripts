import gmsh

from matrix import Matrix


class RegularMatrix(Matrix):
    def __init__(self, factory='geo', transform_data=None,
                 dx=1, dy=2, dz=3, nx=3, ny=2, nz=1,
                 lc=None, tx=None, ty=None, tz=None,
                 trans=1, rec=1, item_input=None, item_type=1):
        transform_data = [] if transform_data is None else transform_data
        coordinates_type = 'delta'
        n = nx * ny * nz
        xs = [dx for _ in range(nx)]
        ys = [dy for _ in range(ny)]
        zs = [dz for _ in range(nz)]
        lcs = [lc for _ in range(n)] if lc is not None else None
        txs = [tx for _ in range(nx)] if tx is not None else None
        tys = [ty for _ in range(ny)] if ty is not None else None
        tzs = [tz for _ in range(nz)] if tz is not None else None
        type_map = [item_type for _ in range(n)]
        inputs = [item_input] if item_input is not None else None
        inputs_map = [0 for _ in range(n)] if item_input is not None else None
        recs_map = [rec for _ in range(n)] if rec is not None else None
        trans_map = [trans for _ in range(n)] if trans is not None else None
        Matrix.__init__(self, factory, xs, ys, zs, lcs=lcs,
                        coordinates_type=coordinates_type,
                        transform_data=transform_data,
                        txs=txs, tys=tys, tzs=tzs,
                        type_map=type_map, inputs=inputs,
                        volumes_map=None, volumes_names=None,
                        surfaces_map=None, surfaces_names=None,
                        inputs_map=inputs_map,
                        recs_map=recs_map, trans_map=trans_map)


