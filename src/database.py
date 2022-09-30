import json
import sqlite3
from tkinter import END


class Database:
    def __init__(self, out_text, path="database.db"):
        self.out_text = out_text
        self.conn = sqlite3.connect(path)
        self.conn.execute(
            "CREATE TABLE IF NOT EXISTS events (title STRING, s_year INT, s_month INT, \
            s_day INT, e_year INT, e_month INT, e_day INT, sub INT)"
        )

        self.conn.execute(
            "CREATE TABLE IF NOT EXISTS artists (name STRING, make STRING, model STRING)"
        )
        self.conn.commit()

    def clean_all(self):
        self.clean_events()
        self.clean_artists()
        self.conn.execute("DROP TABLE IF EXISTS events")
        self.conn.execute("DROP TABLE IF EXISTS artists")

        self.conn.execute(
            "CREATE TABLE IF NOT EXISTS events (title STRING, s_year INT, s_month INT, \
            s_day INT, e_year INT, e_month INT, e_day INT, sub INT)"
        )
        self.conn.execute(
            "CREATE TABLE IF NOT EXISTS artists (name STRING, make STRING, model STRING)"
        )

        self.out_text.insert(END, "All table entrys were deleted.\n")

    ######################
    # Generell functions #
    ######################
    def has_elem(self, table, attr, var):
        query = f"SELECT * FROM {table} WHERE {attr}=?"
        cur = self.conn.execute(query, (var,))
        result = cur.fetchall()
        cur.close()

        return len(result) > 0

    def delete_one(self, table, attr, var):
        if var == "":
            self.out_text.insert(END, "Could not delete: Missing value!\n")
            return

        if self.has_elem(table, attr, var):
            query = f"DELETE FROM {table} WHERE {attr}=?"
            self.conn.execute(query, (var,))
            self.conn.commit()
            self.out_text.insert(END, f"From table {table}, {var} was deleted.\n")
        else:
            self.out_text.insert(END, f"In table {table}, {var} was not found.\n")

    def get_all_from_table(self, table):
        cur = self.conn.execute(f"SELECT * FROM {table}")
        result = cur.fetchall()
        cur.close()
        return result

    def print_table(self, table):
        cur = self.conn.execute(f"SELECT * FROM {table}")
        result = cur.fetchall()
        cur.close()
        for r in result:
            self.out_text.insert(END, str(r) + "\n")

        if len(result) == 0:
            self.out_text.insert(END, "Table empty.\n")

    #################
    # Event related #
    #################
    def insert_event_from_date(self, title, start_date, end_date, subevent=0):
        if end_date < start_date:
            self.out_text.insert(END, "Could not add Event: end date < start date!\n")
            return
        if title == "":
            self.out_text.insert(END, "Could not add Event: Missing title!\n")
            return

        s_event = self.get_event(start_date.year, start_date.month, start_date.day, subevent)
        e_event = self.get_event(end_date.year, end_date.month, end_date.day, subevent)
        if len(s_event) > 0 or len(e_event) > 0:
            self.out_text.insert(END, "Event was not added. Overlapping event found.\n")
            return

        # Remove unwanted characters
        str(title).replace(" ", "")
        str(title).replace("-", "")
        str(title).replace("_", "")

        self.insert_event(
            title,
            start_date.year,
            start_date.month,
            start_date.day,
            end_date.year,
            end_date.month,
            end_date.day,
            subevent,
        )

    def insert_subevent_from_date(self, title, start_date, end_date):
        s_main = self.get_event(start_date.year, start_date.month, start_date.day)
        e_main = self.get_event(end_date.year, end_date.month, end_date.day)
        if len(s_main) == 0 or len(e_main) == 0:
            self.out_text.insert(END, "Subevent could not be added. Missing main event.\n")
            return
        if s_main[0][0] != e_main[0][0]:
            self.out_text.insert(
                END, "Subevent could not be added. Two matching main events found.\n"
            )
            return

        self.insert_event_from_date(title, start_date, end_date, 1)

    def insert_event(self, title, s_year, s_month, s_day, e_year, e_month, e_day, sub_event):
        # TODO Add check that the new events do not overlap
        if not self.has_elem("events", "title", title):
            title = str(title).replace(" ", "")
            self.conn.execute(
                "INSERT INTO events (title, s_year, s_month, s_day, e_year, e_month, e_day, sub) \
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                (title, s_year, s_month, s_day, e_year, e_month, e_day, sub_event),
            )
            self.conn.commit()
            self.out_text.insert(END, f"Event {title} was added.\n")
        else:
            self.out_text.insert(END, f"Event {title} was already there, could NOT add.\n")

    def insert_events(self, file):
        with open(file) as json_file:
            data = json.load(json_file)
            for event in data["events"]:
                self.insert_event(
                    event["title"],
                    event["start"]["year"],
                    event["start"]["month"],
                    event["start"]["day"],
                    event["end"]["year"],
                    event["end"]["month"],
                    event["end"]["day"],
                    event["subevent"],
                )

    def delete_event(self, title):
        title = str(title).replace(" ", "")
        self.delete_one("events", "title", title)

    def clean_events(self):
        self.conn.execute("DROP TABLE IF EXISTS events")

        self.conn.execute(
            "CREATE TABLE IF NOT EXISTS events (title STRING, s_year INT, s_month INT, \
            s_day INT, e_year INT, e_month INT, e_day INT, sub INT)"
        )

        self.out_text.insert(END, "All event entrys were deleted.\n")

    def save_events(self, file):
        data = self.get_all_from_table("events")
        json_data = {"events": []}
        for elem in data:
            json_data["events"].append(
                {
                    "title": elem[0],
                    "start": {
                        "year": elem[1],
                        "month": elem[2],
                        "day": elem[3],
                    },
                    "end": {
                        "year": elem[4],
                        "month": elem[5],
                        "day": elem[6],
                    },
                    "subevent": elem[7],
                }
            )

        with open(file, "w") as outfile:
            json.dump(json_data, outfile, indent=4)
        self.out_text.insert(END, f"Events were saved to file {file}.\n")

    def get_event(self, year, month, day, sub=0):
        cur = self.conn.execute(
            "SELECT title, s_year, s_month, s_day, e_year, e_month, e_day \
            FROM events WHERE s_year<=? AND s_month<=? AND s_day<=? AND e_year>=? \
            AND e_month>=? AND e_day>=? AND sub=?",
            (year, month, day, year, month, day, sub),
        )
        result = cur.fetchall()
        cur.close()
        return result

    def print_events(self):
        self.print_table("events")

    ##################
    # Artist related #
    ##################
    def insert_artist(self, name, make, model):
        if name == "":
            self.out_text.insert(END, "Could not add Artist: Missing name!\n")
            return
        if make == "":
            self.out_text.insert(END, "Could not add Artist: Missing make!\n")
            return
        if model == "":
            self.out_text.insert(END, "Could not add Artist: Missing model!\n")
            return

        # TODO Artist can have multiple cameras, so a different check is needed
        # TODO have cameras be time dependend on artist, maybe the person did change the camera
        # if not self.has_elem("artists", "name", name):
        self.conn.execute(
            "INSERT INTO artists (name, make, model) VALUES (?, ?, ?)", (name, make, model)
        )
        self.conn.commit()
        self.out_text.insert(END, f"Artist {name} was added.\n")
        # else:
        #     self.out_text.insert(END, f"Artist {name} was already there, could NOT add.\n")

    def insert_artists(self, file):
        with open(file) as json_file:
            data = json.load(json_file)
            for artist in data["artists"]:
                self.insert_artist(
                    artist["name"],
                    artist["make"],
                    artist["model"],
                )

    def delete_artist(self, name):
        self.delete_one("artists", "name", name)

    def clean_artists(self):
        self.conn.execute("DROP TABLE IF EXISTS artists")

        self.conn.execute(
            "CREATE TABLE IF NOT EXISTS artists (name STRING, make STRING, model STRING)"
        )

        self.out_text.insert(END, "All artist entrys were deleted.\n")

    def save_artists(self, file):
        data = self.get_all_from_table("artists")
        json_data = {"artists": []}
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

    def get_artist(self, make, model):
        cur = self.conn.execute("SELECT name FROM artists WHERE make=? AND model=?", (make, model))
        result = cur.fetchall()
        cur.close()
        return result

    def print_artists(self):
        self.print_table("artists")
