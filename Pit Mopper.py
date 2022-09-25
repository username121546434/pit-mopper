"""Main Python file, run it to play the game"""
import logging
import os
from tkinter import *
from tkinter import messagebox
from Scripts.app import App
from Scripts.constants import VERSION, debug_log_file
from Scripts.network import check_internet
from Scripts import multiplayer, single_player
import sys

with open(debug_log_file, 'w') as _:
    pass
from Scripts.base_logger import init_logger
init_logger()

logging.info('Loading...')
__version__ = VERSION
__license__ = 'GNU GPL v3, see LICENSE.txt for more info'

def run_single_player():
    single_player.main()
    sys.exit()


def run_multiplayer():
    if check_internet():
        multiplayer.main()
        sys.exit()
    else:
        messagebox.showerror('No Internet', 'You need internet for this')


if '-s' in sys.argv:
    logging.info('-s command arg given, loading single player...')
    single_player.main()
elif '-m' in sys.argv:
    logging.info('-m command arg given, loading multiplayer...')
    multiplayer.main()
elif len(sys.argv) > 1:
    if os.path.exists(sys.argv[1]):
        single_player.main()
    elif sys.argv[1].isdigit():
        multiplayer.main()

window = App('Pit Mopper')

Button(window, text='Single Player', command=run_single_player).pack(pady=(25, 0))
Button(window, text='Multiplayer', command=run_multiplayer).pack(pady=(0, 20), padx=90)

logging.info('Finished loading')
window.mainloop()