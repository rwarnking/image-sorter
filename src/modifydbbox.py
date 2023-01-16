import datetime
import os

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
from tkinter.ttk import Checkbutton, Combobox, Progressbar, Scrollbar, Separator

from tktimepicker import AnalogPicker, AnalogThemes, SpinTimePickerOld, constants
from functools import partial

from helper import center_window

from idlelib.tooltip import Hovertip
from sorter import Sorter
from tkcalendar import DateEntry
from tooltips import TooltipDict

from database import Database

PAD_X = 5
PAD_Y = (10, 0)


# Source: https://stackoverflow.com/questions/29619418/
class ModifyDBBox(object):
    def row(self):
        self.row_idx += 1
        return self.row_idx - 1

    def __init__(self, title, message, db, meta_info):

        self.db = db

        # Return value
        self.choice = False

        self.row_idx = 0
        self.meta_info = meta_info

        # Creating Dialogue for messagebox
        self.root = Toplevel()
        self.root.title(title)

        Label(
            self.root,
            text=message,
        ).grid(row=self.row(), column=0, columnspan=2, padx=PAD_X, pady=PAD_Y, sticky="w")

        ########################################

        separator = Separator(self.root, orient="horizontal")
        separator.grid(row=self.row(), column=0, columnspan=2, padx=PAD_X, pady=PAD_Y, sticky="EW")

        def browse_button_open(dir):
            filename = filedialog.askopenfilename(initialdir=os.path.dirname(dir.get()))
            if filename != "" and not filename.lower().endswith(".json"):
                messagebox.showinfo(message="Please select a json file.", title="Error")
            elif filename != "":
                self.db.load_from_file(filename)
                self.updateListFrame(db, self.db_select.get())
                dir.set(filename)

        def browse_button_save(dir):
            filename = filedialog.asksaveasfilename(initialdir=os.path.dirname(dir.get()))
            if filename != "" and not filename.lower().endswith(".json"):
                messagebox.showinfo(message="Please select a json file.", title="Error")
            elif filename != "":
                self.db.save_to_file(filename)
                dir.set(filename)

        # Load events from file
        btn_loadfile = Button(
            self.root,
            text="Load database from json file",
            command=lambda: browse_button_open(self.meta_info.event_src),
        )
        btn_loadfile.grid(row=self.row_idx, column=0, padx=PAD_X, pady=PAD_Y, sticky="EW")
        Hovertip(btn_loadfile, TooltipDict["btn_loadfile"])

        lbl_load = Label(self.root, textvariable=self.meta_info.event_src)
        lbl_load.grid(row=self.row(), column=1, padx=PAD_X, pady=PAD_Y, sticky="EW")

        # Save events to file
        btn_savefile = Button(
            self.root,
            text="Save database to json file",
            command=lambda: browse_button_save(self.meta_info.event_tgt),
        )
        btn_savefile.grid(row=self.row_idx, column=0, padx=PAD_X, pady=PAD_Y, sticky="EW")
        Hovertip(btn_savefile, TooltipDict["btn_savefile"])

        lbl_save = Label(self.root, textvariable=self.meta_info.event_tgt)
        lbl_save.grid(row=self.row(), column=1, padx=PAD_X, pady=PAD_Y, sticky="EW")

        ########################################

        separator = Separator(self.root, orient="horizontal")
        separator.grid(row=self.row(), column=0, columnspan=2, padx=PAD_X, pady=PAD_Y, sticky="EW")

        Label(
            self.root,
            text="Selected database table:",
        ).grid(row=self.row_idx, column=0, padx=PAD_X, pady=PAD_Y, sticky="w")

        def update_db_gui(_):
            str_selection = self.db_select.get()
            assert(str_selection == "events" or str_selection == "artists" or str_selection == "persons")
            self.updateListFrame(db, self.db_select.get())

        # https://www.pythontutorial.net/tkinter/tkinter-combobox/
        list_dbs = [
            "events",
            "artists",
            "persons",
        ]
        self.db_select = StringVar()
        self.db_select.set(list_dbs[0])
        cb_dbs = Combobox(self.root, textvariable=self.db_select)
        # Write artist values from database
        cb_dbs["values"] = list_dbs
        # Prevent typing a value
        cb_dbs["state"] = "readonly"
        # Place the widget
        cb_dbs.grid(row=self.row(), column=1, padx=PAD_X, pady=PAD_Y, sticky="EW")
        # Bind callback
        cb_dbs.bind("<<ComboboxSelected>>", update_db_gui)
        # Hovertip(cb_dbs, TooltipDict["cb_dbs"]) TODO

        ########################################

        self.frame_db_add = Frame(self.root, width=500, height=30, bg="white")
        self.frame_db_add.pack_propagate(False)
        self.frame_db_add.grid(
            row=self.row(), column=0, columnspan=2, padx=PAD_X, pady=PAD_Y, sticky="EW"
        )

        # Word wrap
        # https://stackoverflow.com/questions/19029157/
        self.text_db_add = Text(self.frame_db_add, wrap="none")
        self.text_db_add.pack(fill="both", expand=True)

        button = Button(self.text_db_add, text="Add", command=self.clickAdd, width=5)
        self.text_db_add.window_create("end", window=button)
        button = Button(self.text_db_add, text="", width=5, background="white", state="disabled")
        self.text_db_add.window_create("end", window=button)

        self.text_db_add.insert("end", " ...")

        ##############################################

        # self.frame_db_list = Frame(self.root, width=self.root.winfo_width() - PAD_X * 2, height=300, bg="white")
        self.frame_db_list = Frame(self.root, width=500, height=100, bg="white")
        self.frame_db_list.pack_propagate(False)
        self.frame_db_list.grid(
            row=self.row(), column=0, columnspan=2, padx=PAD_X, pady=(5, 0), sticky="EW"
        )

        # Word wrap
        # https://stackoverflow.com/questions/19029157/
        self.text_db_list = Text(self.frame_db_list, wrap="none")
        self.sb_db_list = Scrollbar(self.frame_db_list, command=self.text_db_list.yview)
        self.sb_db_list.pack(side=RIGHT, fill="y")
        self.text_db_list.configure(yscrollcommand=self.sb_db_list.set)
        self.text_db_list.pack(fill="both", expand=True)

        self.updateListFrame(db, self.db_select.get())

        def cleanup():
            str_selection = self.db_select.get()
            if str_selection == "events":
                self.db.clean_events()
            elif str_selection == "artists":
                self.db.clean_artists()
            elif str_selection == "persons":
                self.db.clean_persons()
            self.updateListFrame(db, str_selection)

        # Remove all events from the database
        btn_clear = Button(
            self.root,
            text="Clear selected table",
            command=lambda: cleanup(),
        )
        btn_clear.grid(row=self.row(), column=1, padx=PAD_X, pady=PAD_Y, sticky="EW")
        # Hovertip(btn_clear, TooltipDict["btn_clear"]) # TODO

        Button(
            self.root,
            text="Done",
            command=self.closed,
        ).grid(row=self.row(), column=1, padx=PAD_X, pady=(10, 15), sticky="ew")

        center_window(self.root)

        # Making MessageBox Visible
        self.root.wait_window()

    # https://stackoverflow.com/questions/68288119/how-to-create-a-scrollable-list-of-buttons-in-tkinter
    def updateListFrame(self, db, table):
        for child in self.text_db_list.winfo_children():
            child.destroy()
        self.text_db_list.delete('1.0', END)

        list_table_content = [
            ' | '.join(str(e) for e in x)
            for x in db.get_all(table)
        ]

        ############################
        str_selection = self.db_select.get()

        # Creating label for each artist/event/...
        for i, e in enumerate(list_table_content):
            # https://stackoverflow.com/questions/6920302/
            button = Button(self.text_db_list, text="Mod", command=partial(self.clickModify, e), width=5)
            self.text_db_list.window_create("end", window=button)

            button = Button(self.text_db_list, text="Del", command=partial(self.clickDelete, e), width=5)
            self.text_db_list.window_create("end", window=button)

            # Special case because the artist contains a person id
            if str_selection == "artists":
                first_idx = e.index(" | ")
                second_idx = e.index(" | ", first_idx + 1)
                num = int(e[first_idx+3:second_idx])
                e = e[:second_idx] + " (" + self.db.get("persons", ("pid", num))[0][1] + ")" + e[second_idx:]

            self.text_db_list.insert("end", " " + e + "\n")

        self.text_db_list.update()

    # Function on Closeing MessageBox
    def closed(self):
        self.root.destroy()

    # Function on pressing Delete
    def clickDelete(self, elem):
        str_selection = self.db_select.get()
        if str_selection == "events":
            elm_data = elem.split(" | ")
            self.db.delete_event(elm_data[1], elm_data[2], elm_data[3])
        elif str_selection == "artists":
            elm_data = elem.split(" | ")
            # Obacht: elm_data[0] is the index not the name
            self.db.delete_artist(elm_data[1], elm_data[2], elm_data[3], elm_data[4], elm_data[5])
        elif str_selection == "persons":
            elm_data = elem.split(" | ")
            self.db.delete_person(elm_data[1])
        self.updateListFrame(self.db, self.db_select.get())

    # Function on pressing Modify
    def clickModify(self, elem):
        str_selection = self.db_select.get()
        if str_selection == "events":
            box = ModifyEventBox("Modify event", self.db, elem)
        elif str_selection == "artists":
            box = ModifyArtistBox("Modify artist", self.db, elem)
        elif str_selection == "persons":
            box = ModifyPersonBox("Modify person", self.db, elem)

        if box.changed:
            self.updateListFrame(self.db, self.db_select.get())

    # Function on pressing Add
    def clickAdd(self):
        str_selection = self.db_select.get()
        if str_selection == "events":
            box = ModifyEventBox("Add event", self.db)
        elif str_selection == "artists":
            box = ModifyArtistBox("Add artist", self.db)
        elif str_selection == "persons":
            box = ModifyPersonBox("Add person", self.db)

        if box.changed:
            self.updateListFrame(self.db, self.db_select.get())

