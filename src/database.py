import sqlite3
import json


class Database:
    def __init__(self, path="database.db"):
        self.conn = sqlite3.connect(path)
        self.conn.execute('CREATE TABLE IF NOT EXISTS events (title STRING, s_year INT, s_month INT, s_day INT, e_year INT, e_month INT, e_day INTT)')
        self.conn.commit()

    def clean(self):
        self.conn.execute("DROP TABLE IF EXISTS events")

    def insert_event(self, title, s_year, s_month, s_day, e_year, e_month, e_day):
        # TODO check if event already there
        self.conn.execute(
            "INSERT INTO events (title, s_year, s_month, s_day, e_year, e_month, e_day) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (title, s_year, s_month, s_day, e_year, e_month, e_day)
        )

    # TODO why src?
    def insert_events(self, file="src/events.json"):
        with open(file) as json_file:
            data = json.load(json_file)
            for event in data["events"]:
                self.insert_event(
                    event["title"],
                    event["start"]["year"], event["start"]["month"], event["start"]["day"],
                    event["end"]["year"], event["end"]["month"], event["end"]["day"]
                )
        self.conn.commit()

    # TODO dump events to file
    #def save_events(self, file="src/events.json"):

    def delete_event(self, title):
        self.conn.execute("DELETE FROM events WHERE title=?", (title))

    def get_event(self, year, month, day):
        cur = self.conn.execute(
            "SELECT title FROM events WHERE s_year<=? AND s_month<=? AND s_day<=? AND e_year>=? AND e_month>=? AND e_day>=?",
            (year, month, day, year, month, day)
        )
        result = cur.fetchall()
        cur.close()
        return result
