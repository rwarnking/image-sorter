import os

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
        self.meta_info.file_count_max = len(filelist)

        # Iterate the files
        for file in filelist:
            self.process_file(file, target_dir)

        print(f"Finished sorting")

        self.meta_info.finished = True

    def process_file(self, file, target_dir):
        # Get information of file
        year = "2020"
        month = "01"
        day = "01"
        is_compatible = file.endswith(".jpg") or file.endswith(".png")
        if not is_compatible:
            # TODO print name
            print(f"Found incompatible file.")
            return

        # Ask database for event using the date
        #event = db.get_event(year, month, day)
        event = "christmas"

        # Check if year folder for this file exists
        year_dir = target_dir + "/" + year
        try:
            if not os.path.exists(year_dir):
                os.mkdir(year_dir)
        except OSError:
            messagebox.showinfo(
                message="Creation of the directory %s failed" % year_dir, title="Error"
            )

        # Check if event folder for this file exists
        event_dir = year_dir + "/" + event
        try:
            if not os.path.exists(event_dir):
                os.mkdir(event_dir)
        except OSError:
            messagebox.showinfo(
                message="Creation of the directory %s failed" % event_dir, title="Error"
            )

        # Move file to the correct folder

        # Rename file with the defined template
