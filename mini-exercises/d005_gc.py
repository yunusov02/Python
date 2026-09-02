import gc

class Node:
    def __init__(self, value):
        self.value = value
        self.next = None
        
    def __del__(self):
        print(f"{self.value} is being deleted")



gc.collect()
        
a = Node("A")
b = Node("B")
c = Node("C")

a.next = b
b.next = c
c.next = a  # Create a circular reference

del a
del b


gc.collect()

# always prints empty list because the 
print(gc.garbage)

