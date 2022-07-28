import os
from datetime import datetime

APPDATA = os.path.expanduser(r'~\AppData\Local\Pit Mopper')
DEBUG = APPDATA + r'\debug'
SW_HIDE = 0
SW_SHOW = 5
STRFTIME = r'%A %B %d, %I:%M %p %Y %Z'
HIGHSCORE_TXT = os.path.join(APPDATA, 'highscore.txt')
LOGO = "data\\images\\logo.ico"
MAX_ROWS_AND_COLS = 75
MIN_ROWS_AND_COLS = 4
DARK_MODE_BG = '#282828'
DARK_MODE_FG = '#FFFFFF'
DEFAULT_BG = '#f0f0f0f0f0f0'
DEFAULT_FG = '#000000'
CURRENT_BG = DEFAULT_BG
CURRENT_FG = DEFAULT_FG
APP_CLOSED = False
VERSION = '1.4.0'

dark_mode = False
del_data = 'none'
debug_log_file = os.path.join(DEBUG, f"{datetime.now().strftime(STRFTIME.replace(':', '-'))}.log")