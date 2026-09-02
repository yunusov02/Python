


class Heap:
    
    def __init__(self):
        self.heap = []
        
        
    def parent(self, i):
        return (i - 1) // 2
    
    def left(self, i):
        return 2 * i + 1
    
    def right(self, i):
        return 2 * i + 2
    
    
    def push(self, value):
        pass
    
    def remove(self, value):
        pass
    
    