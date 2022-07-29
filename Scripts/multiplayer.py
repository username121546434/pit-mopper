from tkinter.ttk import Progressbar
from .app import App
from .functions import _update_game
from .grid import ButtonGrid
from .network import Network
from .game import OnlineGame
from tkinter import *
from . import constants
from .functions import *
from .console_window import get_console
get_console()
from .base_logger import init_logger
import logging
init_logger()


def _quit_app(*_):
    n.send_data('disconnect')
    base_quit_app(window)


logging.info('Loading multiplayer...')

window = App('Pit Mopper Multiplayer')
window.quit_app = _quit_app
label = Label(window, text='Waiting for player...')
label.pack(pady=(25, 0))

progress_bar = Progressbar(window, mode='indeterminate', length=200)
progress_bar.pack(pady=(0, 20), padx=50)

n = Network()
player = n.data
grid = None
game_window = None
connected = False

logging.info('GUI successfully created')

while True:
    if constants.APP_CLOSED:
        sys.exit()
    game: OnlineGame = n.send_data('get')
    if game.available:
        label.config(text='Starting game...')
        progress_bar.pack_forget()
        connected = True
        if grid == None and game_window == None:
            game_window = Toplevel(window)
            game_window.title('Pit Mopper Multiplayer')

            self_info = StringVar(game_window)
            Label(game_window, textvariable=self_info).grid(row=1, column=1)

            other_info = Label(game_window)
            other_info.grid(row=2, column=1)

            grid = ButtonGrid((10, 10), game_window, row=3, click_random_square=True)
            result = _update_game(
                game_window,
                grid,
                datetime.now(),
                self_info,
                [],
                grid.num_mines,
                True,
                with_time=False
            )
            while True:
                if constants.APP_CLOSED:
                    sys.exit()
                result2 = result.get('result')
                result = _update_game(**result)
                game = n.send_data('get')
                if constants.APP_CLOSED:
                    sys.exit()
                if player == 2:
                    other_info.config(text=f'Oponent: {game.p1_info["timer text"]}')
                else:
                    other_info.config(text=f'Oponent: {game.p2_info["timer text"]}')
                if not game.available:
                    messagebox.showerror('Player disconnected', 'It seems like the player has disconnected, please re-open Pit Mopper')
                    window.quit_app()
                game = n.send_data({'timer text': self_info.get()[4:]})
    else:
        if connected:
            connected = False
            grid = None
            game_window.destroy()
            game_window = None
            messagebox.showerror('Connection Error', 'It seems that the other player disconected')
        else:
            progress_bar['value'] += 0.1
    window.update()
