import os
import sys
import threading
from idlelib.tooltip import Hovertip
from tkinter import (
    DISABLED,
    END,
    HORIZONTAL,
    NORMAL,
    RIGHT,
    Button,
    Frame,
    Label,
    StringVar,
    Text,
    Tk,
    filedialog,
    messagebox,
)
from tkinter.ttk import Checkbutton, Combobox, Progressbar, Radiobutton, Scrollbar, Separator

# own imports
from database import Database
from guiboxes.basebox import PAD_X, PAD_Y, WINDOW_W
from guiboxes.modifydbbox import ModifyDBBox
from helper import lt_window
from meta_information import MetaInformation
from sorter import Sorter
from tooltips import TooltipDict

# https://stackoverflow.com/questions/404744/
if getattr(sys, "frozen", False):
    # If the application is run as a bundle, the PyInstaller bootloader
    # extends the sys module by a flag frozen=True and sets the app path
    APP_PATH = os.path.dirname(sys.executable)
else:
    APP_PATH = os.path.dirname(os.path.abspath(__file__))

TMAIN_H = 250
TMAIN_W = WINDOW_W - 2 * PAD_X


class MainApp:
    def __init__(self, window: Tk):
        """
        Initialize all GUI elements as well as the metainformation and database object.
        """
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

        btn_run = Button(window, text="Dew it", command=lambda: self.run(window))
        btn_run.grid(row=self.row_idx, column=0, columnspan=3, padx=PAD_X, pady=10)
        Hovertip(btn_run, TooltipDict["btn_run"])

        # Stretch the gui, when the window size is adjusted
        window.grid_columnconfigure(1, weight=2)
        window.grid_columnconfigure(2, weight=1)

        lt_window(window)

    def row(self):
        """Keep track of the row the GUI is in."""
        self.row_idx += 1
        return self.row_idx - 1

    def run(self, window: Tk):
        """Main application loop that starts the sorting thread on keypress."""
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

    def listen_for_result(self, window: Tk):
        """Update the GUI on the number of files processed and how many are still left."""
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
            self.file_label.config(text=f"Finished file {f_count} of {f_count_max} files.")
            # Update the time expected for processing all files
            self.meta_info.update_estimated_time(f_count_max - f_count)
            s = self.meta_info.get_estimated_time_s()
            m = self.meta_info.get_estimated_time_m()
            self.time_label.config(
                text=f"Processing Files. Estimated rest time: {m} minutes and {s} seconds."
            )

            window.after(50, lambda: self.listen_for_result(window))

        # Scroll text to the end
        self.details_text.yview(END)

    ###############################################################################################
    # Initialization functions
    ###############################################################################################
    def init_resource_folder(self, window: Tk):
        """Add GUI elemtens for source and target directory."""

        def browse_button(dir: StringVar):
            filename = filedialog.askdirectory(initialdir=dir.get())
            if filename != "":
                dir.set(filename)

        self.meta_info.set_dirs(APP_PATH, APP_PATH, APP_PATH, APP_PATH)

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

    def init_signatures(self, window: Tk):
        """Add GUI elements for read and write signatures."""
        lst_input_options = self.meta_info.get_read_choices()
        list_file_choices = self.meta_info.get_supported_file_signatures()
        list_folder_choices = self.meta_info.get_supported_folder_signatures()

        lbl = Label(window, text="Input data:")
        lbl.grid(row=self.row_idx, column=0, padx=PAD_X, sticky="EW")

        for pattern in lst_input_options:
            rbtn_input = Radiobutton(
                window, text=pattern, variable=self.meta_info.in_signature, value=pattern
            )
            rbtn_input.grid(row=self.row(), column=1, padx=PAD_X, sticky="W")
            Hovertip(rbtn_input, TooltipDict["rbtn_" + pattern])

        lbl = Label(window, text="Pattern for output-files:")
        lbl.grid(row=self.row_idx, column=0, padx=PAD_X, pady=PAD_Y, sticky="EW")

        cb_filesig_select = Combobox(window, textvariable=self.meta_info.file_signature)
        # Write file signatures
        cb_filesig_select["values"] = list_file_choices
        # Prevent typing a value
        cb_filesig_select["state"] = "readonly"
        # Place the widget
        cb_filesig_select.grid(
            row=self.row(), column=1, columnspan=2, padx=PAD_X, pady=PAD_Y, sticky="EW"
        )
        # Assign width
        cb_filesig_select["width"] = len(max(list_file_choices, key=len))
        Hovertip(cb_filesig_select, TooltipDict["cb_filesig_select"])

        lbl = Label(window, text="Pattern for event folder:")
        lbl.grid(row=self.row_idx, column=0, padx=PAD_X, pady=PAD_Y, sticky="EW")

        cb_foldersig_select = Combobox(window, textvariable=self.meta_info.folder_signature)
        # Write folder signatures
        cb_foldersig_select["values"] = list_folder_choices
        # Prevent typing a value
        cb_foldersig_select["state"] = "readonly"
        # Place the widget
        cb_foldersig_select.grid(
            row=self.row(), column=1, columnspan=2, padx=PAD_X, pady=PAD_Y, sticky="EW"
        )
        # Assign width
        cb_foldersig_select["width"] = len(max(list_folder_choices, key=len))
        Hovertip(cb_foldersig_select, TooltipDict["cb_foldersig_select"])

    def init_database_system(self, window: Tk):
        """Add GUI button to open the database menu."""

        def create_modifydb_box():
            ModifyDBBox(
                "Modify Database",
                self.db,
                self.meta_info,
            )

        # Load events from file
        btn_mod_db = Button(
            window,
            text="Modify Database",
            command=lambda: create_modifydb_box(),
        )
        btn_mod_db.grid(
            row=self.row(), column=0, columnspan=3, padx=PAD_X, pady=PAD_Y, sticky="EW"
        )
        Hovertip(btn_mod_db, TooltipDict["btn_mod_db"])

    def init_checkboxes(self, window: Tk):
        """Add GUI checkboxes for additional settings, like require artist or similar."""
        cb_recursive = Checkbutton(
            window, text="Process folder recursively", variable=self.meta_info.recursive
        )
        cb_recursive.grid(row=self.row_idx, column=0, padx=PAD_X, pady=PAD_Y, sticky="W")
        Hovertip(cb_recursive, TooltipDict["cb_recursive"])

        cb_unmatched = Checkbutton(
            window, text="Process unmatched files", variable=self.meta_info.process_unmatched
        )
        cb_unmatched.grid(row=self.row_idx, column=1, padx=PAD_X, pady=PAD_Y, sticky="W")
        Hovertip(cb_unmatched, TooltipDict["cb_unmatched"])

        # Add a checkbof for processing files with the same name
        # This checkbox is disabled when "Foldername_Number" is active
        cb_samename = Checkbutton(
            window, text="Process same name files", variable=self.meta_info.process_samename
        )
        cb_samename.grid(row=self.row(), column=2, padx=PAD_X, pady=PAD_Y, sticky="W")
        Hovertip(cb_samename, TooltipDict["cb_samename"])

        def on_change(index, value, op):
            if self.meta_info.file_signature.get() == "Foldername_Number":
                cb_samename.config(state=DISABLED)
                self.meta_info.process_samename.set(0)
            else:
                cb_samename.config(state=NORMAL)

        self.meta_info.file_signature.trace("w", on_change)

        cb_reqartist = Checkbutton(
            window, text="Require artist", variable=self.meta_info.require_artist
        )
        cb_reqartist.grid(row=self.row_idx, column=0, padx=PAD_X, pady=PAD_Y, sticky="W")
        Hovertip(cb_reqartist, TooltipDict["cb_reqartist"])

        cb_modmeta = Checkbutton(
            window, text="Modify metadata", variable=self.meta_info.modify_meta
        )
        cb_modmeta.grid(row=self.row_idx, column=1, padx=PAD_X, pady=PAD_Y, sticky="W")
        Hovertip(cb_modmeta, TooltipDict["cb_modmeta"])

        cb_overmeta = Checkbutton(
            window, text="Overwrite metadata", variable=self.meta_info.overwrite_meta
        )
        cb_overmeta.grid(row=self.row(), column=2, padx=PAD_X, pady=PAD_Y, sticky="W")
        Hovertip(cb_overmeta, TooltipDict["cb_overmeta"])

        rbtn_copy = Radiobutton(
            window, text="Copy files", variable=self.meta_info.copy_files, value=1
        )
        rbtn_copy.grid(row=self.row_idx, column=0, padx=PAD_X, pady=PAD_Y, sticky="W")
        Hovertip(rbtn_copy, TooltipDict["rbtn_copyfile"])

        rbtn_move = Radiobutton(
            window, text="Move files", variable=self.meta_info.copy_files, value=0
        )
        rbtn_move.grid(row=self.row(), column=1, padx=PAD_X, pady=PAD_Y, sticky="W")
        Hovertip(rbtn_move, TooltipDict["rbtn_movefile"])

    def init_progressindicator(self, window: Tk):
        """Add GUI progressbar and corresponding label."""
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

    def init_details(self, window: Tk):
        """Add GUI textbox for detailed information."""
        helper_frame = Frame(window, width=TMAIN_W, height=TMAIN_H)
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
