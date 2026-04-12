from .. utils import io
from .. utils import menu
from typing import Generator, Callable



def ConsonantWords(text) -> Generator[str, None, None]:
    """
    Return lowercase words starting with consonants (Russian + English).
    
    Args:
        text (str): input text to analyze
        
    Returns:
        str: list Elemenet
    """
    consonants = "бвгджзйклмнпрстфхцчшщbcdfghjklmnpqrstvwxyz"
    words = text.split()
    for word in words:
       if word and word[0].lower() in consonants:
            yield word


def CalculateWords(text: str) -> int:
    """
    Counts lowercase words starting with consonants (Russian + English).
    
    Args:
        text (str): input text to analyze
        
    Returns:
        int: count of matching words
    """
    return len(list(ConsonantWords(text)))  




def Task3() ->None:
    """Main program: counts lowercase consonant-starting words in text."""
    print("Welcome to the programm that help you calculate amount of words in text, that start with consolas")
    screen = True

    while (screen):
        print("Enter text to analyse\n")

        text = input()

        words_amount = CalculateWords(text)

        print(f"The result number of words is {words_amount}")
        screen = menu.ProgramEnd()



Task3()