import pickle
from functools import partial
from tkinter import *
import os
from datetime import datetime
from tkinter import filedialog, messagebox

from . import constants
from .console_window import *
from .functions import _update_game
get_console()
# Creates AppData folder if doesn't exist
if not os.path.exists(DEBUG):
    os.makedirs(DEBUG)
from .base_logger import init_logger
init_logger()
from .custom_menubar import CustomMenuBar
from .squares import PickleSquare, Square
from .grid import ButtonGrid, PickleButtonGrid
from .squares import PickleSquare, Square
from .functions import *
from .app import App
import gc
logging.info('Loading Single Player...')


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
Started Game: {start.strftime(STRFTIME)}
Session Started: {session_start.strftime(STRFTIME)}
''')


def save_game(
    start,
    total_time,
    grid,
    zeros_checked,
    num_mines,
    chording,
):
    global difficulty
    logging.info(f'''Saving game with the following attributes:

start:               {start}
total_time:          {total_time}
grid:                {grid}
zeros_checked:       {zeros_checked}
num_mines:           {num_mines}
chording:            {chording}
grid.grid_size       {grid.grid_size}
''')
    data = {
        'start': start,
        'time played': total_time,
        'grid': PickleButtonGrid.from_grid(grid),
        'zeros checked': zeros_checked,
        'num mines': num_mines,
        'chording': chording,
        'difficulty': difficulty.get()
    }
    logging.info(f'Data to save: {data}')
    with filedialog.asksaveasfile('wb', filetypes=(('Pit Mopper Game Files', '*.min'), ('Any File', '*.*'))) as f:  # Pickling
        messagebox.showinfo('Save Game', 'You game is being saved right now, this may a few moments. Please wait until another popup comes before closing the game.')
        logging.info('Saving data...')
        pickle.dump(data, f)
        logging.info('Data successfully saved')
        messagebox.showinfo('Save Game', 'Your game has been saved, you can now close the game.')


def update_game(
    game_window: Toplevel,
    grid: ButtonGrid,
    session_start: datetime,
    total_time: StringVar,
    zeros_checked: list[Square] = None,
    num_mines: int = 0,
    chording: bool = None,
    mines_found: int = 0,
    additional_time: float = 0.0,
):
    if zeros_checked == None:
        zeros_checked = []
    result = _update_game(
        game_window,
        grid,
        session_start,
        total_time,
        zeros_checked,
        num_mines,
        chording,
        mines_found,
        additional_time
    )
    result2 = result.get('result')
    while True:
        if not isinstance(result, dict):
            return None
        game_window.after(100, do_nothing)
        result = _update_game(**result)
        result2 = result.get('result')
        if result2['game over']:
            result2['mines_found'] = result['mines_found']
            return result2
        try:
            game_window.winfo_exists()
        except TclError:
            return None


def load_game(_=None):
    logging.info('Opening game...')
    file = filedialog.askopenfile('rb', filetypes=(('Pit Mopper Game Files', '*.min'), ('Any File', '*.*')))
    if file == None:
        return
    else:
        logging.info(f'Reading {file}...')
        with file as f:  # Un Pickling
            data = pickle.load(f)
            data: dict[str]
    logging.info(f'{file} successfully read, setting up game...')

    game_window = Toplevel(window)
    game_window.iconbitmap(LOGO)
    game_window.title('Pit Mopper')

    grid = data['grid'].grid
    button_grid = ButtonGrid(data['grid'].grid_size, game_window, grid, window.dark_mode_state.get())

    start: datetime = data['start']
    time = data['time played']
    num_mines: int = data['num mines']
    zeros_checked = data['zeros checked']
    chording = data['chording']
    game_window.grid_columnconfigure(1, weight=1)

    mines_found = 0
    for row in button_grid.grid:
        for square in row:
            if square.category == 'mine' and square.cget('text') == '🚩':
                mines_found += 1

    create_game(
        None,
        game_window,
        start,
        button_grid,
        zeros_checked,
        num_mines,
        chording,
        mines_found,
        additional_time=time,
    )


def create_game(
    _ = None,
    game_window: Toplevel = None,
    start: datetime = None,
    grid: ButtonGrid = None,
    zeros_checked: list[Square] = None,
    num_mines: int = 0,
    chording: bool = None,
    mines_found: int = 0,
    additional_time: float = 0.0
):
    if zeros_checked == None:
        zeros_checked = []
    if game_window == None:
        game_window = Toplevel(window)
        game_window.iconbitmap(LOGO)
        game_window.title('Pit Mopper')
        game_window.grid_columnconfigure(1, weight=1)
        chording = chord_state.get()

        start = datetime.now()

        if difficulty.get() == (None, None) or difficulty.get() == ('None', 'None'):
            logging.error('Game size not chosen')
            messagebox.showerror(title='Game Size not chosen', message='You have not chosen a game size!')
            game_window.destroy()
            return
        elif difficulty.get() >= (60, 60):
            logging.warning(f'Size too big {difficulty.get()}')
            messagebox.showwarning(title='Size too big', message='Warning: When the game is a size of 60x60 or above, the expierence might be so laggy it is unplayable.')
        elif mines.get() > (difficulty.get()[0] * difficulty.get()[1]) - 10:
            logging.error(f'Mines too high, game size {difficulty.get()}, mines: {mines.get()}')
            messagebox.showerror(title='Mines too high', message='You have chosen too many mines.')
            game_window.destroy()
            return
        elif mines.get() == 0 or mines.get() < -1:
            logging.error(f'Mines too low ({mines.get()})')
            messagebox.showerror('Mines too low', 'You cannot have a mine count below 0 with -1 being a special number')
            game_window.destroy()
            return
        elif mines.get() > ((difficulty.get()[0] * difficulty.get()[1])/2):
            logging.warning(f'Number of mines high, game size {difficulty.get()}, mines: {mines.get()}')
            messagebox.showwarning(title='Number of mines high', message='You have chosen a high amount of mines, so it might take a long time to place them all')

    if window.dark_mode_state.get():
        dark_title_bar(game_window)

    logging.info(f'''Creating game with following attributes:

