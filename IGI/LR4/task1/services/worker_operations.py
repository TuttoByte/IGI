import task1.source.resources as res
import utils.io




class WokreBase:

    def __init__(self):
        self.workers: list[res.WorkerInfo] = []

    def NewWorker(self):
        """
        Create a new worker from user input and add it to the collection.
        """
        print("Type Name of Worker: ")
        name = input()
        date = utils.io.validate_user_input_datatime("Type start date in foram dd-MM-YYYY: ")
        duration = utils.io.validate_user_input_int("Input duration time: ")
    

        worker = res.WorkerInfo(name, date, duration)
        self.workers.append(worker)


    def GetStatistic(self) -> dict:
        """
        Count workers by start month.

        Returns:
            Dictionary where key is month and value is worker count.
        """
        monthsStat = {}
        for i in range(len(self.workers)):
            monthsStat[self.workers[i].GetStartMonth()] = monthsStat.get(self.workers[i].name, 0) + 1

        return monthsStat



    def GetStatisticPersent(self) -> dict:
        """
        Return worker statistics in percent.
        """
        inner = self.GetStatistic()

        for k  in inner.keys():
            inner[k] = inner[k] * 100 / len(self.workers) 
        
        return inner

    def MakeCollection(self) -> dict:
        """
        Convert workers list to indexed dictionary.
        """
        return {index: value for index, value in enumerate(self.workers)}
        
    
    def LoadFromCollection(self, collection : list) -> None:
        """
        Load workers from a collection.
        """
        self.workers = collection




        





