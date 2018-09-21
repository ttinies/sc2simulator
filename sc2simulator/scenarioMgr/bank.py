

################################################################################
class Bank(object):
    ############################################################################
    def __init__(self, name):
        self.name = name
        self.scenarios = {}
    ############################################################################
    def __str__(self):  return self.__repr__()
    def __repr__(self):
        return "<%s %s (%d)>"%(self.__class__.__name___, self.name, len(self))
    ############################################################################
    def __len__(self):
        return len(self.scenarios)
    def __getitem__(self, key):
        return self.scenarios[key]
    def addScenario(self, scenario):
        if scenario.name in self.scenarios:
            raise KeyError("cannot add '%s' because %s is already defined"%(
                scenario.name, scenario))
        self.scenarios[scenario.name] = scenario

