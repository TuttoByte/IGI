def validate_user_input_float(msg : str) -> float:
    while True:
        try:
            inp = (float)(input(msg))
            return inp
        except ValueError:
            print("Invalid input! Please try again")



def validate_user_input_int(msg : str) -> int:
    while True:
        try:
            inp = (int)(input(msg))
            return inp
        except ValueError:
            print("Invalid input! Please try again")


def valifate_user_float_list_input() -> list:
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

        