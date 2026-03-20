from .. utils import io
from .. utils import menu
import math



def get_sublist(lst: list) -> list:
    first = - 1
    second = -1


    for i in range(len(lst)):
        if (lst[i] > 0 and first == -1):
            first = i 
    
        if (lst[i] >0 ):
            second = i


    if (first == second == -1):
        return []

    return lst[first:second + 1]     


def Task5():
    print("Welcome to the programm that help you to find sum and minimum")
    screen = True

    while (screen):
        print("Enter float list to procced\n")
        lst = io.valifate_user_float_list_input()

        working_list = get_sublist(lst)

        list_sum = sum(working_list)
        list_minimum = min(list(map(math.fabs, working_list)))


        print(f"The inputed array {lst}") 
        print(f"The proceeded array {working_list}")
        print(f"Sum: {list_sum}")
        print(f"FABS Minimum: {list_minimum}") 

        screen = menu.ProgramEnd()



Task5()