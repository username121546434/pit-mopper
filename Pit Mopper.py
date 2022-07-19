import pickle
import sys
import traceback
import webbrowser
from functools import partial
from tkinter import *
import ctypes
import os
import shutil
from datetime import datetime
from tkinter import filedialog, messagebox

from Scripts.constants import *
from Scripts.console_window import *
# Creates AppData folder if doesn't exist
if not os.path.exists(DEBUG):
    os.makedirs(DEBUG)
from Scripts.base_logger import init_logger
get_console()
init_logger()
from Scripts.custom_menubar import CustomMenuBar
from Scripts.squares import PickleSquare, Square
from Scripts.grid import ButtonGrid, PickleButtonGrid
from Scripts.squares import PickleSquare, Square


from Scripts.network import check_internet
from Scripts.updater import check_for_updates

import pyperclip

__version__ = '1.4.0'
__license__ = 'GNU GPL v3, see LICENSE.txt for more info'


logging.info('Loading app...')

def handle_exception(exc_type, exc_value, exc_traceback):
    if issubclass(exc_type, KeyboardInterrupt):
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return
    sys.last_type = exc_type
    sys.last_value = exc_value
    sys.last_traceback = exc_traceback
    messagebox.showerror('Unknown Error', f'There has been an error, details are below\n\n{exc_value}')
    if check_internet():
        if messagebox.askyesno('Unknown Error', 'Would you like to submit a bug report?'):
            bug_report()
    logging.critical("Uncaught exception", exc_info=(exc_type, exc_value, exc_traceback))

sys.excepthook = handle_exception


def console(*_):
    if not console_open.get():
        hide_console()
    else:
        show_console()


def format_second(seconds: int | float):
    if seconds != float('inf'):
        seconds = int(seconds)
        minutes = int(seconds / 60)
        sec = seconds % 60
        if sec < 10:
            sec = f'0{sec % 60}'

        return f'{minutes}:{sec}'
    else:
        return 'None'


