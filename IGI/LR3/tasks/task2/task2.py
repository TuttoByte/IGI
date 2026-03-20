

from .. utils import io
from .. utils import menu


def CalculateSum() -> int:
    sum = 0
    check = 0
    while True:
        inp = io.validate_user_input_int("Enter the integer: ")
        if (inp == 1):
            return sum

        check = (check + 1) % 2

        if check == 0:
            sum += inp
    



def Task2():
    print("Welcome to the programm that help you to sum every second number")
    screen = True

    while (screen):
        sum_second = CalculateSum()

        print(f"The result sum is {sum_second}")
        screen = menu.ProgramEnd()


Task2()