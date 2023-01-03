from __future__ import annotations
import ctypes
import os
import sys
from tkinter import messagebox
from tkinter import *
from . import constants
import traceback
import pyperclip
import logging
from .base_logger import init_logger
import webbrowser
from .enums import KBDShortcuts


def handle_exception(exc_type, exc_value, exc_traceback):
    init_logger()
    if not issubclass(exc_type, Exception): # The error is SystemExit, KeyboardInterupt...
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return
    sys.last_type = exc_type
    sys.last_value = exc_value
    sys.last_traceback = exc_traceback
    messagebox.showerror('Unknown Error', f'There has been an error, details are below\n\n{exc_value}')
    if messagebox.askyesno('Unknown Error', 'Would you like to submit a bug report?'):
        bug_report()
    logging.critical("Uncaught exception", exc_info=(exc_type, exc_value, exc_traceback))


sys.excepthook = handle_exception


def format_second(seconds: int | float):
    """
    Takes a number like 12 and formats it like it would on a clock
    
    For example, `format_second(69)` would return `1:09` and `format_second(3)` returns `0:03`
    """
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
    Adds a dark title bar to a tkinter window
    
    Apperantely, this is supposed to only work on Windows 11 but sometimes it works on Windows 10

    Taken from https://stackoverflow.com/a/70724666
    """
    if os.name == 'nt': # This is Windows specific
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


def clear_all_data():
    if messagebox.askyesno('Delete Data', 'Are you sure you want to delete all data? This includes highscores and debug logs and may break some features.'):
        logging.info('Requested to delete all data')
        constants.del_data = 'all'
        messagebox.showinfo('Delete Data', 'As soon as you close Pit Mopper, all data will be deleted')


def clear_debug():
    if messagebox.askyesno('Delete Data', 'Are you sure you want to delete the debug logs?'):
        logging.info('Requested to delete debug logs')
        constants.del_data = 'debug'
        messagebox.showinfo('Delete Data', 'As soon as you close Pit Mopper, the debug logs will be deleted')


def clear_highscore():
    if messagebox.askyesno('Delete Data', 'Are you sure you want to delete your higscores?'):
        logging.info('Requested to delete highscore data')
        constants.del_data = 'highscore'
        messagebox.showinfo('Delete Data', 'As soon as you close Pit Mopper, the your highscores will be deleted')


def clear_last_game():
    if messagebox.askyesno('Delete Data', 'Are you sure you want to delete your last game?'):
        logging.info('Requested to delete last game')
        os.remove(constants.LAST_GAME_FILE)
        messagebox.showinfo('Delete Data', 'Data has been deleted')


def bind_widget(widget: Widget, event: str|KBDShortcuts, all_:bool=False, func=None):
    """
    Set or retrieve the binding for an event on a widget
    taken from https://stackoverflow.com/a/226141/19581763
    """
    has_binding_key = hasattr(widget, 'bindings')
    if not has_binding_key:
        setattr(widget, 'bindings', dict())

    if not isinstance(event, str):
        event = event.value

    if func:
        if not all_:
            widget.bind(event, func)
        else:
            widget.bind_all(event, func)
        widget.bindings[event] = func
    else:
        return widget.bindings.get(event, None)


def bug_report():
    """Called when an unknown error occurs, and the user accepts the bug report messagebox"""
    new_window = Toplevel()
    new_window.config(padx=20, pady=20)
    func = bind_widget(new_window.master, KBDShortcuts.start_game)
    new_window.master.unbind_all(KBDShortcuts.start_game.value)

    Label(new_window, text='Enter a description of what happenned below, also include information about which platform you are on etc').pack()
    description = Text(new_window, width=1, height=1)
    description.pack(side='top',fill='both',expand=True)

    Button(new_window, text='Continue', command=lambda: make_github_issue(body=description.get('1.0', 'end'))).pack()
    new_window.master.wait_window(new_window)
    if func is not None:
        new_window.master.bind_all(KBDShortcuts.start_game.value, func)


def make_github_issue(body=None):
    with open(constants.debug_log_file, 'r') as f:
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
    webbrowser.open('https://github.com/username121546434/pit-mopper/issues/new')


def format_kbd_shortcut(shortcut: KBDShortcuts) -> str:
    """
    Takes a tkinter binding like `<Control-a>` and turns it into something like `Ctrl+A`
    """
    return shortcut.value[1:-1].lower().replace('control', 'Ctrl').replace('-', '+').title()
