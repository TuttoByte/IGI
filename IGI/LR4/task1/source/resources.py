
import datetime


months = {
    1: "January", 2: "February", 3: "March", 4: "April",
    5: "May", 6: "June", 7: "July", 8: "August",
    9: "September", 10: "October", 11: "November", 12: "December"
}

class WorkerInfo:
    def __init__(self, name : str, date : datetime, duration : int):
        self.startDate = date
        self.duration = duration
        self.name = name

    def GetStartMonth(self) -> str:
        return months[self.startDate.date().month]
        

