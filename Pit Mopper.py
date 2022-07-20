from tkinter import *


def run_single_player():
    window.destroy()
    import Scripts.single_player


def run_multiplayer():
    window.destroy()
    import Scripts.multiplayer


window = Tk()
window.title('Pit Mopper')
window.iconbitmap(r'data\images\logo.ico', default=r'data\images\logo.ico')
window.config(padx=20, pady=20)

Button(window, text='Single Player', command=run_single_player).pack()
Button(window, text='Multilayer', command=run_multiplayer).pack()

window.mainloop()