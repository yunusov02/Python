
class Cell:
    
    def __init__(self):
        self.__value = 0


    @property
    def value(self):
        return self.__value
    
    @value.setter
    def value(self, new_value):
        if isinstance(new_value, int):
            self.__value = new_value

    def __check_type(self, other):
        if not isinstance(other, Cell):
            raise TypeError("Type must be Cell")

    def __eq__(self, other):
        self.__check_type(other)
        return self.value == other.value
    
    def __iadd__(self, other):
        self.__check_type(other)
        self.value += other.value
        return self

