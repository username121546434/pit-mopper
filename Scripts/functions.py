import ctypes
import shutil
import sys
from tkinter import messagebox
from tkinter import *

from . import constants
from .squares import Square
from .custom_menubar import CustomMenuBar
from .network import check_internet
from .constants import *
import traceback
import pyperclip
import logging
from .base_logger import init_logger
import webbrowser


def handle_exception(exc_type, exc_value, exc_traceback):
    init_logger()
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


def base_change_theme(window: Tk):
    if constants.dark_mode:
        logging.info('User switched theme to dark mode')
        CURRENT_BG = DARK_MODE_BG
        CURRENT_FG = DARK_MODE_FG
        constants.CURRENT_BG = DARK_MODE_BG
        constants.CURRENT_FG = DARK_MODE_FG
        dark_title_bar(window)
    else:
        logging.info('User switched theme to light mode')
        CURRENT_BG = DEFAULT_BG
        CURRENT_FG = DEFAULT_FG
        constants.CURRENT_BG = DEFAULT_BG
        constants.CURRENT_FG = DEFAULT_FG
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


def do_nothing():
    pass


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


def base_quit_app(window: Tk):
    global APP_CLOSED
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


def bindWidget(widget: Widget, event, all:bool=False, func=None):
    # https://stackoverflow.com/a/226141/19581763
    '''Set or retrieve the binding for an event on a widget'''
    try:
        _ = widget.__dict__['bindings']
    except KeyError:
        has_binding_key = False
    else:
        has_binding_key = True
    if not has_binding_key:
        setattr(widget, 'bindings', dict())

    if func:
        if not all:
            widget.bind(event, func)
        else:
            widget.bind_all(event, func)
        widget.bindings[event] = func
    else:
        return(widget.bindings.setdefault(event, None))


def bug_report():
    new_window = Toplevel()
    new_window.config(padx=20, pady=20)
    func = bindWidget(new_window.master, '<space>')
    new_window.master.unbind_all('<space>')

    Label(new_window, text='Enter a description of what happenned below, also include information about which platform you are on etc').pack()
    description = Text(new_window, width=1, height=1)
    description.pack(side='top',fill='both',expand=True)

    Button(new_window, text='Continue', command=lambda: make_github_issue(body=description.get('1.0', 'end'))).pack()
    new_window.master.wait_window(new_window)
    if not APP_CLOSED:
        new_window.master.bind_all('<space>', func)


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