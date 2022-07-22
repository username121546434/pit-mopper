from datetime import datetime


class OnlineGame:
    def __init__(self, id) -> None:
        self.id = id
        self.p2_name = ''
        self.p1_name = ''
        self.p1_finished = False
        self.p2_finished = False
        self.p1_info = {'timer text': ''}
        self.p2_info = {'timer text': ''}
        self.available = False
    
    def update_info(self, player:int, info:dict):
        if player == 1:
            self.p1_info.update(info)
        else:
            self.p2_info.update(info)
    
    def both_finished(self):
        return isinstance(self.p1_finished, datetime) and isinstance(self.p2_finished, datetime)

