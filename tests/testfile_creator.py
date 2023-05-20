import os
import shutil
from datetime import datetime
from os.path import join
from typing import Any

import piexif


def create_all_test_files(test_folder: str = "test_images", sample_folder: str = "samples"):
    """
    Create files for all possible tests
    - test input file parsing
    - test recursive folder processing
    - file/s with/out event in db
    - file/s with/out make and model and therefore no artist in db
    - file/s with/out creation date in metadata
    - file/s with/out additional characters at the beginning (IMG_, MVI_, ...)
    - file/s with/out additional characters at the end (_1, - Copy, (2))
    - non jpg files (.svg, .gif, .raw, .txt)
    """
    BASE_DIR = os.path.dirname(__file__)
    IN_DIR = join(BASE_DIR, sample_folder)
    OUT_DIRS = [
        join(BASE_DIR, test_folder),
        join(join(BASE_DIR, test_folder), "_1"),
        join(join(BASE_DIR, test_folder), "recursive"),
        join(join(BASE_DIR, test_folder), "(2)"),
        join(join(BASE_DIR, test_folder), " - Copy"),
    ]

    for out_dir in OUT_DIRS:
        if not os.path.exists(out_dir):
            os.mkdir(out_dir)

    lst_endings = [".jpg", ".raw", ".svg", ".gif", ".txt"]

    lst_formats = [
        "%Y-%m-%d_%H-%M-%S",  # YYYY-MM-DD_HH-MM-SS
        "%Y-%m-%d_%H-%M-%S.%f",  # YYYY-MM-DD_HH-MM-SS.fff
        "%Y%m%d_%H%M%S",  # YYYYMMDD_HHMMSS
        "IMG_%Y%m%d_%H%M%S",  # IMG_YYYYMMDD_HHMMSS
        "MVI_%Y%m%d_%H%M%S",  # MVI_YYYYMMDD_HHMMSS
        "VID_%Y%m%d_%H%M%S",  # VID_YYYYMMDD_HHMMSS
        "%a %b %d %H-%M-%S %Y",  # Day Month DD HH-MM-SS YYYY
        "%m-%B-%d_001",  # MM-Month-DD_Number
        "%Y_[%m_%d]",  # YYYY_[MM_DD]
        "%Y_[%m_%d-%m_%d]",  # YYYY_[MM_DD-MM_DD]
        "IMG_YYYY",  # IMG_Number
        "gibberish",  # Random text only
    ]

    lst_metadata = [
        {  # Default case
            "Model": True,
            "Make": True,
            "Artist": False,
            "Date": True,
        },
        {  # All information
            "Model": True,
            "Make": True,
            "Artist": True,
            "Date": True,
        },
        {  # + Artist info
            "Model": True,
            "Make": True,
            "Artist": True,
            "Date": False,
        },
        {  # Only camera info
            "Model": True,
            "Make": True,
            "Artist": False,
            "Date": False,
        },
        {  # Date only
            "Model": False,
            "Make": False,
            "Artist": False,
            "Date": True,
        },
        {  # No information
            "Model": False,
            "Make": False,
            "Artist": False,
            "Date": False,
        },
    ]

    lst_dates = [
        # Date with matching event 1: Umzug
        lambda d: datetime.strptime(f"2020-07-{d:02d}_09-28-50.000", "%Y-%m-%d_%H-%M-%S.%f"),
        # Date with matching event 2: December
        lambda d: datetime.strptime(f"2020-12-{d:02d}_09-28-50.000", "%Y-%m-%d_%H-%M-%S.%f"),
        # Date without matching event
        lambda d: datetime.strptime(f"2020-09-{d:02d}_15-28-50.000", "%Y-%m-%d_%H-%M-%S.%f"),
        # Date with matching event 3: November
        lambda d: datetime.strptime(f"2021-11-{d:02d}_09-28-50.000", "%Y-%m-%d_%H-%M-%S.%f"),
        # Date with matching event 4: August
        lambda d: datetime.strptime(f"2022-08-{d:02d}_09-28-50.000", "%Y-%m-%d_%H-%M-%S.%f"),
    ]

    assert len(OUT_DIRS) == len(lst_dates)

    for i, format in enumerate(lst_formats):
        assert i + 1 < 28
        for j, date in enumerate(lst_dates):

            file_date = date(i + 1).strftime(format)
            # .%f prints 6 digits but we want 3
            if format == "%Y-%m-%d_%H-%M-%S.%f":
                file_date = file_date[:-3]

            if format == "gibberish":
                file_date = f"gibberish{j}"

            if format == "IMG_YYYY":
                file_date = f"IMG_{i*j:04d}"

            if j == 1:
                file_date += "_1"
            elif j == 3:
                file_date += " (2)"
            elif j == 4:
                file_date += " - Copy"

            for ext in lst_endings:
                out_dir = OUT_DIRS[j]
                shutil.copy2(join(IN_DIR, f"sample{ext}"), join(out_dir, f"{file_date}{ext}"))

                # Modify metadata
                if ext == ".jpg" and i < len(lst_metadata):
                    modify_metadata_piexif(
                        join(out_dir, f"{file_date}{ext}"), lst_metadata[i], date(i + 1)
                    )

                if ext == ".jpg" and i == 10:
                    modify_metadata_piexif(
                        join(out_dir, f"{file_date}{ext}"), lst_metadata[0], date(i + 1)
                    )


def modify_metadata_piexif(file_with_path: str, data: dict[str, Any], date: datetime):
    """
    Use piexif to load the exif metadata from the image
    and store it in the copy by using insert.
    This method prevents the image data from being decompressed and potentially altered.
    Documentation: https://github.com/hMatoba/Piexif
    Source: https://stackoverflow.com/questions/53543549/
    Since piexif is only sparsely maintained
    an alternate function is implemented using pyexiv2.

    The function processes all objects in meta_fields and tries to
    assign the value to the given dict/key.
    """
    try:
        exif_dict = piexif.load(file_with_path)
    except FileNotFoundError:
        return

    exif_dict["0th"][piexif.ImageIFD.Make] = "samsung" if data["Make"] else ""
    exif_dict["0th"][piexif.ImageIFD.Model] = "SM-G800F" if data["Model"] else ""
    exif_dict["0th"][piexif.ImageIFD.Artist] = "artist1" if data["Artist"] else ""

    # The original has no date so modification is only needed when it should be added
    if data["Date"]:
        # Create string from datetime object
        date_str = date.strftime("%Y:%m:%d %H:%M:%S")
        # Convert to binary
        date_bytes = date_str.encode("ascii")
        exif_dict["Exif"][piexif.ExifIFD.DateTimeOriginal] = date_bytes

        # Add millisecounds
        ms_str = date.strftime("%Y:%m:%d %H:%M:%S.%f")[-6:-3]
        ms_bytes = ms_str.encode("ascii")
        exif_dict["Exif"][piexif.ExifIFD.SubSecTimeOriginal] = ms_bytes

    # Write back to the file
    exif_bytes = piexif.dump(exif_dict)
    piexif.insert(exif_bytes, file_with_path)


###################################################################################################
# Main
###################################################################################################
if __name__ == "__main__":
    create_all_test_files()
