from . import network
from .game import OnlineGame
from tkinter import *
from .constants import *
from .console_window import get_console, show_console, hide_console
get_console()
from .base_logger import init_logger
init_logger()

window = Tk()
window.title('Pit Mopper Multiplayer')
window.iconbitmap()
