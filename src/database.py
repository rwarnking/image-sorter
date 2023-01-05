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
                title STRING, start_date DATE, end_date DATE, sub INT)"
        )

        self.conn.execute(
            "CREATE TABLE IF NOT EXISTS persons (pid INTEGER PRIMARY KEY ASC, name STRING)"
        )

        self.conn.execute(
            "CREATE TABLE IF NOT EXISTS artists(\
            person_id INT, make TEXT, model TEXT, \
            FOREIGN KEY (person_id) REFERENCES persons (pid) ON DELETE CASCADE)"
        )

        self.conn.execute("CREATE TABLE IF NOT EXISTS participants (\
            event_id INT NOT NULL, person_id INT NOT NULL, \
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
                self.insert_person(person["name"])
            
            for artist in data["artists"]:
                self.insert_artist(
                    artist["name"],
                    artist["make"],
                    artist["model"],
                )

            for event in data["events"]:
                self.insert_event(
                    event["title"],
                    datetime.datetime.strptime(event["start"]["date"], "%Y-%m-%d %H:%M:%S"),
                    datetime.datetime.strptime(event["end"]["date"], "%Y-%m-%d %H:%M:%S"),
                    0 # TODO remove subevent idx
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

        data = self.get_all_from_table("events")
        for elem in data:
            json_data["events"].append(
                {
                    "title": elem[1],
                    "start": {
                        "date": elem[2],
                    },
                    "end": {
                        "date": elem[3],
                    },
                }
            )
    
        data = self.get_all_from_table("participants")
        for elem in data:
            json_data["participants"].append(
                {
                    "person_id": elem[0],
                    "event_id": elem[1],
                }
            )

        data = self.get_all_from_table("artists")
        for elem in data:
            json_data["artists"].append(
                {
                    "name": elem[0],
                    "make": elem[1],
                    "model": elem[2],
                }
            )
        
        data = self.get_all_from_table("persons")
        for elem in data:
            json_data["persons"].append(
                {
                    "name": elem[1],
                }
            )

        with open(file, "w") as outfile:
            json.dump(json_data, outfile, indent=4)
        self.out_text.insert(END, f"All tables were saved to file {file}.\n")

    def clean_all(self):
        self.clean_events()
        self.clean_artists()
        self.clean_persons()
        self.clean_participants()

        self.out_text.insert(END, "All table entrys were deleted.\n")

    ######################
    # Generell functions #
    ######################
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

    def has_elem(self, table: str, *args: Tuple[str, ...]) -> bool:
        where, vals = self.get_where_and_vals(args)
        if where == "":
            return False

        query = f"SELECT * FROM {table} WHERE {where}"
        cur = self.conn.execute(query, vals)
        result = cur.fetchall()
        cur.close()

        return len(result) > 0

    def delete(self, table: str, *args: Tuple[str, str]):
        where, vals = self.get_where_and_vals(args)

        if self.has_elem(table, args[0]):
            query = f"DELETE FROM {table} WHERE {where}"
            self.conn.execute(query, vals)
            self.conn.commit()
            self.out_text.insert(END, f"From table {table}, {args} was deleted.\n")
        else:
            self.out_text.insert(END, f"In table {table}, {args} was not found.\n")

    def update(self, table: str, *args: Tuple[str, ...]):
        where, vals1 = self.get_where_and_vals(args)
        setter, vals2 = self.get_setter(args)
        vals = vals2 + vals1

        if self.has_elem(table, args[0]):
            query = f"UPDATE {table} SET {setter} WHERE {where}"
            self.conn.execute(query, vals)
            self.conn.commit()
            self.out_text.insert(END, f"From table {table}, {args} was updated.\n")
        else:
            self.out_text.insert(END, f"In table {table}, {args} was not found.\n")

    def get_all_from_table(self, table: str):
        cur = self.conn.execute(f"SELECT * FROM {table}")
        result = cur.fetchall()
        cur.close()
        return result

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
    def insert_person(self, name: str):
        self.conn.execute(
            "INSERT INTO persons (name) VALUES (?)",
            (name,),
        )
        self.conn.commit()

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

    def update_person(self, name: str, n_name: str):
        """
        Update the selected person.
        """
        if n_name == "":
            self.out_text.insert(END, "Could not update person: Missing name!\n")
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

    def get_person_by_name(self, name: str):
        """
        Get the person with the specified name.
        """
        cur = self.conn.execute("SELECT * FROM persons WHERE name=?", (name,))
        result = cur.fetchall()
        cur.close()
        return result

    def get_person_by_id(self, pid: int):
        """
        Get the person with the specified id.
        """
        cur = self.conn.execute("SELECT * FROM persons WHERE pid=?", (pid,))
        result = cur.fetchall()
        cur.close()
        return result

    def print_persons(self):
        self.print_table("persons")

    #######################
    # Participant related #
    #######################
    def insert_participant(self, event_id: int, person_id: int):
        self.conn.execute(
            "INSERT INTO participants \
            (event_id, person_id) \
            VALUES (?, ?)",
            (event_id, person_id),
        )
        self.conn.commit()

    # TODO unused & untested?
    def delete_participant(self, event_id: int, person_id: int):
        """
        Delete the selected participant.
        """
        self.delete("persons", ("event_id", event_id), ("person_id", person_id))

    def clean_participants(self):
        """
        Delete all participants in the database.
        """
        self.conn.execute("DROP TABLE IF EXISTS participants")

        self.conn.execute("CREATE TABLE IF NOT EXISTS participants (\
            event_id INT NOT NULL, person_id INT NOT NULL, \
            FOREIGN KEY (event_id) \
                REFERENCES events (eid) ON DELETE CASCADE, \
            FOREIGN KEY (person_id) \
                REFERENCES persons (pid))"
        )

        self.out_text.insert(END, "All participant entrys were deleted.\n")

    # TODO unused & untested?
    def get_participants_by_event(self, event_id: int):
        """
        Get all participants with the specified event.
        """
        cur = self.conn.execute("SELECT * FROM participants WHERE event_id=?", (event_id,))
        result = cur.fetchall()
        cur.close()
        return result

    # TODO unused & untested?
    def get_participants_by_person(self, person_id: int):
        """
        Get all participants with the specified person.
        """
        cur = self.conn.execute("SELECT * FROM participants WHERE person_id=?", (person_id,))
        result = cur.fetchall()
        cur.close()
        return result

    def print_participants(self):
        self.print_table("participants")

    #################
    # Event related #
    #################
    def insert_event_from_date(
        self, title, start_day, start_hour: int, end_day, end_hour: int, parts, subevent=0
    ):
        """
        Adds a new event to the database using given date information.
        The event is only added if the title is not empty
        and the start date lies before the end date.

        Mainevents are allowed to overlap, subevent are not.
        Mainevents are also allowed to have the same title,
        while subevents need to have a unique title inside its mainevent.

        Args:
            title: The title of the event as a String
            start_day: The start day as a datetime object
            start_hour: The hour in which the event start at the given day as an Integer (0-24)
            end_day: The end day as a datetime object
            end_hour: The hour in which the event ends at the given day as an Integer (0-24)
            subevent: Indicate wether this is a subevent (0 = event, 1 = subevent)
        """
        start_date = datetime.datetime.combine(
            start_day, datetime.datetime.min.time()
        ) + datetime.timedelta(hours=start_hour)
        end_date = datetime.datetime.combine(
            end_day, datetime.datetime.min.time()
        ) + datetime.timedelta(hours=end_hour)

        # Remove unwanted characters
        # TODO replace only for folder name not for internal storage
        title = sub(r"[^\w\s]", "", title)
        # TODO remove
        # # Remove whitespaces but only before and after commata
        # parts = sub(r"\s*,\s*", ",", parts).split(",")
        # parts = list(filter(None, parts))

        if end_date < start_date:
            self.out_text.insert(END, "Could not add Event: end date < start date!\n")
            return
        if title == "":
            self.out_text.insert(END, "Could not add Event: Missing title!\n")
            return

        # Insert event first, so we can get its primary key for the participants
        self.insert_event(
            title,
            start_date,
            end_date,
            subevent,
        )

        # Use the event data to get the primary key
        event_id = self.get_event2(title, start_date, end_date, subevent)[0][0]
        # For each participant create an entry in the list
        for p_name in parts:
            if p_name == "":
                continue
            # Insert if not present
            if not self.has_elem("persons", ("name", p_name)):
                self.insert_person(p_name)

            # Use the string to get the person id
            person_id = self.get_person_by_name(p_name)[0][0]

            self.insert_participant(event_id, person_id)
        if len(parts) > 0:
            self.out_text.insert(END, f"Participants were added.\n")
        else:
            self.out_text.insert(END, f"No participants were added!\n")

    def insert_subevent_from_date(
        self, title: str, start_day, start_hour: int, end_day, end_hour: int, parts: str
    ):
        start_date = datetime.datetime.combine(
            start_day, datetime.datetime.min.time()
        ) + datetime.timedelta(hours=start_hour)
        end_date = datetime.datetime.combine(
            end_day, datetime.datetime.min.time()
        ) + datetime.timedelta(hours=end_hour)

        # TODO make mainevent selectable in gui and then allow for a date range
        s_main = self.get_event(start_date)
        e_main = self.get_event(end_date)
        if len(s_main) == 0 or len(e_main) == 0:
            self.out_text.insert(END, "Subevent could not be added. Missing main event.\n")
            return
        if s_main[0][0] != e_main[0][0]:
            self.out_text.insert(
                END, "Subevent could not be added. Two matching main events found.\n"
            )
            return
        # TODO do an overlap check with other subevents
        # TODO subevents need to assigned to a mainevent

        # Do not use the calculated date, since the insert event function itself does
        # calculate the date.
        self.insert_event_from_date(title, start_day, start_hour, end_day, end_hour, parts, 1)

    def insert_event(self, title: str, start_date, end_date, sub_event: int):
        title = str(title).replace(" ", "")
        self.conn.execute(
            "INSERT INTO events \
            (title, start_date, end_date, sub) \
            VALUES (?, ?, ?, ?)",
            (title, start_date, end_date, sub_event),
        )
        self.conn.commit()
        self.out_text.insert(END, f"Event {title} was added. ({start_date}, {end_date})\n")

    def update_event(self, title, s_date, e_date, n_title, n_s_day, n_s_hour, n_e_day, n_e_hour):
        """
        Update the selected event.
        """
        n_s_date = datetime.datetime.combine(
            n_s_day, datetime.datetime.min.time()
        ) + datetime.timedelta(hours=n_s_hour)
        n_e_date = datetime.datetime.combine(
            n_e_day, datetime.datetime.min.time()
        ) + datetime.timedelta(hours=n_e_hour)

        if n_e_date < n_s_date:
            self.out_text.insert(END, "Could not add Event: end date < start date!\n")
            return
        if title == "":
            self.out_text.insert(END, "Could not add Event: Missing title!\n")
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
        # TODO if main event delete subevents

    def clean_events(self):
        """
        Delete all events in the database.
        """
        self.conn.execute("DROP TABLE IF EXISTS events")

        self.conn.execute(
            "CREATE TABLE IF NOT EXISTS events \
            (eid INTEGER PRIMARY KEY ASC, \
                title STRING, start_date DATE, end_date DATE, sub INT)"
        )

        self.out_text.insert(END, "All event entrys were deleted.\n")

    def save_events(self, file: str):
        """
        Save all events to a json file.
        """
        data = self.get_all_from_table("events")
        json_data: Dict[str, List] = {"events": []}
        for elem in data:
            json_data["events"].append(
                {
                    "title": elem[0],
                    "start": {
                        "date": elem[1],
                    },
                    "end": {
                        "date": elem[2],
                    },
                    "subevent": elem[3],
                }
            )

        with open(file, "w") as outfile:
            json.dump(json_data, outfile, indent=4)
        self.out_text.insert(END, f"Events were saved to file {file}.\n")

    def get_event(self, date: datetime.datetime, sub: int = 0):
        """
        Get the event with the specified date.
        """
        cur = self.conn.execute(
            "SELECT * \
            FROM events WHERE start_date<=? AND end_date>=? AND sub=?",
            (date, date, sub),
        )
        result = cur.fetchall()
        cur.close()
        return result

    # TODO rename and merge with before method?
    def get_event2(self, title: str, s_date: datetime.datetime, e_date: datetime.datetime, sub: int = 0):
        """
        Get the event with the specified date.
        """
        cur = self.conn.execute(
            "SELECT * \
            FROM events WHERE title=? AND start_date=? AND end_date=? AND sub=?",
            (title, s_date, e_date, sub),
        )
        result = cur.fetchall()
        cur.close()
        return result

    def print_events(self):
        # TODO remove 
        self.print_table("events")
        self.print_table("participants")
        self.print_table("persons")

    ##################
    # Artist related #
    ##################
    def insert_artist(self, p_name: str, make: str, model: str):
        if p_name == "":
            self.out_text.insert(END, "Could not add Artist: Missing name!\n")
            return
        if make == "":
            self.out_text.insert(END, "Could not add Artist: Missing make!\n")
            return
        if model == "":
            self.out_text.insert(END, "Could not add Artist: Missing model!\n")
            return

        # Insert if not present
        if not self.has_elem("persons", ("name", p_name)):
            self.insert_person(p_name)

        # Use the string to get the person id
        person_id = self.get_person_by_name(p_name)[0][0]

        # TODO have cameras be time dependend on artist, maybe the person did change the camera
        if not self.has_elem("artists", ("person_id", person_id), ("make", make), ("model", model)):
            self.conn.execute(
                "INSERT INTO artists (person_id, make, model) VALUES (?, ?, ?)", (person_id, make, model)
            )
            self.conn.commit()
            self.out_text.insert(END, f"Artist {p_name}|{make}|{model} was added.\n")
        else:
            self.out_text.insert(
                END, f"Artist {p_name}|{make}|{model} was already there, did NOT add.\n"
            )
        return

    def update_artist(self, name: str, make: str, model: str, n_name: str, n_make: str, n_model):
        """
        Update the selected artist.
        """
        if n_name == "":
            self.out_text.insert(END, "Could not add Artist: Missing name!\n")
            return
        if n_make == "":
            self.out_text.insert(END, "Could not add Artist: Missing make!\n")
            return
        if n_model == "":
            self.out_text.insert(END, "Could not add Artist: Missing model!\n")
            return

        # Check if person present
        if self.has_elem("persons", ("name", name)):
            # Use the string to get the person id
            person_id = self.get_person_by_name(name)[0][0]

            if self.has_elem("artists", ("person_id", person_id), ("make", make), ("model", model)):
                self.update(
                    "persons",
                    ("name", name, n_name),
                )

                self.update(
                    "artists",
                    ("make", make, n_make),
                    ("model", model, n_model),
                )
            else:
                self.out_text.insert(END, "Artist could not be updated, artist does not exist!\n")
        else:
            self.out_text.insert(END, "Artist could not be updated, person does not exist!\n")

    def delete_artist(self, name: str, make: str, model: str):
        """
        Delete the selected artist.
        """
        if name == "" or make == "" or model == "":
            self.out_text.insert(END, "Could not delete: Missing value!\n")
            return

        table = "artists"
        # Check if person present
        if self.has_elem("persons", ("name", name)):
            # Use the string to get the person id
            person_id = self.get_person_by_name(name)[0][0]

            if self.has_elem(table, ("person_id", person_id), ("make", make), ("model", model)):
                # Only one entry should be present,
                # since the insertion does not allow direct copys of an entry
                query = f"DELETE FROM {table} WHERE person_id=? AND make=? AND model=?"
                self.conn.execute(
                    query,
                    (
                        person_id,
                        make,
                        model,
                    ),
                )
                self.conn.commit()
                self.out_text.insert(END, f"From table {table}, {name}|{make}|{model} was deleted.\n")
        else:
            self.out_text.insert(END, f"In table {table}, {name}|{make}|{model} was not found.\n")

    def clean_artists(self):
        """
        Delete all artists in the database.
        """
        self.conn.execute("DROP TABLE IF EXISTS artists")

        self.conn.execute(
            "CREATE TABLE IF NOT EXISTS artists(\
            person_id INT, make TEXT, model TEXT, \
            FOREIGN KEY (person_id) REFERENCES persons (pid))"
        )

        self.out_text.insert(END, "All artist entrys were deleted.\n")

    def save_artists(self, file: str):
        """
        Save all artists to a json file.
        """
        data = self.get_all_from_table("artists")
        json_data: Dict[str, List] = {"artists": []}
        for elem in data:
            json_data["artists"].append(
                {
                    "name": elem[0],
                    "make": elem[1],
                    "model": elem[2],
                }
            )

        with open(file, "w") as outfile:
            json.dump(json_data, outfile, indent=4)
        self.out_text.insert(END, f"Artists were saved to file {file}.\n")

    def get_artist(self, make: str, model: str):
        """
        Get the artist with the specified make and model.
        """
        cur = self.conn.execute("SELECT * FROM artists WHERE make=? AND model=?", (make, model))
        result = cur.fetchall()
        cur.close()
        return result

    def has_artist(self, name: str, make: str, model: str):
        """
        Check if there is an artist with the specified name, make and model.
        """
        result = False
        lst_persons = self.db.get_person_by_name(name)

        for p in lst_persons:
            # Get first attribute (pid) and use it for the check
            if self.db.has_elem("artists", ("person_id", p[0]), ("make", make), ("model", model)):
                return (p[0], make, model)
        return result

    def print_artists(self):
        self.print_table("artists")
