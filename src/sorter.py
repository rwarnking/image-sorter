import datetime
import os
import re
import shutil
from os.path import isfile, join
from tkinter import messagebox

import piexif
from database import Database
from messagebox import MessageBox

# from PIL import Image
# from exif import Image as Image2
# from pyexiv2 import Image as ImgMeta

META = 1
NAME = 2


class Sorter:
    def __init__(self, meta_info):
        self.meta_info = meta_info
        self.confirm = False

    ###############################################################################################
    # Main
    ###############################################################################################
    def run(self):
        self.meta_info.text_queue.put("Start sorting\n")

        # create database
        self.db = Database()
        # List of raw files that were processed
        self.raw_list = []

        # These variables are duplicates of the metadata vars.
        # This is done to improve the performance since these get() functions can get expensive
        # and should therefore not be called for each processed file
        self.copy_files = self.meta_info.copy_files.get()
        self.copy_unmatched = self.meta_info.copy_unmatched.get()
        self.process_raw = self.meta_info.process_raw.get()
        self.modify_meta = self.meta_info.modify_meta.get()
        self.fallback_sig = self.meta_info.fallback_sig.get()

        self.shift_timedata = self.meta_info.shift_timedata.get()
        self.time_option = self.meta_info.time_option.get()
        self.shift_days = int(self.meta_info.shift_days.get())
        self.shift_hours = int(self.meta_info.shift_hours.get())
        self.shift_minutes = int(self.meta_info.shift_minutes.get())
        self.shift_seconds = int(self.meta_info.shift_seconds.get())

        self.in_signature = self.meta_info.in_signature.get()
        self.file_signature = self.meta_info.file_signature.get()
        self.folder_signature = self.meta_info.folder_signature.get()

        # Get all files in the directory
        source_dir = self.meta_info.img_src.get()
        target_dir = self.meta_info.img_tgt.get()

        if not os.path.exists(source_dir):
            messagebox.showinfo(message="Source path could not be found.", title="Error")
            self.meta_info.finished = True
            return

        # If only the root directory should be processed
        file_dirs = [source_dir]
        file_counts = len([1 for f in os.listdir(source_dir) if isfile(join(source_dir, f))])
        # Override if the folder should be processed recursive
        if self.meta_info.recursive.get() == 1:
            dir_info = [(len(files), cur_path) for cur_path, d, files in os.walk(source_dir)]
            file_counts, file_dirs = zip(*dir_info)
            file_counts = sum(file_counts)

        # Update the progressbar and label for the files
        self.meta_info.file_count_max = file_counts

        if file_counts == 0:
            messagebox.showinfo(
                message="No files found! Select a different source path.", title="Error"
            )
            self.meta_info.finished = True
            return

        for file_dir in file_dirs:
            filelist = [f for f in os.listdir(file_dir) if isfile(join(file_dir, f))]

            if len(os.listdir(file_dir)) == 0:
                messagebox.showinfo(message=f"Found empty folder: {file_dir}!", title="Error")

            # Iterate the files
            for file in filelist:
                self.process_file(file, file_dir, target_dir)
                self.meta_info.file_count += 1

        self.meta_info.text_queue.put("Finished sorting\n")
        self.meta_info.finished = True

    def process_file(self, file, source_dir, target_dir):
        is_compatible = (
            file.lower().endswith(".jpg")
            or file.lower().endswith(".png")
            or file.lower().endswith(".mp4")
            or file.lower().endswith(".gif")
            or file.lower().endswith(".svg")
        )
        if not is_compatible:
            self.meta_info.text_queue.put(f"Found incompatible file: {file}.\n")
            if self.copy_unmatched > 0:
                # Checks if a file is a .raw file and was already processed
                # This does only work if the files are ordered alphabetically
                if (
                    file.lower().endswith(".raw")
                    and self.process_raw > 0
                    and file in self.raw_list
                ):
                    return
                # Copy file
                shutil.copy2(join(source_dir, file), target_dir)
                self.meta_info.text_queue.put("Copied file anyway.\n")
            return

        # Get information of file
        orig_file_name, file_extension = os.path.splitext(file)
        file_extension = file_extension.lower()
        date = self.get_file_info(file, source_dir, file_extension)
        if date is False:
            return
        if self.shift_timedata > 0:
            try:
                self.date_shift = datetime.timedelta(
                    days=self.shift_days,
                    hours=self.shift_hours,
                    minutes=self.shift_minutes,
                    seconds=self.shift_seconds,
                )
                if self.time_option == "Forward":
                    date = date + self.date_shift
                else:
                    date = date - self.date_shift
            except ValueError:
                messagebox.showinfo(message="Shift values need to be at least 0.", title="Error")

        # Ask database for event using the date
        event_list = self.db.get_event(date)
        subevent_list = self.db.get_event(date, 1)
        if len(event_list) == 0:
            self.meta_info.text_queue.put(f"No matching event found for file: {file}.\n")
            return
        elif len(event_list) > 1:
            self.meta_info.text_queue.put(f"To many matching events found for file: {file}.\n")
            return

        # TODO
        # print(event_list)
        # print(event_list[0])
        # print(event_list[0][0])

        # Check if year folder for this file exists
        year_dir = join(target_dir, str(date.year))
        try:
            if not os.path.exists(year_dir):
                os.mkdir(year_dir)
        except OSError:
            messagebox.showinfo(
                message="Creation of the directory %s failed" % year_dir, title="Error"
            )

        # Get sub event if exists
        sub_event = subevent_list[0] if len(subevent_list) > 0 else None
        # Get event folder
        event_dir = join(year_dir, self.get_new_foldername(event_list[0], sub_event))
        # Check if event folder for this file exists
        try:
            if not os.path.exists(event_dir):
                os.mkdir(event_dir)
        except OSError:
            messagebox.showinfo(
                message="Creation of the directory %s failed" % event_dir, title="Error"
            )

        # Rename file with the defined template
        new_name = self.get_new_filename(date, event_dir)
        new_name_ext = self.get_new_filename(date, event_dir) + file_extension

        if os.path.exists(os.path.join(event_dir, new_name_ext)):
            if not self.meta_info.dont_ask_again.get():
                box = MessageBox(
                    title="Warning: Filename already taken!",
                    message="Override file? Adding number to name otherwise.",
                    meta_info=self.meta_info,
                )
                self.confirm = box.choice
            if not self.confirm:
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

                # If enabled search for a matching raw file
                if self.process_raw > 0:
                    # Check for a matching raw file
                    raw_file_path = os.path.join(source_dir, orig_file_name + ".RAW")
                    if os.path.exists(raw_file_path):
                        # Copy the raw file with the new name and add it to the raw_list
                        shutil.copy2(raw_file_path, join(event_dir, new_name + ".RAW"))
                        self.raw_list.append(orig_file_name + ".RAW")
            else:
                # Move file to the correct folder
                shutil.move(join(source_dir, file), join(event_dir, new_name_ext))
                self.meta_info.text_queue.put(f"Moved file: {file}. New Name: {new_name_ext}.\n")

                # If enabled search for a matching raw file
                if self.process_raw > 0:
                    # Check for a matching raw file
                    raw_file_path = os.path.join(source_dir, orig_file_name + ".RAW")
                    if os.path.exists(raw_file_path):
                        # Copy the raw file with the new name and add it to the raw_list
                        shutil.move(raw_file_path, join(event_dir, new_name + ".RAW"))
                        self.raw_list.append(orig_file_name + ".RAW")

        except OSError:
            messagebox.showinfo(message="Movement of file %s failed" % file, title="Error")

        if file_extension == ".jpg" and self.modify_meta > 0:
            event_name = event_list[0][0]
            if len(subevent_list) == 1:
                event_name += " " + subevent_list[0][0]

            self.modify_metadata_piexif(join(event_dir, new_name_ext), event_name)
            # self.modify_metadata_pyexiv2(join(event_dir, new_name_ext), event_name)
            # self.modify_metadata_exif(join(event_dir, new_name_ext), event_name)
            # self.modify_metadata_pil(join(event_dir, new_name_ext), event_name)

    # https://www.w3schools.com/python/python_regex.asp#search
    def get_file_info(self, file, source_dir, file_extension, fallback=0):
        """
        Obtains the creation date of the image by either accessing the meta data,
        or using the filename to parse the correct date.
        It is possible to specify which approach should be used,
        while using the other one as fallback if the first one does not succeed.
        """
        date = False

        # Check if meta data should be used
        if (self.in_signature == "IMG-Meta-Info" and fallback == 0) or fallback == META:
            # Check if the file has metadata that can be parsed
            # TODO add support for .mp4 exif
            if file_extension == ".jpg":
                try:
                    exif_dict = piexif.load(join(source_dir, file))
                    # https://www.ffsf.de/threads/exif-datetimeoriginal-oder-datetimedigitized.9913/
                    # TODO what if time not present? return False
                    time = exif_dict["Exif"][piexif.ExifIFD.DateTimeOriginal]
                    val = str(time, "ascii")
                    date = datetime.datetime.strptime(val, "%Y:%m:%d %H:%M:%S")
                    # Check if millisecounds are present and parse them if so
                    if piexif.ExifIFD.SubSecTimeOriginal in exif_dict["Exif"]:
                        ms = exif_dict["Exif"][piexif.ExifIFD.SubSecTimeOriginal]
                        val += "." + str(ms, "ascii")
                        date = datetime.datetime.strptime(val, "%Y:%m:%d %H:%M:%S.%f")
                # TODO which exceptions?
                except FileNotFoundError:
                    self.meta_info.text_queue.put(f"File {file} could not be found.\n")
                except KeyError:
                    self.meta_info.text_queue.put(f"Metadata not readable for file: {file}.\n")
                except ValueError:
                    self.meta_info.text_queue.put(f"Time data not readable for file: {file}.\n")

            else:
                self.meta_info.text_queue.put(
                    f"Unsupported! Could not read metadata for file: {file}.\n"
                )
                if self.fallback_sig and fallback == 0:
                    self.meta_info.text_queue.put(f"Invoking fallback (Name) for file: {file}.\n")
                    date = self.get_file_info(file, source_dir, file_extension, NAME)

        # Since the file has no metadata the filename is used
        elif (self.in_signature == "IMG-File-Name" and fallback == 0) or fallback == NAME:
            regex_list = self.meta_info.get_signature_regex()
            regex_num_list = self.meta_info.get_num_signature_regex()
            strptime_list = self.meta_info.get_signature_strptime()
            assert len(regex_list) == len(strptime_list)

            for regex, regex_num, strptime in zip(regex_list, regex_num_list, strptime_list):
                if re.search(regex_num, file) is not None:
                    file = file.rsplit("_", 1)[0] + file_extension

                if re.search(regex, file) is not None:
                    try:
                        date = datetime.datetime.strptime(file, strptime + file_extension)
                    except ValueError:
                        self.meta_info.text_queue.put(
                            f"Time data not readable for file: {file}.\n"
                        )
                    return date

            # If this is reached no matching signature was found
            self.meta_info.text_queue.put(
                f"Unsupported! Name signature not found for file: {file}.\n"
            )
            if self.fallback_sig and fallback == 0:
                date = self.get_file_info(file, source_dir, file_extension, META)
                self.meta_info.text_queue.put(f"Invoking fallback (Metadata) for file: {file}.\n")

        return date

    def get_new_foldername(self, event, subevent):
        event_name = event[0]
        start_date = datetime.datetime.strptime(event[1], "%Y-%m-%d %H:%M:%S")
        end_date = datetime.datetime.strptime(event[2], "%Y-%m-%d %H:%M:%S")

        subevent_name = ""
        if subevent is not None:
            start_date = datetime.datetime.strptime(subevent[1], "%Y-%m-%d %H:%M:%S")
            end_date = datetime.datetime.strptime(subevent[2], "%Y-%m-%d %H:%M:%S")
            subevent_name = "-" + subevent[0]

        # Get date information and padd month and day with 0 if necessary
        year = str(start_date.year)
        s_month_id = str(start_date.month).zfill(2)
        e_month_id = str(end_date.month).zfill(2)

        s_day_id = str(start_date.day).zfill(2)
        e_day_id = str(end_date.day).zfill(2)

        # Create span object - used for example inside braces
        span = s_month_id + "_" + s_day_id
        if s_day_id != e_day_id or s_month_id != e_month_id:
            span = s_month_id + "_" + s_day_id + "-" + e_month_id + "_" + e_day_id

        foldername = ""
        sig = self.meta_info.get_supported_folder_signatures()

        if self.folder_signature == sig[0]:
            foldername = year + "_[" + span + "]_" + event_name + subevent_name
        elif self.folder_signature == sig[1]:
            foldername = year + "[" + span + "]_" + event_name + subevent_name
        elif self.folder_signature == sig[2]:
            foldername = "[" + year + "][" + span + "][" + event_name + subevent_name + "]"
        elif self.folder_signature == sig[3]:
            lst = span.split("-")
            center = "[" + lst[0] + "]-[" + lst[1] + "]" if len(lst) == 2 else "[" + lst[0] + "]"
            foldername = "[" + year + "]" + center + "[" + event_name + subevent_name + "]"
        elif self.folder_signature == sig[4]:
            foldername = year + "[" + span + "]" + event_name + subevent_name
        elif self.folder_signature == sig[5]:
            foldername = year + "_" + span + "_" + event_name + subevent_name
        elif self.folder_signature == sig[6]:
            foldername = year + "'" + span + "'" + event_name + subevent_name
        elif self.folder_signature == sig[7]:
            month = s_month_id if s_month_id == e_month_id else s_month_id + "-" + e_month_id
            foldername = year + "_" + month + "_" + event_name + subevent_name
        elif self.folder_signature == sig[8]:
            foldername = year + "_" + event_name + subevent_name
        elif self.folder_signature == sig[9]:
            foldername = event_name + subevent_name

        return foldername

    # https://docs.python.org/3/library/datetime.html#strftime-strptime-behavior
    def get_new_filename(self, date, event_dir):
        filename = ""
        sig = self.meta_info.get_supported_file_signatures()

        if self.file_signature == sig[0]:
            filename = date.isoformat("_", "seconds")
            filename = filename.replace(":", "-")
        elif self.file_signature == sig[1]:
            filename = date.isoformat("_", "milliseconds")
            filename = filename.replace(":", "-")
        elif self.file_signature == sig[2]:
            filename = date.strftime("%Y%m%d_%H%M%S")
        elif self.file_signature == sig[3]:
            filename = date.strftime("IMG_%Y%m%d_%H%M%S")
        elif self.file_signature == sig[4]:
            filename = date.ctime()
            filename = filename.replace(":", "-")
        else:
            number = str(
                len(
                    [
                        name
                        for name in os.listdir(event_dir)
                        if os.path.isfile(join(event_dir, name))
                    ]
                )
                + 1
            )
            filename = date.strftime("%m-%B-%d_") + number

        return filename

    def modify_metadata_piexif(self, file_with_path, title=""):
        """
        Use piexif to load the exif metadata from the image
        and store it in the copy by using insert.
        This method prevents the image data from being decompressed and potentially altered.
        Documentation: https://github.com/hMatoba/Piexif
        Source: https://stackoverflow.com/questions/53543549/
        Since piexif is only sparsely maintained
        an alternate function is implemented using pyexiv2.
        """
        try:
            exif_dict = piexif.load(file_with_path)

            if piexif.ImageIFD.ImageDescription not in exif_dict["0th"]:
                # Add a whitespace infront of every upper letter
                t = re.sub(r"(\w)([A-Z])", r"\1 \2", title)
                exif_dict["0th"][piexif.ImageIFD.ImageDescription] = t

            if (
                piexif.ImageIFD.Artist not in exif_dict["0th"]
                or len((exif_dict["0th"][piexif.ImageIFD.Artist]).decode("ascii")) < 1
            ):
                # Get data
                # TODO what if not present?
                make = exif_dict["0th"][piexif.ImageIFD.Make]
                model = exif_dict["0th"][piexif.ImageIFD.Model]
                # Access database to get the artist for this make and model
                artist = self.db.get_artist(str(make, "ascii"), str(model, "ascii"))
                if len(artist) == 1:
                    # TODO [0][0]
                    exif_dict["0th"][piexif.ImageIFD.Artist] = artist[0][0]

            # If enabled shift the datetime metadata
            # TODO what if the filename is used as date?
            if self.shift_timedata > 0 and piexif.ExifIFD.DateTimeOriginal in exif_dict["Exif"]:
                # Read data
                time = exif_dict["Exif"][piexif.ExifIFD.DateTimeOriginal]
                # Convert from binary to ascii string
                val = str(time, "ascii")
                # Parse string to datetime object
                date = datetime.datetime.strptime(val, "%Y:%m:%d %H:%M:%S")
                # Shift datetime
                if self.time_option == "Forward":
                    date = date + self.date_shift
                else:
                    date = date - self.date_shift
                # Create string from datetime object
                datestr = date.strftime("%Y:%m:%d %H:%M:%S")
                # Convert to binary
                datestr = datestr.encode("ascii")
                # Write back to the buffer
                exif_dict["Exif"][piexif.ExifIFD.DateTimeOriginal] = datestr

            # Write back to the file
            exif_bytes = piexif.dump(exif_dict)
            piexif.insert(exif_bytes, file_with_path)

        except FileNotFoundError:
            self.meta_info.text_queue.put(f"File {file_with_path} could not modify metadata.\n")

    def modify_metadata_pyexiv2(self, file_with_path, title=""):
        """
        This function uses pyexiv2 to modify the exif metadata.
        This method prevents the image data from being decompressed and potentially altered.
        Documentation: https://github.com/LeoHsiao1/pyexiv2
        Source: https://stackoverflow.com/questions/53543549/
        """
        try:
            with ImgMeta(  # noqa: F821 # pylint: disable=undefined-variable
                file_with_path
            ) as img_meta:

                T_KEY = "Exif.Image.ImageDescription"
                img_meta.modify_exif({T_KEY: title})

                exif = img_meta.read_exif()
                try:
                    make = exif["Exif.Image.Make"]
                    model = exif["Exif.Image.Model"]
                except KeyError:
                    raise

                artist = self.db.get_artist(make, model)
                if len(artist) == 1:
                    A_KEY = "Exif.Image.Artist"
                    img_meta.modify_exif({A_KEY: artist[0][0]})

        except FileNotFoundError:
            self.meta_info.text_queue.put(f"File {file_with_path} could not modify metadata.\n")

    def modify_metadata_exif(self, file_with_path, title=""):
        """
        This function uses exif to modify the exif metadata.
        This method prevents the image data from being decompressed and potentially altered.
        Sadly the lib is only sparsely maintained and using it might leed to corrupted data
        when adding metadata, similar to this issue: https://gitlab.com/TNThieding/exif/-/issues/68
        Therefore it is discuraged to use this function.
        Documentation: https://gitlab.com/TNThieding/exif
        """
        try:
            with open(file_with_path, "rb") as img_file:
                img = Image2(img_file)  # noqa: F821 # pylint: disable=undefined-variable

            # Add description and title
            img.image_description = title

            # Add artist information
            make = img.make
            model = img.model
            artist = self.db.get_artist(make, model)
            if len(artist) == 1:
                # TODO [0][0]
                img.artist = artist[0][0]

            # Overwrite image with modified EXIF metadata to an image file
            with open(file_with_path, "wb") as new_image_file:
                new_image_file.write(img.get_file())

        except FileNotFoundError:
            self.meta_info.text_queue.put(f"File {file_with_path} could not modify metadata.\n")

    def modify_metadata_pil(self, file_with_path, title=""):
        """
        This function uses piexif in combination with pillow to modify the exif metadata.
        Sadly the pillow lib does decompress the image
        even though we only want to change the metadata.
        Therefore it is discuraged to use this function.
        Documentation: https://pillow.readthedocs.io/en/stable/index.html
        Expl: https://towardsdatascience.com/read-and-edit-image-metadata-with-python-f635398cd991
        """
        try:
            img = Image.open(file_with_path)  # noqa: F821 # pylint: disable=undefined-variable

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

            # https://jdhao.github.io/2019/07/20/pil_jpeg_image_quality/
            img.save(
                file_with_path,
                exif=exif_bytes,
                quality="keep",
                dpi=img.info["dpi"],
                subsampling="keep",
                qtables="keep",
                icc_profile=img.info.get("icc_profile"),
                optimize=False,
            )

        except FileNotFoundError:
            self.meta_info.text_queue.put(f"File {file_with_path} could not modify metadata.\n")

    def debug_print_metadata(self, file):
        img = Image.open(file)  # noqa: F821 # pylint: disable=undefined-variable
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
