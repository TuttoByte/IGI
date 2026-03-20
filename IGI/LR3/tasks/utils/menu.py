def ProgramEnd() -> bool:
    print("1. Enter q to exit the program")
    print("2. Enter any button to continue")
    inp = input()
    if inp == "q":
        print("Exit")
        return False
    

    return True