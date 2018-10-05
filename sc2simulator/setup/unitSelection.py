
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

from sc2simulator.setup.simpleSelection import selectSimpleUnits
from sc2simulator.setup.treeSelection import selectUnitList


################################################################################
def generatePlayerUnits(scenario, playerID, race, rules, location, mapData):
    if techtree: # acquire unit definitions
        playerUnits = selectUnitList(sc2techTree, race, rules, mapData)
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
    else: # select units without the sc2techTree
        for unitCode in selectSimpleUnits(race, rules, mapData): # generate unit codes and add the units to this scenario
            newUnit = scenario.updateUnit(position=location, owner=playerID,
                                          code=unitCode)


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

