"""Defines the `Square` and `PickleSquare` class"""
from tkinter import *
from .load_font import load_font
from .constants import DEFAULT_BG, DARK_MODE_BG, SQUARES_FONT
from . import functions

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
    """Holds data for a square in the game. `Square` is a subclass of the `Button` class from tkinter"""
    __slots__ = (
        'category',
        'num',
        'game_over',
        'flaged',
        'position',
        'chord',
        'completed',
        'clicked_on',
        'dark_mode',
        'last_bg',
        'last_fg',
        'tk',
        '_w',
        'widgetName',
        'bindings'
    )
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

        _, font_name = load_font(SQUARES_FONT)
        super().__init__(master, text=text, font=(font_name, 12))

        functions.bind_widget(self, '<Button-1>', func=self.clicked)
        functions.bind_widget(self, '<Button-2>', func=self.chord_self)
        functions.bind_widget(self, '<Button-3>', func=self.flag)
        functions.bind_widget(self, '<Enter>', func=self.hover_enter)
        functions.bind_widget(self, '<Leave>', func=self.hover_leave)

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
    
    def switch_theme(self, theme: bool | None = None):
        if theme is None:
            self.dark_mode = not self.dark_mode
        else:
            self.dark_mode = theme
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
        self.last_bg = self.cget('bg')
    
    def hover_enter(self, _):
        self.last_bg = self.cget('bg')
        self.last_fg = self.cget('fg')
        self.config(bg='#bdd1a9')
    
    def hover_leave(self, _):
        self.config(bg=self.last_bg, fg=self.last_fg)
        if self.flaged:
            self.flag()
            self.flag()
        elif self.clicked_on:
            self.clicked()


class PickleSquare:
    """Same as `Square` but is has less attributes and can be pickled"""
    __slots__ = ('chord', 'completed', 'clicked_on', 'category', 'position', 'game_over', 'num', 'flaged')
    def __init__(
        self,
        category: str,
        position: tuple[int, int],
        num,
        chord=False,
        completed=False,
        clicked_on=False,
        game_over=False,
        flaged:bool = False,
    ) -> None:
        self.chord: bool = chord
        self.completed: bool = completed
        self.clicked_on: bool = clicked_on
        self.category = category
        self.position = position
        self.game_over = game_over
        self.num = num
        self.flaged = flaged

    def to_square(self, master) -> Square:
        square = Square(master)
        for key in self.__slots__:
            value = getattr(self, key)
            setattr(square, key, value)
        return square

    @classmethod
    def from_square(cls, square: Square):
        new_square = cls(square.category, square.position, square.num)
        for attr in cls.__slots__:
            setattr(new_square, attr, getattr(square, attr))
        return new_square
