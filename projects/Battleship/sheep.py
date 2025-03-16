from typing import List

from config import POLE_SIZE

class Sheep:
    def __init__(self, i, j, length):
        self.burned = False
        self.i = i
        self.j = j
        self.length = length
        self.sign = "X"

    def rotate(self):
        pivot_x, pivot_y = self.sheep[0]

        new_sheep = []
        for x, y in self.sheep:
            new_x = pivot_x + (y - pivot_y)
            new_y = pivot_y - (x - pivot_x)
            
            new_sheep.append([new_x, new_y])

        if all(0 <= x < POLE_SIZE and 0 <= y < POLE_SIZE for x, y in new_sheep):
            self.sheep = new_sheep
        

        