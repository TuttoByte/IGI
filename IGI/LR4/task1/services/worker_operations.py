from task1.source.resources import WorkerInfo
import utils.io




class WokreBase:


    


    def __init__(self):
        self.workers: list[WorkerInfo] = []

    def NewWorker(self, collecton : list[WorkerInfo]):


        print("Type Name of Worker: ")
        name = input()
        date = utils.io.validate_user_input_datatime("Type start date in foram dd-MM-YYYY")
        duration = utils.io.validate_user_input_int("Input duration time")
    

        worker = WorkerInfo(name, date, duration)
        self.workers.append(worker)


    def GetStatistic(self) -> dict:
        monthsStat = dict

        for i in range(self.workers[i]):
            monthsStat[self.workers[i].name] = monthsStat.get(self.workers[i].name, 0) + 1

        return monthsStat



    def GetStatisticPersent(self) -> dict:
        inner = self.GetStatisticInner()

        for k, v in inner:
            inner[k] = inner[k] * 100 / len(self.workers) 
        
        return inner




        





