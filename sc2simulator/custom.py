
from sc2simulator.setupGeneration import generateScenario
from sc2simulator.scenarioMgr import parseBankXml, getBankPath


################################################################################
def getSetup(mapObj, options):
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
        return generateScenario(mapObj, options)

