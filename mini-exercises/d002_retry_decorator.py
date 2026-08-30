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

            else:
                raise last_error

        return wrapper

    return decorator

    
attempts = 0

@retry(5)
def flaky_function():

    global attempts
    attempts += 1
    print(f"Attempt #{attempts}")

    if attempts < 3:
        raise ValueError("Still Unsuccessfull")

    return "Worked!"      

@retry(3)
def always_fails():
    raise ValueError("Never Works")



try:
    res = always_fails()
    print(res)
except Exception as e:
    print(e)

