from datetime import datetime
from idlelib.tooltip import Hovertip
from tkinter import DISABLED, NORMAL, Button, Label, StringVar
from tkinter.ttk import Combobox, Separator

from database import Database
from dateutils import TimeFrameSelector
from debug_messages import WarningArray, WarningCodes
from guiboxes.basebox import PAD_X, PAD_Y, PAD_Y_LBL, SEPARATOR, BaseBox
from helper import center_window, limit_input, test_time_frame, test_time_frame_swap
from tooltips import TooltipDict


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

    def __init__(
        self,
        header: str,
        db: Database,
        part_list,
        startdate_parent: datetime,
        enddate_parent: datetime,
    ):
        """
        Create a GUI element that includes a combobox for the participant name,
        and a time frame selector for start and end date.
        """
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
        self.lbl_warning.grid(
            row=self.row(), column=2, columnspan=2, padx=PAD_X, pady=PAD_Y_LBL, sticky="E"
        )

        ##########################
        # Participant data input #
        ##########################
        # Get a list of all persons to select from
        list_persons = [x[1] for x in db.get_all("persons")]

        lbl_p_name = Label(self.root, text="Name: ")
        lbl_p_name.grid(row=self.row_idx, column=0, padx=PAD_X, pady=PAD_Y, sticky="EW")
        self.sv_p_name = StringVar()
        self.sv_p_name.set(self.name)
        self.sv_p_name.trace_add("write", self.validate_input)
        cb_part_person = self.add_cmp(
            "cb_part_person",
            Combobox(self.root, textvariable=self.sv_p_name, validate="key", validatecommand=vcmd),
        )
        # List of available persons
        cb_part_person["values"] = list_persons
        # Place the widget
        cb_part_person.grid(
            row=self.row(), column=1, columnspan=3, padx=PAD_X, pady=PAD_Y, sticky="EW"
        )
        Hovertip(cb_part_person, TooltipDict["cb_part_person"])

        #####################
        # TimeFrameSelector #
        #####################
        tfs_part = self.add_cmp(
            "tfs_part",
            TimeFrameSelector(self.root, self.row_idx, startdate_parent, enddate_parent),
        )
        tfs_part.set_start_date(startdate_parent)
        tfs_part.set_end_date(enddate_parent)
        self.row_idx += 2

        # Bind after setting the values to avoid triggering the callback
        tfs_part.bind(self.validate_input)

        separator = Separator(self.root, orient="horizontal")
        separator.grid(row=self.row(), column=0, columnspan=4, padx=PAD_X, pady=PAD_Y, sticky="EW")

        #########################
        # Add and abort buttons #
        #########################
        btn_abort = self.add_cmp(
            "btn_abort",
            Button(
                self.root,
                text="Abort",
                command=self.close,
            ),
        )
        btn_abort.grid(row=self.row_idx, column=1, padx=PAD_X, pady=PAD_Y, sticky="EW")
        Hovertip(btn_abort, TooltipDict["btn_abort"])

        btn_add = self.add_cmp(
            "btn_add",
            Button(
                self.root,
                text="Add",
                command=self.add,
                state="disabled",
            ),
        )
        btn_add.grid(row=self.row(), column=3, padx=PAD_X, pady=PAD_Y, sticky="EW")
        Hovertip(btn_add, TooltipDict["btn_add_part"])

        center_window(self.root)

        # Making MessageBox Visible
        self.root.wait_window()

    def validate_input(self, *args):
        """
        Test if the values of all input fields are valid
        and disable the add button in case they are not.
        """
        name = self.sv_p_name.get()
        if not name:
            self.set_cmp_state("btn_add", DISABLED)
            self.lbl_warning.config(text=WarningArray[WarningCodes.WARNING_MISSING_DATA])
            return

        # In case the person does not yet exist there can not be any overlap
        if not self.db.has("persons", ("name", name)):
            self.set_cmp_state("btn_add", NORMAL)
            self.lbl_warning.config(text=WarningArray[WarningCodes.NO_WARNING])
            return

        start_date = self.get_cmp("tfs_part").get_start_date()
        end_date = self.get_cmp("tfs_part").get_end_date()

        if err := test_time_frame_swap(start_date, end_date):
            self.set_cmp_state("btn_add", DISABLED)
            self.lbl_warning.config(text=WarningArray[err])
            return

        # Since a person can not be at two places at once all participant entries
        # with the same person name are checked if they have overlapping time dates
        if err := self.db.test_participant_time_frame(self.sv_p_name.get(), start_date, end_date):
            self.set_cmp_state("btn_add", DISABLED)
            self.lbl_warning.config(text=WarningArray[err])
            return

        for part in self.part_list:
            part_data = part.split(SEPARATOR)
            if part_data[0] == self.sv_p_name.get():
                testdate_start = datetime.fromisoformat(part_data[1])
                testdate_end = datetime.fromisoformat(part_data[2])

                # Check if start date lies in time frame
                if err := test_time_frame(start_date, end_date, testdate_start, testdate_end):
                    self.set_cmp_state("btn_add", DISABLED)
                    self.lbl_warning.config(text=WarningArray[err])
                    return

        self.set_cmp_state("btn_add", NORMAL)
        self.lbl_warning.config(text=WarningArray[WarningCodes.NO_WARNING])

    def add(self):
        """
        Use the input data to create a new participant and save it in a variable.
        The result can be accessed from the outside (for example from the eventbox).
        """
        start_date = self.get_cmp("tfs_part").get_start_date()
        end_date = self.get_cmp("tfs_part").get_end_date()

        # Add participant
        self.participant = f"{self.sv_p_name.get()}{SEPARATOR}{start_date}{SEPARATOR}{end_date}"
        self.changed = True
        self.close()
