"""
import asyncio

async def square(number: int) -> int:
    return number * number


async def main():
    x = await square(10)
    print(f"x={x}")

    y = await square(5)
    print(f"y={y}")

    print(f"x+y={x+y}")

if __name__ == "__main__":
    asyncio.run(main())

"""


"""
import asyncio
import time

async def call_api(message, result=1000, delay=3):
    print(message)
    await asyncio.sleep(delay)
    return result

async def main():
    start = time.perf_counter()

    price = await call_api("Get stock price of GOOG...", 300)
    print(price)

    price = await call_api("Get stock price of APPL...", 400)
    print(price)

    end = time.perf_counter()

    print(f"It took {round(end - start, 0)} second(s) to complete.")

asyncio.run(main())

"""


"""

import time
import asyncio

async def call_api(message, result=1000, delay=3):
    print(message)
    await asyncio.sleep(delay)
    return result

async def main():
    start = time.perf_counter()

    task1 = asyncio.create_task(call_api("Get stock price of GOOG...", 200))
    task2 = asyncio.create_task(call_api("Get stock price of APPL...", 300))

    price = await task1
    print(price)

    price = await task2
    print(price)

    end = time.perf_counter()
    print(f"It took {round(end - start, 0)} second's to complete.")

asyncio.run(main())

"""



"""
import asyncio
import time


async def call_api(message, result=1000, delay=3):
    print(message)
    await asyncio.sleep(delay)
    return result

async def show_message():
    for _ in range(3):
        await asyncio.sleep(1)
        print("API call in progress...")


async def main():
    start = time.perf_counter()

    message_task = asyncio.create_task(show_message())

    task1 =asyncio.create_task(call_api("Get stock price of GOOG...", 300))
    task2= asyncio.create_task(call_api("Get stock price of APPL...", 200))

    price = await task1
    print(price)

    price = await task2
    print(price)

    await message_task

    end = time.perf_counter()

    print(f'It took {round(end-start,0)} second(s) to complete.')


asyncio.run(main())
"""


import asyncio

async def call_api(message, result=1000, delay=3):
    print(message)
    await asyncio.sleep(delay)
    return result

# async def main():
#     task = asyncio.create_task(
#         call_api('Calling API...', result=2000, delay=5)
#     )

#     # if not task.done():
#     #     print("Cancelling the task...")
#     #     task.cancel()

#     # try:
#     #     res = await task
#     # except asyncio.CancelledError:
#     #     print("The task has been cancelled")

#     time_elapsed = 0
#     while not task.done():
#         time_elapsed += 1

#         await asyncio.sleep(1)

#         print("The task not completed, checking again in a second")

#         if time_elapsed == 3:
#             print("Cancelling task...")
#             task.cancel()
#             break
    
#     try:
#         res = await task
#     except asyncio.CancelledError:
#         print("The task is cancelled")


async def main():
    task = asyncio.create_task(call_api('Calling API...', result=2000, delay=5))

    MAX_TIMEOUT = 3

    try:
        res = await asyncio.wait_for(task, timeout=MAX_TIMEOUT)
        print(res)
    except asyncio.TimeoutError:
        print("The task was cancelled dut to timeout")


asyncio.run(main())


"""import asyncio


async def call_api(message, result, delay=3):
    print(message)
    await asyncio.sleep(delay)
    return result


async def main():
    a, b = await asyncio.gather(
        call_api('Calling API 1 ...', 1),
        call_api('Calling API 2 ...', 2)
    )
    print(a, b)


asyncio.run(main())"""