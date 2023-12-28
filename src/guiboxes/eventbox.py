from datetime import datetime
from functools import partial
from idlelib.tooltip import Hovertip
from tkinter import END, RIGHT, Button, Entry, Frame, Label, StringVar, Text
from tkinter.ttk import Scrollbar, Separator

from database import Database
from dateutils import TimeFrameSelector
from debug_messages import WarningArray, WarningCodes
from guiboxes.basebox import BTN_W, LINE_H, PAD_X, PAD_Y, PAD_Y_LBL, SEPARATOR, WINDOW_W, BaseBox
from guiboxes.participantbox import ModifyParticipantBox
from guiboxes.subeventbox import ModifySubeventBox
from helper import center_window, limit_input, test_time_frame_outside, test_time_frame_swap
from tooltips import TooltipDict

TEVENT_H = 100
TEVENT_W = WINDOW_W * 0.9 - 2 * PAD_X


class ModifyEventBox(BaseBox):
    def __init__(self, header: str, db: Database, event: str = ""):
        """
        Create a GUI element that includes a input field for the title
        and a time frame selector for start and end date.
        """
        super().__init__(header)

        # Save the database
        self.db = db

        # Register the character input check only once for this widget
        vcmd = (self.root.register(limit_input), "%S")

        # Split the string to gain the data
        # If the string did not contain everything override with empty string
        # and assign it to the values
        event_data = event.split(SEPARATOR)

        self.e_id = None
        self.title = ""
        self.start_date = None
        self.end_date = None

        if len(event_data) == 2:
            self.start_date = event_data[0]
            self.end_date = event_data[1]
        elif len(event_data) >= 4:
            # Convert e_id to integer
            self.e_id = int(event_data[0])
            self.title = event_data[1]
            self.start_date = event_data[2]
            self.end_date = event_data[3]

        ###############
        # Header Line #
        ###############
        lbl_header = Label(self.root, text="Fill all cells to add the event.")
        lbl_header.grid(row=self.row_idx, column=1, padx=PAD_X, pady=PAD_Y_LBL, sticky="W")
        self.lbl_warning = Label(self.root, fg="#a00", text="")
        self.lbl_warning.grid(
            row=self.row(), column=2, columnspan=2, padx=PAD_X, pady=PAD_Y_LBL, sticky="E"
        )

        ####################
        # Event data input #
        ####################
        self.sv_e_title = StringVar()
        self.sv_e_title.set(self.title)
        self.sv_e_title.trace("w", self.validate_input)
        lbl_e_title = Label(self.root, text="Title: ")
        lbl_e_title.grid(row=self.row_idx, column=0, padx=PAD_X, pady=PAD_Y, sticky="EW")
        ent_e_title = Entry(
            self.root, textvariable=self.sv_e_title, validate="key", validatecommand=vcmd
        )
        ent_e_title.grid(
            row=self.row(), column=1, columnspan=3, padx=PAD_X, pady=PAD_Y, sticky="EW"
        )
        Hovertip(ent_e_title, TooltipDict["ent_e_title"])

        #####################
        # TimeFrameSelector #
        #####################
        self.tfs = TimeFrameSelector(self.root, self.row_idx)
        self.row_idx += 2

        if self.start_date is not None and self.end_date is not None:
            self.tfs.set_start_date_s(self.start_date)
            self.tfs.set_end_date_s(self.end_date)

        # Bind after setting the values to avoid triggering the callback
        self.tfs.bind(self.validate_input)

        separator = Separator(self.root, orient="horizontal")
        separator.grid(row=self.row(), column=0, columnspan=4, padx=PAD_X, pady=PAD_Y, sticky="EW")

        #########
        # Participant List Input
        #########
        str_e_parts_w = StringVar()
        str_e_parts_w.set("")
        lbl_e_parts = Label(self.root, text="List of Participants:")
        lbl_e_parts.grid(row=self.row(), column=1, padx=PAD_X, pady=PAD_Y_LBL, sticky="W")

        # Participant Frame and Text
        self.frame_part_new = Frame(self.root, width=TEVENT_W, height=LINE_H, bg="white")
        self.frame_part_new.pack_propagate(False)
        self.frame_part_new.grid(
            row=self.row(), column=1, columnspan=3, padx=PAD_X, pady=PAD_Y, sticky="EW"
        )

        self.text_part_new = Text(self.frame_part_new, wrap="none")
        self.text_part_new.pack(fill="both", expand=True)

        btn_add_part = Button(
            self.text_part_new, text="Add", command=self.clickAddParticipant, width=BTN_W
        )
        self.text_part_new.window_create("end", window=btn_add_part)
        Hovertip(btn_add_part, TooltipDict["btn_add_part"])
        btn_none = Button(
            self.text_part_new, text="", width=BTN_W, background="white", state="disabled"
        )
        self.text_part_new.window_create("end", window=btn_none)

        self.text_part_new.insert("end", " ...")

        #########
        # Participant List Frame
        #########
        self.frame_part_list = Frame(self.root, width=TEVENT_W, height=TEVENT_H, bg="white")
        self.frame_part_list.pack_propagate(False)
        self.frame_part_list.grid(
            row=self.row(), column=1, columnspan=3, padx=PAD_X, pady=PAD_Y, sticky="EW"
        )

        # Word wrap
        # https://stackoverflow.com/questions/19029157/
        self.text_part_list = Text(self.frame_part_list, wrap="none")
        self.sb_part_list = Scrollbar(self.frame_part_list, command=self.text_part_list.yview)
        self.sb_part_list.pack(side=RIGHT, fill="y")
        self.text_part_list.configure(yscrollcommand=self.sb_part_list.set)
        self.text_part_list.pack(fill="both", expand=True)

        self.list_new_participants: list[str] = []
        if self.e_id is not None:
            self.list_new_participants = [
                f"{self.db.get_pname(x[1])} | {x[3]} | {x[4]}"
                for x in self.db.get("participants", ("event_id", self.e_id))
            ]

        self.updateParticipantListFrame()

        #################
        # Subevent list #
        #################
        str_e_sub_w = StringVar()
        str_e_sub_w.set("")
        lbl_e_sub = Label(self.root, text="List of Subevents:")
        lbl_e_sub.grid(row=self.row(), column=1, padx=PAD_X, pady=PAD_Y_LBL, sticky="W")

        # Subevent Frame and Text
        self.frame_sub_new = Frame(self.root, width=TEVENT_W, height=LINE_H, bg="white")
        self.frame_sub_new.pack_propagate(False)
        self.frame_sub_new.grid(
            row=self.row(), column=1, columnspan=3, padx=PAD_X, pady=PAD_Y, sticky="EW"
        )

        self.text_sub_new = Text(self.frame_sub_new, wrap="none")
        self.text_sub_new.pack(fill="both", expand=True)

        btn_add_sube = Button(
            self.text_sub_new, text="Add", command=self.clickAddSubevent, width=BTN_W
        )
        self.text_sub_new.window_create("end", window=btn_add_sube)
        Hovertip(btn_add_sube, TooltipDict["btn_add_sube"])
        btn_none = Button(
            self.text_sub_new, text="", width=BTN_W, background="white", state="disabled"
        )
        self.text_sub_new.window_create("end", window=btn_none)

        self.text_sub_new.insert("end", " ...")

        #########
        # Subevent List Frame
        #########
        self.frame_sub_list = Frame(self.root, width=TEVENT_W, height=TEVENT_H, bg="white")
        self.frame_sub_list.pack_propagate(False)
        self.frame_sub_list.grid(
            row=self.row(), column=1, columnspan=3, padx=PAD_X, pady=PAD_Y, sticky="EW"
        )

        # Word wrap
        # https://stackoverflow.com/questions/19029157/
        self.text_sub_list = Text(self.frame_sub_list, wrap="none")
        self.sb_sub_list = Scrollbar(self.frame_sub_list, command=self.text_sub_list.yview)
        self.sb_sub_list.pack(side=RIGHT, fill="y")
        self.text_sub_list.configure(yscrollcommand=self.sb_sub_list.set)
        self.text_sub_list.pack(fill="both", expand=True)

        self.list_new_subevents: list[str] = []
        if self.e_id is not None:
            self.list_new_subevents = [
                f"{x[2]} | {x[3]} | {x[4]}"
                for x in self.db.get("subevents", ("event_id", self.e_id))
            ]

        self.updateSubeventListFrame()

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

        # In update mode the button must not be disabled from the start,
        # because changes in the timecells can not be checked.
        self.btn_add_event = Button(
            self.root,
            text="Add" if len(event_data) < 4 else "Update",
            command=self.add,
            state="disabled",
        )
        self.btn_add_event.grid(row=self.row(), column=3, padx=PAD_X, pady=PAD_Y, sticky="EW")
        Hovertip(self.btn_add_event, TooltipDict["btn_add_event"])

        center_window(self.root)

        # Making MessageBox Visible
        self.root.wait_window()

    def validate_input(self, *args):
        """
        Test if the values of all input fields are valid
        and disable the add button in case they are not.
        """
        title = self.sv_e_title.get()
        if not title:
            self.btn_add_event.config(state="disabled")
            self.lbl_warning.config(text=WarningArray[WarningCodes.WARNING_MISSING_DATA])
            return

        e_date_start = self.tfs.get_start_date()
        e_date_end = self.tfs.get_end_date()

        if err := test_time_frame_swap(e_date_start, e_date_end):
            self.btn_add_event.config(state="disabled")
            self.lbl_warning.config(text=WarningArray[err])
            return

        # Test all participant and all subevents for non matching timeframes.
        # This needs to be done since the event date might have been changed,
        # after the participants and subevents were added.
        for p in self.list_new_participants:
            elem_p_data = p.split(SEPARATOR)
            p_date_start = datetime.fromisoformat(elem_p_data[1])
            p_date_end = datetime.fromisoformat(elem_p_data[2])

            if err := test_time_frame_outside(e_date_start, e_date_end, p_date_start, p_date_end):
                self.btn_add_event.config(state="disabled")
                self.lbl_warning.config(text=WarningArray[err])
                return

        for se in self.list_new_subevents:
            elem_se_data = se.split(SEPARATOR)
            se_date_start = datetime.fromisoformat(elem_se_data[2])
            se_date_end = datetime.fromisoformat(elem_se_data[2])

            if err := test_time_frame_outside(
                e_date_start, e_date_end, se_date_start, se_date_end
            ):
                self.btn_add_event.config(state="disabled")
                self.lbl_warning.config(text=WarningArray[err])
                return

        self.btn_add_event.config(state="normal")
        self.lbl_warning.config(text=WarningArray[WarningCodes.NO_WARNING])

    def add(self):
        """Use the input data to create a new event and add or update it to the database."""
        new_start_date = self.tfs.get_start_date()
        new_end_date = self.tfs.get_end_date()

        if self.e_id is None:
            self.info = self.db.insert_event(
                self.sv_e_title.get(),
                new_start_date,
                new_end_date,
            )
            self.e_id = self.db.get_last_row_id()
        else:
            s_date = datetime.fromisoformat(self.start_date)
            e_date = datetime.fromisoformat(self.end_date)
            self.info = self.db.update_event(
                # old
                self.title,
                s_date,
                e_date,
                # new
                self.sv_e_title.get(),
                new_start_date,
                new_end_date,
            )

        # Delete all participants and subevents of the event
        self.db.delete("participants", ("event_id", self.e_id))
        self.db.delete("subevents", ("event_id", self.e_id))

        # Now add all participants that are in the list
        for p in self.list_new_participants:
            elem_p_data = p.split(SEPARATOR)
            s_date_p = datetime.fromisoformat(elem_p_data[1])
            e_date_p = datetime.fromisoformat(elem_p_data[2])

            # Check if the person is already in the database otherwise add
            pid = self.db.insert_ret_id("persons", ("name", elem_p_data[0]))

            self.db.insert_participant(pid, self.e_id, s_date_p, e_date_p)

        # Now add all subevents that are in the list
        for se in self.list_new_subevents:
            elem_se_data = se.split(SEPARATOR)
            s_date_se = datetime.fromisoformat(elem_se_data[1])
            e_date_se = datetime.fromisoformat(elem_se_data[2])

            self.db.insert_subevent(self.e_id, elem_se_data[0], s_date_se, e_date_se)

        self.changed = True
        self.close()

    def updateParticipantListFrame(self):
        """
        Update the text field listing all participants using the participant list.
        How to create a scrollable list of buttons in Tkinter:
        https://stackoverflow.com/questions/68288119/
        How to pass arguments to a Button command in Tkinter:
        https://stackoverflow.com/questions/6920302/
        """
        # Clear all content in the text area
        self.text_part_list.delete("1.0", END)

        # Creating label for each artist/event/...
        for i, e in enumerate(self.list_new_participants):
            btn_del_part = Button(
                self.text_part_list,
                text="Del",
                command=partial(self.clickDeleteParticipant, e),
                width=BTN_W,
            )
            Hovertip(btn_del_part, TooltipDict["btn_del_part"])
            self.text_part_list.window_create("end", window=btn_del_part)

            self.text_part_list.insert("end", " " + e + "\n")

        self.text_part_list.update()

    def updateSubeventListFrame(self):
        """
        Update the text field listing all subevents using the subevent list.
        How to create a scrollable list of buttons in Tkinter:
        https://stackoverflow.com/questions/68288119/
        How to pass arguments to a Button command in Tkinter:
        https://stackoverflow.com/questions/6920302/
        """
        # Clear all content in the text area
        self.text_sub_list.delete("1.0", END)

        # Creating label for each artist/event/...
        for i, e in enumerate(self.list_new_subevents):
            btn_del_sube = Button(
                self.text_sub_list,
                text="Del",
                command=partial(self.clickDeleteSubevent, e),
                width=BTN_W,
            )
            Hovertip(btn_del_sube, TooltipDict["btn_del_sube"])
            self.text_sub_list.window_create("end", window=btn_del_sube)

            self.text_sub_list.insert("end", " " + e + "\n")

        self.text_sub_list.update()

    def clickAddParticipant(self):
        """Function for adding a participant."""
        start_date = self.tfs.get_start_date()
        end_date = self.tfs.get_end_date()

        box = ModifyParticipantBox(
            "Add participant", self.db, self.list_new_participants, start_date, end_date
        )
        if box.changed:
            self.list_new_participants.append(box.participant)
            self.updateParticipantListFrame()
            self.validate_input()

    def clickAddSubevent(self):
        """Function for adding a subevent."""
        start_date = self.tfs.get_start_date()
        end_date = self.tfs.get_end_date()

        box = ModifySubeventBox(
            "Add subevent", self.db, self.list_new_subevents, start_date, end_date
        )
        if box.changed:
            self.list_new_subevents.append(box.subevent)
            self.list_new_subevents.sort(
                key=lambda x: x[x.find(SEPARATOR) + len(SEPARATOR) : x.rfind(SEPARATOR)]
            )

            self.updateSubeventListFrame()
            self.validate_input()

    def clickDeleteParticipant(self, participant: str):
        """Function for deleting a participant."""
        self.list_new_participants.remove(participant)
        self.updateParticipantListFrame()
        self.validate_input()

    def clickDeleteSubevent(self, subevent: str):
        """Function for deleting a subevent."""
        self.list_new_subevents.remove(subevent)
        self.updateSubeventListFrame()
        self.validate_input()
