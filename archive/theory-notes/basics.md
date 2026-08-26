# Bacis

- Fundamentals
- Operators
- Control Flow
- Functions
- Lists
- Dictionaries
- Sets
- Exception Handling
- More on Python Loops
- More on Python functions
- Modules & Packages
- Working with files
- Working with Directories
- Third-party Packages, PIP and Virtual Environments
- Strings

## Syntax

```python
def main():
    i = 1
    max = 10

    while i < max:
        print(i)
        i += 1

main()
```

## Comments

```python
# This is comment

# One-line docstrings
def quicksort():
    """
        Sort the list using quickSort algorithm
    """
```

## Ternary Operation

```python
age = int(input("Enter your age: "))
ticket_price = 20 if age >= 18 else 5
print(f"The Ticket price is {ticket_price}")

```

## Python Rnage

```python
for index in range(1, 5):
    print(index)

# range(start, stop, step)
```

## Python Functions

### defining Python Functions

```python
def greet():
    """Display a greeting to users"""
    print("HI")

def greet(name):
    return f"Hi {name}"

greeting = greet("John")
print(greeting)

def greet(name='there', message='Hi'):
    return f"{message} {name}"

def get_net_price(price, tax=0.07, discount=0.05):
    return price * (1 + tax - discount)

```

### Python lambda expression

```python
lambda parameters: expression

def get_full_name(first_name, last_name):
    return f"{first_name} {last_name}"

lambda_get_full_name = lambda first_name, last_name: f"{first_name} {last_name}"

```


## Python Lists

```python
numbers = [1, 2, 3, 4, 5]

# del numbers[0]
# last_element = numbers.pop() remove last element from an array
# append() to add a new element to the end of a list
# insert() to add a new at a position in a list
# pop() to remove an element from a list and return that element
# remove() to remove an element from a list
```

```python

guests = ['James', 'Mary', 'John', 'Patricia', 'Robert', 'Jennifer']
guests.sort()

print(guests)

guests = ['James', 'Mary', 'John', 'Patricia', 'Robert', 'Jennifer']
guests.sort(reverse=True)

print(guests)

```


```python
companies = [
    ("Google", 2019, 134.81),
    ("Apple", 2019, 260.2),
    ("Facebook", 2019, 70.7)
]

companies.sort(key=lambda companies: companies[2], reverse=True)

```

```python
guests = ['James', 'Mary', 'John', 'Patricia', 'Robert', 'Jennifer']
sorted_guests = sorted(guests)

print(guests)
print(sorted_guests)
```

```python
cities = ['New York', 'Beijing', 'Cairo', 'Mumbai', 'Mexico']

result = cities.index('Mumbai')
print(result)

```

## map()
```python
iterator = map(fn, list)

bonuses = [100, 200, 300]
iterator = map(lambda bonus: bonus * 1.3, bonuses)
```

## filter()
```python
iterator = map(fn, list)

bonuses = [100, 200, 300]
iterator = map(lambda bonus: bonus * 1.3, bonuses)
filter_iterator = filter(lambda bonus: bonus > 250, map(lambda bonus: bonus* 1.3, bonuses))
```

## reduce()
```python
from functools import reduce

scores = [75, 65, 80, 95, 50]

total = reduce(lambda a, b: a + b, scores)

print(total) # sum of all scores
```

## list comprehension
```python
numbers = [1, 2, 3, 4, 5]
squares = [number**2 for number in numbers]

print(squares)
```


## Python Tuples
```python
rgb = ("red", "green", "blue")

# don't use like these
"""
rgb[0] = "orange"
"""
```
## Python Dictionaries

```python
# {key:value for (key,value) in dict.items() if condition}

stocks = {
    'AAPL': 121,
    'AMZN': 3380,
    'MSFT': 219,
    'BIIB': 280,
    'QDEL': 266,
    'LVGO': 144
}

new_stocks = {symbol: price * 1.02 for (symbol, price) in stocks.items()}

print(new_stocks)

```

## Python Sets

```python
empty_set = set()

```

## Python Exception Handling

```python
try:
    # get input net sales
    print('Enter the net sales for')

    previous = float(input('- Prior period:'))
    current = float(input('- Current period:'))

    # calculate the change in percentage
    change = (current - previous) * 100 / previous

    # show the result
    if change > 0:
        result = f'Sales increase {abs(change)}%'
    else:
        result = f'Sales decrease {abs(change)}%'

    print(result)
except ValueError:
    print('Error! Please enter a number for net sales.')
except ZeroDivisionError:
    print('Error! The prior net sales cannot be zero.')
except Exception as error:
    print(error)
```

## Python Partial Functions

```python
from functools import partial

def multiply(a, b):
    return a*b


double = partial(multiply, b=2)

result = double(10)
print(result)

```

## Python Type hunting

| Type Alias | Built-in Types |
| ------    |   ----    |
| List      | list      |
| Tuple     | tuple     |
| Dict      | dict      |
| Set       | set       |
| Frozenset | frozenset |