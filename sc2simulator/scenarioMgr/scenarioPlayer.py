
import os
import re

try:    import sc2techTree # Versentiedge closed source package
except: sc2techTree = None

from sc2simulator import constants as c
from sc2simulator.scenarioMgr.scenarioUnit import convertTechUnit
from sc2simulator.setup.mapLocations import pickValidMapLoc


################################################################################
class ScenarioPlayer(object):
    """sufficient info to fully represent a player within a scenario"""
    ############################################################################
    def __init__(self, number, units, upgrades, pos=None, race=c.RANDOM):
        self._baseUnits = []
        self.number     = number
        self._units     = units
        self.upgrades   = upgrades
        self.position   = pos
        self.race       = race
    ############################################################################
    def __str__(self): return self.__repr__()
    def __repr__(self):
        return "<%s #%d units:%d upgrades:%d @ %s>"%(self.__class__.__name__,
            self.number, self.numUnits, self.numUpgrades, self.position)
    ############################################################################
    @property
    def baseUnits(self):
        if self._baseUnits: return self._baseUnits
        for u in self._units.values():
            if u.owner != self.number: continue
            if not u.base: continue
            self._baseUnits.append(u)
        return self._baseUnits
    ############################################################################
    @property
    def loc(self):
        if self.position:   return c.cu.MapPoint(*self.position)
        else:               return c.cu.MapPoint(0.0, 0.0)
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
        return [u for u in self._units.values() if \
            u.owner == self.number and not u.base]
    ############################################################################
    @property
    def upgradeReqs(self):
        """identify the producers and producing ability by extracting info """\
        """from tech tree objects"""
        ########################################################################
        def exists(code, unitList):
            """identify the unit in unitList that matches code, else None"""
            for existingUnit in unitList:
                if existingUnit.code == code:
                    return existingUnit
            return None
        ########################################################################
        def getTechAbilities(tech, done, unitAbils, u=None):
            if tech in done: return unitAbils
            done.add(tech) # remember this tech upgrade has already been processed
            cost, techUnit = max([(tu.cost.mineral, tu) for tu in \
                                    tech.producingAbility.producers])
            if not u:
                u = convertTechUnit( # this techUnit hasn't already been selected
                        techUnit, owner=self.number, position=pickValidMapLoc())
                unitAbils[u] = [] # selected a new unit; it also needs a container to hold the abilities it needs to execute
                supplyUnit = techUnit.matchingSupplyDef
                if supplyUnit.name == "Pylon": # protoss upgrade producing structures require pylon power
                    unitAbils[convertTechUnit(supplyUnit, owner=self.number,
                        position=u.position)] = [] # place the pylon directly next to the tech-producing unit
            for r in tech.requires:
                if r.isUnit:
                    if not exists(r.mType.code, unitAbils):
                        reqUnit = convertTechUnit( # this techUnit hasn't already been selected
                            r, owner=self.number, position=pickValidMapLoc())
                        unitAbils[reqUnit] = []
                elif r.isUpgrade:
                    getTechAbilities(r, done, unitAbils, u=u)
                else:
                    raise NotImplementedError(("unclear what to do with the "\
                        "requirement type %s")%(r))
            unitAbils[u].append(tech.producingAbility)
        ########################################################################
        ret = {}
        processedUpgrades = set()
        for tech in self.upgrades:
            getTechAbilities(tech, processedUpgrades, ret)
            # TODO -- ensure addons have their parent building
        return ret
    ############################################################################
    def display(self, indent=0, display=True):
        """pretty print ALL information about this player"""
        idt = " "*indent
        msg = []
        msg.append("%s%s"%(idt, self))
        msg.append("%s    %d unit(s):"%(idt, self.numUnits))
        for u in self.units:    msg.append("%s        %s"%(idt, u))
        msg.append("%s    %d upgrade(s):"%(idt, self.numUpgrades))
        for u in self.upgrades: msg.append("%s        %s"%(idt, u))
        if display:
            for m in msg:
                print(m)
        else:
            return os.linesep.join(msg)

