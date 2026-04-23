from utils import io
from utils import menu
import task3.services.series as series


def Task1() -> None:
    """Main program: interactive Taylor series calculator with table output."""
    print("Welcome to the programm that help with finding the number of Taylort seriece")
    screen = True


    print("Input the float x to calculate TaylorSeries series number")
    x = io.validate_user_input_float("Enter float number: ")


    print("Input the float epsilon to calculate TaylorSeries series number")
    eps = io.validate_user_input_float("Enter float number: ")

    tseries = series.Taylor()


    ret = tseries.TaylorExp(x, eps)

    while (screen):
        print("Chose opertaion to complete")
        print("1. Get MArifmetics")
        print("2. Get Median")
        print("3. Get Mode")
        print("4. Get Dispersion")
        print("5. Get PST")
        print("6. Draw Graphics")
        print("7. Get series info")
        print("Enter anything else to exit")

        chocie = io.validate_user_input_int("Choice ")
        match chocie:
            case 1:
                print("The result is ", tseries.CalculateArifmetic())
            case 2:
                print("The result is ", tseries.CalculateMedian())
            case 3:
                print("The result is ", tseries.CalculateMode())
            case 4:
                print("The result is ", tseries.CalcualDisperison())
            case 5:
                print("The result is ", tseries.CalculatePST())      
            case 6:
                tseries.Plot()

            case 7:
                print("-----------------------------------------------------------------------")
                print(f"|{"X":>10}|{"n":>5}|{"F(x)":>20}|{"FMATH(x)":>20}|{"EPSILON":>10}|")
                print(f"|{x:>10}|{ret[0]:>5}|{ret[1]:>20}|{ret[2]:>20}|{eps:>10}|")
                print("-----------------------------------------------------------------------")

            case _:
                print("Exit")

        screen =  menu.ProgramEnd()        
                


Task1()