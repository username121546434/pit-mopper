from tkinter import *

num_colors = {
    1:'blue',
    2:'green',
    3:'purple',
    4:'orange',
    5:'pink',
    6:'red',
    7:'yellow',
    8:'gray'
}

class Square(Button):
    def __init__(self, master: Misc | None = ..., text = '') -> None:
        self.category:str | None = None
        self.num:int | None = None
        self.game_over = False
        self.position:tuple[int, int]
        self.chord:bool = False
        self.completed:bool = False
        self.clicked_on:bool = False

        super().__init__(master, text = text)
        
        self.bind('<Button-1>', self.clicked)
        self.bind('<Button-2>', self.chord_self)
        self.bind('<Button-3>', self.flag)
    
    def flag(self, _ = ''):
        if self.cget('text').replace(' ', '') == '':
            self.config(text='🚩')
            self.clicked_on = True
        elif self.cget('text') == '🚩':
            self.config(text="  " * 3)
            self.clicked_on = False
    
    def chord_self(self, _ = ''):
        self.chord = not self.chord

    def clicked(self, _ = ''):
        if self.category == 'mine':
            self.config(text='💣', bg='red')
            self.game_over = True
        elif self.num != None:
            self.config(text=str(self.num), bg=num_colors[self.num])
        else:
            self.config(text='0')
        self.clicked_on = True