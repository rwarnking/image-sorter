import operator
import os
from datetime import datetime, time, timedelta
from functools import partial
from idlelib.tooltip import Hovertip
from tkinter import DISABLED, END, RIGHT, Button, Frame, Label, StringVar, Text, filedialog, messagebox
from tkinter.ttk import Combobox, Scrollbar, Separator

import matplotlib as mpl
from database import EVENT_E_DATE, EVENT_S_DATE, EVENT_TITLE, Database
from dateutil.relativedelta import relativedelta
from debug_messages import InfoArray, InfoCodes
from guiboxes.artistbox import ModifyArtistBox
from guiboxes.basebox import (
    BTN_W,
    LINE_H,
    PAD_X,
    PAD_Y,
    PAD_Y_ADD,
    PAD_Y_LBL,
    SEPARATOR,
    WINDOW_W,
    BaseBox,
)
from guiboxes.eventbox import ModifyEventBox
from guiboxes.personbox import ModifyPersonBox
from guiboxes.selectionbox import SelectionBox
from helper import center_window
from meta_information import MetaInformation
from tkcalendar import Calendar
from tooltips import TooltipDict

TMODDB_H = 200
TMODDB_W = WINDOW_W - 2 * PAD_X


class ModifyDBBox(BaseBox):
    def __init__(self, header: str, db: Database, meta_info: MetaInformation):
        """
        Create a GUI element that includes a list of all entries of a table
        selectable via a combobox. Also allows to add, mod or delete entries.
        :param header: Title string
        :param db: Handle to the database containing events, artists, ...
        :param meta_info: The currently set metainformation (like directories)
        """
        super().__init__(header)

        # Save the database
        self.db = db
        # Used for saving the directories in metainfo
        self.meta_info = meta_info

        self.cldr_db = None

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
        btn_loadfile = self.add_cmp("btn_loadfile", Button(
            self.root,
            text="Load database from file",
            command=lambda: self.browse_button_open(self.meta_info.sv_db_src),
        ))
        btn_loadfile.grid(row=self.row_idx, column=0, padx=PAD_X, pady=PAD_Y, sticky="EW")
        Hovertip(btn_loadfile, TooltipDict["btn_loadfile"])

        lbl_load = Label(self.root, textvariable=self.meta_info.sv_db_src)
        lbl_load.grid(row=self.row(), column=1, columnspan=2, padx=PAD_X, pady=PAD_Y, sticky="EW")

        # Save events to file
        btn_savefile = self.add_cmp("btn_savefile", Button(
            self.root,
            text="Save database to file",
            command=lambda: self.browse_button_save(self.meta_info.sv_db_tgt),
        ))
        btn_savefile.grid(row=self.row_idx, column=0, padx=PAD_X, pady=PAD_Y, sticky="EW")
        Hovertip(btn_savefile, TooltipDict["btn_savefile"])

        lbl_save = Label(self.root, textvariable=self.meta_info.sv_db_tgt)
        lbl_save.grid(row=self.row(), column=1, columnspan=2, padx=PAD_X, pady=PAD_Y, sticky="EW")

        separator = Separator(self.root, orient="horizontal")
        separator.grid(row=self.row(), column=0, columnspan=3, padx=PAD_X, pady=PAD_Y, sticky="EW")

        ####################
        # Reorder database #
        ####################
        def reorder_button():
            self.disable_all_cmps()
            info = self.db.reorder_by_date()
            self.lbl_info.config(
                text=InfoArray[info], fg="#0a0" if info == InfoCodes.REORDER_SUCCESS else "#a00"
            )
            self.reset_all_cmps()

        # Reoder the currently loaded database
        btn_reorder = self.add_cmp("btn_reorder", Button(
            self.root,
            text="Reorder currently loaded database by date",
            command=lambda: reorder_button(),
        ))
        btn_reorder.grid(row=self.row(), column=0, padx=PAD_X, pady=PAD_Y, sticky="EW")
        Hovertip(btn_reorder, TooltipDict["btn_reorder"])

        separator = Separator(self.root, orient="horizontal")
        separator.grid(row=self.row(), column=0, columnspan=3, padx=PAD_X, pady=PAD_Y, sticky="EW")

        ##############################
        # Select table from database #
        ##############################
        Label(
            self.root,
            text="Selected database table:",
        ).grid(row=self.row_idx, column=0, padx=PAD_X, pady=PAD_Y, sticky="w")

        def combobox_select(_):
            table = self.db_select.get()
            if table == "events":
                bd = self.cldr_db.__getitem__("borderwidth")
                self.cldr_db._cal_frame.pack(fill="both", expand=True, padx=bd, pady=bd)
                self.cldr_db.grid()
                self.get_cmp("btn_clear_m").grid()
            elif table == "artists":
                self.cldr_db._cal_frame.pack_forget()
                self.cldr_db.grid()
                self.get_cmp("btn_clear_m").grid_remove()
            else:
                self.cldr_db.grid_remove()
                self.get_cmp("btn_clear_m").grid_remove()
            self.lbl_info.config(text=InfoArray[InfoCodes.NO_INFO])
            self.updateGUI(table)

        list_dbs = [
            "events",
            "artists",
            "persons",
        ]
        self.db_select = StringVar()
        self.db_select.set(list_dbs[0])
        cb_dbs = self.add_cmp("cb_dbs", Combobox(self.root, textvariable=self.db_select))
        # Write artist values from database
        cb_dbs["values"] = list_dbs
        # Prevent typing a value
        cb_dbs["state"] = "readonly"
        # Place the widget
        cb_dbs.grid(row=self.row(), column=1, columnspan=2, padx=PAD_X, pady=PAD_Y, sticky="EW")
        # Bind callback
        cb_dbs.bind("<<ComboboxSelected>>", combobox_select)
        Hovertip(cb_dbs, TooltipDict["cb_dbs"])

        #################
        # Calendar view #
        #################
        # Save the row index for the calendar since the calendar can only
        # be added the the grid after the textfield otherwise the tooltip
        # does not work (unclear why that is)
        row_idx_cal = self.row()

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

        btn_add = self.add_cmp("btn_add", Button(self.text_db_add, text="Add", command=self.clickAdd, width=BTN_W))
        Hovertip(btn_add, TooltipDict["btn_add"])
        self.text_db_add.window_create("end", window=btn_add)

        # Filler object for nicer alignment
        btn_null = Button(
            self.text_db_add, text="", width=BTN_W, background="white", state=DISABLED
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
        # This is needed so the Calendar tooltip is shown
        self.text_db_list.update()

        #################
        # Calendar view #
        #################
        # https://tkcalendar.readthedocs.io/en/stable/Calendar.html
        # https://tkcalendar.readthedocs.io/en/stable/_modules/tkcalendar/calendar_.html#Calendar

        # TODO self.cldr_db vs get_cmp
        self.cldr_db = self.add_cmp("cldr_db", Calendar(
            self.root,
            tooltipdelay=100,
            weekendbackground="white",
            weekendforeground="black",
            othermonthwebackground="gray93",
        ))
        self.cldr_db.grid(
            row=row_idx_cal, column=0, columnspan=3, padx=PAD_X, pady=PAD_Y, sticky="EW"
        )

        def calendar_selected(_):
            # Get date
            date_sel = self.cldr_db.selection_get()
            event_data = self.cldr_db.get_calevents(date_sel)

            if len(event_data) > 0:
                idx = event_data[0]
                if len(event_data) > 1:
                    # Select one of the found events for this date
                    box = SelectionBox(
                        title="Warning: Multiple events found!",
                        message=("For the selected date multiple events are present."),
                        actioncall="Select one event:",
                        # Use the calendar tags to present the user information for each event
                        options=[
                            f"{i}: {self.cldr_db.calevent_cget(i, 'tags')[0]}" for i in event_data
                        ],
                    )
                    # Extract the event index from the choice string (month index not db index)
                    idx = int(box.choice.get().split(":")[0])
                self.clickModify(self.cldr_db.calevent_cget(idx, "tags")[0])
            else:
                self.clickAdd()

        self.cldr_db.bind("<<CalendarSelected>>", calendar_selected)
        self.cldr_db.bind(
            "<<CalendarMonthChanged>>", lambda _: self.updateGUI(self.db_select.get())
        )

        # Update calendar AND textfields
        self.updateGUI(self.db_select.get())

        #################################
        # Remove buttons and Info label #
        #################################
        btn_clear_m = self.add_cmp("btn_clear_m", Button(
            self.root,
            text="Clear current month of selected table",
            command=lambda: self.clickClearMonth(),
        ))
        btn_clear_m.grid(row=self.row(), column=2, padx=PAD_X, pady=PAD_Y, sticky="EW")
        Hovertip(btn_clear_m, TooltipDict["btn_clear_month"])

        # Info label for example for success or error informations
        self.lbl_info = Label(self.root, text="")
        self.lbl_info.grid(
            row=self.row_idx, column=0, columnspan=2, padx=PAD_X, pady=PAD_Y_LBL, sticky="W"
        )

        btn_clear = self.add_cmp("btn_clear", Button(
            self.root,
            text="Clear selected table",
            command=lambda: self.clickClear(),
        ))
        btn_clear.grid(row=self.row(), column=2, padx=PAD_X, pady=PAD_Y, sticky="EW")
        Hovertip(btn_clear, TooltipDict["btn_clear"])

        separator = Separator(self.root, orient="horizontal")
        separator.grid(row=self.row(), column=0, columnspan=3, padx=PAD_X, pady=PAD_Y, sticky="EW")

        ###############
        # Done button #
        ###############
        btn_done = self.add_cmp("btn_done", Button(
            self.root,
            text="Done",
            command=self.close,
        ))
        btn_done.grid(row=self.row(), column=2, padx=PAD_X, pady=PAD_Y, sticky="EW")
        Hovertip(btn_done, TooltipDict["btn_done"])

        center_window(self.root)

        # Making MessageBox Visible
        self.root.wait_window()

    def browse_button_open(self, dir: StringVar):
        """
        Open filedialog for browsing for a database file to open.
        :param dir: The directory to load from.
        """
        self.disable_all_cmps()

        filepath = filedialog.askopenfilename(
            initialdir=os.path.dirname(dir.get()),
            filetypes=(("json file", "*.json"), ("excel file", "*.xlsx")),
        )
        if filepath == "":
            messagebox.showinfo(message="Did not load! No filename provided.", title="Error")
            self.reset_all_cmps()
            return

        if filepath.lower().endswith(".json"):
            info = self.db.load_from_json(filepath)
        elif filepath.lower().endswith(".xlsx"):
            info = self.db.load_from_xlsx(filepath)
        else:
            messagebox.showinfo(message="Could not load! Filetype was not valid.", title="Error")
            self.reset_all_cmps()
            return

        self.updateGUI(self.db_select.get())
        self.lbl_info.config(
            text=InfoArray[info], fg="#0a0" if info == InfoCodes.LOAD_SUCCESS else "#a80"
        )
        dir.set(filepath)
        self.reset_all_cmps()

    def browse_button_save(self, dir: StringVar):
        """
        Open filedialog for browsing for a database file to save to.
        :param dir: The directory to save to.
        """
        self.disable_all_cmps()

        filepath = filedialog.asksaveasfilename(
            initialdir=os.path.dirname(dir.get()),
            defaultextension=".json",
            filetypes=(("json file", "*.json"), ("excel file", "*.xlsx")),
        )
        filename = os.path.basename(filepath)
        if filename == "" or filename.lower() == ".json" or filename.lower() == ".xlsx":
            messagebox.showinfo(message="Could not save! Filename was not valid.", title="Error")
            self.reset_all_cmps()
            return

        if filepath.lower().endswith(".json"):
            info = self.db.save_to_json(filepath)
        elif filepath.lower().endswith(".xlsx"):
            info = self.db.save_to_xlsx(filepath)
        else:
            messagebox.showinfo(
                message="Could not save! Select a valid fileextension.", title="Error"
            )
            self.reset_all_cmps()
            return

        self.lbl_info.config(
            text=InfoArray[info], fg="#0a0" if info == InfoCodes.SAVE_SUCCESS else "#a00"
        )
        dir.set(filepath)
        self.reset_all_cmps()

    def clickAdd(self):
        """
        Function when pressing the add button.
        Depending on the selected table an element is created.
        """
        self.disable_all_cmps()
        self.lbl_info.config(text=InfoArray[InfoCodes.NO_INFO])

        str_selection = self.db_select.get()
        if str_selection == "events":
            date = self.getDefaultDay()
            box = ModifyEventBox("Add event", self.db, date)
        elif str_selection == "artists":
            date = self.getDefaultDay()
            box = ModifyArtistBox("Add artist", self.db, date)
        elif str_selection == "persons":
            box = ModifyPersonBox("Add person", self.db)

        if box.changed:
            self.updateGUI(str_selection)
            self.lbl_info.config(text=InfoArray[box.info], fg="#0a0" if box.info < 9 else "#a00")
        self.reset_all_cmps()

    def clickModify(self, elem: str):
        """
        Function when pressing the modify button. The selected elem is modified.
        :param elem: The element that should be modified.
        """
        self.disable_all_cmps()
        self.lbl_info.config(text=InfoArray[InfoCodes.NO_INFO])

        str_selection = self.db_select.get()
        if str_selection == "events":
            box: BaseBox = ModifyEventBox("Modify event", self.db, elem)
        elif str_selection == "artists":
            box = ModifyArtistBox("Modify artist", self.db, elem)
        elif str_selection == "persons":
            box = ModifyPersonBox("Modify person", self.db, elem)

        if box.changed:
            self.updateGUI(str_selection)
            self.lbl_info.config(text=InfoArray[box.info], fg="#0a0" if box.info < 9 else "#a00")
        self.reset_all_cmps()

    def clickDelete(self, elem: str):
        """
        Function when pressing the delete button. The selected elem is deleted.
        :param elem: The element that should be deleted.
        """
        self.disable_all_cmps()
        str_selection = self.db_select.get()
        if str_selection == "events":
            elm_data = elem.split(SEPARATOR)
            info = self.db.delete_event_s(elm_data[1], elm_data[2], elm_data[3])
        elif str_selection == "artists":
            elm_data = elem.split(SEPARATOR)
            # Obacht: elm_data[0] is the index not the name
            info = self.db.delete_artist_s(
                int(elm_data[1]), elm_data[2], elm_data[3], elm_data[4], elm_data[5], elm_data[6]
            )
        elif str_selection == "persons":
            elm_data = elem.split(SEPARATOR)
            info = self.db.delete_person(elm_data[1])

        self.updateGUI(str_selection)
        self.lbl_info.config(text=InfoArray[info], fg="#0a0" if info < 9 else "#a00")
        self.reset_all_cmps()

    def clickClear(self):
        """
        Function when pressing the clear button. The selected table in the database is cleared.
        """
        self.disable_all_cmps()
        str_selection = self.db_select.get()
        info = self.db.clean(str_selection)
        self.updateGUI(str_selection)
        self.lbl_info.config(text=InfoArray[info], fg="#0a0" if info < 9 else "#a00")
        self.reset_all_cmps()

    def clickClearMonth(self):
        """
        Function when pressing the clear month button.
        All entrys in the database of selected table and in the current month are deleted.
        """
        self.disable_all_cmps()
        info = InfoCodes.DEL_SUCCESS
        str_selection = self.db_select.get()
        if str_selection == "events":
            lst_content = self.getEvents()
            for elem in lst_content:
                tmp_info = self.db.delete_event(
                    elem[EVENT_TITLE], elem[EVENT_S_DATE], elem[EVENT_E_DATE]
                )
                if tmp_info == InfoCodes.DEL_ERROR:
                    info = InfoCodes.DEL_ERROR

        self.updateGUI(str_selection)
        self.lbl_info.config(text=InfoArray[info], fg="#0a0" if info < 9 else "#a00")
        self.reset_all_cmps()

    def updateGUI(self, table):
        """
        Update the GUI to display the correct data.
        :param table: The currently selected table
        """
        self.cldr_db.selection_clear()

        if table == "events":
            lst_content = self.getEvents()
            self.updateCalender(lst_content)
        elif table == "persons":
            lst_content = self.getPersons()
        elif table == "artists":
            lst_content = self.getArtists()
        else:
            lst_content = self.db.get_all(table)

        self.updateListFrame(table, lst_content)

    def updateListFrame(self, table: str, lst_content):
        """
        Update the text field listing all entries of the selected table.
        How to create a scrollable list of buttons in Tkinter?
        https://stackoverflow.com/questions/68288119/
        How to pass arguments to a Button command in Tkinter?
        https://stackoverflow.com/questions/6920302/
        :param table: The currently selected table
        :param lst_content: The content for the text frame
        """
        # Clear all content in the text area
        self.text_db_list.delete("1.0", END)

        # TODO wrapper function for self.cmps?
        for key in list(self.cmps.keys()):
            if "mod_" in key:
                del self.cmps[key]
            if "del_" in key:
                del self.cmps[key]

        list_table_content = [SEPARATOR.join(str(e) for e in x) for x in lst_content]

        # Creating label for each artist/event/...
        for i, e in enumerate(list_table_content):
            btn_mod_name = f"mod_{i}"
            btn_del_name = f"del_{i}"
            btn_mod = self.add_cmp(btn_mod_name, Button(
                self.text_db_list, text="Mod", command=partial(self.clickModify, e), width=BTN_W
            ))
            Hovertip(btn_mod, TooltipDict["btn_mod"])
            self.text_db_list.window_create("end", window=btn_mod)

            btn_del = self.add_cmp(btn_del_name, Button(
                self.text_db_list, text="Del", command=partial(self.clickDelete, e), width=BTN_W
            ))
            Hovertip(btn_del, TooltipDict["btn_del"])
            self.text_db_list.window_create("end", window=btn_del)

            # Special case because the artist contains a person id
            if table == "artists":
                first_idx = e.index(SEPARATOR)
                second_idx = e.index(SEPARATOR, first_idx + 1)
                num = int(e[first_idx + 3 : second_idx])
                e = f"{e[:second_idx]} ({self.db.get_pname(num)}){e[second_idx:]}"

            # Remove index from text frame, since they are not sorted anyways
            first_idx = e.index(SEPARATOR)
            e = f"{e[first_idx + len(SEPARATOR):]}"

            self.text_db_list.insert("end", " " + e + "\n")

        self.text_db_list.update()

    def updateCalender(self, lst_events):
        """
        Add all events of the given list to the calendar.
        For each event its days are iterated and added the event of the calendar.
        For each display event a unique color is generated.
        :param lst_events: The list of events to add
        """
        self.cldr_db.calevent_remove("all")

        viridis = mpl.colormaps["viridis"].resampled(len(lst_events))

        for i, e in enumerate(lst_events):
            # Get a list of days from the start and to the end date of the event
            lst_days = [
                e[EVENT_S_DATE] + timedelta(days=x)
                for x in range(((e[EVENT_E_DATE] + timedelta(days=1)) - e[EVENT_S_DATE]).days)
            ]
            for day in lst_days:
                tmp_str = SEPARATOR.join(str(x) for x in e)
                self.cldr_db.calevent_create(day, e[1], tmp_str)
                r, g, b, a = [int(x * 255) for x in viridis(i)]
                # Change font color depending on brightness
                brightness = (299 * r + 587 * g + 114 * b) / 1000
                self.cldr_db.tag_config(
                    tmp_str,
                    foreground="white" if brightness < 125 else "black",
                    background=f"#{r:02x}{g:02x}{b:02x}",
                )

    def getEvents(self):
        """
        Get a list of events in the currently selected month.
        For this the calendar month is queried and the events are obtained from the database
        using a timeframe. The list is sorted by the start date of the event.
        :return: List of events in month
        """
        month, year = self.cldr_db.get_displayed_month()
        month_date = datetime(year, month, 1)

        # Get first day of month
        first_day = month_date + relativedelta(day=1)
        # Get monday before first day of month
        first_day -= timedelta(days=first_day.weekday())
        # Get last day of month
        # last_day = month_date + relativedelta(day=31, hour=23, minute=59, second=59)
        # Get sunday 5 weeks later than the first day
        last_day = first_day + timedelta(weeks=5, days=6, hours=23, minutes=59, seconds=59)

        lst_events = self.db.get_by_timeframe("events", first_day, last_day)
        lst_events.sort(key=lambda x: x[EVENT_S_DATE])

        return lst_events

    def getArtists(self):
        """
        Get a list of artists in the currently selected month.
        For this the calendar month is queried and the artists are obtained from the database
        using a timeframe. The list is sorted by the name and the start date of the artist.
        :return: List of events in month
        """
        month, year = self.cldr_db.get_displayed_month()
        month_date = datetime(year, month, 1)

        # Get first day of month
        first_day = month_date + relativedelta(day=1)
        # Get last day of month
        last_day = month_date + relativedelta(day=31, hour=23, minute=59, second=59)

        lst_content = self.db.get_by_timeframe("artists", first_day, last_day)
        lst_content.sort(key=operator.itemgetter(1, 4))

        return lst_content

    def getPersons(self):
        """
        Get a list of persons. The list is sorted by the name of the person.
        :return: List of persons
        """
        lst_content = self.db.get_all("persons")
        # TODO sort by lastname
        lst_content.sort(key=lambda x: x[1])
        return lst_content

    def getDefaultDay(self):
        """
        Get the currently most fitting default day.
        If a day is selected it is returned, otherwise the first of the current month is used.
        The result is returned in form of a string with the earliest and latest time of the day
        are separated by a separator symbol.
        :return: The first and last moment of the default day as string.
        """
        if date_sel := self.cldr_db.selection_get():
            # Create latest time at the same day
            date_sel_night = datetime.combine(date_sel, time.max)
            return f"{date_sel}{SEPARATOR}{date_sel_night}"

        # If no day is selected use the currently selected month as start date
        month, year = self.cldr_db.get_displayed_month()
        month_date = datetime(year, month, 1)
        month_date_night = datetime.combine(month_date, time.max)
        return f"{month_date}{SEPARATOR}{month_date_night}"
