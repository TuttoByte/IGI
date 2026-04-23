
import re

def GetSentenciesNumber(text : str) -> int:
   return GetAllNSentencies(text) + GetAllQSentencies(text) + GetAllVSentencies(text)


def GetAllNSentencies(text : str) -> int:
   return text.count('.')

def GetAllQSentencies(text : str) -> int:
   return text.count('?')

def GetAllVSentencies(text : str) -> int:
   return text.count('!')


def GetAllSentencies(text : str) -> list:
  return list(filter(lambda x: x != "",re.split(r'[.!?]', text) ))
   


def GetAllWorlds(text : str) -> list:
    return list(filter(lambda x: x != "", re.split(r'[;,\s!?.]', text) ))


def GetMedianSentenceLen(text : str) -> float:
   
    wordLen = 0
    syb = 0
    sentencies = GetAllSentencies(text)
    for s in sentencies:
       words = GetAllWorlds(s)
       wordLen += len(words)
       for w in words:
          syb += len(w)



    return syb / len(sentencies)


def GetMedianWordLen(text : str) -> float:
   
    wordLen = 0
    syb = 0
    sentencies = GetAllSentencies(text)
    for s in sentencies:
       words = GetAllWorlds(s)
       wordLen += len(words)
       for w in words:
          syb += len(w)

        

    return syb / wordLen


def GetSmilesNumber(text : str) -> int:
  return (len(re.findall(r';-*\d*\(', text)) + 
            len(re.findall(r';-*\d*\)', text)) + 
            len(re.findall(r';-*\d*\[', text)) + 
            len(re.findall(r';-*\d*\]', text)) +

            len(re.findall(r':-*\d*\(', text)) + 
            len(re.findall(r':-*\d*\)', text)) + 
            len(re.findall(r':-*\d*\[', text)) + 
            len(re.findall(r':-*\d*\]', text))
            )



def GetAllApostrofs(text : str) -> int:
    sentencies = GetAllSentencies(text)

    count = 0

    for s in sentencies:
      words = GetAllWorlds(s)
      count += len(list(filter(lambda x: x.count("'"), words)))


    return count




def GetEndWithVolves(sbr : str) -> int:
   vowels = "aeiouyAEIOUYаеёиоуыэюяАЕЁИОУЫЭЮЯ"
   words = GetAllWorlds(sbr)

   return len(list(filter(lambda x: x[-1] in vowels, words)))



def GetByNWords(text : str,  n : int) -> list:
   return GetAllWorlds(text)[::n]
    



   