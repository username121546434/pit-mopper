"""Main Python file, run it to play the game"""
import logging
import os
from tkinter import Button
from tkinter import messagebox
from Scripts.app import App
from Scripts.constants import VERSION, debug_log_file, APP_DIR, IS_COMPILED
from Scripts.network import check_internet
from Scripts.url_protocol import register_protocol, has_been_registered, parse_url
from Scripts import multiplayer, single_player
import sys

with open(debug_log_file, 'w') as _:
    pass
from Scripts.base_logger import init_logger
init_logger()

if os.getcwd() != APP_DIR and IS_COMPILED:
    os.chdir(APP_DIR)

logging.info('Loading...')
__version__ = VERSION
__license__ = 'GNU GPL v3, see LICENSE.txt for more info'


if not has_been_registered() and IS_COMPILED:
    logging.info('Registering protocol...')
    register_protocol()


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
    elif url := parse_url(sys.argv[1]):
        mode, server, port, id_ = url
        if mode == 'm':
            multiplayer.main()
        elif mode == 's':
            single_player.main()


def main():
    window = App('Pit Mopper')

    Button(window, text='Single Player', command=run_single_player).pack(pady=(25, 0))
    Button(window, text='Multiplayer', command=run_multiplayer).pack(pady=(0, 20), padx=90)

    logging.info('Finished loading')
    window.mainloop()


if __name__ == '__main__':
    main()
