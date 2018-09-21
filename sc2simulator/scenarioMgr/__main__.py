
"""Simple test of the scenarioMgr package"""

import os

from sc2simulator import constants as c
from sc2simulator.scenarioMgr import parseBankXml


if __name__=="__main__":
    xmlfile = os.path.join(c.PATH_BANKS, "test2.SC2Bank")
    parseBankXml(xmlfile, debug=True)