##############################################################
##############################################################
##############################################################

class ModifyEventBox(object):
    def row(self):
        self.row_idx += 1
        return self.row_idx - 1

    def __init__(self, title, db, elem=""):

        # Creating Dialogue for messagebox
        self.root = Toplevel()
        self.root.title(title)

        self.changed = False
        self.row_idx = 0

        self.db = db

        # TODO 
        titel = ""
        elm_e_data = elem.split(" | ")
        if elem != "":
            titel = elm_e_data[1]

        def checkfull(*args):
            if str_e_title_w.get():
                btn_add.config(state="normal")
            else:
                btn_add.config(state="disabled")

        #########
        # Event title input field
        #########
        str_e_title_w = StringVar()
        str_e_title_w.set(titel)
        str_e_title_w.trace("w", checkfull)
        lbl_e_title = Label(self.root, text="Title: ")
        lbl_e_title.grid(row=self.row_idx, column=0, padx=PAD_X, pady=PAD_Y, sticky="EW")
        Entry(self.root, textvariable=str_e_title_w).grid(row=self.row(), column=1, columnspan=3, padx=PAD_X, pady=PAD_Y, sticky="EW")

        #########
        # Date and time input
        #########
        # https://stackoverflow.com/questions/4443786/how-do-i-create-a-date-picker-in-tkinter
        lbl_e_sdate = Label(self.root, text="Start: ")
        lbl_e_sdate.grid(row=self.row_idx, column=0, padx=PAD_X, pady=PAD_Y, sticky="EW")
        date_e_start = DateEntry(
            self.root, width=12, background="darkblue", foreground="white", borderwidth=2
        )
        date_e_start.grid(row=self.row_idx, column=1, padx=PAD_X, pady=PAD_Y, sticky="EW")
        Hovertip(date_e_start, TooltipDict["date_e_start"])

        tp_e_start = SpinTimePickerOld(self.root)
        tp_e_start.addAll(constants.HOURS24)
        tp_e_start.grid(row=self.row(), column=2, columnspan=2, padx=PAD_X, pady=PAD_Y, sticky="EW")

        # End Date 
        lbl_e_edate = Label(self.root, text="End: ")
        lbl_e_edate.grid(row=self.row_idx, column=0, padx=PAD_X, pady=PAD_Y, sticky="EW")
        date_e_end = DateEntry(
            self.root, width=12, background="darkblue", foreground="white", borderwidth=2
        )
        date_e_end.grid(row=self.row_idx, column=1, padx=PAD_X, pady=PAD_Y, sticky="EW")
        Hovertip(date_e_end, TooltipDict["date_e_end"])

        tp_e_end = SpinTimePickerOld(self.root)
        tp_e_end.addAll(constants.HOURS24)
        tp_e_end.grid(row=self.row(), column=2, columnspan=2, padx=PAD_X, pady=PAD_Y, sticky="EW")
        # This is stupid but I did not find a way to access the variable directly
        for i in range(1, 24):
            tp_e_end._24HrsTime.invoke("buttonup")
        for i in range(1, 60):
            tp_e_end._minutes.invoke("buttonup")

        separator = Separator(self.root, orient="horizontal")
        separator.grid(row=self.row(), column=0, columnspan=4, padx=PAD_X, pady=PAD_Y, sticky="EW")

