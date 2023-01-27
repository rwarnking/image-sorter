from error_messages import WarningArray, WarningCodes


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
        str(window_width) + "x" + str(window_height) + "+" + str(window_x) + "+" + str(window_y)
    )
    # Sets the geometry accordingly
    window.geometry(window_geometry)


def lt_window(window):
    window.update()
    window_width = window.winfo_width()
    window_height = window.winfo_height()

    # Creates a geometric string argument
    window_geometry = str(window_width) + "x" + str(window_height) + "+" + str(20) + "+" + str(20)
    # Sets the geometry accordingly
    window.geometry(window_geometry)


def test_time_frame(frame_start, frame_end, test_frame_start, test_frame_end):
    # Check if start date lies in time frame    
    if frame_start <= test_frame_start and test_frame_start < frame_end:
        return WarningCodes.WARNING_DATE_OVERLAP_START
    # Check if end date lies in time frame
    if frame_start < test_frame_end and test_frame_end <= frame_end:
        return WarningCodes.WARNING_DATE_OVERLAP_END
    # Check if start date being smaller and end date being bigger than compared time frame
    if test_frame_start <= frame_start and frame_end <= test_frame_end:
        return WarningCodes.WARNING_DATE_OVERLAP_BOTH
    # Check if the end date lies before the start date
    if test_frame_end < test_frame_start:
        return WarningCodes.WARNING_DATE_SWAP
    return None