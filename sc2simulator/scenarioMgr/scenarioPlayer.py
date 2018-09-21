

################################################################################
class ScenarioPlayer(object):
    ############################################################################
    def __init__(self, tag):
        self.number     = number
        self._units     = units
        self.upgrades   = upgrades
    ############################################################################
    def __str__(self): return self.__repr__()
    def __repr__(self):
        return "<%s #%d %d units %d upgrades>"%(self.__class__.__name__,
            self.number, self.numUnits, self.numUpgrades)
    ############################################################################
    @property
    def numUnits(self):
        return len(self.units)
    ############################################################################
    @property
    def numUpgrades(self):
        return len(self.upgrades)
    ############################################################################
    @property
    def units(self):
        return [u for u in self._units.values() if u.player == self.number]
    ############################################################################
    @property
    def upgradeObjects(self):
        """convert internal data into tech tree objects"""