################################ TODO

        if elem != "":
            s_date = datetime.datetime.strptime(elm_e_data[2], "%Y-%m-%d %H:%M:%S")
            date_e_start.set_date(s_date)
            while tp_e_start.hours24() < s_date.hour:
                tp_e_start._24HrsTime.invoke("buttonup")
            while tp_e_start.minutes() < s_date.minute:
                tp_e_start._minutes.invoke("buttonup")

            e_date = datetime.datetime.strptime(elm_e_data[3], "%Y-%m-%d %H:%M:%S")
            date_e_end.set_date(e_date)
            while tp_e_end.hours24() > e_date.hour:
                tp_e_end._24HrsTime.invoke("buttondown")
            while tp_e_end.minutes() > e_date.minute:
                tp_e_end._minutes.invoke("buttondown")
##########################

        #########
        # Participant List Input
        #########
        str_e_parts_w = StringVar()
        str_e_parts_w.set("")
        lbl_e_parts = Label(self.root, text="List of Participants:")
        lbl_e_parts.grid(row=self.row(), column=1, padx=PAD_X, pady=PAD_Y, sticky="W")

        # Participant Frame and Text
        self.frame_part_new = Frame(self.root, width=500, height=30, bg="white")
        self.frame_part_new.pack_propagate(False)
        self.frame_part_new.grid(
            row=self.row(), column=1, columnspan=3, padx=PAD_X, pady=PAD_Y, sticky="EW"
        )

        self.text_part_new = Text(self.frame_part_new, wrap="none")
        self.text_part_new.pack(fill="both", expand=True)

        button = Button(self.text_part_new, text="Add", command=self.clickAddParticipant, width=5)
        self.text_part_new.window_create("end", window=button)
        button = Button(self.text_part_new, text="", width=5, background="white", state="disabled")
        self.text_part_new.window_create("end", window=button)

        self.text_part_new.insert("end", " ...")

        #########
        # Participant List Frame
        #########
        # self.frame_db_list = Frame(self.root, width=self.root.winfo_width() - PAD_X * 2, height=300, bg="white")
        self.frame_part_list = Frame(self.root, width=500, height=100, bg="white")
        self.frame_part_list.pack_propagate(False)
        self.frame_part_list.grid(
            row=self.row(), column=1, columnspan=3, padx=PAD_X, pady=(5, 0), sticky="EW"
        )

        # Word wrap
        # https://stackoverflow.com/questions/19029157/
        self.text_part_list = Text(self.frame_part_list, wrap="none")
        self.sb_part_list = Scrollbar(self.frame_part_list, command=self.text_part_list.yview)
        self.sb_part_list.pack(side=RIGHT, fill="y")
        self.text_part_list.configure(yscrollcommand=self.sb_part_list.set)
        self.text_part_list.pack(fill="both", expand=True)

        self.list_new_participants = []
        if elem != "":
            self.list_new_participants = [
                str(self.db.get("persons", ("pid", x[1]))[0][1]) + " | " + x[3] + " | " + x[4]
                for x in self.db.get("participants", ("event_id", elm_e_data[0]))
            ]

        self.updateParticipantListFrame()

        #################
        # Subevent list #
        #################
        str_e_sub_w = StringVar()
        str_e_sub_w.set("")
        lbl_e_sub = Label(self.root, text="List of Subevents:")
        lbl_e_sub.grid(row=self.row(), column=1, padx=PAD_X, pady=PAD_Y, sticky="W")

        # Subevent Frame and Text
        self.frame_sub_new = Frame(self.root, width=500, height=30, bg="white")
        self.frame_sub_new.pack_propagate(False)
        self.frame_sub_new.grid(
            row=self.row(), column=1, columnspan=3, padx=PAD_X, pady=PAD_Y, sticky="EW"
        )

        self.text_sub_new = Text(self.frame_sub_new, wrap="none")
        self.text_sub_new.pack(fill="both", expand=True)

        button = Button(self.text_sub_new, text="Add", command=self.clickAddSubevent, width=5)
        self.text_sub_new.window_create("end", window=button)
        button = Button(self.text_sub_new, text="", width=5, background="white", state="disabled")
        self.text_sub_new.window_create("end", window=button)

        self.text_sub_new.insert("end", " ...")

        #########
        # Subevent List Frame
        #########
        # self.frame_db_list = Frame(self.root, width=self.root.winfo_width() - PAD_X * 2, height=300, bg="white")
        self.frame_sub_list = Frame(self.root, width=500, height=100, bg="white")
        self.frame_sub_list.pack_propagate(False)
        self.frame_sub_list.grid(
            row=self.row(), column=1, columnspan=3, padx=PAD_X, pady=(5, 0), sticky="EW"
        )

        # Word wrap
        # https://stackoverflow.com/questions/19029157/
        self.text_sub_list = Text(self.frame_sub_list, wrap="none")
        self.sb_sub_list = Scrollbar(self.frame_sub_list, command=self.text_sub_list.yview)
        self.sb_sub_list.pack(side=RIGHT, fill="y")
        self.text_sub_list.configure(yscrollcommand=self.sb_sub_list.set)
        self.text_sub_list.pack(fill="both", expand=True)

        self.list_new_subevents = []
        if elem != "":
            # TODO subevents dont have accociated event id
            self.list_new_subevents = [
                x[2] + " | " + x[3] + " | " + x[4]
                for x in self.db.get("subevents", ("event_id", elm_e_data[0]))
            ]

        self.updateSubeventListFrame()

        #####################
        # Main add function #
        #####################
        def add():
            n_s_date = datetime.datetime.combine(
                date_e_start.get_date(), datetime.datetime.min.time()
            ) + datetime.timedelta(hours=tp_e_start.hours24(), minutes=tp_e_start.minutes())
            n_e_date = datetime.datetime.combine(
                date_e_end.get_date(), datetime.datetime.min.time()
            ) + datetime.timedelta(hours=tp_e_end.hours24(), minutes=tp_e_end.minutes())
            
            if elem == "":
                self.db.insert_event(
                    str_e_title_w.get(),
                    n_s_date,
                    n_e_date,
                )
                eid = self.db.get_last_row_id()
            else:
                # TODO does not update participants
                s_date = datetime.datetime.strptime(elm_e_data[2], "%Y-%m-%d %H:%M:%S")
                e_date = datetime.datetime.strptime(elm_e_data[3], "%Y-%m-%d %H:%M:%S")
                self.db.update_event(
                    # old
                    elm_e_data[1],
                    s_date,
                    e_date,
                    # new
                    str_e_title_w.get(),
                    n_s_date,
                    n_e_date,
                )
                eid = int(elm_e_data[0])

            # Delete all participants and subevents of the event
            self.db.delete("participants", ("event_id", eid))
            self.db.delete("subevents", ("event_id", eid))

            # Now add all participants that are in the list
            for p in self.list_new_participants:
                elem_p_data = p.split(" | ")
                s_date_p = datetime.datetime.strptime(elem_p_data[1], "%Y-%m-%d %H:%M:%S")
                e_date_p = datetime.datetime.strptime(elem_p_data[2], "%Y-%m-%d %H:%M:%S")

                # Check if the person is already in the database otherwise add
                _, pid = self.db.get_has_or_insert("persons", ("name", elem_p_data[0]))

                self.db.insert_participant(pid, eid, s_date_p, e_date_p)

            # Now add all subevents that are in the list
            for p in self.list_new_subevents:
                elem_se_data = p.split(" | ")
                s_date_se = datetime.datetime.strptime(elem_se_data[1], "%Y-%m-%d %H:%M:%S")
                e_date_se = datetime.datetime.strptime(elem_se_data[2], "%Y-%m-%d %H:%M:%S")

                self.db.insert_subevent(eid, elem_se_data[0], s_date_se, e_date_se)

            # TODO check if partipant or subevent already exists

            self.changed = True
            self.root.destroy()

        ################
        # Main buttons #
        ################
        Button(
            self.root,
            text="Abort",
            command=self.closed,
        ).grid(row=self.row_idx, column=1, padx=PAD_X, pady=(10, 15), sticky="ew")

        # In update mode the button must not be disabled from the start,
        # because changes in the timecells can not be checked.
        btn_add = Button(
            self.root,
            text="Add" if elem == "" else "Update",
            command=add,
            state="disabled" if elem == "" else "normal",
        )
        btn_add.grid(row=self.row(), column=3, padx=PAD_X, pady=(10, 15), sticky="ew")

        center_window(self.root)

        # Making MessageBox Visible
        self.root.wait_window()

    # https://stackoverflow.com/questions/68288119/how-to-create-a-scrollable-list-of-buttons-in-tkinter
    def updateParticipantListFrame(self):
        for child in self.text_part_list.winfo_children():
            child.destroy()
        self.text_part_list.delete('1.0', END)

        ############################

        # Creating label for each artist/event/...
        for i, e in enumerate(self.list_new_participants):
            # https://stackoverflow.com/questions/6920302/
            button = Button(self.text_part_list, text="Del", command=partial(self.clickDeleteParticipant, e), width=5)
            self.text_part_list.window_create("end", window=button)

            self.text_part_list.insert("end", " " + e + "\n")

        self.text_part_list.update()

    def updateSubeventListFrame(self):
        # TODO check which is needed
        for child in self.text_sub_list.winfo_children():
            child.destroy()
        self.text_sub_list.delete('1.0', END)

        ############################

        # Creating label for each artist/event/...
        for i, e in enumerate(self.list_new_subevents):
            # https://stackoverflow.com/questions/6920302/
            button = Button(self.text_sub_list, text="Del", command=partial(self.clickDeleteSubevent, e), width=5)
            self.text_sub_list.window_create("end", window=button)

            self.text_sub_list.insert("end", " " + e + "\n")

        self.text_sub_list.update()

    # Function for adding a participant
    def clickAddParticipant(self):
        box = ModifyParticipantBox("Add participant", self.db)
        if box.changed:
            self.list_new_participants.append(box.participant)
            self.updateParticipantListFrame()

    def clickDeleteParticipant(self, participant):
        self.list_new_participants.remove(participant)
        self.updateParticipantListFrame()

    # Function for adding a subevent
    def clickAddSubevent(self):
        box = ModifySubeventBox("Add subevent", self.db)
        if box.changed:
            self.list_new_subevents.append(box.subevent)
            self.updateSubeventListFrame()

    def clickDeleteSubevent(self, subevent):
        self.list_new_subevents.remove(subevent)
        self.updateSubeventListFrame()

    # Function on Closeing MessageBox
    def closed(self):
        self.root.destroy()

