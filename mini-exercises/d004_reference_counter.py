import sys

a = [1, 2, 3]
b = a


print(sys.getrefcount(a))
print(sys.getrefcount(b))
print()
a.append(4)

print(sys.getrefcount(a))
print(sys.getrefcount(b))
print()

b = []

print(sys.getrefcount(a))
print(sys.getrefcount(b))
print()


# In python None True False are immortal objects. They are created once and never destroyed. So their reference count is always the same.
a = None
b = None

print(sys.getrefcount(a))
print(sys.getrefcount(b))


class Dummy:
    
    # def __init__(self):
    #     self.value = 42
    pass


a = Dummy()
b = a
c = b

print(sys.getrefcount(a))
print(sys.getrefcount(b))
print(sys.getrefcount(c))


a.value = 100
print(a.value)
print(b.value)
print(c.value)


container = [a, b, c]

print(sys.getrefcount(a))
print(sys.getrefcount(b))    
print(sys.getrefcount(c))


def dummy_func(x: int):
    a.value = x
    print(sys.getrefcount(a))
    return a


dummy_func(200)
print(sys.getrefcount(a))



print("")

def show_count(obj):
    print(sys.getrefcount(obj))
    
    
show_count(a)
print(sys.getrefcount(a))


print("\n")

x = 5
print(sys.getrefcount(x))

y = 6
print(sys.getrefcount(y))

x2 = x
y2 = x2

print(sys.getrefcount(x2))
print(sys.getrefcount(y2))