[![PyPI](https://img.shields.io/pypi/v/sc2simulator.svg)](https://pypi.org/project/sc2simulator/)
[![Build Status](https://travis-ci.org/ttinies/sc2simulator.svg?branch=master)](https://travis-ci.org/ttinies/sc2simulator)
[![Coverage Status](https://coveralls.io/repos/github/ttinies/sc2simulator/badge.svg?branch=master)](https://coveralls.io/github/ttinies/sc2simulator?branch=master)
![Crates.io](https://img.shields.io/crates/l/rustc-serialize.svg)

# [Starcraft 2 Scenario Simulator](https://github.com/ttinies/sc2simulator)

#### Editor Screenshots

![editor -- roach is having a bad day](https://github.com/ttinies/sc2simulator/blob/master/docs/example_editor_01.jpg?raw=true)
![reapers vs lurkers](https://github.com/ttinies/sc2simulator/blob/master/docs/example_editor_03.jpg?raw=true)
![big choke battle](https://github.com/ttinies/sc2simulator/blob/master/docs/example_editor_02.jpg?raw=true)

#### Example simulator gameplay

(Reserved)

## About

This package's purpose to enable an interface for multiple players with various
Starcraft 2 agents to play a variety of pre-built or generated scenarios.  The
uses of this package are diverse, including AI agent training.

#### Status

**This package is in beta testing.**  Reference the defined [issues](https://github.com/ttinies/sc2simulator/issues)
to get a better idea of what is and is not working.  If something is discovered
to not be working, kindly do submit a new issue!

#### Rationale: Why Create this Repository?

While a variety of situations can be encountered over the course of many, many
melee games, there are several problems with this approach.  Specific situations
occur infrequently, possibly once in the course of a match (which normally
elapses ~20 minutes, up to over an hour at realtime speed) and may not occur
even once in many hundreds of matches.  This makes training difficult, slow
and require significantly more data.

By allowing situations to be created artificially, the user may test their
agent's functionality against it.  A specific battery of tests can be created
to compare performance of implementations against each other.  It also allows
for a specific type of situation to be created and tested quickly with slight
variations to enhance the player's learing speed.

## Functionality

#### Brief Overview

1. The simulator is invoked with specific options.

    * *The scenario mini-editor:* if the editor is invoked using --editor, a
    mini-editor appears to create or modify a scenario for play.  Unless the
    option is selected to also play the specified scenario, the editor closes.

    * *Regression testing:* when specifying --regression, a predefined battery of
    test scenarios is run using same functionality as custom games except scenario
    selection criteria are ignored in favor of each predefined scenario setup.
    
    * *Custom Scenarios:* The --custom option allows a player to set up a specific
    scenario to test, including the opponent's setup.  Each agent joins an existing
    scenario by using the --join option.
    
    * *Join:* The --join option allows a player to specify at most its own agent and
    optionally its required opponent.  All other parameters of the scenario are
    determined by the scenario creator.

2. Each player connects to the game automatically via the sc2gameLobby package.
   This occurs by default over Versentiedge's public matchmaking ladder server.
3. Once in-game, the scenario is setup.

    * if upgrades are specified, each player's client controller creates the
    tech producing units and (with cheats enabled) automatically researches
    the scenario-specified upgrades.  This will elapse at most an additional
    21 seconds on top of the specified scenario duration.  (This is required
    due to behavior in Blizzard's API protocol.)

    * The host removes existing units and then creates the units as specified
    by the scenario.

4. gameplay continues for as long as is specified using the --duration option.
5. the scenario can be repeated multiple times as specified using the --loops
   option.  Steps 2-4 are repeated for each loop of the same scenario.
6. A replay is saved locally by each player for each scenario iteration.

#### Example Commands

`python -m sc2simulator --editor --mapname=parasite`

`python -m sc2simulator --custom --unitsMax=7 --ground --players=defaulthuman,blizzbot5_hard --ladder=True`

`python -m sc2simulator --race=zerg --enemyrace=terran --defense=3 --year=2018 --season=3 --players=defaulthuman,blizzbot5_hard`

`python -m sc2simulator --cases=<yourScenarioName> --mapname=MechDepot --players=test,blizzbot5_hard`

NOTE: selecting player 'test' or 'defaulthuman' will allow you to play as a human.
Playing with your own custom agent requires additional player setup to define
the agents setup and execution/callback functions.

#### Cautions

* If your installed Starcraft 2 Maps directory (e.g. C:\Program Files (x86)\Starcraft II\Maps),
these maps can be deleted by the editor.  Maps of the same name in subfolders
beneath Maps\... are safe.

* Including tech upgrades and some features (such as balancing on mineral cost,
unit dps, etc.) are only available if you have also access to the sc2techTree
package.  If interested, petition @ttinies.

* When playing with your AI/bot, your bot may need to wait a few moments in-game
before the scenario is fully setup.

