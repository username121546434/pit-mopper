from tkinter.ttk import Progressbar
from socket import error as SocketError
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


class MultiplayerApp(App):
    def quit_app(self, *_):
        try:
            n.send_data('disconnect')
        except Exception:
            pass
        return super().quit_app(*_)


logging.info('Loading multiplayer...')

window = MultiplayerApp('Pit Mopper Multiplayer')
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
logging.info('Waiting for player...')
while True:
    if constants.APP_CLOSED:
        sys.exit()
    game: OnlineGame = n.send_data('get')
    if game.available:
        logging.info('Player joined, starting game')
        label.config(text='Starting game...')
        progress_bar.pack_forget()
        connected = True
        if grid == None and game_window == None:
            game_window = Toplevel(window)
            game_window.title('Pit Mopper Multiplayer')

            timer = Label(game_window, text='Time: 0:00')
            timer.grid(row=1, column=1)

            self_info = StringVar(game_window)
            Label(game_window, textvariable=self_info).grid(row=2, column=1)

            other_info = Label(game_window)
            other_info.grid(row=3, column=1)

            grid = ButtonGrid((10, 10), game_window, row=4, click_random_square=True)
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
                if not game.available:
                    break
                if constants.APP_CLOSED:
                    sys.exit()
                result2 = result.get('result')
                result = _update_game(**result)
                if constants.APP_CLOSED:
                    sys.exit()
                if player == 2:
                    other_info.config(text=f'Oponent: {game.p1_info["timer text"]}')
                else:
                    other_info.config(text=f'Oponent: {game.p2_info["timer text"]}')
                timer.config(text=f'Time: {format_second(result["result"]["seconds"])}')
                game = n.send_data({'timer text': self_info.get()[4:]})
    else:
        if connected:
            connected = False
            grid = None
            game_window.destroy()
            game_window = None
            progress_bar.pack(pady=(0, 20), padx=50)
            label.config(text='Waiting for player...')
            messagebox.showerror('Connection Error', 'It seems that the other player disconected')
            logging.error('It seems like the player has disconnected')
            logging.info('Waiting for new player...')
        else:
            progress_bar['value'] += 0.1
    window.update()
