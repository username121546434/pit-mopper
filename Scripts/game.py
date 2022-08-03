from datetime import datetime


class OnlineGame:
    def __init__(self, id) -> None:
        self.id = id
        self.p1_finished: bool | datetime = False
        self.p2_finished: bool | datetime = False
        self.p1_info = {'timer text': ''}
        self.p2_info = {'timer text': ''}
        self.p1_won: bool | None = None
        self.p2_won: bool | None = None
        self.available = False
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
            item = "%s = %r" % (prop, value)
            items.append(item)

        return "%s(%s)" % (self.__class__.__name__, ', '.join(items))

