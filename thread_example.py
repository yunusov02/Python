from threading import Thread
from time import sleep, perf_counter



def replace(filename, substr, new_substr):
    print(f"Processing the file {filename}")

    with open(filename, "r") as f:
        content = f.read()
    
    content = content.replace(substr, new_substr)

    with open(filename, "w") as f:
        f.write(content)



def main():

    filenames = []

    for i in range(1, 11):
        filename = f"filenames/test{i}.txt"
        filenames.append(filename)
    
    threads = [Thread(target=replace, args=(filename, "id", "ids")) for filename in filenames]

    for thread in threads:
        thread.start()

    for thread in threads:
        thread.join()


if __name__ == "__main__":
    start_time = perf_counter()

    main()

    end_time = perf_counter()
    print(f'It took {end_time- start_time :0.2f} second(s) to complete.')

