"""

Shapes

1.
    * *
    * *
2. 
    *
    * * 
    *
3.
    *
    *
    *
    *
4.
    *
    *
5.
    *
    *
    * *
6.
    *
    * *
      *
"""
from config import POLE_X, POLE_Y, SHAPE_SIGN

class Shape:
    def __init__(self, array):
        self.array = array
        self.pasted = False
        self.sign = SHAPE_SIGN

    def rotate(self):
        pivot_x, pivot_y = self.array[0]
        rotated_shape = []

        for x, y in self.array:
            new_x = pivot_x + (y - pivot_y)
            new_y = pivot_y - (x - pivot_x)
            rotated_shape.append([new_x, new_y])

        if all(0 <= x < POLE_Y and 0 <= y < POLE_X for x, y in rotated_shape):
            self.array = rotated_shape

    def left(self):
        new_array = [[x, y - 1] for x, y in self.array]
        if all(0 <= x < POLE_Y and 0 <= y < POLE_X for x, y in new_array):
            self.array = new_array

    def right(self):
        new_array = [[x, y + 1] for x, y in self.array]
        if all(0 <= x < POLE_Y and 0 <= y < POLE_X for x, y in new_array):
            self.array = new_array

    def down(self):
        new_array = [[x + 1, y] for x, y in self.array]
        if all(0 <= x < POLE_Y and 0 <= y < POLE_X for x, y in new_array):
            self.array = new_array

    def inside_pole(self):
        return all(0 <= x < POLE_Y and 0 <= y < POLE_X for x, y in self.array)
