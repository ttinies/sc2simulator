
import os

from sc2common.constants import *
from sc2common import containers as cu
from sc2common import constants_shapes as cs
from sc2common import commonUtilFuncs as cf
from sc2common import types


DEF_DURATION = 15
PATH_NEW_MAPS = ""
PATH_BANKS = os.path.join(USER_HOME_DIR, "Documents", "StarCraft II", "Banks")
MAX_MAP_PICK_TRIES = 30
MAX_UNIT_GRP_TRIES = 10
MAX_TAG = 65536 # 0x0000 - 0xFFFF

