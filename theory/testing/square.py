
class Square:
    def __init__(self, length):
        if type(length) not in [int, float]:
            raise TypeError("Length must be an integer or float")

        if length <= 0:
            raise ValueError("Length must be greater than zero")

        self.length = length
    
    def area(self):
        return self.length ** 2

