import datetime

from tkinter import Button, Label

from tkinter import (
    Button,
    Entry,
    Label,
    StringVar,
)
from tkinter.ttk import Separator

from helper import center_window, test_time_frame, test_time_frame_swap, limit_input

from idlelib.tooltip import Hovertip
from tooltips import TooltipDict
from debug_messages import WarningArray, WarningCodes
from dateutils import TimeFrameSelector
from guiboxes.basebox import BaseBox, PAD_X, PAD_Y, PAD_Y_LBL


class ModifySubeventBox(BaseBox):
    def __init__(self, header, db, subevent_list, startdate_parent, enddate_parent):
        super().__init__(header)

        # Save the database
        self.db = db
        # List of all subevents, for overlap tests
        self.subevent_list = subevent_list
        # Register the character input check only once for this widget
        vcmd = (self.root.register(limit_input), "%S")
        # Save the data of the subevent
        self.subevent = ""
        # Initial value of the subevent title
        subevent_title = ""

        ###############
        # Header Line #
        ###############
        lbl_header = Label(self.root, text="Fill all cells to add the subevent.")
        lbl_header.grid(row=self.row_idx, column=1, padx=PAD_X, pady=PAD_Y_LBL, sticky="W")
        self.lbl_warning = Label(self.root, fg="#a00", text="")
        self.lbl_warning.grid(row=self.row(), column=2, columnspan=2, padx=PAD_X, pady=PAD_Y_LBL, sticky="E")

        ###############
        # Title input #
        ###############
        self.sv_se_title = StringVar()
        self.sv_se_title.set(subevent_title)
        self.sv_se_title.trace("w", self.validate_input)
        lbl_se_title = Label(self.root, text="Title: ")
        lbl_se_title.grid(row=self.row_idx, column=0, padx=PAD_X, pady=PAD_Y, sticky="W")
        ent_se_title = Entry(self.root, textvariable=self.sv_se_title, validate="key", validatecommand=vcmd)
        ent_se_title.grid(row=self.row(), column=1, columnspan=3, padx=PAD_X, pady=PAD_Y, sticky="EW")
        Hovertip(ent_se_title, TooltipDict["ent_se_title"])

        #####################
        # TimeFrameSelector #
        #####################
        self.tfs = TimeFrameSelector(self.root, self.row_idx, startdate_parent, enddate_parent)
        self.tfs.set_start_date(startdate_parent)
        self.tfs.set_end_date(enddate_parent)
        self.row_idx += 2
        
        # Bind after setting the values to avoid triggering the callback
        self.tfs.bind(self.validate_input)

        separator = Separator(self.root, orient="horizontal")
        separator.grid(row=self.row(), column=0, columnspan=4, padx=PAD_X, pady=PAD_Y, sticky="EW")

        #########################
        # Add and abort buttons #
        #########################
        btn_abort = Button(
            self.root,
            text="Abort",
            command=self.close,
        )
        btn_abort.grid(row=self.row_idx, column=1, padx=PAD_X, pady=PAD_Y, sticky="EW")
        Hovertip(btn_abort, TooltipDict["btn_abort"])

        self.btn_add = Button(
            self.root,
            text="Add",
            command=self.add,
            state="disabled",
        )
        self.btn_add.grid(row=self.row(), column=3, padx=PAD_X, pady=PAD_Y, sticky="EW")
        Hovertip(self.btn_add, TooltipDict["btn_add_sube"])

        center_window(self.root)

        # Making MessageBox Visible
        self.root.wait_window()

    def validate_input(self, *args):
        if self.sv_se_title.get():
            self.btn_add.config(state="normal")
        else:
            self.btn_add.config(state="disabled")

        # Disable button in case some cells are not yet filled
        # (Date and time cells have always atleast some value)
        if not self.sv_se_title.get():
            self.btn_add.config(state="disabled")
            self.lbl_warning.config(text = WarningArray[WarningCodes.WARNING_MISSING_DATA])
            return

        start_date = self.tfs.get_start_date()
        end_date = self.tfs.get_end_date()

        if err:= test_time_frame_swap(start_date, end_date):
            self.btn_add.config(state="disabled")
            self.lbl_warning.config(text = WarningArray[err])
            return

        # Test all subevents of the list, to check if there are two subevents with 
        # the same time frame, which is not allowed
        for subevent in self.subevent_list:
            subevent_data = subevent.split(" | ")
            testdate_start = datetime.datetime.strptime(subevent_data[1], "%Y-%m-%d %H:%M:%S")
            testdate_end = datetime.datetime.strptime(subevent_data[2], "%Y-%m-%d %H:%M:%S")

            # Test for overlapping time frames
            if err := test_time_frame(testdate_start, testdate_end, start_date, end_date):
                self.btn_add.config(state="disabled")
                self.lbl_warning.config(text = WarningArray[err])
                return

        self.btn_add.config(state="normal")
        self.lbl_warning.config(text = WarningArray[WarningCodes.NO_WARNING])

    def add(self):
        start_date = self.tfs.get_start_date()
        end_date = self.tfs.get_end_date()

        self.subevent = self.sv_se_title.get() + " | " + str(start_date) + " | " + str(end_date)
        self.changed = True
        self.close()
