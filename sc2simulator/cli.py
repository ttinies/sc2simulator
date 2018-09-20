
"""
PURPOSE: train a player using test scenarios.
"""

import argparse
import sys

from sc2maptool import selectMap
from sc2maptool.cli import getSelectionParams
from sc2maptool.cli import optionsParser as addMapOptions
from sc2gameLobby.scenarioEditor import launchEditor

from sc2simulator.__version__ import __version__


################################################################################
def optionsParser(passedParser=None):
    if passedParser == None:
        parser = argparse.ArgumentParser(
           #usage="python %s"%__file__,
            description=__doc__,
            epilog="version: %s"%__version__)
    else:
        parser = passedParser
    mainOptions = parser.add_argument_group('Training Simulator Operations')
    mainOptions.add_argument("--editor"         , action="store_true"   , help="launch the scenario editor")
    mainOptions.add_argument("--regression"     , default=""            , help="run a predefined battery of test cases", metavar="NAMES")
    mainOptions.add_argument("--training"       , action="store_true"   , help="perform testing using specified map + scenarios")
    addMapOptions(parser)
    #mapSelOptns = parser.add_argument_group('MAP SELECTION OPTIONS')
    #mapSelOptns.add_argument("--map"            , default=""            , help="the specific map", metavar="NAME")
    #mapSelOptns.add_argument("--year"           , default=""            , help="the specific map", metavar="NAME")
    predefOptns = parser.add_argument_group('Predefined Scenario options (from the editor)')
    #predefOptns.add_argument("--nogui"          , action="store_true"   , help="launch game directly using command-line arguments formatted as key=value.")
    predefOptns.add_argument("--cases"          , default=""            , help="the specific sc2 bank setup names (comma separated)", metavar="NAMES")
    newGenOptns = parser.add_argument_group('Dynamically generated composition options')
    newGenOptns.add_argument("--locPlayer1"     , default=""            , help="where player 1's army will be clustered", metavar="X,Y")
    newGenOptns.add_argument("--locPlayer2"     , default=""            , help="where player 2's army will be clustered", metavar="X,Y")
    newGenOptns.add_argument("--distance"       , default=20,  type=int , help="the distance between each player's army (if both player's army locations aren't specified)", metavar="NUMBER")
    newGenOptns.add_argument("--mineral"        , default=0,   type=int , help="the target amount of mineral of each army composition", metavar="INT")
    newGenOptns.add_argument("--vespene"        , default=0,   type=int , help="the target amount of vespene of each army composition", metavar="INT")
    newGenOptns.add_argument("--supply"         , default=16,  type=int , help="the maximum supply each army composition will consume", metavar="INT")
    newGenOptns.add_argument("--maxdps"         , default=0,   type=int , help="the target amount of total dps (damage per second) of each army composition", metavar="NUMBER")
    newGenOptns.add_argument("--maxhp"          , default=0,   type=int , help="the target amount of total hp (hit points) of each army composition", metavar="NUMBER")
    simControlO = parser.add_argument_group('Training control options')
    simControlO.add_argument("--loops"          , default=1, type=int   , help="the number of learning iterations performed per test.", metavar="INT")
    simControlO.add_argument("--players"        , default=""            , help="the ladder player name(s) to control a player (comma separated).", metavar="NAMES")
    #trainContrl = parser.add_argument_group('Training control options')
    #trainContrl.add_argument("--learn"          , action="store_true"   , help="perform learning after each iteration.")
    return parser


################################################################################
def main():
    options = optionsParser().parse_args()
    sys.argv = sys.argv[:1] # remove all arguments to avoid problems with absl FLAGS :(
    specifiedMap = selectMap(
        options.mapname,
        excludeName =options.exclude,
        closestMatch=True, # force selection of at most one map
        **getSelectionParams(options))
    print(dir(specifiedMap))
    print()
    print(specifiedMap)
    if options.editor:
        launchEditor(specifiedMap) # run the editor using the game modification
    elif options.regression:
        batteries = options.test.split(",")
        # TODO -- run each test battery
    elif options.training:
    
        pass
        # TODO -- select the bank repository from the specified map
        # TODO -- use options.cases to select which cases to run
        #launcher.run(options)
    else:
        print("ERROR: must select a main option.  See --help.")

