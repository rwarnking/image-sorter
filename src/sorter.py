import os
import datetime

from database import Database
from os.path import isfile, join


class Sorter:
    def __init__(self, meta_info):
        self.meta_info = meta_info

    ###############################################################################################
    # Main
    ###############################################################################################
    def run(self):
        print(f"Start sorting")

        # Get all files in the directory
        source_dir = self.meta_info.source_dir.get()
        target_dir = self.meta_info.target_dir.get()
        filelist = None
        if os.path.exists(source_dir):
            filelist = [f for f in os.listdir(source_dir) if isfile(join(source_dir, f))]

        if filelist is None or len(filelist) == 0:
            messagebox.showinfo(
                message="No files found! Select a different source path.", title="Error"
            )
            return

        # Update the progressbar and label for the files
        self.meta_info.file_count = 0
        self.meta_info.file_count_max = len(filelist)

        # Iterate the files
        for file in filelist:
            self.process_file(file, source_dir, target_dir)
            self.meta_info.file_count += 1

        print(f"Finished sorting")

        self.meta_info.finished = True

    def process_file(self, file, source_dir, target_dir):
        is_compatible = file.endswith(".jpg") or file.endswith(".png")
        if not is_compatible:
            # TODO print filename
            print(f"Found incompatible file.")
            return

        # Get information of file
        date = self.get_file_info(file)
        if date == False:
            return

        # Ask database for event using the date
        db = Database()
        result = db.get_event(date.year, date.month, date.day)
        if len(result) == 0:
            print("No matching event found.")
            return
        elif len(result) > 1:
            print("To many matching events found. Remove overlays.")

        # TODO
        #print(result)
        #print(result[0])
        #print(result[0][0])

        event = result[0][0]

        # Check if year folder for this file exists
        year_dir = join(target_dir, str(date.year))
        try:
            if not os.path.exists(year_dir):
                os.mkdir(year_dir)
        except OSError:
            messagebox.showinfo(
                message="Creation of the directory %s failed" % year_dir, title="Error"
            )

        # Check if event folder for this file exists
        month_id = str(date.month).zfill(2)
        event_dir = join(year_dir, month_id + "_" + event)
        try:
            if not os.path.exists(event_dir):
                os.mkdir(event_dir)
        except OSError:
            messagebox.showinfo(
                message="Creation of the directory %s failed" % event_dir, title="Error"
            )

        # Rename file with the defined template
        tmp, file_extension = os.path.splitext(file)
        new_name = self.get_new_filename(date, file_extension)
        print(new_name)

        # Move file to the correct folder
        try:
            #os.rename(join(source_dir, file), join(event_dir, new_name))
            print(f"Moved file.")
        except OSError:
            messagebox.showinfo(
                message="Movement of file %s failed" % file, title="Error"
            )

    # Expects a filename without path but with ending (.jpg)
    def get_file_info(self, file):
        # TODO improve this for example with a regex
        SIGNATURE_1_LEN = 15 + 4
        SIGNATURE_2_LEN = 19 + 4

        date = False

        if len(file) == SIGNATURE_1_LEN:
            date = datetime.datetime.strptime(file, "%Y%m%d_%H%M%S.jpg")
        elif len(file) == SIGNATURE_2_LEN:
            date = datetime.datetime.strptime(file, "%Y-%m-%d_%H-%M-%S.jpg")
        else:
            # TODO print filename
            print(f"Unsupported signature.")

        return date

    # https://docs.python.org/3/library/datetime.html#strftime-strptime-behavior
    def get_new_filename(self, date, file_extension):
        filename = ""
        sig = self.meta_info.get_supported_signatures()

        if self.meta_info.out_signature.get() == sig[0]:
            filename = date.isoformat("_")
        elif self.meta_info.out_signature.get() == sig[1]:
            filename = date.strftime("%Y-%m-%d_%H-%M-%S")
        elif self.meta_info.out_signature.get() == sig[2]:
            filename = date.isoformat("_", "milliseconds")
        elif self.meta_info.out_signature.get() == sig[3]:
            filename = date.strftime("%Y%m%d_%H%M%S")
        elif self.meta_info.out_signature.get() == sig[4]:
            filename = date.strftime("IMG_%Y%m%d_%H%M%S")
        elif self.meta_info.out_signature.get() == sig[5]:
            filename = date.ctime()
        else:
            # TODO number must be files in folder
            number = "001"
            filename = date.strftime("%m-%B-%d_") + number

        return filename + file_extension
