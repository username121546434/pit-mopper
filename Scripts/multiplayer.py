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
from .enums import KBDShortcuts
from .base_logger import init_logger
import logging
init_logger()


class MultiplayerApp(SinglePlayerApp):
    """Subclass of `SinglePlayerApp`"""
    def __init__(self, title: str) -> None:
        super().__init__(title)

    def quit_app(self, *_):
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
        for _ in range(2):
            self.settings._menubutton.pop()
        self.settings.add_separator()
        self.settings.add_command(label='Restart connection', command=self.n.restart, accelerator=format_kbd_shortcut(KBDShortcuts.reset_connection))
    
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
        self.game_info = self.online_game.game_info
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
        logging.info(f'{self.game_info = }')
        logging.info(f'{self.game_id_state.get() = }')
        logging.info('Waiting for player...')
        if not self.set_waiting_variables():
            return
        self.clear()
        self.draw_waiting()
        self.draw_waiting_menubar()
        self.after_cancel_code = self.after(1, self.wait_for_game_mainloop)
    
    def set_keyboard_shorcuts(self):
        App.set_keyboard_shorcuts(self)
        bind_widget(self, KBDShortcuts.toggle_chording, True, func=lambda _: self.chord_state.set(not self.chord_state.get()))
        bind_widget(self, KBDShortcuts.reset_connection, all_=True, func=lambda _: self.n.restart())
        bind_widget(self, KBDShortcuts.start_game, True, self.draw_all_waiting)
    
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

        self.game_timer = Label(self, text='Time: 0:00')
        self.game_timer.grid(row=1, column=1)

        self.self_info = StringVar(self)
        Label(self, textvariable=self.self_info).grid(row=2, column=1)

        self.other_info = Label(self)
        self.other_info.grid(row=3, column=1)

        grid = ButtonGrid(
            self.game_info.game_size,
            num_mines=self.game_info.mine_count,
            window=self,
            row=4,
            click_random_square=True,
            dark_mode=self.dark_mode_state.get(),
        )
        self.game = Game(
            grid,
            self.self_info,
            datetime.now(),
            [],
            grid.num_mines,
            chording=self.game_info.chording,
            with_time=False
        )

        self.menubar = CustomMenuBar(self)
        self.menubar.place(x=0, y=0)
        game_menu = SubMenu()
        game_menu.add_checkbutton(label='Dark Mode', accelerator=format_kbd_shortcut(KBDShortcuts.toggle_theme), variable=self.dark_mode_state)
        game_menu.add_separator()
        game_menu.add_checkbutton(label='Full Screen', accelerator=format_kbd_shortcut(KBDShortcuts.fullscreen), variable=self.fullscreen_state)
        game_menu.add_command(label='Leave', accelerator=format_kbd_shortcut(KBDShortcuts.quit_game), command=self.leave_game)
        self.menubar.add_menu('Game', game_menu)

        bind_widget(self, KBDShortcuts.quit_game, all_=True, func=lambda _: self.leave_game())
        bind_widget(self, KBDShortcuts.fullscreen, all_=True, func=lambda *_: self.fullscreen_state.set(not self.fullscreen_state.get()))
        bind_widget(self, KBDShortcuts.toggle_theme, all_=True, func=lambda *_: self.dark_mode_state.set(not self.dark_mode_state.get()))

        if self.dark_mode_state.get():
            self._change_theme()

        self._game()
    
    def _game(self):
        self.game_over = BooleanVar(self, name='game_over')
        self.game_after_cancel = self.after(50, self._update_game)
        self.wait_variable('game_over')

    def _update_game(self):
        super()._update_game(after=False)

        if self.online_game.quit:
            self.player_left = True
            self.game.quit = True
            self.leave_game()
            return
        if self.online_game.game_is_tie():
            messagebox.showinfo('Game Results', f'The game ended with a tie!\nTime taken: {format_second(self.game.result["seconds"])}')
            logging.info('Game Over, ended in a tie')
            self.game.quit = True
            self.leave_game()
            return
        elif self.online_game.player_who_won() == self.player:
            messagebox.showinfo('Game Results', f'You won the game!\nTime taken: {format_second(self.game.result["seconds"])}')
            logging.info('Game Over, ended in a victory')
            self.game.quit = True
            self.leave_game()
            return
        elif self.online_game.player_who_won() != 12 and self.online_game.player_who_won() != None and self.online_game.player_who_won() != self.player:
            messagebox.showinfo('Game Results', f'You lost the game :( Better luck next time!\nTime taken: {format_second(self.game.result["seconds"])}')
            logging.info('Game Over, ended in a loss')
            self.game.quit = True
            self.leave_game()
            return

        if self.player == 2:
            self.other_info.config(text=f'Oponent: {self.online_game.p1_info["timer text"]}')
        else:
            self.other_info.config(text=f'Oponent: {self.online_game.p2_info["timer text"]}')

        self.game_timer.config(text=f'Time: {format_second(self.game.result["seconds"])}')
        if self.game.result['game over']:
            reply = self.game.result['win']
        else:
            reply = {'timer text': self.self_info.get()[4:]}

        try:
            self.online_game = self.n.send_data(reply)
        except Exception:
            logging.error(f'Error while sending data\n{traceback.format_exc()}')
            if messagebox.askokcancel('Connection Error', 'There was an error while sending data, would you like to leave the game?'):
                self.game.quit = True
                self.leave_game()
                return
        else:
            if self.online_game == 'restart':
                self.player_left = True
                self.leave_game()
                return

        self.game_after_cancel = self.after(50, self._update_game)
    
    def leave_game(self):
        self.after_cancel(self.game_after_cancel)
        self.game_over.set(True)
        self.fullscreen_state.set(False)
        self.game = None
        self.connected = False
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
        self.after_cancel_code = self.after(10, self.wait_for_game_mainloop)
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
    if len(sys.argv) > 1:
        if sys.argv[1].isdigit():
            window.game_id_state.set(int(sys.argv[1]))
            window.draw_all_waiting()

    window.mainloop()
