class Surface:
    def __init__(self, tag=None, name='line', zone=None, curves_loops=None,
                 structure=None, quadrate=None, **kwargs):
        """Surface
        Args:
            tag(int): unique id
            name(str): type
            zone(str): zone
            curves_loops(list of CurveLoop): curves loops
            quadrate(Quadrate): surface quadrate
            structure(Structure): surface structure
        """
        self.tag = tag
        self.name = name
        self.zone = zone
        self.curves_loops = curves_loops
        self.structure = structure
        self.quadrate = quadrate
        self.kwargs = kwargs


str2obj = {
    Surface.__name__: Surface,
    Surface.__name__.lower(): Surface
}
