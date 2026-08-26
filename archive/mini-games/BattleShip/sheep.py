from enum import Enum
from config import POLE_X, POLE_Y

class SheepStatus(Enum):
    FREE = 1
    PUTTED = 2
    BURNED = 3

class Sheep:
    def __init__(self, i, j, length):
        self.i = i
        self.j = j
        self.length = length
        self.sheep = [[i + x, j] for x in range(length)]
        self.status = SheepStatus.FREE

    def rotate(self):
        pivot_x, pivot_y = self.sheep[0]

        rotated_sheep = []

        for x, y in self.sheep:
            new_x = pivot_x + (y - pivot_y)
            new_y = pivot_y - (x - pivot_x)
            rotated_sheep.append([new_x, new_y])

        self.__initialize_new_coords(rotated_sheep)

    def left(self):
        new_array = [[x, y - 1] for x, y in self.sheep]
        self.__initialize_new_coords(new_array)

    def right(self):
        new_array = [[x, y + 1] for x, y in self.sheep]
        self.__initialize_new_coords(new_array)

    def down(self):
        new_array = [[x + 1, y] for x, y in self.sheep]
        self.__initialize_new_coords(new_array)

    def up(self):
        new_array = [[x - 1, y] for x, y in self.sheep]
        self.__initialize_new_coords(new_array)
        
    def __initialize_new_coords(self, new_array):
        if all(0 <= x < POLE_Y and 0 <= y < POLE_X for x, y in new_array):
            self.sheep = new_array


