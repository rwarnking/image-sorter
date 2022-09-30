def center_window(window):
    window.update()
    window_width = window.winfo_width()
    window_height = window.winfo_height()

    # Calculates the x for the window to be in the center
    window_x = int((window.winfo_screenwidth() / 2) - (window_width / 2))
    # Calculates the y for the window to be in the center
    window_y = int((window.winfo_screenheight() / 2) - (window_height / 2))

    # Creates a geometric string argument
    window_geometry = (
        str(window_width) + 'x' + str(window_height) + '+' + str(window_x) + '+' + str(window_y)
    )
    # Sets the geometry accordingly
    window.geometry(window_geometry)

def lt_window(window):
    window.update()
    window_width = window.winfo_width()
    window_height = window.winfo_height()

    # Creates a geometric string argument
    window_geometry = str(window_width) + 'x' + str(window_height) + '+' + str(20) + '+' + str(20) 
    # Sets the geometry accordingly
    window.geometry(window_geometry)
