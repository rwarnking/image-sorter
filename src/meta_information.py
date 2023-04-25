import queue
from os.path import isfile, join
from tkinter import BooleanVar, IntVar, StringVar


class MetaInformation:
    def __init__(self):
        self.finished = True

        self.file_count = 0
        self.file_count_max = 1
        self.estimated_time_per_file_ms = 100
        self.estimated_time_ms = 0

        self.modify_meta = IntVar()
        self.modify_meta.set(1)
        self.overwrite_meta = IntVar()
        self.overwrite_meta.set(1)
        self.recursive = IntVar()
        self.recursive.set(1)
        self.copy_files = IntVar()
        self.copy_files.set(1)
        self.process_unmatched = IntVar()
        self.process_unmatched.set(1)
        self.require_artist = IntVar()
        self.require_artist.set(1)
        self.process_samename = IntVar()
        self.process_samename.set(1)
        self.dont_ask_again = BooleanVar()
        self.dont_ask_again.set(False)

        self.in_signature = StringVar()
        self.in_signature.set(self.get_read_choices()[0])
        self.file_signature = StringVar()
        self.file_signature.set(self.get_supported_file_signatures()[0])
        self.folder_signature = StringVar()
        self.folder_signature.set(self.get_supported_folder_signatures()[0])

        self.event_action = StringVar()
        self.artist_action = StringVar()

        self.event_selection = StringVar()
        self.artist_selection = StringVar()

        self.text_queue = queue.Queue()

    def set_dirs(self, img_src: str, img_tgt: str, db_src: str, db_tgt: str):
        self.img_src = StringVar()
        self.img_src.set(img_src)
        self.img_tgt = StringVar()
        self.img_tgt.set(img_tgt)

        self.sv_db_src = StringVar()
        if isfile(join(db_src, "db.json")):
            self.sv_db_src.set(join(db_src, "db.json"))
        else:
            self.sv_db_src.set("C:\\")
        self.sv_db_tgt = StringVar()
        if isfile(join(db_tgt, "db.json")):
            self.sv_db_tgt.set(join(db_tgt, "db.json"))
        else:
            self.sv_db_tgt.set("C:\\")

    # Optional TODO: IMG_ is currently used for all file types (.mp4)
    # Change to TYPE_ / EXTENSION_
    def get_supported_file_signatures(self):
        return [
            "YYYY-MM-DD_HH-MM-SS",
            "YYYY-MM-DD_HH-MM-SS.fff",
            "YYYYMMDD_HHMMSS",
            "IMG_YYYYMMDD_HHMMSS",
            "Day Month DD HH-MM-SS YYYY",
            "Foldername_Number",
        ]

    def get_supported_folder_signatures(self):
        return [
            "YYYY_[MM_DD-MM_DD]_Event-Subevent",
            "YYYY[MM_DD-MM_DD]_Event-Subevent",
            "[YYYY][MM_DD-MM_DD][Event-Subevent]",
            "[YYYY][MM_DD]-[MM_DD][Event-Subevent]",
            "YYYY[MM_DD-MM_DD]Event-Subevent",
            "YYYY_MM_DD-MM_DD_Event-Subevent",
            "YYYY'MM_DD-MM_DD'Event-Subevent",
            "YYYY_MM-MM_Event-Subevent",
            "YYYY_Event-Subevent",
            "Event-Subevent",
        ]

    def get_read_choices(self):
        return [
            "Metadata, fallback: Filename",
            "Filename, fallback: Metadata",
            "Metadata only",
            "Filename only",
        ]

    # List of regex for supported filesignatures.
    # Each regex allows for additional name information after the date,
    # but the file must start either with the date or with three charaters
    # indicating the file type e.g. IMG/MVI/VID/RAW
    def get_signature_regex(self):
        return [
            r"^(\d{4}-\d{2}-\d{2}_\d{2}-\d{2}-\d{2}\.\d{3})",
            r"^(\d{4}-\d{2}-\d{2}_\d{2}-\d{2}-\d{2})",
            r"^(\d{8}_\d{6})",
            r"^\w{3}_(\d{8}_\d{6})",
            r"^(\w{3}\s\w{3}\s\d{2}\s\d{2}-\d{2}-\d{2}\s\d{4})",
            r"^(\d{2}-\w*-\d{2}_\d{3})",
            r"^(\d{4}_\[\d{2}_\d{2}\])",
            r"^(\d{4}_\[\d{2}_\d{2})-\d{2}_\d{2}\]",
            r"^(\w{3}_\d{4})",
        ]


    def get_signature_strptime(self):
        return [
            "%Y-%m-%d_%H-%M-%S.%f",
            "%Y-%m-%d_%H-%M-%S",
            "%Y%m%d_%H%M%S",
            "%Y%m%d_%H%M%S",
            "%a %b %d %H-%M-%S %Y",
            # OBACHT: Year is not accessable
            "%m-%B-%d_%f",
            "%Y_[%m_%d]",
            "%Y_[%m_%d",
            "",
        ]

    def update_estimated_time(self, filecount: int):
        self.estimated_time_ms = filecount * self.estimated_time_per_file_ms

    def get_estimated_time_s(self):
        return (self.estimated_time_ms / 1000) % 60
    
    def get_estimated_time_m(self):
        return int((self.estimated_time_ms / 1000) / 60)
