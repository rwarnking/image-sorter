import datetime
import os
import re

from database import Database
from os.path import isfile, join


class Sorter:
    def __init__(self, meta_info):
        self.meta_info = meta_info

    ###############################################################################################
    # Main
    ###############################################################################################
    def run(self):
        self.meta_info.text_queue.put("Start sorting\n")

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

        self.meta_info.text_queue.put("Finished sorting\n")
        self.meta_info.finished = True

    def process_file(self, file, source_dir, target_dir):
        is_compatible = file.endswith(".jpg") or file.endswith(".png")
        if not is_compatible:
            self.meta_info.text_queue.put(f"Found incompatible file: {file}.\n")
            return

        # Get information of file
        tmp, file_extension = os.path.splitext(file)
        date = self.get_file_info(file, file_extension)
        if date == False:
            return

        # Ask database for event using the date
        db = Database()
        result = db.get_event(date.year, date.month, date.day)
        if len(result) == 0:
            self.meta_info.text_queue.put(f"No matching event found for file: {file}.\n")
            return
        elif len(result) > 1:
            self.meta_info.text_queue.put(f"To many matching events found for file: {file}.\n")

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
        new_name = self.get_new_filename(date, file_extension)

        # Move file to the correct folder
        try:
            #os.rename(join(source_dir, file), join(event_dir, new_name))
            self.meta_info.text_queue.put(f"Moved file: {file}. New Name: {new_name}.\n")
        except OSError:
            messagebox.showinfo(
                message="Movement of file %s failed" % file, title="Error"
            )

    # https://www.w3schools.com/python/python_regex.asp#search
    def get_file_info(self, file, file_extension):
        date = False

        if self.meta_info.in_signature == "IMG-Meta-Info":
            print(f"Unimplemented.")
        else :
            if re.search("^\d{4}-\d{2}-\d{2}_\d{2}-\d{2}-\d{2}(\.jpg|\.png)$", file) is not None:
                date = datetime.datetime.strptime(file, "%Y-%m-%d_%H-%M-%S" + file_extension)
            elif re.search("^\d{4}-\d{2}-\d{2}_\d{2}-\d{2}-\d{2}\.\d{3}(\.jpg|\.png)$", file) is not None:
                date = datetime.datetime.strptime(file, "%Y-%m-%d_%H-%M-%S.%f"+ file_extension)
            elif re.search("^\d{8}_\d{6}(\.jpg|\.png)$", file) is not None:
                date = datetime.datetime.strptime(file, "%Y%m%d_%H%M%S" + file_extension)
            elif re.search("^IMG_\d{8}_\d{6}(\.jpg|\.png)$", file) is not None:
                date = datetime.datetime.strptime(file, "IMG_%Y%m%d_%H%M%S" + file_extension)
            elif re.search(
                "^\w{3}\s\w{3}\s\d{2}\s\d{2}-\d{2}-\d{2}\s\d{4}(\.jpg|\.png)$", file
            ) is not None:
                date = datetime.datetime.strptime(file, "%a %b %d %H-%M-%S %Y" + file_extension)
            elif re.search("^\d{2}-\w*-\d{2}_\d{3}(\.jpg|\.png)$", file) is not None:
                # TODO year must be accessed somehow
                date = datetime.datetime.strptime(file[:9], "%m-%b-%d")
            else:
                self.meta_info.text_queue.put(f"Unsupported signature for file: {file}.\n")

        return date

    # https://docs.python.org/3/library/datetime.html#strftime-strptime-behavior
    def get_new_filename(self, date, file_extension):
        filename = ""
        sig = self.meta_info.get_supported_signatures()

        if self.meta_info.out_signature.get() == sig[0]:
            filename = date.isoformat("_")
            filename = filename.replace(":", "-")
        elif self.meta_info.out_signature.get() == sig[1]:
            filename = date.isoformat("_", "milliseconds")
            filename = filename.replace(":", "-")
        elif self.meta_info.out_signature.get() == sig[2]:
            filename = date.strftime("%Y%m%d_%H%M%S")
        elif self.meta_info.out_signature.get() == sig[3]:
            filename = date.strftime("IMG_%Y%m%d_%H%M%S")
        elif self.meta_info.out_signature.get() == sig[4]:
            filename = date.ctime()
            filename = filename.replace(":", "-")
        else:
            # TODO number must be files in folder
            number = "001"
            filename = date.strftime("%m-%B-%d_") + number

        return filename + file_extension
