from tkinter import *
from grid import ButtonGrid
import ctypes
from datetime import datetime


def Mbox(title, text, style):
    """
    Creates a message window.

    The styles are:
    0 : OK
    1 : OK | Cancel
    2 : Abort | Retry | Ignore
    3 : Yes | No | Cancel
    4 : Yes | No
    5 : Retry | Cancel 
    6 : Cancel | Try Again | Continue
    """
    return ctypes.windll.user32.MessageBoxW(0, text, title, style)


def format_second(seconds: int):
    seconds = int(seconds)
    minutes = int(seconds / 60)
    sec = seconds % 60
    if sec < 10:
        sec = f'0{sec % 60}'

    return f'{minutes}:{sec}'


def game():
    global difficulty
    global window

    game_window = Toplevel(window)
    game_window.iconbitmap("logo.ico")
    game_window.title('Minesweeper')
    total_time = StringVar(game_window)
    start = datetime.now()
    game_window.grid_columnconfigure(1, weight=1)

    Label(game_window, textvariable=total_time).grid(
        row=0, column=1, sticky=N+S+E+W)

    grid = ButtonGrid(10 * difficulty, game_window)
    showed_game_over = False
    zeros_checked = []
    num_mines = 0
    highscore_txt = 'highscore.txt'
    highscore = load_highscore(highscore_txt)

    for row in grid.grid:
        for square in row:
            if square.category == 'mine':
                num_mines += 1
    mines_found = 0

    while showed_game_over == False:
        game_window.after(100)

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

            # Checks all square if they are completed
            for square in [square for square in row if square.completed == False]:
                mines_around_square = len([square for square in grid.around_square(
                    *square.position) if (square.category == 'mine') and (square.clicked_on == True)])
                if mines_around_square == square.num or square.num == None:
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
                    for square2 in [square for square in grid.around_square(*square.position) if not square.clicked_on]:
                        square2.clicked()
                    square.chord = False

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
        Mbox(
            'Game Over', f'Game Over.\nYou won!\nYou found {mines_found} out of {num_mines} mines.\nTime: {format_second(time.total_seconds())}\nHighscore: {format_second(highscore)}', 0)
    else:
        Mbox(
            'Game Over', f'Game Over.\nYou found {mines_found} out of {num_mines} mines.\nTime: {format_second(time.total_seconds())}\nHighscore: {format_second(highscore)}', 0)
    if win and time.total_seconds() < highscore:
        with open('highscore.txt', 'w') as f:
            f.write(str(int(time.total_seconds())))
    game_window.destroy()

    window.wait_window(game_window)


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
        highscore = 0
    else:
        with open(txt_file) as f:
            highscore = int(f.read())
    finally:
        return highscore


window = Tk()
window.title('Game Loader')
window.config(padx=50, pady=20)
window.iconbitmap("logo.ico")

Label(text='Select Difficulty').pack()

# Variable to hold on to which radio button value is checked.
radio_state = IntVar()

radio_button1 = Radiobutton(
    text="Easy", value=1, variable=radio_state, command=change_difficulty)
radio_button1.pack()

radio_button2 = Radiobutton(text="Medium", value=2,
                            variable=radio_state, command=change_difficulty)
radio_button2.pack()

radio_button3 = Radiobutton(
    text='Hard', value=3, variable=radio_state, command=change_difficulty)
radio_button3.pack()

Button(window, text='Play!', command=game).pack()

window.mainloop()