game_window:           {game_window}
start:                 {start}
grid:                  {grid}
zeros_checked:         {zeros_checked}
num_mines:             {num_mines}
chording:              {chording}
mines_found:           {mines_found}
additional_time:       {additional_time}
''')
    session_start: datetime = datetime.now()
    total_time = StringVar(game_window)

    Label(game_window, textvariable=total_time, bg=constants.CURRENT_BG, fg=constants.CURRENT_FG).grid(
        row=1, column=1, sticky=N+S+E+W, pady=(5, 0))
    game_window.config(bg=constants.CURRENT_BG)

    if grid == None:
        logging.info('Creating grid of buttons...')
        grid = ButtonGrid(difficulty.get(), game_window, dark_mode=window.dark_mode_state.get(), num_mines=mines.get())
        if constants.APP_CLOSED:
            try:
                game_window.destroy()
            except TclError:
                return
        for row in grid.grid:
            for square in row:
                if square.category == 'mine':
                    num_mines += 1

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

    if additional_time != 0.0:
        total_time.set(f'Time: {format_second(int(additional_time))} 🚩0/{num_mines}💣')

    highscore_data = load_highscore()
    game_size_str = f'{difficulty.get()[0]}x{difficulty.get()[1]}'
    game_window.title(f'{game_size_str} Pit Mopper Game')
    logging.info(f'{game_size_str} Pit Mopper Game starting...')
    if not isinstance(highscore_data, float):
        try:
            highscore = highscore_data[game_size_str]
        except KeyError:
            highscore = float('inf')
    else:
        highscore = float('inf')
    seconds = additional_time

    # create a menubar
    menubar = CustomMenuBar(game_window, bg=constants.CURRENT_BG, fg=constants.CURRENT_FG)
    menubar.place(x=0, y=0)

    # create the file_menu
    file_menu = Menu(
        menubar,
        tearoff=0
    )
    game_window.bind('<Control-s>', lambda _: save_game(start, seconds, grid, zeros_checked, num_mines, chording))
    game_window.bind('<Alt-q>', lambda _: game_window.destroy())
    game_window.bind('<Alt-i>', lambda _: more_info(
        num_mines, mines_found, squares_clicked_on, squares_not_clicked_on, start, session_start,  grid.grid_size[0] * grid.grid_size[1]))

    file_menu.add_command(label='Save As', accelerator='Ctrl+S', command=partial(save_game, start, seconds, grid, [
                          PickleSquare.from_square(square) for square in zeros_checked], num_mines, chording))
    file_menu.add_command(label='More Info', command=lambda: more_info(
        num_mines, mines_found, squares_clicked_on, squares_not_clicked_on, start, session_start, grid.grid_size[0] * grid.grid_size[1]),
        accelerator='Alt+I')
    file_menu.add_command(label='Exit', command=game_window.destroy, accelerator='Alt+Q')

    menubar.add_menu(menu=file_menu, title='File')

    logging.info('Entering while loop...')
    result = update_game(
        game_window,
        grid,
        session_start,
        total_time,
        zeros_checked,
        num_mines,
        chording,
        mines_found,
        additional_time
    )
    if not isinstance(result, dict):
        return
    win = result['win']
    seconds = result['seconds']
    mines_found = result['mines_found']
    del result
    gc.collect()
    if win:
        messagebox.showinfo(
            'Game Over', f'Game Over.\nYou won!\nYou found {mines_found} out of {num_mines} mines.\nTime: {format_second(seconds)}\nHighscore: {format_second(highscore)}')
    else:
        messagebox.showinfo(
            'Game Over', f'Game Over.\nYou lost.\nYou found {mines_found} out of {num_mines} mines.\nTime: {format_second(seconds)}\nHighscore: {format_second(highscore)}')
    if win and seconds < highscore:
        logging.info('Highscore has been beaten, writing new highscore data')
        with open(HIGHSCORE_TXT, 'wb') as f:
            if isinstance(highscore_data, dict):
                new_highscore_data = highscore_data.copy()
            else:
                new_highscore_data = {}
            new_highscore_data[game_size_str] = seconds
            pickle.dump(new_highscore_data, f)
    logging.info('Destroying window')
    game_window.destroy()
    gc.collect()


def change_difficulty(from_spinbox:bool = False):
    global game_size
    global difficulty
    if not from_spinbox:
        logging.info(f'Setting game size to: {tuple(int(i) for i in difficulty.get().split(" "))}')
        difficulty.set(tuple(int(i) for i in difficulty.get().split(' ')))
    else:
        logging.info(f'Setting custom game size: {(rows.get(), cols.get())}')
        difficulty.set((rows.get(), cols.get()))
    game_size.set(f'Your game size will be {difficulty.get()[0]} rows and {difficulty.get()[1]} columns')


def load_highscore() -> dict[str, float | int] | float:
    logging.info('Loading highscore...')
    if not os.path.exists(HIGHSCORE_TXT):
        logging.info(f'{HIGHSCORE_TXT} does not exist, looking in root directory')
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
                os.remove(HIGHSCORE_TXT)
                value = float('inf')
            messagebox.showerror('Highscore file in wrong place', 'The highscore file was found, but in the wrong spot, as soon as you click OK, Pit Mopper will attempt to move the file to a new location, you might have to delete the file yourself.')
            if not isinstance(value, float):
                with open(HIGHSCORE_TXT, 'wb') as f:
                    pickle.dump(value, f)
            try:
                os.remove(os.path.join(os.getcwd(), 'highscore.txt'))
            except:
                messagebox.showerror('File Delete', 'Unable to delete file, you will have to delete it yourself')
            return value
    else:
        logging.info(f'{HIGHSCORE_TXT} does exist, reading data from it')
        with open(HIGHSCORE_TXT, 'rb') as f:
            value = pickle.load(f)
        if isinstance(value, dict):
            logging.info(f'{HIGHSCORE_TXT} successfully read')
            return value
        else:
            logging.info(f'{HIGHSCORE_TXT} contains invalid data: {value}')
            messagebox.showerror('Highscore value invalide', 'The highscore file contains an invalid value, press OK to delete the content of it')
            logging.info('Removing file...')
            os.remove(HIGHSCORE_TXT)
            return float('inf')


def show_highscores(_=None):
    logging.info('User requested highscores')
    highscore_data = load_highscore()

    if isinstance(highscore_data, dict):
        logging.info(f'Highscore data detected: {highscore_data}')
        data = [['Game Size', 'Seconds']]
        for key, value in highscore_data.items():
            data.append([key, str(round(value, 1))])

        new_window = Toplevel(window)
        new_window.title('Highscores')
        new_window.iconbitmap(LOGO)
        new_window.config(padx=50, pady=20)
        frame = Frame(new_window, bg='black')
        new_window.grid_columnconfigure(0, weight=1)
        new_window.grid_rowconfigure(0, weight=1)
        frame.grid(row=0, column=0)

        if window.dark_mode_state.get():
            new_window.config(bg=DARK_MODE_BG)
            dark_title_bar(new_window)
            bg_of_labels = DARK_MODE_BG
            fg_of_labels = DARK_MODE_FG
        else:
            bg_of_labels = DEFAULT_BG
            fg_of_labels = DEFAULT_FG

        for y, row in enumerate(data):
            Grid.rowconfigure(frame, y, weight=1)
            for x, item in enumerate(row):
                Grid.columnconfigure(frame, x, weight=1)
                Label(frame, text=str(item), bg=bg_of_labels, fg=fg_of_labels).grid(row=y, column=x, padx=1, pady=1, sticky='nsew')
        new_window.update()
    else:
        logging.info('No highscores found')
        messagebox.showinfo('Highscores', 'No highscores were found, play a game and win it to get some')


def change_mines():
    mines_counter.set(f'Your game will have {mines.get()} mines')
    logging.info(f'Setting custom mine count: {mines.get()}')


logging.info('Functions successfully defined, creating GUI')

window = App('Game Loader')

Label(text='Select Difficulty').pack(pady=(25, 0))

# Variable to hold on to which radio button value is checked.
difficulty = Variable(window, (None, None))

Radiobutton(
    text="Easy", value=(10, 10), variable=difficulty, command=change_difficulty
).pack()

Radiobutton(
    text="Medium", value=(20, 20), variable=difficulty, command=change_difficulty
).pack()

Radiobutton(
    text='Hard', value=(30, 30), variable=difficulty, command=change_difficulty
).pack()

game_size = StringVar(window, f'You game size will be {difficulty.get()[0]} rows and {difficulty.get()[1]} columns')

Label(window, textvariable=game_size).pack()

cols = IntVar(window)
rows = IntVar(window)

Spinbox(window, from_=MIN_ROWS_AND_COLS, to=MAX_ROWS_AND_COLS, textvariable=rows, width=4, command=partial(change_difficulty, True)).pack()
Spinbox(window, from_=MIN_ROWS_AND_COLS, to=MAX_ROWS_AND_COLS, textvariable=cols, width=4, command=partial(change_difficulty, True)).pack()

mines = IntVar(window, -1)

mines_counter = StringVar(window, f'Your game will have {mines.get()} mines')

Label(window, textvariable=mines_counter).pack()
Label(window, text='-1 means it will generate a random number/use default').pack(padx=20)

Spinbox(window, textvariable=mines, width=4, from_= -1, to = 2000, command=change_mines).pack()

Button(window, text='Play!', command=create_game).pack(pady=(0, 20))

window.file_menu.add_separator()
window.file_menu.add_command(label='Open File', command=load_game, accelerator='Ctrl+O')
window.file_menu.add_command(label='Highscores', command=show_highscores, accelerator='Ctrl+H')

chord_state = BooleanVar(window)

window.settings.add_separator()
window.settings.add_checkbutton(variable=chord_state, label='Enable Chording', accelerator='Ctrl+A')

# Keyboard Shortcuts
bindWidget(window, '<Control-o>', True, load_game)
bindWidget(window, '<space>', True, create_game)
bindWidget(window, '<Control-h>', True, show_highscores)

logging.info('GUI successfully created')
window.mainloop()
