from config import PLAYER_I, PLAYER_J

class Player:
    def __init__(self, name, i=PLAYER_I, j=PLAYER_J, score = 0):
        self.name = name
        self.score = score
        self.i = i
        self.j = j

    def increase_score(self, value: int) -> None:
        self.score += value

