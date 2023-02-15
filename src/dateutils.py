import datetime

from tkinter import Button, Checkbutton, Label, Toplevel

from tkinter import (
    END,
    HORIZONTAL,
    RIGHT,
    Button,
    Entry,
    Frame,
    Label,
    StringVar,
    Text,
    Tk,
    filedialog,
    messagebox,
)
from tkinter.ttk import Checkbutton, Combobox, Progressbar, Scrollbar, Separator, Spinbox
from idlelib.tooltip import Hovertip
from tkcalendar import DateEntry
from tooltips import TooltipDict

from guiboxes.basebox import PAD_X, PAD_Y


class Selector:
    def __init__(self, root, from_val: int, to_val: int, w: int):
        self.sv = StringVar()
        self.sv.set("0")
        self.sb = Spinbox(
            root,
            from_=from_val,
            to=to_val,
            textvariable=self.sv,
            justify="left",
            state="readonly",
            width=w,
        )

    def get(self):
        return int(self.sv.get())

    def set(self, val: int):
        self.sv.set(str(val))

    def addTooltip(self, msg: str):
        Hovertip(self.sb, msg)

    def bind(self, callback):
        self.sv.trace("w", callback)

class DaySelectorM(Selector):
    def __init__(self, root, current: int = 0, w: int = 20):
        super().__init__(root, -365*1000, 365*1000, w)
        self.set(current)

class HourSelector(Selector):
    def __init__(self, root, current: int = 0, w: int = 20):
        super().__init__(root, 0, 23, w)
        self.set(current)

class HourSelectorM(Selector):
    def __init__(self, root, current: int = 0, w: int = 20):
        super().__init__(root, -23, 23, w)
        self.set(current)

class MinuteSelector(Selector):
    def __init__(self, root, current: int = 0, w: int = 20):
        super().__init__(root, 0, 59, w)
        self.set(current)

class MinuteSelectorM(Selector):
    def __init__(self, root, current: int = 0, w: int = 20):
        super().__init__(root, -59, 59, w)
        self.set(current)

class SecondSelectorM(Selector):
    def __init__(self, root, current: int = 0, w: int = 20):
        super().__init__(root, -59, 59, w)
        self.set(current)

class DateSelector:
    def __init__(self, root, data):
        """
        https://stackoverflow.com/questions/4443786/how-do-i-create-a-date-picker-in-tkinter
        """
        # Date
        lbl_date = Label(root, text=data["label"] + ": ")
        lbl_date.grid(row=data["row_idx"], column=0, padx=PAD_X, pady=PAD_Y, sticky="W")
        self.date_entry = DateEntry(
            root, 
            width=12, 
            background="darkblue", 
            foreground="white", 
            borderwidth=2, 
            date_pattern="mm/dd/yyyy", 
            mindate=data["date_min"], 
            maxdate=data["date_max"],
        )
        self.date_entry.grid(row=data["row_idx"], column=1, padx=PAD_X, pady=PAD_Y, sticky="EW")
        Hovertip(self.date_entry, TooltipDict[data["tt_date"]])

        # Hour
        self.hs = HourSelector(root, data["hour"])
        self.hs.sb.grid(row=data["row_idx"], column=2, padx=PAD_X, pady=PAD_Y, sticky="EW")
        self.hs.addTooltip(TooltipDict[data["tt_hour"]])

        # Minute
        self.ms = MinuteSelector(root, data["minute"])
        self.ms.sb.grid(row=data["row_idx"], column=3, padx=PAD_X, pady=PAD_Y, sticky="EW")
        self.ms.addTooltip(TooltipDict[data["tt_minute"]])

    def bind(self, callback):
        self.date_entry.bind("<<DateEntrySelected>>", callback)
        self.date_entry.bind("<KeyRelease>", callback)

        self.hs.bind(callback)
        self.ms.bind(callback)

    def get_date(self):
        return datetime.datetime.combine(
            self.get_day(), datetime.datetime.min.time()
        ) + datetime.timedelta(hours=self.get_hour(), minutes=self.get_minute())

    def get_day(self):
        return self.date_entry.get_date()

    def get_hour(self):
        return self.hs.get()

    def get_minute(self):
        return self.ms.get()

    def set_date(self, date):
        self.date_entry.set_date(date)
        self.set_hour(date.hour)
        self.set_minute(date.minute)

    def set_day(self, day):
        self.date_entry.set_date(day)

    def set_hour(self, hour):
        self.hs.set(hour)

    def set_minute(self, minute):
        self.ms.set(minute)

