from .. utils import menu

text = "So she was considering in her own mind, as well as she could," \
" for the hot day made her feel very sleepy and stupid, whether the pleasure" \
" of making a daisy-chain would be worth the trouble of getting up and picking " \
"the daisies, when suddenly a White Rabbit with pink eyes ran close by her."




def custom_split(text: str) -> list:
    """
    Splits text by commas, then by spaces. Flattens result into single word list.
    
    Args:
        text (str): input text
        
    Returns:
        list: all words from text
    """
    words = list(map(lambda x: x.split(), text.split(",")))

    new_words = []
    for i in range(len(words)):
        new_words.extend(words[i])

    return new_words    


def find_longest(text: str, lit: str) -> str:
    """
    Finds longest word ending with given letter.
    
    Args:
        text (str): input text
        lit (str): ending letter to match
        
    Returns:
        str: longest matching word (empty if none found)
    """
    return sorted(list(filter(lambda x: x[-1] == lit, custom_split(text))), key=lambda x: len(x), reverse=True)[0]   



def find_count_minimum(text: str) -> int:
    """
    Counts words with minimum length in text.
    
    Args:
        text (str): input text
        
    Returns:
        int: count of shortest words
    """
    new_words = custom_split(text)
    
    minimum = len(new_words[0])

    for i in range(len(new_words)):
        if (len(new_words[i]) <= minimum):
            minimum = len(new_words[i])


    return len([x for x in new_words if len(x) == minimum ])



def find_if_last(text: str, last:str) -> list:
    """
    Finds all words ending with given character.
    
    Args:
        text (str): input text
        last (str): ending character
        
    Returns:
        list: matching words
    """
    new_words = custom_split(text)
    return [x for x in new_words if x[-1] == last]


def Task4() -> None:
    """Main program: demonstrates text analysis functions on sample text."""
    print("Welcome to the programm procceed some text operations")
    screen = True

    while (screen):

        print(f"a) Amount of words with minimum lenght: {find_count_minimum(text)}")
        print(f"b) Words, after wich goes point: ")
        words_point = find_if_last(text, '.')
        for i in range(len(words_point)):
            print(words_point[i])

        print (f"c) Find longest word that's end with 'r': {find_longest(text, "r")}")

        
        

        screen = menu.ProgramEnd()

Task4()