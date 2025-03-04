from player import Player
from game import Game


def main():
    name1 = "Player1"
    name2 = "Player2"

    game = Game(name1=name1, name2=name2)

    game.print_pole()


if __name__ == "__main__":
    main()