class TimeFrameSelector:
    def __init__(self, root, row_idx, date_min=None, date_max=None):
        start_data = {
            "row_idx": row_idx, 
            "label": "Start",
            "date_min": date_min,
            "date_max": date_max,
            "hour": 0,
            "minute": 0,
            "tt_date": "date_se_start",
            "tt_hour": "hs_se_start",
            "tt_minute": "ms_se_start",
        }
        self.ds_start = DateSelector(root, start_data)

        end_data = {
            "row_idx": row_idx + 1, 
            "label": "End",
            "date_min": date_min,
            "date_max": date_max,
            "hour": 23,
            "minute": 59,
            "tt_date": "date_se_end",
            "tt_hour": "hs_se_end",
            "tt_minute": "ms_se_end",
        }
        self.ds_end = DateSelector(root, end_data)

    def bind(self, callback):
        self.ds_start.bind(callback)
        self.ds_end.bind(callback)

    def get_start_date(self):
        return self.ds_start.get_date()

    def get_end_date(self):
        return self.ds_end.get_date()

    def get_start_day(self):
        return self.ds_start.get_day()

    def get_end_day(self):
        return self.ds_end.get_day()

    def get_start_hour(self):
        return self.ds_start.get_hour()

    def get_end_hour(self):
        return self.ds_end.get_hour()

    def get_start_minute(self):
        return self.ds_start.get_minute()

    def get_end_minute(self):
        return self.ds_end.get_minute()

    def set_start_date(self, date):
        self.ds_start.set_date(date)

    def set_start_date(self, date: str, pattern: str):
        self.ds_start.set_date(datetime.datetime.strptime(date, pattern))

    def set_end_date(self, date):
        self.ds_end.set_date(date)

    def set_end_date(self, date: str, pattern: str):
        self.ds_end.set_date(datetime.datetime.strptime(date, pattern))

    # def set_start_day(self, day):
    #     self.ds_start.set_day(day)

    # def set_end_day(self, day):
    #     self.ds_end.set_day(day)

    # def set_start_hour(self, hour):
    #     self.ds_start.set_hour(hour)

    # def set_end_hour(self, hour):
    #     self.ds_end.set_hour(hour)

    # def set_start_minute(self, minute):
    #     self.ds_start.set_minute(minute)

    # def set_end_minute(self, minute):
    #     self.ds_end.set_minute(minute)

class TimeShiftSelector:
    """
    https://pythonguides.com/create-date-time-picker-using-python-tkinter/
    """
    def __init__(self, root, row_idx):
        lbl_tshift = Label(root, text="Timeshift: ")
        lbl_tshift.grid(row=row_idx, column=0, padx=PAD_X, pady=PAD_Y, sticky="W")
        frame_tshift = Frame(root)
        frame_tshift.grid(row=row_idx, column=1, columnspan=3, padx=PAD_X, pady=PAD_Y, sticky="EW")

        # Day
        lbl_d = Label(frame_tshift, text="Days: ")
        lbl_d.pack(side="left", fill="x", expand=1)
        self.ds = DaySelectorM(frame_tshift, 0, 3)
        self.ds.sb.pack(side="left", fill="x", expand=1)
        self.ds.addTooltip(TooltipDict["sp_a_shift"])

        # Hour
        lbl_h = Label(frame_tshift, text="Hours: ")
        lbl_h.pack(side="left", fill="x", expand=1)
        self.hs = HourSelectorM(frame_tshift, 0, 3)
        self.hs.sb.pack(side="left", fill="x", expand=1)
        self.hs.addTooltip(TooltipDict["sp_a_shift"])

        # Minute
        lbl_m = Label(frame_tshift, text="Minutes: ")
        lbl_m.pack(side="left", fill="x", expand=1)
        self.ms = MinuteSelectorM(frame_tshift, 0, 3)
        self.ms.sb.pack(side="left", fill="x", expand=1)
        self.ms.addTooltip(TooltipDict["sp_a_shift"])

        # Seconds
        lbl_s = Label(frame_tshift, text="Seconds: ")
        lbl_s.pack(side="left", fill="x", expand=1)
        self.s = SecondSelectorM(frame_tshift, 0, 3)
        self.s.sb.pack(side="left", fill="x", expand=1)
        self.s.addTooltip(TooltipDict["sp_a_shift"])

    def bind(self, callback):
        self.ds.bind(callback)
        self.hs.bind(callback)
        self.ms.bind(callback)
        self.s.bind(callback)

    def get_all(self):
        return self.get_d(), self.get_h(), self.get_m(), self.get_s()

    def get_d(self):
        return self.ds.get()

    def get_h(self):
        return self.hs.get()

    def get_m(self):
        return self.ms.get()

    def get_s(self):
        return self.s.get()

    def set_all(self, d, h, m, s):
        self.set_d(d)
        self.set_h(h)
        self.set_m(m)
        self.set_s(s)

    def set_d(self, value):
        self.ds.set(value)

    def set_h(self, value):
        self.hs.set(value)

    def set_m(self, value):
        self.ms.set(value)

    def set_s(self, value):
        self.s.set(value)

    def to_string(self):
        return (
            str(self.get_d()) + ":" +
            str(self.get_h()) + ":" +
            str(self.get_m()) + ":" +
            str(self.get_s())
        )