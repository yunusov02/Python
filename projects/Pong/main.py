from pole import Pole

def main():
    print("Welcome to Ping Pong Game")

    player1 = input("Enter first player name: ")
    player2 = input("Enter second player name: ")

    pole = Pole(player1, player2)

    pole.game()

    pole.print_winner()

    print("Game End")



if __name__ == "__main__":
    main()