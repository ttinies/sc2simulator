
"""
Fully define a 'random' generated setup for the players per specified conditions
"""

import random
import re

from sc2simulator import constants as c
from sc2simulator.scenarioMgr import Scenario, parseBankXml, getBankFilepath
from sc2simulator.setup import mapLocations
from sc2simulator.setup.mapLocations import convertStrToPoint, defineLocs
from sc2simulator.setup.unitSelection import generateUpgrades
from sc2simulator.setup.unitSelection import generatePlayerUnits


################################################################################
def getSetup(mapObj, options, cfg):
    """get the appropriate scenarios, whether predefined or custom generated"""
    mdata = None
    try:
        import sc2maps # Versentiedge closed source package
        mData = sc2maps.MapData(mapName=mapObj.name)
        mapLocations.mapDimensions = mData.dimensions.toCoords()
        mdata = mData.placement.halfGrid
    except Exception: # ModuleNotFoundError isn't available in python 3.5
        try:
            if not options.dimensions:  raise ValueError("must provide dims")
            mapLocations.mapDimensions = convertStrToPoint(options.dimensions)
            if len(mapLocations.mapDimensions) < 2:
                raise ValueError("must provide valid dimensions (given: %s)"%(
                    mapLocations.mapDimensions))
        except ValueError:
            print("ERROR: must provide valid map dimensions (given: %s"%(
                options.dimensions))
            return []
        mdata = mapLocations.mapDimensions
    scenarios = []
    if options.cases: # use preloaded cases
        try:
            bankName = getBankFilepath(mapObj.name) # select the bank repository from the specified map
            bank = parseBankXml(bankName) # load the bank's defined scenarios
        except:
            print("ERROR: failed to load specified bank '%s'"%(mapObj.name))
            return scenarios
        for scenarioName in re.split("[,;:]+", options.cases): # use options.cases to select which cases to run
            try: # attempt to retrieve the specified scenario from the bank
                scenarios.append(bank.scenarios[scenarioName])
            except:
                print("WARNING: scenario '%s' was not found in bank %s"%(
                    scenarioName, bankName))
    else: # dynamically generate the scenario
        scenarios += generateScenario(mapObj, options, cfg, mdata)
    return scenarios


################################################################################
def generateScenario(mapObj, options, cfg, mdata):
    """override this function is different generation methods are desired"""
    scenario = Scenario("custom%s"%mapObj.name)
    scenario.duration = options.duration
    d = options.distance # generate each player's locations
    mapLocs = defineLocs(options.loc, options.enemyloc, d)
    givenRaces = [options.race, options.enemyrace]
    for i, (pLoc, r) in enumerate(zip(mapLocs, givenRaces)):
        race = pickRace(r)
        pIdx = i + 1 # player indexes start at one, not zero
        scenario.addPlayer(pIdx, loc=pLoc, race=race)
        generatePlayerUnits(scenario, pIdx, race, options, pLoc, mapData=mdata)
        try:    generateUpgrades(scenario, pIdx, options)
        except Exception as e:
            print("ERROR: %s"%e)
            return []
        #scenario.players[pIdx].upgradeReqs
        #for u in scenario.newBaseUnits(pIdx):
        #    print("%d  %s"%(pIdx, u))
        #print()
        #for u in scenario.players[pIdx].baseUnits:
        #    print("%d  %s"%(pIdx, u))
        #print()
    return [scenario]


################################################################################
def pickRace(specifiedRace):
    """ensure the selected race for scenario generation is a race, not random"""
    if specifiedRace == c.RANDOM:
        choices = list(c.types.SelectRaces.ALLOWED_TYPES.keys())
        choices.remove(c.RANDOM) # ensure the new race isn't 'random' again
        newRace = random.choice(choices)
        return newRace
    return specifiedRace

