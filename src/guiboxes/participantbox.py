import datetime

from tkinter import Button, Label

from tkinter import (
    Button,
    Label,
    StringVar,
)
from tkinter.ttk import Combobox, Separator

from helper import center_window, test_time_frame, test_time_frame_swap, limit_input

from idlelib.tooltip import Hovertip
from tooltips import TooltipDict
from debug_messages import WarningArray, WarningCodes
from dateutils import TimeFrameSelector

from guiboxes.basebox import BaseBox, PAD_X, PAD_Y, PAD_Y_LBL


class ModifyParticipantBox(BaseBox):
    """
    A participant is a person that attents an event.
    Since it possible for a person to attent after the event
    already started or leave before the event concluded, 
    each participant also has a timeframe for when he attended.

    A participant constist out of a person instead of an artist, since like this:
    1. there can be attending persons, which are not an artist
    2. it is not necessary to have N participants for a person, that 
       uses multiple (N) divices
    """
    def __init__(self, header, db, part_list, startdate_parent, enddate_parent):
        super().__init__(header)

        # Save the database
        self.db = db
        # List of all participants, for overlap tests
        self.part_list = part_list
        # Register the character input check only once for this widget
        vcmd = (self.root.register(limit_input), "%S")
        # Save the data of the participant
        self.participant = ""
        self.name = ""

        ###############
        # Header Line #
        ###############
        lbl_header = Label(self.root, text="Fill all cells to add the participant.")
        lbl_header.grid(row=self.row_idx, column=1, padx=PAD_X, pady=PAD_Y_LBL, sticky="W")
        self.lbl_warning = Label(self.root, fg="#a00", text="")
        self.lbl_warning.grid(row=self.row(), column=2, columnspan=2, padx=PAD_X, pady=PAD_Y_LBL, sticky="E")

        ##########################
        # Participant data input #
        ##########################
        # Get a list of all persons to select from
        list_persons = [
            x[1] for x in db.get_all("persons")
        ]

        lbl_p_name = Label(self.root, text="Name: ")
        lbl_p_name.grid(row=self.row_idx, column=0, padx=PAD_X, pady=PAD_Y, sticky="EW")
        self.sv_p_name = StringVar()
        self.sv_p_name.set(self.name)
        self.sv_p_name.trace("w", self.validate_input)
        cb_part_person = Combobox(self.root, textvariable=self.sv_p_name, validate="key", validatecommand=vcmd)
        # Write file signatures
        cb_part_person["values"] = list_persons
        # Place the widget
        cb_part_person.grid(
            row=self.row(), column=1, columnspan=3, padx=PAD_X, pady=PAD_Y, sticky="EW"
        )
        Hovertip(cb_part_person, TooltipDict["cb_part_person"])

        #####################
        # TimeFrameSelector #
        #####################
        self.tfs = TimeFrameSelector(self.root, self.row_idx, startdate_parent, enddate_parent)
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
        Hovertip(self.btn_add, TooltipDict["btn_add_part"])

        center_window(self.root)

        # Making MessageBox Visible
        self.root.wait_window()

    def validate_input(self, *args):
        name = self.sv_p_name.get()
        if not name:
            self.btn_add.config(state="disabled")
            self.lbl_warning.config(text = WarningArray[WarningCodes.WARNING_MISSING_DATA])
            return

        # In case the person does not yet exist there can not be any overlap
        if not self.db.has("persons", ("name", name)):
            self.btn_add.config(state="normal")
            self.lbl_warning.config(text = WarningArray[WarningCodes.NO_WARNING])
            return
    
        start_date = self.tfs.get_start_date()
        end_date = self.tfs.get_end_date()

        if err:= test_time_frame_swap(start_date, end_date):
            self.btn_add.config(state="disabled")
            self.lbl_warning.config(text = WarningArray[err])
            return

        # Since a person can not be at two places at once all participant entries
        # with the same person name are checked if they have overlapping time dates
        if err := self.db.test_participant_time_frame(self.sv_p_name.get(), start_date, end_date):
            self.btn_add.config(state="disabled")
            self.lbl_warning.config(text = WarningArray[err])
            return

        for part in self.part_list:
            part_data = part.split(" | ")
            if part_data[0] == self.sv_p_name.get():
                testdate_start = datetime.datetime.strptime(part_data[1], "%Y-%m-%d %H:%M:%S")
                testdate_end = datetime.datetime.strptime(part_data[2], "%Y-%m-%d %H:%M:%S")

                # Check if start date lies in time frame
                if err := test_time_frame(start_date, end_date, testdate_start, testdate_end):
                    self.btn_add.config(state="disabled")
                    self.lbl_warning.config(text = WarningArray[err])
                    return

        self.btn_add.config(state="normal")
        self.lbl_warning.config(text = WarningArray[WarningCodes.NO_WARNING])

    def add(self):
        start_date = self.tfs.get_start_date()
        end_date = self.tfs.get_end_date()

        # Add participant
        self.participant = self.sv_p_name.get() + " | " + str(start_date) + " | " + str(end_date)
        self.changed = True
        self.close()
