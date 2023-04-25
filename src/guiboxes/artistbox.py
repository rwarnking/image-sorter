from tkinter import Button, Label

from tkinter import (
    Button,
    Entry,
    Frame,
    Label,
    StringVar,
)
from tkinter.ttk import Combobox, Separator

from helper import center_window, test_time_frame_swap, limit_input

from idlelib.tooltip import Hovertip
from tooltips import TooltipDict
from debug_messages import WarningArray, WarningCodes
from dateutils import TimeFrameSelector, TimeShiftSelector

from guiboxes.basebox import BaseBox, PAD_X, PAD_Y, PAD_Y_LBL


class ModifyArtistBox(BaseBox):
    def __init__(self, header, db, artist=""):
        super().__init__(header)

        # Save the database
        self.db = db

        # Register the character input check only once for this widget
        vcmd = (self.root.register(limit_input), "%S")

        # Split the string to gain the data
        # If the string did not contain everything override with empty string
        # and assign it to the values
        artist_data = artist.split(" | ")
        if len(artist_data) < 7:
            artist_data = [None, None, "", "", None, None, None]
        else:
            # Convert a_id and p_id to integer
            artist_data[0] = int(artist_data[0])
            artist_data[1] = int(artist_data[1])
        self.a_id, self.p_id, self.make, self.model, self.start_date, self.end_date, self.time_shift = artist_data
        self.name = "" if self.p_id is None else self.db.get("persons", ("pid", self.p_id))[0][1] 

        ###############
        # Header Line #
        ###############
        lbl_header = Label(self.root, text="Fill all cells to add the artist.")
        lbl_header.grid(row=self.row_idx, column=1, padx=PAD_X, pady=PAD_Y_LBL, sticky="W")
        self.lbl_warning = Label(self.root, fg="#a00", text="")
        self.lbl_warning.grid(row=self.row(), column=2, columnspan=2, padx=PAD_X, pady=PAD_Y_LBL, sticky="E")

        #####################
        # Artist data input #
        #####################
        # Get a list of all persons to select from
        list_persons = [
            x[1] for x in db.get_all("persons")
        ]

        lbl_a_name = Label(self.root, text="Name: ")
        lbl_a_name.grid(row=self.row_idx, column=0, padx=PAD_X, pady=PAD_Y, sticky="W")
        self.sv_a_name = StringVar()
        self.sv_a_name.set(self.name)
        self.sv_a_name.trace("w", self.validate_input)
        cb_a_person = Combobox(self.root, textvariable=self.sv_a_name, validate="key", validatecommand=vcmd)
        # Write file signatures
        cb_a_person["values"] = list_persons
        # Place the widget
        cb_a_person.grid(
            row=self.row(), column=1, columnspan=3, padx=PAD_X, pady=PAD_Y, sticky="EW"
        )
        Hovertip(cb_a_person, TooltipDict["cb_a_person"])

        # Make input field
        self.sv_a_make = StringVar()
        self.sv_a_make.set(self.make)
        self.sv_a_make.trace("w", self.validate_input)
        lbl_a_make = Label(self.root, text="Make: ")
        lbl_a_make.grid(row=self.row_idx, column=0, padx=PAD_X, pady=PAD_Y, sticky="W")
        ent_a_make = Entry(self.root, textvariable=self.sv_a_make, validate="key", validatecommand=vcmd)
        ent_a_make.grid(
            row=self.row(), column=1, columnspan=3, padx=PAD_X, pady=PAD_Y, sticky="EW"
        )
        Hovertip(ent_a_make, TooltipDict["ent_a_make"])

        # Model input field
        self.sv_a_model = StringVar()
        self.sv_a_model.set(self.model)
        self.sv_a_model.trace("w", self.validate_input)
        lbl_a_model = Label(self.root, text="Model: ")
        lbl_a_model.grid(row=self.row_idx, column=0, padx=PAD_X, pady=PAD_Y, sticky="W")
        ent_a_model = Entry(self.root, textvariable=self.sv_a_model, validate="key", validatecommand=vcmd)
        ent_a_model.grid(
            row=self.row(), column=1, columnspan=3, padx=PAD_X, pady=PAD_Y, sticky="EW"
        )
        Hovertip(ent_a_model, TooltipDict["ent_a_model"])

        #####################
        # TimeFrameSelector #
        #####################
        self.tfs = TimeFrameSelector(self.root, self.row_idx)
        self.row_idx += 2

        if self.start_date is not None and self.end_date is not None:
            self.tfs.set_start_date_s(self.start_date, "%Y-%m-%d %H:%M:%S")
            self.tfs.set_end_date_s(self.end_date, "%Y-%m-%d %H:%M:%S")

        # Bind after setting the values to avoid triggering the callback
        self.tfs.bind(self.validate_input)

        #############
        # Timeshift #
        #############
        self.tss = TimeShiftSelector(self.root, self.row_idx)
        self.row()

        # Set timeshift data
        if self.time_shift is not None:
            d, h, m, s = [x for x in self.time_shift.split(":")]
            self.tss.set_all(d, h, m, s)

        # Bind after setting the values to avoid triggering the callback
        self.tss.bind(self.validate_input)

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
            text="Add" if artist == "" else "Update",
            command=self.add,
            state="disabled",
        )
        self.btn_add.grid(row=self.row(), column=3, padx=PAD_X, pady=PAD_Y, sticky="EW")
        Hovertip(self.btn_add, TooltipDict["btn_add_art" if artist == "" else "btn_update_art"])

        center_window(self.root)

        # Making MessageBox Visible
        self.root.wait_window()

    def validate_input(self, *args):
        name = self.sv_a_name.get()
        make = self.sv_a_make.get()
        model = self.sv_a_model.get()

        # Disable button in case some cells are not yet filled
        # (Date and time cells have always atleast some value)
        if not name or not make or not model:
            self.btn_add.config(state="disabled")
            self.lbl_warning.config(text = WarningArray[WarningCodes.WARNING_MISSING_DATA])
            return

        # In case the person does not yet exist there can not be any overlap
        if not self.db.has("persons", ("name", name)):
            self.btn_add.config(state="normal")
            self.lbl_warning.config(text = WarningArray[WarningCodes.NO_WARNING])
            return

        # Get id and dates to test for overlap
        p_id = self.db.get("persons", ("name", name))[0][0]
        # Get the dates
        start_date = self.tfs.get_start_date()
        end_date = self.tfs.get_end_date()

        if err:= test_time_frame_swap(start_date, end_date):
            self.btn_add.config(state="disabled")
            self.lbl_warning.config(text = WarningArray[err])
            return

        # Test the timeframe of this artist against the timeframes of each artist in the database.
        # If this is only an artist update, the artist id is used to skip
        # the timeframe of this artist which is already present in the database.
        if err := self.db.test_artist_time_frame(self.a_id, p_id, make, model, start_date, end_date):
            self.btn_add.config(state="disabled")
            self.lbl_warning.config(text = WarningArray[err])
        else:
            self.btn_add.config(state="normal")
            self.lbl_warning.config(text = WarningArray[WarningCodes.NO_WARNING])

    def add(self):
        new_start_date = self.tfs.get_start_date()
        new_end_date = self.tfs.get_end_date()
        # Create time shift string from input spinboxes
        new_time_shift = self.tss.to_string()

        # Call a function that returns the id of the person and adds the person
        # if it is not yet present in the database.
        # This is also needed for the update, since the person name might change.
        # In that case the name of the person can not be altered since it might 
        # be used by other artists, but rather a new person with this name is needed.
        new_p_id = self.db.get_has_or_insert("persons", ("name", self.sv_a_name.get()))[1]

        if self.p_id is None:
            self.info = self.db.insert_artist(
                new_p_id,
                self.sv_a_make.get(),
                self.sv_a_model.get(),
                new_start_date,
                new_end_date,
                new_time_shift,
            )
        else:
            self.info = self.db.update_artist(
                self.p_id,
                self.make,
                self.model,
                self.start_date,
                self.end_date,
                self.time_shift,
                new_p_id,
                self.sv_a_make.get(),
                self.sv_a_model.get(),
                new_start_date,
                new_end_date,
                new_time_shift,
            )

        self.changed = True
        self.close()