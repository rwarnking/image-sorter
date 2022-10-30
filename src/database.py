import datetime
import json
import sqlite3
from tkinter import END
from typing import Dict, List, Tuple, Union


class Database:
    def __init__(self, path: str = "database.db"):
        self.conn = sqlite3.connect(path)
        self.conn.execute(
            "CREATE TABLE IF NOT EXISTS events \
            (title STRING, start_date DATE, end_date DATE, sub INT)"
        )

        self.conn.execute(
            "CREATE TABLE IF NOT EXISTS artists (name STRING, make STRING, model STRING)"
        )
        self.conn.commit()

    def set_out_text(self, out_text):
        self.out_text = out_text

    def clean_all(self):
        self.clean_events()
        self.clean_artists()
        self.conn.execute("DROP TABLE IF EXISTS events")
        self.conn.execute("DROP TABLE IF EXISTS artists")

        self.conn.execute(
            "CREATE TABLE IF NOT EXISTS events \
            (title STRING, start_date DATE, end_date DATE, sub INT)"
        )
        self.conn.execute(
            "CREATE TABLE IF NOT EXISTS artists (name STRING, make STRING, model STRING)"
        )

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
        for r in result:
            self.out_text.insert(END, str(r) + "\n")

        if len(result) == 0:
            self.out_text.insert(END, "Table empty.\n")
        # TODO autoscroll text box by using this
        # Scroll text to the end
        self.out_text.yview(END)

    #################
    # Event related #
    #################
    def insert_event_from_date(self, title, start_day, start_hour, end_day, end_hour, subevent=0):
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

        if end_date < start_date:
            self.out_text.insert(END, "Could not add Event: end date < start date!\n")
            return
        if title == "":
            self.out_text.insert(END, "Could not add Event: Missing title!\n")
            return

        # TODO remove this check as soon as events are participant bound
        s_event = self.get_event(start_date, subevent)
        e_event = self.get_event(end_date, subevent)
        if len(s_event) > 0 or len(e_event) > 0:
            self.out_text.insert(END, "Event was not added. Overlapping event found.\n")
            return

        # Remove unwanted characters
        str(title).replace(" ", "")
        str(title).replace("-", "")
        str(title).replace("_", "")

        self.insert_event(
            title,
            start_date,
            end_date,
            subevent,
        )

    def insert_subevent_from_date(self, title: str, start_day, start_hour, end_day, end_hour):
        start_date = datetime.datetime.combine(
            start_day, datetime.datetime.min.time()
        ) + datetime.timedelta(hours=start_hour)
        end_date = datetime.datetime.combine(
            end_day, datetime.datetime.min.time()
        ) + datetime.timedelta(hours=end_hour)

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
        self.insert_event_from_date(title, start_day, start_hour, end_day, end_hour, 1)

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

    def insert_events(self, file: str):
        """
        Add events from a file.
        """
        with open(file) as json_file:
            data = json.load(json_file)
            for event in data["events"]:
                self.insert_event(
                    event["title"],
                    datetime.datetime.strptime(event["start"]["date"], "%Y-%m-%d %H:%M:%S"),
                    datetime.datetime.strptime(event["end"]["date"], "%Y-%m-%d %H:%M:%S"),
                    event["subevent"],
                )

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
            (title STRING, start_date DATE, end_date Date INT, sub INT)"
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
            "SELECT title, start_date, end_date \
            FROM events WHERE start_date<=? AND end_date>=? AND sub=?",
            (date, date, sub),
        )
        result = cur.fetchall()
        cur.close()
        return result

    def print_events(self):
        self.print_table("events")

    ##################
    # Artist related #
    ##################
    def insert_artist(self, name: str, make: str, model: str):
        if name == "":
            self.out_text.insert(END, "Could not add Artist: Missing name!\n")
            return
        if make == "":
            self.out_text.insert(END, "Could not add Artist: Missing make!\n")
            return
        if model == "":
            self.out_text.insert(END, "Could not add Artist: Missing model!\n")
            return

        # TODO have cameras be time dependend on artist, maybe the person did change the camera
        if not self.has_elem("artists", ("name", name), ("make", make), ("model", model)):
            self.conn.execute(
                "INSERT INTO artists (name, make, model) VALUES (?, ?, ?)", (name, make, model)
            )
            self.conn.commit()
            self.out_text.insert(END, f"Artist {name}|{make}|{model} was added.\n")
        else:
            self.out_text.insert(
                END, f"Artist {name}|{make}|{model} was already there, did NOT add.\n"
            )
        return

    def insert_artists(self, file: str):
        """
        Add artists from a file.
        """
        with open(file) as json_file:
            data = json.load(json_file)
            for artist in data["artists"]:
                self.insert_artist(
                    artist["name"],
                    artist["make"],
                    artist["model"],
                )

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

        self.update(
            "artists",
            ("name", name, n_name),
            ("make", make, n_make),
            ("model", model, n_model),
        )

    def delete_artist(self, name: str, make: str, model: str):
        """
        Delete the selected artist.
        """
        if name == "" or make == "" or model == "":
            self.out_text.insert(END, "Could not delete: Missing value!\n")
            return

        table = "artists"
        if self.has_elem(table, ("name", name), ("make", make), ("model", model)):
            # Only one entry should be present,
            # since the insertion does not allow direct copys of an entry
            query = f"DELETE FROM {table} WHERE name=? AND make=? AND model=?"
            self.conn.execute(
                query,
                (
                    name,
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
            "CREATE TABLE IF NOT EXISTS artists (name STRING, make STRING, model STRING)"
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
        cur = self.conn.execute("SELECT name FROM artists WHERE make=? AND model=?", (make, model))
        result = cur.fetchall()
        cur.close()
        return result

    def print_artists(self):
        self.print_table("artists")
