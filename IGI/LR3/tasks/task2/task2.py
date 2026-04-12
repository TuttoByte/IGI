

from .. utils import io
from .. utils import menu


def CalculateSum() -> int:
    """
    Sums every second input number (alternating addition).
    Stops when user enters 1. Ignores numbers on odd turns.
    
    Returns:
        int: sum of selected numbers
    """
    sum = 0
    check = 0
    while True:
        inp = io.validate_user_input_int("Enter the integer: ")
        if (inp == 1):
            return sum

        check = (check + 1) % 2

        if check == 0:
            sum += inp
    



def Task2()->None:
    """Main program: interactive sum calculator for every second number."""
    print("Welcome to the programm that help you to sum every second number")
    screen = True

    while (screen):
        sum_second = CalculateSum()

        print(f"The result sum is {sum_second}")
        screen = menu.ProgramEnd()


Task2()