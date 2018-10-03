
import random

from sc2simulator import constants as c
from sc2simulator.scenarioMgr.scenarioPlayer import ScenarioPlayer
from sc2simulator.scenarioMgr.scenarioUnit import ScenarioUnit, convertTechUnit
from sc2simulator.setup.mapLocations import pickCloserLoc, pickFurtherLoc


################################################################################
class Scenario(object):
    """contains all information required to set up a scenario"""
    ############################################################################
    def __init__(self, name):
        self.name = name
        self.players = {}
        self.units = {}
        self.upgrades = {}
        self.startloop = 1
        self.duration = c.DEF_DURATION
    ############################################################################
    def __str__(self):  return self.__repr__()
    def __repr__(self):
        return "<%s '%s' players:%s>"%(self.__class__.__name__,
            self.name, list(self.players.keys()))
    ############################################################################
    def addPlayer(self, idx, loc=None, race=None):
        """add a definition for a player within a Scenario"""
        idx = int(idx) # ensure value is an integer
        if idx in self.players:
            print("WARNING: attempted to add already existing player %d: %s"%(
                idx, self.players[idx]))
            return self.players[idx]
        upgradeList = []
        self.upgrades[idx] = upgradeList
        p = ScenarioPlayer(idx, self.units, upgradeList, pos=loc, race=race)
        self.players[idx] = p
    ############################################################################
    def addUnit(self, tag=0, newUnit=None, **attrs):
        """define a unit within a Scenario"""
        ############################################################################
        def genTag(minVal=150):
            usedUnits = self.units
            newTag = random.randint(minVal, c.MAX_TAG) # preselected tag for first unit
            while newTag in usedUnits: # new unit cannot share a tag with a known unit
                newTag = random.randint(minVal, c.MAX_TAG)
            return newTag
        ############################################################################
        if tag:     tag = int(tag) # ensure unit uid is always an integer
        else:       tag = genTag()
        if tag in self.units: # catch possible redundant definitions
            print("WARNING: unit tag %d already exists in %s as %s"%(
                tag, self, self.units[tag]))
            return
        if newUnit:
            if not isinstance(newUnit, ScenarioUnit):
                newUnit = convertTechUnit(newUnit, tag=tag, **attrs) # allow tech units to be converted into ScenarioUnits too!
        else:
            newUnit = ScenarioUnit(tag)
            newUnit.update(**attrs)
        self.units[tag] = newUnit
        return newUnit
    ############################################################################
    def addUpgrade(self, player, upgrade):
        """define an upgrade within a Scenario"""
        if player not in self.players:
            self.addPlayer(player)
        self.upgrades[player].append(upgrade)
    ############################################################################
    def newBaseUnits(self, playerID):
        """define a set of new 'base' units for the specified player"""
        player = self.players[playerID]
        if player.baseUnits: return player.baseUnits # don't generate more base units after the first time
        location = player.position
        x0, y0 = location[:2]
        if player.race == c.ZERG:
            off = 2 # zergOffset for creep tumors
            for i in range(0,2):
                newUnit = self.updateUnit(tag=0, base=True, # add units to scenario
                    nametype = "NydusNetwork",
                    code     = 95,
                    owner    = playerID,
                    position = pickCloserLoc(location, 5*i), # the game handles attempting to place multiple units on top of each other
                    energy   = 0,
                    life     = 850,
                    shields  = 0)
            for x, y in [(  0 ,-off), (-off,  0 ), (off,  0 ), ( 0 , off)]:
                          #(-off,-off), (-off, off), (off,-off), (off, off)]:
                targetX, targetY = location[:2]
                unitLoc = (targetX + x, targetY + y)
                newUnit = self.updateUnit(tag=0, base=True, # add units to scenario
                    nametype = "CreepTumorBurrowed",
                    code     = 137,
                    owner    = playerID,
                    position = unitLoc, # the game handles attempting to place multiple units on top of each other
                    energy   = 0,
                    life     = 50,
                    shields  = 0)
        elif player.race == c.PROTOSS:
            for i in range(0,4):
                newUnit = self.updateUnit(tag=0, base=True, # add units to scenario
                    nametype = "Pylon",
                    code     = 60,
                    owner    = playerID,
                    position = pickCloserLoc(location, 4*i), # the game handles attempting to place multiple units on top of each other
                    energy   = 0,
                    life     = 200,
                    shields  = 200)
        elif player.race == c.TERRAN:
            for i in range(0,4):
                newUnit = self.updateUnit(tag=0, base=True, # add units to scenario
                    nametype = "SupplyDepot",
                    code     = 19,
                    owner    = playerID,
                    position = pickCloserLoc(location, 4*i), # the game handles attempting to place multiple units on top of each other
                    energy   = 0,
                    life     = 400,
                    shields  = 0)
        else:  raise ValueError("bad race value: %s"%(player.race))
        return player.baseUnits
    ############################################################################
    def updateUnit(self, tag=0, techUnit=None, **attrs):
        """include more information to better represent the specified unit"""
        try: # lookup previously defined unit
            u = self.units[tag]
            u.update(**attrs) # assign attributes into unit
        except KeyError: # define a new unit
            u = self.addUnit(tag, newUnit=techUnit, **attrs)
            if u.owner and u.owner not in self.players: # ensure that this unit's owner is represented as a player
                self.addPlayer(u.owner)
        return u

