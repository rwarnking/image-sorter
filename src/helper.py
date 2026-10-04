import re

from datetime import datetime
from fractions import Fraction
from tkinter import Tk, Toplevel, messagebox

from debug_messages import InfoCodes, WarningCodes


def wbox(msg: str):
    """Show warning box for validation error."""
    messagebox.showwarning(title="Validation Error!", message=msg)
    return InfoCodes.VAL_ERROR


def center_window(window: Toplevel):
    """Centers the given window on the screen."""
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
    # Override again such that automatic window resizing works
    # https://stackoverflow.com/questions/50955987/auto-resize-tkinter-window-to-fit-all-widgets
    window.geometry("")


def lt_window(window: Tk):
    """Aligns the given window at the left side of the screen (with margin)."""
    window.update()
    window_width = window.winfo_width()
    window_height = window.winfo_height()

    # Creates a geometric string argument
    window_geometry = str(window_width) + "x" + str(window_height) + "+" + str(20) + "+" + str(20)
    # Sets the geometry accordingly
    window.geometry(window_geometry)


def limit_input(S: str):
    """Returns true if the input character is a whitespace, -, _, a number or a letter."""
    return str.isalnum(S) or str.isspace(S) or S == "-" or S == "_" or S == "&"

def limit_input_float(input: str):
    """Returns true if the input is a float"""
    return re.fullmatch(r"\d*(\.\d*)?", input) is not None

def test_time_frame(
    frame_start: datetime,
    frame_end: datetime,
    test_frame_start: datetime,
    test_frame_end: datetime,
):
    """Check if the second time frame lies inside or overlaps with the first time frame."""
    # Check if start date lies in time frame
    if frame_start <= test_frame_start and test_frame_start < frame_end:
        return WarningCodes.WARNING_DATE_OVERLAP_START
    # Check if end date lies in time frame
    if frame_start < test_frame_end and test_frame_end <= frame_end:
        return WarningCodes.WARNING_DATE_OVERLAP_END
    # Check if start date being smaller and end date being bigger than compared time frame
    if test_frame_start <= frame_start and frame_end <= test_frame_end:
        return WarningCodes.WARNING_DATE_OVERLAP_BOTH
    return None


def test_time_frame_outside(
    frame_start: datetime,
    frame_end: datetime,
    test_frame_start: datetime,
    test_frame_end: datetime,
):
    """Check if the second time frame lies outside or overlaps with the first time frame."""
    if test_frame_start < frame_start and frame_end < test_frame_end:
        return WarningCodes.WARNING_DATE_OUTSIDE_BOTH
    # Check if start date lies outside time frame
    if test_frame_start < frame_start:
        return WarningCodes.WARNING_DATE_OUTSIDE_START
    if frame_end < test_frame_end:
        return WarningCodes.WARNING_DATE_OUTSIDE_END
    return None


def test_time_frame_swap(test_frame_start: datetime, test_frame_end: datetime):
    """Test if the start date and the the end date of the timeframe are swapped."""
    if test_frame_end < test_frame_start:
        return WarningCodes.WARNING_DATE_SWAP
    return None

# https://stackoverflow.com/questions/77015464/
def deg_to_dms(decimal_coordinate, cardinal_directions):
    """
    This function converts decimal coordinates into the
    DMS (degrees, minutes and seconds) format.
    It also determines the cardinal direction of the coordinates.

    :param decimal_coordinate: the decimal coordinates, such as 34.0522
    :param cardinal_directions: the locations of the decimal coordinate,
    such as ["S", "N"] or ["W", "E"]
    :return: degrees, minutes, seconds and compass_direction
    :rtype: int, int, float, string
    """
    if decimal_coordinate < 0:
        compass_direction = cardinal_directions[0]
    elif decimal_coordinate > 0:
        compass_direction = cardinal_directions[1]
    else:
        compass_direction = ""
    degrees = int(abs(decimal_coordinate))
    decimal_minutes = (abs(decimal_coordinate) - degrees) * 60
    minutes = int(decimal_minutes)
    seconds = Fraction((decimal_minutes - minutes) * 60).limit_denominator(100)
    return degrees, minutes, seconds, compass_direction

def dms_to_exif_format(dms_degrees, dms_minutes, dms_seconds):
    """
    This function converts DMS (degrees, minutes and seconds) to values that can
    be used with the EXIF (Exchangeable Image File Format).

    :param dms_degrees: int value for degrees
    :param dms_minutes: int value for minutes
    :param dms_seconds: fractions.Fraction value for seconds
    :return: EXIF values for the provided DMS values
    :rtype: nested tuple
    """
    exif_format = (
        (dms_degrees, 1),
        (dms_minutes, 1),
        (int(dms_seconds.limit_denominator(100).numerator), int(dms_seconds.limit_denominator(100).denominator))
    )
    return exif_format
