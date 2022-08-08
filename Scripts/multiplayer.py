from tkinter.ttk import Progressbar
from .custom_menubar import SubMenu
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
            self.n.disconnect()
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
        self.settings.add_command(label='Restart connection', command=self.n.restart, accelerator='Ctrl+R')
    
    def set_variables(self):
        super().set_variables()
        self.connected = False
        self.player_left = False
        self.online_game: OnlineGame = self.n.send_data('get')
        self.player = self.n.data
    
    def set_keyboard_shorcuts(self):
        super().set_keyboard_shorcuts()
        bindWidget(self, '<Control-r>', all=True, func=lambda _: self.n.restart())
    
    def create_game(self):
        logging.info('Player joined, starting game')
        self.clear()
        self.draw_menubar()
        self.set_keyboard_shorcuts()
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
        game_menu = SubMenu()
        game_menu.add_command(label='Leave', accelerator='Alt+Q', command=self.leave_game)
        self.menubar.add_menu('Game', game_menu)

        bindWidget(self, '<Alt-q>', all=True, func=lambda _: self.leave_game())

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
            try:
                if self.player == 2:
                    other_info.config(text=f'Oponent: {self.online_game.p1_info["timer text"]}')
                else:
                    other_info.config(text=f'Oponent: {self.online_game.p2_info["timer text"]}')
            except TclError: # Game left using menubar or Alt + Q
                break
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
    
    def leave_game(self):
        self.game.quit = True
        if self.player_left:
            messagebox.showerror('Connection Error', 'It seems that the other player disconnected')
            self.player_left = False
            logging.error('It seems like the player has disconnected')
        self.clear()
        self.n.restart()
        logging.info('Waiting for new player...')
        self.draw_all()


logging.info('Loading multiplayer...')

window = MultiplayerApp('Pit Mopper Multiplayer')

logging.info('GUI successfully created')
logging.info('Waiting for player...')


def mainloop():
    if constants.APP_CLOSED:
        sys.exit()
    elif window.connected:
        window.leave_game()
    elif not window.connected and not window.online_game.available:
        window.online_game = window.n.send_data('get')
        window.progress_bar.step()
    elif window.online_game.available and not window.connected:
        window.create_game()
    window.after(10, mainloop)

mainloop()
window.mainloop()
