
"""
PURPOSE: train a player using test scenarios.
"""

import argparse
import os
import sys
import time

from sc2maptool import selectMap
from sc2maptool.cli import getSelectionParams
from sc2maptool.cli import optionsParser as addMapOptions
from sc2gameLobby.gameConfig import Config
from sc2gameLobby.scenarioEditor import launchEditor

from sc2simulator.__version__ import __version__
from sc2simulator import constants as c
from sc2simulator.setup import getSetup

# TODO -- launch game, apply a predefined setup and play as a human
# TODO -- perform coverage check by adding launch point in the code

# TODO -- place units in map (without sc2maps)
# TODO -- unit selection without sc2techTree
# TODO -- launch game, apply a predefined setup and play as a ai/bot

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
    mainOptions.add_argument("--custom"         , action="store_true"   , help="play customized scenario(s) toward your own objectives using specified map")
    mainOptions.add_argument("--join"           , action="store_true"   , help="join another player's custom scenarior setup (your race is determined by the host)")
    simControlO = parser.add_argument_group('Gameplay control options')
    simControlO.add_argument("--loops"          , default=1,    type=int, help="the number of learning iterations performed per test.", metavar="INT")
    simControlO.add_argument("--players"        , default=""            , help="the ladder player name(s) to control a player (comma separated).", metavar="NAMES")
    addMapOptions(parser) # ensure map selection options are also added
    predefOptns = parser.add_argument_group('Predefined Scenario options (from the editor)')
    predefOptns.add_argument("--cases"          , default=""            , help="the specific sc2 bank setup names (comma separated)", metavar="NAMES")
    newGenOptns = parser.add_argument_group('Dynamically generated composition options')
    newGenOptns.add_argument("--duration"       , default=c.DEF_DURATION, help="how long this generated scenario should last")
    newGenOptns.add_argument("--player1race"    , default=c.RANDOM, choices=c.types.SelectRaces.ALLOWED_TYPES,
                                                                          help="the race player 1 will play (default: random)")
    newGenOptns.add_argument("--player2race"    , default=c.RANDOM, choices=c.types.SelectRaces.ALLOWED_TYPES,
                                                                          help="the race player 2 will play (default: random)")
    newGenOptns.add_argument("--player1loc"     , default=""            , help="where player 1's army will be clustered", metavar="X,Y")
    newGenOptns.add_argument("--player2loc"     , default=""            , help="where player 2's army will be clustered", metavar="X,Y")
    newGenOptns.add_argument("--distance"       , default=13,   type=int, help="the distance between each player's army (if both player's army locations aren't specified)", metavar="NUMBER")
    newGenOptns.add_argument("--unitsMin"       , default=1,    type=int, help="the minimum number of units each player shall control")
    newGenOptns.add_argument("--unitsMax"       , default=10,   type=int, help="the maximum number of units each player shall control")
    sc2mapsOpts = parser.add_argument_group('Dynamic composition options WITHOUT sc2maps package')
    sc2mapsOpts.add_argument("--dimensions"     , default="150,150"     , help="provide maximum map dimensions", metavar="X,Y")
    techTreeOpt = parser.add_argument_group('Dynamic composition options with sc2techTree package')
    techTreeOpt.add_argument("--mineral"        , default=99999,type=int, help="the target amount of mineral of each army composition", metavar="INT")
    techTreeOpt.add_argument("--vespene"        , default=99999,type=int, help="the target amount of vespene of each army composition", metavar="INT")
    techTreeOpt.add_argument("--supply"         , default=99999,type=int, help="the maximum supply each army composition will consume", metavar="INT")
    techTreeOpt.add_argument("--maxdps"         , default=99999,type=int, help="the target amount of total dps (damage per second) of each army composition", metavar="NUMBER")
    techTreeOpt.add_argument("--maxhp"          , default=99999,type=int, help="the target amount of total hp (hit points) of each army composition", metavar="NUMBER")
    newGenOptns.add_argument("--energy"         , default=0,    type=int, help="each caster will have this energy or their max, whichever is lower")
    newGenOptns.add_argument("--energyMax"      , action="store_true"   , help="all casters have maximum energy")
    newGenOptns.add_argument("--energyRand"     , action="store_true"   , help="all casters have a random amount of energy between 0 and their maximum")
   #newGenOptns.add_argument("--upgrades"       , default=""            , help="")
    techTreeOpt.add_argument("--allowDefense"   , action="store_true"   , help="whether defensive buildings ")
    techTreeOpt.add_argument("--air"            , action="store_true"   , help="all generated units must be air units")
    techTreeOpt.add_argument("--ground"         , action="store_true"   , help="all generated units must be non-air units")
    #trainContrl = parser.add_argument_group('Training control options')
    #trainContrl.add_argument("--learn"          , action="store_true"   , help="perform learning after each iteration.")
    return parser


################################################################################
def main(options=None):
    if options == None: # if not provided, assume options are provided via command line
        options = optionsParser().parse_args()
        sys.argv = sys.argv[:1] # remove all arguments to avoid problems with absl FLAGS :(
    specifiedMap = selectMap(
        options.mapname,
        excludeName =options.exclude,
        closestMatch=True, # force selection of at most one map
        **getSelectionParams(options))
    outTempName = specifiedMap.name + "_%d_%d." + c.SC2_REPLAY_EXT
    outTemplate = os.path.join(c.PATH_NEW_MATCH_DATA, outTempName)
    if options.editor:
        launchEditor(specifiedMap) # run the editor using the game modification
    elif options.regression:
        batteries = options.test.split(",")
        # TODO -- run each test battery
    elif options.custom:
        cfg = Config(themap=specifiedMap)
        scenarios = getSetup(specifiedMap, options, cfg)
        for scenario in scenarios:
            epoch = int(time.time())
            # TODO -- load scenario specific
            cfg.scenario = scenario # each scenario needs to set up its own designated units
            for curLoop in range(options.loops): # each loop of each scenario gets its own unique replay
                cfg.replay = outTemplate%(epoch, curLoop)
                print("outFile:", outFile)
                launcher.run(cfg)
    elif options.join:
        pass # TODO -- implement
    else:
        print("ERROR: must select a main option.  See --help.")

