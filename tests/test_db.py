import pathmagic  # noqa isort:skip

import datetime
import os
import unittest

from database import Database


class TestDB(unittest.TestCase):
    def test_run(self):
        TEST_DIR = os.path.dirname(os.path.abspath(__file__))

        self.db = Database()

        EVENT_COUNT = 4
        ARTIST_COUNT = 3

        # Check if initially empty
        self.db_empty_test("events")
        self.db_empty_test("artists")

        # Check if not empty after insert from file
        self.db.insert_events(TEST_DIR + "/events.json")
        self.db_not_empty_test("events", EVENT_COUNT)

        # Check if empty after clean
        self.db.clean_events()
        self.db_empty_test("events")

        # Check if not empty after insert from file
        self.db.insert_artists(TEST_DIR + "/artists.json")
        self.db_not_empty_test("artists", ARTIST_COUNT)

        # Check if empty after clean
        self.db.clean_artists()
        self.db_empty_test("artists")

        # Check if not empty after insert one
        start_date = datetime.date(2020, 12, 1)
        end_date = datetime.date(2020, 12, 31)
        self.db.insert_event_from_date("test_title", start_date, end_date)
        self.db_not_empty_test("events", 1)

        # Check if get elem returns correct elem
        res = self.db.get_event(2020, 12, 15)
        self.assertTrue(res[0][0] == "test_title")

        # Check if file exists after save
        self.db.save_events(TEST_DIR + "/events2.json")
        print(TEST_DIR)
        print(TEST_DIR + "/events2.json")
        self.assertTrue(os.path.exists(TEST_DIR + "/events2.json"))

        # Check if empty after clean
        self.db.delete_event("test_title")
        self.db_empty_test("events")

        # Check if not empty after insert one
        self.db.insert_artist("test_name", "test_make", "test_model")
        self.db_not_empty_test("artists", 1)

        # Check if get elem returns correct elem
        res = self.db.get_artist("test_make", "test_model")
        self.assertTrue(res[0][0] == "test_name")

        # Check if file exists after save
        self.db.save_artists(TEST_DIR + "/artists2.json")
        self.assertTrue(os.path.exists(TEST_DIR + "/artists2.json"))

        # Check if empty after clean
        self.db.delete_artist("test_name")
        self.db_empty_test("artists")

        # Check if not empty after insert from saved file
        self.db.insert_events(TEST_DIR + "/events2.json")
        self.db_not_empty_test("events", 1)

        # Check if not empty after insert from saved file
        self.db.insert_artists(TEST_DIR + "/artists2.json")
        self.db_not_empty_test("artists", 1)

    def db_not_empty_test(self, table: str, size):
        res = self.db.get_all_from_table(table)
        self.assertTrue(len(res) == size)

    def db_empty_test(self, table: str):
        res = self.db.get_all_from_table(table)
        self.assertTrue(len(res) == 0)