###############################################
###############################################
###############################################

class ModifyArtistBox(object):
    def row(self):
        self.row_idx += 1
        return self.row_idx - 1

    def __init__(self, title, db, elem=""):

        # Creating Dialogue for messagebox
        self.root = Toplevel()
        self.root.title(title)

        self.changed = False
        self.row_idx = 0

        self.db = db

        # TODO 
        name = ""
        make = ""
        model = ""
        elm_a_data = elem.split(" | ")
        if elem != "":
            name = self.db.get("persons", ("pid", elm_a_data[1]))[0][1]
            make = elm_a_data[2]
            model = elm_a_data[3]

        def checkfull(*args):
            a = sv_a_name.get()
            b = sv_a_make.get()
            c = sv_a_model.get()
            if a and b and c:
                btn_add.config(state="normal")
            else:
                btn_add.config(state="disabled")

        # Artist name input field
        # Get a list of all persons to select from
        list_persons = [
            x[1] for x in db.get_all("persons")
        ]
        # Test that the name is present in the list
        assert(name in list_persons if elem != "" else True)

        lbl_a_name = Label(self.root, text="Name: ")
        lbl_a_name.grid(row=self.row_idx, column=0, padx=PAD_X, pady=PAD_Y, sticky="EW")
        sv_a_name = StringVar()
        sv_a_name.set(name if elem != "" else "")
        sv_a_name.trace("w", checkfull)
        cb_person_select = Combobox(self.root, textvariable=sv_a_name)
        # Write file signatures
        cb_person_select["values"] = list_persons
        # Place the widget
        cb_person_select.grid(
            row=self.row(), column=1, columnspan=3, padx=PAD_X, pady=PAD_Y, sticky="EW"
        )
        # Hovertip(cb_insig_select, TooltipDict["cb_person_select"]) # TODO

        # Make input field
        sv_a_make = StringVar()
        sv_a_make.set(make)
        sv_a_make.trace("w", checkfull)
        lbl_a_make = Label(self.root, text="Make: ")
        lbl_a_make.grid(row=self.row_idx, column=0, padx=PAD_X, pady=PAD_Y, sticky="EW")
        Entry(self.root, textvariable=sv_a_make).grid(
            row=self.row(), column=1, columnspan=3, padx=PAD_X, pady=PAD_Y, sticky="EW"
        )

        # Make input field
        sv_a_model = StringVar()
        sv_a_model.set(model)
        sv_a_model.trace("w", checkfull)
        lbl_a_model = Label(self.root, text="Model: ")
        lbl_a_model.grid(row=self.row_idx, column=0, padx=PAD_X, pady=PAD_Y, sticky="EW")
        Entry(self.root, textvariable=sv_a_model).grid(
            row=self.row(), column=1, columnspan=3, padx=PAD_X, pady=PAD_Y, sticky="EW"
        )

        #########
        # Date Frame (write)
        #########
        # https://stackoverflow.com/questions/4443786/how-do-i-create-a-date-picker-in-tkinter
        lbl_e_sdate = Label(self.root, text="Start: ")
        lbl_e_sdate.grid(row=self.row_idx, column=0, padx=PAD_X, pady=PAD_Y, sticky="EW")
        date_e_start = DateEntry(
            self.root, width=12, background="darkblue", foreground="white", borderwidth=2
        )
        date_e_start.grid(row=self.row_idx, column=1, padx=PAD_X, pady=PAD_Y, sticky="EW")
        Hovertip(date_e_start, TooltipDict["date_e_start"])

        tp_e_start = SpinTimePickerOld(self.root)
        tp_e_start.addAll(constants.HOURS24)
        tp_e_start.grid(row=self.row(), column=2, columnspan=2, padx=PAD_X, pady=PAD_Y, sticky="EW")

        # End Date 
        lbl_e_edate = Label(self.root, text="End: ")
        lbl_e_edate.grid(row=self.row_idx, column=0, padx=PAD_X, pady=PAD_Y, sticky="EW")
        date_e_end = DateEntry(
            self.root, width=12, background="darkblue", foreground="white", borderwidth=2
        )
        date_e_end.grid(row=self.row_idx, column=1, padx=PAD_X, pady=PAD_Y, sticky="EW")
        Hovertip(date_e_end, TooltipDict["date_e_end"])

        tp_e_end = SpinTimePickerOld(self.root)
        tp_e_end.addAll(constants.HOURS24)
        tp_e_end.grid(row=self.row(), column=2, columnspan=2, padx=PAD_X, pady=PAD_Y, sticky="EW")
        # This is stupid but I did not find a way to access the variable directly
        for i in range(1, 24):
            tp_e_end._24HrsTime.invoke("buttonup")
        for i in range(1, 60):
            tp_e_end._minutes.invoke("buttonup")

        separator = Separator(self.root, orient="horizontal")
        separator.grid(row=self.row(), column=0, columnspan=4, padx=PAD_X, pady=PAD_Y, sticky="EW")

        if elem != "":
            s_date = datetime.datetime.strptime(elm_a_data[4], "%Y-%m-%d %H:%M:%S")
            date_e_start.set_date(s_date)
            while tp_e_start.hours24() < s_date.hour:
                tp_e_start._24HrsTime.invoke("buttonup")
            while tp_e_start.minutes() < s_date.minute:
                tp_e_start._minutes.invoke("buttonup")

            e_date = datetime.datetime.strptime(elm_a_data[5], "%Y-%m-%d %H:%M:%S")
            # TODO for some reason does 2100 not get to the gui
            # -> it is possible to have 2100 but the gui does shorten it to 31/12/00 so -> 2000
            # 31/12/2100 works check if there is a setting
            date_e_end.set_date(e_date)
            while tp_e_end.hours24() > e_date.hour:
                tp_e_end._24HrsTime.invoke("buttondown")
            while tp_e_end.minutes() > e_date.minute:
                tp_e_end._minutes.invoke("buttondown")

        def add():
            s_date = datetime.datetime.combine(
                date_e_start.get_date(), datetime.datetime.min.time()
            ) + datetime.timedelta(hours=tp_e_start.hours24(), minutes=tp_e_start.minutes())
            e_date = datetime.datetime.combine(
                date_e_end.get_date(), datetime.datetime.min.time()
            ) + datetime.timedelta(hours=tp_e_end.hours24(), minutes=tp_e_end.minutes())
            if elem == "":

                # Call a function that returns the id of the person and adds the person
                # if it is not yet present in the database
                p_id = self.db.get_has_or_insert("persons", ("name", sv_a_name.get()))[1]

                self.db.insert_artist(
                    p_id,
                    sv_a_make.get(),
                    sv_a_model.get(),
                    s_date,
                    e_date,
                )
            else:
                # Call a function that returns the id of the person and adds the person
                # if it is not yet present in the database
                p_id = self.db.get_has_or_insert("persons", ("name", sv_a_name.get()))[1]

                self.db.update_artist(
                    int(elm_a_data[1]),
                    elm_a_data[2],
                    elm_a_data[3],
                    elm_a_data[4],
                    elm_a_data[5],
                    p_id,
                    sv_a_make.get(),
                    sv_a_model.get(),
                    s_date,
                    e_date,
                )

            self.changed = True
            self.root.destroy()

        Button(
            self.root,
            text="Abort",
            command=self.closed,
        ).grid(row=self.row_idx, column=1, padx=PAD_X, pady=(10, 15), sticky="ew")

        # In update mode the button must not be disabled from the start,
        # because changes in the timecells can not be checked.
        # TODO it is possible to have empty time cells currently and the timepicker 
        # does not check for this itself
        btn_add = Button(
            self.root,
            text="Add" if elem == "" else "Update",
            command=add,
            state="disabled" if elem == "" else "normal",
        )
        btn_add.grid(row=self.row(), column=3, padx=PAD_X, pady=(10, 15), sticky="ew")

        center_window(self.root)

        # Making MessageBox Visible
        self.root.wait_window()

    # Function on Closeing MessageBox
    def closed(self):
        self.root.destroy()

