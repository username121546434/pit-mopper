import ctypes
from ctypes import wintypes
import sys
from .constants import *
from .base_logger import init_logger
import logging
init_logger()


def get_console():
    global user32, kernel32, allocated_console
    user32 = ctypes.WinDLL('user32', use_last_error=True)
    kernel32 = ctypes.WinDLL('kernel32', use_last_error=True)

    kernel32.GetConsoleWindow.restype = wintypes.HWND
    user32.SendMessageW.argtypes = (wintypes.HWND, wintypes.UINT,
        wintypes.WPARAM, wintypes.LPARAM)
    user32.ShowWindow.argtypes = (wintypes.HWND, ctypes.c_int)

    allocated_console = None
    if allocated_console is None:
        # one-time set up for all instances
        allocated = bool(kernel32.AllocConsole())
        allocated_console = allocated
        if allocated:
            hwnd = kernel32.GetConsoleWindow()
            user32.ShowWindow(hwnd, SW_HIDE)

    sys.stdin = open('CONIN$', 'r')
    sys.stdout = open('CONOUT$', 'w')
    sys.stderr = open('CONOUT$', 'w', buffering=1)


def show_console():
    logging.info('Showing Console')
    logging.warning('If you close this window, the app will terminate')
    hwnd = kernel32.GetConsoleWindow()
    user32.ShowWindow(hwnd, SW_SHOW)


def hide_console():
    logging.info('Hiding Console')
    hwnd = kernel32.GetConsoleWindow()
    user32.ShowWindow(hwnd, SW_HIDE)
