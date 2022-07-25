from tkinter import *
from .load_font import load_font
from .constants import DEFAULT_BG, DARK_MODE_BG

font_family, font_name = load_font(r"data\fonts\DSEG7ClassicMini-Bold.ttf")

num_colors = {
    1: 'blue',
    2: 'green',
    3: 'purple',
    4: 'orange',
    5: 'pink',
    6: 'red',
    7: 'yellow',
    8: 'gray',
}

dark_mode_colors = {
    1: 'DarkBlue',
    2: 'DarkGreen',
    3: 'DarkMagenta',
    4: 'DarkOrange',
    5: 'DeepPink',
    6: 'DarkRed',
    7: 'Goldenrod',
    8: 'DarkGrey'
}


class Square(Button):
    __slots__ = ('category', 'num', 'game_over', 'flaged', 'position', 'chord', 'completed', 'clicked_on', 'dark_mode')
    def __init__(self, master: Misc | None = ..., text='') -> None:
        self.category: str | None = None
        self.num: int | None = None
        self.game_over = False
        self.flaged = False
        self.position: tuple[int, int]
        self.chord: bool = False
        self.completed: bool = False
        self.clicked_on: bool = False
        self.dark_mode: bool = False

        super().__init__(master, text=text, font=(font_name, 12))

        self.bind('<Button-1>', self.clicked)
        self.bind('<Button-2>', self.chord_self)
        self.bind('<Button-3>', self.flag)

    def flag(self, _=None):
        if self.cget('text').replace(' ', '') == '':
            if self.dark_mode:
                self.config(fg='white')
            else:
                self.config(fg='black')
            self.config(text='🚩')
            self.clicked_on = True
            self.flaged = True
        elif self.cget('text') == '🚩':
            if self.dark_mode:
                self.config(fg='black')
            self.config(text="   " * 3)
            self.clicked_on = False
            self.flaged = False

    def chord_self(self, _=None):
        self.chord = not self.chord

    def clicked(self, _=None):
        if self.category == 'mine':
            self.config(text='💣', bg='red')
            self.game_over = True
        elif self.num != None:
            if self.dark_mode:
                self.config(text=str(self.num), bg=dark_mode_colors[self.num], fg=DARK_MODE_BG)
            else:
                self.config(text=str(self.num), bg=num_colors[self.num], fg='black')
        else:
            if self.dark_mode:
                self.config(bg=DARK_MODE_BG)
            else:
                self.config(bg=DEFAULT_BG)
            self.config(text='0')
        self.clicked_on = True
    
    def switch_theme(self):
        self.dark_mode = not self.dark_mode
        if not self.dark_mode:
            if self.clicked_on and self.num != None:
                self.config(bg=num_colors[self.num])
            elif self.flaged:
                self.config(fg='black', bg=DEFAULT_BG)
            else:
                self.config(bg=DEFAULT_BG)
        elif self.dark_mode:
            if self.clicked_on and self.num != None:
                self.config(bg=dark_mode_colors[self.num])
            elif self.flaged:
                self.config(fg='white', bg=DARK_MODE_BG)
            else:
                self.config(bg=DARK_MODE_BG)


class PickleSquare:
    """Same as `Square` but is used to pickle and save data"""

    def __init__(self, category: str, position: tuple[int, int], num, chord=False, completed=False, clicked_on=False, game_over=False, flaged:bool = False, dark_mode:bool = False) -> None:
        self.chord: bool = chord
        self.completed: bool = completed
        self.clicked_on: bool = clicked_on
        self.category = category
        self.position = position
        self.game_over = game_over
        self.num = num
        self.flaged = flaged
        self.dark_mode = dark_mode

    def to_square(self, master) -> Square:
        square = Square(master)
        for key, value in self.__dict__.items():
            square.__dict__[key] = value
        return square

    @classmethod
    def from_square(cls, square: Square):
        return cls(
            square.category,
            square.position,
            square.num,
            square.chord,
            square.completed,
            square.clicked_on,
            square.game_over,
            square.flaged,
            square.dark_mode
        )
