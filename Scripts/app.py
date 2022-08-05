from tkinter import *
from . import constants
from .custom_menubar import CustomMenuBar
from .functions import *
from .console_window import show_console, hide_console
from functools import partial
from .updater import check_for_updates
import shutil
from tkinter.ttk import Progressbar
import os
from .game import Game


class App(Tk):
    def __init__(self, title: str) -> None:
        logging.info('Loading new app instance...')
        super().__init__()
        sys.excepthook = handle_exception
        self.report_callback_exception = handle_exception

        self.title(title)
        self.iconbitmap(constants.LOGO, constants.LOGO)

        self.draw_all()

        self.protocol('WM_DELETE_WINDOW', self.quit_app)
    
    def draw_all(self):
        self.set_variables()
        self.draw_menubar()
        self.set_keyboard_shorcuts()
        self.draw()
    
    def set_variables(self):
        self.console_open = BooleanVar(self, False)
        self.console_open.trace('w', self.console)
        self.dark_mode_state = BooleanVar(self, constants.dark_mode)
        self.dark_mode_state.trace('w', self.change_theme)
    
    def set_keyboard_shorcuts(self):
        # Keyboard Shortcuts
        bindWidget(self, '<Control-i>', True, lambda _: messagebox.showinfo(title='Version Info', message=f'Pit Mopper Version: {constants.VERSION}'))
        bindWidget(self, '<Control-u>', True, lambda _: check_for_updates(self.quit_app))
        bindWidget(self, '<Control-q>', True, self.quit_app)
        bindWidget(self, '<Control-d>', True, lambda _: self.dark_mode_state.set(not self.dark_mode_state.get()))
        bindWidget(self, '<Control-x>', True, lambda _: self.console_open.set(not self.console_open.get()))
    
    def draw_menubar(self):
        # create a menubar
        self.menubar = CustomMenuBar(self)
        self.menubar.place(x=0, y=0)

        # create the file_menu
        self.file_menu = Menu(
            self.menubar,
            tearoff=0
        )
        self.file_menu.add_command(label='Exit', command=self.quit_app, accelerator='Ctrl+Q')

        self.settings = Menu(self.menubar, tearoff=0)
        self.settings.add_checkbutton(variable=self.dark_mode_state, label='Dark Mode', accelerator='Ctrl+D')
        self.settings.add_separator()
        self.settings.add_command(label='Check for Updates', command=partial(check_for_updates, self.quit_app), accelerator='Ctrl+U')
        self.settings.add_command(label='Version Info', command=partial(messagebox.showinfo, title='Version Info', message=f'Pit Mopper Version: {constants.VERSION}'), accelerator='Ctrl+I')
        self.settings.add_separator()
        self.settings.add_command(label='Delete all data', command=clear_all_data)
        self.settings.add_command(label='Delete Debug Logs', command=clear_debug)
        self.settings.add_command(label='Delete Highscore', command=clear_highscore)

        self.advanced = Menu(self.settings, tearoff=0)
        self.advanced.add_checkbutton(label='Console', variable=self.console_open, accelerator='Ctrl+X')
        self.menubar.add_menu(menu=self.file_menu, title='File')
        self.menubar.add_menu(menu=self.settings, title='Settings')
        self.menubar.add_menu(menu=self.advanced, title='Advanced')
    
    def draw(self):
        pass
    
    def quit_app(self, *_):
        constants.APP_CLOSED = True
        logging.info('Closing Pit Mopper...')
        try:
            self.setvar('button pressed', 39393)
        except TclError:
            pass
        self.destroy()
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
        sys.exit()

    def console(self, *_):
        if not self.console_open.get():
            hide_console()
        else:
            show_console()

    def change_theme(self, *_):
        constants.dark_mode = self.dark_mode_state.get()
        if constants.dark_mode:
            logging.info('User switched theme to dark mode')
            constants.CURRENT_BG = constants.DARK_MODE_BG
            constants.CURRENT_FG = constants.DARK_MODE_FG
            CURRENT_BG = constants.DARK_MODE_BG
            CURRENT_FG = constants.DARK_MODE_FG
            dark_title_bar(self)
        else:
            logging.info('User switched theme to light mode')
            constants.CURRENT_BG = constants.DEFAULT_BG
            constants.CURRENT_FG = constants.DEFAULT_FG
            CURRENT_BG = constants.DEFAULT_BG
            CURRENT_FG = constants.DEFAULT_FG
            self.resizable(False, False)

        self.config(bg=CURRENT_BG)
        for child in self.winfo_children():
            if not isinstance(child, (Toplevel, Spinbox, CustomMenuBar, Progressbar, Frame)):
                child.config(bg=CURRENT_BG, fg=CURRENT_FG)
            elif isinstance(child, CustomMenuBar):
                child.change_bg_fg(bg=CURRENT_BG, fg=CURRENT_FG)
            elif isinstance(child, Spinbox):
                if CURRENT_BG == constants.DEFAULT_BG:
                    child.config(bg='white', fg=CURRENT_FG)
                else:
                    child.config(bg=CURRENT_BG, fg=CURRENT_FG)
            elif not isinstance(child, Frame) and not isinstance(child, CustomMenuBar) and not isinstance(child, Progressbar):
                child.config(bg=CURRENT_BG, fg=CURRENT_FG)
            elif isinstance(child, CustomMenuBar):
                child.change_bg_fg(bg=CURRENT_BG, fg=CURRENT_FG)
            elif isinstance(child, Frame):
                for square in child.winfo_children():
                    if isinstance(square, Square):
                        square.switch_theme(CURRENT_BG != constants.DEFAULT_BG)
                    elif isinstance(square, Label):
                        square.config(bg=CURRENT_BG, fg=CURRENT_FG)

    def clear(self):
        """Clears everything on the window, including bindings"""
        for child in self.winfo_children():
            child.destroy()
        if not hasattr(self, 'bindings'):
            self.bindings = {}
        for event, func in self.bindings.items():
            self.unbind_all(event)
        self.bindings = {}

    def _update_game(self):
        self.game: Game
        self.game.mines_found = 0

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
        if constants.APP_CLOSED:
            try:
                self.destroy()
            except TclError:
                pass
            return
        now = datetime.now()
        now = now.replace(microsecond=0)
        if now > self.game.previous_sec:
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
                        self.after(1000)
                        for square2 in squares:
                            precolor = precolors[squares.index(square2)]
                            square2.config(bg=precolor)
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
        game_overs = [
            square.game_over
            for row in self.game.grid.grid
            for square in row
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
        elif any(game_overs):
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
        self.update()
        try:
            self.game = Game(**{
                'grid': self.game.grid,
                'session_start': self.game.session_start,
                'total_time': self.game.total_time,
                'zeros_checked': self.game.zeros_checked,
                'num_mines': self.game.num_mines,
                'chording': self.game.chording,
                'mines_found': self.game.mines_found,
                'additional_time': self.game.additional_time,
                'squares_checked': self.game.squares_checked,
                'previous_sec': self.game.previous_sec,
                'result': {
                    'win': win,
                    'seconds': self.game.seconds,
                    'game over': game_over
                },
                'with_time': self.game.with_time,
                'quit': game_over
            })
        except AttributeError:
            return

