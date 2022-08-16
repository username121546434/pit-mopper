"""Main Python file, run it to play the game"""
import logging
import os
from tkinter import *
from tkinter import messagebox
from Scripts.app import App
from Scripts.constants import VERSION, DEBUG, debug_log_file
from Scripts.network import check_internet
from Scripts.console_window import get_console
from Scripts import multiplayer, single_player
import sys
get_console()

if not os.path.exists(DEBUG):
    os.makedirs(DEBUG)

with open(debug_log_file, 'w') as _:
    pass
from Scripts.base_logger import init_logger
init_logger()

logging.info('Loading...')
__version__ = VERSION
__license__ = 'GNU GPL v3, see LICENSE.txt for more info'

def run_single_player():
    window.destroy()
    single_player.main()
    sys.exit()


def run_multiplayer():
    if check_internet():
        window.destroy()
        multiplayer.main()
        sys.exit()
    else:
        messagebox.showerror('No Internet', 'You need internet for this')


window = App('Pit Mopper')

Button(window, text='Single Player', command=run_single_player).pack(pady=(25, 0))
Button(window, text='Multiplayer', command=run_multiplayer).pack(pady=(0, 20), padx=90)

logging.info('Finished loading')
window.mainloop()