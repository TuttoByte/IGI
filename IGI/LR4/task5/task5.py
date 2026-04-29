from utils import menu
from utils import io
import task5.services.matrix as m

def Task5():

    nSize = io.validate_user_input_int("Input the matrix size: ")
    

    matrix = m.MatrixController(nSize)
    print("Matrix randomly created: ")
    print(matrix.matrix)

    screen = True
    while screen:

        print("----------------------------------")
        print("Chose opertaion to complete")
        print("1. Get all minimal equals indexes")
        print("2. Get std build in")
        print("3. Get std self calculated")
        choice = io.validate_user_input_int("Input choice to procced: ")
    
        match choice:
            case 1:
                print("Min element is:  ", matrix.Minimum())
                print("Min elements equla indexes:", matrix.AllMinimum())

            case 2:
                print ("Std is  ", m.MatrixOperation.std_dev(matrix.matrix))
            case 3:
                print("Std is ", m.MatrixOperation.std_arif(matrix.matrix))    
            case _:
                print("End")
    
        
        
        
        screen = menu.ProgramEnd()
        menu.cls()



# If module is executing run it
if __name__ == "__main__":
    Task5()
