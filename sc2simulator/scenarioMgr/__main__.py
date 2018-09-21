
"""Simple test of the scenarioMgr package"""

import os

from sc2simulator import constants as c
from sc2simulator.scenarioMgr import getBankPath, parseBankXml

if __name__=="__main__":
    xmlfile = getBankPath("test2")
    parseBankXml(xmlfile, debug=True)

