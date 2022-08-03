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


class App(Tk):
    def __init__(self, title: str) -> None:
        logging.info('Loading new app instance...')
        super().__init__()
        sys.excepthook = handle_exception
        self.report_callback_exception = handle_exception

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

        # Keyboard Shortcuts
        bindWidget(self, '<Control-i>', True, lambda _: messagebox.showinfo(title='Version Info', message=f'Pit Mopper Version: {constants.VERSION}'))
        bindWidget(self, '<Control-u>', True, lambda _: check_for_updates(self.quit_app))
        bindWidget(self, '<Control-q>', True, self.quit_app)
        bindWidget(self, '<Control-d>', True, lambda _: self.dark_mode_state.set(not self.dark_mode_state.get()))
        bindWidget(self, '<Control-x>', True, lambda _: self.console_open.set(not self.console_open.get()))

        self.menubar.add_menu(menu=self.file_menu, title='File')
        self.menubar.add_menu(menu=self.settings, title='Settings')
        self.menubar.add_menu(menu=self.advanced, title='Advanced')
        self.protocol('WM_DELETE_WINDOW', self.quit_app)
    
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
            if not isinstance(child, Toplevel) and not isinstance(child, Spinbox) and not isinstance(child, CustomMenuBar) and not isinstance(child, Progressbar):
                child.config(bg=CURRENT_BG, fg=CURRENT_FG)
            elif isinstance(child, CustomMenuBar):
                child.change_bg_fg(bg=CURRENT_BG, fg=CURRENT_FG)
            elif isinstance(child, Spinbox):
                if CURRENT_BG == constants.DEFAULT_BG:
                    child.config(bg='white', fg=CURRENT_FG)
                else:
                    child.config(bg=CURRENT_BG, fg=CURRENT_FG)
            elif isinstance(child, Toplevel):
                if CURRENT_BG == constants.DARK_MODE_BG:
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

