import datetime
import os
import re
import shutil
from os.path import isfile, join
from tkinter import messagebox

import piexif
from database import Database
from messagebox import MessageBox
from helper import test_time_frame_outside

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
        self.process_unmatched = self.meta_info.process_unmatched.get()
        self.require_artist = self.meta_info.require_artist.get()
        self.process_samename = self.meta_info.process_samename.get()
        self.modify_meta = self.meta_info.modify_meta.get()

        self.in_signature = self.meta_info.in_signature.get()
        self.file_signature = self.meta_info.file_signature.get()
        self.folder_signature = self.meta_info.folder_signature.get()

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
            # Get all files in the directory
            filelist = [f for f in os.listdir(file_dir) if isfile(join(file_dir, f))]

            if len(os.listdir(file_dir)) == 0:
                messagebox.showinfo(message=f"Found empty folder: {file_dir}!", title="Error")

            # Iterate the files
            for file in filelist:
                self.meta_info.file_count += self.process_file(file, file_dir, target_dir)

        self.meta_info.text_queue.put("Finished sorting.\n")
        self.meta_info.finished = True

    def process_file(self, f_name_cpl_old: str, src_dir: str, tgt_dir: str):
        """
        Process:
        TODO
        """
        event_dir = "misc"
        e_title = None
        a_name2 = None

        # Get name and extension of file
        f_name_old, f_ext = os.path.splitext(f_name_cpl_old)
        f_ext = f_ext.lower()

        # Parse date from either metadata or file name
        f_date = self.get_img_date(src_dir, f_name_cpl_old, f_ext)

        if f_date:

            # TODO
            e_id, e_title, e_start, e_end = self.get_event_by_date(f_date)

            if f_ext == ".jpg":
                # Get all available file information from metadata
                a_name1, a_make, a_model = self.get_img_artist(src_dir, f_name_cpl_old, f_ext)
                # Afterwards get event data
                # Also returns possible author name and image date with applied shift 
                if result:= self.get_event_by_artist(f_name_cpl_old, f_date, a_make, a_model):
                    e_id, e_title, e_start, e_end, a_name2, f_date = result
                    # TODO check a_name1 == a_name2
                # Do not process file when GUI option is deselected
                elif self.require_artist > 0:
                    # Disable access to new foldername
                    e_title = None

            # TODO
            # se_title, se_start, se_end = self.get_subevent_by_dateid(f_date, e_id)

            # Create year folder
            self.create_folder(tgt_dir, str(f_date.year))
            tgt_dir = join(tgt_dir, str(f_date.year))

            # Override event_dir if there is one
            if e_title and e_start and e_end:
                event_dir = self.get_new_foldername(e_title, e_start, e_end)
            # Otherwise the file is ignored or moved into a misc folder inside the year directory
            else:
                # TODO dopplung with get_evet_by_artist
                self.meta_info.text_queue.put(f"No matching event found for file: {f_name_cpl_old}.\n")
                # Do not process file when GUI option is deselected
                if self.process_unmatched == 0:
                    self.meta_info.text_queue.put("Did not move or copy file!\n")
                    return 1
        else:
            self.meta_info.text_queue.put(f"Found incompatible file: {f_name_cpl_old}.\n")
            # Do not process file when GUI option is deselected
            if self.process_unmatched == 0:
                self.meta_info.text_queue.put("Did not move or copy file!\n")
                return 1

        # Create event folder
        self.create_folder(tgt_dir, event_dir)

        # TODO
        if f_date:
            f_name_new, f_name_cpl_new = self.get_file_name(join(tgt_dir, event_dir), f_date, f_ext)
        else:
            f_name_cpl_new = f_name_cpl_old

        # TODO In case same-name-files should be processed,
        # the filelist is searched for a file with the same name (different fileending).
        # It there is one, modify the name in the same way as the current file.
        # TODO return number of modified files 
        # if (self.process_samename > 0):
            # return count

        #####################
        # Move or copy file #
        #####################
        tgt_dir = join(tgt_dir, event_dir)
        self.move_or_copy_image(tgt_dir, src_dir, f_name_cpl_old, f_name_cpl_new)

        ###################
        # Modify metadata #
        ###################
        # Only modifies the file in the new folder not the original
        if self.modify_meta > 0 and f_ext == ".jpg" and e_title and a_name2 and f_date:
            self.modify_metadata_piexif(join(tgt_dir, f_name_cpl_new), e_title, a_name2, f_date)
            # self.modify_metadata_pyexiv2(join(event_dir, new_name_ext), event_name)
            # self.modify_metadata_exif(join(event_dir, new_name_ext), event_name)
            # self.modify_metadata_pil(join(event_dir, new_name_ext), event_name)

        return 1
    
    def get_event_by_date(self, date):
        # Get a list of all events using the given date
        lst_events = self.db.get_by_date("events", date)

        if len(lst_events) == 0:
            return (False, False, False, False)
        # TODO
        # if len(lst_events) > 0:
            # let user select

        # TODO just return lst_events[0][0:3]?
        return (
            lst_events[0][0], # e_id
            lst_events[0][1], # e_title
            lst_events[0][2], # e_start
            lst_events[0][3], # e_end
        )

    # Get subevent if present
    def get_subevent_by_dateid(self, date, e_id):
        # There can only be one subevent so there is no need to manually select it
        lst_subevent = self.db.get_by_date("subevents", date, ("event_id", e_id))
        assert(len(lst_subevent) < 2)
        # Override result if subevent exists
        if len(lst_subevent) == 1:
            # TODO just return lst_events[0][1:3]?
            return (
                lst_subevent[0][1], # se_title
                lst_subevent[0][2], # se_start
                lst_subevent[0][3], # se_end
            )
        else:
            return (None, None, None)

    # TODO rename old_name to filename
    def get_event_by_artist(self, old_name: str, date, make: str, model: str):
        # In case one of the values is False or None
        if not (old_name and date and make and model):
            return False

        ########################
        # Get possible artists #
        ########################
        # List all artists, that used the right camera
        lst_artists = self.db.get("artists", ("make", make), ("model", model))
        # If there was no matching artist found, print error
        if len(lst_artists) < 1:
            self.meta_info.text_queue.put(f"No matching artist found for file: {old_name}.\n")
            return False

        print("Artist List:")
        print(lst_artists)
        lst_final = []
        for artist in lst_artists:
            shift = artist[6].split(":")
            date_shift = datetime.timedelta(
                days=int(shift[0]),
                hours=int(shift[1]),
                minutes=int(shift[2]),
                seconds=int(shift[3]),
            )
            # Shift the image date
            shifted_date = date + date_shift
            s_date = datetime.datetime.strptime(artist[4], "%Y-%m-%d %H:%M:%S")
            e_date = datetime.datetime.strptime(artist[5], "%Y-%m-%d %H:%M:%S")

            # Check if this artist matches the time frame itselft
            if test_time_frame_outside(s_date, e_date, shifted_date, shifted_date):
                print(f"Dropped artist {artist}")
                continue

            # Get a list of all events using the shifted date of this artist 
            lst_events = self.db.get_by_date("events", shifted_date)

            print("Event list:")
            print(lst_events)

            # Finally the artist and event list are cross referenced to reduce the pool of candidates.
            # TODO rename e to event
            for e in lst_events:
                # Get all participants for the tested event
                # TODO might be possible to use a database join here
                lst_parts = self.db.get("participants", ("event_id", e[0]))
                print("Participant list")
                print(lst_parts)

                for p in lst_parts:
                    # Check if pid of participant matches with the current artist
                    # Use person id for both
                    if p[1] == artist[1]:
                        name = self.db.get("persons", ("pid", p[1]))[0][1]
                        # TODO remove artist?
                        lst_final.append((e, artist, name, shifted_date))

        print("Final list:")
        print(lst_final)

        # If there was no matching event and artist combo found print error
        if len(lst_final) < 1:
            self.meta_info.text_queue.put(
                f"No matching combination of artist and event found for file: {old_name}.\n"
            )
            return False

        final_selection = lst_final[0]
        # If more than one artist or event is left over
        # the user need to manually select the right one.
        if len(lst_final) > 1:
            self.meta_info.text_queue.put(f"To many matching events found for file: {old_name}.\n")
            return False

        print("Success!")
        print(final_selection)

        ###########################
        # Get subevent if present #
        ###########################
        # TODO remove subevent from here
        # There can only be one subevent so there is no need to manually select it
        subevent_list = self.db.get_by_date("subevents", date, ("event_id", final_selection[0][0]))
        assert(len(subevent_list) < 2)
        # Get subevent if exists
        sub_event = subevent_list[0] if len(subevent_list) > 0 else None
        print("Subevent: ", sub_event)

        # TODO substitute if subevent was found
        # if sub_event:
        #     final_selection[0] = sub_event
        return (
            final_selection[0][0], # e_id
            final_selection[0][1], # e_title
            final_selection[0][2], # e_start
            final_selection[0][3], # e_end
            final_selection[2], # name of artist
            final_selection[3], # date
        )

    def create_folder(self, tgt_dir, folder_name):
        res_dir = join(tgt_dir, folder_name)
        # Check if the folder already exists
        try:
            if not os.path.exists(res_dir):
                os.mkdir(res_dir)
        except OSError:
            messagebox.showinfo(
                message=f"Creation of the directory {res_dir} failed!", title="Error"
            )
        return res_dir

    def get_file_name(self, event_dir: str, f_date, f_ext: str):
        assert event_dir
        assert f_date
        assert f_ext
        # Rename file with the defined template
        # TODO switch parameter
        new_name = self.get_new_filename(f_date, event_dir)
        new_name_ext = self.get_new_filename(f_date, event_dir) + f_ext

        # Check if the file already exists
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
                new_name_ext = f"{new_name}_{i}{f_ext}"
                while os.path.exists(os.path.join(event_dir, new_name_ext)):
                    new_name_ext = f"{new_name}_{i}{f_ext}"
                    i += 1

        return (new_name, new_name_ext)

    def move_or_copy_image(self, event_dir, src_dir, name_cpl_old, name_cpl_new):
        try:
            if self.copy_files > 0:
                # Copy file
                shutil.copy2(join(src_dir, name_cpl_old), join(event_dir, name_cpl_new))
                self.meta_info.text_queue.put(f"Copied file: {name_cpl_old} with name: {name_cpl_new}.\n")
            else:
                # Move file to the correct folder
                shutil.move(join(src_dir, name_cpl_old), join(event_dir, name_cpl_new))
                self.meta_info.text_queue.put(f"Moved file: {name_cpl_old}. New Name: {name_cpl_new}.\n")
        except OSError:
            messagebox.showinfo(message=f"Movement of file {name_cpl_old} failed", title="Error")

    def get_img_artist(self, src_dir, f_name, f_ext):
        assert f_ext == ".jpg"
        try:
            exif_dict = piexif.load(join(src_dir, f_name))
            # If present get the artist from metadata
            a_name = self.get_exif_value(exif_dict, piexif.ImageIFD.Artist)
            # Get make and model from metadata
            a_make = self.get_exif_value(exif_dict, piexif.ImageIFD.Make)
            a_model = self.get_exif_value(exif_dict, piexif.ImageIFD.Model)
            return a_name, a_make, a_model
        except FileNotFoundError:
            self.meta_info.text_queue.put(f"File {f_name} could not be found.\n")
            return None, None, None

    # TODO custom dict param
    def get_exif_value(self, exif_dict, key):
        if (
            key in exif_dict["0th"]
            and len((exif_dict["0th"][key]).decode("ascii")) > 0
        ):
            return str(exif_dict["0th"][key], "ascii")
        else:
            return False

    def get_img_date(self, source_dir, file, file_extension, fallback=0):
        """
        Obtains the creation date of the image by either accessing the meta data,
        or using the filename to parse the correct date.
        It is possible to specify which approach should be used,
        while using the other one as fallback if the first one does not succeed.
        """
        date = False

        if (self.in_signature == "Metadata, fallback: Filename"):
            if not (date := self.get_img_date_by_metadata(source_dir, file, file_extension)):
                self.meta_info.text_queue.put(f"Invoking fallback (Filename) for file: {file}.\n")
                date = self.get_img_date_by_filename(file, file_extension)
        elif (self.in_signature == "Filename, fallback: Metadata"):
            if not (date := self.get_img_date_by_filename(file, file_extension)):
                self.meta_info.text_queue.put(f"Invoking fallback (Metadata) for file: {file}.\n")
                date = self.get_img_date_by_metadata(source_dir, file, file_extension)
        elif (self.in_signature == "Metadata only"):
            date = self.get_img_date_by_metadata(source_dir, file, file_extension)
        elif (self.in_signature == "Filename only"):
            date = self.get_img_date_by_filename(file, file_extension)

        return date
    
    def get_img_date_by_metadata(self, source_dir, file, file_extension):
        date = False

        # Check if the file has metadata that can be parsed
        # TODO add support for .mp4 exif
        if file_extension == ".jpg":
            try:
                exif_dict = piexif.load(join(source_dir, file))
                # https://www.ffsf.de/threads/exif-datetimeoriginal-oder-datetimedigitized.9913/
                # TODO date time original does not match imgname and shown date in windows
                if (piexif.ExifIFD.DateTimeOriginal in exif_dict["Exif"]):
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
        return date
    
    # https://www.w3schools.com/python/python_regex.asp#search
    def get_img_date_by_filename(self, file, file_extension):
        date = False

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
            f"Unsupported! No matching name-signature found for file: {file}.\n"
        )

        return date

    def get_new_foldername(self, e_name, e_start, e_end):
        # Replace all whitespaces to prevent spaces in path
        event_name = e_name.replace(" ", "")
        start_date = datetime.datetime.strptime(e_start, "%Y-%m-%d %H:%M:%S")
        end_date = datetime.datetime.strptime(e_end, "%Y-%m-%d %H:%M:%S")

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

        # BIG TODO
        subevent_name = ""

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

    # TODO write more general approach
    # For entry in dict
    # if key in exif_dict[dict] or overwrite
    #     exif_dict[dict][key] = data
    def modify_metadata_piexif(self, file_with_path, title, artist, date):
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
                exif_dict["0th"][piexif.ImageIFD.ImageDescription] = title

            # TODO add checkbox for overwriting meta data
            if (
                piexif.ImageIFD.Artist not in exif_dict["0th"]
                or len((exif_dict["0th"][piexif.ImageIFD.Artist]).decode("ascii")) < 1
            ):
                exif_dict["0th"][piexif.ImageIFD.Artist] = artist

            # If enabled set the datetime metadata
            if date:
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
