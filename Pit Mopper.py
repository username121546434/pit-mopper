import logging
import os
from tkinter import *
from tkinter import messagebox
from Scripts.app import App
from Scripts.constants import VERSION, DEBUG
from Scripts.network import check_internet
from Scripts.console_window import get_console
import sys
get_console()
from Scripts.base_logger import init_logger
init_logger()

logging.info('Loading...')
__version__ = VERSION
__license__ = 'GNU GPL v3, see LICENSE.txt for more info'

if not os.path.exists(DEBUG):
    os.makedirs(DEBUG)

def run_single_player():
    window.destroy()
    import Scripts.single_player
    sys.exit()


def run_multiplayer():
    if check_internet():
        window.destroy()
        import Scripts.multiplayer
        sys.exit()
    else:
        messagebox.showerror('No Internet', 'You need internet for this')


window = App('Pit Mopper')

Button(window, text='Single Player', command=run_single_player).pack(pady=(25, 0))
Button(window, text='Multiplayer', command=run_multiplayer).pack(pady=(0, 20), padx=90)

logging.info('Finished loading')
window.mainloop()