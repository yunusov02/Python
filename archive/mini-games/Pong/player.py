class Player:
    def __init__(self, name, i=0, j=0, score = 0):
        self.name = name
        self.score = score
        self.i = i
        self.j = j

    def increase_score(self, value = 1) -> None:
        self.score += value

