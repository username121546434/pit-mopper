from tkinter import *
from tkinter import messagebox
from Scripts.constants import VERSION
from Scripts.network import check_internet

__version__ = VERSION
__license__ = 'GNU GPL v3, see LICENSE.txt for more info'

def run_single_player():
    window.destroy()
    import Scripts.single_player


def run_multiplayer():
    if check_internet():
        window.destroy()
        import Scripts.multiplayer
    else:
        messagebox.showerror('No Internet', 'You need internet for this')


window = Tk()
window.title('Pit Mopper')
window.iconbitmap(r'data\images\logo.ico', default=r'data\images\logo.ico')
window.config(padx=20, pady=20)

Button(window, text='Single Player', command=run_single_player).pack()
Button(window, text='Multiplayer', command=run_multiplayer).pack()

window.mainloop()