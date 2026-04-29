
from utils import io
from utils import menu
from task2.services.over_text import Analyzer
from task2.services.file_service import ZipFileService

def Task2() -> None:
    """
    Menu for Task_2
    """

    screen = True
    
    while screen:
     
            

            input_filename = input("Input Input File Name: ")

            output_filename = input("Input Output File Name: ")
            
            zip_filename = input("Input Zip File Name: ")

            file_service = ZipFileService(input_filename, output_filename, zip_filename)

            text = file_service.read()
            print("Text Read Successfully!")
            print(text)
            print()

            analyzer = Analyzer(text)
            print("\nResult:")
            print(analyzer)
            print()

            file_service.write(analyzer.__str__())
            print("Result Write Successfully!")


            file_service.zip_file()
            print("Result Zipped Successfully!")
            print()

            print("Zip Info: ")
            print(file_service.zipped_file_info())


            screen = menu.ProgramEnd()

        

# If module is executing run it
if __name__ == "__main__":
    Task2() 