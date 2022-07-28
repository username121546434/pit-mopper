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


def quit_app():
    n.send_data('disconnect')
    base_quit_app(window)


logging.info('Loading multiplayer...')

window = App('Pit Mopper Multiplayer')
window.quit_app = quit_app
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
    game: OnlineGame = n.send_data('get')
    print(game)
    if game.available:
        label.config(text='Starting game...')
        progress_bar.pack_forget()
        connected = True
        if grid == None and game_window == None:
            game_window = Toplevel(window)
            game_window.title('Pit Mopper Multiplayer')

            self_timer = StringVar(game_window)
            Label(game_window, textvariable=self_timer).grid(row=1, column=1)

            other_timer = Label(game_window)
            other_timer.grid(row=2, column=1)

            grid = ButtonGrid((10, 10), game_window, row=3, click_random_square=True)
            result = _update_game(
                game_window,
                grid,
                datetime.now(),
                self_timer,
                [],
                grid.num_mines,
                True
            )
            while True:
                constants.after_cancel.append(game_window.after(50, do_nothing))
                result2 = result.pop('result')
                result = _update_game(**result)
                game = n.send_data('get')
                if player == 2:
                    other_timer.config(text=game.p1_info['timer text'])
                else:
                    other_timer.config(text=game.p2_info['timer text'])
                data = {'timer text': self_timer.get()}
                game = n.send_data(data)
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
