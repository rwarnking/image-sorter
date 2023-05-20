import os
from functools import partial
from idlelib.tooltip import Hovertip
from tkinter import END, RIGHT, Button, Frame, Label, StringVar, Text, filedialog, messagebox
from tkinter.ttk import Combobox, Scrollbar, Separator

from database import Database
from debug_messages import InfoArray, InfoCodes
from guiboxes.artistbox import ModifyArtistBox
from guiboxes.basebox import BTN_W, LINE_H, PAD_X, PAD_Y, PAD_Y_ADD, PAD_Y_LBL, WINDOW_W, BaseBox
from guiboxes.eventbox import ModifyEventBox
from guiboxes.personbox import ModifyPersonBox
from helper import center_window
from meta_information import MetaInformation
from tooltips import TooltipDict

TMODDB_H = 200
TMODDB_W = WINDOW_W - 2 * PAD_X


class ModifyDBBox(BaseBox):
    def __init__(self, header: str, db: Database, meta_info: MetaInformation):
        """
        Create a GUI element that includes a list of all entries of a table
        selectable via a combobox. Also allows to add, mod or delete entries.
        """
        super().__init__(header)

        # Save the database
        self.db = db
        # Used for saving the directories in metainfo
        self.meta_info = meta_info

        ###############
        # Header Line #
        ###############
        Label(
            self.root,
            text="Inspect, modify, add and delete entries from the database.",
        ).grid(row=self.row(), column=0, columnspan=3, padx=PAD_X, pady=PAD_Y_LBL, sticky="w")

        separator = Separator(self.root, orient="horizontal")
        separator.grid(row=self.row(), column=0, columnspan=3, padx=PAD_X, pady=PAD_Y, sticky="EW")

        ###########################
        # Saving and loading json #
        ###########################
        # Load events from file
        btn_loadfile = Button(
            self.root,
            text="Load database from json file",
            command=lambda: self.browse_button_open(self.meta_info.sv_db_src),
        )
        btn_loadfile.grid(row=self.row_idx, column=0, padx=PAD_X, pady=PAD_Y, sticky="EW")
        Hovertip(btn_loadfile, TooltipDict["btn_loadfile"])

        lbl_load = Label(self.root, textvariable=self.meta_info.sv_db_src)
        lbl_load.grid(row=self.row(), column=1, columnspan=2, padx=PAD_X, pady=PAD_Y, sticky="EW")

        # Save events to file
        btn_savefile = Button(
            self.root,
            text="Save database to json file",
            command=lambda: self.browse_button_save(self.meta_info.sv_db_tgt),
        )
        btn_savefile.grid(row=self.row_idx, column=0, padx=PAD_X, pady=PAD_Y, sticky="EW")
        Hovertip(btn_savefile, TooltipDict["btn_savefile"])

        lbl_save = Label(self.root, textvariable=self.meta_info.sv_db_tgt)
        lbl_save.grid(row=self.row(), column=1, columnspan=2, padx=PAD_X, pady=PAD_Y, sticky="EW")

        separator = Separator(self.root, orient="horizontal")
        separator.grid(row=self.row(), column=0, columnspan=3, padx=PAD_X, pady=PAD_Y, sticky="EW")

        ##############################
        # Select table from database #
        ##############################
        Label(
            self.root,
            text="Selected database table:",
        ).grid(row=self.row_idx, column=0, padx=PAD_X, pady=PAD_Y, sticky="w")

        def update_db_gui(_):
            self.lbl_info.config(text=InfoArray[InfoCodes.NO_INFO])
            self.updateListFrame(db, self.db_select.get())

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
        cb_dbs.grid(row=self.row(), column=1, columnspan=2, padx=PAD_X, pady=PAD_Y, sticky="EW")
        # Bind callback
        cb_dbs.bind("<<ComboboxSelected>>", update_db_gui)
        Hovertip(cb_dbs, TooltipDict["cb_dbs"])

        ######################################
        # Frame and textfield for add button #
        ######################################
        self.frame_db_add = Frame(self.root, width=TMODDB_W, height=LINE_H, bg="white")
        self.frame_db_add.pack_propagate(False)
        self.frame_db_add.grid(
            row=self.row(), column=0, columnspan=3, padx=PAD_X, pady=PAD_Y_ADD, sticky="EW"
        )

        # Word wrap
        # https://stackoverflow.com/questions/19029157/
        self.text_db_add = Text(self.frame_db_add, wrap="none")
        self.text_db_add.pack(fill="both", expand=True)

        btn_add = Button(self.text_db_add, text="Add", command=self.clickAdd, width=BTN_W)
        Hovertip(btn_add, TooltipDict["btn_add"])
        self.text_db_add.window_create("end", window=btn_add)
        btn_null = Button(
            self.text_db_add, text="", width=BTN_W, background="white", state="disabled"
        )
        self.text_db_add.window_create("end", window=btn_null)

        self.text_db_add.insert("end", " ...")

        #########################################
        # Frame and textfield for table content #
        #########################################
        self.frame_db_list = Frame(self.root, width=TMODDB_W, height=TMODDB_H, bg="white")
        self.frame_db_list.pack_propagate(False)
        self.frame_db_list.grid(
            row=self.row(), column=0, columnspan=3, padx=PAD_X, pady=PAD_Y, sticky="EW"
        )

        # Word wrap
        # https://stackoverflow.com/questions/19029157/
        self.text_db_list = Text(self.frame_db_list, wrap="none")
        self.sb_db_list = Scrollbar(self.frame_db_list, command=self.text_db_list.yview)
        self.sb_db_list.pack(side=RIGHT, fill="y")
        self.text_db_list.configure(yscrollcommand=self.sb_db_list.set)
        self.text_db_list.pack(fill="both", expand=True)

        self.updateListFrame(db, self.db_select.get())

        #####################
        # Remove all button #
        #####################
        self.lbl_info = Label(self.root, text="")
        self.lbl_info.grid(
            row=self.row_idx, column=0, columnspan=2, padx=PAD_X, pady=PAD_Y_LBL, sticky="W"
        )

        btn_clear = Button(
            self.root,
            text="Clear selected table",
            command=lambda: self.clickClear(),
        )
        btn_clear.grid(row=self.row(), column=2, padx=PAD_X, pady=PAD_Y, sticky="EW")
        Hovertip(btn_clear, TooltipDict["btn_clear"])

        separator = Separator(self.root, orient="horizontal")
        separator.grid(row=self.row(), column=0, columnspan=3, padx=PAD_X, pady=PAD_Y, sticky="EW")

        ###############
        # Done button #
        ###############
        btn_done = Button(
            self.root,
            text="Done",
            command=self.close,
        )
        btn_done.grid(row=self.row(), column=2, padx=PAD_X, pady=PAD_Y, sticky="EW")
        Hovertip(btn_done, TooltipDict["btn_done"])

        center_window(self.root)

        # Making MessageBox Visible
        self.root.wait_window()

    def browse_button_open(self, dir: StringVar):
        """Open filedialog for browsing for a database file to open."""
        filename = filedialog.askopenfilename(initialdir=os.path.dirname(dir.get()))
        if filename != "" and not filename.lower().endswith(".json"):
            messagebox.showinfo(message="Please select a json file.", title="Error")
        elif filename != "":
            info = self.db.load_from_file(filename)
            self.updateListFrame(self.db, self.db_select.get())
            self.lbl_info.config(
                text=InfoArray[info], fg="#0a0" if info == InfoCodes.LOAD_SUCCESS else "#a80"
            )
            dir.set(filename)

    def browse_button_save(self, dir: StringVar):
        """Open filedialog for browsing for a database file to save to."""
        filename = filedialog.asksaveasfilename(initialdir=os.path.dirname(dir.get()))
        if filename != "" and not filename.lower().endswith(".json"):
            messagebox.showinfo(message="Please select a json file.", title="Error")
        elif filename != "":
            info = self.db.save_to_file(filename)
            self.lbl_info.config(
                text=InfoArray[info], fg="#0a0" if info == InfoCodes.SAVE_SUCCESS else "#a00"
            )
            dir.set(filename)

    def clickAdd(self):
        """Function when pressing the add button. The selected box is created."""
        self.lbl_info.config(text=InfoArray[InfoCodes.NO_INFO])

        str_selection = self.db_select.get()
        if str_selection == "events":
            box = ModifyEventBox("Add event", self.db)
        elif str_selection == "artists":
            box = ModifyArtistBox("Add artist", self.db)
        elif str_selection == "persons":
            box = ModifyPersonBox("Add person", self.db)

        if box.changed:
            self.updateListFrame(self.db, self.db_select.get())
            self.lbl_info.config(text=InfoArray[box.info], fg="#0a0" if box.info < 9 else "#a00")

    def clickModify(self, elem: str):
        """Function when pressing the modify button. The selected box is created."""
        self.lbl_info.config(text=InfoArray[InfoCodes.NO_INFO])

        str_selection = self.db_select.get()
        if str_selection == "events":
            box: BaseBox = ModifyEventBox("Modify event", self.db, elem)
        elif str_selection == "artists":
            box = ModifyArtistBox("Modify artist", self.db, elem)
        elif str_selection == "persons":
            box = ModifyPersonBox("Modify person", self.db, elem)

        if box.changed:
            self.updateListFrame(self.db, self.db_select.get())
            self.lbl_info.config(text=InfoArray[box.info], fg="#0a0" if box.info < 9 else "#a00")

    def clickDelete(self, elem: str):
        """Function when pressing the delete button. The selected box is created."""
        str_selection = self.db_select.get()
        if str_selection == "events":
            elm_data = elem.split(" | ")
            info = self.db.delete_event_s(elm_data[1], elm_data[2], elm_data[3])
        elif str_selection == "artists":
            elm_data = elem.split(" | ")
            # Obacht: elm_data[0] is the index not the name
            info = self.db.delete_artist_s(
                int(elm_data[1]), elm_data[2], elm_data[3], elm_data[4], elm_data[5], elm_data[6]
            )
        elif str_selection == "persons":
            elm_data = elem.split(" | ")
            info = self.db.delete_person(elm_data[1])

        self.updateListFrame(self.db, self.db_select.get())
        self.lbl_info.config(text=InfoArray[info], fg="#0a0" if info < 9 else "#a00")

    def clickClear(self):
        """Function when pressing the clear button. The selec table in the database is cleared."""
        str_selection = self.db_select.get()
        info = self.db.clean(str_selection)
        self.updateListFrame(self.db, str_selection)
        self.lbl_info.config(text=InfoArray[info], fg="#0a0" if info < 9 else "#a00")

    def updateListFrame(self, db: Database, table: str):
        """
        Update the text field listing all entries of the selected table.
        How to create a scrollable list of buttons in Tkinter?
        https://stackoverflow.com/questions/68288119/
        How to pass arguments to a Button command in Tkinter?
        https://stackoverflow.com/questions/6920302/
        """
        # Clear all content in the text area
        self.text_db_list.delete("1.0", END)

        list_table_content = [" | ".join(str(e) for e in x) for x in db.get_all(table)]

        ############################
        str_selection = self.db_select.get()

        # Creating label for each artist/event/...
        for i, e in enumerate(list_table_content):
            btn_mod = Button(
                self.text_db_list, text="Mod", command=partial(self.clickModify, e), width=BTN_W
            )
            Hovertip(btn_mod, TooltipDict["btn_mod"])
            self.text_db_list.window_create("end", window=btn_mod)

            btn_del = Button(
                self.text_db_list, text="Del", command=partial(self.clickDelete, e), width=BTN_W
            )
            Hovertip(btn_del, TooltipDict["btn_del"])
            self.text_db_list.window_create("end", window=btn_del)

            # Special case because the artist contains a person id
            if str_selection == "artists":
                first_idx = e.index(" | ")
                second_idx = e.index(" | ", first_idx + 1)
                num = int(e[first_idx + 3 : second_idx])
                e = f"{e[:second_idx]} ({self.db.get_pname(num)}){e[second_idx:]}"

            self.text_db_list.insert("end", " " + e + "\n")

        self.text_db_list.update()
