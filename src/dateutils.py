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

class Selector:
    def __init__(self, root, from_val: int, to_val: int):
        self.sv = StringVar()
        self.sv.set("0")
        self.sb = Spinbox(
            root,
            from_=from_val,
            to=to_val,
            textvariable=self.sv,
            justify="left",
            state="readonly",
        )

    def get(self):
        return int(self.sv.get())

    def set(self, val: int):
        self.sv.set(str(val))

    def addTooltip(self, msg: str):
        Hovertip(self.sb, msg)

class HourSelector(Selector):
    def __init__(self, root, current: int = 0):
        Selector.__init__(self, root, 0, 23)
        self.set(current)

class MinuteSelector(Selector):
    def __init__(self, root, current: int = 0):
        Selector.__init__(self, root, 0, 59)
        self.set(current)
