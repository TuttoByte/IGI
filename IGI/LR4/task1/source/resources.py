
import datetime


months = {
    01: "January", 02: "February", 03: "March", 04: "April",
    05: "May", 06: "June", 07: "July", 08: "August",
    09: "September", 10: "October", 11: "November", 12: "December"
}

class WorkerInfo:
    def __init__(self, name : str, start : datetime, duration : int):
        self.startDate = start
        self.duration = duration
        self.name = name

    def GetStartMonth(self) -> str:

        mIndex = self.startDate.split('.')[1]
        return months[mIndex]
        

