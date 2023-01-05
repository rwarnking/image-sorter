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
from modifydbbox import ModifyDBBox

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
        self.init_database_system(window)
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

    def init_database_system(self, window):
        def create_modifydb_box(dir):
            box = ModifyDBBox(
                "Modify Database",
                "Inspect, modify, add and delete entries from the database.",
                self.db,
                self.meta_info,
            )

        # Load events from file
        btn_modify_database = Button(
            window,
            text="Modify Database",
            command=lambda: create_modifydb_box(self.meta_info.event_src),
        )
        btn_modify_database.grid(row=self.row(), column=0, columnspan=3, padx=PAD_X, pady=PAD_Y, sticky="EW")

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
