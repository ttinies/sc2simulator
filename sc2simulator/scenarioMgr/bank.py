
from sc2simulator import constants as c
from sc2simulator.setup.simpleRaceMap import codeMap


################################################################################
class Bank(object):
    """contain all defined scenarios for a given map represented by 'name'"""
    ############################################################################
    def __init__(self, name):
        self.name = name
        self.scenarios = {}
    ############################################################################
    def __str__(self):  return self.__repr__()
    def __repr__(self):
        return "<%s %s scenarios:%d>"%(self.__class__.__name__, self.name, len(self))
    ############################################################################
    def __len__(self):
        return len(self.scenarios)
    ############################################################################
    def __iter__(self):
        return iter(self.scenarios.values())
    ############################################################################
    def __getitem__(self, key):
        return self.scenarios[key]
    ############################################################################
    @property
    def available(self):
        """the names of the available scenarios"""
        return list(self.scenarios.keys())
    ############################################################################
    def addScenario(self, scenario):
        """ensure the provided scenario is identified in this bank"""
        if scenario.name in self.scenarios:
            raise KeyError("cannot add '%s' because %s is already defined"%(
                scenario.name, scenario))
        self.scenarios[scenario.name] = scenario
    ############################################################################
    def initPlayers(self):
        """all players must define their initial starting positions and races"""
        ########################################################################
        def findUnitRace(unit):
            """locate the race in predefined data of unit given its name"""
            name = unit.nametype
            for race, data in codeMap.items():
                for uType, codes in data.items():
                    for code, target in codes.items():
                        if name != target:  continue
                        unit.code = code # also update the unit's code type
                        return race
            print("WARNING: failed to locate the race of unit '%s'."%name)
            return None
        ########################################################################
        unitsToIgnore = { # ignore these units which are saved in the XML, but not placed
            "BroodlingEscort",
            "Broodling",
        }
        for s in self.scenarios.values():
            for u in list(s.units.values()):
                if u.nametype in unitsToIgnore:
                      del s.units[u.tag] # unit is ignored
                else: u.tag = 0 # unit tag is reset for general use
            for p in s.players.values():
                if p.position == None: # player's location is not already defined
                    units = p.units
                    x, y = (0, 0)
                    for u in units:
                        uX, uY = u.position[:2]
                        x += uX
                        y += uY
                    numUnits = len(units)
                    p.position = (x / numUnits, y / numUnits) # average position is calculated as the player's starting location
                if p.race == None: # pick the appropriate race for this player
                    allowed = list(c.types.ActualRaces.ALLOWED_TYPES)
                    try:    allowed.remove(None)
                    except: pass
                    allowed = dict(zip(allowed, [0]*len(allowed))) # unit counter is initialized
                    for u in p.units:
                        race = findUnitRace(u)
                        if race:
                            allowed[race] += 1
                    count, p.race = max([
                        (count, r) for r, count in allowed.items()
                    ])

