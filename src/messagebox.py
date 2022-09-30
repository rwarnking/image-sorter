from tkinter import Button, Checkbutton, Label, Toplevel

from helper import center_window

PAD_X = 20
PAD_Y = (10, 0)


# Source: https://stackoverflow.com/questions/29619418/
class MessageBox(object):
    def __init__(self, title, message, meta_info):

        # Return value
        self.choice = False

        # Creating Dialogue for messagebox
        self.root = Toplevel()
        self.root.title(title)

        # Creating Label For message
        Label(
            self.root,
            text=message,
        ).grid(row=0, column=0, columnspan=2, padx=PAD_X, pady=PAD_Y, sticky="w")

        Checkbutton(self.root, text="Do not ask again", variable=meta_info.dont_ask_again).grid(
            row=1, column=0, columnspan=2, padx=PAD_X, pady=PAD_Y, sticky="w"
        )

        # Creating Yes button
        Button(
            self.root,
            text="Yes",
            command=self.clickYes,
        ).grid(row=2, column=0, padx=PAD_X, pady=(10, 15), sticky="ew")

        # Creating No button
        Button(
            self.root,
            text="No",
            command=self.clickNo,
        ).grid(row=2, column=1, padx=PAD_X, pady=(10, 15), sticky="ew")

        center_window(self.root)

        # Making MessageBox Visible
        self.root.wait_window()

    # Function on Closeing MessageBox
    def closed(self):
        self.root.destroy()
        self.choice = False

    # Function on pressing Yes
    def clickYes(self):
        self.root.destroy()
        self.choice = True

    # Function on pressing No
    def clickNo(self):
        self.root.destroy()
        self.choice = False
