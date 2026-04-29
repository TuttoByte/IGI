
import task1.source.resources as res

def FindWorker(workers : list[res.WorkerInfo], target: str) -> res.WorkerInfo:
    for i in len(workers):
        if workers[i].name == target:
            return workers[i]

    return res.WorkerInfo("nothing", "", "")    
     



def SortByName(workers : list[res.WorkerInfo]) -> list[res.WorkerInfo]:
    return workers.sort(key= lambda x: x.name)


