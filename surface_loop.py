class SurfaceLoop:
    def __init__(self, tag=None, name=None, zone=None, surfaces=None, **kwargs):
        """Volume
        Args:
            tag(int): unique id
            name(str): type
            zone(str): zone
            surfaces(list of Surface): surfaces
        """
        self.tag = tag
        self.name = name
        self.zone = zone
        self.surfaces = surfaces
        self.kwargs = kwargs


str2obj = {
    SurfaceLoop.__name__: SurfaceLoop,
    SurfaceLoop.__name__.lower(): SurfaceLoop
}