###############################################
###############################################
###############################################

class ModifyParticipantBox(object):
    def row(self):
        self.row_idx += 1
        return self.row_idx - 1

    def __init__(self, title, db, elem=""):

        # Creating Dialogue for messagebox
        self.root = Toplevel()
        self.root.title(title)

        self.changed = False
        self.participant = ""
        self.row_idx = 0

        self.db = db

        # TODO 
        name = ""
        elm_a_data = elem.split(" | ")
        if elem != "":
            name = self.db.get("persons", ("pid", elm_a_data[1]))[0][1]

        def checkfull(*args):
            if sv_p_name.get():
                btn_add.config(state="normal")
            else:
                btn_add.config(state="disabled")

        # Artist name input field
        # Get a list of all persons to select from
        list_persons = [
            x[1] for x in db.get_all("persons")
        ]
        # Test that the name is present in the list
        assert(name in list_persons if elem != "" else True)


        lbl_p_name = Label(self.root, text="Name: ")
        lbl_p_name.grid(row=self.row_idx, column=0, padx=PAD_X, pady=PAD_Y, sticky="EW")
        sv_p_name = StringVar()
        sv_p_name.set(name if elem != "" else "")
        sv_p_name.trace("w", checkfull)
        cb_person_select = Combobox(self.root, textvariable=sv_p_name)
        # Write file signatures
        cb_person_select["values"] = list_persons
        # Place the widget
        cb_person_select.grid(
            row=self.row(), column=1, columnspan=3, padx=PAD_X, pady=PAD_Y, sticky="EW"
        )
        # Hovertip(cb_insig_select, TooltipDict["cb_person_select"]) # TODO

        #########
        # Date Frame (write)
        #########
        # https://stackoverflow.com/questions/4443786/how-do-i-create-a-date-picker-in-tkinter
        lbl_p_sdate = Label(self.root, text="Start: ")
        lbl_p_sdate.grid(row=self.row_idx, column=0, padx=PAD_X, pady=PAD_Y, sticky="EW")
        date_p_start = DateEntry(
            self.root, width=12, background="darkblue", foreground="white", borderwidth=2
        )
        date_p_start.grid(row=self.row_idx, column=1, padx=PAD_X, pady=PAD_Y, sticky="EW")
        Hovertip(date_p_start, TooltipDict["date_e_start"])

        tp_p_start = SpinTimePickerOld(self.root)
        tp_p_start.addAll(constants.HOURS24)
        tp_p_start.grid(row=self.row(), column=2, columnspan=2, padx=PAD_X, pady=PAD_Y, sticky="EW")

        # End Date 
        lbl_p_edate = Label(self.root, text="End: ")
        lbl_p_edate.grid(row=self.row_idx, column=0, padx=PAD_X, pady=PAD_Y, sticky="EW")
        date_p_end = DateEntry(
            self.root, width=12, background="darkblue", foreground="white", borderwidth=2
        )
        date_p_end.grid(row=self.row_idx, column=1, padx=PAD_X, pady=PAD_Y, sticky="EW")
        Hovertip(date_p_end, TooltipDict["date_e_end"])

        tp_p_end = SpinTimePickerOld(self.root)
        tp_p_end.addAll(constants.HOURS24)
        tp_p_end.grid(row=self.row(), column=2, columnspan=2, padx=PAD_X, pady=PAD_Y, sticky="EW")
        # This is stupid but I did not find a way to access the variable directly
        for i in range(1, 24):
            tp_p_end._24HrsTime.invoke("buttonup")
        for i in range(1, 60):
            tp_p_end._minutes.invoke("buttonup")

        separator = Separator(self.root, orient="horizontal")
        separator.grid(row=self.row(), column=0, columnspan=4, padx=PAD_X, pady=PAD_Y, sticky="EW")

        if elem != "":
            s_date = datetime.datetime.strptime(elm_a_data[4], "%Y-%m-%d %H:%M:%S")
            date_p_start.set_date(s_date)
            while tp_p_start.hours24() < s_date.hour:
                tp_p_start._24HrsTime.invoke("buttonup")
            while tp_p_start.minutes() < s_date.minute:
                tp_p_start._minutes.invoke("buttonup")

            e_date = datetime.datetime.strptime(elm_a_data[5], "%Y-%m-%d %H:%M:%S")
            # TODO for some reason does 2100 not get to the gui
            # -> it is possible to have 2100 but the gui does shorten it to 31/12/00 so -> 2000
            # 31/12/2100 works check if there is a setting
            date_p_end.set_date(e_date)
            while tp_p_end.hours24() > e_date.hour:
                tp_p_end._24HrsTime.invoke("buttondown")
            while tp_p_end.minutes() > e_date.minute:
                tp_p_end._minutes.invoke("buttondown")

        def add():
            s_date = datetime.datetime.combine(
                date_p_start.get_date(), datetime.datetime.min.time()
            ) + datetime.timedelta(hours=tp_p_start.hours24(), minutes=tp_p_start.minutes())
            e_date = datetime.datetime.combine(
                date_p_end.get_date(), datetime.datetime.min.time()
            ) + datetime.timedelta(hours=tp_p_end.hours24(), minutes=tp_p_end.minutes())

            self.participant = sv_p_name.get() + " | " + str(s_date) + " | " + str(e_date)
            self.changed = True
            self.root.destroy()

        Button(
            self.root,
            text="Abort",
            command=self.closed,
        ).grid(row=self.row_idx, column=1, padx=PAD_X, pady=(10, 15), sticky="ew")

        # In update mode the button must not be disabled from the start,
        # because changes in the timecells can not be checked.
        # TODO it is possible to have empty time cells currently and the timepicker 
        # does not check for this itself
        btn_add = Button(
            self.root,
            text="Add" if elem == "" else "Update",
            command=add,
            state="disabled" if elem == "" else "normal",
        )
        btn_add.grid(row=self.row(), column=3, padx=PAD_X, pady=(10, 15), sticky="ew")

        center_window(self.root)

        # Making MessageBox Visible
        self.root.wait_window()

    # Function on Closeing MessageBox
    def closed(self):
        self.root.destroy()

