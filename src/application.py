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
    Text,
    Tk,
    filedialog,
    messagebox,
)
from tkinter.ttk import Checkbutton, Progressbar, Scrollbar

import config as cfg

# own imports
from sorter import Sorter
from meta_information import MetaInformation

PAD_X = 20
PAD_Y = (10, 0)

THIS_DIR = "C:/Users/" + os.getlogin() + "/Projekte/mc-map-modifier/original"


class MainApp:
    def __init__(self, window):
        self.meta_info = MetaInformation()

        self.init_resource_folder(window)
        self.init_progressindicator(window)

        self.run_button = Button(window, text="Dew it", command=lambda: self.run(window))
        self.run_button.grid(row=7, column=0, padx=PAD_X, pady=10)

    def run(self, window):
        if not self.meta_info.finished:
            messagebox.showinfo(message="Modification is already happening.", title="Error")
            window.after(50, lambda: self.listen_for_result(window))
            return

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

        if self.meta_info.finished:
            self.file_label.config(text=f"Finished all {f_count_max} files.")
            self.time_label.config(text="Done.")
        else:
            #self.meta_info.update_estimated_time()
            #s = int(self.meta_info.timer.estimated_time % 60)
            #m = int(self.meta_info.timer.estimated_time / 60)
            #self.time_label.config(
            #    text=f"Processing Data. Estimated rest time: {m} minutes and {s} seconds."
            #)

            self.file_label.config(text=f"Finished file {f_count} of {f_count_max} files.")
            window.after(50, lambda: self.listen_for_result(window))

    ###############################################################################################
    # Initialisation functions
    ###############################################################################################
    def init_resource_folder(self, window):
        def browse_button(dir, initial):
            filename = filedialog.askdirectory(initialdir=initial)
            dir.set(filename)

        dir_path = os.path.dirname(os.path.realpath(__file__))
        self.meta_info.set_dirs(dir_path)

        source_button = Button(
            window,
            text="Browse for source directory.",
            command=lambda: browse_button(self.meta_info.source_dir, S_DIR),
        )
        source_button.grid(row=0, column=0, pady=PAD_Y)
        lbl1 = Label(window, textvariable=self.meta_info.source_dir)
        lbl1.grid(row=1, column=0, padx=PAD_X, pady=PAD_Y)

        target_button = Button(
            window,
            text="Browse for target directory.",
            command=lambda: browse_button(self.meta_info.target_dir, S_DIR + "_copy"),
        )
        target_button.grid(row=2, column=0, pady=PAD_Y)
        lbl1 = Label(window, textvariable=self.meta_info.target_dir)
        lbl1.grid(row=3, column=0, padx=PAD_X, pady=10)


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
        self.file_progress.grid(row=4, sticky="W", padx=PAD_X, pady=10)

        # Progress label
        self.file_label = Label(window, text="Program is not yet running!")
        self.file_label.grid(row=5, sticky="E", padx=PAD_X)

        self.time_label = Label(window, text="")
        self.time_label.grid(row=6, sticky="E", padx=PAD_X)

###################################################################################################
# Main
###################################################################################################
if __name__ == "__main__":
    window = Tk()
    window.title("image-sorter")
    main_app = MainApp(window)
    window.mainloop()
