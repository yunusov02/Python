from random import choice
from config import DEFAULT_I, DEFAULT_J

class Ball:

    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(Ball, cls).__new__(cls)
        return cls._instance

    def __init__(self, appearence, i=DEFAULT_I, j=DEFAULT_J):
        if not hasattr(self, "initialized"):

            self.appearence = appearence
            self.i = i
            self.j = j

            self.x = choice([-1, 1])
            self.y = choice([-1, 1])
            self.initialized = True
    

    def reset_position(self):
        self.i = DEFAULT_I
        self.j = DEFAULT_J

        self.x = choice([-1, 1])
        self.y = choice([-1, 1])

    def __str__(self):
        return self.appearence



# a = Ball("a")
# b = Ball("b")


# print(a)
# print(b)


