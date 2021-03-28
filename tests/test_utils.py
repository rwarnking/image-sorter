# https://realpython.com/python-application-layouts/
# https://realpython.com/python-modules-packages/
# https://github.com/navdeep-G/samplemod
# https://stackoverflow.com/questions/16981921/relative-imports-in-python-3
import pathmagic  # noqa isort:skip

from tkinter import Tk

from database import Database
from meta_information import MetaInformation
from sorter import Sorter


class TestUtils:
    def sort(self, TEST_DIR: str, test_num: str):
        Tk()
        meta_info = MetaInformation()
        meta_info.set_dirs(TEST_DIR)
        meta_info.source_dir.set(TEST_DIR + "/test_images")
        meta_info.finished = False

        db = Database()
        # Set the meta_info data
        db.insert_events(TEST_DIR + "/events.json"),
        db.insert_artists(TEST_DIR + "/artists.json"),

        print(TEST_DIR)

        # Run the sort process
        s = Sorter(meta_info)
        s.run()

        while not meta_info.text_queue.empty():
            print(meta_info.text_queue.get(0))

    # def test_success(self, TEST_PATH: str, test_num: str):
    #   return os.path.exists(TEST_PATH + "/2020")
