import os
import random

from bricks import Shape
from config import POLE_X, POLE_Y, SHAPE_SIGN

class Game:
    def __init__(self):
        self.pole = [[" " for _ in range(POLE_X)] for _ in range(POLE_Y)]
        self.score = 0

    def game(self):
        shape = self.get_shape()

        while True:
            self.show_pole(shape)
            self.print_score()

            while True:
                command = input("Command [WASD]: ").upper()
                if command in "WASD":
                    break
                print("Please try again.")
            
            if command == "W":
                shape.rotate()
            elif command == "A":
                shape.left()
            elif command == "D":
                shape.right()
            else:
                shape.down()
                
                if self.check_for_down(shape):
                    self.score += 1
                    shape.pasted = True

            
            if shape.pasted == True:
                
                for i, j in shape.array:
                    self.pole[i][j] = shape.sign

                shape = self.get_shape()

                self.check_full_row()

    def check_full_row(self):
        for i in range(POLE_Y):
            if all(map(lambda cell: cell == SHAPE_SIGN, self.pole[i])):
                self.pole.pop(i)
                self.pole.insert(0, [" " for _ in range(POLE_X)])                
        

    def check_for_down(self, shape: Shape):
        for i, j in shape.array:
            if (i+1 < POLE_Y and self.pole[i+1][j] == shape.sign) or i+1 == POLE_Y - 1:
                return True
            
    def get_shape(self):
        i = 0
        j = POLE_X // 2

        square = Shape([[i, j], [i, j+1], [i+1, j], [i+1, j+1]])
        plus = Shape([[i, j], [i+1, j], [i+1, j+1], [i+2, j]])
        big_line = Shape([[i, j], [i, j+1], [i, j+2], [i, j+3]])
        half_line = Shape([[i, j], [i, j+1]])
        l_shape = Shape([[i, j], [i+1, j], [i+2, j], [i+2, j+1]])
        four_shape = Shape([[i, j], [i+1, j], [i+1, j+1], [i+2, j+1]])

        shapes = [square, plus, big_line, half_line, l_shape, four_shape]
        return random.choice(shapes)


    def show_pole(self, shape: Shape):

        os.system("clear")

        border = "_" * ((POLE_X + 1) * 2)
        print(border)
        
        for i in range(POLE_Y):
            print("|", end=" ")

            for j in range(POLE_X):
                if [i, j] in shape.array:
                    print(shape.sign, end=" ")
                else:
                    print(self.pole[i][j], end=" ")

            print("|")
        
        print(border)
    
    def print_score(self):
        print(f"\nYour score is {self.score}\n")



