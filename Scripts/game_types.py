from __future__ import annotations
from typing import Callable, Literal, TypedDict
from tkinter import Variable
import sys

if sys.version_info.major == 3 and sys.version_info.minor >= 11:
    from typing import NotRequired


class GameResult(TypedDict):
    game_over: bool
    seconds: float
    win: bool



class MenubarCommand(TypedDict):
    command: NotRequired[Callable]
    accelerator: NotRequired[str]
    label: str
    variable: NotRequired[Variable]
    checkbutton: NotRequired[bool]


class MenubarSeperator(TypedDict):
    separator: Literal[True]


MenubarItem = MenubarCommand | MenubarSeperator
