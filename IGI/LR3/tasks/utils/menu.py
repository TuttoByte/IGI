def ProgramEnd() -> bool:
    """
    Menu function: asks user to continue or exit program.
    
    Returns:
        bool: True to continue, False to exit
    """
    print("1. Enter q to exit the program")
    print("2. Enter any button to continue")
    inp = input()
    if inp == "q":
        print("Exit")
        return False
    

    return True