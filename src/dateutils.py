import datetime
from idlelib.tooltip import Hovertip
from tkinter import DISABLED, NORMAL, Frame, Label, StringVar, Toplevel
from tkinter.ttk import Spinbox
from typing import Any, Callable, Optional, Union

from guiboxes.basebox import PAD_X, PAD_Y
from tkcalendar import DateEntry
from tooltips import TooltipDict


class Selector:
    """Wrapper for a spinbox component."""

    def __init__(self, root: Union[Frame, Toplevel], from_val: int, to_val: int, w: int):
        """Create a selector for selecting one spinbox value."""
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
        """Get the value of the spinbox."""
        return int(self.sv.get())

    def set(self, val: Union[int, str]):
        """Set the value of the spinbox."""
        self.sv.set(str(val))

    def addTooltip(self, msg: str):
        """Add a tooltip string to the spinbox."""
        Hovertip(self.sb, msg)

    def bind(self, callback: Callable):
        """Bind a callback to the spinbox."""
        self.sv.trace_add("write", callback)

    def enable(self):
        self.sb["state"] = "readonly"

    def disable(self):
        self.sb["state"] = DISABLED


class DaySelectorM(Selector):
    """Special type of selector for a day of a year (including minus numbers)."""

    def __init__(self, root: Frame, current: int = 0, w: int = 20):
        super().__init__(root, -365 * 1000, 365 * 1000, w)
        self.set(current)


class HourSelector(Selector):
    """Special type of selector for an hour of a day (NOT including minus numbers)."""

    def __init__(self, root: Toplevel, current: int = 0, w: int = 20):
        super().__init__(root, 0, 23, w)
        self.set(current)


class HourSelectorM(Selector):
    """Special type of selector for an hour of a day (including minus numbers)."""

    def __init__(self, root: Frame, current: int = 0, w: int = 20):
        super().__init__(root, -23, 23, w)
        self.set(current)


class MinuteSelector(Selector):
    """Special type of selector for a minute of an hour (NOT including minus numbers)."""

    def __init__(self, root: Toplevel, current: int = 0, w: int = 20):
        super().__init__(root, 0, 59, w)
        self.set(current)


class MinuteSelectorM(Selector):
    """Special type of selector for a minute of an hour (including minus numbers)."""

    def __init__(self, root: Frame, current: int = 0, w: int = 20):
        super().__init__(root, -59, 59, w)
        self.set(current)


class SecondSelectorM(Selector):
    """Special type of selector for a second of a minute (including minus numbers)."""

    def __init__(self, root: Frame, current: int = 0, w: int = 20):
        super().__init__(root, -59, 59, w)
        self.set(current)


