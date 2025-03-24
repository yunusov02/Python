import os
from config import POLE_X, POLE_Y
from player import Player
from sheep import Sheep



class Game:
    def __init__(self):
        self.player = Player(name="Player")
        # self.computer = Player(name="Computer")
    def game(self):

        while True:
            self.print_pole()
            break

    def print_pole(self):

        print(f"\n{self.player.name}: {self.player.score}\t\t{self.computer.name}:{self.computer.score}\n")

        for i in range(POLE_Y):
            
            for j in range(POLE_X):
                print(self.player.pole[i][j], end=" ")
            
            print("\t", end="")

            for j in range(POLE_X):
                print(self.computer.pole[i][j], end=" ")
            
            print(end="\n")
