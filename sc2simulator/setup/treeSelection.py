
"""
unit selection that requires the sc2techTree package
"""

import random

from sc2simulator import constants as c
from sc2simulator.setup.simpleRaceMap import codeMap


################################################################################
def selectUnitList(treeMod, race, rules, mapData, numFails=0):
    """pick units that meet all criteria"""
    units = []
    newRules = copyRules(rules)
    motherShipPicked = False
    available = set()
    tree = treeMod.getLastTree()
    ignoredTypes = {12, 31, 58, 85, 113, 128, 151, 501, 687, 892}
    for u in tree._leaves[race].values():
        for p in u.produces:
            if any([ignoreType == p.mType for ignoreType in ignoredTypes]):
                continue
            available.add(p)
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
    if rules.defense:
        remaining = int(rules.defense)
        available = [treeMod.getUnitByID(code)[0] \
            for code in codeMap[race]["defense"]]
        while remaining > 0:
            newU = random.choice(available)
            units.append(newU)
            remaining -= 1
    if rules.detectors:
        remaining = int(rules.detectors)
        available = [treeMod.getUnitByID(code)[0] \
            for code in codeMap[race]["detection"]]
        while remaining > 0:
            newU = random.choice(available)
            units.append(newU)
            remaining -= 1
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
    choices = list(choices) # copy, preparing for bad item removal
    while True: # ensure selection hasn't been considered already
        try:    selection = random.choice(choices)
        except: return None # when no choices remain, no selection can occur
        if isValidSelection(selection): # if selected unit fails criteria, pick a different unit
            break
        choices.remove(selection) # this selection is an unsuccessful attempt
    return confirmSelection(selection)


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

