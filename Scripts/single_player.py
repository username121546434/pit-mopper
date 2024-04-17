"""A module that that has the `SinglePlayerApp` class"""
from __future__ import annotations
import pickle
from functools import partial
from tkinter import IntVar, BooleanVar, Variable, StringVar, N, S, E, W, TclError
import os
from datetime import datetime
from tkinter import filedialog, messagebox

from Scripts.multiplayer import MultiplayerApp
from .custom_menubar import CustomMenuBar, SubMenu
from . import constants
from .base_logger import init_logger
init_logger()
from .squares import Square
from .grid import ButtonGrid, PickleButtonGrid
from .functions import *
from .app import App
from .game import Game, PickleGame
from .enums import KBDShortcuts

DEFAULT_TITLE = 'Single Player Game Loader'


def more_info(
    num_mines,
    mines_found,
    squares_clicked_on,
    squares_not_clicked_on,
    start,
    session_start,
    total_squares
):
    messagebox.showinfo('Additional Information', f'''
Total Mines: {num_mines}
Mines found: {mines_found}
Squares clicked on: {len(squares_clicked_on)}
Squares not clicked on: {len(squares_not_clicked_on)}
Total squares: {total_squares}
Ratio of mines: {round((num_mines/total_squares) * 100, 2)}%
Started Game: {start.strftime(constants.STRFTIME)}
Session Started: {session_start.strftime(constants.STRFTIME)}
''')


def load_highscore() -> dict[str, float | int] | float:
    logging.info('Loading highscore...')
    if not os.path.exists(constants.HIGHSCORE_TXT):
        logging.info(f'{constants.HIGHSCORE_TXT} does not exist, looking in root directory')
        if not os.path.exists(os.path.join(os.getcwd(), 'highscore.txt')):
            logging.info('No highscore was found')
            return float('inf')
        else:
            with open(os.path.join(os.getcwd(), 'highscore.txt'), 'rb') as f:
                value = pickle.load(f)
            if isinstance(value, dict):
                logging.info(f'highscore.txt successfully read')
            else:
                logging.info(f'highscore.txt contains invalid data: {value}')
                messagebox.showerror('Highscore value invalide', 'The highscore file contains an invalid value, press OK to delete the content of it')
                logging.info('Removing file...')
                os.remove(constants.HIGHSCORE_TXT)
                value = float('inf')
            messagebox.showerror('Highscore file in wrong place', 'The highscore file was found, but in the wrong spot, as soon as you click OK, Pit Mopper will attempt to move the file to a new location, you might have to delete the file yourself.')
            if not isinstance(value, float):
                with open(constants.HIGHSCORE_TXT, 'wb') as f:
                    pickle.dump(value, f)
            try:
                os.remove(os.path.join(os.getcwd(), 'highscore.txt'))
            except:
                messagebox.showerror('File Delete', 'Unable to delete file, you will have to delete it yourself')
            return value
    else:
        logging.info(f'{constants.HIGHSCORE_TXT} does exist, reading data from it')
        with open(constants.HIGHSCORE_TXT, 'rb') as f:
            value = pickle.load(f)
        if isinstance(value, dict):
            logging.info(f'{constants.HIGHSCORE_TXT} successfully read')
            return value
        else:
            logging.info(f'{constants.HIGHSCORE_TXT} contains invalid data: {value}')
            messagebox.showerror('Highscore value invalide', 'The highscore file contains an invalid value, press OK to delete the content of it')
            logging.info('Removing file...')
            os.remove(constants.HIGHSCORE_TXT)
            return float('inf')