def dark_title_bar(window):
    """
    MORE INFO:
    https://docs.microsoft.com/en-us/windows/win32/api/dwmapi/ne-dwmapi-dwmwindowattribute
    """
    # https://stackoverflow.com/a/70724666
    window.update()
    DWMWA_USE_IMMERSIVE_DARK_MODE = 20
    set_window_attribute = ctypes.windll.dwmapi.DwmSetWindowAttribute
    get_parent = ctypes.windll.user32.GetParent
    hwnd = get_parent(window.winfo_id())
    rendering_policy = DWMWA_USE_IMMERSIVE_DARK_MODE
    value = 2
    value = ctypes.c_int(value)
    set_window_attribute(hwnd, rendering_policy, ctypes.byref(value),
                         ctypes.sizeof(value))


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
    button_grid = ButtonGrid(data['grid'].grid_size, game_window, grid, dark_mode_state.get())

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
    zeros_checked: list[Square] = [],
    num_mines: int = 0,
    chording: bool = None,
    mines_found: int = 0,
    additional_time: float = 0.0
):
    global after_cancel
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

    if dark_mode_state.get():
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

    Label(game_window, textvariable=total_time, bg=CURRENT_BG, fg=CURRENT_FG).grid(
        row=1, column=1, sticky=N+S+E+W, pady=(5, 0))
    game_window.config(bg=CURRENT_BG)

    if grid == None:
        logging.info('Creating grid of buttons...')
        grid = ButtonGrid(difficulty.get(), game_window, dark_mode=dark_mode_state.get(), num_mines=mines.get())
        if APP_CLOSED:
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
    menubar = CustomMenuBar(game_window, bg=CURRENT_BG, fg=CURRENT_FG)
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
    previous_sec = datetime.now()
    previous_sec = previous_sec.replace(microsecond=0)
    squares_flaged = []
    squares_checked = []

    logging.info('Entering while loop...')
    while True:
        if APP_CLOSED:
            try:
                game_window.destroy()
            except TclError:
                pass
            return
        after_cancel.append(window.after(100, do_nothing))

        now = datetime.now()
        now = now.replace(microsecond=0)
        if now > previous_sec:
            previous_sec = now
            seconds = (now - session_start).total_seconds() + additional_time

        percent = round(((len(squares_flaged))/num_mines) * 100, 2)
        total_time.set(f'Time: {format_second(seconds)}  🚩 {len(squares_flaged)}/{num_mines} 💣 ({percent}%)')

        for row in grid.iter_rows():
            # Clicks Zeros
            for square in (square for square in row if (square.num == None) and (square.clicked_on) and (square not in zeros_checked) and (square.category != 'mine')):
                zeros_checked.append(square)
                for square2 in (square2 for square2 in grid.around_square(*square.position) if (square2.category != 'mine') and square2 not in squares_checked):
                    square2.clicked()

            # Counts mines found
            for square in (square for square in squares_flaged if square.category == 'mine'):
                mines_found += 1

            if chording:
                # Checks all square if they are completed
                for square in (square for square in row if square.completed == False):
                    mines_around_square = [square for square in grid.around_square(
                        *square.position) if (square.category == 'mine') and (square.clicked_on == True)]
                    if (len(mines_around_square) == square.num and all(mine.category == 'mine' for mine in mines_around_square)) or square.num == None:
                        square.completed = True

                # Shows all squares around a square if it was middle clicked
                for square in (square for square in row if (square.chord)):
                    if square.completed == False:
                        precolors = []
                        squares = [
                            square
                            for square in grid.around_square(*square.position)
                            if square.clicked_on == False
                        ]
                        for square2 in squares:
                            precolors.append(square2.cget('bg'))
                            square2.config(bg='brown')
                        game_window.update()
                        game_window.after(1000)
                        for square2 in squares:
                            precolor = precolors[squares.index(square2)]
                            square2.config(bg=precolor)
                    else:
                        for square2 in (square for square in grid.around_square(*square.position) if not square.clicked_on and square.category != 'mine'):
                            square2.clicked()
                        square.chord = False
        mines_found = 0

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

        squares_flaged = [
            square
            for row in grid.grid
            for square in row
            if square.flaged
        ]

        game_overs = [
            square.game_over
            for row in grid.grid
            for square in row
        ]

        if (len(squares_clicked_on) == (grid.grid_size[0] * grid.grid_size[1]) and all(square.category == 'mine' for square in squares_flaged)) or \
                (all(square.category == 'mine' for square in squares_not_clicked_on) and len(squares_not_clicked_on) == num_mines):
            game_over = True
            win = True
            if (len(squares_clicked_on) == (grid.grid_size[0] * grid.grid_size[1]) and all(square.category == 'mine' for square in squares_flaged)):
                logging.info('Game has been won because all squares are clicked and all mines flagged')
            else:
                logging.info('Game has been won because the squares left are mines')
        elif any(game_overs):
            logging.info('The game is over, and it is lost.')
            game_over = True
            win = False
        else:
            game_over = False

        if game_over:
            for row in grid.grid:
                for square in row:
                    if square.category == 'mine' and square.cget('text') != '🚩':
                        square.clicked()
                    elif square.category == 'mine' and square.cget('text') == '🚩':
                        mines_found += 1
                        square.config(text='✅')
                    elif square.num != None and square.cget('text') == '🚩':
                        square.config(text='❌')
            game_window.update()
            break
        game_window.update()

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


