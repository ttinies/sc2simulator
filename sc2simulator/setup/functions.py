
"""
Fully define a 'random' generated setup for the players per specified conditions
"""

import random

from sc2simulator import constants as c
from sc2simulator.scenarioMgr import Scenario, parseBankXml, getBankPath
from sc2simulator.setup.mapLocations import convertStrToPoint, defineLocs
from sc2simulator.setup.unitSelection import generatePlayerUnits


################################################################################
def getSetup(mapObj, options, cfg):
    """get the appropriate scenarios, whether predefined or custom generated"""
    if options.cases: # use preloaded cases
        scenarios = []
        try:
            bankName = getBankPath(mapObj.name) # select the bank repository from the specified map
            bank = parseBankXml(bankName) # load the bank's defined scenarios
        except:
            print("ERROR: failed to load specified bank '%s'"%(mapObj.name))
            return scenarios
        for scenarioName in options.cases: # use options.cases to select which cases to run
            try: # attempt to retrieve the specified scenario from the bank
                scenarios.append(bank.scenarios[scenarioName])
            except:
                print("WARNING: scenario '%s' was not found in bank %s"%(
                    scenarioName, bankName))
        return scenarios
    else: # dynamically generate the scenario
        return generateScenario(mapObj, options, cfg)


################################################################################
def generateScenario(mapObj, options, cfg):
    """override this function is different generation methods are desired"""
    dim = None
    mData = None
    try:
        import sc2maps # closed source package
        mData = sc2maps.MapData(mapName=mapObj.name)
        dim = mData.dimensions.toCoords()
    except Exception: # ModuleNotFoundError isn't available in python 3.5
        dim = convertStrToPoint(options.dimensions)
    scenario = Scenario("custom%s"%mapObj.name)
    scenario.duration = options.duration
    #options.players # TODO -- add players to cfg ??
    d = options.distance # generate each player's locations
    mapLocs = defineLocs(options.player1loc, options.player2loc, d, dim)
    givenRaces = [options.player1race, options.player2race]
    for i, (pLoc, r) in enumerate(zip(mapLocs, givenRaces)):
        race = pickRace(r)
        generatePlayerUnits(scenario, i+1, race, options, pLoc, mapData=mData)
    return []


################################################################################
def pickRace(specifiedRace):
    """ensure the selected race for scenario generation is a race, not random"""
    if specifiedRace == c.RANDOM:
        choices = list(c.types.SelectRaces.ALLOWED_TYPES.keys())
        choices.remove(c.RANDOM) # ensure the new race isn't 'random' again
        newRace = random.choice(choices)
        return newRace
    return specifiedRace

