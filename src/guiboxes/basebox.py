from tkinter import Toplevel

from debug_messages import InfoCodes

PAD_X = 5
PAD_Y = (5, 5)
PAD_Y_LBL = (5, 0)
PAD_Y_ADD = (0, 0)
# Window dimensions
WINDOW_W = 650
# Line height
LINE_H = 30
# Button width
BTN_W = 5


class BaseBox(object):
    """
    Baseclass for GUI boxes.
    Source: https://stackoverflow.com/questions/29619418/
    """

    def __init__(self, header: str):
        """Initialize most common variables."""
        # Creating Dialogue for messagebox
        self.root = Toplevel()
        self.root.title(header)

        # Row index for GUI formatting
        self.row_idx = 0
        # Save if a object was changed
        self.changed = False
        # Save if the add or update was successfull
        self.info = InfoCodes.NO_INFO

        # Stretch the gui, when the window size is adjusted
        # w=2 for column 1 is needed for the modifydb box
        self.root.grid_columnconfigure(1, weight=2)
        self.root.grid_columnconfigure(2, weight=1)
        self.root.grid_columnconfigure(3, weight=1)

    def row(self):
        """Increase the row idx and return the previous value."""
        self.row_idx += 1
        return self.row_idx - 1

    def close(self):
        """Function for closing the box."""
        self.root.destroy()
