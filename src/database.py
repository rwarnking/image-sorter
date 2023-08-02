import json
import sqlite3
from collections.abc import Iterable
from datetime import datetime
from typing import Any, Literal, Union

from debug_messages import InfoCodes
from helper import test_time_frame, test_time_frame_outside, wbox

# TODO use these
EVENT_TITLE = 1
EVENT_S_DATE = 2
EVENT_E_DATE = 3
ARTIST_S_DATE = 4
ARTIST_E_DATE = 5


class Database:
    """
    A participant: participant_id, person_id, event_id, start_date, end_date
    It was decided to link to a person instead of an artist, since like this:
    1. there can be attending persons, which are not an artist
    2. it is not necessary to have N participants for a person, that
       uses multiple (N) divices
    """

    def __init__(self, path: str = "database.db"):
        """Setup database."""
        self.conn = sqlite3.connect(
            path, detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES
        )
        self.conn.execute("PRAGMA foreign_keys = 1")
        self.create_tables()
        self.conn.commit()

    def close(self):
        self.conn.close()

    def create_tables(self):
        """Creates tables for events, subevents, persons, artists & participants."""
        self.conn.execute(
            "CREATE TABLE IF NOT EXISTS events( \
            eid INTEGER PRIMARY KEY ASC, \
            title STRING, start_date TIMESTAMP, end_date TIMESTAMP)"
        )

        self.conn.execute(
            "CREATE TABLE IF NOT EXISTS subevents( \
            seid INTEGER PRIMARY KEY ASC, \
            event_id INT NOT NULL, \
            title STRING, start_date TIMESTAMP, end_date TIMESTAMP, \
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
            start_date TIMESTAMP, end_date TIMESTAMP, time_shift TEXT, \
            FOREIGN KEY (person_id) REFERENCES persons (pid) ON DELETE CASCADE ON UPDATE CASCADE)"
        )

        self.conn.execute(
            "CREATE TABLE IF NOT EXISTS participants (\
            paid INTEGER PRIMARY KEY ASC, \
            person_id INT NOT NULL, event_id INT NOT NULL, \
            start_date TIMESTAMP, end_date TIMESTAMP, \
            FOREIGN KEY (event_id) \
                REFERENCES events (eid) ON DELETE CASCADE ON UPDATE CASCADE, \
            FOREIGN KEY (person_id) \
                REFERENCES persons (pid) ON DELETE CASCADE ON UPDATE CASCADE)"
        )

    def load_from_file(self, file: str):
        """
        Read the table data from a json file.
        If the data was not parseable the GUI will show an info message.
        """
        err = False

        with open(file) as json_file:
            data = json.load(json_file)
            for person in data["persons"]:
                err |= (
                    self.insert_person_with_id(person["pid"], person["name"])
                    == InfoCodes.ADD_ERROR
                )

            for artist in data["artists"]:
                err |= (
                    self.insert_artist_with_id(
                        artist["aid"],
                        artist["person_id"],
                        artist["make"],
                        artist["model"],
                        datetime.fromisoformat(artist["start"]["date"]),
                        datetime.fromisoformat(artist["end"]["date"]),
                        artist["timeshift"]["date"],
                    )
                    == InfoCodes.ADD_ERROR
                )

            for event in data["events"]:
                err |= (
                    self.insert_event_with_id(
                        event["eid"],
                        event["title"],
                        datetime.fromisoformat(event["start"]["date"]),
                        datetime.fromisoformat(event["end"]["date"]),
                    )
                    == InfoCodes.ADD_ERROR
                )

            for subevent in data["subevents"]:
                err |= (
                    self.insert_subevent_with_id(
                        subevent["seid"],
                        subevent["event_id"],
                        subevent["title"],
                        datetime.fromisoformat(subevent["start"]["date"]),
                        datetime.fromisoformat(subevent["end"]["date"]),
                    )
                    == InfoCodes.ADD_ERROR
                )

            for participant in data["participants"]:
                err |= (
                    self.insert_participant_with_id(
                        participant["paid"],
                        participant["person_id"],
                        participant["event_id"],
                        datetime.fromisoformat(participant["start"]["date"]),
                        datetime.fromisoformat(participant["end"]["date"]),
                    )
                    == InfoCodes.ADD_ERROR
                )

        if err:
            return InfoCodes.LOAD_SUCCESS_PARTIAL
        else:
            return InfoCodes.LOAD_SUCCESS

    def save_to_file(self, file: str):
        """Save all table data to a json file."""
        json_data: dict[str, list] = {
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
                        "date": str(elem[2]),
                    },
                    "end": {
                        "date": str(elem[3]),
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
                        "date": str(elem[3]),
                    },
                    "end": {
                        "date": str(elem[4]),
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
                        "date": str(elem[3]),
                    },
                    "end": {
                        "date": str(elem[4]),
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
                        "date": str(elem[4]),
                    },
                    "end": {
                        "date": str(elem[5]),
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
        Deletes all table contents.
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
    def assert_tuple_list(self, list: tuple[Union[tuple[str, Any], tuple[str, Any, Any]], ...]):
        """Assertion function to guarantee that the the argument is a list of valid touples."""
        assert isinstance(list, Iterable), "Argument is not iterable!"
        assert len(list) > 0, "List is to short, no elements found!"
        for e in list:
            assert isinstance(e, tuple), f"Element of list ({e}) is not a tuple."
            assert len(e) == 2 or len(e) == 3, f"Element of list ({e}) is to short."
            assert e[0] != "", f"First part of list-element ({e}) is an empty string."
            assert isinstance(e[0], str), f"First part of list-element ({e}) is not a string."
            assert e[1] != "", f"Second part of list-element ({e}) is an empty string."
            assert e[1] is not None, f"Second part of list-element ({e}) is none."

    def get_setter_qmarks_vals(self, args: tuple[tuple[str, Any], ...]):
        """
        Convenience function to extract the setter, question marks and
        values from the given tuple (used for db querys).
        Example:
        [("key1", value1), ("key2", value2), ("key3", value3)]
        would result in
        setter: "key1, key2, key3"
        qmaks: "?, ?, ?"
        vals: (value1, value2, value3)
        """
        self.assert_tuple_list(args)
        setter: str = ""
        qmarks: str = ""
        vals: tuple[Union[str, datetime], ...] = ()
        for pair in args:
            if setter != "":
                setter += ", "
                qmarks += ", "
            setter += pair[0]
            qmarks += "?"
            vals += (pair[1],)
        return setter, qmarks, vals

    def get_where_and_vals(self, args: tuple[Union[tuple[str, Any], tuple[str, Any, Any]], ...]):
        """
        Convenience function to extract the where and values from the given tuple (for db querys).
        Example:
        [("key1", value1), ("key2", value2), ("key3", value3)]
        would result in
        where: "key1=? AND key2=? AND key3=?"
        vals: (value1, value2, value3)
        """
        self.assert_tuple_list(args)
        where: str = ""
        vals: tuple[Union[str, datetime], ...] = ()
        for pair in args:
            if where != "":
                where += "AND "
            where += pair[0] + "=? "
            vals += (pair[1],)

        return where, vals

    def get_setter(self, args: tuple[tuple[str, Any, Any], ...]):
        """
        Convenience function to extract the setter and values from the given tuple (for db querys).
        Example:
        [("key1", value1), ("key2", value2), ("key3", value3)]
        would result in
        setter: "key1, key2, key3"
        vals: (value1, value2, value3)
        """
        self.assert_tuple_list(args)
        setter: str = ""
        vals: tuple[Union[str, datetime], ...] = ()
        for pair in args:
            if setter != "":
                setter += ", "
            setter += pair[0] + "=? "
            vals += (pair[2],)
        return setter, vals

    def get_all(self, table: str):
        """Get all entries from the given table."""
        cur = self.conn.execute(f"SELECT * FROM {table}")
        result = cur.fetchall()
        cur.close()
        return result

    def get(self, table: str, *args: Union[tuple[str, Any], tuple[str, Any, Any]]):
        """Get all entries of the given table that match the via args given conditions."""
        # Extract the query components.
        where, vals = self.get_where_and_vals(args)
        assert where != ""
        assert len(vals) > 0

        query = f"SELECT * FROM {table} WHERE {where}"
        cur = self.conn.execute(query, vals)
        result = cur.fetchall()
        cur.close()
        return result

    def get_by_date(self, table: str, date: datetime, *args: tuple[str, Any]):
        """Get all elements from the table with the specified date."""
        where = "start_date<=? AND end_date>=?"
        vals = (date, date)
        if args:
            # Extract the query components.
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

    def get_by_timeframe(self, table: str, s_date: datetime, e_date: datetime):
        """Get all elements from the table with the specified date."""
        # When the elem sdate is smaller than the timeframe end date,
        # while the elem edate is bigger than the timeframe start date
        # the element is atleast partially inside the timeframe.
        where = "start_date<=? AND end_date>=?"
        vals = (e_date, s_date)

        cur = self.conn.execute(
            f"SELECT * FROM {table} WHERE {where}",
            vals,
        )
        result = cur.fetchall()
        cur.close()
        return result

    def has(
        self, table: str, *args: Union[tuple[str, Any], tuple[str, Any, Any]]
    ) -> Union[int, Literal[False]]:
        """
        This function tests the given table if it contains an element with the given attributes.
        Obviously the input must match the columns of the table.
        There are no individual table functions for checking this,
        since it is unpredictable which attributes the user might want to test against.
        For example if the function would require make and model of an artist,
        the user could not just check against the model.
        This function does allow such special cases.
        """
        result = self.get(table, *args)

        # Return the id if present
        return result[0][0] if len(result) > 0 else False

    def insert(self, table: str, *args: tuple[str, Any]):
        """Insert a new entry to the table with the attributes specified by args."""
        # Extract the query components.
        setter, qmarks, vals = self.get_setter_qmarks_vals(args)

        # If the element is not already present add
        if not self.has(table, *args):
            query = f"INSERT INTO {table} ({setter}) VALUES ({qmarks})"
            self.conn.execute(query, vals)
            self.conn.commit()
            return InfoCodes.ADD_SUCCESS
        else:
            return InfoCodes.ADD_ERROR

    def insert_ret_id(self, table: str, *args: tuple[str, Any]):
        """
        If the element is not yet present in the specified table it is added.
        In either case the id is returned.
        """
        # Extract the query components.
        setter, qmarks, vals = self.get_setter_qmarks_vals(args)

        # If the element is not already present add
        has_elem = self.has(table, *args)
        if not has_elem:
            query = f"INSERT INTO {table} ({setter}) VALUES ({qmarks})"
            cur = self.conn.execute(query, vals)
            self.conn.commit()
            return cur.lastrowid
        else:
            return has_elem

    def insert_with_id(self, table: str, *args: tuple[str, Any]):
        """
        This function adds an element to the table with the specified id.
        This should only be used, if it is important to keep the id,
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
        # Extract the query components.
        setter, qmarks, vals = self.get_setter_qmarks_vals(args)

        # If the element is already present with the same id it is not added
        if self.has(table, *args):
            return InfoCodes.ADD_ERROR

        # If the id is already taken the present element is shifted out of the way.
        if has_elem := self.has(table, args[0]):
            # Shift the element to the biggest index
            # All elements with reference to the old element are also shifted via ON UPDATE CASCADE
            count = self.get_biggest_row_id(table)
            self.update(table, (args[0][0], has_elem, count + 1))

        # If the insertion element is present in the table using a different id,
        # it should be shifted to the new one. The new id is guaranteed to be available,
        # since the potential element was shifted in the previos step.
        if has_elem := self.has(table, *args[1:]):
            # All elements with reference to the old element are also shifted via ON UPDATE CASCADE
            self.update(table, (args[0][0], has_elem, args[0][1]))
            return InfoCodes.ADD_SUCCESS_AFTER_SHIFT

        # Add the element since it is not yet in the table
        query = f"INSERT INTO {table} ({setter}) VALUES ({qmarks})"
        self.conn.execute(query, vals)
        self.conn.commit()

        return InfoCodes.ADD_SUCCESS

    def get_last_row_id(self) -> int:
        """
        Returns the id of the last row added.
        https://www.alphacodingskills.com/sqlite/notes/sqlite-func-last-insert-rowid.php
        """
        # last_insert_rowid returns (0,) when no row was inserted
        query = "SELECT last_insert_rowid()"
        cursor = self.conn.execute(query)
        # Get first element of tuple
        result = cursor.fetchone()[0]
        cursor.close()

        if result > 0:
            return result
        else:
            raise IndexError("No last row for this database connection present!")

    def get_biggest_row_id(self, table: str) -> int:
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

    def update(self, table: str, *args: tuple[str, Any, Any]):
        """
        Update the entry of the given table defined by args.
        The args should also contain the new values for the modified entry.
        """
        # Extract the query components.
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

    def delete(self, table: str, *args: tuple[str, Any]):
        """Delete the entry from the table specified by args."""
        # Extract the query components.
        where, vals = self.get_where_and_vals(args)

        if self.has(table, *args):
            query = f"DELETE FROM {table} WHERE {where}"
            self.conn.execute(query, vals)
            self.conn.commit()
            return InfoCodes.DEL_SUCCESS
        else:
            return InfoCodes.DEL_ERROR

    def clean(self, table: str):
        """Delete all entries of this database table."""
        self.conn.execute(f"DROP TABLE IF EXISTS {table}")

        # Since this is a generic function it is sadly necessary to
        # call the function to create all tables.
        # (There are no functions for creating each solo table)
        self.create_tables()

        return InfoCodes.CLEAN_SUCCESS

    def print_table(self, table: str):
        """Debugging function for printing the table contents to the console."""
        cur = self.conn.execute(f"SELECT * FROM {table}")
        res = cur.fetchall()
        cur.close()

        print(f"Table {table} is empty." if len(res) == 0 else f"Contents of table {table}:")
        for e in res:
            print(str(e))

    ###############################################################################################
    # Artist related
    ###############################################################################################
    def validate_artist(
        self,
        pid: int,
        make: str,
        model: str,
        start_date: datetime,
        end_date: datetime,
        time_shift: str,
        aid: int = 1,
    ):
        """
        Validation function to test and guarantee, that the given parameter are valid and match
        the expected input for an artist.
        """
        if not isinstance(aid, int):
            return wbox(f"Artist: A-ID {aid}, ({make}, {model}) is not an int.")
        if aid < 1:
            return wbox(f"Artist: A-ID {aid}, ({make}, {model}) smaller than 1.")
        if not isinstance(pid, int):
            return wbox(f"Artist: P-ID {pid}, ({make}, {model}) is not an int.")
        if pid < 1:
            return wbox(f"Artist: P-ID {pid}, ({make}, {model}) smaller than 1.")
        if not self.has("persons", ("pid", pid)):
            return wbox(f"Artist: Could not find person with ID {pid}, ({make}, {model}).")

        if not isinstance(make, str):
            return wbox(f"Artist: Make ({make}) is not of type string (ID: {aid}).")
        if make == "":
            return wbox(f"Artist: Make is an empty string (ID: {aid}).")

        if not isinstance(model, str):
            return wbox(f"Artist: Model ({model}) is not of type string (ID: {aid}).")
        if model == "":
            return wbox(f"Artist: Model is an empty string (ID: {aid}).")

        if not isinstance(time_shift, str):
            return wbox(f"Artist: Timeshift ({time_shift}) is not string (ID: {aid}).")
        if time_shift == "":
            return wbox(f"Artist: Timeshift is an empty string (ID: {aid}).")

        if not isinstance(start_date, datetime):
            return wbox(f"Artist: Start date ({start_date}) is not datetime (ID: {aid}).")
        if not isinstance(end_date, datetime):
            return wbox(f"Artist: End date ({end_date}) is not datetime (ID: {aid}).")
        if start_date > end_date:
            return wbox(f"Artist: End date ({end_date}) > start date ({start_date}).")

        return InfoCodes.VAL_SUCCESS

    def insert_artist(
        self,
        pid: int,
        make: str,
        model: str,
        start_date: datetime,
        end_date: datetime,
        time_shift: str,
    ):
        """Add an artist to the database table using the given data."""
        if (
            self.validate_artist(pid, make, model, start_date, end_date, time_shift)
            == InfoCodes.VAL_ERROR
        ):
            return InfoCodes.ADD_ERROR

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
        self,
        aid: int,
        pid: int,
        make: str,
        model: str,
        start_date: datetime,
        end_date: datetime,
        time_shift: str,
    ):
        """
        Add an artist to the database table using the given data and a specific ID.
        Only use this function if it is import to have a specific ID.
        """
        if (
            self.validate_artist(pid, make, model, start_date, end_date, time_shift, aid)
            == InfoCodes.VAL_ERROR
        ):
            return InfoCodes.ADD_ERROR

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
        person_id: int,
        make: str,
        model: str,
        s_date: datetime,
        e_date: datetime,
        time_shift: str,
        n_person_id: int,
        n_make: str,
        n_model: str,
        n_s_date: datetime,
        n_e_date: datetime,
        n_time_shift: str,
    ):
        """
        Wrapper function to update an artist. The given arguments specify the attributes
        of the artist that shall be updated and how its new values look like.
        """
        if (
            self.validate_artist(person_id, make, model, s_date, e_date, time_shift)
            == InfoCodes.VAL_ERROR
        ):
            return InfoCodes.MOD_ERROR
        if (
            self.validate_artist(n_person_id, n_make, n_model, n_s_date, n_e_date, n_time_shift)
            == InfoCodes.VAL_ERROR
        ):
            return InfoCodes.MOD_ERROR

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

    def delete_artist(
        self,
        person_id: int,
        make: str,
        model: str,
        s_date: datetime,
        e_date: datetime,
        time_shift: str,
    ):
        """Delete the specified artist."""
        if (
            self.validate_artist(person_id, make, model, s_date, e_date, time_shift)
            == InfoCodes.VAL_ERROR
        ):
            return InfoCodes.DEL_ERROR

        return self.delete(
            "artists",
            ("person_id", person_id),
            ("make", make),
            ("model", model),
            ("start_date", s_date),
            ("end_date", e_date),
            ("time_shift", time_shift),
        )

    def delete_artist_s(
        self, person_id: int, make: str, model: str, s_date_s: str, e_date_s: str, time_shift: str
    ):
        """Delete the specified artist using strings as dateinformation."""
        s_date = datetime.fromisoformat(s_date_s)
        e_date = datetime.fromisoformat(e_date_s)
        return self.delete_artist(person_id, make, model, s_date, e_date, time_shift)

    def test_artist_time_frame(
        self,
        artist_id: int,
        person_id: int,
        make: str,
        model: str,
        start_date: datetime,
        end_date: datetime,
    ):
        """
        Test the timeframe of an artist against the timeframes of
        each identical artist in the database.
        If this is only an artist update, the artist id is used to skip
        the timeframe of this artist which is already present in the database.

        Does not check against time_frame_swap, since this should be done beforehand.
        The time_shift is not needed, since it should only be applied to the images,
        not the time frames.
        """
        if (
            self.validate_artist(
                person_id, make, model, start_date, end_date, "_", artist_id if artist_id else 1
            )
            == InfoCodes.VAL_ERROR
        ):
            return None

        for artist in self.get(
            "artists", ("person_id", person_id), ("make", make), ("model", model)
        ):
            # Do not test against itself
            if artist_id == artist[0]:
                continue

            if err := test_time_frame(artist[4], artist[5], start_date, end_date):
                return err
        return None

    def print_artists(self):
        self.print_table("artists")

    ###############################################################################################
    # Person related
    ###############################################################################################
    def validate_person(self, name: str, pid: int = 1):
        """
        Validation function to test and guarantee, that the given parameter are valid and match
        the expected input for a person.
        """
        if not isinstance(pid, int):
            return wbox(f"Person ID ({pid}, Name: {name}) is not an int.")
        if pid < 1:
            return wbox(f"Person ID ({pid}, Name: {name}) smaller than 1.")
        if not isinstance(name, str):
            return wbox(f"Name ({name}) is not of type string (ID: {pid}).")
        if name == "":
            return wbox(f"Name is an empty string (ID: {pid}).")

        return InfoCodes.VAL_SUCCESS

    def insert_person(self, name: str):
        """Add a person to the database table using the given data."""
        if self.validate_person(name) == InfoCodes.VAL_ERROR:
            return InfoCodes.ADD_ERROR

        return self.insert("persons", ("name", name))

    def insert_person_with_id(self, pid: int, name: str):
        """
        Add a person to the database table using the given data and a specific ID.
        Only use this function if it is import to have a specific ID.
        """
        if self.validate_person(name, pid) == InfoCodes.VAL_ERROR:
            return InfoCodes.ADD_ERROR

        return self.insert_with_id("persons", ("pid", pid), ("name", name))

    def update_person(self, name: str, n_name: str):
        """
        Wrapper function to update a person. The given argument specifies the name
        of the person that shall be updated and what its new name is.
        """
        if self.validate_person(name) == InfoCodes.VAL_ERROR:
            return InfoCodes.MOD_ERROR
        if self.validate_person(n_name) == InfoCodes.VAL_ERROR:
            return InfoCodes.MOD_ERROR

        return self.update("persons", ("name", name, n_name))

    def get_pname(self, id: int) -> str:
        """Returns the name of the participant that has the given id."""
        res = self.get("persons", ("pid", id))
        assert len(res) > 0
        assert len(res[0]) > 0
        return res[0][1]

    def delete_person(self, name: str):
        """Delete the specified event."""
        if self.validate_person(name) == InfoCodes.VAL_ERROR:
            return InfoCodes.DEL_ERROR

        return self.delete("persons", ("name", name))

    def print_persons(self):
        self.print_table("persons")

    ###############################################################################################
    # Event related
    ###############################################################################################
    def validate_event(self, title: str, start_date: datetime, end_date: datetime, eid: int = 1):
        """
        Validation function to test and guarantee, that the given parameter are valid and match
        the expected input for an event.
        """
        if not isinstance(eid, int):
            return wbox(f"Event ID ({eid}, Title: {title}) is not an int.")
        if eid < 1:
            return wbox(f"Event ID ({eid}, Title: {title}) smaller than 1.")
        if not isinstance(title, str):
            return wbox(f"Title ({title}) is not of type string (ID: {eid}).")
        if title == "":
            return wbox(f"Title is an empty string (ID: {eid}).")
        if not isinstance(start_date, datetime):
            return wbox(f"Start date ({start_date}) is not of type datetime (ID: {eid}).")
        if not isinstance(end_date, datetime):
            return wbox(f"End date ({end_date}) is not of type datetime (ID: {eid}).")
        if start_date > end_date:
            return wbox(f"End date ({end_date}) starts before start date ({start_date}).")

        return InfoCodes.VAL_SUCCESS

    def insert_event(self, title: str, start_date: datetime, end_date: datetime):
        """Add an event to the database table using the given data."""
        if self.validate_event(title, start_date, end_date) == InfoCodes.VAL_ERROR:
            return InfoCodes.ADD_ERROR

        return self.insert(
            "events",
            ("title", title),
            ("start_date", start_date),
            ("end_date", end_date),
        )

    def insert_event_with_id(self, eid: int, title: str, start_date: datetime, end_date: datetime):
        """
        Add an event to the database table using the given data and a specific ID.
        Only use this function if it is import to have a specific ID.
        """
        if self.validate_event(title, start_date, end_date, eid) == InfoCodes.VAL_ERROR:
            return InfoCodes.ADD_ERROR

        return self.insert_with_id(
            "events",
            ("eid", eid),
            ("title", title),
            ("start_date", start_date),
            ("end_date", end_date),
        )

    def update_event(
        self,
        title: str,
        s_date: datetime,
        e_date: datetime,
        n_title: str,
        n_s_date: datetime,
        n_e_date: datetime,
    ):
        """
        Wrapper function to update an event. The given arguments specify the attributes
        of the event that shall be updated and how its new values look like.
        """
        if self.validate_event(title, s_date, e_date) == InfoCodes.VAL_ERROR:
            return InfoCodes.MOD_ERROR
        if self.validate_event(n_title, n_s_date, n_e_date) == InfoCodes.VAL_ERROR:
            return InfoCodes.MOD_ERROR

        return self.update(
            "events",
            ("title", title, n_title),
            ("start_date", s_date, n_s_date),
            ("end_date", e_date, n_e_date),
        )

    def delete_event(self, title: str, s_date: datetime, e_date: datetime):
        """
        Delete the specified event.
        Its subevents and participants are automatically deleted too.
        """
        if self.validate_event(title, s_date, e_date) == InfoCodes.VAL_ERROR:
            return InfoCodes.DEL_ERROR

        return self.delete(
            "events", ("title", title), ("start_date", s_date), ("end_date", e_date)
        )

    def delete_event_s(self, title: str, s_date_s: str, e_date_s: str):
        """
        Delete the specified event, using strings as date information.
        Its subevents and participants are automatically deleted too.
        """
        s_date = datetime.fromisoformat(s_date_s)
        e_date = datetime.fromisoformat(e_date_s)
        return self.delete_event(title, s_date, e_date)

    def print_events(self):
        self.print_table("events")

    ###############################################################################################
    # Subevent related
    ###############################################################################################
    def validate_subevent(
        self, event_id: int, title: str, start_date: datetime, end_date: datetime, seid: int = 1
    ):
        """
        Validation function to test and guarantee, that the given parameter are valid and match
        the expected input for a subevent.
        """
        if not isinstance(seid, int):
            return wbox(f"Subevent ({seid}, {title}): SE-ID is not an int.")
        if seid < 1:
            return wbox(f"Subevent ({seid}, {title}): SE-ID smaller than 1.")
        if not isinstance(event_id, int):
            return wbox(f"Subevent ({seid}, {title}): E-ID is not an int.")
        if event_id < 1:
            return wbox(f"Subevent ({seid}, {title}): E-ID smaller than 1.")
        if not self.has("events", ("eid", event_id)):
            return wbox(f"Subevent ({seid}, {title}): Could not find event with ID.")

        if not isinstance(title, str):
            return wbox(f"Subevent ({seid}, {title}): Title is not of type string.")
        if title == "":
            return wbox(f"Subevent ({seid}, {title}): Title is an empty string.")

        if not isinstance(start_date, datetime):
            return wbox(f"Subevent ({seid}, {title}): Start date is not of type datetime.")
        if not isinstance(end_date, datetime):
            return wbox(f"Subevent ({seid}, {title}): End date is not of type datetime.")
        if start_date > end_date:
            return wbox(f"Subevent ({seid}, {title}): End date begins before start date.")

        event = self.get("events", ("eid", event_id))[0]
        if test_time_frame_outside(event[2], event[3], start_date, end_date) is not None:
            return wbox(f"Subevent ({seid}, {title}): Timeframe does not match parent event.")

        return InfoCodes.VAL_SUCCESS

    def insert_subevent(self, event_id: int, title: str, start_date: datetime, end_date: datetime):
        """Add a subevent to the database table using the given data."""
        if self.validate_subevent(event_id, title, start_date, end_date) == InfoCodes.VAL_ERROR:
            return InfoCodes.ADD_ERROR

        return self.insert(
            "subevents",
            ("event_id", event_id),
            ("title", title),
            ("start_date", start_date),
            ("end_date", end_date),
        )

    def insert_subevent_with_id(
        self, seid: int, event_id: int, title: str, start_date: datetime, end_date: datetime
    ):
        """
        Add a subevent to the database table using the given data and a specific ID.
        Only use this function if it is import to have a specific ID.
        """
        if self.validate_subevent(event_id, title, start_date, end_date) == InfoCodes.VAL_ERROR:
            return InfoCodes.ADD_ERROR

        return self.insert_with_id(
            "subevents",
            ("seid", seid),
            ("event_id", event_id),
            ("title", title),
            ("start_date", start_date),
            ("end_date", end_date),
        )

    def update_subevent(
        self,
        event_id: int,
        title: str,
        s_date: datetime,
        e_date: datetime,
        n_title: str,
        n_s_date: datetime,
        n_e_date: datetime,
    ):
        """
        OBACHT: unused function
        Wrapper function to update a subevent. The given arguments specify the attributes
        of the subevent that shall be updated and how its new values look like.
        """
        if self.validate_subevent(event_id, title, s_date, e_date) == InfoCodes.VAL_ERROR:
            return InfoCodes.MOD_ERROR
        if self.validate_subevent(event_id, n_title, n_s_date, n_e_date) == InfoCodes.VAL_ERROR:
            return InfoCodes.MOD_ERROR

        return self.update(
            "subevents",
            ("event_id", event_id, event_id),
            ("title", title, n_title),
            ("start_date", s_date, n_s_date),
            ("end_date", e_date, n_e_date),
        )

    def delete_subevent(self, event_id: int, title: str, s_date: datetime, e_date: datetime):
        """
        OBACHT: unused function
        Delete the specified subevent.
        """
        if self.validate_subevent(event_id, title, s_date, e_date) == InfoCodes.VAL_ERROR:
            return InfoCodes.DEL_ERROR

        return self.delete(
            "subevents",
            ("event_id", event_id),
            ("title", title),
            ("start_date", s_date),
            ("end_date", e_date),
        )

    def print_subevents(self):
        self.print_table("subevents")

    ###############################################################################################
    # Participant related
    ###############################################################################################
    def validate_participant(
        self,
        person_id: int,
        event_id: int,
        start_date: datetime,
        end_date: datetime,
        paid: int = 1,
    ):
        """
        Validation function to test and guarantee, that the given parameter are valid and match
        the expected input for a participant.
        """
        if not isinstance(paid, int):
            return wbox(f"Participant ({paid}, {person_id}): PA-ID is not an int.")
        if paid < 1:
            return wbox(f"Participant ({paid}, {person_id}): PA-ID smaller than 1.")
        if not isinstance(person_id, int):
            return wbox(f"Participant ({paid}, {person_id}): P-ID is not an int.")
        if person_id < 1:
            return wbox(f"Participant ({paid}, {person_id}): P-ID smaller than 1.")
        if not self.has("persons", ("pid", person_id)):
            return wbox(f"Participant ({paid}, {person_id}): Could not find person with ID.")
        if not isinstance(event_id, int):
            return wbox(f"Participant ({paid}, {person_id}): E-ID is not an int.")
        if event_id < 1:
            return wbox(f"Participant ({paid}, {person_id}): E-ID smaller than 1.")
        if not self.has("events", ("eid", event_id)):
            return wbox(f"Participant ({paid}, {person_id}): Could not find event with ID.")

        if not isinstance(start_date, datetime):
            return wbox(f"Participant ({paid}, {person_id}): Start date is not of type datetime.")
        if not isinstance(end_date, datetime):
            return wbox(f"Participant ({paid}, {person_id}): End date is not of type datetime.")
        if start_date > end_date:
            return wbox(f"Participant ({paid}, {person_id}): End date begins before start date.")

        event = self.get("events", ("eid", event_id))[0]
        if test_time_frame_outside(event[2], event[3], start_date, end_date) is not None:
            return wbox(f"Participant ({paid}, {person_id}): Timeframe doesnt match parent event.")

        return InfoCodes.VAL_SUCCESS

    def insert_participant(
        self, person_id: int, event_id: int, start_date: datetime, end_date: datetime
    ):
        """Add a participant to the database table using the given data."""
        if (
            self.validate_participant(person_id, event_id, start_date, end_date)
            == InfoCodes.VAL_ERROR
        ):
            return InfoCodes.ADD_ERROR

        return self.insert(
            "participants",
            ("person_id", person_id),
            ("event_id", event_id),
            ("start_date", start_date),
            ("end_date", end_date),
        )

    def insert_participant_with_id(
        self, paid: int, person_id: int, event_id: int, start_date: datetime, end_date: datetime
    ):
        """
        Add a participant to the database table using the given data and a specific ID.
        Only use this function if it is import to have a specific ID.
        """
        if (
            self.validate_participant(person_id, event_id, start_date, end_date, paid)
            == InfoCodes.VAL_ERROR
        ):
            return InfoCodes.ADD_ERROR

        return self.insert_with_id(
            "participants",
            ("paid", paid),
            ("person_id", person_id),
            ("event_id", event_id),
            ("start_date", start_date),
            ("end_date", end_date),
        )

    def update_participant(
        self,
        person_id: int,
        event_id: int,
        s_date: datetime,
        e_date: datetime,
        n_s_date: datetime,
        n_e_date: datetime,
    ):
        """
        OBACHT: unused function
        Wrapper function to update a participant. The given arguments specify the attributes
        of the participant that shall be updated and how its new values look like.
        """
        if self.validate_participant(person_id, event_id, s_date, e_date) == InfoCodes.VAL_ERROR:
            return InfoCodes.MOD_ERROR
        if (
            self.validate_participant(person_id, event_id, n_s_date, n_e_date)
            == InfoCodes.VAL_ERROR
        ):
            return InfoCodes.MOD_ERROR

        return self.update(
            "participants",
            ("person_id", person_id, person_id),
            ("event_id", event_id, event_id),
            ("start_date", s_date, n_s_date),
            ("end_date", e_date, n_e_date),
        )

    def delete_participant(
        self, person_id: int, event_id: int, start_date: datetime, end_date: datetime
    ):
        """
        OBACHT: unused function
        Delete the specified participant.
        """
        if (
            self.validate_participant(person_id, event_id, start_date, end_date)
            == InfoCodes.VAL_ERROR
        ):
            return InfoCodes.DEL_ERROR

        return self.delete(
            "persons",
            ("event_id", event_id),
            ("person_id", person_id),
            ("start_date", start_date),
            ("end_date", end_date),
        )

    def test_participant_time_frame(self, name: str, start_date: datetime, end_date: datetime):
        """
        Test the timeframe of the particiapnt against the timeframes of each participant
        with the same name in the database.

        Does not check against time_frame_swap, since this should be done beforehand.
        """
        if person_id := self.has("persons", ("name", name)):
            for part in self.get("participants", ("person_id", person_id)):
                if err := test_time_frame(part[3], part[4], start_date, end_date):
                    return err

            return None
        else:
            raise ValueError(f"Person with name {name} could not found!")

    def print_participants(self):
        self.print_table("participants")
