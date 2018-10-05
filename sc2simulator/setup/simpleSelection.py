
import random

from sc2simulator.setup.simpleRaceMap import codeMap


################################################################################
def selectSimpleUnits(race, rules, mapData):
    ############################################################################
    def pick(choices, count=1):
        choices = list(choices)
        return [random.choice(choices) for i in range(count)]
    ############################################################################
    ret = []
    available = set()
    if rules.allowDefense:  available |= codeMap[race]["defense"]
    if rules.air:           available |= codeMap[race]["air"]
    if rules.ground:        available |= codeMap[race]["ground"]
    elif not rules.air: # if neither air nor ground are specified, select both air + ground
                            available |= codeMap[race]["air"]
                            available |= codeMap[race]["ground"]
    if not rules.detectors: available |= codeMap[race]["detection"]
    if rules.defense:
        ret += pick(codeMap[race]["defense"], rules.addDefense)
    if rules.detectors:
        ret += pick(codeMap[race]["detection"], rules.detectors)
    ret += pick(available, count=random.randint(rules.unitsMin, rules.unitsMax))
    return ret