class DateSelector:
    """Wrapper for selecting a complete date via a dateentry & hour/minute selector."""

    def __init__(self, root: Toplevel, data: dict[str, Any]):
        """
        Create the components for the dateselector: a dateentry, a hour- and minute selector.
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

    def bind(self, callback: Callable):
        """Bind callback to hour and minute selector."""
        self.date_entry.bind("<<DateEntrySelected>>", callback)
        self.date_entry.bind("<KeyRelease>", callback)

        self.hs.bind(callback)
        self.ms.bind(callback)

    def enable(self):
        self.date_entry["state"] = NORMAL
        self.hs.enable()
        self.ms.enable()

    def disable(self):
        self.date_entry["state"] = DISABLED
        self.hs.disable()
        self.ms.disable()

    def get_date(self):
        """Get the complete date represented by this dateselector."""
        return datetime.datetime.combine(
            self.get_day(), datetime.datetime.min.time()
        ) + datetime.timedelta(hours=self.get_hour(), minutes=self.get_minute())

    def get_day(self):
        """Get only the day represented by this dateselector."""
        return self.date_entry.get_date()

    def get_hour(self):
        """Get only the hour represented by this dateselector."""
        return self.hs.get()

    def get_minute(self):
        """Get only the minute represented by this dateselector."""
        return self.ms.get()

    def set_date(self, date: datetime.datetime):
        """Set the date of this dateselector via a datetime object."""
        self.date_entry.set_date(date)
        self.set_hour(date.hour)
        self.set_minute(date.minute)

    def set_day(self, day: datetime.datetime):
        """Set only the day of this dateselector via a datetime object."""
        self.date_entry.set_date(day)

    def set_hour(self, hour: int):
        """Set only the hour of this dateselector."""
        self.hs.set(hour)

    def set_minute(self, minute: int):
        """Set only the minute of this dateselector."""
        self.ms.set(minute)


class TimeFrameSelector:
    """Wrapper for a time frame selector component. This includes two dateselector components."""

    def __init__(
        self,
        root: Toplevel,
        row_idx: int,
        date_min: Optional[datetime.datetime] = None,
        date_max: Optional[datetime.datetime] = None,
    ):
        start_data = {
            "row_idx": row_idx,
            "label": "Start",
            "date_min": date_min,
            "date_max": date_max,
            "hour": date_min.hour if date_min else 0,
            "minute": date_min.minute if date_min else 0,
            "tt_date": "date_start",
            "tt_hour": "hs_start",
            "tt_minute": "ms_start",
        }
        self.ds_start = DateSelector(root, start_data)
        self.state = NORMAL

        end_data = {
            "row_idx": row_idx + 1,
            "label": "End",
            "date_min": date_min,
            "date_max": date_max,
            "hour": date_max.hour if date_max else 23,
            "minute": date_max.minute if date_max else 59,
            "tt_date": "date_end",
            "tt_hour": "hs_end",
            "tt_minute": "ms_end",
        }
        self.ds_end = DateSelector(root, end_data)

    def __getitem__(self, key):
        return getattr(self, key)

    def bind(self, callback: Callable):
        """Bind callback to both dateselectors."""
        self.ds_start.bind(callback)
        self.ds_end.bind(callback)

    def config(self, state):
        if state == DISABLED:
            self.ds_start.disable()
            self.ds_end.disable()
        else:
            self.ds_start.enable()
            self.ds_end.enable()

    def enable(self):
        self.ds_start.enable()
        self.ds_end.enable()

    def disable(self):
        self.ds_start.disable()
        self.ds_end.disable()

    def get_start_date(self):
        """Returns the start date of the time frame."""
        return self.ds_start.get_date()

    def get_end_date(self):
        """Returns the end date of the time frame."""
        return self.ds_end.get_date()

    def get_start_day(self):
        """Returns only the start day of the time frame."""
        return self.ds_start.get_day()

    def get_end_day(self):
        """Returns only the end day of the time frame."""
        return self.ds_end.get_day()

    def get_start_hour(self):
        """Returns only the start hour of the time frame."""
        return self.ds_start.get_hour()

    def get_end_hour(self):
        """Returns only the end hour of the time frame."""
        return self.ds_end.get_hour()

    def get_start_minute(self):
        """Returns only the start minute of the time frame."""
        return self.ds_start.get_minute()

    def get_end_minute(self):
        """Returns only the end minute of the time frame."""
        return self.ds_end.get_minute()

    def set_start_date(self, date: datetime.datetime):
        """Set the start date of the time frame via a datetime object."""
        self.ds_start.set_date(date)

    def set_start_date_s(self, date: str):
        """Set the start date of the time frame via a string."""
        self.ds_start.set_date(datetime.datetime.fromisoformat(date))

    def set_end_date(self, date: datetime.datetime):
        """Set the end date of the time frame via a datetime object."""
        self.ds_end.set_date(date)

    def set_end_date_s(self, date: str):
        """Set the end date of the time frame via a string."""
        self.ds_end.set_date(datetime.datetime.fromisoformat(date))

    # def set_start_day(self, day: datetime.datetime):
    #     self.ds_start.set_day(day)

    # def set_end_day(self, day: datetime.datetime):
    #     self.ds_end.set_day(day)

    # def set_start_hour(self, hour: int):
    #     self.ds_start.set_hour(hour)

    # def set_end_hour(self, hour: int):
    #     self.ds_end.set_hour(hour)

    # def set_start_minute(self, minute: int):
    #     self.ds_start.set_minute(minute)

    # def set_end_minute(self, minute: int):
    #     self.ds_end.set_minute(minute)


class TimeShiftSelector:
    """
    Wrapper component for a time shift selector, allowing to define a
    time shift via four selector components - one for each of the following:
    day, hour, minute, second.
    https://pythonguides.com/create-date-time-picker-using-python-tkinter/
    """

    def __init__(self, root: Toplevel, row_idx: int):
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

        self.state = NORMAL

    def __getitem__(self, key):
        return getattr(self, key)

    def bind(self, callback: Callable):
        """Bind callback to all selectors."""
        self.ds.bind(callback)
        self.hs.bind(callback)
        self.ms.bind(callback)
        self.s.bind(callback)

    def config(self, state):
        if state == DISABLED:
            self.ds.disable()
            self.hs.disable()
            self.ms.disable()
            self.s.disable()
        else:
            self.ds.enable()
            self.hs.enable()
            self.ms.enable()
            self.s.enable()

    def get_all(self):
        """Get the value of all selectors as a tuple"""
        return self.get_d(), self.get_h(), self.get_m(), self.get_s()

    def get_d(self):
        """Get only the value of the day selector."""
        return self.ds.get()

    def get_h(self):
        """Get only the value of the hour selector."""
        return self.hs.get()

    def get_m(self):
        """Get only the value of the minute selector."""
        return self.ms.get()

    def get_s(self):
        """Get only the value of the second selector."""
        return self.s.get()

    def set_all(
        self, d: Union[int, str], h: Union[int, str], m: Union[int, str], s: Union[int, str]
    ):
        """Set the value of all selectors."""
        self.set_d(d)
        self.set_h(h)
        self.set_m(m)
        self.set_s(s)

    def set_d(self, value: Union[int, str]):
        """Set only the value of the day selector."""
        self.ds.set(value)

    def set_h(self, value: Union[int, str]):
        """Set only the value of the hour selector."""
        self.hs.set(value)

    def set_m(self, value: Union[int, str]):
        """Set only the value of the minute selector."""
        self.ms.set(value)

    def set_s(self, value: Union[int, str]):
        """Set only the value of the second selector."""
        self.s.set(value)

    def to_string(self):
        """Return the value of all selectors as a string."""
        return (
            str(self.get_d())
            + ":"
            + str(self.get_h())
            + ":"
            + str(self.get_m())
            + ":"
            + str(self.get_s())
        )
