from functools import partial
import pickle
from tkinter import *
from grid import ButtonGrid, PickleButtonGrid
from squares import PickleSquare, Square
from datetime import datetime
from tkinter import filedialog, messagebox
import os
from updater import check_for_updates
from windows_tools.installed_software import get_installed_software

STRFTIME = '%A %B %m, %I:%M %p %Y %Z'
CURRENT_DIR = os.getcwd()
__version__ = '1.1.0'
HIGHSCORE_TXT = os.path.join(CURRENT_DIR, 'highscore.txt')
LOGO = "data\\images\\logo.ico"
MAX_ROWS_AND_COLS = 75
MIN_ROWS_AND_COLS = 6


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


def more_info(
    num_mines,
    mines_found,
    squares_clicked_on,
    squares_not_clicked_on,
    start,
    session_start
):
    messagebox.showinfo('Additional Information', f'''
Total Mines: {num_mines}
Mines found: {mines_found}
Squares clicked on: {len(squares_clicked_on)}
Squares not clicked on: {len(squares_not_clicked_on)}
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
    data = {
        'start': start,
        'time played': total_time,
        'grid': PickleButtonGrid.from_grid(grid),
        'zeros checked': zeros_checked,
        'num mines': num_mines,
        'chording': chording,
        'difficulty': difficulty.get()
    }
    with filedialog.asksaveasfile('wb', filetypes=(('Minesweeper Game Files', '*.min'), ('Any File', '*.*'))) as f:  # Pickling
        pickle.dump(data, f)


def load_game(_=None):
    with filedialog.askopenfile('rb', filetypes=(('Minesweeper Game Files', '*.min'), ('Any File', '*.*'))) as f:  # Un Pickling
        data = pickle.load(f)
        data: dict[str]

    game_window = Toplevel(window)
    game_window.iconbitmap(LOGO)
    game_window.title('Minesweeper')
    grid = data['grid'].grid
    button_grid = ButtonGrid(data['grid'].grid_size, game_window, grid)
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
        game_window,
        start,
        button_grid,
        zeros_checked,
        num_mines,
        chording,
        mines_found,
        additional_time=time,
    )


def game(_=None):
    global difficulty
    global window
    global chord_state

    chording = chord_state.get()

    game_window = Toplevel(window)
    game_window.iconbitmap(LOGO)
    game_window.title('Minesweeper')
    start = datetime.now()
    game_window.grid_columnconfigure(1, weight=1)

    if difficulty.get() < (7, 7):
        messagebox.showwarning(title='Size too small', message='Warning: It is rare but 6x6 and 6x7 and 7x6 games might crash or not work properly.\nIt is recommended to use 7x7 or higher')
    elif difficulty.get() >= (40, 40):
        messagebox.showwarning(title='Size too big', message='Warning: When the game is a size of 40x40 or above, the expierence might be so laggy it is unplayable.')    
    grid = ButtonGrid(difficulty.get(), game_window)
    zeros_checked = []
    num_mines = 0

    for row in grid.grid:
        for square in row:
            if square.category == 'mine':
                num_mines += 1
    mines_found = 0
    create_game(
        game_window,
        start,
        grid,
        zeros_checked,
        num_mines,
        chording,
        mines_found,
    )


def create_game(
    game_window: Toplevel,
    start: datetime,
    grid: ButtonGrid,
    zeros_checked: list[Square],
    num_mines: int,
    chording: bool,
    mines_found: int,
    additional_time: float = 0.0
):
    session_start: datetime = datetime.now()
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
    showed_game_over = False
    total_time = StringVar(game_window)

    Label(game_window, textvariable=total_time).grid(
        row=0, column=1, sticky=N+S+E+W)

    if additional_time != 0.0:
        total_time.set(f'Time: {format_second(int(additional_time))} 🚩0/{num_mines}💣')

    highscore = load_highscore(HIGHSCORE_TXT)
    seconds = additional_time

    # create a menubar
    menubar = Menu(game_window)
    game_window.config(menu=menubar)

    # create the file_menu
    file_menu = Menu(
        menubar,
        tearoff=0
    )
    file_menu.add_command(label='Save As', command=partial(save_game, start, seconds, grid, [
                          PickleSquare.from_square(square) for square in zeros_checked], num_mines, chording))
    file_menu.add_command(label='Additional Information', command=partial(
        more_info, num_mines, mines_found, squares_clicked_on, squares_not_clicked_on, start, session_start))
    file_menu.add_command(label='Exit', command=game_window.destroy)

    menubar.add_cascade(menu=file_menu, label='File')
    previous_sec = datetime.now()
    previous_sec = previous_sec.replace(microsecond=0)
    squares_flaged = []

    while showed_game_over == False:
        game_window.after(100)

        now = datetime.now()
        now = now.replace(microsecond=0)
        if now > previous_sec:
            previous_sec = now
            seconds = (now - session_start).total_seconds() + additional_time

        percent = round(((len(squares_flaged))/num_mines) * 100, 2)
        total_time.set(f'Time: {format_second(seconds)}  🚩 {len(squares_flaged)}/{num_mines} 💣 ({percent}%)')

        game_overs = [
            square.game_over
            for row in grid.grid
            for square in row
        ]

        for row in grid.grid:
            # Clicks Zeros
            for square in [square for square in row if (square.cget('text') == '0') and (square not in zeros_checked)]:
                zeros_checked.append(square)
                for square2 in [square2 for square2 in grid.around_square(*square.position) if (square2.category != 'mine')]:
                    square2.clicked()

            for square in [square for square in row if square.category == 'mine']:
                if square.category == 'mine' and square.cget('text') == '🚩':
                    mines_found += 1

            if chording:
                # Checks all square if they are completed
                for square in [square for square in row if square.completed == False]:
                    mines_around_square = [square for square in grid.around_square(
                        *square.position) if (square.category == 'mine') and (square.clicked_on == True)]
                    if (len(mines_around_square) == square.num and all(mine.category == 'mine' for mine in mines_around_square)) or square.num == None:
                        square.completed = True

                # Shows all squares around a square if it was middle clicked
                for square in [square for square in row if (square.chord)]:
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
                        for square2 in [square for square in grid.around_square(*square.position) if not square.clicked_on and square.category != 'mine']:
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

        if (len(squares_clicked_on) == (grid.grid_size[0] * grid.grid_size[1]) and all(square.category == 'mine' for square in squares_flaged)) or \
                (all(square.category == 'mine' for square in squares_not_clicked_on) and len(squares_not_clicked_on) == num_mines):
            game_over = True
            win = True
        elif True in game_overs:
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
            showed_game_over = True
        game_window.update()

    if win:
        messagebox.showinfo(
            'Game Over', f'Game Over.\nYou won!\nYou found {mines_found} out of {num_mines} mines.\nTime: {format_second(seconds)}\nHighscore: {format_second(highscore)}')
    else:
        messagebox.showinfo(
            'Game Over', f'Game Over.\nYou lost.\nYou found {mines_found} out of {num_mines} mines.\nTime: {format_second(seconds)}\nHighscore: {format_second(highscore)}')
    if win and seconds < highscore:
        with open(HIGHSCORE_TXT, 'wb') as f:
            pickle.dump(seconds, f)
    game_window.destroy()


def change_difficulty(from_spinbox:bool = False):
    global game_size
    global difficulty
    if not from_spinbox:
        difficulty.set(tuple(int(i) for i in difficulty.get().split(' ')))
    else:
        difficulty.set((rows.get(), cols.get()))
    game_size.set(f'You game size will be {difficulty.get()[0]} rows and {difficulty.get()[1]} columns')


def load_highscore(txt_file: str):
    try:
        f = open(txt_file)
        f.close()
    except FileNotFoundError:
        return float('inf')
    else:
        with open(txt_file, 'rb') as f:
            return pickle.load(f)


def zip_or_installer():
    # Checks whether the current minesweeper is from the zip download or from the installer
    # returns False if it was downloaded through the installer and True if from zip file
    return_value = True
    # print(get_installed_software())
    for app in get_installed_software():
        if 'Minesweeper' in app['name']:
            return_value = False
    return return_value


window = Tk()
window.title('Game Loader')
window.config(padx=50, pady=20)
window.iconbitmap(LOGO)
window.resizable(False, False)

Label(text='Select Difficulty').pack()

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
Label(window, text='Or you can set a custom size below.(Top one is rows and the other one is columns)')

cols = IntVar()
rows = IntVar()

Spinbox(window, from_=MIN_ROWS_AND_COLS, to=MAX_ROWS_AND_COLS, textvariable=rows, width=4, command=partial(change_difficulty, True)).pack()
Spinbox(window, from_=MIN_ROWS_AND_COLS, to=MAX_ROWS_AND_COLS, textvariable=cols, width=4, command=partial(change_difficulty, True)).pack()

chord_state = BooleanVar()

Button(window, text='Play!', command=game).pack()

# create a menubar
menubar = Menu(window)
window.config(menu=menubar)

# create the file_menu
file_menu = Menu(
    menubar,
    tearoff=0
)
file_menu.add_command(label='Open File', command=load_game, accelerator='Ctrl+O')
file_menu.add_command(label='Exit', command=window.destroy, accelerator='Ctrl+Q')

settings = Menu(menubar, tearoff=0)
settings.add_checkbutton(variable=chord_state, label='Enable Chording', accelerator='C')
settings.add_separator()
settings.add_command(label='Check for Updates', command=partial(check_for_updates, __version__, zip_or_installer(), window), accelerator='Ctrl+U')
settings.add_command(label='Version Info', command=partial(messagebox.showinfo, title='Version Info', message=f'Minesweeper Version: {__version__}'), accelerator='Ctrl+I')

# Keyboard Shortcuts
window.bind_all('<Control-i>', lambda _: partial(messagebox.showinfo, title='Version Info', message=f'Minesweeper Version: {__version__}').__call__())
window.bind_all('<Control-u>', lambda _: partial(check_for_updates, __version__, zip_or_installer(), window).__call__())
window.bind_all('<Control-q>', lambda _: window.destroy())
window.bind_all('<Control-o>', load_game)
window.bind_all('<space>', game)
window.bind_all('c', lambda _: chord_state.set(not chord_state.get()))

menubar.add_cascade(menu=file_menu, label='File')
menubar.add_cascade(menu=settings, label='Settings')

window.mainloop()
