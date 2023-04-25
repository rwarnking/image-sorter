from tkinter import Button, Label, Toplevel, Radiobutton, StringVar

from helper import center_window

from guiboxes.basebox import PAD_X, PAD_Y


# Source: https://stackoverflow.com/questions/29619418/
class SelectionBox(object):
    def __init__(self, title, actioncall, message, options):

        # Return value
        self.choice = StringVar()
        self.choice.set(options[0])

        # Creating Dialogue for messagebox
        self.root = Toplevel()
        self.root.title(title)

        # Creating Label For message
        Label(
            self.root,
            text=message,
        ).grid(row=0, column=0, columnspan=3, padx=PAD_X, pady=PAD_Y, sticky="w")

        Label(
            self.root,
            text=actioncall,
        ).grid(row=1, column=0, padx=PAD_X, sticky="w")

        row_idx = 1
        col = 0
        for opt in options:
            Radiobutton(
                self.root, text=opt, variable=self.choice, value=opt
            ).grid(
                row=row_idx, column=1+col, padx=PAD_X, sticky="W"
            )
            col += 1
            if col % 2 == 0:
                col -= 2
                row_idx+=1

        # Creating Yes button
        Button(
            self.root,
            text="Confirm",
            command=self.closed,
        ).grid(row=row_idx, column=1, padx=PAD_X, pady=(10, 15), sticky="ew")

        center_window(self.root)

        # Making MessageBox Visible
        self.root.wait_window()

    # Function on Closeing MessageBox
    def closed(self):
        self.root.destroy()
