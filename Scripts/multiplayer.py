from tkinter.ttk import Progressbar
from .app import App
from .grid import ButtonGrid
from .network import Network
from .game import Game, OnlineGame
from tkinter import *
from . import constants
from .functions import *
from .console_window import get_console
get_console()
from .base_logger import init_logger
import logging
init_logger()


class DummyGame:
    available = False


class MultiplayerApp(App):
    def __init__(self, title: str) -> None:
        try:
            self.n = Network()
        except ConnectionError:
            logging.error(f'There was an error while connecting to the server\n{traceback.format_exc()}')
            messagebox.showerror('Connection error', 'There was an error while connecting to the server, Please try again later')
            self.quit_app()
        super().__init__(title)

    def quit_app(self, *_):
        try:
            self.n.send_data('disconnect')
        except Exception:
            pass
        return super().quit_app(*_)
    
    def draw(self):
        self.label = Label(self, text='Waiting for player...')
        self.label.pack(pady=(25, 0))

        self.progress_bar = Progressbar(self, mode='indeterminate', length=200)
        self.progress_bar.pack(pady=(0, 20), padx=50)
    
    def draw_menubar(self):
        super().draw_menubar()
        self.settings.add_separator()
        self.settings.add_command(label='Restart connection', command=self.n.restart)
    
    def set_variables(self):
        super().set_variables()
        self.connected = False
        self.player_left = False
        self.online_game: OnlineGame = self.n.send_data('get')
        self.player = self.n.data
    
    def draw_game(self):
        logging.info('Player joined, starting game')
        self.clear()
        self.draw_menubar()
        self.connected = True
        self.title('Pit Mopper Multiplayer')

        timer = Label(self, text='Time: 0:00')
        timer.grid(row=1, column=1)

        self_info = StringVar(self)
        Label(self, textvariable=self_info).grid(row=2, column=1)

        other_info = Label(self)
        other_info.grid(row=3, column=1)

        grid = ButtonGrid((10, 10), self, row=4, click_random_square=True, dark_mode=self.dark_mode_state.get())
        self.game = Game(
            grid,
            datetime.now(),
            self_info,
            [],
            grid.num_mines,
            True,
            with_time=False
        )
        self._update_game()
        while True:
            if constants.APP_CLOSED:
                sys.exit()
            if self.online_game.quit:
                self.player_left = True
                break
            if self.online_game.game_is_tie():
                messagebox.showinfo('Game Results', f'The game ended with a tie!\nTime taken: {format_second(self.game.result["seconds"])}')
                logging.info('Game Over, ended in a tie')
                break
            elif self.online_game.player_who_won() == self.player:
                messagebox.showinfo('Game Results', f'You won the game!\nTime taken: {format_second(self.game.result["seconds"])}')
                logging.info('Game Over, ended in a victory')
                break
            elif self.online_game.player_who_won() != 12 and self.online_game.player_who_won() != None and self.online_game.player_who_won() != self.player:
                messagebox.showinfo('Game Results', f'You lost the game :( Better luck next time!\nTime taken: {format_second(self.game.result["seconds"])}')
                logging.info('Game Over, ended in a loss')
                break
            self._update_game()
            if constants.APP_CLOSED:
                sys.exit()
            if self.player == 2:
                other_info.config(text=f'Oponent: {self.online_game.p1_info["timer text"]}')
            else:
                other_info.config(text=f'Oponent: {self.online_game.p2_info["timer text"]}')
            timer.config(text=f'Time: {format_second(self.game.result["seconds"])}')
            if self.game.result['game over']:
                reply = self.game.result['win']
            else:
                reply = {'timer text': self_info.get()[4:]}
            try:
                self.online_game = self.n.send_data(reply)
            except Exception:
                logging.error(f'Error while sending data\n{traceback.format_exc()}')
                if messagebox.askokcancel('Connection Error', 'There was an error while sending data, would you like to restart the connection?'):
                    break
            else:
                if self.online_game == 'restart':
                    self.player_left = True
                    break


logging.info('Loading multiplayer...')

window = MultiplayerApp('Pit Mopper Multiplayer')

logging.info('GUI successfully created')
logging.info('Waiting for player...')


def mainloop():
    if constants.APP_CLOSED:
        sys.exit()
    elif window.connected:
        if window.player_left:
            messagebox.showerror('Connection Error', 'It seems that the other player disconnected')
            window.player_left = False
            logging.error('It seems like the player has disconnected')
        window.clear()
        window.n.restart()
        logging.info('Waiting for new player...')
        window.draw_all()
    elif not window.connected and not window.online_game.available:
        window.online_game = window.n.send_data('get')
        window.progress_bar.step()
    elif window.online_game.available and not window.connected:
        window.draw_game()
    window.after(10, mainloop)

mainloop()
window.mainloop()
