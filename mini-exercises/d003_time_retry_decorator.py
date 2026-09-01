import time
import functools


def retry(times=3):

    def decorator(func):

        @functools.wraps(func)
        def wrapper(*args, **kwargs):

            last_error = None

            for i in range(times):

                try:
                    res = func(*args, **kwargs)
                    return res
                except Exception as e:
                    last_error = e

        
            raise last_error


        return wrapper

    return decorator


def timer(func):

    @functools.wraps(func)
    def wrapper(*args, **kwargs):

        start = time.perf_counter()

        res = func(*args, **kwargs)

        end = time.perf_counter()

        print(f"{func.__name__} function worked {end - start}s")

        return res

    return wrapper




attempts = 0

@timer
@retry(6)
def flaky_function():

    time.sleep(1)

    global attempts
    attempts += 1
    print(f"Attempt #{attempts}")

    if attempts < 3:
        raise ValueError("Still Unsuccessfull")

    return "Worked!"      



print(flaky_function())
