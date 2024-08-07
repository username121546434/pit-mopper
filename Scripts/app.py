"""Defines the `App` class"""
from __future__ import annotations
from tkinter import BooleanVar
from typing import TYPE_CHECKING

from .game_types import GameResult
from . import constants
from .custom_menubar import CustomMenuBar, SubMenu
from .functions import *
from functools import partial
from .updater import check_for_updates
import shutil
from datetime import datetime
import os
from .enums import KBDShortcuts
from .game import Game
from typing import overload

if TYPE_CHECKING:
    from .single_player import SinglePlayerApp
    from .multiplayer import MultiplayerApp


class App(Tk):
    """
    Base class for `SinglePlayerApp` and `MultiplayerApp`.
    It defines all keyboard shorcuts, menubar options, and variables common in both
    """
    _alive: App | None = None

    @overload
    def __new__(cls: type[MultiplayerApp], *args, **kw) -> MultiplayerApp:
        ...

    @overload
    def __new__(cls: type[SinglePlayerApp], *args, **kw) -> SinglePlayerApp:
        ...

    @overload
    def __new__(cls: type[App], *args, **kw) -> App:
        ...

    def __new__(cls: type[App | SinglePlayerApp | MultiplayerApp], *args, **kwargs) -> App | SinglePlayerApp | MultiplayerApp:
        if App._alive is None:
            return super().__new__(cls) # type: ignore
        else:
            App._alive.__class__ = cls
            return App._alive

    def __init__(self, title: str) -> None:
        if App._alive is None:
            super().__init__()
            App._alive = self
        self.clear()
        self.initialized = False

        logging.info('Loading new app instance...')
        sys.excepthook = handle_exception
        self.report_callback_exception = handle_exception

        self.title(title)

        if os.name == 'nt':
            self.iconbitmap(constants.LOGO, constants.LOGO)
        else:
            self.iconbitmap(constants.LOGO)

        self.draw_all()
        assert App._alive is self
        self.protocol('WM_DELETE_WINDOW', self.quit_app)
        self.initialized = True
    
    def winfo_geometry(self):
        """Return geometry as a tuple of (width, height, x, y)
        the last element is the initial geometry string given by tkinter."""
        geometry = super().winfo_geometry()
        width, height_xy = geometry.split('x')
        height, x, y = height_xy.split('+')
        width, height, x, y = int(width), int(height), int(x), int(y)

        return width, height, x, y, geometry
    
    def switch_multiplayer(self):
        from .multiplayer import MultiplayerApp, DEFAULT_TITLE
        MultiplayerApp(DEFAULT_TITLE)

    def switch_singleplayer(self):
        from .single_player import SinglePlayerApp, DEFAULT_TITLE
        SinglePlayerApp(DEFAULT_TITLE)
    
    def draw_all(self):
        self.set_variables()
        self.draw_menubar()
        self.set_keyboard_shorcuts()
        self.draw()

        if self.initialized:
            if os.name == 'nt':
                self.state('normal')
            else:
                self.attributes('-zoomed', False)
            self.geometry('')

        self.resizable(False, False)
        change_theme_of_window(self)
    
    def set_variables(self):
        self.dark_mode_state = BooleanVar(self, constants.dark_mode)
        self.dark_mode_state.trace('w', self.change_theme)
        self.fullscreen_state = BooleanVar(self)
        self.fullscreen_state.trace('w', lambda *_: self.attributes("-fullscreen", self.fullscreen_state.get()))
    
    def set_keyboard_shorcuts(self):
        # Keyboard Shortcuts
        bind_widget(self, KBDShortcuts.version_info, True, lambda _: messagebox.showinfo(title='Version Info', message=f'Pit Mopper Version: {constants.VERSION}'))
        bind_widget(self, KBDShortcuts.check_for_updates, True, lambda _: check_for_updates(self.quit_app))
        bind_widget(self, KBDShortcuts.quit_app, True, self.quit_app)
        bind_widget(self, KBDShortcuts.toggle_theme, True, lambda _: self.dark_mode_state.set(not self.dark_mode_state.get()))
    
    def draw_menubar(self):
        # create a menubar
        self.menubar = CustomMenuBar(self)
        self.menubar.place(x=0, y=0)

        # create the file_menu
        self.file_menu = SubMenu()
        self.file_menu.add_command(label='Exit', command=self.quit_app, accelerator=format_kbd_shortcut(KBDShortcuts.quit_app))

        self.settings = SubMenu()
        self.settings.add_checkbutton(variable=self.dark_mode_state, label='Dark Mode', accelerator=format_kbd_shortcut(KBDShortcuts.toggle_theme))
        self.settings.add_separator()
        self.settings.add_command(label='Check for Updates', command=partial(check_for_updates, self.quit_app), accelerator=format_kbd_shortcut(KBDShortcuts.check_for_updates))
        self.settings.add_command(label='Version Info', command=partial(messagebox.showinfo, title='Version Info', message=f'Pit Mopper Version: {constants.VERSION}'), accelerator=format_kbd_shortcut(KBDShortcuts.version_info))

        self.advanced = SubMenu()
        self.advanced.add_command(label='Delete all data', command=clear_all_data)
        self.advanced.add_command(label='Delete Debug Logs', command=clear_debug)
        self.advanced.add_command(label='Delete Highscore', command=clear_highscore)
        self.advanced.add_command(label='Delete Last Game', command=clear_last_game)

        self.help_about = SubMenu()
        self.help_about.add_command(label='Wiki', command=partial(webbrowser.open, 'https://github.com/username121546434/pit-mopper/wiki'))
        self.help_about.add_command(label='Keyboard Shortcuts', command=partial(webbrowser.open, 'https://github.com/username121546434/pit-mopper/wiki/Keyboard-Shortcuts'))
        self.help_about.add_command(label='How to Play', command=partial(webbrowser.open, 'https://github.com/username121546434/pit-mopper/wiki/How-to-play'))
        self.help_about.add_command(label='GitHub Repo', command=partial(webbrowser.open, 'https://github.com/username121546434/pit-mopper'))
        self.help_about.add_separator()
        self.help_about.add_command(label='Join the discord server', command=partial(webbrowser.open, 'https://discord.gg/AetMeBTyMx'))

        self.menubar.add_menu(menu=self.file_menu, title='File')
        self.menubar.add_menu(menu=self.settings, title='Settings')
        self.menubar.add_menu(menu=self.advanced, title='Advanced')
        self.menubar.add_menu(menu=self.help_about, title='Help/About')
    
    def draw(self):
        """This is supposed to be overridden by subclasses"""
        pass
    
    def quit_app(self, *_):
        constants.APP_CLOSED = True
        logging.info('Closing Pit Mopper...')
        try:
            self.setvar('button pressed', '39393')
        except Exception:
            pass
        try:
            self.destroy()
        except RecursionError:
            pass
        logging.shutdown()
        if constants.del_data == 'all':
            try:
                shutil.rmtree(constants.APPDATA)
            except FileNotFoundError:
                pass
        elif constants.del_data == 'debug':
            try:
                shutil.rmtree(constants.DEBUG)
            except FileNotFoundError:
                pass
        elif constants.del_data == 'highscore':
            try:
                os.remove(constants.HIGHSCORE_TXT)
            except FileNotFoundError:
                pass
        del self
        os._exit(0)

    def change_theme(self, *_):
        constants.dark_mode = self.dark_mode_state.get()
        if constants.dark_mode:
            logging.info('User switched theme to dark mode')
            constants.CURRENT_BG = constants.DARK_MODE_BG
            constants.CURRENT_FG = constants.DARK_MODE_FG
        else:
            logging.info('User switched theme to light mode')
            constants.CURRENT_BG = constants.DEFAULT_BG
            constants.CURRENT_FG = constants.DEFAULT_FG
        change_theme_of_window(self)

    def clear(self):
        """Clears everything on the window, including bindings"""
        for child in self.winfo_children():
            child.destroy()
        if not hasattr(self, 'bindings'):
            self.bindings = {}
        for event, _ in self.bindings.items():
            self.unbind_all(event)
        self.bindings = {}

    def _update_game(self, after: bool=True):
        """
        Updates one frame of the game, this is called over and over again
        
        Most of the game logic can be found here
        """
        # Type hints
        self.game: Game
        self.game_over: BooleanVar

        squares_flaged = [
            square
            for row in self.game.grid.grid
            for square in row
            if square.flaged
        ]
        squares_clicked_on = [
            square
            for row in self.game.grid.grid
            for square in row
            if square.clicked_on
        ]
        squares_not_clicked_on = [
            square
            for row in self.game.grid.grid
            for square in row
            if square.clicked_on == False
        ]

        now = datetime.now()
        now = now.replace(microsecond=0)

        if now > self.game.previous_sec:
            # Update timer
            self.game.previous_sec = now
            self.game.seconds = (now - self.game.session_start).total_seconds() + self.game.additional_time
            percent = round(((len(squares_flaged))/self.game.num_mines) * 100, 2)
            if self.game.with_time:
                self.game.total_time.set(f'Time: {format_second(self.game.seconds)}  🚩 {len(squares_flaged)}/{self.game.num_mines} 💣 ({percent}%)')
            else:
                self.game.total_time.set(f'You: 🚩 {len(squares_flaged)}/{self.game.num_mines} 💣 ({percent}%)')

        for row in self.game.grid.iter_rows():
            # Clicks Zeros
            for square in (square for square in row if (square.num == None) and (square.clicked_on) and (square not in self.game.zeros_checked) and (square.category != 'mine')):
                self.game.zeros_checked.append(square)
                for square2 in (square2 for square2 in self.game.grid.around_square(*square.position) if (square2.category != 'mine') and square2 not in self.game.squares_checked):
                    square2.clicked()
                    self.game.squares_checked.append(square2)
            if self.game.chording:
                # Checks all square if they are completed
                for square in (square for square in row if square.completed == False):
                    mines_around_square = [square for square in self.game.grid.around_square(
                        *square.position) if (square.category == 'mine') and (square.clicked_on == True)]
                    if (len(mines_around_square) == square.num and all(mine.category == 'mine' for mine in mines_around_square)) or square.num == None:
                        square.completed = True
                # Shows all squares around a square if it was middle clicked
                for square in (square for square in row if (square.chord)):
                    if square.completed == False:
                        precolors = []
                        squares = [
                            square
                            for square in self.game.grid.around_square(*square.position)
                            if square.clicked_on == False
                        ]
                        for square2 in squares:
                            precolors.append(square2.cget('bg'))
                            square2.config(bg='brown')
                        self.update()
                        def undo():
                            for square2 in squares:
                                precolor = precolors[squares.index(square2)]
                                square2.config(bg=precolor)
                            square.chord = False
                        self.after(500, undo)
                    else:
                        for square2 in (square for square in self.game.grid.around_square(*square.position) if not square.clicked_on and square.category != 'mine'):
                            square2.clicked()
                        square.chord = False

        squares_clicked_on = [
            square
            for row in self.game.grid.grid
            for square in row
            if square.clicked_on
        ]
        squares_not_clicked_on = [
            square
            for row in self.game.grid.grid
            for square in row
            if square.clicked_on == False
        ]
        squares_flaged = [
            square
            for row in self.game.grid.grid
            for square in row
            if square.flaged
        ]

        # Counts mines found
        for square in (square for square in squares_flaged if square.category == 'mine'):
            self.game.mines_found += 1
        if (len(squares_clicked_on) == (self.game.grid.grid_size[0] * self.game.grid.grid_size[1]) and all(square.category == 'mine' for square in squares_flaged)) or \
                (all(square.category == 'mine' for square in squares_not_clicked_on) and len(squares_not_clicked_on) == self.game.num_mines):
            game_over = True
            win = True
            if (len(squares_clicked_on) == (self.game.grid.grid_size[0] * self.game.grid.grid_size[1]) and all(square.category == 'mine' for square in squares_flaged)):
                logging.info('Game has been won because all squares are clicked and all mines flagged')
            else:
                logging.info('Game has been won because the squares left are mines')
        elif any(square.game_over for square, _ in self.game.grid.iter_squares()):
            logging.info('The game is over, and it is lost.')
            game_over = True
            win = False
        else:
            game_over = False
            win = False

        if game_over:
            self.game.mines_found = 0
            for square, _ in self.game.grid.iter_squares():
                if square.category == 'mine' and square.cget('text') != '🚩':
                    square.clicked()
                elif square.category == 'mine' and square.cget('text') == '🚩':
                    self.game.mines_found += 1
                    square.config(text='✅')
                elif square.num != None and square.cget('text') == '🚩':
                    square.config(text='❌')
            self.game_over.set(True)

        self.game.result = GameResult(game_over=game_over, seconds=self.game.seconds, win=win)
        self.update()
        if hasattr(self, 'game') and \
           self.game is not None and \
           not self.game.quit and after:
            self.game_after_cancel = self.after(50, self._update_game)
