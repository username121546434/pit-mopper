from functools import partial
import pickle
from tkinter import *
from grid import ButtonGrid, PickleButtonGrid
from squares import PickleSquare, Square
import ctypes
from datetime import datetime, timedelta
from tkinter import filedialog, messagebox

STRFTIME = '%A %B %m, %I:%M %p %Y %Z'


def format_second(seconds: int):
    seconds = int(seconds)
    minutes = int(seconds / 60)
    sec = seconds % 60
    if sec < 10:
        sec = f'0{sec % 60}'

    return f'{minutes}:{sec}'


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
        'time played': total_time.total_seconds(),
        'grid': PickleButtonGrid.from_grid(grid),
        'zeros checked': zeros_checked,
        'num mines': num_mines,
        'chording': chording,
        'difficulty': difficulty
    }
    with filedialog.asksaveasfile('wb', filetypes=(('Minesweeper Game Files', '*.min'), ('Any File', '*.*'))) as f:  # Pickling
        pickle.dump(data, f)


def load_game():
    with filedialog.askopenfile('rb', filetypes=(('Minesweeper Game Files', '*.min'), ('Any File', '*.*'))) as f:  # Un Pickling
        data = pickle.load(f)
        data: dict[str]

    game_window = Toplevel(window)
    game_window.iconbitmap("logo.ico")
    game_window.title('Minesweeper')
    grid = data['grid'].to_grid(game_window)
    session_start = datetime.now()
    start: datetime = data['start']
    time: timedelta = data['time played']
    num_mines: int = data['num mines']
    zeros_checked = data['zeros checked']
    chording = data['chording']
    game_window.grid_columnconfigure(1, weight=1)
    #print(grid.grid)

    mines_found = 0
    for row in grid.grid:
        for square in row:
            if square.category == 'mine' and square.cget('text') == '🚩':
                mines_found += 1
    
    create_game(
        game_window,
        start,
        grid,
        zeros_checked,
        num_mines,
        chording,
        mines_found,
        session_start,
        time
    )


def game():
    global difficulty
    global window
    global check_state

    chording = check_state.get()

    game_window = Toplevel(window)
    game_window.iconbitmap("logo.ico")
    game_window.title('Minesweeper')
    start = datetime.now()
    game_window.grid_columnconfigure(1, weight=1)

    grid = ButtonGrid(10 * difficulty, game_window)
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
    session_start: datetime = datetime(1,1,1),
    current_time: int | float | datetime = datetime(1,1,1)
):
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
    
    if current_time != datetime(1,1,1):
        total_time.set(f'Time: {format_second(int(current_time))}')

    highscore_txt = 'highscore.txt'
    highscore = load_highscore(highscore_txt)
    time = datetime.now() - session_start

    # create a menubar
    menubar = Menu(game_window)
    game_window.config(menu=menubar)

    # create the file_menu
    file_menu = Menu(
        menubar,
        tearoff=0
    )
    file_menu.add_command(label='Save As', command=partial(save_game, start, time, grid, [
                          PickleSquare.from_square(square) for square in zeros_checked], num_mines, chording))
    file_menu.add_command(label='Additional Information', command=partial(
        more_info, num_mines, mines_found, squares_clicked_on, squares_not_clicked_on, start, session_start))
    file_menu.add_command(label='Exit', command=game_window.destroy)

    menubar.add_cascade(menu=file_menu, label='File')

    while showed_game_over == False:
        game_window.after(100)

        if session_start != datetime(1,1,1):
            now = datetime.now()
            time = now - session_start + timedelta(seconds=current_time)
        else:
            now = datetime.now()
            time = now - start

        total_time.set(f'Time: {format_second(time.total_seconds())}')

        game_overs = [
            square.game_over
            for row in grid.grid
            for square in row
        ]

        for row in grid.grid:
            # Clicks Zeros
            for square in [square for square in row if (square.cget('text') == '0') and (square not in zeros_checked)]:
                zeros_checked.append(square)
                for square2 in [square2 for square2 in grid.around_square(*square.position) if (square2.category != 'mine') and (square2.num == None)]:
                    square2.clicked()
                    # Clicks all numbers next to clicked zeros
                    for square3 in [square3 for square3 in grid.around_square(*square2.position) if square3 in zeros_checked or square3.num != None]:
                        square3.clicked()

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

        if len(squares_clicked_on) == grid.grid_size ** 2 or all(square.category == 'bomb' for square in squares_not_clicked_on):
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
            'Game Over', f'Game Over.\nYou won!\nYou found {mines_found} out of {num_mines} mines.\nTime: {format_second(time.total_seconds())}\nHighscore: {format_second(highscore)}')
    else:
        messagebox.showinfo(
            'Game Over', f'Game Over.\nYou found {mines_found} out of {num_mines} mines.\nTime: {format_second(time.total_seconds())}\nHighscore: {format_second(highscore)}')
    if win and time.total_seconds() < highscore:
        with open('highscore.txt', 'w') as f:
            f.write(str(int(time.total_seconds())))
    game_window.destroy()


def change_difficulty():
    global difficulty
    difficulty = radio_state.get()


def load_highscore(txt_file: str):
    try:
        f = open(txt_file)
    except FileNotFoundError:
        f = open(txt_file, 'w')
        f.write('0')
        f.close()
        highscore = float('inf')
    else:
        with open(txt_file) as f:
            highscore = int(f.read())
    finally:
        return highscore


window = Tk()
window.title('Game Loader')
window.config(padx=50, pady=20)
window.iconbitmap("logo.ico")
window.resizable(False, False)

Label(text='Select Difficulty').pack()

# Variable to hold on to which radio button value is checked.
radio_state = IntVar()

radio_button1 = Radiobutton(
    text="Easy", value=1, variable=radio_state, command=change_difficulty)
radio_button1.pack()

radio_button2 = Radiobutton(
    text="Medium", value=2, variable=radio_state, command=change_difficulty)
radio_button2.pack()

radio_button3 = Radiobutton(
    text='Hard', value=3, variable=radio_state, command=change_difficulty)
radio_button3.pack()

check_state = BooleanVar()

Button(window, text='Play!', command=game).pack()

# create a menubar
menubar = Menu(window)
window.config(menu=menubar)

# create the file_menu
file_menu = Menu(
    menubar,
    tearoff=0
)
file_menu.add_command(label='Open File', command=load_game)
file_menu.add_command(label='Exit', command=window.destroy)

settings = Menu(file_menu)
settings.add_checkbutton(variable=check_state, label='Enable Chording')


menubar.add_cascade(menu=file_menu, label='File')
menubar.add_cascade(menu=settings, label='Settings')

window.mainloop()
