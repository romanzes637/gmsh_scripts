class Curve:
    """Curve

    Args:
        tag (int): unique id
        name (str): type of the curve:
            line, polyline, circle_arc, ellipse_arc, spline, bspline, bezier
        zone (str): zone
        points (list of Point): curve points
        structure (Structure): curve structure
        kwargs (dict): other keyword arguments
    """
    def __init__(self, tag=None, name='line', zone=None, points=None,
                 structure=None, **kwargs):
        self.tag = tag
        self.name = name
        self.zone = zone
        self.points = points if points is not None else []
        self.structure = structure
        self.kwargs = kwargs


str2obj = {
    Curve.__name__: Curve,
    Curve.__name__.lower(): Curve
}
