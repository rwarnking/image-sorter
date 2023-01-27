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
from tkinter.ttk import Checkbutton, Combobox, Progressbar, Scrollbar, Separator, Spinbox

from tktimepicker import AnalogPicker, AnalogThemes, SpinTimePickerOld, constants
from functools import partial

from helper import center_window, test_time_frame

from idlelib.tooltip import Hovertip
from sorter import Sorter
from tkcalendar import DateEntry
from tooltips import TooltipDict
from error_messages import WarningArray, WarningCodes
from dateutils import HourSelector, MinuteSelector

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
        Hovertip(cb_dbs, TooltipDict["cb_dbs"])

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

        btn_add = Button(self.text_db_add, text="Add", command=self.clickAdd, width=5)
        Hovertip(btn_add, TooltipDict["btn_add"])
        self.text_db_add.window_create("end", window=btn_add)
        btn_null = Button(self.text_db_add, text="", width=5, background="white", state="disabled")
        self.text_db_add.window_create("end", window=btn_null)

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
        Hovertip(btn_clear, TooltipDict["btn_clear"])

        btn_done = Button(
            self.root,
            text="Done",
            command=self.closed,
        )
        btn_done.grid(row=self.row(), column=1, padx=PAD_X, pady=(10, 15), sticky="EW")
        Hovertip(btn_done, TooltipDict["btn_done"])

        center_window(self.root)

        # Making MessageBox Visible
        self.root.wait_window()

    # https://stackoverflow.com/questions/68288119/how-to-create-a-scrollable-list-of-buttons-in-tkinter
    def updateListFrame(self, db, table):
        # Clear all content in the text area
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
            btn_mod = Button(self.text_db_list, text="Mod", command=partial(self.clickModify, e), width=5)
            Hovertip(btn_mod, TooltipDict["btn_mod"])
            self.text_db_list.window_create("end", window=btn_mod)

            btn_del = Button(self.text_db_list, text="Del", command=partial(self.clickDelete, e), width=5)
            Hovertip(btn_del, TooltipDict["btn_del"])
            self.text_db_list.window_create("end", window=btn_del)

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
            self.db.delete_artist(elm_data[1], elm_data[2], elm_data[3], elm_data[4], elm_data[5], elm_data[6])
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
            # TODO test if all participant and all subevents match the event date
            # This needs to be done since the event date could be changed,
            # after adding some participants or subevents

            if str_e_title_w.get():
                btn_add_event.config(state="normal")
            else:
                btn_add_event.config(state="disabled")

        #########
        # Event title input field
        #########
        str_e_title_w = StringVar()
        str_e_title_w.set(titel)
        str_e_title_w.trace("w", checkfull)
        lbl_e_title = Label(self.root, text="Title: ")
        lbl_e_title.grid(row=self.row_idx, column=0, padx=PAD_X, pady=PAD_Y, sticky="EW")
        ent_e_title = Entry(self.root, textvariable=str_e_title_w)
        ent_e_title.grid(row=self.row(), column=1, columnspan=3, padx=PAD_X, pady=PAD_Y, sticky="EW")
        Hovertip(ent_e_title, TooltipDict["ent_e_title"])

        #########
        # Date and time input
        #########
        # https://stackoverflow.com/questions/4443786/how-do-i-create-a-date-picker-in-tkinter
        lbl_e_sdate = Label(self.root, text="Start: ")
        lbl_e_sdate.grid(row=self.row_idx, column=0, padx=PAD_X, pady=PAD_Y, sticky="EW")
        date_e_start = DateEntry(
            self.root, width=12, background="darkblue", foreground="white", borderwidth=2, date_pattern="mm/dd/yyyy"
        )
        date_e_start.grid(row=self.row_idx, column=1, padx=PAD_X, pady=PAD_Y, sticky="EW")
        Hovertip(date_e_start, TooltipDict["date_e_start"])

        tp_e_start = SpinTimePickerOld(self.root)
        tp_e_start.addAll(constants.HOURS24)
        tp_e_start.grid(row=self.row(), column=2, columnspan=2, padx=PAD_X, pady=PAD_Y, sticky="EW")
        Hovertip(tp_e_start, TooltipDict["tp_e_start"])

        # End Date 
        lbl_e_edate = Label(self.root, text="End: ")
        lbl_e_edate.grid(row=self.row_idx, column=0, padx=PAD_X, pady=PAD_Y, sticky="EW")
        date_e_end = DateEntry(
            self.root, width=12, background="darkblue", foreground="white", borderwidth=2, date_pattern="mm/dd/yyyy"
        )
        date_e_end.grid(row=self.row_idx, column=1, padx=PAD_X, pady=PAD_Y, sticky="EW")
        Hovertip(date_e_end, TooltipDict["date_e_end"])

        tp_e_end = SpinTimePickerOld(self.root)
        tp_e_end.addAll(constants.HOURS24)
        tp_e_end.grid(row=self.row(), column=2, columnspan=2, padx=PAD_X, pady=PAD_Y, sticky="EW")
        Hovertip(tp_e_end, TooltipDict["tp_e_end"])
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

        ##############################################################

        # TODO TODO TODO
        # Function for adding a participant
        def clickAddParticipant():
            n_s_date = datetime.datetime.combine(
                date_e_start.get_date(), datetime.datetime.min.time()
            ) + datetime.timedelta(hours=tp_e_start.hours24(), minutes=tp_e_start.minutes())
            n_e_date = datetime.datetime.combine(
                date_e_end.get_date(), datetime.datetime.min.time()
            ) + datetime.timedelta(hours=tp_e_end.hours24(), minutes=tp_e_end.minutes())

            box = ModifyParticipantBox("Add participant", self.db, self.list_new_participants, n_s_date, n_e_date)
            if box.changed:
                self.list_new_participants.append(box.participant)
                self.updateParticipantListFrame()

        # Function for adding a subevent
        def clickAddSubevent():
            n_s_date = datetime.datetime.combine(
                date_e_start.get_date(), datetime.datetime.min.time()
            ) + datetime.timedelta(hours=tp_e_start.hours24(), minutes=tp_e_start.minutes())
            n_e_date = datetime.datetime.combine(
                date_e_end.get_date(), datetime.datetime.min.time()
            ) + datetime.timedelta(hours=tp_e_end.hours24(), minutes=tp_e_end.minutes())

            box = ModifySubeventBox("Add subevent", self.db, self.list_new_subevents, n_s_date, n_e_date)
            if box.changed:
                self.list_new_subevents.append(box.subevent)
                self.updateSubeventListFrame()

        ##############################################################

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

        btn_add_part = Button(self.text_part_new, text="Add", command=clickAddParticipant, width=5)
        self.text_part_new.window_create("end", window=btn_add_part)
        Hovertip(btn_add_part, TooltipDict["btn_add_part"])
        btn_none = Button(self.text_part_new, text="", width=5, background="white", state="disabled")
        self.text_part_new.window_create("end", window=btn_none)

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

        btn_add_sube = Button(self.text_sub_new, text="Add", command=clickAddSubevent, width=5)
        self.text_sub_new.window_create("end", window=btn_add_sube)
        Hovertip(btn_add_sube, TooltipDict["btn_add_sube"])
        btn_none = Button(self.text_sub_new, text="", width=5, background="white", state="disabled")
        self.text_sub_new.window_create("end", window=btn_none)

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
            # TODO this prints all participants are deleted even though it might be empty
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

            # TODO two checks are needed
            # 1. check if new participant/subevent fits in time frame
            # 2. check if all participants/subevents fit in time frame after changing the time 

            self.changed = True
            self.root.destroy()

        ################
        # Main buttons #
        ################
        btn_abort = Button(
            self.root,
            text="Abort",
            command=self.closed,
        )
        btn_abort.grid(row=self.row_idx, column=1, padx=PAD_X, pady=(10, 15), sticky="EW")
        Hovertip(btn_abort, TooltipDict["btn_abort"])

        # In update mode the button must not be disabled from the start,
        # because changes in the timecells can not be checked.
        btn_add_event = Button(
            self.root,
            text="Add" if elem == "" else "Update",
            command=add,
            state="disabled" if elem == "" else "normal",
        )
        btn_add_event.grid(row=self.row(), column=3, padx=PAD_X, pady=(10, 15), sticky="EW")
        Hovertip(btn_add_event, TooltipDict["btn_add_event"])

        center_window(self.root)

        # Making MessageBox Visible
        self.root.wait_window()

    # https://stackoverflow.com/questions/68288119/how-to-create-a-scrollable-list-of-buttons-in-tkinter
    def updateParticipantListFrame(self):
        # Clear all content in the text area
        self.text_part_list.delete('1.0', END)

        ############################

        # Creating label for each artist/event/...
        for i, e in enumerate(self.list_new_participants):
            # https://stackoverflow.com/questions/6920302/
            btn_del_part = Button(self.text_part_list, text="Del", command=partial(self.clickDeleteParticipant, e), width=5)
            Hovertip(btn_del_part, TooltipDict["btn_del_part"])
            self.text_part_list.window_create("end", window=btn_del_part)

            self.text_part_list.insert("end", " " + e + "\n")

        self.text_part_list.update()

    def updateSubeventListFrame(self):
        # Clear all content in the text area
        self.text_sub_list.delete('1.0', END)

        ############################

        # Creating label for each artist/event/...
        for i, e in enumerate(self.list_new_subevents):
            # https://stackoverflow.com/questions/6920302/
            btn_del_sube = Button(self.text_sub_list, text="Del", command=partial(self.clickDeleteSubevent, e), width=5)
            Hovertip(btn_del_sube, TooltipDict["btn_del_sube"])
            self.text_sub_list.window_create("end", window=btn_del_sube)

            self.text_sub_list.insert("end", " " + e + "\n")

        self.text_sub_list.update()

    def clickDeleteParticipant(self, participant):
        self.list_new_participants.remove(participant)
        self.updateParticipantListFrame()

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

        # TODO rename check_valid or validate_input
        def checkfull(*args):
            name = sv_a_name.get()
            make = sv_a_make.get()
            model = sv_a_model.get()

            # Disable button in case some cells are not yet filled
            # (Date and time cells have always atleast some value) (TODO)
            if not name or not make or not model:
                btn_add_art.config(state="disabled")
                self.lbl_warning.config(text = WarningArray[WarningCodes.WARNING_MISSING_DATA])
                return

            # In case the person does not yet exist there can not be any overlap
            if not self.db.has_elem("persons", ("name", name)):
                btn_add_art.config(state="normal")
                self.lbl_warning.config(text = WarningArray[WarningCodes.NO_WARNING])
                return

            # Get id and dates to test for overlap
            p_id = self.db.get("persons", ("name", name))[0][0]

            s_date = datetime.datetime.combine(
                date_a_start.get_date(), datetime.datetime.min.time()
            ) + datetime.timedelta(hours=tp_a_start.hours24(), minutes=tp_a_start.minutes())
            e_date = datetime.datetime.combine(
                date_a_end.get_date(), datetime.datetime.min.time()
            ) + datetime.timedelta(hours=tp_a_end.hours24(), minutes=tp_a_end.minutes())

            if err := self.db.test_artist_time_frame(p_id, make, model, s_date, e_date):
                btn_add_art.config(state="disabled")
                self.lbl_warning.config(text = WarningArray[err])
            else:
                btn_add_art.config(state="normal")
                self.lbl_warning.config(text = WarningArray[WarningCodes.NO_WARNING])

        ##################################################################################

        lbl_header = Label(self.root, text="Fill all cells to add the artist.")
        lbl_header.grid(row=self.row_idx, column=1, padx=PAD_X, pady=(5, 0), sticky="W")
        self.lbl_warning = Label(self.root, fg='#f00', text="")
        self.lbl_warning.grid(row=self.row(), column=2, columnspan=2, padx=PAD_X, pady=(5, 0), sticky="E")

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
        cb_a_person = Combobox(self.root, textvariable=sv_a_name)
        # Write file signatures
        cb_a_person["values"] = list_persons
        # Place the widget
        cb_a_person.grid(
            row=self.row(), column=1, columnspan=3, padx=PAD_X, pady=PAD_Y, sticky="EW"
        )
        Hovertip(cb_a_person, TooltipDict["cb_a_person"])

        # Make input field
        sv_a_make = StringVar()
        sv_a_make.set(make)
        sv_a_make.trace("w", checkfull)
        lbl_a_make = Label(self.root, text="Make: ")
        lbl_a_make.grid(row=self.row_idx, column=0, padx=PAD_X, pady=PAD_Y, sticky="EW")
        ent_a_make = Entry(self.root, textvariable=sv_a_make)
        ent_a_make.grid(
            row=self.row(), column=1, columnspan=3, padx=PAD_X, pady=PAD_Y, sticky="EW"
        )
        Hovertip(ent_a_make, TooltipDict["ent_a_make"])

        # Make input field
        sv_a_model = StringVar()
        sv_a_model.set(model)
        sv_a_model.trace("w", checkfull)
        lbl_a_model = Label(self.root, text="Model: ")
        lbl_a_model.grid(row=self.row_idx, column=0, padx=PAD_X, pady=PAD_Y, sticky="EW")
        ent_a_model = Entry(self.root, textvariable=sv_a_model)
        ent_a_model.grid(
            row=self.row(), column=1, columnspan=3, padx=PAD_X, pady=PAD_Y, sticky="EW"
        )
        Hovertip(ent_a_model, TooltipDict["ent_a_model"])

        #########
        # Date and time data
        #########
        # https://stackoverflow.com/questions/4443786/how-do-i-create-a-date-picker-in-tkinter
        lbl_a_sdate = Label(self.root, text="Start: ")
        lbl_a_sdate.grid(row=self.row_idx, column=0, padx=PAD_X, pady=PAD_Y, sticky="EW")
        date_a_start = DateEntry(
            self.root, width=12, background="darkblue", foreground="white", borderwidth=2, date_pattern="mm/dd/yyyy"
        )
        date_a_start.grid(row=self.row_idx, column=1, padx=PAD_X, pady=PAD_Y, sticky="EW")
        date_a_start.bind("<<DateEntrySelected>>", checkfull)
        date_a_start.bind("<KeyRelease>", checkfull)
        Hovertip(date_a_start, TooltipDict["date_a_start"])

        # TODO check if the spintimepicker really is needed if one can instead use the spinboxes used for the timeshift
        tp_a_start = SpinTimePickerOld(self.root)
        tp_a_start.addAll(constants.HOURS24)
        tp_a_start.grid(row=self.row(), column=2, columnspan=2, padx=PAD_X, pady=PAD_Y, sticky="EW")
        Hovertip(tp_a_start, TooltipDict["tp_a_start"])

        # End Date 
        lbl_a_edate = Label(self.root, text="End: ")
        lbl_a_edate.grid(row=self.row_idx, column=0, padx=PAD_X, pady=PAD_Y, sticky="EW")
        date_a_end = DateEntry(
            self.root, width=12, background="darkblue", foreground="white", borderwidth=2, date_pattern="mm/dd/yyyy"
        )
        date_a_end.grid(row=self.row_idx, column=1, padx=PAD_X, pady=PAD_Y, sticky="EW")
        date_a_end.bind("<<DateEntrySelected>>", checkfull)
        date_a_end.bind("<KeyRelease>", checkfull)
        Hovertip(date_a_end, TooltipDict["date_a_end"])

        tp_a_end = SpinTimePickerOld(self.root)
        tp_a_end.addAll(constants.HOURS24)
        tp_a_end.grid(row=self.row(), column=2, columnspan=2, padx=PAD_X, pady=PAD_Y, sticky="EW")
        Hovertip(tp_a_end, TooltipDict["tp_a_end"])

        # This is stupid but I did not find a way to access the variable directly
        for i in range(1, 24):
            tp_a_end._24HrsTime.invoke("buttonup")
        for i in range(1, 60):
            tp_a_end._minutes.invoke("buttonup")

        #############
        # Timeshift #
        # https://pythonguides.com/create-date-time-picker-using-python-tkinter/
        #############
        lbl_tshift = Label(self.root, text="Timeshift: ")
        lbl_tshift.grid(row=self.row_idx, column=0, padx=PAD_X, pady=PAD_Y, sticky="EW")
        frame_tshift_vals = Frame(self.root)
        frame_tshift_vals.grid(row=self.row(), column=1, columnspan=3, padx=PAD_X, pady=PAD_Y, sticky="EW")

        sv_tshift_d = StringVar()
        sv_tshift_d.set("0")
        lbl_tshift_d = Label(frame_tshift_vals, text="Days: ")
        lbl_tshift_d.pack(side="left", fill="x", expand=1)
        sp_a_shiftd = Spinbox(
            frame_tshift_vals,
            from_=-365*1000,
            to=365*1000,
            textvariable=sv_tshift_d,
            width=3,
            justify="left",
            state="readonly",
        )
        sp_a_shiftd.pack(side="left", fill="x", expand=1)
        Hovertip(sp_a_shiftd, TooltipDict["sp_a_shift"])

        sv_tshift_h = StringVar()
        sv_tshift_h.set("0")
        lbl_tshift_h = Label(frame_tshift_vals, text="Hours: ")
        lbl_tshift_h.pack(side="left", fill="x", expand=1)
        sp_a_shifth = Spinbox(
            frame_tshift_vals,
            from_=-23,
            to=23,
            textvariable=sv_tshift_h,
            width=3,
            justify="left",
            state="readonly",
        )
        sp_a_shifth.pack(side="left", fill="x", expand=1)
        Hovertip(sp_a_shifth, TooltipDict["sp_a_shift"])

        sv_tshift_m = StringVar()
        sv_tshift_m.set("0")
        lbl_tshift_m = Label(frame_tshift_vals, text="Minutes: ")
        lbl_tshift_m.pack(side="left", fill="x", expand=1)
        sp_a_shiftm = Spinbox(
            frame_tshift_vals,
            from_=-59,
            to=59,
            textvariable=sv_tshift_m,
            width=3,
            justify="left",
            state="readonly",
        )
        sp_a_shiftm.pack(side="left", fill="x", expand=1)
        Hovertip(sp_a_shiftm, TooltipDict["sp_a_shift"])

        sv_tshift_s = StringVar()
        sv_tshift_s.set("0")
        lbl_tshift_s = Label(frame_tshift_vals, text="Seconds: ")
        lbl_tshift_s.pack(side="left", fill="x", expand=1)
        sp_a_shifts = Spinbox(
            frame_tshift_vals,
            from_=-59,
            to=59,
            textvariable=sv_tshift_s,
            width=3,
            justify="left",
            state="readonly",
        )
        sp_a_shifts.pack(side="left", fill="x", expand=1)
        Hovertip(sp_a_shifts, TooltipDict["sp_a_shift"])

        #############################################################################
        separator = Separator(self.root, orient="horizontal")
        separator.grid(row=self.row(), column=0, columnspan=4, padx=PAD_X, pady=PAD_Y, sticky="EW")

        if elem != "":
            s_date = datetime.datetime.strptime(elm_a_data[4], "%Y-%m-%d %H:%M:%S")
            date_a_start.set_date(s_date)
            while tp_a_start.hours24() < s_date.hour:
                tp_a_start._24HrsTime.invoke("buttonup")
            while tp_a_start.minutes() < s_date.minute:
                tp_a_start._minutes.invoke("buttonup")

            e_date = datetime.datetime.strptime(elm_a_data[5], "%Y-%m-%d %H:%M:%S")
            date_a_end.set_date(e_date)
            while tp_a_end.hours24() > e_date.hour:
                tp_a_end._24HrsTime.invoke("buttondown")
            while tp_a_end.minutes() > e_date.minute:
                tp_a_end._minutes.invoke("buttondown")

            d, h, m, s = [x for x in elm_a_data[6].split(":")]
            sv_tshift_s.set(s)
            sv_tshift_m.set(m)
            sv_tshift_h.set(h)
            sv_tshift_d.set(d)

        def add():
            s_date = datetime.datetime.combine(
                date_a_start.get_date(), datetime.datetime.min.time()
            ) + datetime.timedelta(hours=tp_a_start.hours24(), minutes=tp_a_start.minutes())
            e_date = datetime.datetime.combine(
                date_a_end.get_date(), datetime.datetime.min.time()
            ) + datetime.timedelta(hours=tp_a_end.hours24(), minutes=tp_a_end.minutes())
            # Create time shift string from input spinboxes
            time_shift = sv_tshift_d.get() + ":" + sv_tshift_h.get() + ":" + sv_tshift_m.get() + ":" + sv_tshift_s.get()

            # Call a function that returns the id of the person and adds the person
            # if it is not yet present in the database
            p_id = self.db.get_has_or_insert("persons", ("name", sv_a_name.get()))[1]

            # TODO use None instead of ""
            if elem == "":
                self.db.insert_artist(
                    p_id,
                    sv_a_make.get(),
                    sv_a_model.get(),
                    s_date,
                    e_date,
                    time_shift,
                )
            else:
                self.db.update_artist(
                    int(elm_a_data[1]),
                    elm_a_data[2],
                    elm_a_data[3],
                    elm_a_data[4],
                    elm_a_data[5],
                    elm_a_data[6],
                    p_id,
                    sv_a_make.get(),
                    sv_a_model.get(),
                    s_date,
                    e_date,
                    time_shift,
                )

            self.changed = True
            self.root.destroy()

        btn_abort = Button(
            self.root,
            text="Abort",
            command=self.closed,
        )
        btn_abort.grid(row=self.row_idx, column=1, padx=PAD_X, pady=(10, 15), sticky="W")
        Hovertip(btn_abort, TooltipDict["btn_abort"])

        # TODO it is nececarry to call the function on change of timepicker hour and minute cells
        # TODO it is possible to have empty time cells currently and the timepicker 
        # does not check for this itself
        btn_add_art = Button(
            self.root,
            text="Add" if elem == "" else "Update",
            command=add,
            state="disabled",
        )
        # TODO PAD_X pady check for final version
        btn_add_art.grid(row=self.row(), column=3, padx=PAD_X, pady=(10, 15), sticky="E")
        Hovertip(btn_add_art, TooltipDict["btn_add_art" if elem == "" else "btn_update_art"])

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

    # TODO rename dates e_edate
    def __init__(self, title, db, part_list, e_sdate, e_edate, elem=""):

        # Creating Dialogue for messagebox
        self.root = Toplevel()
        self.root.title(title)

        self.changed = False
        self.participant = ""
        self.row_idx = 0

        self.db = db

        # TODO 
        name = ""
        # TODO elem or elm
        elm_a_data = elem.split(" | ")
        if elem != "":
            name = self.db.get("persons", ("pid", elm_a_data[1]))[0][1]

        ##############################
        # Validate participant input #
        ##############################
        def checkfull(*args):
            # TODO (BIG) should an participant be a person or an artist???
            if not sv_p_name.get():
                btn_add_part.config(state="disabled")
                self.lbl_warning.config(text = WarningArray[WarningCodes.WARNING_MISSING_DATA])
                return
        
            # TODO s_date or start_Date -> obacht s_date is also in use below
            start_date = datetime.datetime.combine(
                date_p_start.get_date(), datetime.datetime.min.time()
            ) + datetime.timedelta(hours=tp_p_start.hours24(), minutes=tp_p_start.minutes())
            end_date = datetime.datetime.combine(
                date_p_end.get_date(), datetime.datetime.min.time()
            ) + datetime.timedelta(hours=tp_p_end.hours24(), minutes=tp_p_end.minutes())

            # Since a person can not be at two places at once all participant entries
            # with the same person name are checked if they have overlapping time dates
            if err := self.db.test_participant_time_frame(sv_p_name.get(), start_date, end_date):
                btn_add_part.config(state="disabled")
                self.lbl_warning.config(text = WarningArray[err])
                return

            for part in part_list:
                part_data = part.split(" | ")
                if part_data[0] == sv_p_name.get():
                    s_date = datetime.datetime.strptime(part_data[1], "%Y-%m-%d %H:%M:%S")
                    e_date = datetime.datetime.strptime(part_data[2], "%Y-%m-%d %H:%M:%S")

                    # Check if start date lies in time frame
                    if err := test_time_frame(start_date, end_date, s_date, e_date):
                        btn_add_part.config(state="disabled")
                        self.lbl_warning.config(text = WarningArray[err])
                        return

            btn_add_part.config(state="normal")
            self.lbl_warning.config(text = WarningArray[WarningCodes.NO_WARNING])

        lbl_header = Label(self.root, text="Fill all cells to add the participant.")
        lbl_header.grid(row=self.row_idx, column=1, padx=PAD_X, pady=(5, 0), sticky="W")
        self.lbl_warning = Label(self.root, fg='#f00', text="")
        self.lbl_warning.grid(row=self.row(), column=2, columnspan=2, padx=PAD_X, pady=(5, 0), sticky="E")

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
        cb_part_person = Combobox(self.root, textvariable=sv_p_name)
        # Write file signatures
        cb_part_person["values"] = list_persons
        # Place the widget
        cb_part_person.grid(
            row=self.row(), column=1, columnspan=3, padx=PAD_X, pady=PAD_Y, sticky="EW"
        )
        Hovertip(cb_part_person, TooltipDict["cb_part_person"])

        #########
        # Date Frame (write)
        #########
        # https://stackoverflow.com/questions/4443786/how-do-i-create-a-date-picker-in-tkinter
        lbl_p_sdate = Label(self.root, text="Start: ")
        lbl_p_sdate.grid(row=self.row_idx, column=0, padx=PAD_X, pady=PAD_Y, sticky="EW")
        date_p_start = DateEntry(
            self.root, width=12, background="darkblue", foreground="white", borderwidth=2, date_pattern="mm/dd/yyyy", mindate=e_sdate, maxdate=e_edate
        )
        date_p_start.grid(row=self.row_idx, column=1, padx=PAD_X, pady=PAD_Y, sticky="EW")
        Hovertip(date_p_start, TooltipDict["date_p_start"])

        tp_p_start = SpinTimePickerOld(self.root)
        tp_p_start.addAll(constants.HOURS24)
        tp_p_start.grid(row=self.row(), column=2, columnspan=2, padx=PAD_X, pady=PAD_Y, sticky="EW")
        Hovertip(tp_p_start, TooltipDict["tp_p_start"])

        # End Date 
        lbl_p_edate = Label(self.root, text="End: ")
        lbl_p_edate.grid(row=self.row_idx, column=0, padx=PAD_X, pady=PAD_Y, sticky="EW")
        date_p_end = DateEntry(
            self.root, width=12, background="darkblue", foreground="white", borderwidth=2, date_pattern="mm/dd/yyyy", mindate=e_sdate, maxdate=e_edate
        )
        date_p_end.grid(row=self.row_idx, column=1, padx=PAD_X, pady=PAD_Y, sticky="EW")
        Hovertip(date_p_end, TooltipDict["date_p_end"])

        tp_p_end = SpinTimePickerOld(self.root)
        tp_p_end.addAll(constants.HOURS24)
        tp_p_end.grid(row=self.row(), column=2, columnspan=2, padx=PAD_X, pady=PAD_Y, sticky="EW")
        Hovertip(tp_p_end, TooltipDict["tp_p_end"])
        
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
            date_p_end.set_date(e_date)
            while tp_p_end.hours24() > e_date.hour:
                tp_p_end._24HrsTime.invoke("buttondown")
            while tp_p_end.minutes() > e_date.minute:
                tp_p_end._minutes.invoke("buttondown")

        def add():
            # TODO s_date or start_Date -> obacht s_date is also in use below
            start_date = datetime.datetime.combine(
                date_p_start.get_date(), datetime.datetime.min.time()
            ) + datetime.timedelta(hours=tp_p_start.hours24(), minutes=tp_p_start.minutes())
            end_date = datetime.datetime.combine(
                date_p_end.get_date(), datetime.datetime.min.time()
            ) + datetime.timedelta(hours=tp_p_end.hours24(), minutes=tp_p_end.minutes())

            ###################
            # Add participant #
            ###################
            self.participant = sv_p_name.get() + " | " + str(start_date) + " | " + str(end_date)
            self.changed = True
            self.root.destroy()

        ########################
        # Add and abort button #
        ########################
        btn_abort = Button(
            self.root,
            text="Abort",
            command=self.closed,
        )
        btn_abort.grid(row=self.row_idx, column=1, padx=PAD_X, pady=(10, 15), sticky="EW")
        Hovertip(btn_abort, TooltipDict["btn_abort"])

        # In update mode the button must not be disabled from the start,
        # because changes in the timecells can not be checked.
        # TODO it is possible to have empty time cells currently and the timepicker 
        # does not check for this itself
        btn_add_part = Button(
            self.root,
            text="Add" if elem == "" else "Update",
            command=add,
            state="disabled" if elem == "" else "normal",
        )
        btn_add_part.grid(row=self.row(), column=3, padx=PAD_X, pady=(10, 15), sticky="EW")
        Hovertip(btn_add_part, TooltipDict["btn_add_part"])

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

    def __init__(self, header, db, subevent_list, e_sdate, e_edate):

        # Creating Dialogue for messagebox
        self.root = Toplevel()
        self.root.title(header)

        # Save the database
        self.db = db
        # Save if a subevent was changed
        self.changed = False
        # Save the data of the subevent
        self.subevent = ""
        # Initial value of the subevent title
        subevent_title = ""
        # Row index for GUI formatting
        self.row_idx = 0

        def checkfull(*args):
            if sv_se_title.get():
                btn_add_sube.config(state="normal")
            else:
                btn_add_sube.config(state="disabled")

            # Disable button in case some cells are not yet filled
            # (Date and time cells have always atleast some value) (TODO)
            if not sv_se_title.get():
                btn_add_sube.config(state="disabled")
                self.lbl_warning.config(text = WarningArray[WarningCodes.WARNING_MISSING_DATA])
                return

            s_date = datetime.datetime.combine(
                date_se_start.get_date(), datetime.datetime.min.time()
            ) + datetime.timedelta(hours=hs_se_start.get(), minutes=ms_se_start.get())
            e_date = datetime.datetime.combine(
                date_se_end.get_date(), datetime.datetime.min.time()
            ) + datetime.timedelta(hours=hs_se_end.get(), minutes=ms_se_end.get())

            # Test all subevents of the list, to check if there are two subevents with 
            # the same time frame, which is not allowed
            for subevent in subevent_list:
                subevent_data = subevent.split(" | ")
                # TODO s_date s_date_1
                s_date_1 = datetime.datetime.strptime(subevent_data[1], "%Y-%m-%d %H:%M:%S")
                e_date_1 = datetime.datetime.strptime(subevent_data[2], "%Y-%m-%d %H:%M:%S")

                # Test for overlapping time frames
                if err := test_time_frame(s_date_1, e_date_1, s_date, e_date):
                    btn_add_sube.config(state="disabled")
                    self.lbl_warning.config(text = WarningArray[err])
                    return

            btn_add_sube.config(state="normal")
            self.lbl_warning.config(text = WarningArray[WarningCodes.NO_WARNING])


        lbl_header = Label(self.root, text="Fill all cells to add the subevent.")
        lbl_header.grid(row=self.row_idx, column=1, padx=PAD_X, pady=(5, 0), sticky="W")
        self.lbl_warning = Label(self.root, fg='#f00', text="")
        self.lbl_warning.grid(row=self.row(), column=2, columnspan=2, padx=PAD_X, pady=(5, 0), sticky="E")

        #########
        # Subevent title input field
        #########
        sv_se_title = StringVar()
        sv_se_title.set(subevent_title)
        sv_se_title.trace("w", checkfull)
        lbl_se_title = Label(self.root, text="Title: ")
        lbl_se_title.grid(row=self.row_idx, column=0, padx=PAD_X, pady=PAD_Y, sticky="EW")
        ent_se_title = Entry(self.root, textvariable=sv_se_title)
        ent_se_title.grid(row=self.row(), column=1, columnspan=3, padx=PAD_X, pady=PAD_Y, sticky="EW")
        Hovertip(ent_se_title, TooltipDict["ent_se_title"])

        ######################
        # Date Frame (write) #
        # https://stackoverflow.com/questions/4443786/how-do-i-create-a-date-picker-in-tkinter
        ######################
        # TODO further compress the code needed here by moving it to dateutils
        #####
        # Start date
        #####
        lbl_se_sdate = Label(self.root, text="Start: ")
        lbl_se_sdate.grid(row=self.row_idx, column=0, padx=PAD_X, pady=PAD_Y, sticky="EW")
        date_se_start = DateEntry(
            self.root, width=12, background="darkblue", foreground="white", borderwidth=2, date_pattern="mm/dd/yyyy", mindate=e_sdate, maxdate=e_edate
        )
        date_se_start.grid(row=self.row_idx, column=1, padx=PAD_X, pady=PAD_Y, sticky="EW")
        date_se_start.bind("<<DateEntrySelected>>", checkfull)
        date_se_start.bind("<KeyRelease>", checkfull)
        Hovertip(date_se_start, TooltipDict["date_se_start"])

        #####
        # Start hour
        #####
        hs_se_start = HourSelector(self.root)
        hs_se_start.sb.grid(row=self.row_idx, column=2, padx=PAD_X, pady=PAD_Y, sticky="EW")
        hs_se_start.addTooltip(TooltipDict["hs_se_start"])

        #####
        # Start minute
        #####
        ms_se_start = MinuteSelector(self.root)
        ms_se_start.sb.grid(row=self.row(), column=3, padx=PAD_X, pady=PAD_Y, sticky="EW")
        ms_se_start.addTooltip(TooltipDict["ms_se_start"])

        #####
        # End date
        #####
        lbl_se_edate = Label(self.root, text="End: ")
        lbl_se_edate.grid(row=self.row_idx, column=0, padx=PAD_X, pady=PAD_Y, sticky="EW")
        date_se_end = DateEntry(
            self.root, width=12, background="darkblue", foreground="white", borderwidth=2, date_pattern="mm/dd/yyyy", mindate=e_sdate, maxdate=e_edate
        )
        date_se_end.grid(row=self.row_idx, column=1, padx=PAD_X, pady=PAD_Y, sticky="EW")
        date_se_end.bind("<<DateEntrySelected>>", checkfull)
        date_se_end.bind("<KeyRelease>", checkfull)
        Hovertip(date_se_end, TooltipDict["date_se_end"])

        #####
        # End hour
        #####
        hs_se_end = HourSelector(self.root, 23)
        hs_se_end.sb.grid(row=self.row_idx, column=2, padx=PAD_X, pady=PAD_Y, sticky="EW")
        hs_se_end.addTooltip(TooltipDict["hs_se_end"])

        #####
        # End minute
        #####
        ms_se_end = MinuteSelector(self.root, 59)
        ms_se_end.sb.grid(row=self.row(), column=3, padx=PAD_X, pady=PAD_Y, sticky="EW")
        ms_se_end.addTooltip(TooltipDict["ms_se_end"])

        separator = Separator(self.root, orient="horizontal")
        separator.grid(row=self.row(), column=0, columnspan=4, padx=PAD_X, pady=PAD_Y, sticky="EW")

        ##############
        # 
        ##############
        def add():
            s_date = datetime.datetime.combine(
                date_se_start.get_date(), datetime.datetime.min.time()
            ) + datetime.timedelta(hours=hs_se_start.get(), minutes=ms_se_start.get())
            e_date = datetime.datetime.combine(
                date_se_end.get_date(), datetime.datetime.min.time()
            ) + datetime.timedelta(hours=hs_se_end.get(), minutes=ms_se_end.get())

            self.subevent = sv_se_title.get() + " | " + str(s_date) + " | " + str(e_date)
            self.changed = True
            self.root.destroy()

        btn_abort = Button(
            self.root,
            text="Abort",
            command=self.closed,
        )
        btn_abort.grid(row=self.row_idx, column=1, padx=PAD_X, pady=(10, 15), sticky="EW")
        Hovertip(btn_abort, TooltipDict["btn_abort"])

        btn_add_sube = Button(
            self.root,
            text="Add",
            command=add,
            state="disabled",
        )
        btn_add_sube.grid(row=self.row(), column=3, padx=PAD_X, pady=(10, 15), sticky="EW")
        Hovertip(btn_add_sube, TooltipDict["btn_add_sube"])

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
            name = sv_p_name.get()
            if name:
                if self.db.has_elem("persons", ("name", name)):
                    btn_add_psn.config(state="disabled")
                    self.lbl_warning.config(text = WarningArray[WarningCodes.WARNING_PERSON_EXISTS])
                else:
                    btn_add_psn.config(state="normal")
                    self.lbl_warning.config(text = WarningArray[WarningCodes.NO_WARNING])
            else:
                btn_add_psn.config(state="disabled")
                self.lbl_warning.config(text = WarningArray[WarningCodes.WARNING_MISSING_DATA])

        lbl_header = Label(self.root, text="Give the person a name.")
        lbl_header.grid(row=self.row_idx, column=1, padx=PAD_X, pady=(5, 0), sticky="W")
        self.lbl_warning = Label(self.root, fg='#f00', text="")
        self.lbl_warning.grid(row=self.row(), column=2, padx=PAD_X, pady=(5, 0), sticky="E")

        # Person name input field
        sv_p_name = StringVar()
        sv_p_name.set(name)
        sv_p_name.trace("w", checkfull)
        lbl_p_name = Label(self.root, text="Name: ")
        lbl_p_name.grid(row=self.row_idx, column=0, padx=PAD_X, pady=PAD_Y, sticky="EW")
        ent_p_name = Entry(self.root, textvariable=sv_p_name, width=50)
        ent_p_name.grid(
            row=self.row(), column=1, columnspan=2, padx=PAD_X, pady=PAD_Y, sticky="EW"
        )
        Hovertip(ent_p_name, TooltipDict["ent_p_name"])

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

        # TODO should buttons be sticky EW or as small as possible?
        btn_abort = Button(
            self.root,
            text="Abort",
            command=self.closed,
        )
        btn_abort.grid(row=self.row_idx, column=1, padx=PAD_X, pady=(10, 15), sticky="W")
        Hovertip(btn_abort, TooltipDict["btn_abort"])

        btn_add_psn = Button(
            self.root,
            text="Add" if elem == "" else "Update",
            command=add,
            state="disabled",
        )
        btn_add_psn.grid(row=self.row(), column=2, padx=PAD_X, pady=(10, 15), sticky="E")
        Hovertip(btn_add_psn, TooltipDict["btn_add_psn" if elem == "" else "btn_update_psn"])

        center_window(self.root)

        # Making MessageBox Visible
        self.root.wait_window()

    # Function on Closeing MessageBox
    def closed(self):
        self.root.destroy()