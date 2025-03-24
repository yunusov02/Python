import os
import time

from sheep import Sheep, SheepStatus
from config import POLE_X, POLE_Y

class Player:
    def __init__(self, name="Player 1"):
        self.name = name
        self.score = 0
        self.pole = [["*" for _ in range(POLE_X)] for _ in range(POLE_Y)]
        self.selected: Sheep | None = None
        
        self.initialize_sheeps()
        self.placing_sheeps()

    def placing_sheeps(self):
        
        os.system("clear")
        print("Let's place sheeps on the right coords...")

        while any(sheep.status == SheepStatus.FREE for sheep in self.sheeps):
            self.selected = self.select_sheep()

            while self.selected.status != SheepStatus.PUTTED:
                self.sheeps_on_pole()
                command = input("[A][W][D][S] - Directions\n[P] putt it\n[R] rotate\n\t: ").upper()

                if command == "A":
                    self.selected.left()
                elif command == "D":
                    self.selected.right()
                elif command == "W":
                    self.selected.up()
                elif command == "S":
                    self.selected.down()
                elif command == "R":
                    self.selected.rotate()
                elif command == "P":
                    for x, y in self.selected.sheep:
                        self.pole[x][y] = "#"
                    
                    sheep_base = self.selected.sheep[0]
                    length = self.selected.length
                    
                    start_x, start_y = sheep_base[0] - 1, sheep_base[1] - 1
                    stop_x, stop_y = sheep_base[0] + length, sheep_base[1] + length

                    for x in range(start_x, stop_x+1):
                        for y in range(start_y, stop_y+1):
                            if 0 <= x < POLE_Y and 0 <= y < POLE_X and self.pole[x][y] != "#":
                                self.pole[x][y] = "."

                    self.selected.status = SheepStatus.PUTTED
                    time.sleep(2)

      
    def initialize_sheeps(self):
        self.sheeps = []
        j = 0

        for length, count in [[4, 1], [3, 2], [2, 3], [1, 4]]:
            self.sheeps.extend(Sheep(0, j + k, length) for k in range(count))
            j += count


    def select_sheep(self):
        print("Sheeps:")
        for i in range(len(self.sheeps)):
            if self.sheeps[i].status == SheepStatus.FREE:
                print(f"{i+1}.\t {"# " * self.sheeps[i].length}")
        
        index = int(input("Select a sheep number: "))

        # if self.sheeps[index - 1].status == SheepStatus.PUTTED:
        #     self.select_sheep()
        
        return self.sheeps.pop(index - 1)


    def sheeps_on_pole(self):
        os.system("clear")
        for i in range(POLE_Y):
            for j in range(POLE_X):
                if self.selected is not None and [i, j] in self.selected.sheep:
                    print("#", end=" ")
                else:
                    print(self.pole[i][j], end=" ")
            print("\n")   


a = Player()