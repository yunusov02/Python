import os
import random
from typing import List

from sheep import Sheep
from player import Player

def main():
    pass


# def main():
#     i = 0
#     j = 0
#     array = [["*" for _ in range(10)] for _ in range(10)]

#     while True:
#         print_pole(i, j)
#         command = input("Enter a command: ").upper()
#         if command == "A" and 1 <= j < 10:
#             j -= 1
#         elif command == "D" and 0 <= j < 9:
#             j += 1
#         elif command == "W" and 1 <= i < 10:
#             i -= 1
#         elif command == "S" and 0 <= i < 9:
#             i += 1

# def print_pole(coord_i: int, coord_j: int):
    
#     os.system("clear")

#     for i in range(10):
#         for j in range(10):
#             if coord_i == i and coord_j == j:
#                 print("X", end=" ")
#             else:
#                 print("*", end=" ")
#         print(end="\n")



if __name__ == "__main__":
    main()


