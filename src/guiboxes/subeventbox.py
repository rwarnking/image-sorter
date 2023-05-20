from datetime import datetime
from idlelib.tooltip import Hovertip
from tkinter import Button, Entry, Label, StringVar
from tkinter.ttk import Separator

from database import Database
from dateutils import TimeFrameSelector
from debug_messages import WarningArray, WarningCodes
from guiboxes.basebox import PAD_X, PAD_Y, PAD_Y_LBL, BaseBox
from helper import center_window, limit_input, test_time_frame, test_time_frame_swap
from tooltips import TooltipDict


class ModifySubeventBox(BaseBox):
    def __init__(
        self,
        header: str,
        db: Database,
        subevent_list: list[str],
        startdate_parent: datetime,
        enddate_parent: datetime,
    ):
        """
        Create a GUI element that includes a input field for the subevent title,
        and a time frame selector for start and end date.
        """
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
        self.lbl_warning.grid(
            row=self.row(), column=2, columnspan=2, padx=PAD_X, pady=PAD_Y_LBL, sticky="E"
        )

        ###############
        # Title input #
        ###############
        self.sv_se_title = StringVar()
        self.sv_se_title.set(subevent_title)
        self.sv_se_title.trace("w", self.validate_input)
        lbl_se_title = Label(self.root, text="Title: ")
        lbl_se_title.grid(row=self.row_idx, column=0, padx=PAD_X, pady=PAD_Y, sticky="W")
        ent_se_title = Entry(
            self.root, textvariable=self.sv_se_title, validate="key", validatecommand=vcmd
        )
        ent_se_title.grid(
            row=self.row(), column=1, columnspan=3, padx=PAD_X, pady=PAD_Y, sticky="EW"
        )
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
        """
        Test if the values of all input fields are valid
        and disable the add button in case they are not.
        """
        if self.sv_se_title.get():
            self.btn_add.config(state="normal")
        else:
            self.btn_add.config(state="disabled")

        # Disable button in case some cells are not yet filled
        # (Date and time cells have always atleast some value)
        if not self.sv_se_title.get():
            self.btn_add.config(state="disabled")
            self.lbl_warning.config(text=WarningArray[WarningCodes.WARNING_MISSING_DATA])
            return

        start_date = self.tfs.get_start_date()
        end_date = self.tfs.get_end_date()

        if err := test_time_frame_swap(start_date, end_date):
            self.btn_add.config(state="disabled")
            self.lbl_warning.config(text=WarningArray[err])
            return

        # Test all subevents of the list, to check if there are two subevents with
        # the same time frame, which is not allowed
        for subevent in self.subevent_list:
            subevent_data = subevent.split(" | ")
            testdate_start = datetime.fromisoformat(subevent_data[1])
            testdate_end = datetime.fromisoformat(subevent_data[2])

            # Test for overlapping time frames
            if err := test_time_frame(testdate_start, testdate_end, start_date, end_date):
                self.btn_add.config(state="disabled")
                self.lbl_warning.config(text=WarningArray[err])
                return

        self.btn_add.config(state="normal")
        self.lbl_warning.config(text=WarningArray[WarningCodes.NO_WARNING])

    def add(self):
        """
        Use the input data to create a new subevent and save it in a variable.
        The result can be accessed from the outside (for example from the eventbox).
        """
        start_date = self.tfs.get_start_date()
        end_date = self.tfs.get_end_date()

        self.subevent = self.sv_se_title.get() + " | " + str(start_date) + " | " + str(end_date)
        self.changed = True
        self.close()
