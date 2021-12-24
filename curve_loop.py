class CurveLoop:
    def __init__(self, tag=None, name=None, zone=None, curves=None,
                 curves_signs=None, **kwargs):
        """Volume
        Args:
            tag(int): unique id
            name(str): type
            zone(str): zone
            curves(list of Curve): curves
            curves_signs(list of int): curves signs
        """
        self.tag = tag
        self.name = name
        self.zone = zone
        self.curves = curves
        self.curves_signs = curves_signs
        self.kwargs = kwargs


str2obj = {
    CurveLoop.__name__: CurveLoop,
    CurveLoop.__name__.lower(): CurveLoop
}
