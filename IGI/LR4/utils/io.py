import random as rnd
from datetime import datetime
from collections.abc import Callable

def repeat_input (func : Callable) -> Callable:
    """
    Decorator: repeats input request until valid input received.
    
    Args:
        func: decorated validation function
        
    Returns:
        wrapper: function that retries on ValueError
    """

    def wrapper(*args, **kwargs):
         while True:
            try:
                val = func(*args, **kwargs)

                return val
            
            except ValueError as error:
                print(f"Invalid Input: {error}") 



    return wrapper



def validate_positive (func : Callable) -> Callable:
    """
    Decorator: validate if input is positive.
    
    Args:
        func: decorated validation function
        
    Returns:
        wrapper: function that return ValueError
    """

    def wrapper(*args, **kwargs):
         val = func(*args, **kwargs)
         if val <= 0:
             raise ValueError("Side can not be negative")
         
         return val
    return wrapper


def validate_angle (func : Callable) -> Callable:
    """
    Decorator: validate if triagnle angle is less then 180.
    
    Args:
        func: decorated validation function
        
    Returns:
        wrapper: function that return ValueError
    """

    def wrapper(*args, **kwargs):
         val = func(*args, **kwargs)
         if val >= 180 or val < 0:
             raise ValueError("Angle in triangle can not be more then 180 or less then 0")
         return val

    return wrapper



@repeat_input
@validate_positive
def validate_user_input_float_positive(msg : str) -> float:
    """Repeatedly asks for float input until valid."""
    inp = (float)(input(msg))
    return inp



@repeat_input
def validate_user_input_float(msg : str) -> float:
    """Repeatedly asks for float input until valid."""
    inp = (float)(input(msg))
    return inp




@repeat_input
@validate_angle
def validate_user_input_angle(msg : str) -> float:
    """Repeatedly asks for float input until valid."""
    inp = (float)(input(msg))
    return inp





@repeat_input
def validate_user_input_datatime(msg : str) -> datetime:
    """Repeatedly asks for data input in %d-%m-%Y foramt until valid."""
    inp = (input(msg))
    inp = datetime.strptime(inp, "%d-%m-%Y")
    return inp

 

@repeat_input
def validate_user_input_int(msg : str) -> int:
    """Repeatedly asks for int input until valid."""
    inp = (int)(input(msg))
    return inp


def valifate_user_float_list_input() -> list:
    """
    Validates space-separated float list input with manual retry loop.
    """
    print("Plese enter the values with space seporation: \n")
    while True:
        err = False
        inp = input().split()
        for i in range(len(inp)):
            try:
                inp[i] = (float)(inp[i])
            except ValueError:
                print("Invalid input! Please try again")
                err = True
        if (err == False):
            return inp        

        


def generator_int_list(size : int, min_value : int = -10, max_value : int = 10) -> Generator[int, None, None]:
    """
    Generate List of Integers
    
    Args:
        size: List Size
        min_value: Minimum Value for List
        max_value: Maximum Value for List

    Yields:
        int: List Element
    """

    for _ in range(size):
        yield rnd.randint(min_value, max_value)

def generator_float_list(size : int, min_value : float = -10, max_value : float = 10) -> Generator[float, None, None]:
    """
    Generate List of Float Numbers
    
    Args:
        size: List Size
        min_value: Minimum Value for List
        max_value: Maximum Value for List

    Yields:6
    """

    for _ in range(size):
        yield rnd.uniform(min_value, max_value)



        
        
@repeat_input
def get_yes_or_no(prompt: str) -> bool:
    """
    Get User Answer Yes or No
    
    Args:
        prompt: Message for User

    Returns:
        bool: User Answer
    """

    answer = input(prompt).lower()
    if answer == "yes" or answer == "y":
        return True
        
    if answer == "no" or answer == "n":
        return False
        
    raise ValueError("Wrong Answer! Enter yes(y) or no(n)")        