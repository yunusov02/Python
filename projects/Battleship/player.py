import os
from typing import List

from config import POLE_SIZE
from sheep import Sheep


class Player:
    def __init__(self):
        i, j = 0, 0

        self.sheeps = [
            Sheep(i, j)
        ]



