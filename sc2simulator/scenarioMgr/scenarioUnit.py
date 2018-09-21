

################################################################################
class ScenarioUnit(object):
    """sufficient info to fully represent a unit within a scenario"""
    ############################################################################
    def __init__(self, tag):
        self.tag        = tag # as reported by the mini-editor
        self.owner      = 0
        self.position   = None
        self.facing     = 0.0
        self.nametype   = ""
        self.energy     = 0.0
        self.life       = 0.0
        self.shields    = 0.0
        self.xp         = 0
    ############################################################################
    def __str__(self): return self.__repr__()
    def __repr__(self):
        attrList = ["%s=%s"%(k, v) for k, v in sorted(self.attrs.items())]
        attrStr = ", ".join(attrList)
        return "<%s %s>"%(self.__class__.__name__, attrStr)
    ############################################################################
    @property
    def attrs(self):
        return self.__dict__
    ############################################################################
    @property
    def loc(self):
        """MapPoint object where this unit is located"""
    ############################################################################
    @property
    def unitType(self):
        """the tech tree definition for this specific unit"""

