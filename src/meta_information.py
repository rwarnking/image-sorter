import queue
from os.path import isfile, join
from tkinter import BooleanVar, IntVar, StringVar


class MetaInformation:
    def __init__(self):
        self.finished = True

        self.file_count = 0
        self.file_count_max = 1

        self.modify_meta = IntVar()
        self.recursive = IntVar()
        self.recursive.set(1)
        self.copy_files = IntVar()
        self.copy_files.set(1)
        self.copy_unmatched = IntVar()
        self.copy_unmatched.set(1)
        self.process_raw = IntVar()
        self.process_raw.set(1)
        self.dont_ask_again = BooleanVar()
        self.dont_ask_again.set(False)
        self.fallback_sig = IntVar()

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

    def set_dirs(self, img_src, img_tgt, db_src, db_tgt):
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

    def get_supported_file_signatures(self):
        return [
            "YYYY-MM-DD_HH-MM-SS",
            "YYYY-MM-DD_HH-MM-SS.fff",
            "YYYYMMDD_HHMMSS",
            "IMG_YYYYMMDD_HHMMSS",
            "Day Month DD HH-MM-SS YYYY",
            "MM-Month-DD_Number",
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
        return ["IMG-Meta-Info", "IMG-File-Name"]

    # TODO remove file extension and dollar sign since there could be more information
    # in the filename which should just be ignored
    def get_signature_regex(self):
        return [
            r"^\d{4}-\d{2}-\d{2}_\d{2}-\d{2}-\d{2}(\.jpg|\.png|\.gif|\.svg|\.mp4)$",
            r"^\d{4}-\d{2}-\d{2}_\d{2}-\d{2}-\d{2}\.\d{3}(\.jpg|\.png|\.gif|\.svg|\.mp4)$",
            r"^\d{8}_\d{6}(\.jpg|\.png|\.gif|\.svg|\.mp4)$",
            r"^IMG_\d{8}_\d{6}(\.jpg|\.png|\.gif|\.svg)$",
            r"^MVI_\d{8}_\d{6}(\.mp4)$",
            r"^VID_\d{8}_\d{6}(\.mp4)$",
            r"^\w{3}\s\w{3}\s\d{2}\s\d{2}-\d{2}-\d{2}\s\d{4}(\.jpg|\.png|\.gif|\.svg|\.mp4)$",
            r"^\d{2}-\w*-\d{2}_\d{3}(\.jpg|\.png|\.gif|\.svg|\.mp4)$",
        ]

    def get_num_signature_regex(self):
        return [
            r"^\d{4}-\d{2}-\d{2}_\d{2}-\d{2}-\d{2}_\d+(\.jpg|\.png|\.gif|\.svg|\.mp4)$",
            r"^\d{4}-\d{2}-\d{2}_\d{2}-\d{2}-\d{2}\.\d{3}_\d+(\.jpg|\.png|\.gif|\.svg|\.mp4)$",
            r"^\d{8}_\d{6}_\d+(\.jpg|\.png|\.gif|\.svg|\.mp4)$",
            r"^IMG_\d{8}_\d{6}_\d+(\.jpg|\.png|\.gif|\.svg)$",
            r"^MVI_\d{8}_\d{6}_\d+(\.mp4)$",
            r"^VID_\d{8}_\d{6}_\d+(\.mp4)$",
            r"^\w{3}\s\w{3}\s\d{2}\s\d{2}-\d{2}-\d{2}\s\d{4}_\d+(\.jpg|\.png|\.gif|\.svg|\.mp4)$",
            r"^\d{2}-\w*-\d{2}_\d{3}_\d+(\.jpg|\.png|\.gif|\.svg|\.mp4)$",
        ]

    def get_signature_strptime(self):
        return [
            "%Y-%m-%d_%H-%M-%S",
            "%Y-%m-%d_%H-%M-%S.%f",
            "%Y%m%d_%H%M%S",
            "IMG_%Y%m%d_%H%M%S",
            "MVI_%Y%m%d_%H%M%S",
            "VID_%Y%m%d_%H%M%S",
            "%a %b %d %H-%M-%S %Y",
            # TODO year must be accessed somehow
            "%m-%b-%d_%f",
        ]
