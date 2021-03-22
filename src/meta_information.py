from tkinter import IntVar, StringVar

import config as cfg


class MetaInformation:
    def __init__(self):
        self.finished = True

        self.file_count = 0
        self.file_count_max = 1

    def set_dirs(self, dir):
        self.source_dir = StringVar()
        self.source_dir.set(dir)

        self.target_dir = StringVar()
        self.target_dir.set(dir)
