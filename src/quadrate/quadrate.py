class Quadrate:
    def __init__(self, name=None, **kwargs):
        self.name = name
        self.kwargs = kwargs


class NoQuadrate:
    def __init__(self):
        pass

    def __call__(self, block):
        pass


class QuadrateBlock:
    def __init__(self):
        pass

    def __call__(self, block):
        pass
        # for b in block:
        #     vs_dt = [(3, v.tag) for v in b.volumes if v.tag is not None]
        #     dt = DataTree(vs_dt=vs_dt)
        #     for vi, ss_cs_ps_dt in enumerate(dt.vs_ss_cs_ps_dt):
        #         for si, cs_ps_dt in enumerate(ss_cs_ps_dt):
        #             s_dt = dt.vs_ss_dt[vi][si]
        #             ss_ps_dt = set()
        #             for ci, ps_dt in enumerate(cs_ps_dt):
        #                 ss_ps_dt.update(ps_dt)
        #             ss_ps_cs = [dt.ps_dt_to_cs[x] for x in ss_ps_dt]
        #             points = [Point(list(x)) for x in ss_ps_cs]
        #             q = get_surface_quadrate(points)
        #             s = Surface(tag=s_dt[1], quadrate=q)
        #             register_quadrate_surface(block.factory, s)


str2obj = {
    Quadrate.__name__: Quadrate,
    QuadrateBlock.__name__: QuadrateBlock,
    NoQuadrate.__name__: NoQuadrate
}
