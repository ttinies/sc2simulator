
"""
PURPOSE: simulate a 1v1 scenario to test player actions.
"""

import argparse
import os
import re
import sys
import time

from sc2ladderMgmt import getLadder
from sc2maptool import selectMap
from sc2maptool.cli import getSelectionParams
from sc2maptool.cli import optionsParser as addMapOptions
from sc2gameLobby import launcher
from sc2gameLobby.gameConfig import Config
from sc2gameLobby.setScenario import launchEditor
from sc2gameLobby.versions import Version
from sc2players import getPlayer, PlayerPreGame

from sc2simulator.__version__ import __version__
from sc2simulator import constants as c
from sc2simulator.setup import getSetup


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
    simControlO.add_argument("--repeat"         , default=1,    type=int, help="the number of learning iterations performed per test.", metavar="INT")
    simControlO.add_argument("--duration"       , default=c.DEF_DURATION, help="how long this generated scenario should last (default: %d)"%c.DEF_DURATION, metavar="INT")
    simControlO.add_argument("--players"        , default=""            , help="the ladder player name(s) to control a player (comma separated).", metavar="NAMES")
    simControlO.add_argument("--replaydir"      , default=c.PATH_NEW_MATCH_DATA,
                                                                          help="the path where generated replays will be stored.", metavar="PATH")
    addMapOptions(parser) # ensure map selection options are also added
    predefOptns = parser.add_argument_group('Predefined Scenario options (from the editor)')
    predefOptns.add_argument("--cases"          , default=""            , help="the specific sc2 bank setup names (comma separated)", metavar="NAMES")
    newGenOptns = parser.add_argument_group('Dynamically generated composition options')
    newGenOptns.add_argument("--race"           , default=c.RANDOM, choices=c.types.SelectRaces.ALLOWED_TYPES,
                                                                          help="the race this agent will play (default: random)")
    newGenOptns.add_argument("--enemyrace"      , default=c.RANDOM, choices=c.types.SelectRaces.ALLOWED_TYPES,
                                                                          help="the race your enemy will play (default: random)")
    newGenOptns.add_argument("--loc"            , default=""            , help="where this agent's army will be clustered", metavar="X,Y")
    newGenOptns.add_argument("--enemyloc"       , default=""            , help="where the enemy's army will be clustered", metavar="X,Y")
    newGenOptns.add_argument("--distance"       , default=c.DEF_PLAYER_DIST, type=int, help="the distance between each player's armies when either player's location isn't specified (default: %.1f)"%c.DEF_PLAYER_DIST, metavar="NUMBER")
    newGenOptns.add_argument("--unitsMin"       , default=c.DEF_UNITS_MIN,   type=int, help="the minimum number of units each player shall control", metavar="INT")
    newGenOptns.add_argument("--unitsMax"       , default=c.DEF_UNITS_MAX,   type=int, help="the maximum number of units each player shall control", metavar="INT")
    newGenOptns.add_argument("--allowDefense"   , action="store_true"   , help="defense structures can also be selected as part of the unit count")
    newGenOptns.add_argument("--air"            , action="store_true"   , help="all generated units must be air units")
    newGenOptns.add_argument("--ground"         , action="store_true"   , help="all generated units must be non-air units")
    newGenOptns.add_argument("--defense"        , default=0,    type=int, help="include this many defensive structures for each player", metavar="INT")
    newGenOptns.add_argument("--detectors"      , default=0,    type=int, help="include this many mobile detectors for each player", metavar="INT")
    sc2mapsOpts = parser.add_argument_group('Dynamic composition options WITHOUT sc2maps package')
    sc2mapsOpts.add_argument("--dimensions"     , default="150,150"     , help="provide actual map dimensions", metavar="X,Y")
    techTreeOpt = parser.add_argument_group('Dynamic composition options with sc2techTree package')
    techTreeOpt.add_argument("--mineral"        , default=99999,type=int, help="the target amount of mineral of each army composition", metavar="INT")
    techTreeOpt.add_argument("--vespene"        , default=99999,type=int, help="the target amount of vespene of each army composition", metavar="INT")
    techTreeOpt.add_argument("--supply"         , default=99999,type=int, help="the maximum supply each army composition will consume", metavar="INT")
    techTreeOpt.add_argument("--maxdps"         , default=99999,type=int, help="the target amount of total dps (damage per second) of each army composition", metavar="NUMBER")
    techTreeOpt.add_argument("--maxhp"          , default=99999,type=int, help="the target amount of total hp (hit points) of each army composition", metavar="NUMBER")
    techTreeOpt.add_argument("--energy"         , default=0,    type=int, help="each caster will have this energy or their max, whichever is lower", metavar="NUMBER")
    techTreeOpt.add_argument("--energyMax"      , action="store_true"   , help="all casters have maximum energy")
    techTreeOpt.add_argument("--energyRand"     , action="store_true"   , help="all casters have a random amount of energy between 0 and their maximum")
    techTreeOpt.add_argument("--upgrades"       , default=""            , help="the names or IDs that your agent will start with", metavar="IDs")
    techTreeOpt.add_argument("--enemyUpgrades"  , default=""            , help="the names or IDs that your opponent will start with", metavar="IDs")
    #trainContrl = parser.add_argument_group('Training control options')
    #trainContrl.add_argument("--learn"          , action="store_true"   , help="perform learning after each iteration.")
    return parser


