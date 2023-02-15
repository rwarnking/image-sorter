import pathmagic  # noqa isort:skip

import datetime
import os
import unittest
from tkinter import Text, Tk

from database import Database


class TestDB(unittest.TestCase):
    def test_run(self):
        TEST_DIR = os.path.dirname(os.path.abspath(__file__))

        self.db = Database()

        table_list = [
            ("events", 3),
            ("subevents", 1),
            ("participants", 1),
            ("artists", 3),
            ("persons", 3),
        ]

        # Check if initially empty
        for table in table_list:
            self.db_empty_test(table[0])

        ####################
        # Load from file 1 #
        ####################
        # Check if not empty after insert from file
        self.db.load_from_file(TEST_DIR + "/test_dbs/db_test_1-1.json")
        for table in table_list:
            self.db_not_empty_test(table[0], table[1])

        # Check if empty after clean
        for table in table_list:
            self.db.clean(table[0])
            self.db_empty_test(table[0])

        ####################
        # Load from file 2 #
        ####################
        self.db.load_from_file(TEST_DIR + "/test_dbs/db_test_2-1.json")
        persons = self.db.get_all("persons")
        self.assertTrue(len(persons) == 1)
        self.person_test(persons[0], 1, "artist1")

        artists = self.db.get_all("artists")
        self.assertTrue(len(artists) == 1)
        self.artist_test(artists[0], 1, 1, "test_make_1", "test_model_1")

        self.db.load_from_file(TEST_DIR + "/test_dbs/db_test_2-2.json")
        persons = self.db.get_all("persons")
        self.assertTrue(len(persons) == 2)
        self.person_test(persons[0], 1, "artist2")
        self.person_test(persons[1], 2, "artist1")

        artists = self.db.get_all("artists")
        self.assertTrue(len(artists) == 2)
        self.artist_test(artists[0], 1, 1, "test_make_1", "test_model_1")
        self.artist_test(artists[1], 2, 2, "test_make_1", "test_model_1")

        for table in table_list:
            self.db.clean(table[0])
            self.db_empty_test(table[0])

        ####################
        # Load from file 3 #
        ####################
        self.db.load_from_file(TEST_DIR + "/test_dbs/db_test_3-1.json")
        persons = self.db.get_all("persons")
        self.assertTrue(len(persons) == 1)
        self.person_test(persons[0], 3, "artist1")

        artists = self.db.get_all("artists")
        self.assertTrue(len(artists) == 1)
        self.artist_test(artists[0], 1, 3, "test_make_1", "test_model_1")

        self.db.load_from_file(TEST_DIR + "/test_dbs/db_test_3-2.json")
        persons = self.db.get_all("persons")
        self.assertTrue(len(persons) == 1)
        self.person_test(persons[0], 1, "artist1")

        artists = self.db.get_all("artists")
        self.assertTrue(len(artists) == 1)
        self.artist_test(artists[0], 1, 1, "test_make_1", "test_model_1")

        self.db.load_from_file(TEST_DIR + "/test_dbs/db_test_3-3.json")
        persons = self.db.get_all("persons")
        self.assertTrue(len(persons) == 1)
        self.person_test(persons[0], 1, "artist1")

        artists = self.db.get_all("artists")
        self.assertTrue(len(artists) == 2)
        self.artist_test(artists[0], 1, 1, "test_make_2", "test_model_2")
        self.artist_test(artists[1], 2, 1, "test_make_1", "test_model_1")

        for table in table_list:
            self.db.clean(table[0])
            self.db_empty_test(table[0])

        ##########
        # Person #
        ##########
        # Check if not empty after insert one
        self.db.insert_person("test_name")
        self.db_not_empty_test("persons", 1)

        # Check if same person can be in db twice (should not)
        self.db.insert_person("test_name")
        self.db_not_empty_test("persons", 1)

        #########
        # Event #
        #########
        # Check if not empty after insert one
        start_day = datetime.date(2020, 12, 1)
        end_day = datetime.date(2020, 12, 31)
        start_hour = 0
        end_hour = 23
        start_date = datetime.datetime.combine(
            start_day, datetime.datetime.min.time()
        ) + datetime.timedelta(hours=start_hour)
        end_date = datetime.datetime.combine(
            end_day, datetime.datetime.min.time()
        ) + datetime.timedelta(hours=end_hour)
        self.db.insert_event("test_title", start_date, end_date)
        self.db_not_empty_test("events", 1)

        event_id = self.db.get(
            "events", 
            ("title", "test_title"), 
            ("start_date", start_date), 
            ("end_date", end_date)
        )[0][0]

        person_id = self.db.get("persons", ("name", "test_name"))[0][0]

        self.db.insert_subevent(event_id, "test_day1", start_date, end_date)
        self.db.insert_participant(person_id, event_id, start_date, end_date)

        # Check if get elem returns correct elem
        check_date = datetime.date(2020, 12, 15)
        res = self.db.get_by_date("events", check_date)
        self.assertTrue(res[0][1] == "test_title")

        res = self.db.get_by_date("subevents", check_date)
        self.assertTrue(res[0][1] == event_id)
        self.assertTrue(res[0][2] == "test_day1")

        res = self.db.get_by_date("participants", check_date)
        self.assertTrue(res[0][1] == person_id)
        self.assertTrue(res[0][2] == event_id)

        ################
        # Save to file #
        ################
        # Check if file exists after save
        self.db.save_to_file(TEST_DIR + "/db2.json")
        print(TEST_DIR)
        print(TEST_DIR + "/db2.json")
        self.assertTrue(os.path.exists(TEST_DIR + "/db2.json"))

        # Check if empty after clean
        self.db.delete_event("test_title", start_date, end_date)
        self.db_empty_test("events")
        self.db_empty_test("participants")
        self.db_empty_test("subevents")
        self.db_not_empty_test("persons", 1)

        ##########
        # Artist #
        ##########
        # Check if not empty after insert one
        time_shift = "0:0:0:0"
        p_id = self.db.get("persons", ("name", "test_name"))[0][0]
        self.db.insert_artist(p_id, "test_make", "test_model", start_date, end_date, time_shift)
        self.db_not_empty_test("artists", 1)

        # Check if get elem returns correct elem
        res = self.db.get("artists", ("make", "test_make"), ("model", "test_model"))
        self.assertTrue(res[0][1] == p_id)

        # Check if empty after clean
        self.db.delete_artist(p_id, "test_make", "test_model", start_date, end_date, time_shift)
        self.db_empty_test("artists")

    def person_test(self, person, pid, name):
        self.assertTrue(person[0] == pid)
        self.assertTrue(person[1] == name)

    def artist_test(self, artist, aid, pid, make, model):
        self.assertTrue(artist[0] == aid)
        self.assertTrue(artist[1] == pid)
        self.assertTrue(artist[2] == make)
        self.assertTrue(artist[3] == model)

    def db_not_empty_test(self, table: str, size):
        res = self.db.get_all(table)
        self.assertTrue(len(res) == size)

    def db_empty_test(self, table: str):
        res = self.db.get_all(table)
        self.assertTrue(len(res) == 0)
