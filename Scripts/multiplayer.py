from functools import partial
from tkinter.ttk import Progressbar
from .functions import _update_game

from .grid import ButtonGrid
from .updater import check_for_updates
from .network import Network
from .game import OnlineGame
from tkinter import *
from . import constants
from .functions import *
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
window.iconbitmap(constants.LOGO, constants.LOGO)

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
settings.add_command(label='Check for Updates', command=partial(check_for_updates, quit_app), accelerator='Ctrl+U')
settings.add_command(label='Version Info', command=partial(messagebox.showinfo, title='Version Info', message=f'Pit Mopper Version: {constants.VERSION}'), accelerator='Ctrl+I')
settings.add_separator()
settings.add_command(label='Delete all data', command=clear_all_data)
settings.add_command(label='Delete Debug Logs', command=clear_debug)
settings.add_command(label='Delete Highscore', command=clear_highscore)

advanced = Menu(settings, tearoff=0)
advanced.add_checkbutton(label='Console', variable=console_open, accelerator='Ctrl+X')

# Keyboard Shortcuts
bindWidget(window, '<Control-i>', True, lambda _: messagebox.showinfo(title='Version Info', message=f'Pit Mopper Version: {constants.VERSION}'))
bindWidget(window, '<Control-u>', True, lambda _: check_for_updates(quit_app))
bindWidget(window, '<Control-q>', True, quit_app)
bindWidget(window, '<Control-d>', True, lambda _: dark_mode_state.set(not dark_mode_state.get()))
bindWidget(window, '<Control-x>', True, lambda _: console_open.set(not console_open.get()))

menubar.add_menu(menu=file_menu, title='File')
menubar.add_menu(menu=settings, title='Settings')
menubar.add_menu(menu=advanced, title='Advanced')
window.protocol('WM_DELETE_WINDOW', quit_app)

label = Label(window, text='Waiting for player...')
label.pack(pady=(25, 0))

progress_bar = Progressbar(window, mode='indeterminate', length=200)
progress_bar.pack(pady=(0, 20), padx=50)

n = Network()
player = n.data
grid = None
game_window = None
connected = False

logging.info('GUI successfully created')

while True:
    game: OnlineGame = n.send_data('get')
    print(game)
    if game.available:
        label.config(text='Starting game...')
        progress_bar.pack_forget()
        connected = True
        if grid == None and game_window == None:
            game_window = Toplevel(window)
            game_window.title('Pit Mopper Multiplayer')

            self_timer = StringVar(game_window)
            Label(game_window, textvariable=self_timer).grid(row=1, column=1)

            other_timer = Label(game_window)
            other_timer.grid(row=2, column=1)

            grid = ButtonGrid((10, 10), game_window, row=3, click_random_square=True)
            result = _update_game(
                game_window,
                grid,
                datetime.now(),
                self_timer,
                [],
                grid.num_mines,
                True
            )
            while True:
                constants.after_cancel.append(game_window.after(50, do_nothing))
                result2 = result.pop('result')
                result = _update_game(**result)
                game = n.send_data('get')
                if player == 2:
                    other_timer.config(text=game.p1_info['timer text'])
                else:
                    other_timer.config(text=game.p2_info['timer text'])
                data = {'timer text': self_timer.get()}
                game = n.send_data(data)
    else:
        if connected:
            connected = False
            grid = None
            game_window.destroy()
            game_window = None
            messagebox.showerror('Connection Error', 'It seems that the other player disconected')
        else:
            progress_bar['value'] += 0.1
    window.update()
