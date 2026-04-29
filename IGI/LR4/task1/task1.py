
from utils import io
from utils import menu
import task1.services.collection_operations as op
import task1.services.worker_operations as wr
import task1.services.file_operations as fl



def Task1():
    """
    Run the worker management menu.
    """

    print("Welcome to worker controll base")
    controlBase = wr.WokreBase()
    print("Base in succesfully created")

    marshaller = fl.Marshaller()



    screen = True
    while screen:
        
        print("----------------------------------")
        print("Chose opertaion to complete")
        print("1. Add Worker")
        print("2. Find Worker By Name")
        print("3. Get vacation statistic")
        print("4. Save to csv")
        print("5. Save to pickle")
        print("6. Load from csv")
        print("7. Load from pickle")
        print("Any antother button to exit")
        choice = input("Input choice to procced: ")
    
        match choice:
            case '1':
                controlBase.NewWorker()
            case '2':
                print("Input worker name ")
                name = input()
                wrk = op.FindWorker(controlBase.workers, name)
                print(wrk)
            case '3':
                print("The vacations statistic overall : ", controlBase.GetStatistic())
                print("The vacations statistic percent : ", controlBase.GetStatisticPersent())
            case '4':
                marshaller.WriteToCSV("igi", controlBase.workers)
            case '5':
                marshaller.WriteToPickle("igi", controlBase.workers)   
            case '6':
                newCollection = marshaller.ReadFromCSV("igi") 
                controlBase.LoadFromCollection(newCollection)  
            case '7':
                newCollection = marshaller.ReadFromPickle("igi") 
                controlBase.LoadFromCollection(newCollection)   
            case _:
                print("Exit")     
        
        
        
        screen = menu.ProgramEnd()
        menu.cls()



# If module is executing run it
if __name__ == "__main__":
    Task1()
