## Functions as Objects


## Functions as Objects

when we have functions we normally think like

```python
def add(a, b):
    return a + b

result = add(4, 5)

```



but when we try this command

```python
print(add)
print(type(add))
```

we will get 

```
<function add at 0x...>
<class 'function'>
```

this means functions are also just python obects

In Python everything is object

when we do like this

```python
operation = add

print(operation is add)
```

## Passing functions as arguments


```python
def add(a, b):
    return a + b


def multiply(a, b):
    return a * b


def substract(a, b):
    return a - b



def calculation(func, a, b):
    return func(a, b)


def calculation(func, a, b):
    return func(func(a, b), func(a, b))

```


## Functions returning Functions

```python
def create_multiplier(multiplier):

    def multiply(a):
        return a * multiplier

    return multiply


double = create_multiplier(2)
res = double(5)  # This will return 10


print(res)  # Output: 10
```