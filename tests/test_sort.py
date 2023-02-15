# https://realpython.com/python-application-layouts/
# https://realpython.com/python-modules-packages/
# https://github.com/navdeep-G/samplemod
# https://stackoverflow.com/questions/16981921/relative-imports-in-python-3
import pathmagic  # noqa isort:skip

import os
import shutil
import unittest
from os.path import join
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
        meta_info.set_dirs(TEST_DIR, TEST_DIR, TEST_DIR, TEST_DIR, TEST_DIR, TEST_DIR)
        meta_info.img_src.set(join(TEST_DIR, "test_images"))

        # load database
        self.db = Database()
        self.db.insert_events(join(TEST_DIR, "events.json")) # TODO
        self.db.insert_artists(join(TEST_DIR, "artists.json"))

        for idx, settings in enumerate(self.get_settings_list(meta_info)):
            print(idx)
            print(settings)
            meta_info.finished = False
            self.set_meta_info(meta_info, settings)

            # Run the sort process
            s = Sorter(meta_info)
            s.run()

            # Print subdirs in case the directory test does fail
            for x in os.walk(TEST_DIR):
                print(x[0])

            while not meta_info.text_queue.empty():
                print(meta_info.text_queue.get(0))

            # Check dirs
            self.run_checks(idx, TEST_DIR)

            # Remove created folder
            # TODO dir should be variable
            shutil.rmtree(join(TEST_DIR, "2020"))
            if os.path.exists(join(TEST_DIR, "newtext.txt")):
                os.remove(join(TEST_DIR, "newtext.txt"))
            if os.path.exists(join(TEST_DIR, "Test.jpg")):
                os.remove(join(TEST_DIR, "Test.jpg"))

    def get_settings_list(self, meta_info):
        """
        Creates a list of settings objects that should be tested.
        """
        settings = []

        # Use default settings
        obj = self.create_settings_obj(meta_info)
        settings.append(obj)

        # Enable processing .raw files
        obj = self.create_settings_obj(meta_info)
        obj["process_raw"] = 1
        settings.append(obj)

        # Use default settings with fallback signature
        obj = self.create_settings_obj(meta_info)
        obj["fallback_sig"] = 1
        settings.append(obj)

        # Enable processing .raw files, fallback signature and copy all
        obj = self.create_settings_obj(meta_info)
        obj["fallback_sig"] = 1
        obj["process_raw"] = 1
        obj["copy_unmatched"] = 1
        settings.append(obj)

        # Use a version with timeshift
        obj = self.create_settings_obj(meta_info)
        obj["shift_timedata"] = 1
        obj["shift_days"] = "1"
        obj["shift_hours"] = "1"
        obj["shift_minutes"] = "1"
        obj["shift_selection"] = "Forward"
        settings.append(obj)

        # Use a different file signature
        obj = self.create_settings_obj(meta_info)
        obj["file_signature"] = meta_info.get_supported_file_signatures()[3]
        settings.append(obj)

        # Use file movement instead of copying
        obj = self.create_settings_obj(meta_info)
        obj["copy_files"] = 0
        settings.append(obj)

        return settings

    def run_checks(self, idx, base_dir):

        src_files = [
            [  # Test source directory when using default settings
                (True, ""),
                (True, "test_images"),
                (True, join("test_images", "20200701_211534.jpg")),
                (True, join("test_images", "IMG_3113.JPG")),
                (True, join("test_images", "IMG_3113.RAW")),
                (True, join("test_images", "IMG_20200703_092850.svg")),
                (True, join("test_images", "IMG_20200703_092959.gif")),
                (True, join("test_images", "newtext.txt")),
                (True, join("test_images", "Test.jpg")),
            ],
            [  # Test source directory when also processing .raw files
                (True, ""),
                (True, "test_images"),
                (True, join("test_images", "20200701_211534.jpg")),
                (True, join("test_images", "IMG_3113.JPG")),
                (True, join("test_images", "IMG_3113.RAW")),
                (True, join("test_images", "IMG_20200703_092850.svg")),
                (True, join("test_images", "IMG_20200703_092959.gif")),
                (True, join("test_images", "newtext.txt")),
                (True, join("test_images", "Test.jpg")),
            ],
            [  # Test source directory when using fallback signature
                (True, ""),
                (True, "test_images"),
                (True, join("test_images", "20200701_211534.jpg")),
                (True, join("test_images", "IMG_3113.JPG")),
                (True, join("test_images", "IMG_3113.RAW")),
                (True, join("test_images", "IMG_20200703_092850.svg")),
                (True, join("test_images", "IMG_20200703_092959.gif")),
                (True, join("test_images", "newtext.txt")),
                (True, join("test_images", "Test.jpg")),
            ],
            [  # Test source directory when using fallback signature
                # Processing .raw files
                # Copy all
                (True, ""),
                (True, "test_images"),
                (True, join("test_images", "20200701_211534.jpg")),
                (True, join("test_images", "IMG_3113.JPG")),
                (True, join("test_images", "IMG_3113.RAW")),
                (True, join("test_images", "IMG_20200703_092850.svg")),
                (True, join("test_images", "IMG_20200703_092959.gif")),
                (True, join("test_images", "newtext.txt")),
                (True, join("test_images", "Test.jpg")),
            ],
            [  # Test source directory when using time shift settings
                (True, ""),
                (True, "test_images"),
                (True, join("test_images", "20200701_211534.jpg")),
                (True, join("test_images", "IMG_3113.JPG")),
                (True, join("test_images", "IMG_3113.RAW")),
                (True, join("test_images", "IMG_20200703_092850.svg")),
                (True, join("test_images", "IMG_20200703_092959.gif")),
                (True, join("test_images", "newtext.txt")),
                (True, join("test_images", "Test.jpg")),
            ],
            [  # Test source directory when using different image signature
                (True, ""),
                (True, "test_images"),
                (True, join("test_images", "20200701_211534.jpg")),
                (True, join("test_images", "IMG_3113.JPG")),
                (True, join("test_images", "IMG_3113.RAW")),
                (True, join("test_images", "IMG_20200703_092850.svg")),
                (True, join("test_images", "IMG_20200703_092959.gif")),
                (True, join("test_images", "newtext.txt")),
                (True, join("test_images", "Test.jpg")),
            ],
            [  # Test source directory when disabling copying
                (True, ""),
                (True, "test_images"),
                (False, join("test_images", "20200701_211534.jpg")),
                (False, join("test_images", "IMG_3113.JPG")),
                (True, join("test_images", "IMG_3113.RAW")),
                (True, join("test_images", "IMG_20200703_092850.svg")),
                (True, join("test_images", "IMG_20200703_092959.gif")),
                (True, join("test_images", "newtext.txt")),
                (True, join("test_images", "Test.jpg")),
            ],
        ]

        main_dir = "2020"
        sub_dir = "2020_[07_01-07_31]_Juli"
        compl_dir = join(main_dir, sub_dir)

        tgt_files = [
            [  # Test target directory when using default settings
                (True, main_dir),
                (True, compl_dir),
                (True, join(compl_dir, "2020-07-01_21-15-34.jpg")),
                (True, join(compl_dir, "2020-07-02_18-49-10.jpg")),
                (False, join(compl_dir, "2020-07-02_18-49-10.RAW")),
                (False, join(compl_dir, "2020-07-03_09-28-50.svg")),
                (False, join(compl_dir, "2020-07-03_09-29-59.gif")),
                (False, join(base_dir, "newtext.txt")),
                (False, join(base_dir, "Test.jpg")),
            ],
            [  # Test target directory when also processing .raw files
                (True, main_dir),
                (True, compl_dir),
                (True, join(compl_dir, "2020-07-01_21-15-34.jpg")),
                (True, join(compl_dir, "2020-07-02_18-49-10.jpg")),
                (True, join(compl_dir, "2020-07-02_18-49-10.RAW")),
                (False, join(compl_dir, "2020-07-03_09-28-50.svg")),
                (False, join(compl_dir, "2020-07-03_09-29-59.gif")),
                (False, join(base_dir, "newtext.txt")),
                (False, join(base_dir, "Test.jpg")),
            ],
            [  # Test target directory when using fallback signature
                (True, main_dir),
                (True, compl_dir),
                (True, join(compl_dir, "2020-07-01_21-15-34.jpg")),
                (True, join(compl_dir, "2020-07-02_18-49-10.jpg")),
                (False, join(compl_dir, "2020-07-02_18-49-10.RAW")),
                (True, join(compl_dir, "2020-07-03_09-28-50.svg")),
                (True, join(compl_dir, "2020-07-03_09-29-59.gif")),
                (False, join(base_dir, "newtext.txt")),
                (False, join(base_dir, "Test.jpg")),
            ],
            [  # Test source directory when using fallback signature
                # Processing .raw files
                # Copy all
                (True, main_dir),
                (True, compl_dir),
                (True, join(compl_dir, "2020-07-01_21-15-34.jpg")),
                (True, join(compl_dir, "2020-07-02_18-49-10.jpg")),
                (True, join(compl_dir, "2020-07-02_18-49-10.RAW")),
                (True, join(compl_dir, "2020-07-03_09-28-50.svg")),
                (True, join(compl_dir, "2020-07-03_09-29-59.gif")),
                (True, join(base_dir, "newtext.txt")),
                (True, join(base_dir, "Test.jpg")),
            ],
            [  # Test target directory when using time shift settings
                (True, main_dir),
                (True, compl_dir),
                (True, join(compl_dir, "2020-07-02_22-16-34.jpg")),
                (True, join(compl_dir, "2020-07-03_19-50-10.jpg")),
                (False, join(compl_dir, "2020-07-02_18-49-10.RAW")),
                (False, join(compl_dir, "2020-07-03_09-28-50.svg")),
                (False, join(compl_dir, "2020-07-03_09-29-59.gif")),
                (False, join(base_dir, "newtext.txt")),
                (False, join(base_dir, "Test.jpg")),
            ],
            [  # Test target directory when using different image signature
                (True, main_dir),
                (True, compl_dir),
                (True, join(compl_dir, "IMG_20200701_211534.jpg")),
                (True, join(compl_dir, "IMG_20200702_184910.jpg")),
                (False, join(compl_dir, "IMG_20200702_184910.RAW")),
                (False, join(compl_dir, "IMG_20200703_092850.svg")),
                (False, join(compl_dir, "IMG_20200703_092959.gif")),
                (False, join(base_dir, "newtext.txt")),
                (False, join(base_dir, "Test.jpg")),
            ],
            [  # Test target directory when disabling copying
                (True, main_dir),
                (True, compl_dir),
                (True, join(compl_dir, "2020-07-01_21-15-34.jpg")),
                (True, join(compl_dir, "2020-07-02_18-49-10.jpg")),
                (False, join(compl_dir, "2020-07-02_18-49-10.RAW")),
                (False, join(compl_dir, "2020-07-03_09-28-50.svg")),
                (False, join(compl_dir, "2020-07-03_09-29-59.gif")),
                (False, join(base_dir, "newtext.txt")),
                (False, join(base_dir, "Test.jpg")),
            ],
        ]

        for f_tuple in src_files[idx]:
            if f_tuple[0]:
                result = os.path.exists(join(base_dir, f_tuple[1]))
                print(f"Should be true, is {result}. ({base_dir}, {f_tuple[1]})")
                self.assertTrue(os.path.exists(join(base_dir, f_tuple[1])))
            else:
                result = os.path.exists(join(base_dir, f_tuple[1]))
                print(f"Should be false, is {result}. ({base_dir}, {f_tuple[1]})")
                self.assertFalse(os.path.exists(join(base_dir, f_tuple[1])))

        for f_tuple in tgt_files[idx]:
            if f_tuple[0]:
                result = os.path.exists(join(base_dir, f_tuple[1]))
                print(f"Should be true, is {result}. ({base_dir}, {f_tuple[1]})")
                self.assertTrue(os.path.exists(join(base_dir, f_tuple[1])))
            else:
                result = os.path.exists(join(base_dir, f_tuple[1]))
                print(f"Should be false, is {result}. ({base_dir}, {f_tuple[1]})")
                self.assertFalse(os.path.exists(join(base_dir, f_tuple[1])))

    def set_meta_info(self, meta_info, settings):
        meta_info.shift_timedata.set(settings["shift_timedata"])
        meta_info.modify_meta.set(settings["modify_meta"])
        meta_info.recursive.set(settings["recursive"])
        meta_info.copy_files.set(settings["copy_files"])
        meta_info.copy_unmatched.set(settings["copy_unmatched"])
        meta_info.process_raw.set(settings["process_raw"])
        meta_info.dont_ask_again.set(settings["dont_ask_again"])
        meta_info.fallback_sig.set(settings["fallback_sig"])

        meta_info.in_signature.set(settings["in_signature"])
        meta_info.file_signature.set(settings["file_signature"])
        meta_info.folder_signature.set(settings["folder_signature"])

        meta_info.shift_days.set(settings["shift_days"])
        meta_info.shift_hours.set(settings["shift_hours"])
        meta_info.shift_minutes.set(settings["shift_minutes"])
        meta_info.shift_seconds.set(settings["shift_seconds"])
        meta_info.shift_selection.set(settings["shift_selection"])

    def create_settings_obj(self, meta_info):
        obj = {
            "shift_timedata": 0,
            "modify_meta": 0,
            "recursive": 0,
            "copy_files": 1,
            "copy_unmatched": 0,
            "process_raw": 0,
            "dont_ask_again": False,
            "fallback_sig": 0,
            "in_signature": meta_info.get_read_choices()[0],
            "file_signature": meta_info.get_supported_file_signatures()[0],
            "folder_signature": meta_info.get_supported_folder_signatures()[0],
            "shift_days": "0",
            "shift_hours": "0",
            "shift_minutes": "0",
            "shift_seconds": "0",
            "shift_selection": "None",
        }
        return obj
