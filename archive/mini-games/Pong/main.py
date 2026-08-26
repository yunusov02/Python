from game import Game

def main():
    print("Welcome to Ping Pong Game")

    player1 = input("Enter first player name: ")
    player2 = input("Enter second player name: ")

    game = Game(player1, player2)

    game.game()

    game.print_winner()

    print("Game End")



if __name__ == "__main__":
    main()
