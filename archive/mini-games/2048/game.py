import os
import random
from cell import Cell


class Game:    
    def __init__(self, size=4):
        self.size = size
        self.pole = [[Cell() for _ in range(size)] for _ in  range(size)]
        self.__score = 0

    def game(self):
        while self:
            free_pole_coords = self.get_free_pole()
            
            if free_pole_coords is None:
                break
            i, j = free_pole_coords

            self.pole[i][j].value = random.choice([2, 4, 8])

            self.print_pole()
            self.get_score()

            while True:
                command = input("[S] Down [W] Up\n[A] Left [D] Right\nEnter command: ").upper()
                if command in "AWSD":
                    break
                print("Please try again")

            if command == "W":
                self.up()
            elif command == "S":
                self.down()
            elif command == "A":
                self.left()
            else:
                self.right()

        print(f"Your current Score: {self.__score}")
        print("Game Over")


    def up(self):
        for j in range(self.size):
            new_col = [self.pole[i][j] for i in range(self.size) if self.pole[i][j].value != 0]

            while len(new_col) < 4:
                new_col.append(Cell())
            
            for i in range(self.size - 1):
                if new_col[i].value == new_col[i+1].value and new_col[i].value != 0:
                    new_col[i].value += new_col[i+1].value
                    self.__score += new_col[i].value
                    new_col[i+1].value = 0

            final_col = [cell for cell in new_col if cell.value != 0]
            
            while len(final_col) < self.size:
                final_col.append(Cell())

            for i in range(self.size):
                self.pole[i][j] = final_col[i]


    def down(self):
        for j in range(self.size):
            new_col = [self.pole[i][j] for i in range(self.size) if self.pole[i][j].value != 0]

            while len(new_col) < self.size:
                new_col.insert(0, Cell())

            for i in range(self.size - 1, 0, -1):
                if new_col[i].value == new_col[i - 1].value and new_col[i].value != 0:
                    new_col[i].value += new_col[i - 1].value
                    self.__score += new_col[i].value
                    new_col[i - 1].value = 0

            final_col = [cell for cell in new_col if cell.value != 0]
            while len(final_col) < self.size:
                final_col.insert(0, Cell())

            for i in range(self.size):
                self.pole[i][j] = final_col[i]

    def left(self):
        for i in range(self.size):

            new_row = [cell for cell in self.pole[i] if cell.value != 0]

            while len(new_row) < self.size:
                new_row.append(Cell())

            for j in range(self.size - 1):
                if new_row[j].value == new_row[j+1].value and new_row[j].value != 0:
                    new_row[j].value += new_row[j+1].value
                    self.__score += new_row[j].value
                    new_row[j+1].value = 0

            final_row = [cell for cell in new_row if cell.value != 0]

            while len(final_row) < self.size:
                final_row.append(Cell())
            
            self.pole[i] = final_row


    def right(self):    
        for i in range(self.size):
            new_row = [cell for cell in self.pole[i] if cell.value !=0]

            while len(new_row) < self.size:
                new_row.insert(0, Cell())

            for j in range(self.size - 1, 0, -1):
                if new_row[j].value == new_row[j-1].value and new_row[j-1].value != 0:
                    new_row[j].value += new_row[j-1].value
                    self.__score += new_row[j].value
                    new_row[j-1].value = 0

            final_row= [cell for cell in new_row if cell.value != 0]
            
            while len(final_row) < self.size:
                final_row.insert(0, Cell())

            self.pole[i] = final_row


    def print_pole(self):

        os.system("clear")

        for i in range(self.size):
            for j in range(self.size):              
                if self.pole[i][j].value:
                    print(f"{self.pole[i][j].value}\t", end=" ")
                else:
                    print(f"0\t", end=" ")
            print()

    def get_score(self):
        print("Your current Score:", self.__score)

    def __bool__(self):
        # Check can move horizontally
        for i in range(self.size):
            for j in range(self.size - 1):
                if self.pole[i][j].value == self.pole[i][j+1].value:
                    return True
                
        # Check can move vertically
        for i in range(1, self.size):
            for j in range(self.size):
                if self.pole[i][j].value == self.pole[i-1][j].value:
                    return True
        
        return False

    def get_free_pole(self):
        poles = [(i, j) for i in range(self.size) for j in range(self.size) if self.pole[i][j].value == 0]

        if len(poles) == 0:
            return None
        
        return random.choice(poles)
    
