from time import sleep
import os
from player import Player


class Game:
    
    def __init__(self, name1, name2):
        self.player1 = Player(name=name1, sign="X")
        self.player2 = Player(name=name2, sign="O")

        self.pole = [[" " for _ in range(3)] for _ in range(3)]

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

            self.print_pole()
            print("1 2 3\n4 5 6\n7 8 9")
            print(f"{self.player1.name} turn" if player_turn % 2 == 0 else f"{self.player2.name} turn")
            
            while True:
                command = int(input("Enter pole position: "))
                
                i = (command - 1) // 3
                j = (command - 1) % 3
                if 1 <= command <= 9 and self.pole[i][j] == " ":
                    break

                print("please try again:")
            
            self.pole[i][j] = self.player1.sign if (player_turn % 2 == 0) else self.player2.sign
            player_turn += 1

            game_status = self.check_game_status()

            if game_status == "X" or game_status == "O":
                print(f"{game_status} is WIN")
                break
            elif game_status == "Tie":
                print("The game is a Tie!")
                break

    def check_game_status(self):
        # Check diagonals
        if self.pole[0][0] == self.pole[1][1] == self.pole[2][2] and self.pole[0][0] != " ":
            return self.pole[0][0]
        if self.pole[0][2] == self.pole[1][1] == self.pole[2][0] and self.pole[0][2] != " ":
            return self.pole[0][2]

        for i in range(3):
            # Check rows
            if self.pole[i][0] == self.pole[i][1] == self.pole[i][2] and self.pole[i][0] != " ":
                return self.pole[i][0]

            # Check Columns
            if self.pole[0][i] == self.pole[1][i] == self.pole[2][i] and self.pole[0][i] != " ":
                return self.pole[0][i]

            
        for row in self.pole:
            if " " in row:
                return None

        return "Tie"
        
