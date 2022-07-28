from tkinter import *
from typing import Callable
from . import constants
from .custom_menubar import CustomMenuBar
from .functions import *
from .console_window import show_console, hide_console
from functools import partial
from .updater import check_for_updates
from dataclasses import dataclass


@dataclass(slots=True, frozen=True)
class MenuBarCommand:
    index: int
    menu: Menu
    label: str
    command: Callable


class App(Tk):
    def __init__(self, title: str) -> None:
        sys.excepthook = handle_exception
        self.report_callback_exception = handle_exception

        logging.info('Loading new app instance...')
        super().__init__()
        self.title(title)
        self.iconbitmap(constants.LOGO, constants.LOGO)

        self.console_open = BooleanVar(self, False)
        self.console_open.trace('w', self.console)
        self.dark_mode_state = BooleanVar(self)
        self.dark_mode_state.trace('w', self.change_theme)

        # create a menubar
        self.menubar = CustomMenuBar(self)
        self.menubar.place(x=0, y=0)

        # create the file_menu
        file_menu = Menu(
            self.menubar,
            tearoff=0
        )
        file_menu.add_command(label='Exit', command=self.quit_app, accelerator='Ctrl+Q')

        settings = Menu(self.menubar, tearoff=0)
        settings.add_checkbutton(variable=self.dark_mode_state, label='Dark Mode', accelerator='Ctrl+D')
        settings.add_separator()
        settings.add_command(label='Check for Updates', command=partial(check_for_updates, self.quit_app), accelerator='Ctrl+U')
        settings.add_command(label='Version Info', command=partial(messagebox.showinfo, title='Version Info', message=f'Pit Mopper Version: {constants.VERSION}'), accelerator='Ctrl+I')
        settings.add_separator()
        settings.add_command(label='Delete all data', command=clear_all_data)
        settings.add_command(label='Delete Debug Logs', command=clear_debug)
        settings.add_command(label='Delete Highscore', command=clear_highscore)

        advanced = Menu(settings, tearoff=0)
        advanced.add_checkbutton(label='Console', variable=self.console_open, accelerator='Ctrl+X')

        # Keyboard Shortcuts
        bindWidget(self, '<Control-i>', True, lambda _: messagebox.showinfo(title='Version Info', message=f'Pit Mopper Version: {constants.VERSION}'))
        bindWidget(self, '<Control-u>', True, lambda _: check_for_updates(self.quit_app))
        bindWidget(self, '<Control-q>', True, self.quit_app)
        bindWidget(self, '<Control-d>', True, lambda _: self.dark_mode_state.set(not self.dark_mode_state.get()))
        bindWidget(self, '<Control-x>', True, lambda _: self.console_open.set(not self.console_open.get()))

        self.menubar.add_menu(menu=file_menu, title='File')
        self.menubar.add_menu(menu=settings, title='Settings')
        self.menubar.add_menu(menu=advanced, title='Advanced')
        self.protocol('WM_DELETE_WINDOW', self.quit_app)
    
    def quit_app(self):
        base_quit_app(self)

    def console(self, *_):
        if not self.console_open.get():
            hide_console()
        else:
            show_console()

    def change_theme(self, *_):
        constants.dark_mode = self.dark_mode_state.get()
        base_change_theme(self)
