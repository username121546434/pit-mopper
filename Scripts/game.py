from __future__ import annotations
from datetime import datetime
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any, Literal

from .game_types import GameResult
from .grid import PickleButtonGrid, ButtonGrid


if TYPE_CHECKING:
    from .squares import Square
    from tkinter import StringVar
    from .app import App


@dataclass(frozen=True, eq=True)
class OnlineGameInfo:
    """This is initially sent from the client to the server to determine what settings to use"""
    game_size: tuple[int, int]
    mine_count: int
    chording: bool


class OnlineGame:
    """Holds data for an online game, this object is constantly passed back and forth between the client and server in a multiplayer game"""
    def __init__(self, game_id, info: OnlineGameInfo) -> None:
        self.id = game_id
        self.game_info = info
        self.p1_finished: Literal[False] | datetime = False
        self.p2_finished: Literal[False] | datetime = False
        self.p1_info = {'timer text': ''}
        self.p2_info = {'timer text': ''}
        self.p1_won: bool | None = None
        self.p2_won: bool | None = None
        self.is_full = False
        self.quit = False
    
    def update_info(self, player:int, info:dict):
        if player == 1:
            self.p1_info.update(info)
        else:
            self.p2_info.update(info)
    
    def game_is_tie(self):
        return self.both_finished() and self.p1_finished == self.p2_finished and self.p1_won == self.p2_won
    
    def both_finished(self):
        return isinstance(self.p1_finished, datetime) and isinstance(self.p2_finished, datetime)
    
    def player_who_won(self):
        if self.game_is_tie():
            return 12
        elif self.both_finished() and not self.game_is_tie():
            assert isinstance(self.p1_finished, datetime) and isinstance(self.p2_finished, datetime)
            if self.p1_finished < self.p2_finished and self.p1_won:
                return 1
            elif self.p1_finished > self.p2_finished and self.p2_won:
                return 2
            else:
                return None
        elif (isinstance(self.p1_finished, datetime) and self.p1_won) or (not self.p2_won and self.p2_won is not None) or (self.p1_won):
            return 1
        elif (isinstance(self.p2_finished, datetime) and self.p2_won) or (not self.p1_won and self.p1_won is not None) or (self.p2_won):
            return 2
        else:
            return None
    
    def __repr__(self) -> str:
        items = []
        for prop, value in self.__dict__.items():
            item = "%s=%r" % (prop, value)
            items.append(item)

        return "%s(%s)" % (self.__class__.__name__, ', '.join(items))


@dataclass
class Game:
    """Holds all data for a game"""
    grid: ButtonGrid
    total_time: StringVar
    session_start: datetime = field(default_factory=datetime.now)
    zeros_checked: list[Square] = field(default_factory=list)
    num_mines: int = 0
    chording: bool = True
    mines_found: int = 0
    additional_time: float = 0.0
    squares_checked: list[Square] = field(default_factory=list)
    previous_sec: datetime = field(default_factory=datetime.now)
    with_time: bool = True
    quit: bool = False
    result: GameResult = field(default_factory=GameResult(game_over=False, seconds=0, win=False).copy)
    seconds: float = 0
    start: datetime = field(default_factory=datetime.now)


@dataclass
class PickleGame:
    """Same as `Game` but it can be pickled and has less attributes"""
    grid: PickleButtonGrid
    start: datetime
    num_mines: int
    additional_time: float = 0.0
    seconds: float = 0
    chording: bool = False
    
    @classmethod
    def from_game(cls, game: Game):
        return cls(
            grid=PickleButtonGrid.from_grid(game.grid),
            start=game.start,
            num_mines=game.num_mines,
            additional_time=game.additional_time,
            seconds=game.seconds,
            chording=game.chording
        )
    
    def to_game(self, total_time: StringVar, window: App):
        return Game(
            grid=self.grid.to_grid(window),
            start=self.start,
            total_time=total_time,
            chording=self.chording,
            additional_time=self.additional_time + self.seconds,
            num_mines=self.num_mines
        )
    
    @classmethod
    def from_dict(cls, data: dict[str, Any]):
        return cls(
            grid=data['grid'],
            start=data['start'],
            num_mines=data['num mines'],
            additional_time=data['time played'],
            chording=data['chording']
        )

