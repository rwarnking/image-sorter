import sqlite3
import json


class Database:
    def __init__(self, path="database.db"):
        self.conn = sqlite3.connect(path)
        self.conn.execute('CREATE TABLE IF NOT EXISTS events (title STRING, s_year INT, s_month INT, s_day INT, e_year INT, e_month INT, e_day INTT)')
        self.conn.commit()

    def clean(self):
        self.conn.execute("DROP TABLE IF EXISTS events")
        self.conn.execute('CREATE TABLE IF NOT EXISTS events (title STRING, s_year INT, s_month INT, s_day INT, e_year INT, e_month INT, e_day INTT)')
        print("All table entrys were deleted.")

    def has_event(self, title):
        cur = self.conn.execute("SELECT * FROM events WHERE title=?", (title,))
        result = cur.fetchall()
        cur.close()

        return len(result) > 0

    def insert_event_from_date(self, title, start_date, end_date):
        if title == "":
            print("Could not add Event: Missing titel!")
            return

        self.insert_event(
            title,
            start_date.year, start_date.month, start_date.day,
            end_date.year, end_date.month, end_date.day
        )

    def insert_event(self, title, s_year, s_month, s_day, e_year, e_month, e_day):
        if not self.has_event(title):
            self.conn.execute(
                "INSERT INTO events (title, s_year, s_month, s_day, e_year, e_month, e_day) VALUES (?, ?, ?, ?, ?, ?, ?)",
                (title, s_year, s_month, s_day, e_year, e_month, e_day)
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
                    event["start"]["year"], event["start"]["month"], event["start"]["day"],
                    event["end"]["year"], event["end"]["month"], event["end"]["day"]
                )

    # TODO improve formatting of output file
    def save_events(self, file):
        data = self.get_all_events()
        json_data = { "events": [] }
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
                    }
                }
            )

        with open(file, "w") as outfile:
            json.dump(json_data, outfile, indent=4)
        print("Events were saved to file " + file + ".")

    def print_events(self):
        cur = self.conn.execute("SELECT * FROM events")
        result = cur.fetchall()
        cur.close()
        for r in result:
            print(r)

    def delete_event(self, title):
        if self.has_event(title):
            self.conn.execute("DELETE FROM events WHERE title=?", (title,))
            print("Event " + title + " was deleted.")
        else:
            print("Event " + title + " was not found.")

    def get_event(self, year, month, day):
        cur = self.conn.execute(
            "SELECT title FROM events WHERE s_year<=? AND s_month<=? AND s_day<=? AND e_year>=? AND e_month>=? AND e_day>=?",
            (year, month, day, year, month, day)
        )
        result = cur.fetchall()
        cur.close()
        return result

    def get_all_events(self):
        cur = self.conn.execute("SELECT * FROM events")
        result = cur.fetchall()
        cur.close()
        return result