def change_theme(*_):
    global CURRENT_BG, CURRENT_FG
    if dark_mode_state.get():
        logging.info('User switched theme to dark mode')
        CURRENT_BG = DARK_MODE_BG
        CURRENT_FG = DARK_MODE_FG
        dark_title_bar(window)
    else:
        logging.info('User switched theme to light mode')
        CURRENT_BG = DEFAULT_BG
        CURRENT_FG = DEFAULT_FG
        window.resizable(False, False)

    window.config(bg=CURRENT_BG)
    for child in window.winfo_children():
        if not isinstance(child, Toplevel) and not isinstance(child, Spinbox) and not isinstance(child, CustomMenuBar):
            child.config(bg=CURRENT_BG, fg=CURRENT_FG)
        elif isinstance(child, CustomMenuBar):
            child.change_bg_fg(bg=CURRENT_BG, fg=CURRENT_FG)
        elif isinstance(child, Spinbox):
            if CURRENT_BG == DEFAULT_BG:
                child.config(bg='white', fg=CURRENT_FG)
            else:
                child.config(bg=CURRENT_BG, fg=CURRENT_FG)
        elif isinstance(child, Toplevel):
            if CURRENT_BG == DARK_MODE_BG:
                dark_title_bar(child)
            else:
                child.resizable(True, True)
            child.config(bg=CURRENT_BG)
            for child2 in child.winfo_children():
                if not isinstance(child2, Frame) and not isinstance(child2, CustomMenuBar):
                    child2.config(bg=CURRENT_BG, fg=CURRENT_FG)
                elif isinstance(child2, CustomMenuBar):
                    child2.change_bg_fg(bg=CURRENT_BG, fg=CURRENT_FG)
                elif isinstance(child2, Frame):
                    for square in child2.winfo_children():
                        if isinstance(square, Square):
                            square.switch_theme()
                        elif isinstance(square, Label):
                            square.config(bg=CURRENT_BG, fg=CURRENT_FG)


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

        if dark_mode_state.get():
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


def do_nothing():
    pass


def quit_app(_=None):
    global window, APP_CLOSED
    APP_CLOSED = True
    logging.info('Closing Pit Mopper...')
    for code in after_cancel:
        window.after_cancel(code)
    window.setvar('button pressed', 39393)
    window.destroy()
    logging.shutdown()
    if del_data == 'all':
        try:
            shutil.rmtree(APPDATA)
        except FileNotFoundError:
            pass
    elif del_data == 'debug':
        try:
            shutil.rmtree(DEBUG)
        except FileNotFoundError:
            pass
    elif del_data == 'highscore':
        try:
            os.remove(HIGHSCORE_TXT)
        except FileNotFoundError:
            pass
    del window
    sys.exit()


def change_mines():
    mines_counter.set(f'Your game will have {mines.get()} mines')
    logging.info(f'Setting custom mine count: {mines.get()}')


def clear_all_data():
    global del_data
    if messagebox.askyesno('Delete Data', 'Are you sure you want to delete all data? This includes highscores and debug logs and may break some features.'):
        logging.info('Requested to delete all data')
        del_data = 'all'
        messagebox.showinfo('Delete Data', 'As soon as you close Pit Mopper, all data will be deleted')


def clear_debug():
    global del_data
    if messagebox.askyesno('Delete Data', 'Are you sure you want to delete the debug logs?'):
        logging.info('Requested to delete debug logs')
        del_data = 'debug'
        messagebox.showinfo('Delete Data', 'As soon as you close Pit Mopper, the debug logs will be deleted')


def clear_highscore():
    global del_data
    if messagebox.askyesno('Delete Data', 'Are you sure you want to delete your higscores?'):
        logging.info('Requested to delete highscore data')
        del_data = 'highscore'
        messagebox.showinfo('Delete Data', 'As soon as you close Pit Mopper, the your highscores will be deleted')


def bug_report():
    new_window = Toplevel(window)
    new_window.config(padx=20, pady=20)
    window.unbind_all('<space>')

    Label(new_window, text='Enter a description of what happenned below, also include information about which platform you are on etc').pack()
    description = Text(new_window, width=1, height=1)
    description.pack(side='top',fill='both',expand=True)

    Button(new_window, text='Continue', command=lambda: make_github_issue(body=description.get('1.0', 'end'))).pack()
    window.wait_window(new_window)
    if not APP_CLOSED:
        window.bind_all('<space>', create_game)


