import datetime
import os
import re
import shutil
from os.path import isfile, join
from tkinter import messagebox

import piexif
from database import Database
from PIL import Image


class Sorter:
    def __init__(self, meta_info):
        self.meta_info = meta_info

    ###############################################################################################
    # Main
    ###############################################################################################
    def run(self):
        self.meta_info.text_queue.put("Start sorting\n")

        # create database
        self.db = Database()

        # These variables are duplicates of the metadata vars.
        # This is done to improve the performance since these get() functions can get expensive
        # and should therefore not be called for each processed file
        self.copy_files = self.meta_info.copy_files.get()
        self.modify_meta = self.meta_info.modify_meta.get()
        self.fallback_sig = self.meta_info.fallback_sig.get()

        self.shift_timedata = self.meta_info.shift_timedata.get()
        self.time_option = self.meta_info.time_option.get()
        self.shift_days = int(self.meta_info.shift_days.get())
        self.shift_minutes = int(self.meta_info.shift_minutes.get())
        self.shift_hours = int(self.meta_info.shift_hours.get())

        self.in_signature = self.meta_info.in_signature.get()
        self.out_signature = self.meta_info.out_signature.get()

        # Get all files in the directory
        source_dir = self.meta_info.source_dir.get()
        target_dir = self.meta_info.target_dir.get()

        if not os.path.exists(source_dir):
            messagebox.showinfo(message="Source path could not be found.", title="Error")
            return

        dir_info = [(len(files), cur_path) for cur_path, d, files in os.walk(source_dir)]
        file_counts, file_dirs = zip(*dir_info)

        # Update the progressbar and label for the files
        self.meta_info.file_count_max = sum(file_counts)

        if sum(file_counts) == 0:
            messagebox.showinfo(
                message="No files found! Select a different source path.", title="Error"
            )
            return

        for file_dir in file_dirs:
            filelist = [f for f in os.listdir(file_dir) if isfile(join(file_dir, f))]

            if len(filelist) == 0:
                messagebox.showinfo(message=f"Found empty folder: {file_dir}!", title="Error")

            # Iterate the files
            for file in filelist:
                self.process_file(file, file_dir, target_dir)
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
        date = self.get_file_info(file, source_dir, file_extension)
        if date is False:
            return
        if self.shift_timedata > 0:
            try:
                date_shift = datetime.timedelta(
                    days=self.shift_days,
                    minutes=self.shift_minutes,
                    hours=self.shift_hours,
                )
                if self.time_option == "Forward":
                    date = date + date_shift
                else:
                    date = date - date_shift
            except ValueError:
                messagebox.showinfo(message="Shift values need to be at least 0.", title="Error")

        # Ask database for event using the date
        result = self.db.get_event(date.year, date.month, date.day)
        if len(result) == 0:
            self.meta_info.text_queue.put(f"No matching event found for file: {file}.\n")
            return
        elif len(result) > 1:
            self.meta_info.text_queue.put(f"To many matching events found for file: {file}.\n")
            return

        # TODO
        # print(result)
        # print(result[0])
        # print(result[0][0])

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
        new_name = self.get_new_filename(date)
        new_name_ext = self.get_new_filename(date) + file_extension

        if os.path.exists(os.path.join(event_dir, new_name_ext)):
            confirm = messagebox.askyesno(
                title="Warning",
                message="Filename already taken! Override file? Adding number to name otherwise.",
                default="no",
            )
            if not confirm:
                i = 1
                new_name_ext = f"{new_name}_{i}{file_extension}"
                while os.path.exists(os.path.join(event_dir, new_name_ext)):
                    new_name_ext = f"{new_name}_{i}{file_extension}"
                    i += 1

        try:
            if self.copy_files > 0:
                # Copy file
                shutil.copy2(join(source_dir, file), join(event_dir, new_name_ext))
                self.meta_info.text_queue.put(f"Copied file: {file} with name: {new_name_ext}.\n")
            else:
                # Move file to the correct folder
                shutil.move(join(source_dir, file), join(event_dir, new_name_ext))
                self.meta_info.text_queue.put(f"Moved file: {file}. New Name: {new_name_ext}.\n")
        except OSError:
            messagebox.showinfo(message="Movement of file %s failed" % file, title="Error")

        if self.modify_meta > 0:
            self.modify_metadata(join(event_dir, new_name_ext), event)

    # https://www.w3schools.com/python/python_regex.asp#search
    def get_file_info(self, file, source_dir, file_extension, fallback=False):
        date = False

        if self.in_signature == "IMG-Meta-Info" or fallback:
            if fallback:
                self.meta_info.text_queue.put(
                    f"Unsupported signature for file: {file} used fallback.\n"
                )

            try:
                img = Image.open(join(source_dir, file))
                exif_dict = piexif.load(img.info["exif"])
                # https://www.ffsf.de/threads/exif-datetimeoriginal-oder-datetimedigitized.9913/
                time = exif_dict["Exif"][piexif.ExifIFD.DateTimeOriginal]
                date = datetime.datetime.strptime(str(time, "ascii"), "%Y:%m:%d %H:%M:%S")
            # TODO which exceptions?
            except FileNotFoundError:
                self.meta_info.text_queue.put(f"File {file} could not be found.\n")
            except KeyError:
                self.meta_info.text_queue.put(f"Metadata not readable for file: {file}.\n")
            except ValueError:
                self.meta_info.text_queue.put(f"Time data not readable for file: {file}.\n")

        else:
            regex_list = self.meta_info.get_signature_regex()
            strptime_list = self.meta_info.get_signature_strptime()
            assert len(regex_list) == len(strptime_list)

            for regex, strptime in zip(regex_list, strptime_list):
                if re.search(regex, file) is not None:
                    try:
                        date = datetime.datetime.strptime(file, strptime + file_extension)
                    except ValueError:
                        self.meta_info.text_queue.put(
                            f"Time data not readable for file: {file}.\n"
                        )
                    return date

            if self.fallback_sig:
                date = self.get_file_info(file, source_dir, file_extension, True)
            else:
                self.meta_info.text_queue.put(f"Unsupported signature for file: {file}.\n")

        return date

    # https://docs.python.org/3/library/datetime.html#strftime-strptime-behavior
    def get_new_filename(self, date):
        filename = ""
        sig = self.meta_info.get_supported_signatures()

        if self.out_signature == sig[0]:
            filename = date.isoformat("_")
            filename = filename.replace(":", "-")
        elif self.out_signature == sig[1]:
            filename = date.isoformat("_", "milliseconds")
            filename = filename.replace(":", "-")
        elif self.out_signature == sig[2]:
            filename = date.strftime("%Y%m%d_%H%M%S")
        elif self.out_signature == sig[3]:
            filename = date.strftime("IMG_%Y%m%d_%H%M%S")
        elif self.out_signature == sig[4]:
            filename = date.ctime()
            filename = filename.replace(":", "-")
        else:
            # TODO number must be files in folder
            number = "001"
            filename = date.strftime("%m-%B-%d_") + number

        return filename

    def modify_metadata(self, file_with_path, title=""):
        try:
            img = Image.open(file_with_path)
            exif_dict = piexif.load(img.info["exif"])

            if piexif.ImageIFD.ImageDescription not in exif_dict["0th"]:
                exif_dict["0th"][piexif.ImageIFD.ImageDescription] = title

            if piexif.ImageIFD.Artist not in exif_dict["0th"]:
                make = exif_dict["0th"][piexif.ImageIFD.Make]
                model = exif_dict["0th"][piexif.ImageIFD.Model]
                artist = self.db.get_artist(str(make, "ascii"), str(model, "ascii"))
                if len(artist) == 1:
                    # TODO [0][0]
                    exif_dict["0th"][piexif.ImageIFD.Artist] = artist[0][0]

            exif_bytes = piexif.dump(exif_dict)
            img.save(
                file_with_path,
                exif=exif_bytes,
                quality="keep",
                subsampling="keep",
                icc_profile=img.info.get("icc_profile"),
                optimize=False,
            )
        except FileNotFoundError:
            self.meta_info.text_queue.put(
                f"File {file_with_path} could not be found in modify metadata.\n"
            )

    def debug_print_metadata(self, file):
        img = Image.open(file)
        exif_dict = piexif.load(img.info["exif"])

        m_data = exif_dict["0th"]
        tmp_dict = piexif.ImageIFD.__dict__

        for k in m_data:
            for e in tmp_dict:
                if k == tmp_dict[e]:
                    print(e, m_data[k])

        print("%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%")

        m_data = exif_dict["Exif"]
        tmp_dict = piexif.ExifIFD.__dict__

        for k in m_data:
            for e in tmp_dict:
                if k == tmp_dict[e]:
                    print(e, m_data[k])

        print("%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%")

        m_data = exif_dict["1st"]
        tmp_dict = piexif.ImageIFD.__dict__

        for k in m_data:
            for e in tmp_dict:
                if k == tmp_dict[e]:
                    print(e, m_data[k])
