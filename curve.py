class Curve:
    def __init__(self, tag=None, name='line', zone=None, points=None,
                 structure=None, **kwargs):
        """Curve
        Args:
            tag(int): unique id
            name(str): type
            zone(str): zone
            points (list of Point): curve points
            structure (Structure): curve structure
        """
        self.tag = tag
        self.name = name
        self.zone = zone
        self.points = points if points is not None else []
        self.structure = structure
        self.kwargs = kwargs
