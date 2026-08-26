import os
from ball import Ball
from player import Player
from config import POLE_I, POLE_J, PLAYER_1_I, PLAYER_1_J, PLAYER_2_I, PLAYER_2_J



class Game:

    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(Game, cls).__new__(cls)
        return cls._instance


    def __init__(self, player1: str, player2: str):
        self.player1 = Player(player1.title(), i=PLAYER_1_I, j=PLAYER_1_J)
        self.player2 = Player(player2.title(), i=PLAYER_2_I, j=PLAYER_2_J)

        self.ball = Ball("O")

        self.pole = [[" " for _ in range(POLE_J)] for _ in range(POLE_I)]


    def game(self):
        while self.check_winner():
            os.system("clear")
            self.print_players_informations()
            self.print_pole()
            print("Up: A      Up: K\nDown: Z    Down: M\nQuit: Q\n")
            command = input("Enter a command: ")

            if command == " ":
                goal = self.move_ball()
                if goal == 1:
                    self.ball.reset_position()

            elif command in "akzm":
                self.move_player(command)
            elif command == "q":
                break

    def move_ball(self):

        if self.ball.j in [0, 79]:
            if self.ball.j == 0:
                self.player2.score += 1
            elif self.ball.j == 79:
                self.player1.score += 1
            return 1

        if self.ball.i == POLE_I - 1 or self.ball.i == 0:
            self.ball.x *= -1

        if (0 < abs(self.ball.i - self.player1.i) < 3 and abs(self.ball.j - PLAYER_1_J) == 1) or \
           (0 < abs(self.ball.i - self.player2.i) < 3 and abs(self.ball.j - PLAYER_2_J) == 1):
            self.ball.y *= -1

        self.ball.i += self.ball.x
        self.ball.j += self.ball.y

        return 0


    def move_player(self, command):
        if command == "a" and self.player1.i - 1 >= 0:
            self.player1.i -= 1
        elif command == "z" and self.player1.i + 3 < POLE_I:
            self.player1.i += 1
        elif command == "k" and self.player2.i - 1 >= 0:
            self.player2.i -= 1
        elif command == "m" and self.player2.i + 3 < POLE_I:
            self.player2.i += 1


    def print_pole(self):
        print("-" * (POLE_J * 2 - 1))

        for i in range(POLE_I):
            for j in range(POLE_J):
                if i == self.ball.i and j == self.ball.j:
                    print(self.ball.appearence, end=" ") # Print ball coords

                elif (0 <= i - self.player1.i < 3 and j == self.player1.j) or \
                        (0 <= i - self.player2.i < 3 and j == self.player2.j):
                    print("X", end=" ") # Print players Coords
    
                elif j == POLE_J // 2 or j == 0 or j == POLE_J - 1:
                    print("|", end=" ") # Print start and end of pole
                else:
                    print(self.pole[i][j], end=" ")
            print()

        print("-" * (POLE_J *2 - 1))


    def check_winner(self):
        return self.player1.score < 3 and self.player2.score < 3


    def print_players_informations(self):
        print(self.player1.name, ":", self.player1.score)
        print(self.player2.name, ":", self.player2.score)
        

    def get_winner_player_name(self) -> str:
        if (self.player1.score > self.player2.score):
            return self.player1.name
        elif (self.player1.score == self.player1.score):
            return None
        return self.player2.name
    

    def print_winner(self) -> str:
        winner_player = self.get_winner_player_name()

        if winner_player is None:
            print("It is a DRAW")
        else:
            print(f"Player {winner_player.title()} is WIN")

