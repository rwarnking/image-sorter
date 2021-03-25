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

import config as cfg

# own imports
from database import Database
from sorter import Sorter
from meta_information import MetaInformation

PAD_X = 20
PAD_Y = (10, 0)

DIR_PATH = os.path.dirname(os.path.realpath(__file__))

WIDTH_COL3 = 10

class MainApp:
    def __init__(self, window):
        self.meta_info = MetaInformation()

        self.row_idx = 0

        self.init_resource_folder(window)
        separator = Separator(window, orient='horizontal')
        separator.grid(row=self.row(), column=0, columnspan=3, padx=PAD_X, pady=PAD_Y, sticky="EW")
        self.init_signatures(window)
        separator = Separator(window, orient='horizontal')
        separator.grid(row=self.row(), column=0, columnspan=3, padx=PAD_X, pady=PAD_Y, sticky="EW")
        self.init_event_system(window)
        separator = Separator(window, orient='horizontal')
        separator.grid(row=self.row(), column=0, columnspan=3, padx=PAD_X, pady=PAD_Y, sticky="EW")
        self.init_checkboxes(window)
        separator = Separator(window, orient='horizontal')
        separator.grid(row=self.row(), column=0, columnspan=3, padx=PAD_X, pady=PAD_Y, sticky="EW")
        self.init_progressindicator(window)
        separator = Separator(window, orient='horizontal')
        separator.grid(row=self.row(), column=0, columnspan=3, padx=PAD_X, pady=PAD_Y, sticky="EW")
        self.init_details(window)

        self.run_button = Button(window, text="Dew it", command=lambda: self.run(window))
        self.run_button.grid(row=self.row_idx, column=0, columnspan=3, padx=PAD_X, pady=10)

    def row(self):
        self.row_idx += 1
        return self.row_idx - 1

    def run(self, window):
        if not self.meta_info.finished:
            messagebox.showinfo(message="Modification is already happening.", title="Error")
            window.after(50, lambda: self.listen_for_result(window))
            return

        db = Database()
        s = Sorter(self.meta_info)
        self.meta_info.finished = False
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
            #self.meta_info.update_estimated_time()
            #s = int(self.meta_info.timer.estimated_time % 60)
            #m = int(self.meta_info.timer.estimated_time / 60)
            #self.time_label.config(
            #    text=f"Processing Data. Estimated rest time: {m} minutes and {s} seconds."
            #)

            self.file_label.config(text=f"Finished file {f_count} of {f_count_max} files.")
            self.time_label.config(text="")
            window.after(50, lambda: self.listen_for_result(window))

    ###############################################################################################
    # Initialisation functions
    ###############################################################################################
    def init_resource_folder(self, window):
        def browse_button(dir, initial):
            filename = filedialog.askdirectory(initialdir=initial)
            dir.set(filename)

        self.meta_info.set_dirs(DIR_PATH)

        # Source directory
        lbl1 = Label(window, text="Source directory:")
        lbl1.grid(row=self.row_idx, column=0, padx=PAD_X, pady=PAD_Y, sticky="EW")
        lbl_src_dir = Label(window, textvariable=self.meta_info.source_dir)
        lbl_src_dir.grid(row=self.row_idx, column=1, columnspan=1, padx=PAD_X, pady=PAD_Y, sticky="EW")
        source_button = Button(
            window, text="Browse",
            command=lambda: browse_button(self.meta_info.source_dir, DIR_PATH),
        )
        source_button.grid(row=self.row(), column=2, padx=PAD_X, pady=PAD_Y, sticky="EW")

        # Target directory
        lbl2 = Label(window, text="Target directory:")
        lbl2.grid(row=self.row_idx, column=0, padx=PAD_X, pady=PAD_Y, sticky="EW")
        lbl_tgt_dir = Label(window, textvariable=self.meta_info.target_dir)
        lbl_tgt_dir.grid(row=self.row_idx, column=1, padx=PAD_X, pady=PAD_Y, sticky="EW")
        target_button = Button(
            window, text="Browse",
            command=lambda: browse_button(self.meta_info.target_dir, DIR_PATH),
        )
        target_button.grid(row=self.row(), column=2, padx=PAD_X, pady=PAD_Y, sticky="EW")

    def init_signatures(self, window):
        in_choices = ["IMG-Meta-Info", "IMG-File-Name"]
        out_choices = self.meta_info.get_supported_signatures()

        self.meta_info.in_signature.set(in_choices[0])
        lbl = Label(window, text="Input signature:")
        lbl.grid(row=self.row_idx, column=0, padx=PAD_X, pady=PAD_Y, sticky="EW")
        in_options = OptionMenu(window, self.meta_info.in_signature, *in_choices)
        in_options.grid(row=self.row_idx, column=1, padx=PAD_X, pady=PAD_Y, sticky="EW")

        Checkbutton(
            window, text="Use fallback signature", variable=self.meta_info.fallback_sig
        ).grid(row=self.row(), column=2, padx=PAD_X, pady=PAD_Y, sticky="W")

        self.meta_info.out_signature.set(out_choices[0])
        lbl = Label(window, text="Output signature:")
        lbl.grid(row=self.row_idx, column=0, padx=PAD_X, pady=PAD_Y, sticky="EW")
        out_options = OptionMenu(window, self.meta_info.out_signature, *out_choices)
        out_options.grid(row=self.row(), column=1, padx=PAD_X, pady=PAD_Y, sticky="EW")

    def init_event_system(self, window):
        def browse_button(dir, initial):
            filename = filedialog.askopenfilename(initialdir=initial)
            dir.set(filename)

        db = Database()

        # Load events from file
        # TODO why src?
        ld_event_file = StringVar()
        ld_event_file.set("src/events.json")
        load_eventfile_button = Button(
            window, text="Load events from File",
            command=lambda: db.insert_events(ld_event_file.get())
        )
        load_eventfile_button.grid(row=self.row_idx, column=0, padx=PAD_X, pady=PAD_Y, sticky="EW")

        lbl_load_eventfile = Label(window, textvariable=ld_event_file)
        lbl_load_eventfile.grid(row=self.row_idx, column=1, padx=PAD_X, pady=PAD_Y, sticky="EW")

        browse_load_file_button = Button(
            window, text="Browse",
            command=lambda: browse_button(ld_event_file, DIR_PATH)
        )
        browse_load_file_button.grid(row=self.row(), column=2, padx=PAD_X, pady=PAD_Y, sticky="EW")

        # Save events to file
        # TODO why src?
        sv_event_file = StringVar()
        sv_event_file.set("src/events.json")
        save_eventfile_button = Button(
            window, text="Save events to File",
            command=lambda: db.save_events(sv_event_file)
        )
        save_eventfile_button.grid(row=self.row_idx, column=0, padx=PAD_X, pady=PAD_Y, sticky="EW")

        lbl_save_eventfile = Label(window, textvariable=sv_event_file)
        lbl_save_eventfile.grid(row=self.row_idx, column=1, padx=PAD_X, pady=PAD_Y, sticky="EW")

        browse_save_file_button = Button(
            window, text="Browse",
            command=lambda: browse_button(sv_event_file, DIR_PATH)
        )
        browse_save_file_button.grid(row=self.row(), column=2, padx=PAD_X, pady=PAD_Y, sticky="EW")

        # Add one event
        # TODO https://stackoverflow.com/questions/4443786/how-do-i-create-a-date-picker-in-tkinter
        sv_event_title = StringVar()
        sv_event_title.set("")
        s_y = s_m = s_d = e_y = e_m = e_d = 1
        load_eventfile_button = Button(
            window, text="Add event",
            command=lambda: db.insert_event(sv_event_title.get(), s_y, s_m, s_d, e_y, e_m, e_d)
        )
        load_eventfile_button.grid(row=self.row_idx, column=0, padx=PAD_X, pady=PAD_Y, sticky="EW")
        Entry(window, textvariable=sv_event_title).grid(
            row=self.row_idx, column=1, padx=PAD_X, pady=PAD_Y, sticky="EW"
        )
        Entry(window, textvariable=sv_event_title).grid(
            row=self.row(), column=2, padx=PAD_X, pady=PAD_Y, sticky="EW"
        )

        # Remove one event
        rm_event_title = StringVar()
        rm_event_title.set("")
        load_eventfile_button = Button(
            window, text="Remove event",
            command=lambda: db.delete_event(rm_event_title.get())
        )
        load_eventfile_button.grid(row=self.row_idx, column=0, padx=PAD_X, pady=PAD_Y, sticky="EW")
        Entry(window, textvariable=rm_event_title).grid(
            row=self.row(), column=1, padx=PAD_X, pady=PAD_Y, sticky="EW"
        )

        # Remove all events
        print_events_button = Button(
            window, text="Print event list",
            command=lambda: db.print_events()
        )
        print_events_button.grid(row=self.row_idx, column=0, padx=PAD_X, pady=PAD_Y, sticky="EW")

        clear_events_button = Button(
            window, text="Clear event list", command=lambda: db.clean()
        )
        clear_events_button.grid(row=self.row(), column=2, padx=PAD_X, pady=PAD_Y, sticky="EW")

    def init_checkboxes(self, window):
        Checkbutton(
            window, text="Modify metadata", variable=self.meta_info.modify_meta
        ).grid(row=self.row_idx, column=0, padx=PAD_X, pady=PAD_Y, sticky="W")

        Checkbutton(
            window, text="Recursive file/folder processing", variable=self.meta_info.recursive
        ).grid(row=self.row_idx, column=1, padx=PAD_X, pady=PAD_Y, sticky="W")

        Checkbutton(
            window, text="Copy images", variable=self.meta_info.copy_files
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
