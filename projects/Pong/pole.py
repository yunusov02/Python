from ball import Ball
from player import Player


class Pole:
    def __init__(self, player1: str, player2: str):
        self.player1 = Player(player1.title())
        self.player2 = Player(player2.title())

        self.ball = Ball("O")

        


    def game(self):
        pass


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


