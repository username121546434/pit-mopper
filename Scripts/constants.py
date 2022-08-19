"""Has all constants and variable for all of the files"""
import os
from datetime import datetime

if os.name == 'nt':
    # Use the local appdata folder if on Windows
    APPDATA = os.path.join(os.getenv('LOCALAPPDATA'), 'Pit Mopper')
    # *.xbm is Linux specific, use *.
    LOGO = "data\\images\\windows_icon.ico"
else:
    # Otherwise, assume we are are on Linux
    APPDATA = os.path.join(os.getenv('HOME'), '.pitmopper')
    # *.ico is Windows specific, use *.xbm instead
    # for some reason, on linux the path to the icon has to be prefixed with an "@"
    LOGO = '@' + "data/images/linux_icon.xbm"

DEBUG = os.path.join(APPDATA, 'debug')

if not os.path.exists(DEBUG):
    os.makedirs(DEBUG)

SW_HIDE = 0
SW_SHOW = 5
STRFTIME = r'%A %B %d, %I:%M %p %Y %Z'
HIGHSCORE_TXT = os.path.join(APPDATA, 'highscore.txt')
MAX_ROWS_AND_COLS = 75
MIN_ROWS_AND_COLS = 4
DARK_MODE_BG = '#282828'
DARK_MODE_FG = '#FFFFFF'
DEFAULT_BG = '#f0f0f0f0f0f0' if os.name == 'nt' else "#d9d9d9"
DEFAULT_FG = '#000000'
CURRENT_BG = DEFAULT_BG
CURRENT_FG = DEFAULT_FG
APP_CLOSED = False
VERSION = '1.4.0'

dark_mode = False
del_data = 'none'
debug_log_file = os.path.join(DEBUG, f"{datetime.now():{STRFTIME.replace(':', '-')}}.log")