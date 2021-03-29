# https://realpython.com/python-application-layouts/
# https://realpython.com/python-modules-packages/
# https://github.com/navdeep-G/samplemod
# https://stackoverflow.com/questions/16981921/relative-imports-in-python-3
import pathmagic  # noqa isort:skip

import os
import unittest
from tkinter import Tk

from database import Database
from meta_information import MetaInformation
from sorter import Sorter


class TestSort(unittest.TestCase):
    def test_run(self):
        TEST_DIR = os.path.dirname(os.path.abspath(__file__))

        # load database
        self.db = Database()
        self.db.insert_events(TEST_DIR + "/events.json")
        self.db.insert_artists(TEST_DIR + "/artists.json")

        self.sort(TEST_DIR)

        # Check dirs
        self.assertTrue(os.path.exists(TEST_DIR + "/2020"))
        self.assertTrue(os.path.exists(TEST_DIR + "/2020/07_Juli"))
        # self.assertTrue(t_u.test_success(TEST_DIR, test_num))

    def sort(self, TEST_DIR: str):
        Tk()
        # Set the meta_info data
        meta_info = MetaInformation()
        meta_info.set_dirs(TEST_DIR)
        meta_info.source_dir.set(TEST_DIR + "/test_images")
        meta_info.finished = False

        # Run the sort process
        s = Sorter(meta_info)
        s.run()

        while not meta_info.text_queue.empty():
            print(meta_info.text_queue.get(0))
