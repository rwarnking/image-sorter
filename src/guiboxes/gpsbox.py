from datetime import datetime
from idlelib.tooltip import Hovertip
from tkinter import DISABLED, NORMAL, Button, Entry, Label, StringVar
from tkinter.ttk import Separator

from database import Database
from dateutils import TimeFrameSelector
from debug_messages import WarningArray, WarningCodes
from guiboxes.basebox import PAD_X, PAD_Y, PAD_Y_LBL, SEPARATOR, BaseBox
from helper import center_window, limit_input, limit_input_float, test_time_frame, test_time_frame_swap
from tooltips import TooltipDict


class ModifyGPSBox(BaseBox):
    def __init__(
        self,
        header: str,
        db: Database,
        gps_list: list[str],
        startdate_parent: datetime,
        enddate_parent: datetime,
    ):
        """
        Create a GUI element that includes a input field for the location name,
        a time frame selector for start and end date and a GPS coordinate.
        """
        super().__init__(header)

        # Save the database
        self.db = db
        # List of all GPS coordinates, for overlap tests
        self.gps_list = gps_list
        # Register the character input check only once for this widget
        vcmd = (self.root.register(limit_input), "%S")
        vcmd_f = (self.root.register(limit_input_float), "%P")
        # Save the data of the GPS coordiante
        self.gps = ""
        # Initial value of the location name
        location_title = ""
        # Initial value of latitude
        location_latitude = ""
        # Initial value of longitude
        location_longitude = ""

        ###############
        # Header Line #
        ###############
        lbl_header = Label(self.root, text="Fill all cells to add the GPS coordinate.")
        lbl_header.grid(row=self.row_idx, column=1, padx=PAD_X, pady=PAD_Y_LBL, sticky="W")
        self.lbl_warning = Label(self.root, fg="#a00", text="")
        self.lbl_warning.grid(
            row=self.row(), column=2, columnspan=2, padx=PAD_X, pady=PAD_Y_LBL, sticky="E"
        )

        ###############
        # Title input #
        ###############
        self.sv_gps_title = StringVar()
        self.sv_gps_title.set(location_title)
        self.sv_gps_title.trace_add("write", self.validate_input)
        lbl_gps_title = Label(self.root, text="Title: ")
        lbl_gps_title.grid(row=self.row_idx, column=0, padx=PAD_X, pady=PAD_Y, sticky="W")
        ent_gps_title = self.add_cmp(
            "ent_gps_title",
            Entry(self.root, textvariable=self.sv_gps_title, validate="key", validatecommand=vcmd),
        )
        ent_gps_title.grid(
            row=self.row(), column=1, columnspan=3, padx=PAD_X, pady=PAD_Y, sticky="EW"
        )
        Hovertip(ent_gps_title, TooltipDict["ent_gps_title"])

        #####################
        # TimeFrameSelector #
        #####################
        tfs_gps = self.add_cmp(
            "tfs_gps",
            TimeFrameSelector(self.root, self.row_idx, startdate_parent, enddate_parent),
        )
        tfs_gps.set_start_date(startdate_parent)
        tfs_gps.set_end_date(enddate_parent)
        self.row_idx += 2

        # Bind after setting the values to avoid triggering the callback
        tfs_gps.bind(self.validate_input)

        separator = Separator(self.root, orient="horizontal")
        separator.grid(row=self.row(), column=0, columnspan=4, padx=PAD_X, pady=PAD_Y, sticky="EW")

        ####################
        # Coordinate input #
        ####################
        self.sv_gps_latitude = StringVar()
        self.sv_gps_latitude.set(location_latitude)
        self.sv_gps_latitude.trace_add("write", self.validate_input)
        lbl_gps_latitude = Label(self.root, text="Latitude: ")
        lbl_gps_latitude.grid(row=self.row_idx, column=0, padx=PAD_X, pady=PAD_Y, sticky="W")
        ent_gps_latitude = self.add_cmp(
            "ent_gps_latitude",
            Entry(self.root, textvariable=self.sv_gps_latitude, validate="key", validatecommand=vcmd_f),
        )
        ent_gps_latitude.grid(
            row=self.row(), column=1, columnspan=3, padx=PAD_X, pady=PAD_Y, sticky="EW"
        )
        Hovertip(ent_gps_latitude, TooltipDict["ent_gps_lat"])

        self.sv_gps_longitude = StringVar()
        self.sv_gps_longitude.set(location_longitude)
        self.sv_gps_longitude.trace_add("write", self.validate_input)
        lbl_gps_longitude = Label(self.root, text="Longitude: ")
        lbl_gps_longitude.grid(row=self.row_idx, column=0, padx=PAD_X, pady=PAD_Y, sticky="W")
        ent_gps_longitude = self.add_cmp(
            "ent_gps_longitude",
            Entry(self.root, textvariable=self.sv_gps_longitude, validate="key", validatecommand=vcmd_f),
        )
        ent_gps_longitude.grid(
            row=self.row(), column=1, columnspan=3, padx=PAD_X, pady=PAD_Y, sticky="EW"
        )
        Hovertip(ent_gps_longitude, TooltipDict["ent_gps_lon"])

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
                state=DISABLED,
            ),
        )
        btn_add.grid(row=self.row(), column=3, padx=PAD_X, pady=PAD_Y, sticky="EW")
        Hovertip(btn_add, TooltipDict["btn_add_gps"])

        center_window(self.root)

        # Making MessageBox Visible
        self.root.wait_window()

    def validate_input(self, *args):
        """
        Test if the values of all input fields are valid
        and disable the add button in case they are not.
        """
        if self.sv_gps_title.get():
            self.set_cmp_state("btn_add", NORMAL)
        else:
            self.set_cmp_state("btn_add", DISABLED)

        # Disable button in case some cells are not yet filled
        # (Date and time cells have always atleast some value)
        if not self.sv_gps_title.get():
            self.set_cmp_state("btn_add", DISABLED)
            self.lbl_warning.config(text=WarningArray[WarningCodes.WARNING_MISSING_DATA])
            return

        start_date = self.get_cmp("tfs_gps").get_start_date()
        end_date = self.get_cmp("tfs_gps").get_end_date()

        if err := test_time_frame_swap(start_date, end_date):
            self.set_cmp_state("btn_add", DISABLED)
            self.lbl_warning.config(text=WarningArray[err])
            return

        # Test all subevents of the list, to check if there are two subevents with
        # the same time frame, which is not allowed
        for gps_coord in self.gps_list:
            gps_data = gps_coord.split(SEPARATOR)
            testdate_start = datetime.fromisoformat(gps_data[1])
            testdate_end = datetime.fromisoformat(gps_data[2])

            # Test for overlapping time frames
            if err := test_time_frame(testdate_start, testdate_end, start_date, end_date):
                self.set_cmp_state("btn_add", DISABLED)
                self.lbl_warning.config(text=WarningArray[err])
                return

        self.set_cmp_state("btn_add", NORMAL)
        self.lbl_warning.config(text=WarningArray[WarningCodes.NO_WARNING])

    def add(self):
        """
        Use the input data to create a new subevent and save it in a variable.
        The result can be accessed from the outside (for example from the eventbox).
        """
        start_date = self.get_cmp("tfs_gps").get_start_date()
        end_date = self.get_cmp("tfs_gps").get_end_date()

        self.gps = f"{self.sv_gps_title.get()}{SEPARATOR}{start_date}{SEPARATOR}{end_date}{SEPARATOR}{self.sv_gps_latitude.get()}{SEPARATOR}{self.sv_gps_longitude.get()}"
        self.changed = True
        self.close()
