import os
from player import Player


class Game:
    
    def __init__(self, name1, name2):
        self.player1 = Player(name=name1, sign="X")
        self.player2 = Player(name=name2, sign="O")

        self.pole = [["*" for _ in range(3)] for _ in range(3)]

    def print_pole(self):
        
        os.system("clear")

        for i in range(3):
            print("_" * 13)
            for j in range(3):
                if j == 0:
                    print("|", end=" ")
                print(f"{self.pole[i][j]} |", end=" ")
            print()

        print("_" * 13)


    def game(self):

        player_turn = 0

        while True:

            if player_turn % 2 == 0:
                pass

            self.print_pole()
            break

