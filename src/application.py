import os
import threading
from tkinter import (
    END,
    HORIZONTAL,
    RIGHT,
    Button,
    Entry,
    Frame,
    Label,
    OptionMenu,
    StringVar,
    Text,
    Tk,
    filedialog,
    messagebox,
)
from tkinter.ttk import Checkbutton, Progressbar, Scrollbar, Separator

# own imports
from database import Database
from helper import lt_window
from meta_information import MetaInformation
from sorter import Sorter
from tkcalendar import DateEntry

PAD_X = 20
PAD_Y = (10, 0)

DIR_PATH = os.path.dirname(os.path.realpath(__file__))
SRC_PATH = os.path.dirname(os.path.realpath(__file__))
TGT_PATH = os.path.dirname(os.path.realpath(__file__))


class MainApp:
    def __init__(self, window):
        self.meta_info = MetaInformation()

        self.row_idx = 0

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

        self.db = Database(self.details_text)

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
    # Initialisation functions
    ###############################################################################################
    def init_resource_folder(self, window):
        def browse_button(dir, initial):
            filename = filedialog.askdirectory(initialdir=initial)
            if filename != "":
                dir.set(filename)

        self.meta_info.set_dirs(SRC_PATH, TGT_PATH)

        # Source directory
        lbl1 = Label(window, text="Source directory:")
        lbl1.grid(row=self.row_idx, column=0, padx=PAD_X, pady=PAD_Y, sticky="EW")
        lbl_src_dir = Label(window, textvariable=self.meta_info.source_dir)
        lbl_src_dir.grid(
            row=self.row_idx, column=1, columnspan=1, padx=PAD_X, pady=PAD_Y, sticky="EW"
        )
        source_button = Button(
            window,
            text="Browse",
            command=lambda: browse_button(self.meta_info.source_dir, SRC_PATH),
        )
        source_button.grid(row=self.row(), column=2, padx=PAD_X, pady=PAD_Y, sticky="EW")

        # Target directory
        lbl2 = Label(window, text="Target directory:")
        lbl2.grid(row=self.row_idx, column=0, padx=PAD_X, pady=PAD_Y, sticky="EW")
        lbl_tgt_dir = Label(window, textvariable=self.meta_info.target_dir)
        lbl_tgt_dir.grid(row=self.row_idx, column=1, padx=PAD_X, pady=PAD_Y, sticky="EW")
        target_button = Button(
            window,
            text="Browse",
            command=lambda: browse_button(self.meta_info.target_dir, TGT_PATH),
        )
        target_button.grid(row=self.row(), column=2, padx=PAD_X, pady=PAD_Y, sticky="EW")

    def init_signatures(self, window):
        in_choices = self.meta_info.get_read_choices()
        file_choices = self.meta_info.get_supported_file_signatures()
        folder_choices = self.meta_info.get_supported_folder_signatures()

        lbl = Label(window, text="Input data:")
        lbl.grid(row=self.row_idx, column=0, padx=PAD_X, pady=PAD_Y, sticky="EW")
        in_options = OptionMenu(window, self.meta_info.in_signature, *in_choices)
        in_options.grid(row=self.row_idx, column=1, padx=PAD_X, pady=PAD_Y, sticky="EW")

        Checkbutton(window, text="Use fallback data", variable=self.meta_info.fallback_sig).grid(
            row=self.row(), column=2, padx=PAD_X, pady=PAD_Y, sticky="W"
        )

        lbl = Label(window, text="Output file/folder:")
        lbl.grid(row=self.row_idx, column=0, padx=PAD_X, pady=PAD_Y, sticky="EW")
        file_options = OptionMenu(window, self.meta_info.file_signature, *file_choices)
        file_options.grid(row=self.row_idx, column=1, padx=PAD_X, pady=PAD_Y, sticky="EW")

        folder_options = OptionMenu(window, self.meta_info.folder_signature, *folder_choices)
        folder_options.grid(row=self.row(), column=2, padx=PAD_X, pady=PAD_Y, sticky="EW")

    def init_event_system(self, window):
        def browse_button(dir, initial):
            filename = filedialog.askopenfilename(initialdir=initial)
            if filename != "":
                dir.set(filename)

        # Load events from file
        # TODO why src?
        ld_event_file = StringVar()
        ld_event_file.set("src/events.json")
        load_eventfile_button = Button(
            window,
            text="Load events from File",
            command=lambda: self.db.insert_events(ld_event_file.get()),
        )
        load_eventfile_button.grid(row=self.row_idx, column=0, padx=PAD_X, pady=PAD_Y, sticky="EW")

        lbl_load_eventfile = Label(window, textvariable=ld_event_file)
        lbl_load_eventfile.grid(row=self.row_idx, column=1, padx=PAD_X, pady=PAD_Y, sticky="EW")

        browse_load_file_button = Button(
            window, text="Browse", command=lambda: browse_button(ld_event_file, DIR_PATH)
        )
        browse_load_file_button.grid(row=self.row(), column=2, padx=PAD_X, pady=PAD_Y, sticky="EW")

        # Save events to file
        # TODO why src?
        sv_event_file = StringVar()
        sv_event_file.set("src/events.json")
        save_eventfile_button = Button(
            window,
            text="Save events to File",
            command=lambda: self.db.save_events(sv_event_file.get()),
        )
        save_eventfile_button.grid(row=self.row_idx, column=0, padx=PAD_X, pady=PAD_Y, sticky="EW")

        lbl_save_eventfile = Label(window, textvariable=sv_event_file)
        lbl_save_eventfile.grid(row=self.row_idx, column=1, padx=PAD_X, pady=PAD_Y, sticky="EW")

        browse_save_file_button = Button(
            window, text="Browse", command=lambda: browse_button(sv_event_file, DIR_PATH)
        )
        browse_save_file_button.grid(row=self.row(), column=2, padx=PAD_X, pady=PAD_Y, sticky="EW")

        #################
        # Add one event #
        #################
        # https://stackoverflow.com/questions/4443786/how-do-i-create-a-date-picker-in-tkinter
        date_frame = Frame(window)
        date_frame.grid(row=self.row_idx, column=1, padx=PAD_X, pady=PAD_Y, sticky="EW")

        lbl_date = Label(date_frame, text="Start: ")
        lbl_date.pack(side="left")
        e_start_entry = DateEntry(
            date_frame, width=12, background="darkblue", foreground="white", borderwidth=2
        )
        e_start_entry.pack(side="left")
        # Hour selector
        e_start_hour = StringVar()
        e_start_hour.set("0")
        e_end_hour = StringVar()
        e_end_hour.set("24")
        vcmd = window.register(lambda P: str.isdigit(P) and int(P) > -1 and int(P) < 25)

        Label(date_frame, text=":").pack(side="left")
        Entry(
            date_frame,
            textvariable=e_start_hour,
            width=3,
            justify="right",
            validate="all",
            validatecommand=(vcmd, "%P"),
        ).pack(side="left")
        Label(date_frame, text="h").pack(side="left")

        Label(date_frame, text="h").pack(side="right")
        Entry(
            date_frame,
            textvariable=e_end_hour,
            width=3,
            justify="right",
            validate="all",
            validatecommand=(vcmd, "%P"),
        ).pack(side="right")
        Label(date_frame, text=":").pack(side="right")
        e_end_entry = DateEntry(
            date_frame, width=12, background="darkblue", foreground="white", borderwidth=2
        )
        e_end_entry.pack(side="right")
        lbl_date = Label(date_frame, text="End: ")
        lbl_date.pack(side="right")

        sv_event_title = StringVar()
        sv_event_title.set("")
        date_frame = Frame(window)
        date_frame.grid(row=self.row_idx, column=2, padx=PAD_X, pady=PAD_Y, sticky="EW")
        lbl_date = Label(date_frame, text="Title: ")
        lbl_date.pack(side="left")
        Entry(date_frame, textvariable=sv_event_title).pack(side="right")

        add_event_button = Button(
            window,
            text="Add event",
            command=lambda: self.db.insert_event_from_date(
                sv_event_title.get(),
                e_start_entry.get_date(),
                int(e_start_hour.get()),
                e_end_entry.get_date(),
                int(e_end_hour.get()),
            ),
        )
        add_event_button.grid(row=self.row(), column=0, padx=PAD_X, pady=PAD_Y, sticky="EW")

        ############
        # Subevent #
        ############
        # Hour selector
        se_start_hour = StringVar()
        se_start_hour.set("0")
        se_end_hour = StringVar()
        se_end_hour.set("24")

        date_frame = Frame(window)
        date_frame.grid(row=self.row_idx, column=1, padx=PAD_X, pady=PAD_Y, sticky="EW")

        lbl_date = Label(date_frame, text="Start: ")
        lbl_date.pack(side="left")
        se_start_entry = DateEntry(
            date_frame, width=12, background="darkblue", foreground="white", borderwidth=2
        )
        se_start_entry.pack(side="left")
        Label(date_frame, text=":").pack(side="left")
        Entry(
            date_frame,
            textvariable=se_start_hour,
            width=3,
            justify="right",
            validate="all",
            validatecommand=(vcmd, "%P"),
        ).pack(side="left")
        Label(date_frame, text="h").pack(side="left")

        Label(date_frame, text="h").pack(side="right")
        Entry(
            date_frame,
            textvariable=se_end_hour,
            width=3,
            justify="right",
            validate="all",
            validatecommand=(vcmd, "%P"),
        ).pack(side="right")
        Label(date_frame, text=":").pack(side="right")
        se_end_entry = DateEntry(
            date_frame, width=12, background="darkblue", foreground="white", borderwidth=2
        )
        se_end_entry.pack(side="right")
        lbl_date = Label(date_frame, text="End: ")
        lbl_date.pack(side="right")

        sv_subevent_title = StringVar()
        sv_subevent_title.set("")
        date_frame = Frame(window)
        date_frame.grid(row=self.row_idx, column=2, padx=PAD_X, pady=PAD_Y, sticky="EW")
        lbl_date = Label(date_frame, text="Title: ")
        lbl_date.pack(side="left")
        Entry(date_frame, textvariable=sv_subevent_title).pack(side="right")

        add_subevent_button = Button(
            window,
            text="Add subevent",
            command=lambda: self.db.insert_subevent_from_date(
                sv_subevent_title.get(),
                se_start_entry.get_date(),
                int(se_start_hour.get()),
                se_end_entry.get_date(),
                int(se_end_hour.get()),
            ),
        )
        add_subevent_button.grid(row=self.row(), column=0, padx=PAD_X, pady=PAD_Y, sticky="EW")

        # Remove one event
        rm_event_title = StringVar()
        rm_event_title.set("")
        remove_event_button = Button(
            window, text="Remove event", command=lambda: self.db.delete_event(rm_event_title.get())
        )
        remove_event_button.grid(row=self.row_idx, column=0, padx=PAD_X, pady=PAD_Y, sticky="EW")

        date_frame = Frame(window)
        date_frame.grid(row=self.row(), column=2, padx=PAD_X, pady=PAD_Y, sticky="EW")
        lbl_date = Label(date_frame, text="Title: ")
        lbl_date.pack(side="left")
        Entry(date_frame, textvariable=rm_event_title).pack(side="right")

        # Remove all events
        print_events_button = Button(
            window, text="Print event list", command=lambda: self.db.print_events()
        )
        print_events_button.grid(row=self.row_idx, column=0, padx=PAD_X, pady=PAD_Y, sticky="EW")

        clear_events_button = Button(
            window, text="Clear event list", command=lambda: self.db.clean_events()
        )
        clear_events_button.grid(row=self.row(), column=2, padx=PAD_X, pady=PAD_Y, sticky="EW")

    def init_artist_system(self, window):
        def browse_button(dir, initial):
            filename = filedialog.askopenfilename(initialdir=initial)
            if filename != "":
                dir.set(filename)

        # Load artists from file
        # TODO why src?
        ld_artist_file = StringVar()
        ld_artist_file.set("src/artists.json")
        load_artistfile_button = Button(
            window,
            text="Load artists from File",
            command=lambda: self.db.insert_artists(ld_artist_file.get()),
        )
        load_artistfile_button.grid(
            row=self.row_idx, column=0, padx=PAD_X, pady=PAD_Y, sticky="EW"
        )

        lbl_load_artistfile = Label(window, textvariable=ld_artist_file)
        lbl_load_artistfile.grid(row=self.row_idx, column=1, padx=PAD_X, pady=PAD_Y, sticky="EW")

        browse_load_file_button = Button(
            window, text="Browse", command=lambda: browse_button(ld_artist_file, DIR_PATH)
        )
        browse_load_file_button.grid(row=self.row(), column=2, padx=PAD_X, pady=PAD_Y, sticky="EW")

        # Save artists to file
        # TODO why src?
        sv_artist_file = StringVar()
        sv_artist_file.set("src/artists.json")
        save_artistfile_button = Button(
            window,
            text="Save artists to File",
            command=lambda: self.db.save_artists(sv_artist_file.get()),
        )
        save_artistfile_button.grid(
            row=self.row_idx, column=0, padx=PAD_X, pady=PAD_Y, sticky="EW"
        )

        lbl_save_artistfile = Label(window, textvariable=sv_artist_file)
        lbl_save_artistfile.grid(row=self.row_idx, column=1, padx=PAD_X, pady=PAD_Y, sticky="EW")

        browse_save_file_button = Button(
            window, text="Browse", command=lambda: browse_button(sv_artist_file, DIR_PATH)
        )
        browse_save_file_button.grid(row=self.row(), column=2, padx=PAD_X, pady=PAD_Y, sticky="EW")

        # Add one artist
        # https://stackoverflow.com/questions/4443786/how-do-i-create-a-date-picker-in-tkinter
        device_frame = Frame(window)
        device_frame.grid(row=self.row_idx, column=1, padx=PAD_X, pady=PAD_Y, sticky="EW")

        sv_artist_name = StringVar()
        sv_artist_name.set("")
        sv_artist_make = StringVar()
        sv_artist_make.set("")
        sv_artist_model = StringVar()
        sv_artist_model.set("")

        lbl_date = Label(device_frame, text="Make: ")
        lbl_date.pack(side="left")
        Entry(device_frame, textvariable=sv_artist_make).pack(side="left")

        Entry(device_frame, textvariable=sv_artist_model).pack(side="right")
        lbl_date = Label(device_frame, text="Model: ")
        lbl_date.pack(side="right")

        device_frame = Frame(window)
        device_frame.grid(row=self.row_idx, column=2, padx=PAD_X, pady=PAD_Y, sticky="EW")
        lbl_date = Label(device_frame, text="Name: ")
        lbl_date.pack(side="left")
        Entry(device_frame, textvariable=sv_artist_name).pack(side="right")

        load_artistfile_button = Button(
            window,
            text="Add artist",
            command=lambda: self.db.insert_artist(
                sv_artist_name.get(), sv_artist_make.get(), sv_artist_model.get()
            ),
        )
        load_artistfile_button.grid(row=self.row(), column=0, padx=PAD_X, pady=PAD_Y, sticky="EW")

        # Remove one artist
        rm_artist_name = StringVar()
        rm_artist_name.set("")
        load_artistfile_button = Button(
            window,
            text="Remove artist",
            command=lambda: self.db.delete_artist(rm_artist_name.get()),
        )
        load_artistfile_button.grid(
            row=self.row_idx, column=0, padx=PAD_X, pady=PAD_Y, sticky="EW"
        )

        device_frame = Frame(window)
        device_frame.grid(row=self.row(), column=2, padx=PAD_X, pady=PAD_Y, sticky="EW")
        lbl_date = Label(device_frame, text="Name: ")
        lbl_date.pack(side="left")
        Entry(device_frame, textvariable=rm_artist_name).pack(side="right")

        # Remove all artists
        print_artists_button = Button(
            window, text="Print artist list", command=lambda: self.db.print_artists()
        )
        print_artists_button.grid(row=self.row_idx, column=0, padx=PAD_X, pady=PAD_Y, sticky="EW")

        clear_artists_button = Button(
            window, text="Clear artist list", command=lambda: self.db.clean_artists()
        )
        clear_artists_button.grid(row=self.row(), column=2, padx=PAD_X, pady=PAD_Y, sticky="EW")

    def init_checkboxes(self, window):
        Checkbutton(window, text="Shift timedata", variable=self.meta_info.shift_timedata).grid(
            row=self.row_idx, column=0, padx=PAD_X, pady=PAD_Y, sticky="W"
        )

        vcmd = window.register(lambda P: str.isdigit(P) or P == "")
        time_frame = Frame(window)
        time_frame.grid(row=self.row_idx, column=1, padx=PAD_X, pady=PAD_Y, sticky="EW")

        lbl_time = Label(time_frame, text="Days: ")
        lbl_time.pack(side="left")
        Entry(
            time_frame,
            textvariable=self.meta_info.shift_days,
            width=3,
            justify="right",
            validate="all",
            validatecommand=(vcmd, "%P"),
        ).pack(side="left")

        lbl_time = Label(time_frame, text="Hours: ")
        lbl_time.pack(side="left")
        Entry(
            time_frame,
            textvariable=self.meta_info.shift_hours,
            width=3,
            justify="right",
            validate="all",
            validatecommand=(vcmd, "%P"),
        ).pack(side="left")

        lbl_time = Label(time_frame, text="Minutes: ")
        lbl_time.pack(side="left")
        Entry(
            time_frame,
            textvariable=self.meta_info.shift_minutes,
            width=3,
            justify="right",
            validate="all",
            validatecommand=(vcmd, "%P"),
        ).pack(side="left")

        time_choices = ["Forward", "Backward"]
        self.meta_info.time_option.set(time_choices[0])
        time_options = OptionMenu(window, self.meta_info.time_option, *time_choices)
        time_options.grid(row=self.row(), column=2, padx=PAD_X, pady=PAD_Y, sticky="EW")

        Checkbutton(window, text="Modify metadata", variable=self.meta_info.modify_meta).grid(
            row=self.row(), column=0, padx=PAD_X, pady=PAD_Y, sticky="W"
        )

        Checkbutton(window, text="Copy images", variable=self.meta_info.copy_files).grid(
            row=self.row_idx, column=0, padx=PAD_X, pady=PAD_Y, sticky="W"
        )

        Checkbutton(
            window, text="Recursive file/folder processing", variable=self.meta_info.recursive
        ).grid(row=self.row(), column=1, padx=PAD_X, pady=PAD_Y, sticky="W")

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
        # Create details button
        def details():
            if helper_frame.hidden:
                helper_frame.grid()
                helper_frame.hidden = False
                self.run_button.grid(row=self.row_idx + 1)
            else:
                helper_frame.grid_remove()
                helper_frame.hidden = True
                self.run_button.grid(row=self.row_idx)

        details_button = Button(window, text="Details", command=details)
        details_button.grid(row=self.row(), column=0, sticky="W", padx=PAD_X, pady=PAD_Y)

        # Details Menu
        helper_frame = Frame(window, width=window.winfo_width() - PAD_X * 2, height=100)
        helper_frame.pack_propagate(False)
        self.details_text = Text(helper_frame, width=0, height=0)
        details_scroll = Scrollbar(helper_frame, command=self.details_text.yview)
        details_scroll.pack(side=RIGHT, fill="y")
        self.details_text.configure(yscrollcommand=details_scroll.set)
        self.details_text.pack(fill="both", expand=True)
        helper_frame.grid(row=self.row_idx, column=0, columnspan=3, padx=PAD_X, pady=PAD_Y)
        helper_frame.grid_remove()
        helper_frame.hidden = True


###################################################################################################
# Main
###################################################################################################
if __name__ == "__main__":
    window = Tk()
    window.title("image-sorter")
    main_app = MainApp(window)
    window.mainloop()
