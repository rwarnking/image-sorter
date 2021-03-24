import queue

from tkinter import IntVar, StringVar

import config as cfg


class MetaInformation:
    def __init__(self):
        self.finished = True

        self.file_count = 0
        self.file_count_max = 1

        self.in_signature = StringVar()
        self.out_signature = StringVar()

        self.text_queue = queue.Queue()

    def set_dirs(self, dir):
        self.source_dir = StringVar()
        self.source_dir.set(dir)

        self.target_dir = StringVar()
        self.target_dir.set(dir)

    def get_supported_signatures(self):
        return [
            "YYYY-MM-DD_HH-MM-SS",
            "YYYY-MM-DD_HH-MM-SS.fff",
            "YYYYMMDD_HHMMSS",
            "IMG_YYYYMMDD_HHMMSS",
            "Day Month DD HH-MM-SS YYYY",
            "MM-Month-DD_Number",
        ]
