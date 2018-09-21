

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

