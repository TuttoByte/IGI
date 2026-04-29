
import task1.source.resources as res

def FindWorker(workers : list[res.WorkerInfo], target: str) -> res.WorkerInfo:
    """
    Find worker by name.

    Args:
        workers: List of workers.
        target: Name to search.

    Returns:
        Found worker or empty WorkerInfo if not found.
    """
    for i in len(workers):
        if workers[i].name == target:
            return workers[i]

    return res.WorkerInfo("nothing", "", "")    
     



def SortByName(workers : list[res.WorkerInfo]) -> list[res.WorkerInfo]:
    """
    Sort workers by name.

    Args:
        workers: List of workers.

    Returns:
        Sorted list of workers.
    """
    return workers.sort(key= lambda x: x.name)