################################################################################
def defineLaunchOptions(scenario, replayOut):
    """create a configuration that is compatible with the game launcher"""
    class Dummy(): pass
    ret = Dummy()
    ret.search      = False
    ret.history     = False
    ret.nogui       = True
    ret.nofog       = True
    ret.scenario    = scenario
    ret.savereplay  = replayOut
    return ret


################################################################################
def main(options=None):
    if options == None: # if not provided, assume options are provided via command line
        parser = optionsParser()
        options = parser.parse_args()
        sys.argv = sys.argv[:1] # remove all arguments to avoid problems with absl FLAGS :(
    specifiedMap = selectMap(
        options.mapname,
        excludeName =options.exclude,
        closestMatch=True, # force selection of at most one map
        **getSelectionParams(options))
    outTempName = specifiedMap.name + "_%d_%d." + c.SC2_REPLAY_EXT
    outTemplate = os.path.join(options.replaydir, outTempName)
    if options.editor:
        launchEditor(specifiedMap) # run the editor using the game modification
    elif options.regression:
        batteries = options.test.split(",")
        raise NotImplementedError("TODO -- run each test battery")
    elif options.custom:
        playerNames = re.split("[,\s]+", options.players)
        if len(playerNames) != 2: # must specify two players for 1v1
            if not options.players:
                playerNames = ""
            raise ValueError("must specify two players, but given %d: '%s'"%(
                len(playerNames), playerNames))
        try: thisPlayer = getPlayer(playerNames[0]) # player name stated first is expected to be this player
        except Exception:
            print("ERROR: player '%s' is not known"%playerNames[0])
            return
        if options.race == c.RANDOM:    options.race = thisPlayer.raceDefault # defer to a player's specified default race
        cfg = Config(themap=specifiedMap,
                     ladder=getLadder("versentiedge"),
                     players=[PlayerPreGame(thisPlayer,
                              selectedRace=c.types.SelectRaces(options.race))],
                     mode=c.types.GameModes(c.MODE_1V1),
                     opponents=playerNames[1:],
                     whichPlayer=thisPlayer.name,
                     version=Version(), # always using the latest version
                     fogDisabled=True, # disable fog to be able to see, set and remove enemy units
                     **thisPlayer.initOptions, # ensure desired data is sent in callback
             )
        cfg.raw = True # required to be able to set up units using debug commands
        #cfg.display()
        scenarios = getSetup(specifiedMap, options, cfg)
        for scenario in scenarios:
            epoch = int(time.time()) # used for replay differentiation between each scenario
            failure = False
            for curLoop in range(1, options.repeat+1): # each loop of each scenario gets its own unique replay (count starting at one)
                outFile = outTemplate%(epoch, curLoop)
                launchOpts = defineLaunchOptions(scenario, outFile)
                failure = launcher.run(launchOpts, cfg=cfg)
                if failure: break
            if failure: break
    elif options.join:
        raise NotImplementedError("TODO -- implement remote play")
    else:
        parser.print_help()
        print("ERROR: must select a main option.")

