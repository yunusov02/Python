import time
import functools

def timer(func):

    @functools.wraps(func)
    def wrapper(*args, **kwargs):

        start = time.perf_counter()

        result = func(*args, **kwargs)

        worked_time = time.perf_counter() - start

        print("Function Worked:", worked_time)

        return result

    return wrapper

@timer
def long_calculation(a, b):

    """
    This function has docstring
    """
    time.sleep(2)

    return a + b


a = long_calculation(3, 4)
print(a)

print(long_calculation.__doc__)