###############################################
###############################################
###############################################

class ModifySubeventBox(object):
    def row(self):
        self.row_idx += 1
        return self.row_idx - 1

    def __init__(self, title, db, elem=""):

        # Creating Dialogue for messagebox
        self.root = Toplevel()
        self.root.title(title)

        self.changed = False
        self.subevent = ""
        self.row_idx = 0

        self.db = db

        # TODO 
        title = ""
        elem_se_data = elem.split(" | ")
        if elem != "":
            title = elem_se_data[1]

        def checkfull(*args):
            if sv_se_title.get():
                btn_add.config(state="normal")
            else:
                btn_add.config(state="disabled")

        #########
        # Subevent title input field
        #########
        sv_se_title = StringVar()
        sv_se_title.set(title)
        sv_se_title.trace("w", checkfull)
        lbl_se_title = Label(self.root, text="Title: ")
        lbl_se_title.grid(row=self.row_idx, column=0, padx=PAD_X, pady=PAD_Y, sticky="EW")
        Entry(self.root, textvariable=sv_se_title).grid(row=self.row(), column=1, columnspan=3, padx=PAD_X, pady=PAD_Y, sticky="EW")
        # Hovertip(cb_insig_select, TooltipDict["cb_person_select"]) # TODO

        #########
        # Date Frame (write)
        #########
        # https://stackoverflow.com/questions/4443786/how-do-i-create-a-date-picker-in-tkinter
        lbl_se_sdate = Label(self.root, text="Start: ")
        lbl_se_sdate.grid(row=self.row_idx, column=0, padx=PAD_X, pady=PAD_Y, sticky="EW")
        date_se_start = DateEntry(
            self.root, width=12, background="darkblue", foreground="white", borderwidth=2
        )
        date_se_start.grid(row=self.row_idx, column=1, padx=PAD_X, pady=PAD_Y, sticky="EW")
        Hovertip(date_se_start, TooltipDict["date_e_start"])

        tp_se_start = SpinTimePickerOld(self.root)
        tp_se_start.addAll(constants.HOURS24)
        tp_se_start.grid(row=self.row(), column=2, columnspan=2, padx=PAD_X, pady=PAD_Y, sticky="EW")

        # End Date 
        lbl_se_edate = Label(self.root, text="End: ")
        lbl_se_edate.grid(row=self.row_idx, column=0, padx=PAD_X, pady=PAD_Y, sticky="EW")
        date_se_end = DateEntry(
            self.root, width=12, background="darkblue", foreground="white", borderwidth=2
        )
        date_se_end.grid(row=self.row_idx, column=1, padx=PAD_X, pady=PAD_Y, sticky="EW")
        Hovertip(date_se_end, TooltipDict["date_e_end"])

        tp_se_end = SpinTimePickerOld(self.root)
        tp_se_end.addAll(constants.HOURS24)
        tp_se_end.grid(row=self.row(), column=2, columnspan=2, padx=PAD_X, pady=PAD_Y, sticky="EW")
        # This is stupid but I did not find a way to access the variable directly
        for i in range(1, 24):
            tp_se_end._24HrsTime.invoke("buttonup")
        for i in range(1, 60):
            tp_se_end._minutes.invoke("buttonup")

        separator = Separator(self.root, orient="horizontal")
        separator.grid(row=self.row(), column=0, columnspan=4, padx=PAD_X, pady=PAD_Y, sticky="EW")

        if elem != "":
            s_date = datetime.datetime.strptime(elem_se_data[2], "%Y-%m-%d %H:%M:%S")
            date_se_start.set_date(s_date)
            while tp_se_start.hours24() < s_date.hour:
                tp_se_start._24HrsTime.invoke("buttonup")
            while tp_se_start.minutes() < s_date.minute:
                tp_se_start._minutes.invoke("buttonup")

            e_date = datetime.datetime.strptime(elem_se_data[3], "%Y-%m-%d %H:%M:%S")
            # TODO for some reason does 2100 not get to the gui
            # -> it is possible to have 2100 but the gui does shorten it to 31/12/00 so -> 2000
            # 31/12/2100 works check if there is a setting
            date_se_end.set_date(e_date)
            while tp_se_end.hours24() > e_date.hour:
                tp_se_end._24HrsTime.invoke("buttondown")
            while tp_se_end.minutes() > e_date.minute:
                tp_se_end._minutes.invoke("buttondown")

        def add():
            s_date = datetime.datetime.combine(
                date_se_start.get_date(), datetime.datetime.min.time()
            ) + datetime.timedelta(hours=tp_se_start.hours24(), minutes=tp_se_start.minutes())
            e_date = datetime.datetime.combine(
                date_se_end.get_date(), datetime.datetime.min.time()
            ) + datetime.timedelta(hours=tp_se_end.hours24(), minutes=tp_se_end.minutes())

            self.subevent = sv_se_title.get() + " | " + str(s_date) + " | " + str(e_date)
            self.changed = True
            self.root.destroy()

        Button(
            self.root,
            text="Abort",
            command=self.closed,
        ).grid(row=self.row_idx, column=1, padx=PAD_X, pady=(10, 15), sticky="ew")

        # In update mode the button must not be disabled from the start,
        # because changes in the timecells can not be checked.
        # TODO it is possible to have empty time cells currently and the timepicker 
        # does not check for this itself
        btn_add = Button(
            self.root,
            text="Add" if elem == "" else "Update",
            command=add,
            state="disabled" if elem == "" else "normal",
        )
        btn_add.grid(row=self.row(), column=3, padx=PAD_X, pady=(10, 15), sticky="ew")

        center_window(self.root)

        # Making MessageBox Visible
        self.root.wait_window()

    # Function on Closeing MessageBox
    def closed(self):
        self.root.destroy()

