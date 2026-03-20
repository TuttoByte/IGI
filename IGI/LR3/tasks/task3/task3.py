from .. utils import io
from .. utils import menu


def CalculateWords(text: str) -> int:
    consonants = "бвгджзйклмнпрстфхцчшщbcdfghjklmnpqrstvwxyz"
    count = 0
    words = text.split()
    for i in range(len(words)):
        if(words[i][0] in consonants and words[i][0].islower()):
            count+=1


    return count        




def Task3():
    print("Welcome to the programm that help you calculate amount of words in text, that start with consolas")
    screen = True

    while (screen):
        print("Enter text to analyse\n")

        text = input()

        words_amount = CalculateWords(text)

        print(f"The result number of words is {words_amount}")
        screen = menu.ProgramEnd()



Task3()