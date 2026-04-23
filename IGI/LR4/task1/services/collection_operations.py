
from source.resources import WorkerInfo

def FindWorker(workers : list[WorkerInfo], target: str) -> WorkerInfo:
    for i in len(workers):
        if workers[i].name == target:
            return workers[i]

    return WorkerInfo("nothing", "", "")    
     



def SortByName(workers : list[WorkerInfo]) -> list[WorkerInfo]:
    return workers.sort(key= lambda x: x.name)


