import datetime
import os
import sys
import threading
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

# own imports
from database import Database
from helper import lt_window
from idlelib.tooltip import Hovertip
from meta_information import MetaInformation
from sorter import Sorter
from tkcalendar import DateEntry
from tooltips import TooltipDict

PAD_X = 20
PAD_Y = (10, 0)

# https://stackoverflow.com/questions/404744/
if getattr(sys, "frozen", False):
    # If the application is run as a bundle, the PyInstaller bootloader
    # extends the sys module by a flag frozen=True and sets the app
    # path into variable _MEIPASS'.
    APP_PATH = sys._MEIPASS  # type: ignore
else:
    APP_PATH = os.path.dirname(os.path.abspath(__file__))


class MainApp:
    def __init__(self, window):
        self.meta_info = MetaInformation()

        self.row_idx = 0

        self.db = Database()

        self.init_resource_folder(window)
        separator = Separator(window, orient="horizontal")
        separator.grid(row=self.row(), column=0, columnspan=3, padx=PAD_X, pady=PAD_Y, sticky="EW")
        self.init_signatures(window)
        separator = Separator(window, orient="horizontal")
        separator.grid(row=self.row(), column=0, columnspan=3, padx=PAD_X, pady=PAD_Y, sticky="EW")
        self.init_event_system(window)
        separator = Separator(window, orient="horizontal")
        separator.grid(row=self.row(), column=0, columnspan=3, padx=PAD_X, pady=PAD_Y, sticky="EW")
        self.init_artist_system(window)
        separator = Separator(window, orient="horizontal")
        separator.grid(row=self.row(), column=0, columnspan=3, padx=PAD_X, pady=PAD_Y, sticky="EW")
        self.init_checkboxes(window)
        separator = Separator(window, orient="horizontal")
        separator.grid(row=self.row(), column=0, columnspan=3, padx=PAD_X, pady=PAD_Y, sticky="EW")
        self.init_progressindicator(window)
        separator = Separator(window, orient="horizontal")
        separator.grid(row=self.row(), column=0, columnspan=3, padx=PAD_X, pady=PAD_Y, sticky="EW")
        self.init_details(window)

        self.run_button = Button(window, text="Dew it", command=lambda: self.run(window))
        self.run_button.grid(row=self.row_idx, column=0, columnspan=3, padx=PAD_X, pady=10)

        self.db.set_out_text(self.details_text)

        lt_window(window)

    def row(self):
        self.row_idx += 1
        return self.row_idx - 1

    def run(self, window):
        if not self.meta_info.finished:
            messagebox.showinfo(message="Modification is already happening.", title="Error")
            window.after(50, lambda: self.listen_for_result(window))
            return

        s = Sorter(self.meta_info)
        self.meta_info.finished = False
        self.meta_info.file_count = 0
        self.meta_info.dont_ask_again.set(False)
        self.listen_for_result(window)

        self.new_thread = threading.Thread(target=s.run)
        self.new_thread.start()
        window.after(50, lambda: self.listen_for_result(window))

    def listen_for_result(self, window):
        f_count = self.meta_info.file_count
        f_count_max = self.meta_info.file_count_max

        self.file_progress["value"] = f_count
        self.file_progress["maximum"] = f_count_max
        self.file_progress.update()

        if not self.meta_info.text_queue.empty():
            self.details_text.insert(END, self.meta_info.text_queue.get(0))

        if self.meta_info.finished:
            self.file_label.config(text=f"Finished all {f_count_max} files.")
            self.time_label.config(text="Done.")

            while not self.meta_info.text_queue.empty():
                self.details_text.insert(END, self.meta_info.text_queue.get(0))
        else:
            # self.meta_info.update_estimated_time()
            # s = int(self.meta_info.timer.estimated_time % 60)
            # m = int(self.meta_info.timer.estimated_time / 60)
            # self.time_label.config(
            #     text=f"Processing Data. Estimated rest time: {m} minutes and {s} seconds."
            # )

            self.file_label.config(text=f"Finished file {f_count} of {f_count_max} files.")
            self.time_label.config(text="")
            window.after(50, lambda: self.listen_for_result(window))

    ###############################################################################################
    # Initialization functions
    ###############################################################################################
    def init_resource_folder(self, window):
        def browse_button(dir):
            filename = filedialog.askdirectory(initialdir=dir.get())
            if filename != "":
                dir.set(filename)

        self.meta_info.set_dirs(APP_PATH, APP_PATH, APP_PATH, APP_PATH, APP_PATH, APP_PATH)

        # Source directory
        lbl1 = Label(window, text="Source directory:")
        lbl1.grid(row=self.row_idx, column=0, padx=PAD_X, pady=PAD_Y, sticky="EW")
        lbl_src_dir = Label(window, textvariable=self.meta_info.img_src)
        lbl_src_dir.grid(
            row=self.row_idx, column=1, columnspan=1, padx=PAD_X, pady=PAD_Y, sticky="EW"
        )
        btn_src = Button(
            window,
            text="Browse",
            command=lambda: browse_button(self.meta_info.img_src),
        )
        btn_src.grid(row=self.row(), column=2, padx=PAD_X, pady=PAD_Y, sticky="EW")
        Hovertip(btn_src, TooltipDict["btn_src"])

        # Target directory
        lbl2 = Label(window, text="Target directory:")
        lbl2.grid(row=self.row_idx, column=0, padx=PAD_X, pady=PAD_Y, sticky="EW")
        lbl_tgt_dir = Label(window, textvariable=self.meta_info.img_tgt)
        lbl_tgt_dir.grid(row=self.row_idx, column=1, padx=PAD_X, pady=PAD_Y, sticky="EW")
        btn_tgt = Button(
            window,
            text="Browse",
            command=lambda: browse_button(self.meta_info.img_tgt),
        )
        btn_tgt.grid(row=self.row(), column=2, padx=PAD_X, pady=PAD_Y, sticky="EW")
        Hovertip(btn_tgt, TooltipDict["btn_tgt"])

    def init_signatures(self, window):
        list_in_choices = self.meta_info.get_read_choices()
        list_file_choices = self.meta_info.get_supported_file_signatures()
        list_folder_choices = self.meta_info.get_supported_folder_signatures()

        lbl = Label(window, text="Input data:")
        lbl.grid(row=self.row_idx, column=0, padx=PAD_X, pady=PAD_Y, sticky="EW")

        cb_insig_select = Combobox(window, textvariable=self.meta_info.in_signature)
        # Write file signatures
        cb_insig_select["values"] = list_in_choices
        # Prevent typing a value
        cb_insig_select["state"] = "readonly"
        # Place the widget
        cb_insig_select.grid(row=self.row_idx, column=1, padx=PAD_X, pady=PAD_Y, sticky="EW")
        # Assign width
        cb_insig_select["width"] = len(max(list_in_choices, key=len))
        Hovertip(cb_insig_select, TooltipDict["cb_insig_select"])

        Checkbutton(window, text="Use fallback data", variable=self.meta_info.fallback_sig).grid(
            row=self.row(), column=2, padx=PAD_X, pady=PAD_Y, sticky="W"
        )

        lbl = Label(window, text="Output file/folder:")
        lbl.grid(row=self.row_idx, column=0, padx=PAD_X, pady=PAD_Y, sticky="EW")

        cb_filesig_select = Combobox(window, textvariable=self.meta_info.file_signature)
        # Write file signatures
        cb_filesig_select["values"] = list_file_choices
        # Prevent typing a value
        cb_filesig_select["state"] = "readonly"
        # Place the widget
        cb_filesig_select.grid(row=self.row_idx, column=1, padx=PAD_X, pady=PAD_Y, sticky="EW")
        # Assign width
        cb_filesig_select["width"] = len(max(list_file_choices, key=len))
        Hovertip(cb_filesig_select, TooltipDict["cb_filesig_select"])

        cb_foldersig_select = Combobox(window, textvariable=self.meta_info.folder_signature)
        # Write folder signatures
        cb_foldersig_select["values"] = list_folder_choices
        # Prevent typing a value
        cb_foldersig_select["state"] = "readonly"
        # Place the widget
        cb_foldersig_select.grid(row=self.row(), column=2, padx=PAD_X, pady=PAD_Y, sticky="EW")
        # Assign width
        cb_foldersig_select["width"] = len(max(list_folder_choices, key=len))
        Hovertip(cb_foldersig_select, TooltipDict["cb_foldersig_select"])

    def init_event_system(self, window):
        def browse_button_open(dir):
            filename = filedialog.askopenfilename(initialdir=os.path.dirname(dir.get()))
            if filename != "" and not filename.lower().endswith(".json"):
                messagebox.showinfo(message="Please select a json file.", title="Error")
            elif filename != "":
                # TODO check if file is really an event file and not for example an artist file
                self.db.insert_events(filename)
                dir.set(filename)
                update_event_selection()
                update_event_guidata(None)

        def browse_button_save(dir):
            filename = filedialog.asksaveasfilename(initialdir=os.path.dirname(dir.get()))
            if filename != "" and not filename.lower().endswith(".json"):
                messagebox.showinfo(message="Please select a json file.", title="Error")
            elif filename != "":
                self.db.save_events(filename)
                dir.set(filename)

        # Load events from file
        btn_e_loadfile = Button(
            window,
            text="Load events from File",
            command=lambda: browse_button_open(self.meta_info.event_src),
        )
        btn_e_loadfile.grid(row=self.row_idx, column=0, padx=PAD_X, pady=PAD_Y, sticky="EW")
        Hovertip(btn_e_loadfile, TooltipDict["btn_e_loadfile"])

        lbl_e_load = Label(window, textvariable=self.meta_info.event_src)
        lbl_e_load.grid(row=self.row(), column=1, padx=PAD_X, pady=PAD_Y, sticky="EW")

        # Save events to file
        btn_e_savefile = Button(
            window,
            text="Save events to File",
            command=lambda: browse_button_save(self.meta_info.event_tgt),
        )
        btn_e_savefile.grid(row=self.row_idx, column=0, padx=PAD_X, pady=PAD_Y, sticky="EW")
        Hovertip(btn_e_savefile, TooltipDict["btn_e_savefile"])

        lbl_e_save = Label(window, textvariable=self.meta_info.event_tgt)
        lbl_e_save.grid(row=self.row(), column=1, padx=PAD_X, pady=PAD_Y, sticky="EW")

        #########################
        # Eventmodification gui #
        #########################
        def update_event_gui(_):
            str_e_action = self.meta_info.event_action.get()

            frame_e_date_w.grid_remove()
            frame_e_title_w.grid_remove()
            frame_e_title_r.grid_remove()

            lbl_e_repl.grid()
            tmp_row = lbl_e_repl.grid_info()["row"]
            lbl_e_repl.grid_remove()
            str_e_title_w.set("")

            if str_e_action == "Add event":
                frame_e_date_w.grid(row=tmp_row - 1)
                frame_e_title_w.grid(row=tmp_row - 1)
            elif str_e_action == "Add subevent":
                frame_e_date_w.grid(row=tmp_row - 1)
                frame_e_title_w.grid(row=tmp_row - 1)
            elif str_e_action == "Delete (sub)event":
                frame_e_title_r.grid()
            elif str_e_action == "Edit (sub)event":
                frame_e_date_w.grid(row=tmp_row)
                frame_e_title_w.grid(row=tmp_row)
                frame_e_title_r.grid()
                lbl_e_repl.grid()
            update_event_guidata(None)

        def update_event_guidata(_):
            str_e_action = self.meta_info.event_action.get()
            elm_e_data = self.meta_info.event_selection.get().split(" | ")

            if (
                str_e_action != "Add event"
                and str_e_action != "Add subevent"
                and len(elm_e_data) > 1
            ):
                str_e_title_w.set(elm_e_data[0])
                s_date = datetime.datetime.strptime(elm_e_data[1], "%Y-%m-%d %H:%M:%S")
                date_e_start.set_date(s_date)
                sv_e_shour.set(s_date.hour)
                e_date = datetime.datetime.strptime(elm_e_data[2], "%Y-%m-%d %H:%M:%S")
                date_e_end.set_date(e_date)
                sv_e_ehour.set(e_date.hour)
            else:
                str_e_title_w.set("")

        def execute_event_action():
            str_e_action = self.meta_info.event_action.get()
            if str_e_action == "Add event":
                self.db.insert_event_from_date(
                    str_e_title_w.get(),
                    date_e_start.get_date(),
                    int(sv_e_shour.get()),
                    date_e_end.get_date(),
                    int(sv_e_ehour.get()),
                )
            elif str_e_action == "Add subevent":
                self.db.insert_subevent_from_date(
                    str_e_title_w.get(),
                    date_e_start.get_date(),
                    int(sv_e_shour.get()),
                    date_e_end.get_date(),
                    int(sv_e_ehour.get()),
                )
            elif str_e_action == "Delete (sub)event":
                elm_e_data = self.meta_info.event_selection.get().split(" | ")
                self.db.delete_event(elm_e_data[0], elm_e_data[1], elm_e_data[2])
            elif str_e_action == "Edit (sub)event":
                elm_e_data = self.meta_info.event_selection.get().split(" | ")
                self.db.update_event(
                    elm_e_data[0],
                    elm_e_data[1],
                    elm_e_data[2],
                    str_e_title_w.get(),
                    date_e_start.get_date(),
                    int(sv_e_shour.get()),
                    date_e_end.get_date(),
                    int(sv_e_ehour.get()),
                )
            update_event_selection()

        def update_event_selection():
            list_e_titles = [
                str(x[0]) + " | " + str(x[1]) + " | " + str(x[2])
                for x in self.db.get_all_from_table("events")
            ]
            if len(list_e_titles) == 0:
                list_e_titles = [" |  | "]
            # Write event values from database
            cb_e_select["values"] = list_e_titles
            self.meta_info.event_selection.set(list_e_titles[0])
            update_event_guidata(None)

        ##################
        # Action choices #
        ##################
        # https://www.pythontutorial.net/tkinter/tkinter-combobox/
        list_e_actions = [
            "Add event",
            "Add subevent",
            "Delete (sub)event",
            "Edit (sub)event",
        ]
        self.meta_info.event_action.set(list_e_actions[0])
        cb_e_actions = Combobox(window, textvariable=self.meta_info.event_action)
        # Write event values from database
        cb_e_actions["values"] = list_e_actions
        # Prevent typing a value
        cb_e_actions["state"] = "readonly"
        # Place the widget
        cb_e_actions.grid(row=self.row_idx, column=0, padx=PAD_X, pady=PAD_Y, sticky="EW")
        # Bind callback
        cb_e_actions.bind("<<ComboboxSelected>>", update_event_gui)
        Hovertip(cb_e_actions, TooltipDict["cb_e_actions"])

        #######################
        # Event Title & Dates #
        #######################
        #########
        # Date Frame (write)
        #########
        # https://stackoverflow.com/questions/4443786/how-do-i-create-a-date-picker-in-tkinter
        frame_e_date_w = Frame(window)
        frame_e_date_w.grid(row=self.row_idx, column=1, padx=PAD_X, pady=PAD_Y, sticky="EW")

        lbl_e_sdate = Label(frame_e_date_w, text="Start: ")
        lbl_e_sdate.pack(side="left")
        date_e_start = DateEntry(
            frame_e_date_w, width=12, background="darkblue", foreground="white", borderwidth=2
        )
        date_e_start.pack(side="left")
        Hovertip(date_e_start, TooltipDict["date_e_start"])
        # Hour selector
        sv_e_shour = StringVar()
        sv_e_shour.set("0")
        sv_e_ehour = StringVar()
        sv_e_ehour.set("24")
        vcmd = window.register(lambda P: str.isdigit(P) and int(P) > -1 and int(P) < 25)

        Label(frame_e_date_w, text=":").pack(side="left")
        Entry(
            frame_e_date_w,
            textvariable=sv_e_shour,
            width=3,
            justify="right",
            validate="all",
            validatecommand=(vcmd, "%P"),
        ).pack(side="left")
        Label(frame_e_date_w, text="h").pack(side="left")

        Label(frame_e_date_w, text="h").pack(side="right")
        Entry(
            frame_e_date_w,
            textvariable=sv_e_ehour,
            width=3,
            justify="right",
            validate="all",
            validatecommand=(vcmd, "%P"),
        ).pack(side="right")
        Label(frame_e_date_w, text=":").pack(side="right")

        date_e_end = DateEntry(
            frame_e_date_w, width=12, background="darkblue", foreground="white", borderwidth=2
        )
        date_e_end.pack(side="right")
        Hovertip(date_e_end, TooltipDict["date_e_end"])
        lbl_e_edate = Label(frame_e_date_w, text="End: ")
        lbl_e_edate.pack(side="right")

        #########
        # Title Frame (write)
        #########
        frame_e_title_w = Frame(window)
        frame_e_title_w.grid(row=self.row_idx, column=2, padx=PAD_X, pady=PAD_Y, sticky="EW")

        # Event title input field
        str_e_title_w = StringVar()
        str_e_title_w.set("")
        lbl_e_title = Label(frame_e_title_w, text="Title: ")
        lbl_e_title.pack(side="left")
        Entry(frame_e_title_w, textvariable=str_e_title_w).pack(side="left", fill="x", expand=True)

        #########
        # Title Frame (read)
        # Combobox to select events #
        #########
        frame_e_title_r = Frame(window)
        frame_e_title_r.grid(
            row=self.row(), column=1, columnspan=2, padx=PAD_X, pady=PAD_Y, sticky="EW"
        )
        list_e_titles = [
            str(x[0]) + " | " + str(x[1]) + " | " + str(x[2])
            for x in self.db.get_all_from_table("events")
        ]
        if len(list_e_titles) == 0:
            list_e_titles = [""]
        self.meta_info.event_selection.set(list_e_titles[0])

        cb_e_select = Combobox(frame_e_title_r, textvariable=self.meta_info.event_selection)
        # Write event values from database
        cb_e_select["values"] = list_e_titles
        # Prevent typing a value
        cb_e_select["state"] = "readonly"
        # Place the widget
        cb_e_select.pack(side="left", fill="x", expand=True)
        # Assign width
        cb_e_select["width"] = len(max(list_e_titles, key=len))
        # Bind callback
        cb_e_select.bind("<<ComboboxSelected>>", update_event_guidata)
        Hovertip(cb_e_select, TooltipDict["cb_e_select"])

        # Replacement label
        lbl_e_repl = Label(window, text="Replacement: ")
        lbl_e_repl.grid(row=self.row(), column=0, padx=PAD_X, pady=PAD_Y, sticky="EW")

        #####################################
        # Remove unneeded for initial state #
        #####################################
        frame_e_title_r.grid_remove()
        lbl_e_repl.grid_remove()

        ###################
        # General buttons #
        ###################
        btn_e_execute = Button(window, text="Execute", command=lambda: execute_event_action())
        btn_e_execute.grid(row=self.row_idx, column=0, padx=PAD_X, pady=PAD_Y, sticky="EW")
        Hovertip(btn_e_execute, TooltipDict["btn_e_execute"])

        # Print all events to the details window
        btn_e_print = Button(
            window, text="Print event list", command=lambda: self.db.print_events()
        )
        btn_e_print.grid(row=self.row_idx, column=1, padx=PAD_X, pady=PAD_Y, sticky="EW")
        Hovertip(btn_e_print, TooltipDict["btn_e_print"])

        # Remove all events from the database
        btn_e_clear = Button(
            window,
            text="Clear event list",
            command=lambda: {
                self.db.clean_events(),
                update_event_selection(),
                update_event_guidata(None),
            },
        )
        btn_e_clear.grid(row=self.row(), column=2, padx=PAD_X, pady=PAD_Y, sticky="EW")
        Hovertip(btn_e_clear, TooltipDict["btn_e_clear"])

    def init_artist_system(self, window):
        def browse_button_open(dir):
            filename = filedialog.askopenfilename(initialdir=os.path.dirname(dir.get()))
            if filename != "" and not filename.lower().endswith(".json"):
                messagebox.showinfo(message="Please select a json file.", title="Error")
            elif filename != "":
                # TODO check if file is really a artist file and not for example an event file
                self.db.insert_artists(filename)
                dir.set(filename)
                update_artist_selection()
                update_artist_guidata(None)

        def browse_button_save(dir):
            filename = filedialog.asksaveasfilename(initialdir=os.path.dirname(dir.get()))
            if filename != "" and not filename.lower().endswith(".json"):
                messagebox.showinfo(message="Please select a json file.", title="Error")
            elif filename != "":
                self.db.save_artists(filename)
                dir.set(filename)

        # Load artists from file
        btn_a_loadfile = Button(
            window,
            text="Load artists from File",
            command=lambda: browse_button_open(self.meta_info.artist_src),
        )
        btn_a_loadfile.grid(row=self.row_idx, column=0, padx=PAD_X, pady=PAD_Y, sticky="EW")
        Hovertip(btn_a_loadfile, TooltipDict["btn_a_loadfile"])

        lbl_a_load = Label(window, textvariable=self.meta_info.artist_src)
        lbl_a_load.grid(row=self.row(), column=1, padx=PAD_X, pady=PAD_Y, sticky="EW")

        # Save artists to file
        btn_a_savefile = Button(
            window,
            text="Save artists to File",
            command=lambda: browse_button_save(self.meta_info.artist_tgt),
        )
        btn_a_savefile.grid(row=self.row_idx, column=0, padx=PAD_X, pady=PAD_Y, sticky="EW")
        Hovertip(btn_a_savefile, TooltipDict["btn_a_savefile"])

        lbl_save_artistfile = Label(window, textvariable=self.meta_info.artist_tgt)
        lbl_save_artistfile.grid(row=self.row(), column=1, padx=PAD_X, pady=PAD_Y, sticky="EW")

        ##########################
        # Artistmodification gui #
        ##########################
        def update_artist_gui(_):
            str_a_action = self.meta_info.artist_action.get()

            # frame_a_date_w.grid_remove()
            frame_a_name_w.grid_remove()
            frame_a_name_r.grid_remove()
            frame_a_device_w.grid_remove()
            frame_a_device_r.grid_remove()

            lbl_a_repl.grid()
            tmp_row = lbl_a_repl.grid_info()["row"]
            lbl_a_repl.grid_remove()

            if str_a_action == "Add artist":
                # frame_a_date_w.grid(row=tmp_row - 1)
                frame_a_name_w.grid(row=tmp_row - 1)
                frame_a_device_w.grid(row=tmp_row - 1)
            elif str_a_action == "Delete artist":
                frame_a_name_r.grid()
                frame_a_device_r.grid()
            elif str_a_action == "Edit artist":
                # frame_a_date_w.grid(row=tmp_row)
                frame_a_name_r.grid()
                frame_a_name_w.grid(row=tmp_row)
                frame_a_device_r.grid()
                frame_a_device_w.grid(row=tmp_row)
                lbl_a_repl.grid()
            update_artist_guidata(None)

        def update_artist_guidata(_):
            str_a_action = self.meta_info.artist_action.get()
            elm_a_data = self.meta_info.artist_selection.get().split(" | ")

            if str_a_action != "Add artist" and len(elm_a_data) > 1:
                sv_a_name_w.set(elm_a_data[0])
                sv_a_make_w.set(elm_a_data[1])
                lbl_a_make_r.config(text=elm_a_data[1])
                sv_a_model_w.set(elm_a_data[2])
                lbl_a_model_r.config(text=elm_a_data[2])
                # _date = datetime.datetime.strptime(artist[1], "%Y-%m-%d %H:%M:%S")
                # a_start_entry.set_date(s_date)
                # e_date = datetime.datetime.strptime(artist[2], "%Y-%m-%d %H:%M:%S")
                # a_end_entry.set_date(e_date)
            else:
                sv_a_name_w.set("")
                sv_a_make_w.set("")
                lbl_a_make_r.config(text="")
                sv_a_model_w.set("")
                lbl_a_model_r.config(text="")

        def execute_artist_action():
            str_a_action = self.meta_info.artist_action.get()
            if str_a_action == "Add artist":
                self.db.insert_artist(
                    sv_a_name_w.get(),
                    sv_a_make_w.get(),
                    sv_a_model_w.get(),
                    # a_start_entry.get_date(),
                    # int(a_start_hour.get()),
                    # a_end_entry.get_date(),
                    # int(a_end_hour.get()),
                )
            elif str_a_action == "Delete artist":
                elm_a_data = self.meta_info.artist_selection.get().split(" | ")
                self.db.delete_artist(elm_a_data[0], elm_a_data[1], elm_a_data[2])
            elif str_a_action == "Edit artist":
                elm_a_data = self.meta_info.artist_selection.get().split(" | ")
                self.db.update_artist(
                    elm_a_data[0],
                    elm_a_data[1],
                    elm_a_data[2],
                    sv_a_name_w.get(),
                    sv_a_make_w.get(),
                    sv_a_model_w.get(),
                )
            update_artist_selection()

        def update_artist_selection():
            list_a_names = [
                str(x[0]) + " | " + str(x[1]) + " | " + str(x[2])
                for x in self.db.get_all_from_table("artists")
            ]
            if len(list_a_names) == 0:
                list_a_names = [" |  | "]
            # Write artist values from database
            cb_a_select["values"] = list_a_names
            self.meta_info.artist_selection.set(list_a_names[0])
            update_artist_guidata(None)

        ##################
        # Action choices #
        ##################
        # https://www.pythontutorial.net/tkinter/tkinter-combobox/
        list_a_actions = [
            "Add artist",
            "Delete artist",
            "Edit artist",
        ]
        self.meta_info.artist_action.set(list_a_actions[0])
        cb_a_actions = Combobox(window, textvariable=self.meta_info.artist_action)
        # Write artist values from database
        cb_a_actions["values"] = list_a_actions
        # Prevent typing a value
        cb_a_actions["state"] = "readonly"
        # Place the widget
        cb_a_actions.grid(row=self.row_idx, column=0, padx=PAD_X, pady=PAD_Y, sticky="EW")
        # Bind callback
        cb_a_actions.bind("<<ComboboxSelected>>", update_artist_gui)
        Hovertip(cb_a_actions, TooltipDict["cb_a_actions"])

        #############################
        # Artist Name, Make & Model #
        #############################
        #########
        # Name Frame (write)
        #########
        frame_a_name_w = Frame(window)
        frame_a_name_w.grid(row=self.row_idx, column=2, padx=PAD_X, pady=PAD_Y, sticky="EW")

        # Artist name input field
        sv_a_name_w = StringVar()
        sv_a_name_w.set("")
        lbl_a_name = Label(frame_a_name_w, text="Name: ")
        lbl_a_name.pack(side="left")
        Entry(frame_a_name_w, textvariable=sv_a_name_w).pack(side="left", fill="x", expand=True)

        #########
        # Name Frame (read)
        # Combobox to select artists
        #########
        frame_a_name_r = Frame(window)
        frame_a_name_r.grid(row=self.row_idx, column=2, padx=PAD_X, pady=PAD_Y, sticky="EW")
        list_a_names = [
            str(x[0]) + " | " + str(x[1]) + " | " + str(x[2])
            for x in self.db.get_all_from_table("artists")
        ]
        if len(list_a_names) == 0:
            list_a_names = [" |  | "]
        self.meta_info.artist_selection.set(list_a_names[0])

        cb_a_select = Combobox(frame_a_name_r, textvariable=self.meta_info.artist_selection)
        # Write artist values from database
        cb_a_select["values"] = list_a_names
        # Prevent typing a value
        cb_a_select["state"] = "readonly"
        # Place the widget
        cb_a_select.pack(side="left", fill="x", expand=True)
        # Assign width
        cb_a_select["width"] = len(max(list_a_names, key=len))
        # Bind callback
        cb_a_select.bind("<<ComboboxSelected>>", update_artist_guidata)
        Hovertip(cb_a_select, TooltipDict["cb_a_select"])

        #########
        # Device Frame (write)
        #########
        frame_a_device_w = Frame(window)
        frame_a_device_w.grid(row=self.row_idx, column=1, padx=PAD_X, pady=PAD_Y, sticky="EW")

        # Artist make input field
        sv_a_make_w = StringVar()
        sv_a_make_w.set("")
        lbl_a_make = Label(frame_a_device_w, text="Make: ")
        lbl_a_make.pack(side="left")
        Entry(frame_a_device_w, textvariable=sv_a_make_w).pack(side="left", fill="x", expand=1)

        # Artist model input field
        sv_a_model_w = StringVar()
        sv_a_model_w.set("")
        lbl_a_model = Label(frame_a_device_w, text="Model: ")
        lbl_a_model.pack(side="left")
        Entry(frame_a_device_w, textvariable=sv_a_model_w).pack(side="left", fill="x", expand=1)

        #########
        # Device Frame (read)
        #########
        frame_a_device_r = Frame(window)
        # TODO check wether to use border somewhere
        # frame_a_device_r["borderwidth"] = 5
        # frame_a_device_r["relief"] = "solid"
        frame_a_device_r.grid(row=self.row_idx, column=1, padx=PAD_X, pady=PAD_Y, sticky="ew")

        # Artist make input field
        lbl_a_make = Label(frame_a_device_r, text="Make: ")
        lbl_a_make.pack(side="left")
        lbl_a_make_r = Label(frame_a_device_r, text="", anchor="w")
        lbl_a_make_r.pack(side="left", fill="x", expand=1)

        # Artist model input field
        lbl_a_model = Label(frame_a_device_r, text="Model: ")
        lbl_a_model.pack(side="left")
        lbl_a_model_r = Label(frame_a_device_r, text="", anchor="w")
        lbl_a_model_r.pack(side="left", fill="x", expand=1)

        # Advance Row by one
        self.row()

        # Replacement label
        lbl_a_repl = Label(window, text="Replacement: ")
        lbl_a_repl.grid(row=self.row(), column=0, padx=PAD_X, pady=PAD_Y, sticky="EW")

        #########
        # Date Frame (write)
        #########
        # https://stackoverflow.com/questions/4443786/how-do-i-create-a-date-picker-in-tkinter
        # frame_a_date_w = Frame(window)
        # frame_a_date_w.grid(row=self.row_idx, column=1, padx=PAD_X, pady=PAD_Y, sticky="EW")

        # lbl_a_date = Label(frame_a_date_w, text="Start: ")
        # lbl_a_date.pack(side="left")
        # a_start_entry = DateEntry(
        #     frame_a_date_w, width=12, background="darkblue", foreground="white", borderwidth=2
        # )
        # a_start_entry.pack(side="left")
        # # Hour selector
        # a_start_hour = StringVar()
        # a_start_hour.set("0")
        # a_end_hour = StringVar()
        # a_end_hour.set("24")
        # vcmd = window.register(lambda P: str.isdigit(P) and int(P) > -1 and int(P) < 25)

        # Label(frame_a_date_w, text=":").pack(side="left")
        # Entry(
        #     frame_a_date_w,
        #     textvariable=a_start_hour,
        #     width=3,
        #     justify="right",
        #     validate="all",
        #     validatecommand=(vcmd, "%P"),
        # ).pack(side="left")
        # Label(frame_a_date_w, text="h").pack(side="left")

        # Label(frame_a_date_w, text="h").pack(side="right")
        # Entry(
        #     frame_a_date_w,
        #     textvariable=a_end_hour,
        #     width=3,
        #     justify="right",
        #     validate="all",
        #     validatecommand=(vcmd, "%P"),
        # ).pack(side="right")
        # Label(frame_a_date_w, text=":").pack(side="right")
        # a_end_entry = DateEntry(
        #     frame_a_date_w, width=12, background="darkblue", foreground="white", borderwidth=2
        # )
        # a_end_entry.pack(side="right")
        # lbl_date = Label(frame_a_date_w, text="End: ")
        # lbl_date.pack(side="right")

        # Advance Row by one
        # TODO remove
        self.row()

        #####################################
        # Remove unneeded for initial state #
        #####################################
        # frame_a_name_w.grid_remove()
        frame_a_name_r.grid_remove()
        # frame_a_device_w.grid_remove()
        frame_a_device_r.grid_remove()
        lbl_a_repl.grid_remove()

        ###################
        # General buttons #
        ###################
        btn_a_execute = Button(window, text="Execute", command=lambda: execute_artist_action())
        btn_a_execute.grid(row=self.row_idx, column=0, padx=PAD_X, pady=PAD_Y, sticky="EW")
        Hovertip(btn_a_execute, TooltipDict["btn_a_execute"])

        # Print all artists to the details window
        btn_a_print = Button(
            window, text="Print artist list", command=lambda: self.db.print_artists()
        )
        btn_a_print.grid(row=self.row_idx, column=1, padx=PAD_X, pady=PAD_Y, sticky="EW")
        Hovertip(btn_a_print, TooltipDict["btn_a_print"])

        # Remove all artists from the database
        btn_a_clear = Button(
            window,
            text="Clear artist list",
            command=lambda: {
                self.db.clean_artists(),
                update_artist_selection(),
                update_artist_guidata(None),
            },
        )
        btn_a_clear.grid(row=self.row(), column=2, padx=PAD_X, pady=PAD_Y, sticky="EW")
        Hovertip(btn_a_clear, TooltipDict["btn_a_clear"])

    def init_checkboxes(self, window):
        #########
        # Time shift combobox
        #########
        frame_tshift_sel = Frame(window)
        frame_tshift_sel.grid(row=self.row_idx, column=0, padx=PAD_X, pady=PAD_Y, sticky="EW")
        lbl_tshift_sel = Label(frame_tshift_sel, text="Time Shift: ")
        lbl_tshift_sel.pack(side="left", fill="x", expand=1)
        list_shift_actions = ["Forward", "None", "Backward"]
        self.meta_info.shift_selection.set(list_shift_actions[1])

        cb_shift_select = Combobox(frame_tshift_sel, textvariable=self.meta_info.shift_selection)
        # Write event values from database
        cb_shift_select["values"] = list_shift_actions
        # Prevent typing a value
        cb_shift_select["state"] = "readonly"
        # Place the widget
        cb_shift_select.pack(side="left", fill="x", expand=1)
        Hovertip(cb_shift_select, TooltipDict["cb_shift_select"])

        #########
        # Time shift values
        #########
        vcmd = window.register(lambda P: str.isdigit(P) or P == "")
        frame_tshift_vals = Frame(window)
        frame_tshift_vals.grid(row=self.row(), column=1, padx=PAD_X, pady=PAD_Y, sticky="EW")

        lbl_tshift_d = Label(frame_tshift_vals, text="Days: ")
        lbl_tshift_d.pack(side="left", fill="x", expand=1)
        Entry(
            frame_tshift_vals,
            textvariable=self.meta_info.shift_days,
            width=3,
            justify="right",
            validate="all",
            validatecommand=(vcmd, "%P"),
        ).pack(side="left", fill="x", expand=1)

        lbl_tshift_h = Label(frame_tshift_vals, text="Hours: ")
        lbl_tshift_h.pack(side="left", fill="x", expand=1)
        Entry(
            frame_tshift_vals,
            textvariable=self.meta_info.shift_hours,
            width=3,
            justify="right",
            validate="all",
            validatecommand=(vcmd, "%P"),
        ).pack(side="left", fill="x", expand=1)

        lbl_tshift_m = Label(frame_tshift_vals, text="Minutes: ")
        lbl_tshift_m.pack(side="left", fill="x", expand=1)
        Entry(
            frame_tshift_vals,
            textvariable=self.meta_info.shift_minutes,
            width=3,
            justify="right",
            validate="all",
            validatecommand=(vcmd, "%P"),
        ).pack(side="left", fill="x", expand=1)

        lbl_tshift_s = Label(frame_tshift_vals, text="Seconds: ")
        lbl_tshift_s.pack(side="left", fill="x", expand=1)
        Entry(
            frame_tshift_vals,
            textvariable=self.meta_info.shift_seconds,
            width=3,
            justify="right",
            validate="all",
            validatecommand=(vcmd, "%P"),
        ).pack(side="left", fill="x", expand=1)

        ###################
        # General buttons #
        ###################
        Checkbutton(window, text="Modify metadata", variable=self.meta_info.modify_meta).grid(
            row=self.row_idx, column=0, padx=PAD_X, pady=PAD_Y, sticky="W"
        )

        Checkbutton(window, text="Process raw files", variable=self.meta_info.process_raw).grid(
            row=self.row(), column=1, padx=PAD_X, pady=PAD_Y, sticky="W"
        )

        Checkbutton(window, text="Copy images", variable=self.meta_info.copy_files).grid(
            row=self.row_idx, column=0, padx=PAD_X, pady=PAD_Y, sticky="W"
        )

        Checkbutton(
            window, text="Copy unmatched files", variable=self.meta_info.copy_unmatched
        ).grid(row=self.row_idx, column=1, padx=PAD_X, pady=PAD_Y, sticky="W")

        Checkbutton(
            window, text="Recursive file/folder processing", variable=self.meta_info.recursive
        ).grid(row=self.row(), column=2, padx=PAD_X, pady=PAD_Y, sticky="W")

    def init_progressindicator(self, window):
        # Update to get the correct width for the progressbar
        window.update()
        w_width = window.winfo_width()
        # Progress bar widget
        self.file_progress = Progressbar(
            window, orient=HORIZONTAL, length=w_width, mode="determinate"
        )
        self.file_progress["value"] = 0
        self.file_progress.update()
        self.file_progress.grid(row=self.row(), columnspan=3, sticky="EW", padx=PAD_X, pady=PAD_Y)

        # Progress label
        self.file_label = Label(window, text="Program is not yet running!")
        self.file_label.grid(row=self.row(), columnspan=3, sticky="E", padx=PAD_X, pady=PAD_Y)

        self.time_label = Label(window, text="")
        self.time_label.grid(row=self.row(), columnspan=3, sticky="E", padx=PAD_X)

    def init_details(self, window):
        # Details Menu
        helper_frame = Frame(window, width=window.winfo_width() - PAD_X * 2, height=100)
        helper_frame.pack_propagate(False)
        helper_frame.grid(row=self.row(), column=0, columnspan=3, padx=PAD_X, pady=PAD_Y)

        self.details_text = Text(helper_frame)
        self.details_scroll = Scrollbar(helper_frame, command=self.details_text.yview)
        self.details_scroll.pack(side=RIGHT, fill="y")
        self.details_text.configure(yscrollcommand=self.details_scroll.set)
        self.details_text.pack(fill="both", expand=True)


###################################################################################################
# Main
###################################################################################################
if __name__ == "__main__":
    window = Tk()
    window.title("image-sorter")
    main_app = MainApp(window)
    window.mainloop()
