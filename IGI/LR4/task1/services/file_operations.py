
import csv
import pickle
from source.resources import WorkerInfo



class Marshaller:


    def ReadFromCSV(fileName : str) -> list:

        workers = list
        with open(fileName + ".save.csv", mode='r', newline='') as f:
            reader = csv.DictReader(f)
            for row in reader:
                workers.append(WorkerInfo(**row))


        return workers


    def WriteToCSV(fileName : str,  collection : dict):
        data = open(fileName + ".save.csv")
        writer  = csv.writer(data)

        writer.writerow(collection)


    def ReadFromPickle(fileName : str) -> list :
        with open(fileName + ".save.pkl", mode='+rb') as f:
            loadData = pickle.load(f)
            return list(loadData)
        

    def WriteToPickle(fileName : str,  collection : dict):
        with open(fileName + ".save.pkl") as f:
            pickle.dump(collection, f)
