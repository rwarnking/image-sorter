from tkinter import BooleanVar, Button, Checkbutton, Label, Toplevel

from guiboxes.basebox import PAD_X, PAD_Y
from helper import center_window


# Source: https://stackoverflow.com/questions/29619418/
class MessageBox(object):
    def __init__(self, title: str, msg: str, again: BooleanVar, b1: str = "Yes", b2: str = "No"):
        """
        Create a GUI box that allows to select yes, no as buttons as well as
        a Do not ask again option.
        """
        # Return value
        self.choice = False

        # Creating Dialogue for messagebox
        self.root = Toplevel()
        self.root.title(title)
        self.root.minsize(350, 0)

        # Creating Label For message
        Label(
            self.root,
            text=msg,
        ).grid(row=0, column=0, columnspan=2, padx=PAD_X, pady=PAD_Y, sticky="w")

        Checkbutton(self.root, text="Do not ask again", variable=again).grid(
            row=1, column=0, columnspan=2, padx=PAD_X, pady=PAD_Y, sticky="w"
        )

        # Creating Yes button
        Button(self.root, text=b1, command=self.clickYes).grid(
            row=2, column=0, padx=PAD_X, pady=PAD_Y, sticky="ew"
        )

        # Creating No button
        Button(self.root, text=b2, command=self.clickNo).grid(
            row=2, column=1, padx=PAD_X, pady=PAD_Y, sticky="ew"
        )

        center_window(self.root)

        # Making MessageBox Visible
        self.root.wait_window()

    def closed(self):
        """Function for closing the box."""
        self.root.destroy()
        self.choice = False

    def clickYes(self):
        """Function when yes was clicked."""
        self.root.destroy()
        self.choice = True

    def clickNo(self):
        """Function when no was clicked."""
        self.root.destroy()
        self.choice = False
