from idlelib.tooltip import Hovertip
from tkinter import Button, Entry, Label, StringVar

from database import Database
from debug_messages import WarningArray, WarningCodes
from guiboxes.basebox import PAD_X, PAD_Y, PAD_Y_LBL, BaseBox
from helper import center_window, limit_input
from tooltips import TooltipDict

ENAME_W = 50


class ModifyPersonBox(BaseBox):
    def __init__(self, header: str, db: Database, person: str = ""):
        """Create a GUI element that includes a input field for the name of the person."""
        super().__init__(header)

        # Save the database
        self.db = db

        # Register the character input check only once for this widget
        vcmd = (self.root.register(limit_input), "%S")

        # Get the person data if one was given
        person_data = person.split(" | ")
        self.name = "" if len(person_data) < 2 else person_data[1]

        ###############
        # Header Line #
        ###############
        lbl_header = Label(self.root, text="Give the person a name.")
        lbl_header.grid(row=self.row_idx, column=1, padx=PAD_X, pady=PAD_Y_LBL, sticky="W")
        self.lbl_warning = Label(self.root, fg="#a00", text="")
        self.lbl_warning.grid(row=self.row(), column=2, padx=PAD_X, pady=PAD_Y_LBL, sticky="E")

        ##############
        # Name input #
        ##############
        self.sv_p_name = StringVar()
        self.sv_p_name.set(self.name)
        self.sv_p_name.trace("w", self.validate_input)
        lbl_p_name = Label(self.root, text="Name: ")
        lbl_p_name.grid(row=self.row_idx, column=0, padx=PAD_X, pady=PAD_Y, sticky="EW")
        ent_p_name = Entry(
            self.root,
            textvariable=self.sv_p_name,
            width=ENAME_W,
            validate="key",
            validatecommand=vcmd,
        )
        ent_p_name.grid(
            row=self.row(), column=1, columnspan=2, padx=PAD_X, pady=PAD_Y, sticky="EW"
        )
        Hovertip(ent_p_name, TooltipDict["ent_p_name"])

        #########################
        # Add and abort buttons #
        #########################
        btn_abort = Button(
            self.root,
            text="Abort",
            command=self.close,
        )
        btn_abort.grid(row=self.row_idx, column=1, padx=PAD_X, pady=(10, 15), sticky="W")
        Hovertip(btn_abort, TooltipDict["btn_abort"])

        self.btn_add_psn = Button(
            self.root,
            text="Add" if person == "" else "Update",
            command=self.add,
            state="disabled",
        )
        self.btn_add_psn.grid(row=self.row(), column=2, padx=PAD_X, pady=(10, 15), sticky="E")
        Hovertip(
            self.btn_add_psn, TooltipDict["btn_add_psn" if person == "" else "btn_update_psn"]
        )

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
            self.btn_add_psn.config(state="disabled")
            self.lbl_warning.config(text=WarningArray[WarningCodes.WARNING_MISSING_DATA])
            return

        if self.db.has("persons", ("name", name)):
            self.btn_add_psn.config(state="disabled")
            self.lbl_warning.config(text=WarningArray[WarningCodes.WARNING_PERSON_EXISTS])
            return

        self.btn_add_psn.config(state="normal")
        self.lbl_warning.config(text=WarningArray[WarningCodes.NO_WARNING])

    def add(self):
        """Use the input data to create a new person and add or update it to the database."""
        if self.name == "":
            self.info = self.db.insert_person(self.sv_p_name.get())
        else:
            self.info = self.db.update_person(self.name, self.sv_p_name.get())

        self.changed = True
        self.close()
