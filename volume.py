class Volume:
    def __init__(self, tag=None, name=None, zone=None, surfaces_loops=None,
                 structure=None, quadrate=None, **kwargs):
        """Volume
        Args:
            tag (int): unique id
            name (str): type
            zone (str): zone
            surfaces_loops (list of SurfaceLoop): surfaces loops
            structure (Structure): volume structure
            quadrate (Quadrate): volume quadrate
        """
        self.tag = tag
        self.name = name
        self.zone = zone
        self.surfaces_loops = surfaces_loops
        self.structure = structure
        self.quadrate = quadrate
        self.kwargs = kwargs


str2obj = {
    Volume.__name__: Volume,
    Volume.__name__.lower(): Volume
}
