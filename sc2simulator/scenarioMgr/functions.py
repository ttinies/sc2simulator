
import os
import re
import xml.etree.ElementTree

from sc2simulator import constants as c
from sc2simulator.scenarioMgr.bank import Bank
from sc2simulator.scenarioMgr.scenario import Scenario


################################################################################
def xmlChildrenToDict(node):
    """limited conversion power, but appropriately types game value"""
    ret = {}
    for child in node.getchildren():
        key, value = child.items()[0] # still need to convert key into appropriate type
        if   key == "fixed":    value = float(value)
        elif key == "string":   pass # no type conversion is necessary
        elif key == "int":      value = int(value)
        elif key == "point":    value = [float(v) for v in value.split(",")]
        else:
            print("WARNING: could not interpret node key '%s' of %s"%(
                key, child))
            continue
        newtag = child.tag.lower()
        if   newtag == "type":      newtag = "nametype" # rename certain keys to match object definition
        elif newtag == "xpcount":   newtag = "xp"
        ret[newtag] = value
    return ret


################################################################################
def getBankPath(bankName):
    """identify the absolute path to the provided bankName"""
    return os.path.join(c.PATH_BANKS, "%s.%s"%(bankName, c.SC2_BANK_EXT))


################################################################################
def getSectionByName(sections, name, key="name", default=None):
    """identify the first section with matching key among 'sections'"""
    for s in sections:
        if name == s.get(key):
            return s
    return default
    

################################################################################
def getSectionByNameAll(sections, name, key="name"):
    """filter all sections down to only those with matching names/tags"""
    return [s for s in sections if name == s.get(key)]


################################################################################
def parseBankXml(xmlpath, debug=False):
    """interpret scenario bank XML data into usable python objects"""
    root = xml.etree.ElementTree.parse(xmlpath).getroot()
    bankName = re.sub("\..*", "", os.path.basename(xmlpath)) # strip path and extension
    retBank = Bank(bankName)
    sections = root.getchildren()
    caseNameSection = getSectionByName(sections, "TestCases") # should be the first section, but 'search' anyway
    if not caseNameSection: return retBank # must define the "TestCases" section
    sections.remove(caseNameSection) # this meta section doesn't define scenario + player data
    for key in caseNameSection.getchildren(): # acquire each scenario's meta data
        name = key.get("name")
        s = Scenario(name)
        retBank.addScenario(s)
    for s in sections: # iterate all scenario + player sections for data
        sectionNames = s.get("name").split("|")
        scenarioName = sectionNames[0]
        playerID     = int(re.findall("P(\d+)", sectionNames[1]).pop())
        dataType     = sectionNames[2]
        scenario = retBank[scenarioName]
        if dataType == "UnitIndex":
            for key in s.getchildren(): # ensure all tags are represented as units in this scenario
                tag = key.get("name")
                scenario.addUnit(tag)
        elif dataType == "UnitData":
            for key in s.getchildren(): # load unit data for all players in this scenario
                unitMeta = key.get("name").split("|")
                unitTag  = int(unitMeta[0])
                unitAttr = unitMeta[1].lower()
                attrs    = xmlChildrenToDict(key)
                if len(attrs) == 1 and list(attrs.keys())[0] == "value":
                    attrs = {unitAttr : attrs["value"]}
                u = scenario.updateUnit(unitTag, owner=playerID, **attrs)
        elif dataType == "Upgrades":
            for key in s.getchildren(): # ensure all tags are represented as units in this scenario
                value = xmlChildrenToDict(key)["value"]
                scenario.addUpgrade(playerID, value)
        else:
            print("WARNING: skipped unknown data type: %s"%dataType)
    if debug:
        print("*"*80)
        print(retBank)
        print("*"*80)
        for sName, scenario in retBank.scenarios.items():
            print(scenario)
            for p in scenario.players.values():
                p.display()
            print("*"*80)
    return retBank

