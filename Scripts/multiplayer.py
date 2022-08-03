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


class MultiplayerApp(App):
    def quit_app(self, *_):
        try:
            n.send_data('disconnect')
        except Exception:
            pass
        return super().quit_app(*_)


class DummyGame:
    available = False


logging.info('Loading multiplayer...')

window = MultiplayerApp('Pit Mopper Multiplayer')

try:
    window.update()
    n = Network()
except ConnectionError as e:
    logging.error(f'There was an error while connecting to the server\n{traceback.format_exc()}')
    messagebox.showerror('Connection error', 'There was an error while connecting to the server, This is either because you do not have internet or the server is shutdown for maintenence, Please try again later')
    window.quit_app()

label = Label(window, text='Waiting for player...')
label.pack(pady=(25, 0))

progress_bar = Progressbar(window, mode='indeterminate', length=200)
progress_bar.pack(pady=(0, 20), padx=50)

player = n.data
grid = None
game_window = None
connected = False
player_left = False
game = DummyGame()

window.settings.add_separator()
window.settings.add_command(label='Restart connection', command=n.restart)

logging.info('GUI successfully created')
logging.info('Waiting for player...')
while True:
    if constants.APP_CLOSED:
        sys.exit()
    elif connected:
        del result
        if player_left:
            messagebox.showerror('Connection Error', 'It seems that the other player disconnected')
            player_left = False
            logging.error('It seems like the player has disconnected')
        connected = False
        grid = None
        game_window.destroy()
        game_window = None
        n.restart()
        player = n.data
        game: OnlineGame = n.send_data('get')
        progress_bar.pack(pady=(0, 20), padx=50)
        label.config(text='Waiting for player...')
        logging.info('Waiting for new player...')
    elif not connected and not game.available:
        game: OnlineGame = n.send_data('get')
        progress_bar['value'] += 0.1
    elif game.available and not connected:
        logging.info('Player joined, starting game')
        label.config(text='Starting game...')
        progress_bar.pack_forget()
        connected = True
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
            if constants.APP_CLOSED:
                sys.exit()
            if game.quit:
                player_left = True
                break
            if game.game_is_tie():
                messagebox.showinfo('Game Results', f'The game ended with a tie!\nYour time: {format_second(result2["seconds"])}')
                logging.info('Game Over, ended in a tie')
                break
            elif game.player_who_won() == player:
                messagebox.showinfo('Game Results', f'You won the game!\nYour time: {format_second(result2["seconds"])}')
                logging.info('Game Over, ended in a victory')
                break
            elif game.player_who_won() != None:
                messagebox.showinfo('Game Results', f'You lost the game :( Better luck next time!\nYour time: {format_second(result2["seconds"])}')
                logging.info('Game Over, ended in a loss')
                break
            result2 = result.get('result')
            result = _update_game(**result)
            if constants.APP_CLOSED:
                sys.exit()
            if player == 2:
                other_info.config(text=f'Oponent: {game.p1_info["timer text"]}')
            else:
                other_info.config(text=f'Oponent: {game.p2_info["timer text"]}')
            timer.config(text=f'Time: {format_second(result["result"]["seconds"])}')
            if result2['game over']:
                reply = datetime.now()
            else:
                reply = {'timer text': self_info.get()[4:]}
            try:
                game = n.send_data(reply)
            except Exception:
                logging.error(f'Error while sending data\n{traceback.format_exc()}')
                if messagebox.askokcancel('Connection Error', 'There was an error while sending data, would you like to restart the connection?'):
                    break
            else:
                if game == 'restart':
                    player_left = True
                    break
    window.update()
