from .. utils import io
from .. utils import menu
import math



def get_sublist(lst: list) -> list:
    """
    Extracts sublist from first positive number to last positive number.
    
    Args:
        lst (list): input list of floats
        
    Returns:
        list: sublist between first and last positive elements (empty if no positives)
    """
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


def Task5() ->None:
    """Main program: finds sum and absolute minimum of positive sublist."""
    print("Welcome to the programm that help you to find sum and minimum")
    screen = True

    while (screen):

        if(io.get_yes_or_no("Would You Like to Generate List? (y/n)")):
                lst_size = io.validate_user_input_int("Input syze of array: ")
                lst = list(io.generator_float_list(lst_size))
        else:
                print("Enter float list to procced\n")
                lst = io.valifate_user_float_list_input()

        print("Your List: ", end = "")
        print(*lst, sep = ", ")

        

        
        

        working_list = get_sublist(lst)

        list_sum = sum(working_list)
        list_minimum = min(list(map(math.fabs, working_list)))


        print(f"The inputed array {lst}") 
        print(f"The proceeded array {working_list}")
        print(f"Sum: {list_sum}")
        print(f"FABS Minimum: {list_minimum}") 

        screen = menu.ProgramEnd()



Task5()