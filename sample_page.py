# Import the function from the other file and call it
import time

from create_sample import greet

def main():
    # name = input("Enter your name: ")
    message = greet('name')
    print(message)

while True:
    main()
    time.sleep(5)

if __name__ == "__main__":
    main()