class SinglePlayerApp(App):
    """Subclass of `App`"""
    def draw_menubar(self):
        super().draw_menubar()
        self.file_menu.add_separator()
        self.file_menu.add_command(label='Open File', command=self.load_game, accelerator=format_kbd_shortcut(KBDShortcuts.open_file))
        self.file_menu.add_command(label='Highscores', command=self.show_highscores, accelerator=format_kbd_shortcut(KBDShortcuts.show_highscores))
        self.file_menu.add_separator()
        self.file_menu.add_command(label='Switch to Multiplayer', command=self.switch_multiplayer)
        self.settings.add_separator()
        self.settings.add_checkbutton(variable=self.chord_state, label='Enable Chording', accelerator=format_kbd_shortcut(KBDShortcuts.toggle_chording))
    
    def set_variables(self):
        super().set_variables()
        self.chord_state = BooleanVar(self)
        self.mines = IntVar(self, -1)
        self.mines_counter = StringVar(self, f'Your game will have {self.mines.get()} mines')
        self.cols = IntVar(self)
        self.rows = IntVar(self)
        self.difficulty = Variable(self, (None, None))
        self.game_size = StringVar(self, f'You game size will be {self.difficulty.get()[0]} rows and {self.difficulty.get()[1]} columns')
    
    def draw_all(self):
        self.title(DEFAULT_TITLE)
        super().draw_all()
    
    def draw(self):
        super().draw()
        Label(text='Select Difficulty').pack(pady=(25, 0))

        Radiobutton(
            text="Easy", value=(10, 10), variable=self.difficulty, command=self.change_difficulty
        ).pack()

        Radiobutton(
            text="Medium", value=(20, 20), variable=self.difficulty, command=self.change_difficulty
        ).pack()

        Radiobutton(
            text='Hard', value=(30, 30), variable=self.difficulty, command=self.change_difficulty
        ).pack()

        Label(self, textvariable=self.game_size).pack()

        Spinbox(self, from_=constants.MIN_ROWS_AND_COLS, to=constants.MAX_ROWS_AND_COLS, textvariable=self.rows, width=4, command=partial(self.change_difficulty, True)).pack()
        Spinbox(self, from_=constants.MIN_ROWS_AND_COLS, to=constants.MAX_ROWS_AND_COLS, textvariable=self.cols, width=4, command=partial(self.change_difficulty, True)).pack()

        Label(self, textvariable=self.mines_counter).pack()
        Label(self, text='-1 means it will generate a random number/use default').pack(padx=20)

        Spinbox(self, textvariable=self.mines, width=4, from_= -1, to = 2000, command=self.change_mines).pack()

        self.play_button = Button(self, text='Play!', command=self.create_game)
        self.play_button.pack()

        self.load_last_button = Button(self, text='Load Last Game', command=lambda: self.load_game(file=constants.LAST_GAME_FILE))
        self.load_last_button.pack(pady=(0, 20))

        if self.dark_mode_state.get():
            self.dark_mode_state.set(True)
    
    def set_keyboard_shorcuts(self):
        super().set_keyboard_shorcuts()
        bind_widget(self, KBDShortcuts.open_file, True, self.load_game)
        bind_widget(self, KBDShortcuts.start_game, True, self.create_game)
        bind_widget(self, KBDShortcuts.toggle_chording, True, func=lambda _: self.chord_state.set(not self.chord_state.get()))
        bind_widget(self, KBDShortcuts.show_highscores, True, self.show_highscores)
    
    def quit_app(self, *_):
        if hasattr(self, 'game'):
            if self.game is not None:
                self.save_game(constants.LAST_GAME_FILE)
        super().quit_app()
    
    def change_mines(self):
        self.mines_counter.set(f'Your game will have {self.mines.get()} mines')
        logging.info(f'Setting custom mine count: {self.mines.get()}')

    def change_difficulty(self, from_spinbox:bool = False):
        if not from_spinbox:
            logging.info(f'Setting game size to: {tuple(int(i) for i in self.difficulty.get().split(" "))}')
            self.difficulty.set(tuple(int(i) for i in self.difficulty.get().split(' ')))
        else:
            logging.info(f'Setting custom game size: {(self.rows.get(), self.cols.get())}')
            self.difficulty.set((self.rows.get(), self.cols.get()))
        self.game_size.set(f'Your game size will be {self.difficulty.get()[0]} rows and {self.difficulty.get()[1]} columns')
    
    def validate_game(self, game) -> bool:
        if game is None:
            if self.difficulty.get() == (None, None) or self.difficulty.get() == ('None', 'None'):
                logging.error('Game size not chosen')
                messagebox.showerror(title='Game Size not chosen', message='You have not chosen a game size!')
                return False
            elif self.difficulty.get() >= (60, 60):
                logging.warning(f'Size too big {self.difficulty.get()}')
                messagebox.showwarning(title='Size too big', message='Warning: When the game is a size of 60x60 or above, the expierence might be so laggy it is unplayable.')
            elif self.mines.get() > (self.difficulty.get()[0] * self.difficulty.get()[1]) - 10:
                logging.error(f'Mines too high, game size {self.difficulty.get()}, mines: {self.mines.get()}')
                messagebox.showerror(title='Mines too high', message='You have chosen too many mines.')
                return False
            elif self.mines.get() == 0 or self.mines.get() < -1:
                logging.error(f'Mines too low ({self.mines.get()})')
                messagebox.showerror('Mines too low', 'You cannot have a mine count below 0 with -1 being a special number')
                return False
        return True
    
    def create_game(self, _ = None, game: PickleGame | None = None):
        zeros_checked: list[Square] = []

        if not self.validate_game(game):
            return

        self.clear()
        self.title('Pit Mopper')
        self.resizable(True, True)
        self.grid_columnconfigure(1, weight=1)
        session_start: datetime = datetime.now()
        total_time = StringVar(self)
        if self.dark_mode_state.get():
            dark_title_bar(self)
        Label(self, textvariable=total_time, bg=constants.CURRENT_BG, fg=constants.CURRENT_FG).grid(
            row=1, column=1, sticky=N+S+E+W, pady=(5, 0))
        self.config(bg=constants.CURRENT_BG)

        if game is None:
            chording = self.chord_state.get()
            start = datetime.now()
            logging.info('Creating grid of buttons...')
            grid = ButtonGrid(self.difficulty.get(), self, dark_mode=self.dark_mode_state.get(), num_mines=self.mines.get())
            if constants.APP_CLOSED:
                try:
                    self.destroy()
                except TclError:
                    return
            num_mines = 0
            for square, _ in grid.iter_squares():
                if square.category == 'mine':
                    num_mines += 1
            mines_found = 0

            logging.info(f'''Creating game with following attributes:

start:                 {start}
grid:                  {grid}
zeros_checked:         {zeros_checked}
num_mines:             {num_mines}
chording:              {chording}
mines_found:           {mines_found}
additional_time:       0
''')
            game_size_str = 'x'.join(str(i) for i in self.difficulty.get())
        elif isinstance(game, PickleGame):
            start = game.start
            chording = game.chording
            num_mines = game.num_mines
            grid = game.grid
            game_size_str = 'x'.join(str(i) for i in grid.grid_size)
            total_time.set(f'Time: {format_second(int(game.additional_time))} 🚩0/{game.num_mines}💣')

            mines_found = 0
            for row in grid.grid:
                for square in row:
                    if square.category == 'bomb' and square.clicked_on:
                        mines_found += 1
        
        squares_clicked_on = [
            square
            for row in grid.grid
            for square in row
            if square.clicked_on
        ]

        squares_not_clicked_on = [
            square
            for row in grid.grid
            for square in row
            if square.clicked_on == False
        ]

        highscore_data = load_highscore()
        self.title(f'{game_size_str} Pit Mopper Game')
        logging.info(f'{game_size_str} Pit Mopper Game starting...')
        if not isinstance(highscore_data, (float, int)):
            try:
                highscore = highscore_data[game_size_str]
            except KeyError:
                highscore = float('inf')
        else:
            highscore = float('inf')
        if isinstance(game, PickleGame):
            seconds = game.additional_time
        else:
            seconds = 0.0
        self.menubar = CustomMenuBar(self)
        self.menubar.place(x=0, y=0)
        game_menu = SubMenu()
        bind_widget(self, KBDShortcuts.save_file, True, func=lambda _: self.save_game())
        bind_widget(self, KBDShortcuts.quit_game, True, func=lambda _:  [self.save_game(constants.LAST_GAME_FILE), self.clear(), setattr(self.game, 'quit', True), self.draw_all()])
        bind_widget(self, KBDShortcuts.game_info, True, func=lambda _: more_info(
            num_mines, mines_found, squares_clicked_on, squares_not_clicked_on, start, session_start,  grid.grid_size[0] * grid.grid_size[1]))
        bind_widget(self, KBDShortcuts.fullscreen, all_=True, func=lambda *_: self.fullscreen_state.set(not self.fullscreen_state.get()))
        bind_widget(self, KBDShortcuts.toggle_theme, all_=True, func=lambda *_: self.dark_mode_state.set(not self.dark_mode_state.get()))

        game_menu.add_checkbutton(label='Dark Mode', accelerator=format_kbd_shortcut(KBDShortcuts.toggle_theme), variable=self.dark_mode_state)
        game_menu.add_separator()
        game_menu.add_command(label='Save As', accelerator=format_kbd_shortcut(KBDShortcuts.save_file), command=self.save_game)
        game_menu.add_command(label='More Info', command=lambda: more_info(
            num_mines, mines_found, squares_clicked_on, squares_not_clicked_on, start, session_start, grid.grid_size[0] * grid.grid_size[1]),
            accelerator=format_kbd_shortcut(KBDShortcuts.game_info))
        game_menu.add_checkbutton(label='Fullscreen', variable=self.fullscreen_state, accelerator=format_kbd_shortcut(KBDShortcuts.fullscreen))
        game_menu.add_command(label='Exit', command=lambda: [self.save_game(constants.LAST_GAME_FILE), self.clear(), setattr(self.game, 'quit', True), self.draw_all()], accelerator=format_kbd_shortcut(KBDShortcuts.quit_game))

        self.menubar.add_menu(menu=game_menu, title='Game')

        logging.info('Entering while loop...')

        self._game(
            game,
            grid,
            session_start,
            total_time,
            zeros_checked,
            num_mines,
            chording, 
            mines_found,
        )
        win = self.game.result['win']
        seconds = self.game.result['seconds']
        mines_found = self.game.mines_found
        if win:
            messagebox.showinfo(
                'Game Over',
                f'Game Over.\nYou won!\nYou found {mines_found} out of {num_mines} mines.\nTime: {format_second(seconds)}\nHighscore: {format_second(highscore)}'
            )
        else:
            messagebox.showinfo(
                'Game Over',
                f'Game Over.\nYou lost.\nYou found {mines_found} out of {num_mines} mines.\nTime: {format_second(seconds)}\nHighscore: {format_second(highscore)}'
            )
        if win and seconds < highscore:
            logging.info('Highscore has been beaten, writing new highscore data')
            with open(constants.HIGHSCORE_TXT, 'wb') as f:
                if isinstance(highscore_data, dict):
                    new_highscore_data = highscore_data.copy()
                else:
                    new_highscore_data = {}
                new_highscore_data[game_size_str] = seconds
                pickle.dump(new_highscore_data, f)
        logging.info('Destroying window')
        self.fullscreen_state.set(False)
        self.clear()
        self.draw_all()
        del self.game
    
    def show_highscores(self, *_):
        logging.info('User requested highscores')
        highscore_data = load_highscore()

        if isinstance(highscore_data, dict):
            logging.info(f'Highscore data detected: {highscore_data}')
            data = [['Game Size', 'Seconds']]
            for key, value in highscore_data.items():
                data.append([key, str(round(value, 1))])
            self.clear()
            self.title('Highscores')
            self.config(padx=50, pady=20)
            frame = Frame(self, bg='black')
            self.grid_columnconfigure(0, weight=1)
            self.grid_rowconfigure(0, weight=1)
            frame.grid(row=0, column=0)

            if self.dark_mode_state.get():
                self.config(bg=constants.DARK_MODE_BG)
                dark_title_bar(self)
                bg_of_labels = constants.DARK_MODE_BG
                fg_of_labels = constants.DARK_MODE_FG
            else:
                bg_of_labels = constants.DEFAULT_BG
                fg_of_labels = constants.DEFAULT_FG

            for y, row in enumerate(data):
                frame.rowconfigure(y, weight=1)
                for x, item in enumerate(row):
                    frame.columnconfigure(x, weight=1)
                    Label(frame, text=str(item), bg=bg_of_labels, fg=fg_of_labels).grid(row=y, column=x, padx=1, pady=1, sticky='nsew')
            Button(self,
                    text='Exit', 
                    bg=constants.CURRENT_BG, 
                    fg=constants.CURRENT_FG,
                    command=lambda: [self.config(padx=0, pady=0), self.clear(), self.draw_all()][0]
                ).grid(row=1, column=0)
            self.update()
        else:
            logging.info('No highscores found')
            messagebox.showinfo('Highscores', 'No highscores were found, play a game and win it to get some')
    
    def load_game(self, _=None, file: str|None=None):
        logging.info('Opening game...')
        if file is None:
            file = filedialog.askopenfilename(filetypes=(('Pit Mopper Game Files', f'*{constants.APP_FILE_EXT}'), ('Any File', '*.*')))
        if not file:
            return

        logging.info(f'Reading {file}...')
        try:
            with open(file, 'rb') as f:  # Un Pickling
                try:
                    data = pickle.load(f)
                except Exception:
                    messagebox.showerror('Invalid File', 'It seems like this is an invalid file')
                    logging.info(f'Invalid File:\n\n{traceback.format_exc()}')
                    return
        except FileNotFoundError:
            messagebox.showerror('File not found', 'The file does not exist')
            return
        if not isinstance(data, (PickleGame, dict)):
            messagebox.showerror('Invalid Data', 'It seems like this is a file which has invalid data')
            logging.info(f'Invalid File Data:\n\n{data}')
            return
        
        if isinstance(data, dict):
            try:
                data = PickleGame.from_dict(data)
            except Exception:
                messagebox.showerror('Load Error', 'There was an error while loading the file')
                logging.info(f'Load Error File Data:\n\n{data}')
                return


        logging.info(f'{file} successfully read, setting up game...')

        self.create_game(None, game=data)
    
    def _game(
        self,
        game: PickleGame | None,
        grid: ButtonGrid | PickleButtonGrid,
        session_start: datetime,
        total_time: StringVar,
        zeros_checked: list[Square] | None = None,
        num_mines: int = 0,
        chording: bool = False,
        mines_found: int = 0,
        additional_time: float = 0.0,
    ):
        if zeros_checked == None:
            zeros_checked = []
        if game is None:
            assert isinstance(grid, ButtonGrid)
            self.game = Game(
                grid,
                total_time,
                session_start,
                zeros_checked,
                num_mines,
                chording,
                mines_found,
                additional_time,
            )
        else:
            self.game = game.to_game(total_time, self)
        self.game_over = BooleanVar(self, name='game_over')
        change_theme_of_window(self)
        self.after(50, self._update_game)
        self.wait_variable('game_over')
        self.after_cancel(self.game_after_cancel)
    
    def save_game(self, filename: str | None = None):
        data = PickleGame.from_game(self.game)
        logging.info(f'''Saving game with the following attributes:
    {data}
    ''')
        logging.info(f'Data to save: {data}')
        if filename is None:
            filename = filedialog.asksaveasfilename(filetypes=(('Pit Mopper Game Files', f'*{constants.APP_FILE_EXT}'), ('Any File', '*.*')))
            msgboxes = True
        else:
            msgboxes = False
        if not filename:
            return
        with open(filename, 'wb') as f:  # Pickling
            if msgboxes:
                messagebox.showinfo('Save Game', 'You game is being saved right now, this may a few moments. Please wait until another popup comes before closing the game.')
            logging.info('Saving data...')
            pickle.dump(data, f)
            logging.info('Data successfully saved')
            if msgboxes:
                messagebox.showinfo('Save Game', 'Your game has been saved, you can now close the game.')


def main():
    logging.info('Loading single player...')

    window = SinglePlayerApp(DEFAULT_TITLE)
    
    if len(sys.argv) > 1:
        if os.path.exists(sys.argv[1]):
            logging.info('User opened app with a file')
            window.load_game(file=sys.argv[1])

    logging.info('GUI successfully created')
    window.mainloop()
