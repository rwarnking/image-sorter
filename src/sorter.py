import datetime
import os
import re
import shutil
from os.path import isfile, join
from tkinter import messagebox
from typing import Any, Union

import piexif
from database import Database
from guiboxes.messagebox import MessageBox
from guiboxes.selectionbox import SelectionBox
from helper import test_time_frame_outside
from meta_information import MetaInformation

META = 1
NAME = 2


class Sorter:
    def __init__(self, meta_info: MetaInformation):
        """Setup the Sorter Object"""
        self.meta_info = meta_info
        self.confirm = False

    ###############################################################################################
    # Main
    ###############################################################################################
    def run(self):
        """
        Main function, used for starting the sorting process.
        Setups the setting information and collects all files from the source directory.
        Each file is then processed indiviudally using the process_file function.
        """
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
        self.overwrite_meta = self.meta_info.overwrite_meta.get()

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
        # Overwrite if the folder should be processed recursive
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
            self.filelist = [f for f in os.listdir(file_dir) if isfile(join(file_dir, f))]

            if len(os.listdir(file_dir)) == 0:
                messagebox.showinfo(message=f"Found empty folder: {file_dir}!", title="Error")

            # Sort file list so that the .jpg are in the front and getting processed first
            self.filelist.sort(key=lambda f: os.path.splitext(f)[1].lower() != ".jpg")

            # Iterate the files
            for idx, file in enumerate(self.filelist):
                if file is None:
                    assert self.process_samename > 0
                    continue
                self.meta_info.file_count += self.process_file(file, file_dir, target_dir, idx)

        self.meta_info.text_queue.put("Finished sorting.\n")
        self.meta_info.finished = True

    def process_file(self, f_name_cpl_old: str, src_dir: str, tgt_dir: str, file_idx: int):
        """
        This function processes the given file to either be moved or copied
        to a folder that is created using the information given by the file name or metadata.
        For this the date of the file is extracted by either parsing the filename or
        using the metadata. In case no date could be extracted the file is moved/copied
        to a misc folder. Otherwise the date is used to query the database for an event.
        Should the file be a .jpg the metadata is used to obtain information of the artist.
        With the date and artist information the event might be determined.
        Following this a subevent might also be obtained.
        Finally the new filename is generated, the folder are created and the file is moved.
        At the end the artist information is saved in the metadata if possible.

        Obacht: Some features can be disabled via the GUI.
        """
        count = 1
        event_dir = "misc"
        e_id = None
        e_title = None
        e_start = None
        e_end = None
        a_name2 = None

        # Get name and extension of file
        f_name_old, f_ext = os.path.splitext(f_name_cpl_old)
        f_ext = f_ext.lower()
        f_name_cpl_old = f_name_old + f_ext

        # Parse date from either metadata or file name
        f_date = self.get_img_date(src_dir, f_name_cpl_old, f_ext)

        # Optional TODO: Add support for other metadata like .mp4 exif
        ###########################################################################################
        # Process files with date information
        ###########################################################################################
        # If a date was parseable try to get an event with it
        if f_date is not None:
            ##################
            # JPG processing #
            ##################
            if f_ext == ".jpg":
                # Get all available file information from metadata
                a_name1, a_make, a_model = self.get_img_artist(src_dir, f_name_cpl_old)
                # Afterwards get event data
                # Also returns possible author name and image date with applied shift
                if result_e := self.get_event_by_artist(f_name_cpl_old, f_date, a_make, a_model):
                    e_id, e_title, e_start, e_end, a_name2, f_date = result_e

                    # Check that the artist did not change
                    if a_name1 and a_name1 != a_name2:
                        box = SelectionBox(
                            title="Warning: Artist names differ!",
                            message=(
                                "The artist name in the metadata did "
                                + "not match the artist name of the event."
                            ),
                            actioncall="Select artist:",
                            options=[a_name1, a_name2],
                        )
                        # Userselection: Discard event information like title and name
                        if box.choice.get() == a_name1:
                            e_title = None
                            a_name2 = a_name1
                # If it was not possible to get an event via the artist use the date
                else:
                    e_id, e_title, e_start, e_end = self.get_event_by_date(f_name_cpl_old, f_date)

            ######################
            # Non JPG processing #
            ######################
            # If the file is not a .jpg use the date to extract the event
            else:
                e_id, e_title, e_start, e_end = self.get_event_by_date(f_name_cpl_old, f_date)

            ########################################
            # Subevent search and folder creationg #
            ########################################
            # If an event was found search for a matching subevent and overwrite data accordingly
            if e_id and e_title:
                if result_se := self.get_subevent_by_dateid(f_date, e_id):
                    e_title += f" - {result_se[0]}"
                    e_start, e_end = result_se[1:3]

            # Create year folder
            self.create_folder(tgt_dir, str(f_date.year))
            tgt_dir = join(tgt_dir, str(f_date.year))

            # Overwrite event_dir if there is one
            if e_title and e_start and e_end:
                event_dir = self.get_new_foldername(e_title, e_start, e_end)
            # Otherwise the file is ignored or moved into a misc folder inside the year directory
            else:
                # TODO dopplung with get_evet_by_artist
                self.meta_info.text_queue.put(
                    f"No matching event found for file: {f_name_cpl_old}.\n"
                )
                # Do not process file when GUI option is deselected
                if self.process_unmatched == 0:
                    self.meta_info.text_queue.put("Did not move or copy file!\n")
                    return count
        ###########################################################################################
        # Process files without date information
        ###########################################################################################
        else:
            self.meta_info.text_queue.put(f"Found incompatible file: {f_name_cpl_old}.\n")
            # Do not process file when GUI option is deselected
            if self.process_unmatched == 0:
                self.meta_info.text_queue.put("Did not move or copy file!\n")
                return count

        ###########################################################################################
        # Finalization
        ###########################################################################################
        # Create event folder
        self.create_folder(tgt_dir, event_dir)

        # Do not process file when GUI option is deselected
        if self.require_artist > 0 and event_dir != "misc" and a_name2 is None:
            tgt_dir = join(tgt_dir, event_dir)
            event_dir = "no_artist"
            # Create event folder
            self.create_folder(tgt_dir, event_dir)

        # Parse the date to get the new file name. The output pattern is specified using the GUI.
        if f_date is not None:
            f_name_new, f_name_cpl_new = self.get_file_name(
                join(tgt_dir, event_dir), f_date, f_ext
            )
        else:
            f_name_new, f_name_cpl_new = f_name_old, f_name_cpl_old

        #####################
        # Move or copy file #
        #####################
        tgt_dir = join(tgt_dir, event_dir)
        self.move_or_copy_image(tgt_dir, src_dir, f_name_cpl_old, f_name_cpl_new)

        ####################################
        # Move or copy similar named files #
        ####################################
        if self.process_samename > 0 and self.file_signature != "Foldername_Number":
            # Iterate the files in the same directory
            for idx, file in enumerate(self.filelist[file_idx + 1 :]):
                if file is None:
                    continue
                # Extract file ending
                tmp_name, tmp_ext = os.path.splitext(file.lower())
                # If the file has the same name but is a different file and is not a .jpg
                if tmp_name == f_name_old.lower() and tmp_ext != ".jpg" and tmp_ext != f_ext:
                    count += 1
                    self.move_or_copy_image(tgt_dir, src_dir, file, f_name_new + tmp_ext)
                    self.filelist[file_idx + idx + 1] = None

        assert not (self.process_samename == 1 and self.file_signature == "Foldername_Number")

        ###################
        # Modify metadata #
        ###################
        # Only modifies the file in the new folder not the original
        if self.modify_meta > 0 and f_ext == ".jpg":
            meta_fields = [
                {"dict": "0th", "key": piexif.ImageIFD.ImageDescription, "value": e_title},
                {"dict": "0th", "key": piexif.ImageIFD.Artist, "value": a_name2},
                {"dict": "Exif", "key": piexif.ExifIFD.DateTimeOriginal, "value": f_date},
            ]
            self.modify_metadata_piexif(join(tgt_dir, f_name_cpl_new), meta_fields)

        return count

    def get_event_by_date(
        self, f_name_cpl_old: str, date: datetime.datetime
    ) -> Union[
        tuple[int, str, datetime.datetime, datetime.datetime], tuple[None, None, None, None]
    ]:
        """If present returns event information as a tuple for the given date."""
        # Get a list of all events using the given date
        lst_events = self.db.get_by_date("events", date)

        if len(lst_events) == 0:
            return (None, None, None, None)

        select = 0
        # Let the user select the event if more than one matched.
        # Do not process .jpg's
        if len(lst_events) > 1:
            box = SelectionBox(
                title="Warning: Multiple events match!",
                message=f"The given file ({f_name_cpl_old}) matches multiple events.",
                actioncall="Select event:",
                options=[str(i) + " | " + e[1] for i, e in enumerate(lst_events)],
            )
            select = int(box.choice.get().split(" | ")[0])

        # Order: e_id, e_title, e_start, e_end
        return lst_events[select][0:4]

    # Get subevent if present
    def get_subevent_by_dateid(
        self, date: datetime.datetime, e_id: int
    ) -> Union[None, tuple[str, datetime.datetime, datetime.datetime]]:
        """If present returns subevent information as a tuple for the given date and event id."""
        # There can only be one subevent so there is no need to manually select it
        lst_subevent = self.db.get_by_date("subevents", date, ("event_id", e_id))
        assert len(lst_subevent) < 2

        # Overwrite result if subevent exists
        if len(lst_subevent) == 1:
            # Order: se_title, se_start, se_end
            return lst_subevent[0][2:5]
        else:
            return None

    def get_event_by_artist(
        self, filename: str, date: datetime.datetime, make: str, model: str
    ) -> Union[
        tuple[int, str, datetime.datetime, datetime.datetime, str, datetime.datetime], None
    ]:
        """
        If present returns event information as a tuple for the given date & make/model information.
        For this first all artists with the correct make and model are collected.
        Using the shifted date of each artist all matching events are searched for.
        In case the an event was found it is checked if the artist participated at the event
        to the given time. If there are multiple matches a GUI selector for selection is created.
        """
        # In case one of the values is False or None
        if not (filename and date and make and model):
            self.meta_info.text_queue.put(f"No make or model data found for file: {filename}.\n")
            return None

        ########################
        # Get possible artists #
        ########################
        # List all artists, that used the right camera
        lst_artists = self.db.get("artists", ("make", make), ("model", model))
        # If there was no matching artist found, print error
        if len(lst_artists) < 1:
            self.meta_info.text_queue.put(f"No matching artist found for file: {filename}.\n")
            return None

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
            # Check if this artist matches the time frame itselft -> s_date, e_date
            if test_time_frame_outside(artist[4], artist[5], shifted_date, shifted_date):
                continue

            # Get a list of all events using the shifted date of this artist
            lst_events = self.db.get_by_date("events", shifted_date)

            # Finally the artist and event list are cross
            # referenced to reduce the pool of candidates.
            for event in lst_events:
                # Get all participants for the tested event
                # Optional TODO: might be possible to use a database join here
                lst_parts = self.db.get("participants", ("event_id", event[0]))

                for p in lst_parts:
                    # Check if pid of participant matches with the current artist
                    # Use person id for both
                    if p[1] == artist[1]:
                        # Check that the participation timeframe matches the image date
                        # -> p_s_date, p_e_date
                        if test_time_frame_outside(p[3], p[4], shifted_date, shifted_date):
                            continue

                        name = self.db.get_pname(p[1])
                        lst_final.append((event, name, shifted_date))

        # If there was no matching event and artist combo found print error
        if len(lst_final) < 1:
            self.meta_info.text_queue.put(
                f"No matching combination of artist and event found for file: {filename}.\n"
            )
            return None

        select = 0
        # If more than one artist or event is left over
        # the user need to manually select the right one.
        if len(lst_final) > 1:
            self.meta_info.text_queue.put(f"To many matching events found for file: {filename}.\n")

            box = SelectionBox(
                title="Warning: Multiple events/artists match!",
                message=f"The given file ({filename}) matches multiple event-artist combinations.",
                actioncall="Select the correct combination:",
                options=[str(i) + " | " + e[0][1] + " | " + e[1] for i, e in enumerate(lst_final)],
            )
            select = int(box.choice.get().split(" | ")[0])

        return (
            lst_final[select][0][0],  # e_id
            lst_final[select][0][1],  # e_title
            lst_final[select][0][2],  # e_start
            lst_final[select][0][3],  # e_end
            lst_final[select][1],  # name of artist
            lst_final[select][2],  # date
        )

    def create_folder(self, tgt_dir: str, folder_name: str):
        """Create the given folder in the target directory."""
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

    def get_file_name(self, event_dir: str, f_date: datetime.datetime, f_ext: str):
        """Returns the new filename with and without file extension."""
        assert event_dir
        assert f_date
        assert f_ext
        # Rename file with the defined template
        new_name = self.get_new_filename(event_dir, f_date)
        new_name_ext = new_name + f_ext

        # Check if the file already exists
        if os.path.exists(os.path.join(event_dir, new_name_ext)):
            if not self.meta_info.dont_ask_again.get():
                box = MessageBox(
                    title="Warning: Filename already taken!",
                    message="Overwrite file? Adding number to name otherwise.",
                    meta_info=self.meta_info,
                )
                self.confirm = box.choice
            if not self.confirm:
                i = 1
                new_name_ext = f"{new_name}_{i}{f_ext}"
                while os.path.exists(os.path.join(event_dir, new_name_ext)):
                    i += 1
                    new_name_ext = f"{new_name}_{i}{f_ext}"
                new_name = f"{new_name}_{i}"

        return (new_name, new_name_ext)

    def move_or_copy_image(
        self, event_dir: str, src_dir: str, name_cpl_old: str, name_cpl_new: str
    ):
        """Depending on the settings move or copy the given file with the new filename."""
        assert isfile(join(src_dir, name_cpl_old))
        try:
            if self.copy_files > 0:
                # Copy file
                shutil.copy2(join(src_dir, name_cpl_old), join(event_dir, name_cpl_new))
                self.meta_info.text_queue.put(
                    f"Copied file: {name_cpl_old} with name: {name_cpl_new}.\n"
                )
            else:
                # Move file to the correct folder
                shutil.move(join(src_dir, name_cpl_old), join(event_dir, name_cpl_new))
                self.meta_info.text_queue.put(
                    f"Moved file: {name_cpl_old}. New Name: {name_cpl_new}.\n"
                )
        except OSError:
            messagebox.showinfo(message=f"Movement of file {name_cpl_old} failed", title="Error")

    def get_img_artist(self, src_dir: str, f_name: str):
        """Collect and return the image artist information."""
        assert f_name.endswith(".jpg")
        try:
            exif_dict = piexif.load(join(src_dir, f_name))
            # If present get the artist from metadata
            a_name = self.get_exif_value(exif_dict, "0th", piexif.ImageIFD.Artist)
            # Get make and model from metadata
            a_make = self.get_exif_value(exif_dict, "0th", piexif.ImageIFD.Make)
            a_model = self.get_exif_value(exif_dict, "0th", piexif.ImageIFD.Model)
            return a_name, a_make, a_model
        except FileNotFoundError:
            self.meta_info.text_queue.put(f"File {f_name} could not be found.\n")
            return None, None, None

    def get_exif_value(self, exif_dict: dict[str, Any], dict1: str, key: int):
        """Get the value for the given exif dict/key combo."""
        if key in exif_dict[dict1]:
            val = str(exif_dict[dict1][key], "ascii").strip().strip("\x00")
            if len(val) > 0:
                return val
        return None

    def get_img_date(self, source_dir: str, file: str, file_extension: str):
        """
        Obtains the creation date of the image by either accessing the meta data,
        or using the filename to parse the correct date.
        It is possible to specify which approach should be used,
        while using the other one as fallback if the first one does not succeed.
        """
        date = None

        if self.in_signature == "Metadata, fallback: Filename":
            if not (date := self.get_img_date_by_metadata(source_dir, file, file_extension)):
                self.meta_info.text_queue.put(f"Invoking fallback (Filename) for file: {file}.\n")
                date = self.get_img_date_by_filename(file, file_extension)
        elif self.in_signature == "Filename, fallback: Metadata":
            if not (date := self.get_img_date_by_filename(file, file_extension)):
                self.meta_info.text_queue.put(f"Invoking fallback (Metadata) for file: {file}.\n")
                date = self.get_img_date_by_metadata(source_dir, file, file_extension)
        elif self.in_signature == "Metadata only":
            date = self.get_img_date_by_metadata(source_dir, file, file_extension)
        elif self.in_signature == "Filename only":
            date = self.get_img_date_by_filename(file, file_extension)

        return date

    def get_img_date_by_metadata(self, source_dir: str, file: str, file_extension: str):
        """Parse the image date from the exif metadata of the given file."""
        # Check if the file has metadata that can be parsed
        if file_extension == ".jpg":
            try:
                exif_dict = piexif.load(join(source_dir, file))
                # https://www.ffsf.de/threads/exif-datetimeoriginal-oder-datetimedigitized.9913/
                # TODO date time original does not match imgname and shown date in windows
                if piexif.ExifIFD.DateTimeOriginal in exif_dict["Exif"]:
                    time = exif_dict["Exif"][piexif.ExifIFD.DateTimeOriginal]
                    val = str(time, "ascii")
                    date = datetime.datetime.strptime(val, "%Y:%m:%d %H:%M:%S")
                    # Check if millisecounds are present and parse them if so
                    if piexif.ExifIFD.SubSecTimeOriginal in exif_dict["Exif"]:
                        ms = exif_dict["Exif"][piexif.ExifIFD.SubSecTimeOriginal]
                        val += "." + str(ms, "ascii")
                        date = datetime.datetime.strptime(val, "%Y:%m:%d %H:%M:%S.%f")
                    return date
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
        return None

    # https://www.w3schools.com/python/python_regex.asp#search
    def get_img_date_by_filename(self, file: str, file_extension: str):
        """Parse the image date from the filename of the given file."""
        regex_list = self.meta_info.get_signature_regex()
        strptime_list = self.meta_info.get_signature_strptime()
        assert len(regex_list) == len(strptime_list)

        # Test the file name against all supported regex
        # In case a valid regex was found use the strp-string to parse the date.
        for regex, strptime in zip(regex_list, strptime_list):
            # Get the match using the current regex
            if search := re.search(regex, file):
                match = search.group(1) + file_extension

                if regex == r"^\w{3}_\d{8}_\d{6}":
                    strptime = "%Y%m%d_%H%M%S"

                if strptime == "" or not isinstance(match, str):
                    return None

                try:
                    return datetime.datetime.strptime(match, strptime + file_extension)
                except ValueError:
                    self.meta_info.text_queue.put(
                        f"Time data not readable for file: \
                            {file}, {strptime}, {file_extension}.\n"
                    )
                    return None

        # If this is reached no matching signature was found
        self.meta_info.text_queue.put(
            f"Unsupported! No matching name-signature found for file: {file}.\n"
        )

        return None

    def get_new_foldername(
        self, e_title: str, e_start: datetime.datetime, e_end: datetime.datetime
    ):
        """
        Create a foldername using the given title and dates.
        Uses get_supported_folder_signatures to switch between different signatures.
        Note: e_title already consits of event and subevent title
        """
        # Replace all whitespaces to prevent spaces in path
        event_title = e_title.replace(" ", "")

        # Get date information and padd month and day with 0 if necessary
        year = str(e_start.year)
        s_month_id = str(e_start.month).zfill(2)
        e_month_id = str(e_end.month).zfill(2)

        s_day_id = str(e_start.day).zfill(2)
        e_day_id = str(e_end.day).zfill(2)

        # Create span object - used for example inside braces
        span = s_month_id + "_" + s_day_id
        if s_day_id != e_day_id or s_month_id != e_month_id:
            span = s_month_id + "_" + s_day_id + "-" + e_month_id + "_" + e_day_id

        foldername = ""
        sig = self.meta_info.get_supported_folder_signatures()

        if self.folder_signature == sig[0]:
            foldername = year + "_[" + span + "]_" + event_title
        elif self.folder_signature == sig[1]:
            foldername = year + "[" + span + "]_" + event_title
        elif self.folder_signature == sig[2]:
            foldername = "[" + year + "][" + span + "][" + event_title + "]"
        elif self.folder_signature == sig[3]:
            lst = span.split("-")
            center = "[" + lst[0] + "]-[" + lst[1] + "]" if len(lst) == 2 else "[" + lst[0] + "]"
            foldername = "[" + year + "]" + center + "[" + event_title + "]"
        elif self.folder_signature == sig[4]:
            foldername = year + "[" + span + "]" + event_title
        elif self.folder_signature == sig[5]:
            foldername = year + "_" + span + "_" + event_title
        elif self.folder_signature == sig[6]:
            foldername = year + "'" + span + "'" + event_title
        elif self.folder_signature == sig[7]:
            month = s_month_id if s_month_id == e_month_id else s_month_id + "-" + e_month_id
            foldername = year + "_" + month + "_" + event_title
        elif self.folder_signature == sig[8]:
            foldername = year + "_" + event_title
        elif self.folder_signature == sig[9]:
            foldername = event_title

        return foldername

    # https://docs.python.org/3/library/datetime.html#strftime-strptime-behavior
    def get_new_filename(self, event_dir: str, date: datetime.datetime):
        """
        Create a filename using the given and date.
        Uses get_supported_file_signatures to switch between different signatures.
        """
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
            filename = date.strftime("%a %b %d %H-%M-%S %Y")
        else:
            number = (
                len(
                    [
                        name
                        for name in os.listdir(event_dir)
                        if os.path.isfile(join(event_dir, name))
                    ]
                )
                + 1
            )
            event_dir = re.sub(r"[/\\]no_artist", "", event_dir)
            folder_name = re.split(r"[/\\]", event_dir)[-1]
            filename = f"{folder_name}_{number:03d}"

        return filename

    def modify_metadata_piexif(self, file_with_path: str, meta_fields: list[dict[str, Any]]):
        """
        Use piexif to load the exif metadata from the image
        and store it in the copy by using insert.
        This method prevents the image data from being decompressed and potentially altered.
        Documentation: https://github.com/hMatoba/Piexif
        Source: https://stackoverflow.com/questions/53543549/
        OBACHT: piexif is only sparsely maintained

        The function processes all objects in meta_fields and tries to
        assign the value to the given dict/key combo.
        """
        try:
            exif_dict = piexif.load(file_with_path)
        except FileNotFoundError:
            self.meta_info.text_queue.put(f"File {file_with_path} could not modify metadata.\n")
            return

        for elem in meta_fields:
            d = elem["dict"]
            k = elem["key"]
            v = elem["value"]

            # In case the value was None do not process it
            if not v:
                continue

            # Special case: value is a datetime object -> convert to string
            if isinstance(v, datetime.date):
                # Create string from datetime object
                v = v.strftime("%Y:%m:%d %H:%M:%S")
                # Convert to binary
                v = v.encode("ascii")
            else:
                assert isinstance(v, str)

            # how-do-you-modify-xpkeywords-using-piexif
            # https://stackoverflow.com/questions/59856199/
            if (
                k == piexif.ImageIFD.XPTitle  # For 'Titel' entry
                or k == piexif.ImageIFD.XPComment  # For 'Kommentar' entry
                or k == piexif.ImageIFD.XPSubject  # For 'Betreff' entry
            ):
                v = v.encode("utf-16le")

            if (
                self.overwrite_meta > 0
                or k not in exif_dict[d]
                or len((exif_dict[d][k]).decode("ascii")) < 1
            ):
                exif_dict[d][k] = v

            # Write back to the file
            exif_bytes = piexif.dump(exif_dict)
            piexif.insert(exif_bytes, file_with_path)
