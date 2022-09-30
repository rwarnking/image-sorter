# https://realpython.com/python-application-layouts/
# https://realpython.com/python-modules-packages/
# https://github.com/navdeep-G/samplemod
# https://stackoverflow.com/questions/16981921/relative-imports-in-python-3
import pathmagic  # noqa isort:skip

import os
import shutil
import unittest
from tkinter import Text, Tk

from database import Database
from meta_information import MetaInformation
from sorter import Sorter


class TestSort(unittest.TestCase):
    def test_run(self):
        TEST_DIR = os.path.dirname(os.path.abspath(__file__))

        window = Tk()
        details_text = Text(window, width=0, height=0)

        # Set the meta_info data
        meta_info = MetaInformation()
        meta_info.set_dirs(TEST_DIR, TEST_DIR)
        meta_info.source_dir.set(TEST_DIR + "/test_images")

        # load database
        self.db = Database(details_text)
        self.db.insert_events(TEST_DIR + "/events.json")
        self.db.insert_artists(TEST_DIR + "/artists.json")

        for idx, settings in enumerate(self.get_settings_list(meta_info)):
            print(idx)
            meta_info.finished = False
            self.set_meta_info(meta_info, settings)

            # Run the sort process
            s = Sorter(meta_info)
            s.run()

            while not meta_info.text_queue.empty():
                print(meta_info.text_queue.get(0))

            # Check dirs
            self.run_checks(idx, TEST_DIR)

            # Remove created folder
            # TODO os.join here and everywhere else
            # TODO dir should be variable
            shutil.rmtree(TEST_DIR + "/2020")

    def get_settings_list(self, meta_info):
        settings = []

        obj = self.create_settings_obj(meta_info)
        settings.append(obj)

        obj = self.create_settings_obj(meta_info)
        obj["shift_timedata"] = 1
        obj["shift_days"] = "1"
        obj["shift_hours"] = "1"
        obj["shift_minutes"] = "1"
        settings.append(obj)

        obj = self.create_settings_obj(meta_info)
        obj["file_signature"] = meta_info.get_supported_file_signatures()[3]
        settings.append(obj)

        obj = self.create_settings_obj(meta_info)
        obj["copy_files"] = 0
        settings.append(obj)

        print(settings)

        return settings

    def run_checks(self, idx, TEST_DIR):
        if idx == 0:
            self.assertTrue(os.path.exists(TEST_DIR + "/2020"))
            self.assertTrue(os.path.exists(TEST_DIR + "/2020/2020_[07_01-07_31]_Juli"))
            self.assertTrue(
                os.path.exists(TEST_DIR + "/2020/2020_[07_01-07_31]_Juli/2020-07-01_21-15-34.jpg")
            )
            self.assertTrue(os.path.exists(TEST_DIR + "/test_images/20200701_211534.jpg"))
        elif idx == 1:
            self.assertTrue(os.path.exists(TEST_DIR + "/2020"))
            self.assertTrue(os.path.exists(TEST_DIR + "/2020/2020_[07_01-07_31]_Juli"))
            self.assertTrue(
                os.path.exists(TEST_DIR + "/2020/2020_[07_01-07_31]_Juli/2020-07-02_22-16-34.jpg")
            )
            self.assertTrue(os.path.exists(TEST_DIR + "/test_images/20200701_211534.jpg"))
        elif idx == 2:
            self.assertTrue(os.path.exists(TEST_DIR + "/2020"))
            self.assertTrue(os.path.exists(TEST_DIR + "/2020/2020_[07_01-07_31]_Juli"))
            self.assertTrue(
                os.path.exists(TEST_DIR + "/2020/2020_[07_01-07_31]_Juli/IMG_20200701_211534.jpg")
            )
            self.assertTrue(os.path.exists(TEST_DIR + "/test_images/20200701_211534.jpg"))
        elif idx == 3:
            self.assertTrue(os.path.exists(TEST_DIR + "/2020"))
            self.assertTrue(os.path.exists(TEST_DIR + "/2020/2020_[07_01-07_31]_Juli"))
            self.assertTrue(
                os.path.exists(TEST_DIR + "/2020/2020_[07_01-07_31]_Juli/2020-07-01_21-15-34.jpg")
            )
            self.assertFalse(os.path.exists(TEST_DIR + "/test_images/20200701_211534.jpg"))

    def set_meta_info(self, meta_info, settings):
        meta_info.shift_timedata.set(settings["shift_timedata"])
        meta_info.modify_meta.set(settings["modify_meta"])
        meta_info.recursive.set(settings["recursive"])
        meta_info.copy_files.set(settings["copy_files"])
        meta_info.fallback_sig.set(settings["fallback_sig"])

        meta_info.in_signature.set(settings["in_signature"])
        meta_info.file_signature.set(settings["file_signature"])
        meta_info.folder_signature.set(settings["folder_signature"])

        meta_info.shift_days.set(settings["shift_days"])
        meta_info.shift_hours.set(settings["shift_hours"])
        meta_info.shift_minutes.set(settings["shift_minutes"])
        meta_info.time_option.set(settings["time_option"])

    def create_settings_obj(self, meta_info):
        obj = {
            "shift_timedata": 0,
            "modify_meta": 0,
            "recursive": 0,
            "copy_files": 1,
            "fallback_sig": 0,
            "in_signature": meta_info.get_read_choices()[0],
            "file_signature": meta_info.get_supported_file_signatures()[0],
            "folder_signature": meta_info.get_supported_folder_signatures()[0],
            "shift_days": "0",
            "shift_hours": "0",
            "shift_minutes": "0",
            "time_option": "Forward",
        }
        return obj
