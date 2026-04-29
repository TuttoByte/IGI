import zipfile

class FileService:
    """Class To Read And Write To Files"""
    def __init__(self, input_filename, output_filename):
        self.input_filename = input_filename
        self.output_filename = output_filename

    def read(self) -> str:
        """Reads From File

        Returns:
            str: File Content
        """
        try:
            with open(self.input_filename, "r", encoding="utf-8") as file:
                return file.read()
        except IOError as ex:
            raise IOError(f"Read File Error: {ex}")
            
    def write(self, result: str) -> None:
        """Write To File

        Args:
            result: What to Write
        """
        try:
            with open(self.output_filename, "w", encoding="utf-8") as file:
                file.write(result)
        except IOError as ex:
            raise IOError(f"Write to File Error: {ex}")


class ZipFileService(FileService):
    """Class To Zip Output"""
    def __init__(self, input_filename, output_filename, zipname):
        super().__init__(input_filename, output_filename)
        self.zipname = zipname

    def zip_file(self) -> None:
        """Zip Output FIle"""
        try:
            with zipfile.ZipFile(self.zipname, 'w') as myzip:
                myzip.write(self.output_filename)
        except IOError as ex:
            raise IOError(f"Zipping File Error: {ex}")
        
    def zipped_file_info(self) -> str:
        """Show Zip Archive Info

        Returns:
            str: Info
        """
        try:
            with zipfile.ZipFile(self.zipname, 'r') as myzip:
                # for item in myzip.infolist():
                item = myzip.getinfo(self.output_filename)
                return f"File Name: {item.filename}, Date: {item.date_time}, Size: {item.file_size}"
        except IOError as ex:
            raise IOError(f"Zipping File Error: {ex}")
