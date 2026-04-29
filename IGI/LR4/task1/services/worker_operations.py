import task1.source.resources as res
import utils.io




class WokreBase:

    def __init__(self):
        self.workers: list[res.WorkerInfo] = []

    def NewWorker(self):


        print("Type Name of Worker: ")
        name = input()
        date = utils.io.validate_user_input_datatime("Type start date in foram dd-MM-YYYY: ")
        duration = utils.io.validate_user_input_int("Input duration time: ")
    

        worker = res.WorkerInfo(name, date, duration)
        self.workers.append(worker)


    def GetStatistic(self) -> dict:
        monthsStat = {}
        for i in range(len(self.workers)):
            monthsStat[self.workers[i].GetStartMonth()] = monthsStat.get(self.workers[i].name, 0) + 1

        return monthsStat



    def GetStatisticPersent(self) -> dict:
        inner = self.GetStatistic()

        for k  in inner.keys():
            inner[k] = inner[k] * 100 / len(self.workers) 
        
        return inner

    def MakeCollection(self) -> dict:
        return {index: value for index, value in enumerate(self.workers)}
        
    
    def LoadFromCollection(self, collection : list) -> None:
        self.workers = collection




        