###############################################
###############################################
###############################################

class ModifyPersonBox(object):
    def row(self):
        self.row_idx += 1
        return self.row_idx - 1

    def __init__(self, title, db, elem=""):

        # Creating Dialogue for messagebox
        self.root = Toplevel()
        self.root.title(title)

        self.changed = False
        self.row_idx = 0

        self.db = db

        # TODO 
        elm_p_data = elem.split(" | ")
        name = "" if elem == "" else elm_p_data[1]

        def checkfull(*args):
            if sv_p_name.get():
                btn_add.config(state="normal")
            else:
                btn_add.config(state="disabled")

        # Person name input field
        sv_p_name = StringVar()
        sv_p_name.set(name)
        sv_p_name.trace("w", checkfull)
        lbl_p_name = Label(self.root, text="Name: ")
        lbl_p_name.grid(row=self.row_idx, column=0, padx=PAD_X, pady=PAD_Y, sticky="EW")
        Entry(self.root, textvariable=sv_p_name).grid(
            row=self.row(), column=1, columnspan=3, padx=PAD_X, pady=PAD_Y, sticky="EW"
        )

        def add():
            if elem == "":
                self.db.insert_person(
                    sv_p_name.get(),
                )
            else:
                self.db.update_person(
                    elm_p_data[1],
                    sv_p_name.get(),
                )

            self.changed = True
            self.root.destroy()

        Button(
            self.root,
            text="Abort",
            command=self.closed,
        ).grid(row=self.row_idx, column=1, padx=PAD_X, pady=(10, 15), sticky="ew")

        btn_add = Button(
            self.root,
            text="Add" if elem == "" else "Update",
            command=add,
            state="disabled",
        )
        btn_add.grid(row=self.row(), column=3, padx=PAD_X, pady=(10, 15), sticky="ew")

        center_window(self.root)

        # Making MessageBox Visible
        self.root.wait_window()

    # Function on Closeing MessageBox
    def closed(self):
        self.root.destroy()