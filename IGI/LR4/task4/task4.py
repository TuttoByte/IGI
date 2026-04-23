
from utils import menu
from utils import io
import task4.services.figures as figures
import os


def cls():
    os.system('cls' if os.name=='nt' else 'clear')

def Task4():

    print("Input triangle sides and angle between them:")
    a = io.validate_user_input_float_positive("Input the A side: ")
    b = io.validate_user_input_float_positive("Input the B side: ")     
    cAngle = io.validate_user_input_angle("Input the angle between two sides: ")

    color = input("Inuput color that you want to use or proceed none: ")
       

    triangle = figures.Triangle(a, b, cAngle)
    triangle.colorInfo.color = color

    print("Triangle succesfully created")

    screen = True
    while screen:

        print("----------------------------------")
        print("Chose opertaion to complete")
        print("1. Get Area")
        print("2. Get Info")
        print("3. Draw")
        choice = io.validate_user_input_int("Input choice to procced: ")
    
        match choice:
            case 1:
                print("Area is = ", triangle.Area())
            case 2:
                print ("Infp is ", triangle.GetInfo())
            case 3:
                triangle.Draw()    
            case _:
                print("End")
    
        
        
        
        screen = menu.ProgramEnd()
        cls()




Task4()