def make_github_issue(body=None):
    with open(debug_log_file, 'r') as f:
        debug_log = f.read()
    last_traceback = traceback.format_exc()
    body = f'''This is an auto generated bug report

## Description
{body}

## More information
Traceback: {sys.last_traceback}
Type: {sys.last_type}
Value: {sys.last_value}

Full Traceback:
```
{last_traceback}```

<details>
  <summary>
    Debug Log Output
  </summary>
{debug_log.splitlines()[0]}

{"".join(debug_log.splitlines(True)[1:])}
</details>
'''
    messagebox.showinfo('Bug Report', 'As soon as you press OK, you will be directed to a link where you can report this bug and an auto generated issue will be copied to your clipboard')
    pyperclip.copy(body)
    webbrowser.open('https://github.com/username121546434/pit-mopper/issues')


logging.info('Functions successfully defined, creating GUI')

window = Tk()
window.title('Game Loader')
window.iconbitmap(default=LOGO, bitmap=LOGO)
window.resizable(False, False)
window.report_callback_exception = handle_exception

after_cancel = []
del_data = 'none'

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

chord_state = BooleanVar(window)
console_open = BooleanVar(window, False)
console_open.trace('w', console)
dark_mode_state = BooleanVar(window)
dark_mode_state.trace('w', change_theme)  

Button(window, text='Play!', command=create_game).pack(pady=(0, 20))

# create a menubar
menubar = CustomMenuBar(window)
menubar.place(x=0, y=0)

# create the file_menu
file_menu = Menu(
    menubar,
    tearoff=0
)
file_menu.add_command(label='Open File', command=load_game, accelerator='Ctrl+O')
file_menu.add_command(label='Highscores', command=show_highscores, accelerator='Ctrl+H')
file_menu.add_separator()
file_menu.add_command(label='Exit', command=quit_app, accelerator='Ctrl+Q')

settings = Menu(menubar, tearoff=0)
settings.add_checkbutton(variable=chord_state, label='Enable Chording', accelerator='Ctrl+A')
settings.add_checkbutton(variable=dark_mode_state, label='Dark Mode', accelerator='Ctrl+D')
settings.add_separator()
settings.add_command(label='Check for Updates', command=partial(check_for_updates, __version__, window), accelerator='Ctrl+U')
settings.add_command(label='Version Info', command=partial(messagebox.showinfo, title='Version Info', message=f'Pit Mopper Version: {__version__}'), accelerator='Ctrl+I')
settings.add_separator()
settings.add_command(label='Delete all data', command=clear_all_data)
settings.add_command(label='Delete Debug Logs', command=clear_debug)
settings.add_command(label='Delete Highscore', command=clear_highscore)

advanced = Menu(settings, tearoff=0)
advanced.add_checkbutton(label='Console', variable=console_open, accelerator='Ctrl+F')

# Keyboard Shortcuts
window.bind_all('<Control-i>', lambda _: messagebox.showinfo(title='Version Info', message=f'Pit Mopper Version: {__version__}'))
window.bind_all('<Control-u>', lambda _: check_for_updates(__version__, window))
window.bind_all('<Control-q>', quit_app)
window.bind_all('<Control-o>', load_game)
window.bind_all('<space>', create_game)
window.bind_all('<Control-a>', lambda _: chord_state.set(not chord_state.get()))
window.bind_all('<Control-d>', lambda _: dark_mode_state.set(not dark_mode_state.get()))
window.bind_all('<Control-h>', show_highscores)
window.bind_all('<Control-x>', lambda _: console_open.set(not console_open.get()))

menubar.add_menu(menu=file_menu, title='File')
menubar.add_menu(menu=settings, title='Settings')
menubar.add_menu(menu=advanced, title='Advanced')
window.protocol('WM_DELETE_WINDOW', quit_app)

logging.info('GUI successfully created')
window.mainloop()
