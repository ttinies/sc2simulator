
"""
Automatically generate a 'random' unit composition setup for two players using
an approximately equivalent resource values for each player.  The races of each
player are random unless specifically declared.
"""

import random
import re

try:
    import sc2techTree # Versentiedge closed source package
    techtree = sc2techTree.getLastTree()
except Exception: # ModuleNotFoundError isn't available in python 3.5
    techtree = None

from sc2simulator import constants as c
from sc2simulator.setup.mapLocations import setLocation


################################################################################
def generatePlayerUnits(scenario, playerID, race, rules, location, mapData):
    if isinstance(mapData, tuple):  shape =  mapData[:2] # only use x,y
    else:                           shape = (mapData.maxX, mapData.maxY)
    available = set()
    if techtree: # acquire unit definitions
        ignoredTypes = {12, 31, 58, 85, 113, 128, 151, 501, 687, 892}
        for u in techtree._leaves[race].values():
            for p in u.produces:
                if any([ignoreType == p.mType for ignoreType in ignoredTypes]):
                    continue
                available.add(p)
        available = available
        playerUnits = selectUnitList(available, rules, mapData)
        for techUnit in playerUnits:
            allUnits = scenario.units.values()
            if techUnit.energyStart: # detected a caster
                energyMax = techUnit.energyMax
                if   rules.energy:      energyVal = min(rules.energy, energyMax)
                elif rules.energyMax:   energyVal = energyMax
                elif rules.energyRand:  energyVal = random.randint(0, energyMax)
                else:                   energyVal = techUnit.energyStart
            else:                       energyVal = 0
            newUnit = scenario.updateUnit(techUnit=techUnit, owner=playerID,
                                          position=location, energy=energyVal)
    else:
        raise NotImplementedError("TODO -- how to know what units are available without the techtree")


################################################################################
def selectUnitList(available, rules, mapData, numFails=0):
    """pick units that meet all criteria"""
    units = []
    newRules = copyRules(rules)
    motherShipPicked = False
    while len(units) < rules.unitsMax: # create units, but no more than the specified maximum
        u = pickRandomUnit(available, newRules, motherShipPicked)
        if u == None: # didn't find a new unit to add (criteria not met) => verify that this (finished) unit list meets conditions
            if rules.unitsMin < len(units): break # enough units were created; minimum num units condition met
            elif numFails < c.MAX_UNIT_GRP_TRIES: # repick units to better meet conditions
                print("Criteria failed %d times; unit selection has restarted"%(
                    numFails + 1))
                return selectUnitList(available, rules, mapData, numFails+1)
            else: # attempted to generate unit + conditions too many times
                print("FAILED to select units after %d attempts."%(numFails))
                return []
        else: # picked a unit successfully; attempt to pick more!
            if u.name == "Mothership": motherShipPicked = True # ensure that at most only one mothership can be picked
            units.append( u )
    return units


################################################################################
def pickRandomUnit(choices, rules, ms=False):
    ############################################################################
    def isValidSelection(unit):
        """verify that this unit doesn't violate any of the determined rules"""
        if not unit.isUnit:                  return False
        if unit.isStructure:
            if not unit.weapons:             return False # only defense structures are allowed units
            if not rules.allowDefense:       return False # defense structures are only allowed if specified
        if  rules.air    and not unit.isAir: return False
        if  rules.ground and     unit.isAir: return False
        if  unit.dps     > rules.maxdps:     return False
        if  unit.hits    > rules.maxhp:      return False
        cost = unit.cost
        if  cost.mineral > rules.mineral:    return False
        if  cost.vespene > rules.vespene:    return False
        if -cost.supply  > rules.supply:     return False
        if ms and unit.name == "Mothership": return False # at most one mothership can be picked
        return True
    ############################################################################
    def confirmSelection(unit):
        """apply this unit's properties against rule accumulations"""
        rules.mineral -= unit.cost.mineral
        rules.vespene -= unit.cost.vespene
        rules.supply  += unit.cost.supply
        rules.maxdps  -= unit.dps
        rules.maxhp   -= unit.healthMax
        return unit
    ############################################################################
    if techtree: # only perform detailed selection when sc2techTree is available
        choices = list(choices) # copy, preparing for bad item removal
        while True: # ensure selection hasn't been considered already
            try:    selection = random.choice(choices)
            except: return None # when no choices remain, no selection can occur
            if isValidSelection(selection): # if selected unit fails criteria, pick a different unit
                break
            choices.remove(selection) # this selection is an unsuccessful attempt
        return confirmSelection(selection)
    else:
        raise NotImplementedError("TODO")


################################################################################
def copyRules(originals):
    """create a similarly structured object as the provided options, but one"""\
    """ which can be safely modified"""
    class Dummy(): pass
    ret = Dummy()
    ret.mineral         = originals.mineral
    ret.vespene         = originals.vespene
    ret.supply          = originals.supply
    ret.maxdps          = originals.maxdps
    ret.maxhp           = originals.maxhp
    ret.allowDefense    = originals.allowDefense
    ret.air             = originals.air
    ret.ground          = originals.ground
    ret.unitsMin        = originals.unitsMin
    ret.unitsMax        = originals.unitsMax
    return ret


################################################################################
def generateUpgrades(scenario, playerID, options):
    """identify the upgrades corresponding to the specified options"""
    if playerID == 1:   upgradeStr = options.upgrades
    else:               upgradeStr = options.enemyUpgrades
    if not upgradeStr: return # upgrades weren't specified for this player
    if not techtree:
        raise ValueError(("cannot determine upgrades without the sc2techTree "\
            " (given: %s)")%(upgradeStr))
    for techPart in re.split("[,:;]+", upgradeStr):
        try:
            techKey = int(techPart)
            tech = sc2techTree.getUpgradeByID(techKey)[0]
        except ValueError: # not an integer -- assume an exact match key string
            techKey = techPart
            try:  tech = sc2techTree.getUpgrade(techKey)
            except KeyError:
                raise KeyError("could not identify upgrade: '%s'"%(techKey))
        except IndexError:
            raise IndexError("could not identify upgrade ID: '%s'"%(techKey))
        scenario.addUpgrade(playerID, tech)

