
import os

from sc2common.constants import *
from sc2common import containers as cu
from sc2common import constants_shapes as cs
from sc2common import commonUtilFuncs as cf
from sc2common import types


DEF_DURATION = 15
PATH_NEW_MAPS = ""
PATH_BANKS = os.path.join(USER_HOME_DIR, "Documents", "StarCraft II", "Banks")
PATH_HERE = os.path.dirname(os.path.abspath(__file__))
PATH_MPQ_EDITOR = os.path.join(PATH_HERE, "mpqeditor_en")
FILE_MPQ_EDITOR = "MPQEditor.exe"
PATH_MPQ_EDITOR_32BIT = os.path.join(PATH_MPQ_EDITOR, "Win32", FILE_MPQ_EDITOR)
PATH_MPQ_EDITOR_64BIT = os.path.join(PATH_MPQ_EDITOR, "X64"  , FILE_MPQ_EDITOR)
MAX_MAP_PICK_TRIES = 30
MAX_UNIT_GRP_TRIES = 10
MAX_TAG = 65536 # 0x0000 - 0xFFFF
DEF_PLAYER_DIST = 18
DEF_UNITS_MIN = 1
DEF_UNITS_MAX = 10

FILE_BANKLIST = "BankList.xml"
BANK_DATA = "\n".join([
    "<?xml version=\"1.0\" encoding=\"us-ascii\"?>",
    "<BankList>",
    "    <Bank Name=\"%s\" Player=\"1\"/>",
    "</BankList>",
    ""])

MPQ_CMD = "\"%s\" add \"%s\" \"%s\" %s"

