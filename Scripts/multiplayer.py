from functools import partial

from .grid import ButtonGrid
from .updater import check_for_updates
from .network import Network
from .game import OnlineGame
from tkinter import *
from . import constants
from .functions import *
from .constants import *
from .console_window import get_console, show_console, hide_console
get_console()
from .base_logger import init_logger
import logging
init_logger()


def console(*_):
    if not console_open.get():
        hide_console()
    else:
        show_console()


def change_theme(*_):
    constants.dark_mode = dark_mode_state.get()
    base_change_theme(window)


def quit_app():
    n.send_data('disconnect')
    base_quit_app(window)


logging.info('Loading multiplayer...')

window = Tk()
window.title('Pit Mopper Multiplayer')
window.iconbitmap(LOGO, LOGO)

console_open = BooleanVar(window, False)
console_open.trace('w', console)
dark_mode_state = BooleanVar(window)
dark_mode_state.trace('w', change_theme)

# create a menubar
menubar = CustomMenuBar(window)
menubar.place(x=0, y=0)

# create the file_menu
file_menu = Menu(
    menubar,
    tearoff=0
)
file_menu.add_command(label='Exit', command=quit_app, accelerator='Ctrl+Q')

settings = Menu(menubar, tearoff=0)
settings.add_checkbutton(variable=dark_mode_state, label='Dark Mode', accelerator='Ctrl+D')
settings.add_separator()
settings.add_command(label='Check for Updates', command=check_for_updates, accelerator='Ctrl+U')
settings.add_command(label='Version Info', command=partial(messagebox.showinfo, title='Version Info', message=f'Pit Mopper Version: {VERSION}'), accelerator='Ctrl+I')
settings.add_separator()
settings.add_command(label='Delete all data', command=clear_all_data)
settings.add_command(label='Delete Debug Logs', command=clear_debug)
settings.add_command(label='Delete Highscore', command=clear_highscore)

advanced = Menu(settings, tearoff=0)
advanced.add_checkbutton(label='Console', variable=console_open, accelerator='Ctrl+X')

# Keyboard Shortcuts
bindWidget(window, '<Control-i>', True, lambda _: messagebox.showinfo(title='Version Info', message=f'Pit Mopper Version: {VERSION}'))
bindWidget(window, '<Control-u>', True, lambda _: check_for_updates())
bindWidget(window, '<Control-q>', True, quit_app)
bindWidget(window, '<Control-d>', True, lambda _: dark_mode_state.set(not dark_mode_state.get()))
bindWidget(window, '<Control-x>', True, lambda _: console_open.set(not console_open.get()))

menubar.add_menu(menu=file_menu, title='File')
menubar.add_menu(menu=settings, title='Settings')
menubar.add_menu(menu=advanced, title='Advanced')
window.protocol('WM_DELETE_WINDOW', quit_app)

label = Label(window, text='Waiting for game...')
label.pack()

n = Network()
player = n.data
grid = None
game_window = None

logging.info('GUI successfully created')

while True:
    game: OnlineGame = n.send_data('get')
    print(game)
    if game.available:
        label.pack_forget()
        if grid == None and game_window == None:
            game_window = Toplevel(window)
            game_window.title('Pit Mopper Multiplayer')

            timer = StringVar(game_window)
            Label(game_window, textvariable=timer).grid(row=1, column=1)

            grid = ButtonGrid((10, 10), game_window, row=3, column=1, click_random_square=True)
            update_game(
                game_window,
                grid,
                datetime.now(),
                timer
            )

    window.update()
