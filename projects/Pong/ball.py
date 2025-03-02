from config import DEFAULT_I, DEFAULT_J

class Ball:

    def __init__(self, appearence, i, j):
        self.appearence = appearence
        self.i = i
        self.j = j
    

    def reset_position(self):
        self.i = DEFAULT_I
        self.j = DEFAULT_J

