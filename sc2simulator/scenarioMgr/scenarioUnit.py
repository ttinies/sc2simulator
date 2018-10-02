

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
        self.code       = 0
        self.energy     = 0.0
        self.life       = 0.0
        self.shields    = 0.0
        self.xp         = 0
        self.base       = False
    ############################################################################
    def __str__(self): return self.__repr__()
    def __repr__(self):
        attrList = ["%s=%s"%(k, v) for k, v in sorted(self.attrs.items())]
        attrStr = ", ".join(attrList)
        return "<%s %s>"%(self.__class__.__name__, attrStr)
    ############################################################################
    def __hash__(self):
        return hash(self.tag)
    ############################################################################
    @property
    def attrs(self):
        return self.__dict__
    ############################################################################
    @property
    def loc(self):
        """MapPoint object where this unit is located"""
        return self.position
    ############################################################################
    @property
    def unitType(self):
        """the tech tree definition for this specific unit"""
        return self.code
    ############################################################################
    def update(self, **attrs):
        """update this unit's attributes"""
        for k,v in attrs.items(): # assign attributes into unit
            setattr(self, k, v)


################################################################################
def convertTechUnit(techUnit, **attrs):
    """convert a tech unit into a scenario unit"""
    u = ScenarioUnit(0)
    u.update(nametype   = techUnit.name,
             code       = techUnit.mType.code,
             energy     = techUnit.energyStart,
             life       = techUnit.healthMax,
             shields    = techUnit.shieldsMax)
    u.update(**attrs) # allow passed attributes to override techUnit defaults
    return u

