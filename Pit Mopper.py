import os
from tkinter import *
from tkinter import messagebox
from Scripts.constants import VERSION, DEBUG
from Scripts.network import check_internet
import sys

__version__ = VERSION
__license__ = 'GNU GPL v3, see LICENSE.txt for more info'

if not os.path.exists(DEBUG):
    os.makedirs(DEBUG)

def run_single_player():
    window.destroy()
    import Scripts.single_player
    sys.exit()


def run_multiplayer():
    if check_internet():
        window.destroy()
        import Scripts.multiplayer
        sys.exit()
    else:
        messagebox.showerror('No Internet', 'You need internet for this')


window = Tk()
window.title('Pit Mopper')
window.iconbitmap(r'data\images\logo.ico', default=r'data\images\logo.ico')
window.config(padx=20, pady=20)

Button(window, text='Single Player', command=run_single_player).pack()
Button(window, text='Multiplayer', command=run_multiplayer).pack()

window.mainloop()