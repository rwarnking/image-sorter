import datetime
import json
import sqlite3
from re import sub
from tkinter import END
from typing import Dict, List, Tuple, Union

from debug_messages import InfoCodes
from helper import test_time_frame
from collections.abc import Iterable


class Database:
    """
    A participant: participant_id, person_id, event_id, start_date, end_date
    It was decided to link to a person instead of an artist, since like this:
    1. there can be attending persons, which are not an artist
    2. it is not necessary to have N participants for a person, that 
       uses multiple (N) divices
    """
    def __init__(self, path: str = "database.db"):
        self.conn = sqlite3.connect(path)
        self.conn.execute("PRAGMA foreign_keys = 1")
        self.create_tables()
        self.conn.commit()

    def create_tables(self):
        self.conn.execute(
            "CREATE TABLE IF NOT EXISTS events( \
            eid INTEGER PRIMARY KEY ASC, \
            title STRING, start_date DATE, end_date DATE)"
        )

        self.conn.execute(
            "CREATE TABLE IF NOT EXISTS subevents( \
            seid INTEGER PRIMARY KEY ASC, \
            event_id INT NOT NULL, \
            title STRING, start_date DATE, end_date DATE, \
            FOREIGN KEY (event_id) \
                REFERENCES events (eid) ON DELETE CASCADE ON UPDATE CASCADE)"
        )

        self.conn.execute(
            "CREATE TABLE IF NOT EXISTS persons (pid INTEGER PRIMARY KEY ASC, name STRING)"
        )

        self.conn.execute(
            "CREATE TABLE IF NOT EXISTS artists(\
            aid INTEGER PRIMARY KEY ASC, \
            person_id INT, make TEXT, model TEXT, \
            start_date DATE, end_date DATE, time_shift TEXT, \
            FOREIGN KEY (person_id) REFERENCES persons (pid) ON DELETE CASCADE ON UPDATE CASCADE)"
        )

        self.conn.execute("CREATE TABLE IF NOT EXISTS participants (\
            paid INTEGER PRIMARY KEY ASC, \
            person_id INT NOT NULL, event_id INT NOT NULL, \
            start_date DATE, end_date DATE, \
            FOREIGN KEY (event_id) \
                REFERENCES events (eid) ON DELETE CASCADE ON UPDATE CASCADE, \
            FOREIGN KEY (person_id) \
                REFERENCES persons (pid) ON DELETE CASCADE ON UPDATE CASCADE)"
        )

    def load_from_file(self, file):
        """
        Add tables from a file.
        """
        with open(file) as json_file:
            data = json.load(json_file)
            for person in data["persons"]:
                self.insert_person_with_id(person["pid"], person["name"])
            
            for artist in data["artists"]:
                self.insert_artist_with_id(
                    artist["aid"],
                    artist["person_id"],
                    artist["make"],
                    artist["model"],
                    datetime.datetime.strptime(artist["start"]["date"], "%Y-%m-%d %H:%M:%S"),
                    datetime.datetime.strptime(artist["end"]["date"], "%Y-%m-%d %H:%M:%S"),
                    artist["timeshift"]["date"],
                )

            for event in data["events"]:
                self.insert_event_with_id(
                    event["eid"],
                    event["title"],
                    datetime.datetime.strptime(event["start"]["date"], "%Y-%m-%d %H:%M:%S"),
                    datetime.datetime.strptime(event["end"]["date"], "%Y-%m-%d %H:%M:%S"),
                )

            for subevent in data["subevents"]:
                self.insert_subevent_with_id(
                    subevent["seid"],
                    subevent["event_id"],
                    subevent["title"],
                    datetime.datetime.strptime(subevent["start"]["date"], "%Y-%m-%d %H:%M:%S"),
                    datetime.datetime.strptime(subevent["end"]["date"], "%Y-%m-%d %H:%M:%S"),
                )
            
            for participant in data["participants"]:
                self.insert_participant_with_id(
                    participant["paid"],
                    participant["person_id"],
                    participant["event_id"],
                    datetime.datetime.strptime(participant["start"]["date"], "%Y-%m-%d %H:%M:%S"),
                    datetime.datetime.strptime(participant["end"]["date"], "%Y-%m-%d %H:%M:%S"),
                )
        return InfoCodes.LOAD_SUCCESS            

    def save_to_file(self, file):
        """
        Save all tables to a file.
        """
        json_data: Dict[str, List] = {
            "events": [],
            "subevents": [],
            "participants": [],
            "artists": [],
            "persons": [],
        }

        data = self.get_all("events")
        for elem in data:
            json_data["events"].append(
                {
                    "eid": elem[0],
                    "title": elem[1],
                    "start": {
                        "date": elem[2],
                    },
                    "end": {
                        "date": elem[3],
                    },
                }
            )

        data = self.get_all("subevents")
        for elem in data:
            json_data["subevents"].append(
                {
                    "seid": elem[0],
                    "event_id": elem[1],
                    "title": elem[2],
                    "start": {
                        "date": elem[3],
                    },
                    "end": {
                        "date": elem[4],
                    },
                }
            )
    
        data = self.get_all("participants")
        for elem in data:
            json_data["participants"].append(
                {
                    "paid": elem[0],
                    "person_id": elem[1],
                    "event_id": elem[2],
                    "start": {
                        "date": elem[3],
                    },
                    "end": {
                        "date": elem[4],
                    },
                }
            )

        data = self.get_all("artists")
        for elem in data:
            json_data["artists"].append(
                {
                    "aid": elem[0],
                    "person_id": elem[1],
                    "make": elem[2],
                    "model": elem[3],
                    "start": {
                        "date": elem[4],
                    },
                    "end": {
                        "date": elem[5],
                    },
                    "timeshift": {
                        "date": elem[6],
                    },
                }
            )
        
        data = self.get_all("persons")
        for elem in data:
            json_data["persons"].append(
                {
                    "pid": elem[0],
                    "name": elem[1],
                }
            )

        with open(file, "w") as outfile:
            json.dump(json_data, outfile, indent=4)
        return InfoCodes.SAVE_SUCCESS

    def clean_all(self):
        """
        OBACHT: Unused
        """
        self.clean("events")
        self.clean("artists")
        self.clean("persons")
        self.clean("participants")
        self.clean("subevents")

        return InfoCodes.CLEAN_ALL_SUCCESS

    ###############################################################################################
    # Generell functions
    ###############################################################################################
    def assert_tuple_list(self, list):
        """
        Assertion function to guarantee that the the argument is a list of valid touples.
        """
        assert isinstance(list, Iterable), "Argument is not iterable!"
        assert len(list) > 0, "List is to short, no elements found!"
        for e in list:
            assert isinstance(e, Tuple), f"Element of list ({e}) is not a tuple."
            assert len(e) == 2 or len(e) == 3, f"Element of list ({e}) is to short."
            assert e[0] != "", f"First part of list-element ({e}) is an empty string."
            assert isinstance(e[0], str), f"First part of list-element ({e}) is not a string."
            assert e[1] != "", f"Second part of list-element ({e}) is an empty string."
            assert e[1] is not None, f"Second part of list-element ({e}) is none."

    def get_setter_qmarks_vals(self, args: Tuple[Tuple[str, ...], ...]):
        self.assert_tuple_list(args)
        setter: str = ""
        qmarks: str = ""
        vals: Tuple[Union[str, datetime.datetime], ...] = ()
        for pair in args:
            if setter != "":
                setter += ", "
                qmarks += ", "
            setter += pair[0]
            qmarks += "?"
            vals += (pair[1],)
        return setter, qmarks, vals

    def get_where_and_vals(self, args: Tuple[Tuple[str, ...], ...]):
        self.assert_tuple_list(args)
        where: str = ""
        vals: Tuple[Union[str, datetime.datetime], ...] = ()
        for pair in args:
            if where != "":
                where += "AND "
            where += pair[0] + "=? "
            vals += (pair[1],)

        return where, vals

    def get_setter(self, args: Tuple[Tuple[str, ...], ...]):
        self.assert_tuple_list(args)
        setter: str = ""
        vals: Tuple[Union[str, datetime.datetime], ...] = ()
        for pair in args:
            if setter != "":
                setter += ", "
            setter += pair[0] + "=? "
            vals += (pair[2],)
        return setter, vals

    def get_all(self, table: str):
        cur = self.conn.execute(f"SELECT * FROM {table}")
        result = cur.fetchall()
        cur.close()
        return result

    def get(self, table: str, *args: Tuple[str, str]):
        where, vals = self.get_where_and_vals(args)
        assert where != ""
        assert len(vals) > 0

        query = f"SELECT * FROM {table} WHERE {where}"
        cur = self.conn.execute(query, vals)
        result = cur.fetchall()
        cur.close()
        return result

    def get_by_date(self, table: str, date: datetime.datetime, *args):
        """
        Get all elements from the table with the specified date.
        """
        where = "start_date<=? AND end_date>=?"
        vals = (date, date)
        if args:
            opt_where, opt_vals = self.get_where_and_vals(args)
            where += " AND " + opt_where
            vals += opt_vals

        cur = self.conn.execute(
            f"SELECT * FROM {table} WHERE {where}",
            vals,
        )
        result = cur.fetchall()
        cur.close()
        return result

    def has(self, table: str, *args: Tuple[str, ...]) -> bool:
        """
        This function test the given table if it contains an element
        with the given attributes. Obviously the input must match the
        columns of the table.
        There are no individual table functions for checking this,
        since it is unpredictable which attributes the user might want
        to test against. For example if the function would require
        make and model of an artist, the user could not just check against
        the model. This function does allow such special cases.
        """
        result = self.get(table, *args)

        # Return the id if present
        return result[0][0] if len(result) > 0 else False

    def insert(self, table: str, *args: Tuple[str, ...]):
        setter, qmarks, vals = self.get_setter_qmarks_vals(args)

        # If the element is not already present add
        if not self.has(table, *args):
            query = f"INSERT INTO {table} ({setter}) VALUES ({qmarks})"
            self.conn.execute(query, vals)
            self.conn.commit()
            return InfoCodes.ADD_SUCCESS
        else:
            return InfoCodes.ADD_ERROR

    def insert_with_id(self, table: str, *args: Tuple[str, ...]):
        """
        This function adds an element to the table with the specified id.
        This should only be used, if the it is important to keep the id,
        for example when the user has predefinied data which reuses the id.
        In case the user wants to load a complete database from a file,
        this would be the case, since there are already references between
        the different elements.

        Steps of the function:
        1. Check wether an identical element is already present, in which case nothing happens.
        2. Check wether the id is already taken by another element.
           In this case the present element is shifted to another id,
           and all its references must also be adjusted.
        3. Check wether the element is present using a different id.
           In this case the element is shifted to the new id,
           which is guaranteed to be unused since we would have shifted it in 2 otherwise.
           All the present references to the old id must also be shifted.
        4. Lastly the element is added.

        Currently this function is only used for loading from a file.
        Other use is discuraged.
        """
        setter, qmarks, vals = self.get_setter_qmarks_vals(args)

        # If the element is already present with the same id it is not added
        if self.has(table, *args):
            return InfoCodes.ADD_ERROR

        # If the id is already taken the present element is shifted out of the way.
        if has_elem:= self.has(table, args[0]):
            # Shift the element to the biggest index
            # All elements with reference to the old element are also shifted via ON UPDATE CASCADE
            count = self.get_biggest_row_id(table)
            self.update(table, (args[0][0], has_elem, count + 1))

        # If the insertion element is present in the table using a different id,
        # it should be shifted to the new one. The new id is guaranteed to be available,
        # since the potential element was shifted in the previos step.
        if has_elem:= self.has(table, *args[1:]):
            # All elements with reference to the old element are also shifted via ON UPDATE CASCADE
            self.update(table, (args[0][0], has_elem, args[0][1]))
            return InfoCodes.ADD_SUCCESS_AFTER_SHIFT

        # Add the element since it is not yet in the table
        query = f"INSERT INTO {table} ({setter}) VALUES ({qmarks})"
        self.conn.execute(query, vals)
        self.conn.commit()

        return InfoCodes.ADD_SUCCESS

    def get_last_row_id(self):
        """
        https://www.alphacodingskills.com/sqlite/notes/sqlite-func-last-insert-rowid.php
        """
        # last_insert_rowid returns (0,) when no row was inserted
        query = f"SELECT last_insert_rowid()"
        cursor = self.conn.execute(query)
        # Get first element of tuple
        result = cursor.fetchone()[0]
        cursor.close()

        if result > 0:
            return result
        else:
            raise IndexError("No last row for this database connection present!")

    def get_biggest_row_id(self, table):
        """
        Returns the biggest index available for the table.
        OBACHT: It is not possible to just use the length of the table for this,
        since the user could add 3 elements and delete one,
        then the table would be two long and the resulting index 3, 
        but the needed index is 4.
        https://stackoverflow.com/questions/23742208/fetch-the-last-row-of-a-cursor-with-sqlite
        """
        query = f"SELECT * FROM {table} ORDER BY 1 DESC LIMIT 1"
        cursor = self.conn.execute(query)
        result = cursor.fetchone()
        cursor.close()

        if result:
            # Get first element of tuple
            return result[0]
        else:
            raise IndexError("No last row for this database connection present!")

    # TODO one to one doublicate of insert function
    def get_has_or_insert(self, table: str, *args: Tuple[str, ...]):
        setter, qmarks, vals = self.get_setter_qmarks_vals(args)

        # If the element is not already present add
        has_elem = self.has(table, *args)
        if not has_elem:
            query = f"INSERT INTO {table} ({setter}) VALUES ({qmarks})"
            cur = self.conn.execute(query, vals)
            self.conn.commit()
            return True, cur.lastrowid
        else:
            return False, has_elem

    def update(self, table: str, *args: Tuple[str, ...]):
        where, vals1 = self.get_where_and_vals(args)
        setter, vals2 = self.get_setter(args)
        vals = vals2 + vals1

        if self.has(table, *args):
            query = f"UPDATE {table} SET {setter} WHERE {where}"
            self.conn.execute(query, vals)
            self.conn.commit()
            return InfoCodes.MOD_SUCCESS
        else:
            return InfoCodes.MOD_ERROR

    def delete(self, table: str, *args: Tuple[str, str]):
        where, vals = self.get_where_and_vals(args)

        if self.has(table, *args):
            query = f"DELETE FROM {table} WHERE {where}"
            self.conn.execute(query, vals)
            self.conn.commit()
            return InfoCodes.DEL_SUCCESS
        else:
            return InfoCodes.DEL_ERROR

    def clean(self, table):
        """
        Delete all entries of this database table.
        """
        self.conn.execute(f"DROP TABLE IF EXISTS {table}")

        # Since this is a generic function it is sadly necessary to
        # call the function to create all tables.
        # (There are no function for creating each solo table)
        self.create_tables()

        return InfoCodes.CLEAN_SUCCESS

    def print_table(self, table: str):
        """
        Debugging function for printing the table contents to the console.
        """
        cur = self.conn.execute(f"SELECT * FROM {table}")
        res = cur.fetchall()
        cur.close()

        print(f"Table {table} is empty." if len(res) == 0 else f"Contents of table {table}:")
        for e in res:
            print(str(e))

    ###############################################################################################
    # Artist related
    ###############################################################################################
    def assert_artist(
        self, pid: int, make: str, model: str, start_date, end_date, time_shift: str, aid: int = 1
    ):
        assert aid > 0, f"Artist id ({aid}) smaller than 1 or not an int."
        assert pid > 0, f"Person id ({pid}) smaller than 1 or not an int."
        assert self.has("persons", ("pid", pid)), f"Could not find person: {pid}."
        assert make != "", f"Make is an empty string."
        assert isinstance(make, str), f"Make ({make}) is not of type string."
        assert model != "", f"Model is an empty string."
        assert isinstance(model, str), f"Model ({model}) is not of type string."
        assert time_shift != "", f"Timeshift is an empty string."
        assert isinstance(time_shift, str), f"Timeshift ({time_shift}) is not of type string."
        assert start_date < end_date, f"End date ({end_date}) < start date ({start_date})!"

    def insert_artist(
        self, pid: int, make: str, model: str, start_date, end_date, time_shift: str
    ):
        self.assert_artist(pid, make, model, start_date, end_date, time_shift)

        return self.insert(
            "artists",
            ("person_id", pid),
            ("make", make),
            ("model", model),
            ("start_date", start_date),
            ("end_date", end_date),
            ("time_shift", time_shift),
        )

    def insert_artist_with_id(
        self, aid: int, pid: int, make: str, model: str, start_date, end_date, time_shift: str
    ):
        self.assert_artist(pid, make, model, start_date, end_date, time_shift, aid)

        return self.insert_with_id(
            "artists",
            ("aid", aid),
            ("person_id", pid),
            ("make", make),
            ("model", model),
            ("start_date", start_date),
            ("end_date", end_date),
            ("time_shift", time_shift),
        )

    def update_artist(
            self,
            person_id: int, make: str, model: str, s_date, e_date, time_shift: str,
            n_person_id: int, n_make: str, n_model: str, n_s_date, n_e_date, n_time_shift: str,
        ):
        """
        Wrapper function to update an artist. The given arguments specify the attributes
        of the artist that shall be updated and how its new values look like.
        @return Returns a warning in case the artist was not found.
        """
        self.assert_artist(person_id, make, model, s_date, e_date, time_shift)
        self.assert_artist(n_person_id, n_make, n_model, n_s_date, n_e_date, n_time_shift)

        # Update returns a warning in case the element was not found.
        return self.update(
            "artists",
            ("person_id", person_id, n_person_id),
            ("make", make, n_make),
            ("model", model, n_model),
            ("start_date", s_date, n_s_date),
            ("end_date", e_date, n_e_date),
            ("time_shift", time_shift, n_time_shift),
        )

    def delete_artist(self, person_id: int, make: str, model: str, s_date, e_date, time_shift: str):
        """
        Delete the specified artist.
        """
        self.assert_artist(person_id, make, model, s_date, e_date, time_shift)

        return self.delete(
            "artists",
            ("person_id", person_id),
            ("make", make),
            ("model", model),
            ("start_date", s_date),
            ("end_date", e_date),
            ("time_shift", time_shift),
        )

    def test_artist_time_frame(self, artist_id: int, person_id: int, make: str, model: str, start_date, end_date):
        """
        Test the timeframe of an artist against the timeframes of each identical artist in the database.
        If this is only an artist update, the artist id is used to skip
        the timeframe of this artist which is already present in the database.

        Does not check against time_frame_swap, since this should be done beforehand.
        The time_shift is not needed, since it should only be applied to the images, not the time frames.
        """
        self.assert_artist(person_id, make, model, start_date, end_date, "_", artist_id if artist_id else 1)

        for artist in self.get("artists", ("person_id", person_id), ("make", make), ("model", model)):
            s_date = datetime.datetime.strptime(artist[4], "%Y-%m-%d %H:%M:%S")
            e_date = datetime.datetime.strptime(artist[5], "%Y-%m-%d %H:%M:%S")

            # Do not test against itself
            if artist_id == artist[0]:
                continue

            if err:= test_time_frame(s_date, e_date, start_date, end_date):
                return err
        return None

    def print_artists(self):
        self.print_table("artists")

    ###############################################################################################
    # Person related
    ###############################################################################################
    def assert_person(self, name: str, pid: int = 1):
        assert pid > 0, f"Person_id ({pid}) smaller than 1 or not an int."
        assert name != "", f"Name is an empty string."
        assert isinstance(name, str), f"Name ({name}) is not of type string."

    def insert_person(self, name: str):
        self.assert_person(name)

        return self.insert("persons", ("name", name))

    def insert_person_with_id(self, pid: int, name: str):
        self.assert_person(name, pid)

        return self.insert_with_id("persons", ("pid", pid), ("name", name))

    def update_person(self, name: str, n_name: str):
        """
        Wrapper function to update a person. The given argument specifies the name
        of the person that shall be updated and what its new name is.
        @return Returns a warning in case the person was not found.
        """
        self.assert_person(name)
        self.assert_person(n_name)

        return self.update("persons", ("name", name, n_name))

    def delete_person(self, name: str):
        """
        Delete the specified event.
        """
        self.assert_person(name)

        return self.delete("persons", ("name", name))

    def print_persons(self):
        self.print_table("persons")

    ###############################################################################################
    # Event related
    ###############################################################################################
    def assert_event(self, title: str, start_date, end_date, eid: int = 1):
        assert eid > 0, f"Event_id ({eid}) smaller than 1 or not an int."
        assert title != "", f"Title is an empty string."
        assert isinstance(title, str), f"Title ({title}) is not of type string."
        assert start_date < end_date, f"End date ({end_date}) < start date ({start_date})!"

    def insert_event(self, title: str, start_date, end_date):
        self.assert_event(title, start_date, end_date)

        return self.insert(
            "events",
            ("title", title),
            ("start_date", start_date),
            ("end_date", end_date),
        )

    def insert_event_with_id(self, eid: int, title: str, start_date, end_date):
        self.assert_event(title, start_date, end_date, eid)

        return self.insert_with_id(
            "events",
            ("eid", eid),
            ("title", title),
            ("start_date", start_date),
            ("end_date", end_date)
        )

    def update_event(self, title, s_date, e_date, n_title, n_s_date, n_e_date):
        """
        Wrapper function to update an event. The given arguments specify the attributes
        of the event that shall be updated and how its new values look like.
        @return Returns a warning in case the event was not found.
        """
        self.assert_event(title, s_date, e_date)
        self.assert_event(n_title, n_s_date, n_e_date)

        return self.update(
            "events",
            ("title", title, n_title),
            ("start_date", s_date, n_s_date),
            ("end_date", e_date, n_e_date),
        )

    def delete_event(self, title: str, s_date: str, e_date: str):
        """
        Delete the specified event.
        Its subevents and participants are automatically deleted too.
        """
        self.assert_event(title, s_date, e_date)

        return self.delete("events", ("title", title), ("start_date", s_date), ("end_date", e_date))

    def print_events(self):
        self.print_table("events")

    ###############################################################################################
    # Subevent related
    ###############################################################################################
    def assert_subevent(self, event_id: int, title: str, start_date, end_date, seid: int = 1):
        assert seid > 0, f"Subevent_id ({seid}) smaller than 1 or not an int."
        assert event_id > 0, f"Event_id ({event_id}) smaller than 1 or not an int."
        assert self.has("events", ("eid", event_id)), f"Could not find event: {event_id}."
        assert title != "", f"Title is an empty string."
        assert isinstance(title, str), f"Title ({title}) is not of type string."
        assert start_date < end_date, f"End date ({end_date}) < start date ({start_date})!"

    def insert_subevent(self, event_id: int, title: str, start_date, end_date):
        self.assert_subevent(event_id, title, start_date, end_date)

        return self.insert(
            "subevents",
            ("event_id", event_id),
            ("title", title),
            ("start_date", start_date),
            ("end_date", end_date),
        )

    def insert_subevent_with_id(self, seid: int, event_id: int, title: str, start_date, end_date):
        self.assert_subevent(event_id, title, start_date, end_date, seid)

        return self.insert_with_id(
            "subevents",
            ("seid", seid),
            ("event_id", event_id),
            ("title", title),
            ("start_date", start_date),
            ("end_date", end_date),
        )

    def update_subevent(
        self, event_id: int, title: str, s_date, e_date, n_title: str, n_s_date, n_e_date
    ):
        """
        OBACHT: unused function
        Wrapper function to update a subevent. The given arguments specify the attributes
        of the subevent that shall be updated and how its new values look like.
        @return Returns a warning in case the subevent was not found.
        """
        self.assert_subevent(event_id, title, s_date, e_date)
        self.assert_subevent(event_id, n_title, n_s_date, n_e_date)

        return self.update(
            "subevents",
            ("event_id", event_id, event_id),
            ("title", title, n_title),
            ("start_date", s_date, n_s_date),
            ("end_date", e_date, n_e_date),
        )

    def delete_subevent(self, event_id: int, title: str, s_date: str, e_date: str):
        """
        OBACHT: unused function
        Delete the specified subevent.
        """
        self.assert_subevent(event_id, title, s_date, e_date)

        return self.delete(
            "subevents",
            ("event_id", event_id),
            ("title", title),
            ("start_date", s_date),
            ("end_date", e_date),
        )

    def print_events(self):
        self.print_table("subevents")

    ###############################################################################################
    # Participant related
    ###############################################################################################
    def assert_participant(self, person_id: int, event_id: int, start_date, end_date, paid: int = 1):
        assert paid > 0, f"Participant_id ({paid}) smaller than 1 or not an int."
        assert person_id > 0, f"Person_id ({person_id}) smaller than 1 or not an int."
        assert self.has("persons", ("pid", person_id)), f"Could not find person: {person_id}."
        assert event_id > 0, f"Event_id ({event_id}) smaller than 1 or not an int."
        assert self.has("events", ("eid", event_id)), f"Could not find event_id: {event_id}."
        assert start_date < end_date, f"End date ({end_date}) < start date ({start_date})!"

    def insert_participant(self, person_id: int, event_id: int, start_date, end_date):
        self.assert_participant(person_id, event_id, start_date, end_date)

        return self.insert(
            "participants",
            ("person_id", person_id),
            ("event_id", event_id),
            ("start_date", start_date),
            ("end_date", end_date),
        )

    def insert_participant_with_id(self, paid: int, person_id: int, event_id: int, start_date, end_date):
        self.assert_participant(person_id, event_id, start_date, end_date, paid)

        return self.insert_with_id(
            "participants",
            ("paid", paid),
            ("person_id", person_id),
            ("event_id", event_id),
            ("start_date", start_date),
            ("end_date", end_date),
        )

    def update_participant(
            self, person_id: int, event_id: int, s_date, e_date, n_s_date, n_e_date
        ):
        """
        OBACHT: unused function
        Wrapper function to update a participant. The given arguments specify the attributes
        of the participant that shall be updated and how its new values look like.
        @return Returns a warning in case the participant was not found.
        """
        self.assert_participant(person_id, event_id, s_date, e_date)
        self.assert_participant(person_id, event_id, n_s_date, n_e_date)

        return self.update(
            "participants",
            ("person_id", person_id, person_id),
            ("event_id", event_id, event_id),
            ("start_date", s_date, n_s_date),
            ("end_date", e_date, n_e_date),
        )

    def delete_participant(self, person_id: int, event_id: int, start_date, end_date):
        """
        Delete the specified participant.
        OBACHT: unused function
        """
        self.assert_participant(person_id, event_id, start_date, end_date)

        return self.delete(
            "persons",
            ("event_id", event_id),
            ("person_id", person_id),
            ("start_date", start_date),
            ("end_date", end_date),
        )

    def test_participant_time_frame(self, name: str, start_date, end_date):
        """
        Test the timeframe of the particiapnt against the timeframes of each participant
        with the same name in the database.

        Does not check against time_frame_swap, since this should be done beforehand.
        """
        if person_id:= self.has("persons", ("name", name)):
            for part in self.get("participants", ("person_id", person_id)):
                s_date = datetime.datetime.strptime(part[3], "%Y-%m-%d %H:%M:%S")
                e_date = datetime.datetime.strptime(part[4], "%Y-%m-%d %H:%M:%S")

                if err:= test_time_frame(s_date, e_date, start_date, end_date):
                    return err

            return None
        else:
            raise ValueError(f"Person with name {name} could not found!")

    def print_participants(self):
        self.print_table("participants")