import json
import sqlite3


class Database:
    def __init__(self, path="database.db"):
        self.conn = sqlite3.connect(path)
        self.conn.execute(
            "CREATE TABLE IF NOT EXISTS events (title STRING, s_year INT, s_month INT, \
            s_day INT, e_year INT, e_month INT, e_day INTT)"
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
            s_day INT, e_year INT, e_month INT, e_day INTT)"
        )
        self.conn.execute(
            "CREATE TABLE IF NOT EXISTS artists (name STRING, make STRING, model STRING)"
        )

        print("All table entrys were deleted.")

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
        if self.has_elem(table, attr, var):
            query = f"DELETE FROM {table} WHERE {attr}=?"
            self.conn.execute(query, (var,))
            self.conn.commit()
            print("From table " + table + ", " + var + " was deleted.")
        else:
            print("In table " + table + ", " + var + " was not found.")

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
            print(r)

    #################
    # Event related #
    #################
    def insert_event_from_date(self, title, start_date, end_date):
        # TODO
        if end_date < start_date:
            print("Could not add Event: end date < start date!")
            return
        if title == "":
            print("Could not add Event: Missing titel!")
            return

        self.insert_event(
            title,
            start_date.year,
            start_date.month,
            start_date.day,
            end_date.year,
            end_date.month,
            end_date.day,
        )

    def insert_event(self, title, s_year, s_month, s_day, e_year, e_month, e_day):
        if not self.has_elem("events", "title", title):
            title = title.replace(" ", "")
            self.conn.execute(
                "INSERT INTO events (title, s_year, s_month, s_day, e_year, e_month, e_day) \
                VALUES (?, ?, ?, ?, ?, ?, ?)",
                (title, s_year, s_month, s_day, e_year, e_month, e_day),
            )
            self.conn.commit()
            print("Event " + title + " was added.")
        else:
            print("Event " + title + " was already there, could NOT add.")

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
                )

    def delete_event(self, title):
        title = title.replace(" ", "")
        self.delete_one("events", "title", title)

    def clean_events(self):
        self.conn.execute("DROP TABLE IF EXISTS events")

        self.conn.execute(
            "CREATE TABLE IF NOT EXISTS events (title STRING, s_year INT, s_month INT, \
            s_day INT, e_year INT, e_month INT, e_day INTT)"
        )

        print("All event entrys were deleted.")

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
                }
            )

        with open(file, "w") as outfile:
            json.dump(json_data, outfile, indent=4)
        print("Events were saved to file " + file + ".")

    def get_event(self, year, month, day):
        cur = self.conn.execute(
            "SELECT title FROM events WHERE s_year<=? AND s_month<=? AND s_day<=? AND e_year>=? \
            AND e_month>=? AND e_day>=?",
            (year, month, day, year, month, day),
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
        if not self.has_elem("artists", "name", name):
            self.conn.execute(
                "INSERT INTO artists (name, make, model) VALUES (?, ?, ?)", (name, make, model)
            )
            self.conn.commit()
            print("Artist " + name + " was added.")
        else:
            print("Artist " + name + " was already there, could NOT add.")

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

        print("All artist entrys were deleted.")

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
        print("Artists were saved to file " + file + ".")

    def get_artist(self, make, model):
        cur = self.conn.execute("SELECT name FROM artists WHERE make=? AND model=?", (make, model))
        result = cur.fetchall()
        cur.close()
        return result

    def print_artists(self):
        self.print_table("artists")
