
import csv
import pickle
import task1.source.resources as res
import datetime



class Marshaller:


    def ReadFromCSV(self, fileName : str) -> list:
        """
        Read workers from a CSV file.

        Args:
            file_name: Base file name without extension.

        Returns:
            List of WorkerInfo objects.
        """

        workers = []
        with open(fileName + ".save.csv", mode='r', newline='') as f:
            reader = csv.DictReader(f)
            for row in reader:
                workers.append(
                    res.WorkerInfo(
                        name=row["name"],
                        date= datetime.datetime.strptime(row["date"], "%d-%m-%Y"),
                        duration= int(row["duration"])
                    )
                )


        return workers


    def WriteToCSV(self, fileName : str,  collection : list[res.WorkerInfo]):
        """
        Write workers to a CSV file.

        Args:
            file_name: Base file name without extension.
            collection: List of WorkerInfo objects.
        """
        with open(fileName + ".save.csv", mode='w+', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=["name", "date", "duration"])
            writer.writeheader()

            for worker in collection:
                writer.writerow({
                    "name": worker.name,
                    "date": worker.startDate.strftime("%d-%m-%Y"),
                    "duration": worker.duration
                })


    def ReadFromPickle(self, fileName : str) -> list :
        """
        Read serialized data from a Pickle file.

        Args:
            file_name: Base file name without extension.

        Returns:
            Loaded collection as a list.
        """
        with open(fileName + ".save.pkl", mode='+rb') as f:
            loadData = pickle.load(f)
            return list(loadData)
        

    def WriteToPickle(self, fileName : str,  collection : list):
        """
        Write serialized data to a Pickle file.

        Args:
            file_name: Base file name without extension.
            collection: Collection to serialize.
        """
        with open(fileName + ".save.pkl", mode= "wb+") as f:
            pickle.dump(collection, f)
