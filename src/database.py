import datetime
import json
import sqlite3
from re import sub
from tkinter import END
from typing import Dict, List, Tuple, Union


class Database:
    def __init__(self, path: str = "database.db"):
        self.conn = sqlite3.connect(path)
        self.conn.execute("PRAGMA foreign_keys = 1")
        self.create_tables()
        self.conn.commit()

    def set_out_text(self, out_text):
        self.out_text = out_text

    def create_tables(self):
        self.conn.execute(
            "CREATE TABLE IF NOT EXISTS events \
            (eid INTEGER PRIMARY KEY ASC, \
                title STRING, start_date DATE, end_date DATE)"
        )

        self.conn.execute(
            "CREATE TABLE IF NOT EXISTS subevents \
            (seid INTEGER PRIMARY KEY ASC, \
                title STRING, start_date DATE, end_date DATE)"
        )

        self.conn.execute(
            "CREATE TABLE IF NOT EXISTS persons (pid INTEGER PRIMARY KEY ASC, name STRING)"
        )

        self.conn.execute(
            "CREATE TABLE IF NOT EXISTS artists(\
            aid INTEGER PRIMARY KEY ASC, \
            person_id INT, make TEXT, model TEXT, \
            start_date DATE, end_date DATE, \
            FOREIGN KEY (person_id) REFERENCES persons (pid) ON DELETE CASCADE)"
        )

        self.conn.execute("CREATE TABLE IF NOT EXISTS participants (\
            paid INTEGER PRIMARY KEY ASC, \
            person_id INT NOT NULL, event_id INT NOT NULL, \
            start_date DATE, end_date DATE, \
            FOREIGN KEY (event_id) \
                REFERENCES events (eid) ON DELETE CASCADE, \
            FOREIGN KEY (person_id) \
                REFERENCES persons (pid))"
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
                    "title": elem[1],
                    "start": {
                        "date": elem[2],
                    },
                    "end": {
                        "date": elem[3],
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
        self.out_text.insert(END, f"All tables were saved to file {file}.\n")

    # Unused
    def clean_all(self):
        self.clean_events()
        self.clean_artists()
        self.clean_persons()
        self.clean_participants()

        self.out_text.insert(END, "All table entrys were deleted.\n")

    ######################
    # Generell functions #
    ######################
    def get_setter_qmarks_vals(self, args: Tuple[Tuple[str, ...], ...]):
        setter: str = ""
        qmarks: str = ""
        vals: Tuple[Union[str, datetime.datetime], ...] = ()
        for pair in args:
            if pair[1] == "":
                self.out_text.insert(END, f"Ignored attr {pair[0]} (Missing value)!\n")
            else:
                if setter != "":
                    setter += ", "
                    qmarks += ", "
                setter += pair[0]
                qmarks += "?"
                vals += (pair[1],)
        return setter, qmarks, vals

    def get_where_and_vals(self, args: Tuple[Tuple[str, ...], ...]):
        where: str = ""
        vals: Tuple[Union[str, datetime.datetime], ...] = ()
        for pair in args:
            if pair[1] == "":
                self.out_text.insert(END, f"Ignored attr {pair[0]} (Missing value)!\n")
            else:
                if where != "":
                    where += "AND "
                where += pair[0] + "=? "
                vals += (pair[1],)
        return where, vals

    def get_setter(self, args: Tuple[Tuple[str, ...], ...]):
        setter: str = ""
        vals: Tuple[Union[str, datetime.datetime], ...] = ()
        for pair in args:
            if pair[2] == "":
                self.out_text.insert(END, f"Ignored attr {pair[0]} (Missing value)!\n")
            else:
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

        query = f"SELECT * FROM {table} WHERE {where}"
        cur = self.conn.execute(query, vals)
        result = cur.fetchall()
        cur.close()
        return result

    # TODO checken das bei has elem auch immer das ganze array uebergeben wird
    def has_elem(self, table: str, *args: Tuple[str, ...]) -> bool:
        where, vals = self.get_where_and_vals(args)
        if where == "":
            return False

        # TODO use get function
        query = f"SELECT * FROM {table} WHERE {where}"
        cur = self.conn.execute(query, vals)
        result = cur.fetchall()
        cur.close()

        # Return the id if present
        if len(result) > 0:
            return result[0][0]
        return False

    def insert(self, table: str, *args: Tuple[str, ...]):
        setter, qmarks, vals = self.get_setter_qmarks_vals(args)

        # If the element is not already present add
        has_elem = self.has_elem(table, *args)
        if not has_elem:
            query = f"INSERT INTO {table} ({setter}) VALUES ({qmarks})"
            cur = self.conn.execute(query, vals)
            self.conn.commit()
            return True, cur.lastrowid
        else:
            return False, has_elem

    # TODO test this !!!
    def insert_with_id(self, table: str, *args: Tuple[str, ...]):
        setter, qmarks, vals = self.get_setter_qmarks_vals(args)

        # If the element is not already present add
        # Check if the element is present with the same id
        has_elem = self.has_elem(table, *args)
        if has_elem:
            # Do not add since the element is already present
            return False, has_elem

        # Check if the id is taken
        has_elem = self.has_elem(table, args[0])
        if has_elem:
            # Shift the element with the same id
            # TODO this does not work since sqlite does not fill empty slots
            count = len(self.get_all(table))
            self.update(table, (args[0][0], has_elem, count + 1))

        # Check if it is present under another id
        has_elem = self.has_elem(table, *args[1:])
        if has_elem:
            # Shift the element to the current id
            self.update(table, (args[0][0], has_elem, args[0][1]))
            return False, args[0][1]

        # Add the element since it is not yet in the table
        query = f"INSERT INTO {table} ({setter}) VALUES ({qmarks})"
        cursor = self.conn.execute(query, vals)
        self.conn.commit()
        return True, cursor.lastrowid

    # TODO one to one doublicate of insert function
    def get_has_or_insert(self, table: str, *args: Tuple[str, ...]):
        setter, qmarks, vals = self.get_setter_qmarks_vals(args)

        # If the element is not already present add
        has_elem = self.has_elem(table, *args)
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

        if self.has_elem(table, *args):
            query = f"UPDATE {table} SET {setter} WHERE {where}"
            self.conn.execute(query, vals)
            self.conn.commit()
            self.out_text.insert(END, f"From table {table}, {args} was updated.\n")
        else:
            self.out_text.insert(END, f"In table {table}, {args} was not found.\n")

    def delete(self, table: str, *args: Tuple[str, str]):
        where, vals = self.get_where_and_vals(args)

        if self.has_elem(table, *args):
            query = f"DELETE FROM {table} WHERE {where}"
            self.conn.execute(query, vals)
            self.conn.commit()
            self.out_text.insert(END, f"From table {table}, {args} was deleted.\n")
        else:
            self.out_text.insert(END, f"In table {table}, {args} was not found.\n")

    def print_table(self, table: str):
        cur = self.conn.execute(f"SELECT * FROM {table}")
        result = cur.fetchall()
        cur.close()
        if len(result) == 0:
            self.out_text.insert(END, f"{table} table empty.\n")
        else: 
            self.out_text.insert(END, f"Content of table {table}.\n")
            for r in result:
                self.out_text.insert(END, str(r) + "\n")

        # TODO autoscroll text box by using this
        # Scroll text to the end
        self.out_text.yview(END)

    ##################
    # Person related #
    ##################
    def test_person_input(self, pid: int, name: str):
        if name == "":
            self.out_text.insert(END, "Could not add Person: Missing name!\n")
            return False
        if pid < 1:
            self.out_text.insert(END, "Could not add Person: Id must be greater than 0!\n")
            return False
        return True

    def insert_person(self, name: str):
        if not self.test_person_input(1, name):
            return

        res, pid = self.insert(
            "persons",
            ("name", name),
        )
        if res:
            self.out_text.insert(END, f"Person added (pid: {pid}, name: {name}).\n")
        else:
            self.out_text.insert(END, f"Person already present (pid: {pid}).\n")
            self.out_text.insert(END, f"Person not added (name: {name}).\n")

    def insert_person_with_id(self, pid: int, name: str):
        if not self.test_person_input(pid, name):
            return

        res, pid = self.insert_with_id(
            "persons",
            ("pid", pid),
            ("name", name),
        )
        if res:
            self.out_text.insert(END, f"Person added (pid: {pid}, name: {name}).\n")
        else:
            self.out_text.insert(END, f"Person already present (pid: {pid}).\n")
            self.out_text.insert(END, f"Person not added (name: {name}).\n")

    def update_person(self, name: str, n_name: str):
        """
        Update the selected person.
        """
        if not self.test_person_input(1, n_name):
            return

        # Remove unwanted characters
        # TODO + sql injection?
        str(n_name).replace(" ", "")
        str(n_name).replace("-", "")
        str(n_name).replace("_", "")

        self.update(
            "persons",
            ("name", name, n_name),
        )

    # TODO unused?
    def delete_person(self, name: str):
        """
        Delete the selected event.
        """
        self.delete("persons", ("name", name))

    def clean_persons(self):
        """
        Delete all persons in the database.
        """
        self.conn.execute("DROP TABLE IF EXISTS persons")

        self.conn.execute(
            "CREATE TABLE IF NOT EXISTS persons (pid INTEGER PRIMARY KEY ASC, name STRING)"
        )

        self.out_text.insert(END, "All person entrys were deleted.\n")

    def print_persons(self):
        self.print_table("persons")

    #######################
    # Participant related #
    #######################
    # TODO checkts that the person and event exist? or this done automatically?
    def test_participant_input(self, paid: int, person_id: int, event_id: int, start_date, end_date):
        if end_date < start_date:
            self.out_text.insert(END, "Could not add Event: end date < start date!\n")
            return False
        if person_id < 1:
            self.out_text.insert(END, "Could not add Event: Person Id must be greater than 0!\n")
            return False
        if event_id < 1:
            self.out_text.insert(END, "Could not add Event: Event Id must be greater than 0!\n")
            return False
        if paid < 1:
            self.out_text.insert(END, "Could not add Event: Id must be greater than 0!\n")
            return False
        return True

    # TODO person and event id vertausch
    def insert_participant(self, person_id: int, event_id: int, start_date, end_date):
        if not self.test_participant_input(1, person_id, event_id, start_date, end_date):
            return

        res, paid = self.insert(
            "participants",
            ("person_id", person_id),
            ("event_id", event_id),
            ("start_date", start_date),
            ("end_date", end_date),
        )

        if res:
            self.out_text.insert(END, f"Participant added (eid: {paid}, person_id: {person_id}, event_id: {event_id}, start: {start_date}, end: {end_date}).\n")
        else:
            self.out_text.insert(END, f"Participant already present (eid: {paid}).\n")
            self.out_text.insert(END, f"Participant not added (person_id: {person_id}, event_id: {event_id}, start: {start_date}, end: {end_date}).\n")

    def insert_participant_with_id(self, paid: int, person_id: int, event_id: int, start_date, end_date):
        if not self.test_participant_input(paid, person_id, event_id, start_date, end_date):
            return

        res, paid = self.insert_with_id(
            "participants",
            ("paid", paid),
            ("person_id", person_id),
            ("event_id", event_id),
            ("start_date", start_date),
            ("end_date", end_date),
        )

        # TODO additional information like person name and eventtitle
        if res:
            self.out_text.insert(END, f"Participant added (eid: {paid}, person_id: {person_id}, event_id: {event_id}, start: {start_date}, end: {end_date}).\n")
        else:
            self.out_text.insert(END, f"Participant already present (eid: {paid}).\n")
            self.out_text.insert(END, f"Participant not added (person_id: {person_id}, event_id: {event_id}, start: {start_date}, end: {end_date}).\n")


    # TODO unused & untested?
    def delete_participant(self, person_id: int, event_id: int, start_date, end_date):
        """
        Delete the selected participant.
        """
        self.delete("persons", ("event_id", event_id), ("person_id", person_id), ("start_date", start_date), ("end_date", end_date))

    def clean_participants(self):
        """
        Delete all participants in the database.
        """
        self.conn.execute("DROP TABLE IF EXISTS participants")

        self.conn.execute("CREATE TABLE IF NOT EXISTS participants (\
            paid INTEGER PRIMARY KEY ASC, \
            person_id INT NOT NULL, event_id INT NOT NULL, \
            start_date DATE, end_date DATE, \
            FOREIGN KEY (event_id) \
                REFERENCES events (eid) ON DELETE CASCADE, \
            FOREIGN KEY (person_id) \
                REFERENCES persons (pid))"
        )

        self.out_text.insert(END, "All participant entrys were deleted.\n")

    def print_participants(self):
        self.print_table("participants")

    #################
    # Event related #
    #################
    def test_event_input(self, eid: int, title: str, start_date, end_date):
        if end_date < start_date:
            self.out_text.insert(END, "Could not add Event: end date < start date!\n")
            return False
        if title == "":
            self.out_text.insert(END, "Could not add Event: Missing title!\n")
            return False
        if eid < 1:
            self.out_text.insert(END, "Could not add Event: Id must be greater than 0!\n")
            return False
        return True

    def insert_event(self, title: str, start_date, end_date):
        if not self.test_event_input(1, title, start_date, end_date):
            return

        # TODO move this to input
        title = sub(r"[^\w\s]", "", title)
        title = str(title).replace(" ", "")

        res, eid = self.insert(
            "events",
            ("title", title),
            ("start_date", start_date),
            ("end_date", end_date),
        )
        if res:
            self.out_text.insert(END, f"Event added (eid: {eid}, title: {title}, start: {start_date}, end: {end_date}).\n")
        else:
            self.out_text.insert(END, f"Event already present (eid: {eid}).\n")
            self.out_text.insert(END, f"Event not added (title: {title}, start: {start_date}, end: {end_date}).\n")

    # TODO insert methods are very similar
    def insert_event_with_id(self, eid: int, title: str, start_date, end_date):
        if not self.test_event_input(eid, title, start_date, end_date):
            return

        # TODO move this to input
        title = sub(r"[^\w\s]", "", title)
        title = str(title).replace(" ", "")

        res, eid = self.insert_with_id(
            "events",
            ("eid", eid),
            ("title", title),
            ("start_date", start_date),
            ("end_date", end_date)
        )
        if res:
            self.out_text.insert(END, f"Event added (eid: {eid}, title: {title}, start: {start_date}, end: {end_date}).\n")
        else:
            self.out_text.insert(END, f"Event already present (eid: {res}).\n")
            self.out_text.insert(END, f"Event not added (title: {title}, start: {start_date}, end: {end_date}).\n")

    def update_event(self, title, s_date, e_date, n_title, n_s_date, n_e_date):
        """
        Update the selected event.
        """
        if not self.test_event_input(1, title, n_s_date, n_e_date):
            return

        # Remove unwanted characters
        # TODO + sql injection?
        str(n_title).replace(" ", "")
        str(n_title).replace("-", "")
        str(n_title).replace("_", "")

        self.update(
            "events",
            ("title", title, n_title),
            ("start_date", s_date, n_s_date),
            ("end_date", e_date, n_e_date),
        )

    def delete_event(self, title: str, s_date: str, e_date: str):
        """
        Delete the selected event.
        """
        self.delete("events", ("title", title), ("start_date", s_date), ("end_date", e_date))
        # TODO if main event delete subevents needed?

    def clean_events(self):
        """
        Delete all events in the database.
        """
        self.conn.execute("DROP TABLE IF EXISTS events")

        self.conn.execute(
            "CREATE TABLE IF NOT EXISTS events \
            (eid INTEGER PRIMARY KEY ASC, \
                title STRING, start_date DATE, end_date DATE)"
        )

        self.out_text.insert(END, "All event entrys were deleted.\n")

    # TODO make dynamic getter method
    def get_event(self, date: datetime.datetime):
        """
        Get the event with the specified date.
        """
        cur = self.conn.execute(
            "SELECT * \
            FROM events WHERE start_date<=? AND end_date>=?",
            (date, date),
        )
        result = cur.fetchall()
        cur.close()
        return result

    def print_events(self):
        self.print_table("events")

    ####################
    # Subevent related #
    ####################
    # TODO Add check if event is present
    def test_subevent_input(self, seid: int, title: str, start_date, end_date):
        if end_date < start_date:
            self.out_text.insert(END, "Could not add Event: end date < start date!\n")
            return False
        if title == "":
            self.out_text.insert(END, "Could not add Event: Missing title!\n")
            return False
        if seid < 1:
            self.out_text.insert(END, "Could not add Event: Id must be greater than 0!\n")
            return False
        return True

    def insert_subevent(self, title: str, start_date, end_date):
        if not self.test_subevent_input(1, title, start_date, end_date):
            return

        # TODO move this to input
        title = sub(r"[^\w\s]", "", title)
        title = str(title).replace(" ", "")

        res, seid = self.insert(
            "subevents",
            ("title", title),
            ("start_date", start_date),
            ("end_date", end_date),
        )
        if res:
            self.out_text.insert(END, f"Subevent added (seid: {seid}, title: {title}, start: {start_date}, end: {end_date}).\n")
        else:
            self.out_text.insert(END, f"Subevent already present (seid: {seid}).\n")
            self.out_text.insert(END, f"Subevent not added (title: {title}, start: {start_date}, end: {end_date}).\n")

    def insert_subevent_with_id(self, seid: int, title: str, start_date, end_date):
        if not self.test_subevent_input(seid, title, start_date, end_date):
            return

        # TODO move this to input
        title = sub(r"[^\w\s]", "", title)
        title = str(title).replace(" ", "")

        res, seid = self.insert_with_id(
            "subevents",
            ("seid", seid),
            ("title", title),
            ("start_date", start_date),
            ("end_date", end_date),
        )
        if res:
            self.out_text.insert(END, f"Subevent added (seid: {seid}, title: {title}, start: {start_date}, end: {end_date}).\n")
        else:
            self.out_text.insert(END, f"Subevent already present (seid: {seid}).\n")
            self.out_text.insert(END, f"Subevent not added (title: {title}, start: {start_date}, end: {end_date}).\n")

    def update_subevent(self, title, s_date, e_date, n_title, n_s_day, n_s_hour, n_e_day, n_e_hour):
        """
        Update the selected subevent.
        """
        n_s_date = datetime.datetime.combine(
            n_s_day, datetime.datetime.min.time()
        ) + datetime.timedelta(hours=n_s_hour)
        n_e_date = datetime.datetime.combine(
            n_e_day, datetime.datetime.min.time()
        ) + datetime.timedelta(hours=n_e_hour)

        if not self.test_subevent_input(1, n_title, n_s_date, n_e_date):
            return

        # Remove unwanted characters
        # TODO + sql injection?
        str(n_title).replace(" ", "")
        str(n_title).replace("-", "")
        str(n_title).replace("_", "")

        self.update(
            "subevents",
            ("title", title, n_title),
            ("start_date", s_date, n_s_date),
            ("end_date", e_date, n_e_date),
        )

    def delete_subevent(self, title: str, s_date: str, e_date: str):
        """
        Delete the selected subevent.
        """
        self.delete("subevents", ("title", title), ("start_date", s_date), ("end_date", e_date))

    def clean_subevents(self):
        """
        Delete all subevents in the database.
        """
        self.conn.execute("DROP TABLE IF EXISTS subevents")

        self.conn.execute(
            "CREATE TABLE IF NOT EXISTS subevents \
            (seid INTEGER PRIMARY KEY ASC, \
                title STRING, start_date DATE, end_date DATE)"
        )

        self.out_text.insert(END, "All subevent entrys were deleted.\n")

    def get_subevent(self, date: datetime.datetime):
        """
        Get the event with the specified date.
        """
        cur = self.conn.execute(
            "SELECT * \
            FROM subevents WHERE start_date<=? AND end_date>=?",
            (date, date),
        )
        result = cur.fetchall()
        cur.close()
        return result

    def print_events(self):
        self.print_table("subevents")

    ##################
    # Artist related #
    ##################
    def test_artist_input(self, aid: int, pid: int, make: str, model: str, start_date, end_date):
        if end_date < start_date:
            self.out_text.insert(END, "Could not add Artist: end date < start date!\n")
            return False
        if make == "":
            self.out_text.insert(END, "Could not add Artist: Missing make!\n")
            return False
        if model == "":
            self.out_text.insert(END, "Could not add Artist: Missing model!\n")
            return False
        if pid < 1:
            self.out_text.insert(END, "Could not add Artist: Person Id must be greater than 0!\n")
            return False
        if aid < 1:
            self.out_text.insert(END, "Could not add Artist: Id must be greater than 0!\n")
            return False

        # # Check if person is not present
        # if not self.has_elem("persons", ("pid", pid)):
        #     self.out_text.insert(END, f"Could not add Artist: Person (pid: {pid}) not found in table!\n")
        #     return

        return True

    def insert_artist(self, pid: int, make: str, model: str, start_date, end_date):
        if not self.test_artist_input(1, pid, make, model, start_date, end_date):
            return

        res, aid = self.insert(
            "artists",
            ("person_id", pid),
            ("make", make),
            ("model", model),
            ("start_date", start_date),
            ("end_date", end_date),
        )

        if res:
            self.out_text.insert(END, f"Artist added (aid: {aid}, pid: {pid}, make: {make}, model: {model}, start: {start_date}, end: {end_date}).\n")
        else:
            self.out_text.insert(END, f"Artist already present (aid: {aid}).\n")
            self.out_text.insert(END, f"Artist not added (pid: {pid}, make: {make}, model: {model}, start: {start_date}, end: {end_date}).\n")


    # TODO
    def insert_artist_with_id(self, aid: int, pid: int, make: str, model: str, start_date, end_date):
        if not self.test_artist_input(aid, pid, make, model, start_date, end_date):
            return

        res, aid = self.insert_with_id(
            "artists",
            ("aid", aid),
            ("person_id", pid),
            ("make", make),
            ("model", model),
            ("start_date", start_date),
            ("end_date", end_date),
        )

        if res:
            self.out_text.insert(END, f"Artist added (aid: {aid}, pid: {pid}, make: {make}, model: {model}, start: {start_date}, end: {end_date}).\n")
        else:
            self.out_text.insert(END, f"Artist already present (aid: {aid}).\n")
            self.out_text.insert(END, f"Artist not added (pid: {pid}, make: {make}, model: {model}, start: {start_date}, end: {end_date}).\n")

    # TODO check all update methods, if a check is needed is the artist/person present
    # TODO check if time combine can be done before
    def update_artist(
            self, 
            person_id: int, make: str, model: str, s_date, e_date, 
            n_person_id: int, n_make: str, n_model, n_s_date, n_e_date
        ):
        """
        Update the selected artist.
        """
        # TODO
        # n_s_date = datetime.datetime.combine(
        #     n_s_day, datetime.datetime.min.time()
        # ) + datetime.timedelta(hours=n_s_hour)
        # n_e_date = datetime.datetime.combine(
        #     n_e_day, datetime.datetime.min.time()
        # ) + datetime.timedelta(hours=n_e_hour)

        if not self.test_artist_input(1, n_person_id, n_make, n_model, n_s_date, n_e_date):
            return

        self.update(
            "artists",
            ("person_id", person_id, n_person_id),
            ("make", make, n_make),
            ("model", model, n_model),
            ("start_date", s_date, n_s_date),
            ("end_date", e_date, n_e_date),
        )

    def delete_artist(self, person_id: str, make: str, model: str, s_date, e_date):
        """
        Delete the selected artist.
        """
        self.delete(
            "artists",
            ("person_id", person_id),
            ("make", make),
            ("model", model),
            ("start_date", s_date),
            ("end_date", e_date)
        )

    def clean_artists(self):
        """
        Delete all artists in the database.
        """
        self.conn.execute("DROP TABLE IF EXISTS artists")

        self.conn.execute(
            "CREATE TABLE IF NOT EXISTS artists(\
            aid INTEGER PRIMARY KEY ASC, \
            person_id INT, make TEXT, model TEXT, \
            start_date DATE, end_date DATE, \
            FOREIGN KEY (person_id) REFERENCES persons (pid))"
        )

        self.out_text.insert(END, "All artist entrys were deleted.\n")

    # def has_artist(self, name: str, make: str, model: str):
    #     """
    #     Check if there is an artist with the specified name, make and model.
    #     """
    #     result = False
    #     lst_persons = self.db.get_person_by_name(name)

    #     for p in lst_persons:
    #         # Get first attribute (pid) and use it for the check
    #         if self.db.has_elem("artists", ("person_id", p[0]), ("make", make), ("model", model)):
    #             return (p[0], make, model)
    #     return result

    def print_artists(self):
        self.print_table("artists")
