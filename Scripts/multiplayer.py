"""A module that that has the `MultiplayerApp` class"""
from datetime import datetime
from tkinter.ttk import Progressbar
from .custom_menubar import CustomMenuBar, SubMenu
from .app import App
from .grid import ButtonGrid
from .single_player import SinglePlayerApp
from .network import Network
from .game import Game, OnlineGame, OnlineGameInfo
from tkinter import *
from . import constants
from .functions import *
from .console_window import get_console
get_console()
from .base_logger import init_logger
import logging
init_logger()


class MultiplayerApp(SinglePlayerApp):
    """Subclass of `SinglePlayerApp`"""
    def __init__(self, title: str) -> None:
        super().__init__(title)

    def quit_app(self, *_):
        try:
            self.n.disconnect()
        except Exception:
            pass
        return App.quit_app(self)
    
    def draw_waiting(self):
        self.label = Label(self, text=f'Waiting for player... Game id: {self.online_game.id}')
        self.label.pack(pady=(25, 0))

        self.progress_bar = Progressbar(self, mode='indeterminate', length=200)
        self.progress_bar.pack(padx=50)

        Button(self, text='Cancel', command=self.leave_waiting).pack(pady=(0, 20))
    
    def draw_menubar(self):
        super().draw_menubar()
        for _ in range(3):
            self.file_menu._menubutton.pop()
    
    def draw_waiting_menubar(self):
        self.draw_menubar()
        self.settings.add_separator()
        self.settings.add_command(label='Restart connection', command=self.n.restart, accelerator='Ctrl+R')
    
    def set_waiting_variables(self) -> bool:
        App.set_variables(self)
        while True:
            try:
                if self.game_id_state.get() == -1:
                    self.n = Network(self.game_info)
                else:
                    self.n = Network(self.game_id_state.get())
                    if isinstance(self.n.data, bool): # The server sends a boolean if the game id is not valid
                        if self.n.data:
                            logging.error('Game id requested is being played')
                            messagebox.showerror('Game is being played', 'The game id you requested is being played')
                        else:
                            logging.error('Game id requested does not exist')
                            messagebox.showerror('Game does not exist', 'The game id you requested does not exist')
                        return False
            except:
                logging.error(f'There was an error while connecting to the server\n{traceback.format_exc()}')
                if not messagebox.askretrycancel('Connection error', 'There was an error while connecting to the server'):
                    self.quit_app()
            else:
                break
        self.connected = False
        self.player_left = False
        self.online_game: OnlineGame = self.n.send_data('get')
        self.player = self.n.data
        return True
    
    def draw(self):
        super().draw()

        self.load_last_button.destroy()

        self.play_button.config(command=self.draw_all_waiting)
        self.play_button.pack_forget()

        self.game_id_state = IntVar()

        Label(self, text='Or, enter a game id below, -1 means it will not use it').pack()
        Spinbox(self, textvariable=self.game_id_state, width=4, from_=-1, to=constants.GAME_ID_MAX).pack()
        self.game_id_state.set(-1)
        self.play_button.pack(pady=(0, 20))

        self.title('Multiplayer Game Loader')
    
    def draw_all_waiting(self, *_):
        if not self.validate_game(None):
            return

        self.game_info = OnlineGameInfo(self.difficulty.get(), self.mines.get(), self.chord_state.get())
        logging.info(f'{self.game_id_state.get() = }')
        logging.info('Waiting for player...')
        if not self.set_waiting_variables():
            return
        self.clear()
        self.draw_waiting()
        self.draw_waiting_menubar()
        self.wait_for_game_mainloop()
    
    def set_keyboard_shorcuts(self):
        App.set_keyboard_shorcuts(self)
        bind_widget(self, '<Control-a>', True, func=lambda _: self.chord_state.set(not self.chord_state.get()))
        bind_widget(self, '<Control-r>', all_=True, func=lambda _: self.n.restart())
        bind_widget(self, '<space>', True, self.draw_all_waiting)
    
    def validate_game(self, game) -> bool:
        if (not self.game_id_state.get() > constants.GAME_ID_MIN and
                self.game_id_state.get() < constants.GAME_ID_MAX and
                self.game_id_state.get() != -1):
            messagebox.showerror('Invalid Game Id', f'Game id must be between {constants.GAME_ID_MIN} and {constants.GAME_ID_MAX}')
            return False
        elif self.game_id_state.get() == -1:
            return super().validate_game(game)
        else:
            return True
    
    def create_game(self, *_):
        logging.info('Player joined, starting game')
        self.clear()
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
            self_info,
            datetime.now(),
            [],
            grid.num_mines,
            chording=self.game_info.chording,
            with_time=False
        )
        self.menubar = CustomMenuBar(self)
        self.menubar.place(x=0, y=0)
        game_menu = SubMenu()
        game_menu.add_checkbutton(label='Dark Mode', accelerator='Ctrl+D', variable=self.dark_mode_state)
        game_menu.add_separator()
        game_menu.add_checkbutton(label='Full Screen', accelerator='F11', variable=self.fullscreen_state)
        game_menu.add_command(label='Leave', accelerator='Alt+Q', command=self.leave_game)
        self.menubar.add_menu('Game', game_menu)

        bind_widget(self, '<Alt-q>', all_=True, func=lambda _: self.leave_game())
        bind_widget(self, '<F11>', all_=True, func=lambda *_: self.fullscreen_state.set(not self.fullscreen_state.get()))
        bind_widget(self, '<Control-d>', all_=True, func=lambda *_: self.dark_mode_state.set(not self.dark_mode_state.get()))

        if self.dark_mode_state.get():
            self._change_theme()

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
                if messagebox.askokcancel('Connection Error', 'There was an error while sending data, would you like to leave the game?'):
                    break
            else:
                if self.online_game == 'restart':
                    self.player_left = True
                    break
        self.leave_game()
    
    def leave_game(self):
        self.game.quit = True
        self.fullscreen_state.set(False)
        if self.player_left:
            logging.error('It seems like the player has disconnected')
            messagebox.showerror('Connection Error', 'It seems that the other player disconnected')
            self.player_left = False
        self.clear()
        self.n.disconnect()
        del self.n
        logging.info('Waiting for new player...')
        self.draw_all()
    
    def wait_for_game_mainloop(self):
        self.after_cancel_code = self.after(10, lambda: self.wait_for_game_mainloop())
        if self.connected:
            self.leave_game()
            self.after_cancel(self.after_cancel_code)
        elif not self.connected and not self.online_game.is_full:
            self.online_game = self.n.send_data('get')
            self.progress_bar.step()
        elif self.online_game.is_full and not self.connected:
            self.after_cancel(self.after_cancel_code)
            self.create_game()
    
    def leave_waiting(self):
        self.after_cancel(self.after_cancel_code)
        self.n.disconnect()
        del self.n
        self.clear()
        self.draw_all()


def main():
    logging.info('Loading multiplayer...')

    window = MultiplayerApp('Pit Mopper Multiplayer')

    logging.info('GUI successfully created')
    logging.info('Waiting for player...')
    window.mainloop()
