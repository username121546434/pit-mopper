"""Has all constants and variable for all of the files"""
import os
from datetime import datetime
import sys

if os.name == 'nt':
    # Use the local appdata folder if on Windows
    APPDATA: str = os.path.join(os.getenv('LOCALAPPDATA'), 'Pit Mopper') # type: ignore
    # *.xbm is Linux specific, use *.ico instead
    LOGO = "data\\images\\windows_icon.ico"
else:
    # Otherwise, assume we are are on Linux
    APPDATA: str = os.path.join(os.getenv('HOME'), '.pitmopper')
    # *.ico is Windows specific, use *.xbm instead
    # for some reason, on linux the path to the icon has to be prefixed with an "@"
    LOGO = '@' + "data/images/linux_icon.xbm"

DEBUG = os.path.join(APPDATA, 'debug')
HOME: str = os.getenv('HOME') # type: ignore

if not os.path.exists(DEBUG):
    os.makedirs(DEBUG)

STRFTIME = r'%A %B %d, %I:%M %p %Y %Z'
HIGHSCORE_TXT = os.path.join(APPDATA, 'highscore.txt')
MAX_ROWS_AND_COLS = float('inf')
MIN_ROWS_AND_COLS = 4
DARK_MODE_BG = '#282828'
DARK_MODE_FG = '#FFFFFF'
DEFAULT_BG = '#f0f0f0f0f0f0' if os.name == 'nt' else "#d9d9d9"
DEFAULT_FG = '#000000'
CURRENT_BG = DEFAULT_BG
CURRENT_FG = DEFAULT_FG
APP_CLOSED = False
VERSION = '2.1.0'
SQUARES_FONT = r"data\fonts\DSEG7ClassicMini-Bold.ttf"
GAME_ID_MIN = 1000
GAME_ID_MAX = 9999
APP_FILE_EXT = '.ptmpr'
LAST_GAME_FILE = os.path.join(APPDATA, f'last{APP_FILE_EXT}')

# sound effects
CLICK_SOUND = 'data/sounds/click.wav'
FLAG_SOUND = 'data/sounds/flag.wav'
START_SOUND = 'data/sounds/game_start.wav'

dark_mode = False
del_data = 'none'
debug_log_file = os.path.join(DEBUG, f"{datetime.now():{STRFTIME.replace(':', '-')}}.log")

PROTOCOL = 'ptmpr'
IS_COMPILED: bool = getattr(sys, 'frozen', False)

if IS_COMPILED:
    # when compiled to exe file
    APP_EXE = sys.executable
else:
    # when running from normal python file
    APP_EXE = os.path.realpath(__file__)

APP_DIR = os.path.dirname(APP_EXE)
