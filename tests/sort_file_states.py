from os.path import join
from typing import Any

import piexif

file_rules: dict[str, dict[str, list[dict[str, Any]]]] = {
    ###############################################################################################
    # 07-July-08_001
    ###############################################################################################
    "07-July-08_001": {
        "cases": [
            {  # None
                "folder": None,
                "name": None,
                "jpg": True,
                "conditions": [
                    ("process_unmatched", False),
                ],
            },
            {  # Misc
                "folder": "misc",
                "name": 1,
                "jpg": True,
                "conditions": [
                    ("in_signature", "Metadata only"),
                ],
            },
            {  # 1900 misc
                "folder": join("1900", "misc"),
                "name": 0,
                "jpg": True,
                "conditions": [],
            },
        ],
        "out": [
            {
                "YYYY-MM-DD_HH-MM-SS": "1900-07-08_00-00-00",
                "YYYY-MM-DD_HH-MM-SS.fff": "1900-07-08_00-00-00.001",
                "YYYYMMDD_HHMMSS": "19000708_000000",
                "IMG_YYYYMMDD_HHMMSS": "IMG_19000708_000000",
                "Day Month DD HH-MM-SS YYYY": "Sun Jul 08 00-00-00 1900",
                "Foldername_Number": "ERROR",
            },
            {
                "YYYY-MM-DD_HH-MM-SS": "07-July-08_001",
                "YYYY-MM-DD_HH-MM-SS.fff": "07-July-08_001",
                "YYYYMMDD_HHMMSS": "07-July-08_001",
                "IMG_YYYYMMDD_HHMMSS": "07-July-08_001",
                "Day Month DD HH-MM-SS YYYY": "07-July-08_001",
                "Foldername_Number": "07-July-08_001",
            },
        ],
    },
    ###############################################################################################
    # 2020_[07_09]
    ###############################################################################################
    "2020_[07_09]": {
        "cases": [
            {  # Misc
                "folder": "misc",
                "name": 1,
                "jpg": True,
                "conditions": [
                    ("in_signature", "Metadata only"),
                    ("process_unmatched", True),
                ],
            },
            {  # None
                "folder": None,
                "name": None,
                "jpg": True,
                "conditions": [
                    ("in_signature", "Metadata only"),
                ],
            },
            {
                "folder": join("2020", "2020_[07_01-07_10]_Umzug"),
                "name": 0,
                "jpg": True,
                "conditions": [
                    ("require_artist", False),
                ],
            },
            {
                "folder": join("2020", join("2020_[07_01-07_10]_Umzug", "no_artist")),
                "name": 0,
                "jpg": True,
                "conditions": [],
            },
        ],
        "out": [
            {
                "YYYY-MM-DD_HH-MM-SS": "2020-07-09_00-00-00",
                "YYYY-MM-DD_HH-MM-SS.fff": "2020-07-09_00-00-00.000",
                "YYYYMMDD_HHMMSS": "20200709_000000",
                "IMG_YYYYMMDD_HHMMSS": "IMG_20200709_000000",
                "Day Month DD HH-MM-SS YYYY": "Thu Jul 09 00-00-00 2020",
                "Foldername_Number": "ERROR",
            },
            {
                "YYYY-MM-DD_HH-MM-SS": "2020_[07_09]",
                "YYYY-MM-DD_HH-MM-SS.fff": "2020_[07_09]",
                "YYYYMMDD_HHMMSS": "2020_[07_09]",
                "IMG_YYYYMMDD_HHMMSS": "2020_[07_09]",
                "Day Month DD HH-MM-SS YYYY": "2020_[07_09]",
                "Foldername_Number": "2020_[07_09]",
            },
        ],
    },
    ###############################################################################################
    # 2020_[07_10-07_10]
    ###############################################################################################
    "2020_[07_10-07_10]": {
        "cases": [
            {  # Misc
                "folder": "misc",
                "name": 1,
                "jpg": True,
                "conditions": [
                    ("in_signature", "Metadata only"),
                    ("process_unmatched", True),
                ],
            },
            {  # None
                "folder": None,
                "name": None,
                "jpg": True,
                "conditions": [
                    ("in_signature", "Metadata only"),
                ],
            },
            {
                "folder": join("2020", "2020_[07_01-07_10]_Umzug"),
                "name": 0,
                "jpg": True,
                "conditions": [
                    ("require_artist", False),
                ],
            },
            {
                "folder": join("2020", join("2020_[07_01-07_10]_Umzug", "no_artist")),
                "name": 0,
                "jpg": True,
                "conditions": [],
            },
        ],
        "out": [
            {
                "YYYY-MM-DD_HH-MM-SS": "2020-07-10_00-00-00",
                "YYYY-MM-DD_HH-MM-SS.fff": "2020-07-10_00-00-00.000",
                "YYYYMMDD_HHMMSS": "20200710_000000",
                "IMG_YYYYMMDD_HHMMSS": "IMG_20200710_000000",
                "Day Month DD HH-MM-SS YYYY": "Fri Jul 10 00-00-00 2020",
                "Foldername_Number": "ERROR",
            },
            {
                "YYYY-MM-DD_HH-MM-SS": "2020_[07_10-07_10]",
                "YYYY-MM-DD_HH-MM-SS.fff": "2020_[07_10-07_10]",
                "YYYYMMDD_HHMMSS": "2020_[07_10-07_10]",
                "IMG_YYYYMMDD_HHMMSS": "2020_[07_10-07_10]",
                "Day Month DD HH-MM-SS YYYY": "2020_[07_10-07_10]",
                "Foldername_Number": "2020_[07_10-07_10]",
            },
        ],
    },
    ###############################################################################################
    # 2020-07-01_09-28-50
    ###############################################################################################
    "2020-07-01_09-28-50": {
        "cases": [
            {  # Misc
                "folder": "misc",
                "name": 1,
                "jpg": False,
                "conditions": [
                    ("in_signature", "Metadata only"),
                    ("process_unmatched", True),
                    ("process_samename", False),
                ],
            },
            {  # None
                "folder": None,
                "name": None,
                "jpg": False,
                "conditions": [
                    ("in_signature", "Metadata only"),
                    ("process_samename", False),
                ],
            },
            {
                "folder": join("2020", "2020_[07_01-07_10]_Umzug"),
                "name": 0,
                "jpg": True,
                "conditions": [
                    ("require_artist", False),
                ],
            },
            {
                "folder": join("2020", join("2020_[07_01-07_10]_Umzug", "no_artist")),
                "name": 0,
                "jpg": True,
                "conditions": [],
            },
        ],
        "out": [
            {
                "YYYY-MM-DD_HH-MM-SS": "2020-07-01_09-28-50",
                "YYYY-MM-DD_HH-MM-SS.fff": "2020-07-01_09-28-50.000",
                "YYYYMMDD_HHMMSS": "20200701_092850",
                "IMG_YYYYMMDD_HHMMSS": "IMG_20200701_092850",
                "Day Month DD HH-MM-SS YYYY": "Wed Jul 01 09-28-50 2020",
                "Foldername_Number": "ERROR",
            },
            {
                "YYYY-MM-DD_HH-MM-SS": "2020-07-01_09-28-50",
                "YYYY-MM-DD_HH-MM-SS.fff": "2020-07-01_09-28-50",
                "YYYYMMDD_HHMMSS": "2020-07-01_09-28-50",
                "IMG_YYYYMMDD_HHMMSS": "2020-07-01_09-28-50",
                "Day Month DD HH-MM-SS YYYY": "2020-07-01_09-28-50",
                "Foldername_Number": "2020-07-01_09-28-50",
            },
        ],
        "meta": [
            {
                "dict": "0th",
                "key": piexif.ImageIFD.ImageDescription,
                "value_disabled": None,
                "value_enabled": "Umzug",
            },
        ],
    },
    ###############################################################################################
    # 2020-07-02_09-28-50.000
    ###############################################################################################
    "2020-07-02_09-28-50.000": {
        "cases": [
            {  # Misc
                "folder": "misc",
                "name": 1,
                "jpg": False,
                "conditions": [
                    ("in_signature", "Metadata only"),
                    ("process_unmatched", True),
                    ("process_samename", False),
                ],
            },
            {  # None
                "folder": None,
                "name": None,
                "jpg": False,
                "conditions": [
                    ("in_signature", "Metadata only"),
                    ("process_samename", False),
                ],
            },
            {
                "folder": join("2020", "2020_[07_01-07_10]_Umzug"),
                "name": 0,
                "jpg": True,
                "conditions": [
                    ("require_artist", False),
                ],
            },
            {
                "folder": join("2020", join("2020_[07_01-07_10]_Umzug", "no_artist")),
                "name": 0,
                "jpg": True,
                "conditions": [],
            },
        ],
        "out": [
            {
                "YYYY-MM-DD_HH-MM-SS": "2020-07-02_09-28-50",
                "YYYY-MM-DD_HH-MM-SS.fff": "2020-07-02_09-28-50.000",
                "YYYYMMDD_HHMMSS": "20200702_092850",
                "IMG_YYYYMMDD_HHMMSS": "IMG_20200702_092850",
                "Day Month DD HH-MM-SS YYYY": "Thu Jul 02 09-28-50 2020",
                "Foldername_Number": "ERROR",
            },
            {
                "YYYY-MM-DD_HH-MM-SS": "2020-07-02_09-28-50.000",
                "YYYY-MM-DD_HH-MM-SS.fff": "2020-07-02_09-28-50.000",
                "YYYYMMDD_HHMMSS": "2020-07-02_09-28-50.000",
                "IMG_YYYYMMDD_HHMMSS": "2020-07-02_09-28-50.000",
                "Day Month DD HH-MM-SS YYYY": "2020-07-02_09-28-50.000",
                "Foldername_Number": "2020-07-02_09-28-50.000",
            },
        ],
        "meta": [
            {
                "dict": "0th",
                "key": piexif.ImageIFD.ImageDescription,
                "value_disabled": None,
                "value_enabled": "Umzug",
            },
        ],
    },
    ###############################################################################################
    # 20200703_092850
    ###############################################################################################
    "20200703_092850": {
        "cases": [
            {  # Misc
                "folder": "misc",
                "name": 1,
                "jpg": True,
                "conditions": [
                    ("in_signature", "Metadata only"),
                    ("process_unmatched", True),
                ],
            },
            {  # None
                "folder": None,
                "name": None,
                "jpg": True,
                "conditions": [
                    ("in_signature", "Metadata only"),
                ],
            },
            {
                "folder": join("2020", "2020_[07_01-07_10]_Umzug"),
                "name": 0,
                "jpg": True,
                "conditions": [
                    ("require_artist", False),
                ],
            },
            {
                "folder": join("2020", join("2020_[07_01-07_10]_Umzug", "no_artist")),
                "name": 0,
                "jpg": True,
                "conditions": [],
            },
        ],
        "out": [
            {
                "YYYY-MM-DD_HH-MM-SS": "2020-07-03_09-28-50",
                "YYYY-MM-DD_HH-MM-SS.fff": "2020-07-03_09-28-50.000",
                "YYYYMMDD_HHMMSS": "20200703_092850",
                "IMG_YYYYMMDD_HHMMSS": "IMG_20200703_092850",
                "Day Month DD HH-MM-SS YYYY": "Fri Jul 03 09-28-50 2020",
                "Foldername_Number": "ERROR",
            },
            {
                "YYYY-MM-DD_HH-MM-SS": "20200703_092850",
                "YYYY-MM-DD_HH-MM-SS.fff": "20200703_092850",
                "YYYYMMDD_HHMMSS": "20200703_092850",
                "IMG_YYYYMMDD_HHMMSS": "20200703_092850",
                "Day Month DD HH-MM-SS YYYY": "20200703_092850",
                "Foldername_Number": "20200703_092850",
            },
        ],
    },
    ###############################################################################################
    # gibberish
    ###############################################################################################
    "gibberish0": {
        "cases": [
            {  # MISC
                "folder": "misc",
                "name": 0,
                "jpg": True,
                "conditions": [
                    ("process_unmatched", True),
                ],
            },
            {
                "folder": None,
                "name": None,
                "jpg": True,
                "conditions": [],
            },
        ],
        "out": [
            {
                "YYYY-MM-DD_HH-MM-SS": "gibberish0",
                "YYYY-MM-DD_HH-MM-SS.fff": "gibberish0",
                "YYYYMMDD_HHMMSS": "gibberish0",
                "IMG_YYYYMMDD_HHMMSS": "gibberish0",
                "Day Month DD HH-MM-SS YYYY": "gibberish0",
                "Foldername_Number": "gibberish0",
            },
        ],
    },
    ###############################################################################################
    # IMG_20200704_092850
    ###############################################################################################
    "IMG_20200704_092850": {
        "cases": [
            {  # Misc
                "folder": "misc",
                "name": 1,
                "jpg": True,
                "conditions": [
                    ("in_signature", "Metadata only"),
                    ("process_unmatched", True),
                ],
            },
            {  # None
                "folder": None,
                "name": None,
                "jpg": True,
                "conditions": [
                    ("in_signature", "Metadata only"),
                ],
            },
            {
                "folder": join("2020", "2020_[07_01-07_10]_Umzug"),
                "name": 0,
                "jpg": True,
                "conditions": [
                    ("require_artist", False),
                ],
            },
            {
                "folder": join("2020", join("2020_[07_01-07_10]_Umzug", "no_artist")),
                "name": 0,
                "jpg": True,
                "conditions": [],
            },
        ],
        "out": [
            {
                "YYYY-MM-DD_HH-MM-SS": "2020-07-04_09-28-50",
                "YYYY-MM-DD_HH-MM-SS.fff": "2020-07-04_09-28-50.000",
                "YYYYMMDD_HHMMSS": "20200704_092850",
                "IMG_YYYYMMDD_HHMMSS": "IMG_20200704_092850",
                "Day Month DD HH-MM-SS YYYY": "Sat Jul 04 09-28-50 2020",
                "Foldername_Number": "ERROR",
            },
            {
                "YYYY-MM-DD_HH-MM-SS": "IMG_20200704_092850",
                "YYYY-MM-DD_HH-MM-SS.fff": "IMG_20200704_092850",
                "YYYYMMDD_HHMMSS": "IMG_20200704_092850",
                "IMG_YYYYMMDD_HHMMSS": "IMG_20200704_092850",
                "Day Month DD HH-MM-SS YYYY": "IMG_20200704_092850",
                "Foldername_Number": "IMG_20200704_092850",
            },
        ],
    },
    ###############################################################################################
    # IMG_YYYY
    ###############################################################################################
    "IMG_0000": {
        "cases": [
            {  # Misc
                "folder": "misc",
                "name": 1,
                "jpg": False,
                "conditions": [
                    ("process_unmatched", True),
                    ("process_samename", False),
                ],
            },
            {  # Misc
                "folder": "misc",
                "name": 1,
                "jpg": True,
                "conditions": [
                    ("in_signature", "Filename only"),
                    ("process_unmatched", True),
                ],
            },
            {  # None
                "folder": None,
                "name": None,
                "jpg": True,
                "conditions": [
                    ("process_unmatched", False),
                    ("process_samename", False),
                ],
            },
            {
                "folder": join("2020", "misc"),
                "name": 0,
                "jpg": True,
                "conditions": [],
            },
        ],
        "out": [
            {
                "YYYY-MM-DD_HH-MM-SS": "2020-07-11_09-28-50",
                "YYYY-MM-DD_HH-MM-SS.fff": "2020-07-11_09-28-50.000",
                "YYYYMMDD_HHMMSS": "20200711_092850",
                "IMG_YYYYMMDD_HHMMSS": "IMG_20200711_092850",
                "Day Month DD HH-MM-SS YYYY": "Sat Jul 11 09-28-50 2020",
                "Foldername_Number": "ERROR",
            },
            {
                "YYYY-MM-DD_HH-MM-SS": "IMG_0000",
                "YYYY-MM-DD_HH-MM-SS.fff": "IMG_0000",
                "YYYYMMDD_HHMMSS": "IMG_0000",
                "IMG_YYYYMMDD_HHMMSS": "IMG_0000",
                "Day Month DD HH-MM-SS YYYY": "IMG_0000",
                "Foldername_Number": "IMG_0000",
            },
        ],
    },
    ###############################################################################################
    # MVI_20200705_092850
    ###############################################################################################
    "MVI_20200705_092850": {
        "cases": [
            {  # Misc
                "folder": "misc",
                "name": 1,
                "jpg": False,
                "conditions": [
                    ("in_signature", "Metadata only"),
                    ("process_unmatched", True),
                    ("process_samename", False),
                ],
            },
            {  # None
                "folder": None,
                "name": None,
                "jpg": False,
                "conditions": [
                    ("in_signature", "Metadata only"),
                    ("process_samename", False),
                ],
            },
            {
                "folder": join("2020", "2020_[07_01-07_10]_Umzug"),
                "name": 0,
                "jpg": True,
                "conditions": [
                    ("require_artist", False),
                ],
            },
            {
                "folder": join("2020", join("2020_[07_01-07_10]_Umzug", "no_artist")),
                "name": 0,
                "jpg": True,
                "conditions": [],
            },
        ],
        "out": [
            {
                "YYYY-MM-DD_HH-MM-SS": "2020-07-05_09-28-50",
                "YYYY-MM-DD_HH-MM-SS.fff": "2020-07-05_09-28-50.000",
                "YYYYMMDD_HHMMSS": "20200705_092850",
                "IMG_YYYYMMDD_HHMMSS": "IMG_20200705_092850",
                "Day Month DD HH-MM-SS YYYY": "Sun Jul 05 09-28-50 2020",
                "Foldername_Number": "ERROR",
            },
            {
                "YYYY-MM-DD_HH-MM-SS": "MVI_20200705_092850",
                "YYYY-MM-DD_HH-MM-SS.fff": "MVI_20200705_092850",
                "YYYYMMDD_HHMMSS": "MVI_20200705_092850",
                "IMG_YYYYMMDD_HHMMSS": "MVI_20200705_092850",
                "Day Month DD HH-MM-SS YYYY": "MVI_20200705_092850",
                "Foldername_Number": "MVI_20200705_092850",
            },
        ],
    },
    ###############################################################################################
    # Tue Jul 07 09-28-50 2020
    ###############################################################################################
    "Tue Jul 07 09-28-50 2020": {
        "cases": [
            {  # Misc
                "folder": "misc",
                "name": 1,
                "jpg": True,
                "conditions": [
                    ("in_signature", "Metadata only"),
                    ("process_unmatched", True),
                ],
            },
            {  # None
                "folder": None,
                "name": None,
                "jpg": True,
                "conditions": [
                    ("in_signature", "Metadata only"),
                ],
            },
            {
                "folder": join("2020", "2020_[07_01-07_10]_Umzug"),
                "name": 0,
                "jpg": True,
                "conditions": [
                    ("require_artist", False),
                ],
            },
            {
                "folder": join("2020", join("2020_[07_01-07_10]_Umzug", "no_artist")),
                "name": 0,
                "jpg": True,
                "conditions": [],
            },
        ],
        "out": [
            {
                "YYYY-MM-DD_HH-MM-SS": "2020-07-07_09-28-50",
                "YYYY-MM-DD_HH-MM-SS.fff": "2020-07-07_09-28-50.000",
                "YYYYMMDD_HHMMSS": "20200707_092850",
                "IMG_YYYYMMDD_HHMMSS": "IMG_20200707_092850",
                "Day Month DD HH-MM-SS YYYY": "Tue Jul 07 09-28-50 2020",
                "Foldername_Number": "ERROR",
            },
            {
                "YYYY-MM-DD_HH-MM-SS": "Tue Jul 07 09-28-50 2020",
                "YYYY-MM-DD_HH-MM-SS.fff": "Tue Jul 07 09-28-50 2020",
                "YYYYMMDD_HHMMSS": "Tue Jul 07 09-28-50 2020",
                "IMG_YYYYMMDD_HHMMSS": "Tue Jul 07 09-28-50 2020",
                "Day Month DD HH-MM-SS YYYY": "Tue Jul 07 09-28-50 2020",
                "Foldername_Number": "Tue Jul 07 09-28-50 2020",
            },
        ],
    },
    ###############################################################################################
    # VID_20200706_092850
    ###############################################################################################
    "VID_20200706_092850": {
        "cases": [
            {  # Misc
                "folder": "misc",
                "name": 1,
                "jpg": True,
                "conditions": [
                    ("in_signature", "Metadata only"),
                    ("process_unmatched", True),
                ],
            },
            {  # None
                "folder": None,
                "name": None,
                "jpg": True,
                "conditions": [
                    ("in_signature", "Metadata only"),
                ],
            },
            {
                "folder": join("2020", "2020_[07_01-07_10]_Umzug"),
                "name": 0,
                "jpg": True,
                "conditions": [
                    ("require_artist", False),
                ],
            },
            {
                "folder": join("2020", join("2020_[07_01-07_10]_Umzug", "no_artist")),
                "name": 0,
                "jpg": True,
                "conditions": [],
            },
        ],
        "out": [
            {
                "YYYY-MM-DD_HH-MM-SS": "2020-07-06_09-28-50",
                "YYYY-MM-DD_HH-MM-SS.fff": "2020-07-06_09-28-50.000",
                "YYYYMMDD_HHMMSS": "20200706_092850",
                "IMG_YYYYMMDD_HHMMSS": "IMG_20200706_092850",
                "Day Month DD HH-MM-SS YYYY": "Mon Jul 06 09-28-50 2020",
                "Foldername_Number": "ERROR",
            },
            {
                "YYYY-MM-DD_HH-MM-SS": "VID_20200706_092850",
                "YYYY-MM-DD_HH-MM-SS.fff": "VID_20200706_092850",
                "YYYYMMDD_HHMMSS": "VID_20200706_092850",
                "IMG_YYYYMMDD_HHMMSS": "VID_20200706_092850",
                "Day Month DD HH-MM-SS YYYY": "VID_20200706_092850",
                "Foldername_Number": "VID_20200706_092850",
            },
        ],
    },
    ###############################################################################################
    ###############################################################################################
    # RECURSIVE
    ###############################################################################################
    ###############################################################################################
    ###############################################################################################
    # 09-September-08_001
    ###############################################################################################
    join("recursive", "09-September-08_001"): {
        "cases": [
            {  # None
                "folder": None,
                "name": None,
                "jpg": True,
                "conditions": [
                    ("process_unmatched", False),
                ],
            },
            {  # Misc
                "folder": "misc",
                "name": 1,
                "jpg": True,
                "conditions": [
                    ("in_signature", "Metadata only"),
                ],
            },
            {
                "folder": join("1900", "misc"),
                "name": 0,
                "jpg": True,
                "conditions": [],
            },
        ],
        "out": [
            {
                "YYYY-MM-DD_HH-MM-SS": "1900-09-08_00-00-00",
                "YYYY-MM-DD_HH-MM-SS.fff": "1900-09-08_00-00-00.001",
                "YYYYMMDD_HHMMSS": "19000908_000000",
                "IMG_YYYYMMDD_HHMMSS": "IMG_19000908_000000",
                "Day Month DD HH-MM-SS YYYY": "Sat Sep 08 00-00-00 1900",
                "Foldername_Number": "ERROR",
            },
            {
                "YYYY-MM-DD_HH-MM-SS": "09-September-08_001",
                "YYYY-MM-DD_HH-MM-SS.fff": "09-September-08_001",
                "YYYYMMDD_HHMMSS": "09-September-08_001",
                "IMG_YYYYMMDD_HHMMSS": "09-September-08_001",
                "Day Month DD HH-MM-SS YYYY": "09-September-08_001",
                "Foldername_Number": "09-September-08_001",
            },
        ],
    },
    # ###############################################################################################
    # # 2020_[09_09]
    # ###############################################################################################
    join("recursive", "2020_[09_09]"): {
        "cases": [
            {  # Misc
                "folder": "misc",
                "name": 1,
                "jpg": True,
                "conditions": [
                    ("in_signature", "Metadata only"),
                    ("process_unmatched", True),
                ],
            },
            {  # None
                "folder": None,
                "name": None,
                "jpg": True,
                "conditions": [
                    ("process_unmatched", False),
                ],
            },
            {
                "folder": join("2020", "misc"),
                "name": 0,
                "jpg": True,
                "conditions": [],
            },
        ],
        "out": [
            {
                "YYYY-MM-DD_HH-MM-SS": "2020-09-09_00-00-00",
                "YYYY-MM-DD_HH-MM-SS.fff": "2020-09-09_00-00-00.000",
                "YYYYMMDD_HHMMSS": "20200909_000000",
                "IMG_YYYYMMDD_HHMMSS": "IMG_20200909_000000",
                "Day Month DD HH-MM-SS YYYY": "Wed Sep 09 00-00-00 2020",
                "Foldername_Number": "ERROR",
            },
            {
                "YYYY-MM-DD_HH-MM-SS": "2020_[09_09]",
                "YYYY-MM-DD_HH-MM-SS.fff": "2020_[09_09]",
                "YYYYMMDD_HHMMSS": "2020_[09_09]",
                "IMG_YYYYMMDD_HHMMSS": "2020_[09_09]",
                "Day Month DD HH-MM-SS YYYY": "2020_[09_09]",
                "Foldername_Number": "2020_[09_09]",
            },
        ],
    },
    ###############################################################################################
    # 2020_[09_10-09_10]
    ###############################################################################################
    join("recursive", "2020_[09_10-09_10]"): {
        "cases": [
            {  # Misc
                "folder": "misc",
                "name": 1,
                "jpg": True,
                "conditions": [
                    ("in_signature", "Metadata only"),
                    ("process_unmatched", True),
                ],
            },
            {  # None
                "folder": None,
                "name": None,
                "jpg": True,
                "conditions": [
                    ("process_unmatched", False),
                ],
            },
            {
                "folder": join("2020", "misc"),
                "name": 0,
                "jpg": True,
                "conditions": [],
            },
        ],
        "out": [
            {
                "YYYY-MM-DD_HH-MM-SS": "2020-09-10_00-00-00",
                "YYYY-MM-DD_HH-MM-SS.fff": "2020-09-10_00-00-00.000",
                "YYYYMMDD_HHMMSS": "20200910_000000",
                "IMG_YYYYMMDD_HHMMSS": "IMG_20200910_000000",
                "Day Month DD HH-MM-SS YYYY": "Thu Sep 10 00-00-00 2020",
                "Foldername_Number": "ERROR",
            },
            {
                "YYYY-MM-DD_HH-MM-SS": "2020_[09_10-09_10]",
                "YYYY-MM-DD_HH-MM-SS.fff": "2020_[09_10-09_10]",
                "YYYYMMDD_HHMMSS": "2020_[09_10-09_10]",
                "IMG_YYYYMMDD_HHMMSS": "2020_[09_10-09_10]",
                "Day Month DD HH-MM-SS YYYY": "2020_[09_10-09_10]",
                "Foldername_Number": "2020_[09_10-09_10]",
            },
        ],
    },
    ###############################################################################################
    # 2020-09-01_15-28-50
    ###############################################################################################
    join("recursive", "2020-09-01_15-28-50"): {
        "cases": [
            {  # Misc
                "folder": "misc",
                "name": 1,
                "jpg": False,
                "conditions": [
                    ("in_signature", "Metadata only"),
                    ("process_unmatched", True),
                    ("process_samename", False),
                ],
            },
            {  # None
                "folder": None,
                "name": None,
                "jpg": True,
                "conditions": [
                    ("process_unmatched", False),
                ],
            },
            {
                "folder": join("2020", "misc"),
                "name": 0,
                "jpg": True,
                "conditions": [],
            },
        ],
        "out": [
            {
                "YYYY-MM-DD_HH-MM-SS": "2020-09-01_15-28-50",
                "YYYY-MM-DD_HH-MM-SS.fff": "2020-09-01_15-28-50.000",
                "YYYYMMDD_HHMMSS": "20200901_152850",
                "IMG_YYYYMMDD_HHMMSS": "IMG_20200901_152850",
                "Day Month DD HH-MM-SS YYYY": "Tue Sep 01 15-28-50 2020",
                "Foldername_Number": "ERROR",
            },
            {
                "YYYY-MM-DD_HH-MM-SS": "2020-09-01_15-28-50",
                "YYYY-MM-DD_HH-MM-SS.fff": "2020-09-01_15-28-50",
                "YYYYMMDD_HHMMSS": "2020-09-01_15-28-50",
                "IMG_YYYYMMDD_HHMMSS": "2020-09-01_15-28-50",
                "Day Month DD HH-MM-SS YYYY": "2020-09-01_15-28-50",
                "Foldername_Number": "2020-09-01_15-28-50",
            },
        ],
    },
    ###############################################################################################
    # 2020-09-02_15-28-50.000
    ###############################################################################################
    join("recursive", "2020-09-02_15-28-50.000"): {
        "cases": [
            {  # Misc
                "folder": "misc",
                "name": 1,
                "jpg": False,
                "conditions": [
                    ("in_signature", "Metadata only"),
                    ("process_unmatched", True),
                    ("process_samename", False),
                ],
            },
            {  # None
                "folder": None,
                "name": None,
                "jpg": True,
                "conditions": [
                    ("process_unmatched", False),
                ],
            },
            {
                "folder": join("2020", "misc"),
                "name": 0,
                "jpg": True,
                "conditions": [],
            },
        ],
        "out": [
            {
                "YYYY-MM-DD_HH-MM-SS": "2020-09-02_15-28-50",
                "YYYY-MM-DD_HH-MM-SS.fff": "2020-09-02_15-28-50.000",
                "YYYYMMDD_HHMMSS": "20200902_152850",
                "IMG_YYYYMMDD_HHMMSS": "IMG_20200902_152850",
                "Day Month DD HH-MM-SS YYYY": "Wed Sep 02 15-28-50 2020",
                "Foldername_Number": "ERROR",
            },
            {
                "YYYY-MM-DD_HH-MM-SS": "2020-09-02_15-28-50.000",
                "YYYY-MM-DD_HH-MM-SS.fff": "2020-09-02_15-28-50.000",
                "YYYYMMDD_HHMMSS": "2020-09-02_15-28-50.000",
                "IMG_YYYYMMDD_HHMMSS": "2020-09-02_15-28-50.000",
                "Day Month DD HH-MM-SS YYYY": "2020-09-02_15-28-50.000",
                "Foldername_Number": "2020-09-02_15-28-50.000",
            },
        ],
    },
    ###############################################################################################
    # 20200903_152850
    ###############################################################################################
    join("recursive", "20200903_152850"): {
        "cases": [
            {  # Misc
                "folder": "misc",
                "name": 1,
                "jpg": True,
                "conditions": [
                    ("in_signature", "Metadata only"),
                    ("process_unmatched", True),
                ],
            },
            {  # None
                "folder": None,
                "name": None,
                "jpg": True,
                "conditions": [
                    ("process_unmatched", False),
                ],
            },
            {
                "folder": join("2020", "misc"),
                "name": 0,
                "jpg": True,
                "conditions": [],
            },
        ],
        "out": [
            {
                "YYYY-MM-DD_HH-MM-SS": "2020-09-03_15-28-50",
                "YYYY-MM-DD_HH-MM-SS.fff": "2020-09-03_15-28-50.000",
                "YYYYMMDD_HHMMSS": "20200903_152850",
                "IMG_YYYYMMDD_HHMMSS": "IMG_20200903_152850",
                "Day Month DD HH-MM-SS YYYY": "Thu Sep 03 15-28-50 2020",
                "Foldername_Number": "ERROR",
            },
            {
                "YYYY-MM-DD_HH-MM-SS": "20200903_152850",
                "YYYY-MM-DD_HH-MM-SS.fff": "20200903_152850",
                "YYYYMMDD_HHMMSS": "20200903_152850",
                "IMG_YYYYMMDD_HHMMSS": "20200903_152850",
                "Day Month DD HH-MM-SS YYYY": "20200903_152850",
                "Foldername_Number": "20200903_152850",
            },
        ],
    },
    ###############################################################################################
    # gibberish2
    ###############################################################################################
    join("recursive", "gibberish2"): {
        "cases": [
            {  # MISC
                "folder": "misc",
                "name": 0,
                "jpg": True,
                "conditions": [
                    ("process_unmatched", True),
                ],
            },
            {
                "folder": None,
                "name": None,
                "jpg": True,
                "conditions": [],
            },
        ],
        "out": [
            {
                "YYYY-MM-DD_HH-MM-SS": "gibberish2",
                "YYYY-MM-DD_HH-MM-SS.fff": "gibberish2",
                "YYYYMMDD_HHMMSS": "gibberish2",
                "IMG_YYYYMMDD_HHMMSS": "gibberish2",
                "Day Month DD HH-MM-SS YYYY": "gibberish2",
                "Foldername_Number": "gibberish2",
            },
        ],
    },
    ###############################################################################################
    # IMG_20200904_152850
    ###############################################################################################
    join("recursive", "IMG_20200904_152850"): {
        "cases": [
            {  # Misc
                "folder": "misc",
                "name": 1,
                "jpg": True,
                "conditions": [
                    ("in_signature", "Metadata only"),
                    ("process_unmatched", True),
                ],
            },
            {  # None
                "folder": None,
                "name": None,
                "jpg": True,
                "conditions": [
                    ("process_unmatched", False),
                ],
            },
            {
                "folder": join("2020", "misc"),
                "name": 0,
                "jpg": True,
                "conditions": [],
            },
        ],
        "out": [
            {
                "YYYY-MM-DD_HH-MM-SS": "2020-09-04_15-28-50",
                "YYYY-MM-DD_HH-MM-SS.fff": "2020-09-04_15-28-50.000",
                "YYYYMMDD_HHMMSS": "20200904_152850",
                "IMG_YYYYMMDD_HHMMSS": "IMG_20200904_152850",
                "Day Month DD HH-MM-SS YYYY": "Fri Sep 04 15-28-50 2020",
                "Foldername_Number": "ERROR",
            },
            {
                "YYYY-MM-DD_HH-MM-SS": "IMG_20200904_152850",
                "YYYY-MM-DD_HH-MM-SS.fff": "IMG_20200904_152850",
                "YYYYMMDD_HHMMSS": "IMG_20200904_152850",
                "IMG_YYYYMMDD_HHMMSS": "IMG_20200904_152850",
                "Day Month DD HH-MM-SS YYYY": "IMG_20200904_152850",
                "Foldername_Number": "IMG_20200904_152850",
            },
        ],
    },
    ###############################################################################################
    # IMG_0020
    ###############################################################################################
    join("recursive", "IMG_0020"): {
        "cases": [
            {  # Misc
                "folder": "misc",
                "name": 1,
                "jpg": False,
                "conditions": [
                    ("process_unmatched", True),
                    ("process_samename", False),
                ],
            },
            {  # Misc
                "folder": "misc",
                "name": 1,
                "jpg": True,
                "conditions": [
                    ("in_signature", "Filename only"),
                    ("process_unmatched", True),
                ],
            },
            {  # None
                "folder": None,
                "name": None,
                "jpg": True,
                "conditions": [
                    ("process_unmatched", False),
                ],
            },
            {
                "folder": join("2020", "misc"),
                "name": 0,
                "jpg": True,
                "conditions": [],
            },
        ],
        "out": [
            {
                "YYYY-MM-DD_HH-MM-SS": "2020-09-11_15-28-50",
                "YYYY-MM-DD_HH-MM-SS.fff": "2020-09-11_15-28-50.000",
                "YYYYMMDD_HHMMSS": "20200911_152850",
                "IMG_YYYYMMDD_HHMMSS": "IMG_20200911_152850",
                "Day Month DD HH-MM-SS YYYY": "Fri Sep 11 15-28-50 2020",
                "Foldername_Number": "ERROR",
            },
            {
                "YYYY-MM-DD_HH-MM-SS": "IMG_0020",
                "YYYY-MM-DD_HH-MM-SS.fff": "IMG_0020",
                "YYYYMMDD_HHMMSS": "IMG_0020",
                "IMG_YYYYMMDD_HHMMSS": "IMG_0020",
                "Day Month DD HH-MM-SS YYYY": "IMG_0020",
                "Foldername_Number": "IMG_0020",
            },
        ],
    },
    ###############################################################################################
    # MVI_20200905_152850
    ###############################################################################################
    join("recursive", "MVI_20200905_152850"): {
        "cases": [
            {  # Misc
                "folder": "misc",
                "name": 1,
                "jpg": False,
                "conditions": [
                    ("in_signature", "Metadata only"),
                    ("process_unmatched", True),
                    ("process_samename", False),
                ],
            },
            {  # None
                "folder": None,
                "name": None,
                "jpg": True,
                "conditions": [
                    ("process_unmatched", False),
                ],
            },
            {
                "folder": join("2020", "misc"),
                "name": 0,
                "jpg": True,
                "conditions": [],
            },
        ],
        "out": [
            {
                "YYYY-MM-DD_HH-MM-SS": "2020-09-05_15-28-50",
                "YYYY-MM-DD_HH-MM-SS.fff": "2020-09-05_15-28-50.000",
                "YYYYMMDD_HHMMSS": "20200905_152850",
                "IMG_YYYYMMDD_HHMMSS": "IMG_20200905_152850",
                "Day Month DD HH-MM-SS YYYY": "Sat Sep 05 15-28-50 2020",
                "Foldername_Number": "ERROR",
            },
            {
                "YYYY-MM-DD_HH-MM-SS": "MVI_20200905_152850",
                "YYYY-MM-DD_HH-MM-SS.fff": "MVI_20200905_152850",
                "YYYYMMDD_HHMMSS": "MVI_20200905_152850",
                "IMG_YYYYMMDD_HHMMSS": "MVI_20200905_152850",
                "Day Month DD HH-MM-SS YYYY": "MVI_20200905_152850",
                "Foldername_Number": "MVI_20200905_152850",
            },
        ],
    },
    ###############################################################################################
    # Mon Sep 07 15-28-50 2020
    ###############################################################################################
    join("recursive", "Mon Sep 07 15-28-50 2020"): {
        "cases": [
            {  # Misc
                "folder": "misc",
                "name": 1,
                "jpg": True,
                "conditions": [
                    ("in_signature", "Metadata only"),
                    ("process_unmatched", True),
                ],
            },
            {  # None
                "folder": None,
                "name": None,
                "jpg": True,
                "conditions": [
                    ("process_unmatched", False),
                ],
            },
            {
                "folder": join("2020", "misc"),
                "name": 0,
                "jpg": True,
                "conditions": [],
            },
        ],
        "out": [
            {
                "YYYY-MM-DD_HH-MM-SS": "2020-09-07_15-28-50",
                "YYYY-MM-DD_HH-MM-SS.fff": "2020-09-07_15-28-50.000",
                "YYYYMMDD_HHMMSS": "20200907_152850",
                "IMG_YYYYMMDD_HHMMSS": "IMG_20200907_152850",
                "Day Month DD HH-MM-SS YYYY": "Mon Sep 07 15-28-50 2020",
                "Foldername_Number": "ERROR",
            },
            {
                "YYYY-MM-DD_HH-MM-SS": "Mon Sep 07 15-28-50 2020",
                "YYYY-MM-DD_HH-MM-SS.fff": "Mon Sep 07 15-28-50 2020",
                "YYYYMMDD_HHMMSS": "Mon Sep 07 15-28-50 2020",
                "IMG_YYYYMMDD_HHMMSS": "Mon Sep 07 15-28-50 2020",
                "Day Month DD HH-MM-SS YYYY": "Mon Sep 07 15-28-50 2020",
                "Foldername_Number": "Mon Sep 07 15-28-50 2020",
            },
        ],
    },
    ###############################################################################################
    # VID_20200906_152850
    ###############################################################################################
    join("recursive", "VID_20200906_152850"): {
        "cases": [
            {  # Misc
                "folder": "misc",
                "name": 1,
                "jpg": True,
                "conditions": [
                    ("in_signature", "Metadata only"),
                    ("process_unmatched", True),
                ],
            },
            {  # None
                "folder": None,
                "name": None,
                "jpg": True,
                "conditions": [
                    ("process_unmatched", False),
                ],
            },
            {
                "folder": join("2020", "misc"),
                "name": 0,
                "jpg": True,
                "conditions": [],
            },
        ],
        "out": [
            {
                "YYYY-MM-DD_HH-MM-SS": "2020-09-06_15-28-50",
                "YYYY-MM-DD_HH-MM-SS.fff": "2020-09-06_15-28-50.000",
                "YYYYMMDD_HHMMSS": "20200906_152850",
                "IMG_YYYYMMDD_HHMMSS": "IMG_20200906_152850",
                "Day Month DD HH-MM-SS YYYY": "Sun Sep 06 15-28-50 2020",
                "Foldername_Number": "ERROR",
            },
            {
                "YYYY-MM-DD_HH-MM-SS": "VID_20200906_152850",
                "YYYY-MM-DD_HH-MM-SS.fff": "VID_20200906_152850",
                "YYYYMMDD_HHMMSS": "VID_20200906_152850",
                "IMG_YYYYMMDD_HHMMSS": "VID_20200906_152850",
                "Day Month DD HH-MM-SS YYYY": "VID_20200906_152850",
                "Foldername_Number": "VID_20200906_152850",
            },
        ],
    },
    ###############################################################################################
    ###############################################################################################
    # _Number
    ###############################################################################################
    ###############################################################################################
    ###############################################################################################
    # 12-December-08_001_1
    ###############################################################################################
    join("_1", "12-December-08_001_1"): {
        "cases": [
            {  # None
                "folder": None,
                "name": None,
                "jpg": True,
                "conditions": [
                    ("process_unmatched", False),
                ],
            },
            {  # Misc
                "folder": "misc",
                "name": 1,
                "jpg": True,
                "conditions": [
                    ("in_signature", "Metadata only"),
                ],
            },
            {
                "folder": join("1900", "misc"),
                "name": 0,
                "jpg": True,
                "conditions": [],
            },
        ],
        "out": [
            {
                "YYYY-MM-DD_HH-MM-SS": "1900-12-08_00-00-00",
                "YYYY-MM-DD_HH-MM-SS.fff": "1900-12-08_00-00-00.001",
                "YYYYMMDD_HHMMSS": "19001208_000000",
                "IMG_YYYYMMDD_HHMMSS": "IMG_19001208_000000",
                "Day Month DD HH-MM-SS YYYY": "Sat Dec 08 00-00-00 1900",
                "Foldername_Number": "ERROR",
            },
            {
                "YYYY-MM-DD_HH-MM-SS": "12-December-08_001_1",
                "YYYY-MM-DD_HH-MM-SS.fff": "12-December-08_001_1",
                "YYYYMMDD_HHMMSS": "12-December-08_001_1",
                "IMG_YYYYMMDD_HHMMSS": "12-December-08_001_1",
                "Day Month DD HH-MM-SS YYYY": "12-December-08_001_1",
                "Foldername_Number": "12-December-08_001_1",
            },
        ],
    },
    ###############################################################################################
    # 2020_[12_09]_1
    ###############################################################################################
    join("_1", "2020_[12_09]_1"): {
        "cases": [
            {  # Misc
                "folder": "misc",
                "name": 1,
                "jpg": True,
                "conditions": [
                    ("in_signature", "Metadata only"),
                    ("process_unmatched", True),
                ],
            },
            {  # None
                "folder": None,
                "name": None,
                "jpg": True,
                "conditions": [
                    ("in_signature", "Metadata only"),
                ],
            },
            {
                "folder": join("2020", "2020_[12_01-12_31]_December"),
                "name": 0,
                "jpg": True,
                "conditions": [
                    ("require_artist", False),
                ],
            },
            {
                "folder": join("2020", join("2020_[12_01-12_31]_December", "no_artist")),
                "name": 0,
                "jpg": True,
                "conditions": [],
            },
        ],
        "out": [
            {
                "YYYY-MM-DD_HH-MM-SS": "2020-12-09_00-00-00",
                "YYYY-MM-DD_HH-MM-SS.fff": "2020-12-09_00-00-00.000",
                "YYYYMMDD_HHMMSS": "20201209_000000",
                "IMG_YYYYMMDD_HHMMSS": "IMG_20201209_000000",
                "Day Month DD HH-MM-SS YYYY": "Wed Dec 09 00-00-00 2020",
                "Foldername_Number": "ERROR",
            },
            {
                "YYYY-MM-DD_HH-MM-SS": "2020_[12_09]_1",
                "YYYY-MM-DD_HH-MM-SS.fff": "2020_[12_09]_1",
                "YYYYMMDD_HHMMSS": "2020_[12_09]_1",
                "IMG_YYYYMMDD_HHMMSS": "2020_[12_09]_1",
                "Day Month DD HH-MM-SS YYYY": "2020_[12_09]_1",
                "Foldername_Number": "2020_[12_09]_1",
            },
        ],
    },
    ###############################################################################################
    # 2020_[12_10-12_10]_1
    ###############################################################################################
    join("_1", "2020_[12_10-12_10]_1"): {
        "cases": [
            {  # Misc
                "folder": "misc",
                "name": 1,
                "jpg": True,
                "conditions": [
                    ("in_signature", "Metadata only"),
                    ("process_unmatched", True),
                ],
            },
            {  # None
                "folder": None,
                "name": None,
                "jpg": True,
                "conditions": [
                    ("in_signature", "Metadata only"),
                ],
            },
            {
                "folder": join("2020", "2020_[12_01-12_31]_December"),
                "name": 0,
                "jpg": True,
                "conditions": [
                    ("require_artist", False),
                ],
            },
            {
                "folder": join("2020", join("2020_[12_01-12_31]_December", "no_artist")),
                "name": 0,
                "jpg": True,
                "conditions": [],
            },
        ],
        "out": [
            {
                "YYYY-MM-DD_HH-MM-SS": "2020-12-10_00-00-00",
                "YYYY-MM-DD_HH-MM-SS.fff": "2020-12-10_00-00-00.000",
                "YYYYMMDD_HHMMSS": "20201210_000000",
                "IMG_YYYYMMDD_HHMMSS": "IMG_20201210_000000",
                "Day Month DD HH-MM-SS YYYY": "Thu Dec 10 00-00-00 2020",
                "Foldername_Number": "ERROR",
            },
            {
                "YYYY-MM-DD_HH-MM-SS": "2020_[12_10-12_10]_1",
                "YYYY-MM-DD_HH-MM-SS.fff": "2020_[12_10-12_10]_1",
                "YYYYMMDD_HHMMSS": "2020_[12_10-12_10]_1",
                "IMG_YYYYMMDD_HHMMSS": "2020_[12_10-12_10]_1",
                "Day Month DD HH-MM-SS YYYY": "2020_[12_10-12_10]_1",
                "Foldername_Number": "2020_[12_10-12_10]_1",
            },
        ],
    },
    ###############################################################################################
    # 2020-12-01_09-28-50_1
    ###############################################################################################
    join("_1", "2020-12-01_09-28-50_1"): {
        "cases": [
            {  # Misc
                "folder": "misc",
                "name": 1,
                "jpg": False,
                "conditions": [
                    ("in_signature", "Metadata only"),
                    ("process_unmatched", True),
                    ("process_samename", False),
                ],
            },
            {  # None
                "folder": None,
                "name": None,
                "jpg": False,
                "conditions": [
                    ("in_signature", "Metadata only"),
                    ("process_samename", False),
                ],
            },
            {
                "folder": join("2020", join("2020_[12_01-12_31]_December", "no_artist")),
                "name": 0,
                "jpg": False,
                "conditions": [
                    ("require_artist", True),
                    ("process_samename", False),
                ],
            },
            {
                "folder": join("2020", "2020_[12_01-12_31]_December"),
                "name": 0,
                "jpg": True,
                "conditions": [],
            },
        ],
        "out": [
            {
                "YYYY-MM-DD_HH-MM-SS": "2020-12-01_09-28-50",
                "YYYY-MM-DD_HH-MM-SS.fff": "2020-12-01_09-28-50.000",
                "YYYYMMDD_HHMMSS": "20201201_092850",
                "IMG_YYYYMMDD_HHMMSS": "IMG_20201201_092850",
                "Day Month DD HH-MM-SS YYYY": "Tue Dec 01 09-28-50 2020",
                "Foldername_Number": "ERROR",
            },
            {
                "YYYY-MM-DD_HH-MM-SS": "2020-12-01_09-28-50_1",
                "YYYY-MM-DD_HH-MM-SS.fff": "2020-12-01_09-28-50_1",
                "YYYYMMDD_HHMMSS": "2020-12-01_09-28-50_1",
                "IMG_YYYYMMDD_HHMMSS": "2020-12-01_09-28-50_1",
                "Day Month DD HH-MM-SS YYYY": "2020-12-01_09-28-50_1",
                "Foldername_Number": "2020-12-01_09-28-50_1",
            },
        ],
    },
    ###############################################################################################
    # 2020-12-02_09-28-50.000_1
    ###############################################################################################
    join("_1", "2020-12-02_09-28-50.000_1"): {
        "cases": [
            {  # Misc
                "folder": "misc",
                "name": 1,
                "jpg": False,
                "conditions": [
                    ("in_signature", "Metadata only"),
                    ("process_unmatched", True),
                    ("process_samename", False),
                ],
            },
            {  # None
                "folder": None,
                "name": None,
                "jpg": False,
                "conditions": [
                    ("in_signature", "Metadata only"),
                    ("process_samename", False),
                ],
            },
            {
                "folder": join("2020", join("2020_[12_01-12_31]_December", "no_artist")),
                "name": 0,
                "jpg": False,
                "conditions": [
                    ("require_artist", True),
                    ("process_samename", False),
                ],
            },
            {
                "folder": join("2020", "2020_[12_01-12_31]_December"),
                "name": 0,
                "jpg": True,
                "conditions": [],
            },
        ],
        "out": [
            {
                "YYYY-MM-DD_HH-MM-SS": "2020-12-02_09-28-50",
                "YYYY-MM-DD_HH-MM-SS.fff": "2020-12-02_09-28-50.000",
                "YYYYMMDD_HHMMSS": "20201202_092850",
                "IMG_YYYYMMDD_HHMMSS": "IMG_20201202_092850",
                "Day Month DD HH-MM-SS YYYY": "Wed Dec 02 09-28-50 2020",
                "Foldername_Number": "ERROR",
            },
            {
                "YYYY-MM-DD_HH-MM-SS": "2020-12-02_09-28-50.000_1",
                "YYYY-MM-DD_HH-MM-SS.fff": "2020-12-02_09-28-50.000_1",
                "YYYYMMDD_HHMMSS": "2020-12-02_09-28-50.000_1",
                "IMG_YYYYMMDD_HHMMSS": "2020-12-02_09-28-50.000_1",
                "Day Month DD HH-MM-SS YYYY": "2020-12-02_09-28-50.000_1",
                "Foldername_Number": "2020-12-02_09-28-50.000_1",
            },
        ],
    },
    ###############################################################################################
    # 20201203_092850_1
    ###############################################################################################
    join("_1", "20201203_092850_1"): {
        "cases": [
            {  # Misc
                "folder": "misc",
                "name": 1,
                "jpg": True,
                "conditions": [
                    ("in_signature", "Metadata only"),
                    ("process_unmatched", True),
                ],
            },
            {  # None
                "folder": None,
                "name": None,
                "jpg": True,
                "conditions": [
                    ("in_signature", "Metadata only"),
                ],
            },
            {
                "folder": join("2020", join("2020_[12_01-12_31]_December", "no_artist")),
                "name": 0,
                "jpg": False,
                "conditions": [
                    ("require_artist", True),
                    ("process_samename", False),
                ],
            },
            {
                "folder": join("2020", "2020_[12_01-12_31]_December"),
                "name": 0,
                "jpg": True,
                "conditions": [],
            },
        ],
        "out": [
            {
                "YYYY-MM-DD_HH-MM-SS": "2020-12-03_09-28-50",
                "YYYY-MM-DD_HH-MM-SS.fff": "2020-12-03_09-28-50.000",
                "YYYYMMDD_HHMMSS": "20201203_092850",
                "IMG_YYYYMMDD_HHMMSS": "IMG_20201203_092850",
                "Day Month DD HH-MM-SS YYYY": "Thu Dec 03 09-28-50 2020",
                "Foldername_Number": "ERROR",
            },
            {
                "YYYY-MM-DD_HH-MM-SS": "20201203_092850_1",
                "YYYY-MM-DD_HH-MM-SS.fff": "20201203_092850_1",
                "YYYYMMDD_HHMMSS": "20201203_092850_1",
                "IMG_YYYYMMDD_HHMMSS": "20201203_092850_1",
                "Day Month DD HH-MM-SS YYYY": "20201203_092850_1",
                "Foldername_Number": "20201203_092850_1",
            },
        ],
    },
    ###############################################################################################
    # gibberish1_1
    ###############################################################################################
    join("_1", "gibberish1_1"): {
        "cases": [
            {  # MISC
                "folder": "misc",
                "name": 0,
                "jpg": True,
                "conditions": [
                    ("process_unmatched", True),
                ],
            },
            {
                "folder": None,
                "name": None,
                "jpg": True,
                "conditions": [],
            },
        ],
        "out": [
            {
                "YYYY-MM-DD_HH-MM-SS": "gibberish1_1",
                "YYYY-MM-DD_HH-MM-SS.fff": "gibberish1_1",
                "YYYYMMDD_HHMMSS": "gibberish1_1",
                "IMG_YYYYMMDD_HHMMSS": "gibberish1_1",
                "Day Month DD HH-MM-SS YYYY": "gibberish1_1",
                "Foldername_Number": "gibberish1_1",
            },
        ],
    },
    ###############################################################################################
    # IMG_20201204_092850_1
    ###############################################################################################
    join("_1", "IMG_20201204_092850_1"): {
        "cases": [
            {  # Misc
                "folder": "misc",
                "name": 1,
                "jpg": True,
                "conditions": [
                    ("in_signature", "Metadata only"),
                    ("process_unmatched", True),
                ],
            },
            {  # None
                "folder": None,
                "name": None,
                "jpg": True,
                "conditions": [
                    ("in_signature", "Metadata only"),
                ],
            },
            {
                "folder": join("2020", join("2020_[12_01-12_31]_December", "no_artist")),
                "name": 0,
                "jpg": False,
                "conditions": [
                    ("require_artist", True),
                    ("process_samename", False),
                ],
            },
            {
                "folder": join("2020", "2020_[12_01-12_31]_December"),
                "name": 0,
                "jpg": True,
                "conditions": [],
            },
        ],
        "out": [
            {
                "YYYY-MM-DD_HH-MM-SS": "2020-12-04_09-28-50",
                "YYYY-MM-DD_HH-MM-SS.fff": "2020-12-04_09-28-50.000",
                "YYYYMMDD_HHMMSS": "20201204_092850",
                "IMG_YYYYMMDD_HHMMSS": "IMG_20201204_092850",
                "Day Month DD HH-MM-SS YYYY": "Fri Dec 04 09-28-50 2020",
                "Foldername_Number": "ERROR",
            },
            {
                "YYYY-MM-DD_HH-MM-SS": "IMG_20201204_092850_1",
                "YYYY-MM-DD_HH-MM-SS.fff": "IMG_20201204_092850_1",
                "YYYYMMDD_HHMMSS": "IMG_20201204_092850_1",
                "IMG_YYYYMMDD_HHMMSS": "IMG_20201204_092850_1",
                "Day Month DD HH-MM-SS YYYY": "IMG_20201204_092850_1",
                "Foldername_Number": "IMG_20201204_092850_1",
            },
        ],
    },
    ###############################################################################################
    # IMG_0010_1
    ###############################################################################################
    join("_1", "IMG_0010_1"): {
        "cases": [
            {  # Misc
                "folder": "misc",
                "name": 1,
                "jpg": False,
                "conditions": [
                    ("process_unmatched", True),
                    ("process_samename", False),
                ],
            },
            {  # Misc
                "folder": "misc",
                "name": 1,
                "jpg": True,
                "conditions": [
                    ("in_signature", "Filename only"),
                    ("process_unmatched", True),
                ],
            },
            {  # None
                "folder": None,
                "name": None,
                "jpg": False,
                "conditions": [
                    ("process_unmatched", False),
                ],
            },
            {  # None
                "folder": None,
                "name": None,
                "jpg": True,
                "conditions": [
                    ("in_signature", "Filename only"),
                    ("process_unmatched", False),
                ],
            },
            {
                "folder": join("2020", "2020_[12_01-12_31]_December"),
                "name": 0,
                "jpg": True,
                "conditions": [],
            },
        ],
        "out": [
            {
                "YYYY-MM-DD_HH-MM-SS": "2020-12-11_09-28-50",
                "YYYY-MM-DD_HH-MM-SS.fff": "2020-12-11_09-28-50.000",
                "YYYYMMDD_HHMMSS": "20201211_092850",
                "IMG_YYYYMMDD_HHMMSS": "IMG_20201211_092850",
                "Day Month DD HH-MM-SS YYYY": "Fri Dec 11 09-28-50 2020",
                "Foldername_Number": "ERROR",
            },
            {
                "YYYY-MM-DD_HH-MM-SS": "IMG_0010_1",
                "YYYY-MM-DD_HH-MM-SS.fff": "IMG_0010_1",
                "YYYYMMDD_HHMMSS": "IMG_0010_1",
                "IMG_YYYYMMDD_HHMMSS": "IMG_0010_1",
                "Day Month DD HH-MM-SS YYYY": "IMG_0010_1",
                "Foldername_Number": "IMG_0010_1",
            },
        ],
    },
    ###############################################################################################
    # MVI_20201205_092850_1
    ###############################################################################################
    join("_1", "MVI_20201205_092850_1"): {
        "cases": [
            {  # Misc
                "folder": "misc",
                "name": 1,
                "jpg": False,
                "conditions": [
                    ("in_signature", "Metadata only"),
                    ("process_unmatched", True),
                    ("process_samename", False),
                ],
            },
            {  # None
                "folder": None,
                "name": None,
                "jpg": False,
                "conditions": [
                    ("in_signature", "Metadata only"),
                    ("process_samename", False),
                ],
            },
            {
                "folder": join("2020", "2020_[12_01-12_31]_December"),
                "name": 0,
                "jpg": True,
                "conditions": [
                    ("require_artist", False),
                ],
            },
            {
                "folder": join("2020", join("2020_[12_01-12_31]_December", "no_artist")),
                "name": 0,
                "jpg": True,
                "conditions": [],
            },
        ],
        "out": [
            {
                "YYYY-MM-DD_HH-MM-SS": "2020-12-05_09-28-50",
                "YYYY-MM-DD_HH-MM-SS.fff": "2020-12-05_09-28-50.000",
                "YYYYMMDD_HHMMSS": "20201205_092850",
                "IMG_YYYYMMDD_HHMMSS": "IMG_20201205_092850",
                "Day Month DD HH-MM-SS YYYY": "Sat Dec 05 09-28-50 2020",
                "Foldername_Number": "ERROR",
            },
            {
                "YYYY-MM-DD_HH-MM-SS": "MVI_20201205_092850_1",
                "YYYY-MM-DD_HH-MM-SS.fff": "MVI_20201205_092850_1",
                "YYYYMMDD_HHMMSS": "MVI_20201205_092850_1",
                "IMG_YYYYMMDD_HHMMSS": "MVI_20201205_092850_1",
                "Day Month DD HH-MM-SS YYYY": "MVI_20201205_092850_1",
                "Foldername_Number": "MVI_20201205_092850_1",
            },
        ],
    },
    ###############################################################################################
    # Mon Dec 07 09-28-50 2020_1
    ###############################################################################################
    join("_1", "Mon Dec 07 09-28-50 2020_1"): {
        "cases": [
            {  # Misc
                "folder": "misc",
                "name": 1,
                "jpg": True,
                "conditions": [
                    ("in_signature", "Metadata only"),
                    ("process_unmatched", True),
                ],
            },
            {  # None
                "folder": None,
                "name": None,
                "jpg": True,
                "conditions": [
                    ("in_signature", "Metadata only"),
                ],
            },
            {
                "folder": join("2020", "2020_[12_01-12_31]_December"),
                "name": 0,
                "jpg": True,
                "conditions": [
                    ("require_artist", False),
                ],
            },
            {
                "folder": join("2020", join("2020_[12_01-12_31]_December", "no_artist")),
                "name": 0,
                "jpg": True,
                "conditions": [],
            },
        ],
        "out": [
            {
                "YYYY-MM-DD_HH-MM-SS": "2020-12-07_09-28-50",
                "YYYY-MM-DD_HH-MM-SS.fff": "2020-12-07_09-28-50.000",
                "YYYYMMDD_HHMMSS": "20201207_092850",
                "IMG_YYYYMMDD_HHMMSS": "IMG_20201207_092850",
                "Day Month DD HH-MM-SS YYYY": "Mon Dec 07 09-28-50 2020",
                "Foldername_Number": "ERROR",
            },
            {
                "YYYY-MM-DD_HH-MM-SS": "Mon Dec 07 09-28-50 2020_1",
                "YYYY-MM-DD_HH-MM-SS.fff": "Mon Dec 07 09-28-50 2020_1",
                "YYYYMMDD_HHMMSS": "Mon Dec 07 09-28-50 2020_1",
                "IMG_YYYYMMDD_HHMMSS": "Mon Dec 07 09-28-50 2020_1",
                "Day Month DD HH-MM-SS YYYY": "Mon Dec 07 09-28-50 2020_1",
                "Foldername_Number": "Mon Dec 07 09-28-50 2020_1",
            },
        ],
    },
    ###############################################################################################
    # VID_20201206_092850_1
    ###############################################################################################
    join("_1", "VID_20201206_092850_1"): {
        "cases": [
            {  # Misc
                "folder": "misc",
                "name": 1,
                "jpg": True,
                "conditions": [
                    ("in_signature", "Metadata only"),
                    ("process_unmatched", True),
                ],
            },
            {  # None
                "folder": None,
                "name": None,
                "jpg": True,
                "conditions": [
                    ("in_signature", "Metadata only"),
                ],
            },
            {
                "folder": join("2020", "2020_[12_01-12_31]_December"),
                "name": 0,
                "jpg": True,
                "conditions": [
                    ("require_artist", False),
                ],
            },
            {
                "folder": join("2020", join("2020_[12_01-12_31]_December", "no_artist")),
                "name": 0,
                "jpg": True,
                "conditions": [],
            },
        ],
        "out": [
            {
                "YYYY-MM-DD_HH-MM-SS": "2020-12-06_09-28-50",
                "YYYY-MM-DD_HH-MM-SS.fff": "2020-12-06_09-28-50.000",
                "YYYYMMDD_HHMMSS": "20201206_092850",
                "IMG_YYYYMMDD_HHMMSS": "IMG_20201206_092850",
                "Day Month DD HH-MM-SS YYYY": "Sun Dec 06 09-28-50 2020",
                "Foldername_Number": "ERROR",
            },
            {
                "YYYY-MM-DD_HH-MM-SS": "VID_20201206_092850_1",
                "YYYY-MM-DD_HH-MM-SS.fff": "VID_20201206_092850_1",
                "YYYYMMDD_HHMMSS": "VID_20201206_092850_1",
                "IMG_YYYYMMDD_HHMMSS": "VID_20201206_092850_1",
                "Day Month DD HH-MM-SS YYYY": "VID_20201206_092850_1",
                "Foldername_Number": "VID_20201206_092850_1",
            },
        ],
    },
    ###############################################################################################
    ###############################################################################################
    # - Copy
    ###############################################################################################
    ###############################################################################################
    ###############################################################################################
    # 08-August-08_001 - Copy
    ###############################################################################################
    join(" - Copy", "08-August-08_001 - Copy"): {
        "cases": [
            {  # None
                "folder": None,
                "name": None,
                "jpg": True,
                "conditions": [
                    ("process_unmatched", False),
                ],
            },
            {  # Misc
                "folder": "misc",
                "name": 1,
                "jpg": True,
                "conditions": [
                    ("in_signature", "Metadata only"),
                ],
            },
            {
                "folder": join("1900", "misc"),
                "name": 0,
                "jpg": True,
                "conditions": [],
            },
        ],
        "out": [
            {
                "YYYY-MM-DD_HH-MM-SS": "1900-08-08_00-00-00",
                "YYYY-MM-DD_HH-MM-SS.fff": "1900-08-08_00-00-00.001",
                "YYYYMMDD_HHMMSS": "19000808_000000",
                "IMG_YYYYMMDD_HHMMSS": "IMG_19000808_000000",
                "Day Month DD HH-MM-SS YYYY": "Wed Aug 08 00-00-00 1900",
                "Foldername_Number": "ERROR",
            },
            {
                "YYYY-MM-DD_HH-MM-SS": "08-August-08_001 - Copy",
                "YYYY-MM-DD_HH-MM-SS.fff": "08-August-08_001 - Copy",
                "YYYYMMDD_HHMMSS": "08-August-08_001 - Copy",
                "IMG_YYYYMMDD_HHMMSS": "08-August-08_001 - Copy",
                "Day Month DD HH-MM-SS YYYY": "08-August-08_001 - Copy",
                "Foldername_Number": "08-August-08_001 - Copy",
            },
        ],
    },
    ###############################################################################################
    # 2022_[08_09] - Copy
    ###############################################################################################
    join(" - Copy", "2022_[08_09] - Copy"): {
        "cases": [
            {  # Misc
                "folder": "misc",
                "name": 1,
                "jpg": True,
                "conditions": [
                    ("in_signature", "Metadata only"),
                    ("process_unmatched", True),
                ],
            },
            {  # None
                "folder": None,
                "name": None,
                "jpg": True,
                "conditions": [
                    ("in_signature", "Metadata only"),
                ],
            },
            {
                "folder": join("2022", "2022_[08_01-08_31]_August"),
                "name": 0,
                "jpg": True,
                "conditions": [
                    ("require_artist", False),
                ],
            },
            {
                "folder": join("2022", join("2022_[08_01-08_31]_August", "no_artist")),
                "name": 0,
                "jpg": True,
                "conditions": [],
            },
        ],
        "out": [
            {
                "YYYY-MM-DD_HH-MM-SS": "2022-08-09_00-00-00",
                "YYYY-MM-DD_HH-MM-SS.fff": "2022-08-09_00-00-00.000",
                "YYYYMMDD_HHMMSS": "20220809_000000",
                "IMG_YYYYMMDD_HHMMSS": "IMG_20220809_000000",
                "Day Month DD HH-MM-SS YYYY": "Tue Aug 09 00-00-00 2022",
                "Foldername_Number": "ERROR",
            },
            {
                "YYYY-MM-DD_HH-MM-SS": "2022_[08_09] - Copy",
                "YYYY-MM-DD_HH-MM-SS.fff": "2022_[08_09] - Copy",
                "YYYYMMDD_HHMMSS": "2022_[08_09] - Copy",
                "IMG_YYYYMMDD_HHMMSS": "2022_[08_09] - Copy",
                "Day Month DD HH-MM-SS YYYY": "2022_[08_09] - Copy",
                "Foldername_Number": "2022_[08_09] - Copy",
            },
        ],
    },
    ###############################################################################################
    # 2022_[08_10-08_10] - Copy
    ###############################################################################################
    join(" - Copy", "2022_[08_10-08_10] - Copy"): {
        "cases": [
            {  # Misc
                "folder": "misc",
                "name": 1,
                "jpg": True,
                "conditions": [
                    ("in_signature", "Metadata only"),
                    ("process_unmatched", True),
                ],
            },
            {  # None
                "folder": None,
                "name": None,
                "jpg": True,
                "conditions": [
                    ("in_signature", "Metadata only"),
                ],
            },
            {
                "folder": join("2022", "2022_[08_01-08_31]_August"),
                "name": 0,
                "jpg": True,
                "conditions": [
                    ("require_artist", False),
                ],
            },
            {
                "folder": join("2022", join("2022_[08_01-08_31]_August", "no_artist")),
                "name": 0,
                "jpg": True,
                "conditions": [],
            },
        ],
        "out": [
            {
                "YYYY-MM-DD_HH-MM-SS": "2022-08-10_00-00-00",
                "YYYY-MM-DD_HH-MM-SS.fff": "2022-08-10_00-00-00.000",
                "YYYYMMDD_HHMMSS": "20220810_000000",
                "IMG_YYYYMMDD_HHMMSS": "IMG_20220810_000000",
                "Day Month DD HH-MM-SS YYYY": "Wed Aug 10 00-00-00 2022",
                "Foldername_Number": "ERROR",
            },
            {
                "YYYY-MM-DD_HH-MM-SS": "2022_[08_10-08_10] - Copy",
                "YYYY-MM-DD_HH-MM-SS.fff": "2022_[08_10-08_10] - Copy",
                "YYYYMMDD_HHMMSS": "2022_[08_10-08_10] - Copy",
                "IMG_YYYYMMDD_HHMMSS": "2022_[08_10-08_10] - Copy",
                "Day Month DD HH-MM-SS YYYY": "2022_[08_10-08_10] - Copy",
                "Foldername_Number": "2022_[08_10-08_10] - Copy",
            },
        ],
    },
    ###############################################################################################
    # 2022-08-01_09-28-50 - Copy
    ###############################################################################################
    join(" - Copy", "2022-08-01_09-28-50 - Copy"): {
        "cases": [
            {  # Misc
                "folder": "misc",
                "name": 1,
                "jpg": False,
                "conditions": [
                    ("in_signature", "Metadata only"),
                    ("process_unmatched", True),
                    ("process_samename", False),
                ],
            },
            {  # None
                "folder": None,
                "name": None,
                "jpg": False,
                "conditions": [
                    ("in_signature", "Metadata only"),
                    ("process_samename", False),
                ],
            },
            {
                "folder": join("2022", "2022_[08_01-08_31]_August"),
                "name": 0,
                "jpg": True,
                "conditions": [
                    ("require_artist", False),
                ],
            },
            {
                "folder": join("2022", join("2022_[08_01-08_31]_August", "no_artist")),
                "name": 0,
                "jpg": True,
                "conditions": [],
            },
        ],
        "out": [
            {
                "YYYY-MM-DD_HH-MM-SS": "2022-08-01_09-28-50",
                "YYYY-MM-DD_HH-MM-SS.fff": "2022-08-01_09-28-50.000",
                "YYYYMMDD_HHMMSS": "20220801_092850",
                "IMG_YYYYMMDD_HHMMSS": "IMG_20220801_092850",
                "Day Month DD HH-MM-SS YYYY": "Mon Aug 01 09-28-50 2022",
                "Foldername_Number": "ERROR",
            },
            {
                "YYYY-MM-DD_HH-MM-SS": "2022-08-01_09-28-50 - Copy",
                "YYYY-MM-DD_HH-MM-SS.fff": "2022-08-01_09-28-50 - Copy",
                "YYYYMMDD_HHMMSS": "2022-08-01_09-28-50 - Copy",
                "IMG_YYYYMMDD_HHMMSS": "2022-08-01_09-28-50 - Copy",
                "Day Month DD HH-MM-SS YYYY": "2022-08-01_09-28-50 - Copy",
                "Foldername_Number": "2022-08-01_09-28-50 - Copy",
            },
        ],
    },
    ###############################################################################################
    # 2022-08-02_09-28-50.000 - Copy
    ###############################################################################################
    join(" - Copy", "2022-08-02_09-28-50.000 - Copy"): {
        "cases": [
            {  # Misc
                "folder": "misc",
                "name": 1,
                "jpg": False,
                "conditions": [
                    ("in_signature", "Metadata only"),
                    ("process_unmatched", True),
                    ("process_samename", False),
                ],
            },
            {  # None
                "folder": None,
                "name": None,
                "jpg": False,
                "conditions": [
                    ("in_signature", "Metadata only"),
                    ("process_samename", False),
                ],
            },
            {
                "folder": join("2022", "2022_[08_01-08_31]_August"),
                "name": 0,
                "jpg": True,
                "conditions": [
                    ("require_artist", False),
                ],
            },
            {
                "folder": join("2022", join("2022_[08_01-08_31]_August", "no_artist")),
                "name": 0,
                "jpg": True,
                "conditions": [],
            },
        ],
        "out": [
            {
                "YYYY-MM-DD_HH-MM-SS": "2022-08-02_09-28-50",
                "YYYY-MM-DD_HH-MM-SS.fff": "2022-08-02_09-28-50.000",
                "YYYYMMDD_HHMMSS": "20220802_092850",
                "IMG_YYYYMMDD_HHMMSS": "IMG_20220802_092850",
                "Day Month DD HH-MM-SS YYYY": "Tue Aug 02 09-28-50 2022",
                "Foldername_Number": "ERROR",
            },
            {
                "YYYY-MM-DD_HH-MM-SS": "2022-08-02_09-28-50.000 - Copy",
                "YYYY-MM-DD_HH-MM-SS.fff": "2022-08-02_09-28-50.000 - Copy",
                "YYYYMMDD_HHMMSS": "2022-08-02_09-28-50.000 - Copy",
                "IMG_YYYYMMDD_HHMMSS": "2022-08-02_09-28-50.000 - Copy",
                "Day Month DD HH-MM-SS YYYY": "2022-08-02_09-28-50.000 - Copy",
                "Foldername_Number": "2022-08-02_09-28-50.000 - Copy",
            },
        ],
    },
    ###############################################################################################
    # 20220803_092850 - Copy
    ###############################################################################################
    join(" - Copy", "20220803_092850 - Copy"): {
        "cases": [
            {  # Misc
                "folder": "misc",
                "name": 1,
                "jpg": True,
                "conditions": [
                    ("in_signature", "Metadata only"),
                    ("process_unmatched", True),
                ],
            },
            {  # None
                "folder": None,
                "name": None,
                "jpg": True,
                "conditions": [
                    ("in_signature", "Metadata only"),
                ],
            },
            {
                "folder": join("2022", "2022_[08_01-08_31]_August"),
                "name": 0,
                "jpg": True,
                "conditions": [
                    ("require_artist", False),
                ],
            },
            {
                "folder": join("2022", join("2022_[08_01-08_31]_August", "no_artist")),
                "name": 0,
                "jpg": True,
                "conditions": [],
            },
        ],
        "out": [
            {
                "YYYY-MM-DD_HH-MM-SS": "2022-08-03_09-28-50",
                "YYYY-MM-DD_HH-MM-SS.fff": "2022-08-03_09-28-50.000",
                "YYYYMMDD_HHMMSS": "20220803_092850",
                "IMG_YYYYMMDD_HHMMSS": "IMG_20220803_092850",
                "Day Month DD HH-MM-SS YYYY": "Wed Aug 03 09-28-50 2022",
                "Foldername_Number": "ERROR",
            },
            {
                "YYYY-MM-DD_HH-MM-SS": "20220803_092850 - Copy",
                "YYYY-MM-DD_HH-MM-SS.fff": "20220803_092850 - Copy",
                "YYYYMMDD_HHMMSS": "20220803_092850 - Copy",
                "IMG_YYYYMMDD_HHMMSS": "20220803_092850 - Copy",
                "Day Month DD HH-MM-SS YYYY": "20220803_092850 - Copy",
                "Foldername_Number": "20220803_092850 - Copy",
            },
        ],
    },
    ###############################################################################################
    # gibberish4 - Copy
    ###############################################################################################
    join(" - Copy", "gibberish4 - Copy"): {
        "cases": [
            {  # MISC
                "folder": "misc",
                "name": 0,
                "jpg": True,
                "conditions": [
                    ("process_unmatched", True),
                ],
            },
            {
                "folder": None,
                "name": None,
                "jpg": True,
                "conditions": [],
            },
        ],
        "out": [
            {
                "YYYY-MM-DD_HH-MM-SS": "gibberish4 - Copy",
                "YYYY-MM-DD_HH-MM-SS.fff": "gibberish4 - Copy",
                "YYYYMMDD_HHMMSS": "gibberish4 - Copy",
                "IMG_YYYYMMDD_HHMMSS": "gibberish4 - Copy",
                "Day Month DD HH-MM-SS YYYY": "gibberish4 - Copy",
                "Foldername_Number": "gibberish4 - Copy",
            },
        ],
    },
    ###############################################################################################
    # IMG_20220804_092850 - Copy
    ###############################################################################################
    join(" - Copy", "IMG_20220804_092850 - Copy"): {
        "cases": [
            {  # Misc
                "folder": "misc",
                "name": 1,
                "jpg": True,
                "conditions": [
                    ("in_signature", "Metadata only"),
                    ("process_unmatched", True),
                ],
            },
            {  # None
                "folder": None,
                "name": None,
                "jpg": True,
                "conditions": [
                    ("in_signature", "Metadata only"),
                ],
            },
            {
                "folder": join("2022", "2022_[08_01-08_31]_August"),
                "name": 0,
                "jpg": True,
                "conditions": [
                    ("require_artist", False),
                ],
            },
            {
                "folder": join("2022", join("2022_[08_01-08_31]_August", "no_artist")),
                "name": 0,
                "jpg": True,
                "conditions": [],
            },
        ],
        "out": [
            {
                "YYYY-MM-DD_HH-MM-SS": "2022-08-04_09-28-50",
                "YYYY-MM-DD_HH-MM-SS.fff": "2022-08-04_09-28-50.000",
                "YYYYMMDD_HHMMSS": "20220804_092850",
                "IMG_YYYYMMDD_HHMMSS": "IMG_20220804_092850",
                "Day Month DD HH-MM-SS YYYY": "Thu Aug 04 09-28-50 2022",
                "Foldername_Number": "ERROR",
            },
            {
                "YYYY-MM-DD_HH-MM-SS": "IMG_20220804_092850 - Copy",
                "YYYY-MM-DD_HH-MM-SS.fff": "IMG_20220804_092850 - Copy",
                "YYYYMMDD_HHMMSS": "IMG_20220804_092850 - Copy",
                "IMG_YYYYMMDD_HHMMSS": "IMG_20220804_092850 - Copy",
                "Day Month DD HH-MM-SS YYYY": "IMG_20220804_092850 - Copy",
                "Foldername_Number": "IMG_20220804_092850 - Copy",
            },
        ],
    },
    ###############################################################################################
    # IMG_0040 - Copy
    ###############################################################################################
    join(" - Copy", "IMG_0040 - Copy"): {
        "cases": [
            {  # Misc
                "folder": "misc",
                "name": 1,
                "jpg": False,
                "conditions": [
                    ("process_unmatched", True),
                    ("process_samename", False),
                ],
            },
            {  # Misc
                "folder": "misc",
                "name": 1,
                "jpg": True,
                "conditions": [
                    ("in_signature", "Filename only"),
                    ("process_unmatched", True),
                ],
            },
            {  # None
                "folder": None,
                "name": None,
                "jpg": False,
                "conditions": [
                    ("process_unmatched", False),
                    ("process_samename", False),
                ],
            },
            {  # None
                "folder": None,
                "name": None,
                "jpg": True,
                "conditions": [
                    ("in_signature", "Filename only"),
                    ("process_unmatched", False),
                ],
            },
            {
                "folder": join("2022", "2022_[08_01-08_31]_August"),
                "name": 0,
                "jpg": True,
                "conditions": [
                    ("require_artist", False),
                ],
            },
            {
                "folder": join("2022", join("2022_[08_01-08_31]_August", "no_artist")),
                "name": 0,
                "jpg": True,
                "conditions": [],
            },
        ],
        "out": [
            {
                "YYYY-MM-DD_HH-MM-SS": "2022-08-11_09-28-50",
                "YYYY-MM-DD_HH-MM-SS.fff": "2022-08-11_09-28-50.000",
                "YYYYMMDD_HHMMSS": "20220811_092850",
                "IMG_YYYYMMDD_HHMMSS": "IMG_20220811_092850",
                "Day Month DD HH-MM-SS YYYY": "Thu Aug 11 09-28-50 2022",
                "Foldername_Number": "ERROR",
            },
            {
                "YYYY-MM-DD_HH-MM-SS": "IMG_0040 - Copy",
                "YYYY-MM-DD_HH-MM-SS.fff": "IMG_0040 - Copy",
                "YYYYMMDD_HHMMSS": "IMG_0040 - Copy",
                "IMG_YYYYMMDD_HHMMSS": "IMG_0040 - Copy",
                "Day Month DD HH-MM-SS YYYY": "IMG_0040 - Copy",
                "Foldername_Number": "IMG_0040 - Copy",
            },
        ],
    },
    ###############################################################################################
    # MVI_20220805_092850 - Copy
    ###############################################################################################
    join(" - Copy", "MVI_20220805_092850 - Copy"): {
        "cases": [
            {  # Misc
                "folder": "misc",
                "name": 1,
                "jpg": False,
                "conditions": [
                    ("in_signature", "Metadata only"),
                    ("process_unmatched", True),
                    ("process_samename", False),
                ],
            },
            {  # None
                "folder": None,
                "name": None,
                "jpg": False,
                "conditions": [
                    ("in_signature", "Metadata only"),
                    ("process_samename", False),
                ],
            },
            {
                "folder": join("2022", "2022_[08_01-08_31]_August"),
                "name": 0,
                "jpg": True,
                "conditions": [
                    ("require_artist", False),
                ],
            },
            {
                "folder": join("2022", join("2022_[08_01-08_31]_August", "no_artist")),
                "name": 0,
                "jpg": True,
                "conditions": [],
            },
        ],
        "out": [
            {
                "YYYY-MM-DD_HH-MM-SS": "2022-08-05_09-28-50",
                "YYYY-MM-DD_HH-MM-SS.fff": "2022-08-05_09-28-50.000",
                "YYYYMMDD_HHMMSS": "20220805_092850",
                "IMG_YYYYMMDD_HHMMSS": "IMG_20220805_092850",
                "Day Month DD HH-MM-SS YYYY": "Fri Aug 05 09-28-50 2022",
                "Foldername_Number": "ERROR",
            },
            {
                "YYYY-MM-DD_HH-MM-SS": "MVI_20220805_092850 - Copy",
                "YYYY-MM-DD_HH-MM-SS.fff": "MVI_20220805_092850 - Copy",
                "YYYYMMDD_HHMMSS": "MVI_20220805_092850 - Copy",
                "IMG_YYYYMMDD_HHMMSS": "MVI_20220805_092850 - Copy",
                "Day Month DD HH-MM-SS YYYY": "MVI_20220805_092850 - Copy",
                "Foldername_Number": "MVI_20220805_092850 - Copy",
            },
        ],
    },
    ###############################################################################################
    # Sun Aug 07 09-28-50 2022 - Copy
    ###############################################################################################
    join(" - Copy", "Sun Aug 07 09-28-50 2022 - Copy"): {
        "cases": [
            {  # Misc
                "folder": "misc",
                "name": 1,
                "jpg": True,
                "conditions": [
                    ("in_signature", "Metadata only"),
                    ("process_unmatched", True),
                ],
            },
            {  # None
                "folder": None,
                "name": None,
                "jpg": True,
                "conditions": [
                    ("in_signature", "Metadata only"),
                ],
            },
            {
                "folder": join("2022", "2022_[08_01-08_31]_August"),
                "name": 0,
                "jpg": True,
                "conditions": [
                    ("require_artist", False),
                ],
            },
            {
                "folder": join("2022", join("2022_[08_01-08_31]_August", "no_artist")),
                "name": 0,
                "jpg": True,
                "conditions": [],
            },
        ],
        "out": [
            {
                "YYYY-MM-DD_HH-MM-SS": "2022-08-07_09-28-50",
                "YYYY-MM-DD_HH-MM-SS.fff": "2022-08-07_09-28-50.000",
                "YYYYMMDD_HHMMSS": "20220807_092850",
                "IMG_YYYYMMDD_HHMMSS": "IMG_20220807_092850",
                "Day Month DD HH-MM-SS YYYY": "Sun Aug 07 09-28-50 2022",
                "Foldername_Number": "ERROR",
            },
            {
                "YYYY-MM-DD_HH-MM-SS": "Sun Aug 07 09-28-50 2022 - Copy",
                "YYYY-MM-DD_HH-MM-SS.fff": "Sun Aug 07 09-28-50 2022 - Copy",
                "YYYYMMDD_HHMMSS": "Sun Aug 07 09-28-50 2022 - Copy",
                "IMG_YYYYMMDD_HHMMSS": "Sun Aug 07 09-28-50 2022 - Copy",
                "Day Month DD HH-MM-SS YYYY": "Sun Aug 07 09-28-50 2022 - Copy",
                "Foldername_Number": "Sun Aug 07 09-28-50 2022 - Copy",
            },
        ],
    },
    ###############################################################################################
    # VID_20220806_092850 - Copy
    ###############################################################################################
    join(" - Copy", "VID_20220806_092850 - Copy"): {
        "cases": [
            {  # Misc
                "folder": "misc",
                "name": 1,
                "jpg": True,
                "conditions": [
                    ("in_signature", "Metadata only"),
                    ("process_unmatched", True),
                ],
            },
            {  # None
                "folder": None,
                "name": None,
                "jpg": True,
                "conditions": [
                    ("in_signature", "Metadata only"),
                ],
            },
            {
                "folder": join("2022", "2022_[08_01-08_31]_August"),
                "name": 0,
                "jpg": True,
                "conditions": [
                    ("require_artist", False),
                ],
            },
            {
                "folder": join("2022", join("2022_[08_01-08_31]_August", "no_artist")),
                "name": 0,
                "jpg": True,
                "conditions": [],
            },
        ],
        "out": [
            {
                "YYYY-MM-DD_HH-MM-SS": "2022-08-06_09-28-50",
                "YYYY-MM-DD_HH-MM-SS.fff": "2022-08-06_09-28-50.000",
                "YYYYMMDD_HHMMSS": "20220806_092850",
                "IMG_YYYYMMDD_HHMMSS": "IMG_20220806_092850",
                "Day Month DD HH-MM-SS YYYY": "Sat Aug 06 09-28-50 2022",
                "Foldername_Number": "ERROR",
            },
            {
                "YYYY-MM-DD_HH-MM-SS": "VID_20220806_092850 - Copy",
                "YYYY-MM-DD_HH-MM-SS.fff": "VID_20220806_092850 - Copy",
                "YYYYMMDD_HHMMSS": "VID_20220806_092850 - Copy",
                "IMG_YYYYMMDD_HHMMSS": "VID_20220806_092850 - Copy",
                "Day Month DD HH-MM-SS YYYY": "VID_20220806_092850 - Copy",
                "Foldername_Number": "VID_20220806_092850 - Copy",
            },
        ],
    },
    ###############################################################################################
    ###############################################################################################
    # (2)
    ###############################################################################################
    ###############################################################################################
    ###############################################################################################
    # 11-November-08_001 (2)
    ###############################################################################################
    join("(2)", "11-November-08_001 (2)"): {
        "cases": [
            {  # None
                "folder": None,
                "name": None,
                "jpg": True,
                "conditions": [
                    ("process_unmatched", False),
                ],
            },
            {  # Misc
                "folder": "misc",
                "name": 1,
                "jpg": True,
                "conditions": [
                    ("in_signature", "Metadata only"),
                ],
            },
            {
                "folder": join("1900", "misc"),
                "name": 0,
                "jpg": True,
                "conditions": [],
            },
        ],
        "out": [
            {
                "YYYY-MM-DD_HH-MM-SS": "1900-11-08_00-00-00",
                "YYYY-MM-DD_HH-MM-SS.fff": "1900-11-08_00-00-00.001",
                "YYYYMMDD_HHMMSS": "19001108_000000",
                "IMG_YYYYMMDD_HHMMSS": "IMG_19001108_000000",
                "Day Month DD HH-MM-SS YYYY": "Thu Nov 08 00-00-00 1900",
                "Foldername_Number": "ERROR",
            },
            {
                "YYYY-MM-DD_HH-MM-SS": "11-November-08_001 (2)",
                "YYYY-MM-DD_HH-MM-SS.fff": "11-November-08_001 (2)",
                "YYYYMMDD_HHMMSS": "11-November-08_001 (2)",
                "IMG_YYYYMMDD_HHMMSS": "11-November-08_001 (2)",
                "Day Month DD HH-MM-SS YYYY": "11-November-08_001 (2)",
                "Foldername_Number": "11-November-08_001 (2)",
            },
        ],
    },
    ###############################################################################################
    # 2021_[11_09] (2)
    ###############################################################################################
    join("(2)", "2021_[11_09] (2)"): {
        "cases": [
            {  # Misc
                "folder": "misc",
                "name": 1,
                "jpg": True,
                "conditions": [
                    ("in_signature", "Metadata only"),
                    ("process_unmatched", True),
                ],
            },
            {  # None
                "folder": None,
                "name": None,
                "jpg": True,
                "conditions": [
                    ("in_signature", "Metadata only"),
                ],
            },
            {
                "folder": join("2021", "2021_[11_01-11_30]_November"),
                "name": 0,
                "jpg": True,
                "conditions": [
                    ("require_artist", False),
                ],
            },
            {
                "folder": join("2021", join("2021_[11_01-11_30]_November", "no_artist")),
                "name": 0,
                "jpg": True,
                "conditions": [],
            },
        ],
        "out": [
            {
                "YYYY-MM-DD_HH-MM-SS": "2021-11-09_00-00-00",
                "YYYY-MM-DD_HH-MM-SS.fff": "2021-11-09_00-00-00.000",
                "YYYYMMDD_HHMMSS": "20211109_000000",
                "IMG_YYYYMMDD_HHMMSS": "IMG_20211109_000000",
                "Day Month DD HH-MM-SS YYYY": "Tue Nov 09 00-00-00 2021",
                "Foldername_Number": "ERROR",
            },
            {
                "YYYY-MM-DD_HH-MM-SS": "2021_[11_09] (2)",
                "YYYY-MM-DD_HH-MM-SS.fff": "2021_[11_09] (2)",
                "YYYYMMDD_HHMMSS": "2021_[11_09] (2)",
                "IMG_YYYYMMDD_HHMMSS": "2021_[11_09] (2)",
                "Day Month DD HH-MM-SS YYYY": "2021_[11_09] (2)",
                "Foldername_Number": "2021_[11_09] (2)",
            },
        ],
    },
    ###############################################################################################
    # 2021_[11_10-11_10] (2)
    ###############################################################################################
    join("(2)", "2021_[11_10-11_10] (2)"): {
        "cases": [
            {  # Misc
                "folder": "misc",
                "name": 1,
                "jpg": True,
                "conditions": [
                    ("in_signature", "Metadata only"),
                    ("process_unmatched", True),
                ],
            },
            {  # None
                "folder": None,
                "name": None,
                "jpg": True,
                "conditions": [
                    ("in_signature", "Metadata only"),
                ],
            },
            {
                "folder": join("2021", "2021_[11_01-11_30]_November"),
                "name": 0,
                "jpg": True,
                "conditions": [
                    ("require_artist", False),
                ],
            },
            {
                "folder": join("2021", join("2021_[11_01-11_30]_November", "no_artist")),
                "name": 0,
                "jpg": True,
                "conditions": [],
            },
        ],
        "out": [
            {
                "YYYY-MM-DD_HH-MM-SS": "2021-11-10_00-00-00",
                "YYYY-MM-DD_HH-MM-SS.fff": "2021-11-10_00-00-00.000",
                "YYYYMMDD_HHMMSS": "20211110_000000",
                "IMG_YYYYMMDD_HHMMSS": "IMG_20211110_000000",
                "Day Month DD HH-MM-SS YYYY": "Wed Nov 10 00-00-00 2021",
                "Foldername_Number": "ERROR",
            },
            {
                "YYYY-MM-DD_HH-MM-SS": "2021_[11_10-11_10] (2)",
                "YYYY-MM-DD_HH-MM-SS.fff": "2021_[11_10-11_10] (2)",
                "YYYYMMDD_HHMMSS": "2021_[11_10-11_10] (2)",
                "IMG_YYYYMMDD_HHMMSS": "2021_[11_10-11_10] (2)",
                "Day Month DD HH-MM-SS YYYY": "2021_[11_10-11_10] (2)",
                "Foldername_Number": "2021_[11_10-11_10] (2)",
            },
        ],
    },
    ###############################################################################################
    # 2021-11-01_09-28-50 (2)
    ###############################################################################################
    join("(2)", "2021-11-01_09-28-50 (2)"): {
        "cases": [
            {  # Misc
                "folder": "misc",
                "name": 1,
                "jpg": False,
                "conditions": [
                    ("in_signature", "Metadata only"),
                    ("process_unmatched", True),
                    ("process_samename", False),
                ],
            },
            {  # None
                "folder": None,
                "name": None,
                "jpg": False,
                "conditions": [
                    ("in_signature", "Metadata only"),
                    ("process_samename", False),
                ],
            },
            {
                "folder": join("2021", "2021_[11_01-11_30]_November"),
                "name": 0,
                "jpg": True,
                "conditions": [
                    ("require_artist", False),
                ],
            },
            {
                "folder": join("2021", join("2021_[11_01-11_30]_November", "no_artist")),
                "name": 0,
                "jpg": True,
                "conditions": [],
            },
        ],
        "out": [
            {
                "YYYY-MM-DD_HH-MM-SS": "2021-11-01_09-28-50",
                "YYYY-MM-DD_HH-MM-SS.fff": "2021-11-01_09-28-50.000",
                "YYYYMMDD_HHMMSS": "20211101_092850",
                "IMG_YYYYMMDD_HHMMSS": "IMG_20211101_092850",
                "Day Month DD HH-MM-SS YYYY": "Mon Nov 01 09-28-50 2021",
                "Foldername_Number": "ERROR",
            },
            {
                "YYYY-MM-DD_HH-MM-SS": "2021-11-01_09-28-50 (2)",
                "YYYY-MM-DD_HH-MM-SS.fff": "2021-11-01_09-28-50 (2)",
                "YYYYMMDD_HHMMSS": "2021-11-01_09-28-50 (2)",
                "IMG_YYYYMMDD_HHMMSS": "2021-11-01_09-28-50 (2)",
                "Day Month DD HH-MM-SS YYYY": "2021-11-01_09-28-50 (2)",
                "Foldername_Number": "2021-11-01_09-28-50 (2)",
            },
        ],
    },
    ###############################################################################################
    # 2021-11-02_09-28-50.000 (2)
    ###############################################################################################
    join("(2)", "2021-11-02_09-28-50.000 (2)"): {
        "cases": [
            {  # Misc
                "folder": "misc",
                "name": 1,
                "jpg": False,
                "conditions": [
                    ("in_signature", "Metadata only"),
                    ("process_unmatched", True),
                    ("process_samename", False),
                ],
            },
            {  # None
                "folder": None,
                "name": None,
                "jpg": False,
                "conditions": [
                    ("in_signature", "Metadata only"),
                    ("process_samename", False),
                ],
            },
            {
                "folder": join("2021", "2021_[11_01-11_30]_November"),
                "name": 0,
                "jpg": True,
                "conditions": [
                    ("require_artist", False),
                ],
            },
            {
                "folder": join("2021", join("2021_[11_01-11_30]_November", "no_artist")),
                "name": 0,
                "jpg": True,
                "conditions": [],
            },
        ],
        "out": [
            {
                "YYYY-MM-DD_HH-MM-SS": "2021-11-02_09-28-50",
                "YYYY-MM-DD_HH-MM-SS.fff": "2021-11-02_09-28-50.000",
                "YYYYMMDD_HHMMSS": "20211102_092850",
                "IMG_YYYYMMDD_HHMMSS": "IMG_20211102_092850",
                "Day Month DD HH-MM-SS YYYY": "Tue Nov 02 09-28-50 2021",
                "Foldername_Number": "ERROR",
            },
            {
                "YYYY-MM-DD_HH-MM-SS": "2021-11-02_09-28-50.000 (2)",
                "YYYY-MM-DD_HH-MM-SS.fff": "2021-11-02_09-28-50.000 (2)",
                "YYYYMMDD_HHMMSS": "2021-11-02_09-28-50.000 (2)",
                "IMG_YYYYMMDD_HHMMSS": "2021-11-02_09-28-50.000 (2)",
                "Day Month DD HH-MM-SS YYYY": "2021-11-02_09-28-50.000 (2)",
                "Foldername_Number": "2021-11-02_09-28-50.000 (2)",
            },
        ],
    },
    ###############################################################################################
    # 20211103_092850 (2)
    ###############################################################################################
    join("(2)", "20211103_092850 (2)"): {
        "cases": [
            {  # Misc
                "folder": "misc",
                "name": 1,
                "jpg": True,
                "conditions": [
                    ("in_signature", "Metadata only"),
                    ("process_unmatched", True),
                ],
            },
            {  # None
                "folder": None,
                "name": None,
                "jpg": True,
                "conditions": [
                    ("in_signature", "Metadata only"),
                ],
            },
            {
                "folder": join("2021", "2021_[11_01-11_30]_November"),
                "name": 0,
                "jpg": True,
                "conditions": [
                    ("require_artist", False),
                ],
            },
            {
                "folder": join("2021", join("2021_[11_01-11_30]_November", "no_artist")),
                "name": 0,
                "jpg": True,
                "conditions": [],
            },
        ],
        "out": [
            {
                "YYYY-MM-DD_HH-MM-SS": "2021-11-03_09-28-50",
                "YYYY-MM-DD_HH-MM-SS.fff": "2021-11-03_09-28-50.000",
                "YYYYMMDD_HHMMSS": "20211103_092850",
                "IMG_YYYYMMDD_HHMMSS": "IMG_20211103_092850",
                "Day Month DD HH-MM-SS YYYY": "Wed Nov 03 09-28-50 2021",
                "Foldername_Number": "ERROR",
            },
            {
                "YYYY-MM-DD_HH-MM-SS": "20211103_092850 (2)",
                "YYYY-MM-DD_HH-MM-SS.fff": "20211103_092850 (2)",
                "YYYYMMDD_HHMMSS": "20211103_092850 (2)",
                "IMG_YYYYMMDD_HHMMSS": "20211103_092850 (2)",
                "Day Month DD HH-MM-SS YYYY": "20211103_092850 (2)",
                "Foldername_Number": "20211103_092850 (2)",
            },
        ],
    },
    ###############################################################################################
    # gibberish3 (2)
    ###############################################################################################
    join("(2)", "gibberish3 (2)"): {
        "cases": [
            {  # MISC
                "folder": "misc",
                "name": 0,
                "jpg": True,
                "conditions": [
                    ("process_unmatched", True),
                ],
            },
            {
                "folder": None,
                "name": None,
                "jpg": True,
                "conditions": [],
            },
        ],
        "out": [
            {
                "YYYY-MM-DD_HH-MM-SS": "gibberish3 (2)",
                "YYYY-MM-DD_HH-MM-SS.fff": "gibberish3 (2)",
                "YYYYMMDD_HHMMSS": "gibberish3 (2)",
                "IMG_YYYYMMDD_HHMMSS": "gibberish3 (2)",
                "Day Month DD HH-MM-SS YYYY": "gibberish3 (2)",
                "Foldername_Number": "gibberish3 (2)",
            },
        ],
    },
    ###############################################################################################
    # IMG_20211104_092850 (2)
    ###############################################################################################
    join("(2)", "IMG_20211104_092850 (2)"): {
        "cases": [
            {  # Misc
                "folder": "misc",
                "name": 1,
                "jpg": True,
                "conditions": [
                    ("in_signature", "Metadata only"),
                    ("process_unmatched", True),
                ],
            },
            {  # None
                "folder": None,
                "name": None,
                "jpg": True,
                "conditions": [
                    ("in_signature", "Metadata only"),
                ],
            },
            {
                "folder": join("2021", "2021_[11_01-11_30]_November"),
                "name": 0,
                "jpg": True,
                "conditions": [
                    ("require_artist", False),
                ],
            },
            {
                "folder": join("2021", join("2021_[11_01-11_30]_November", "no_artist")),
                "name": 0,
                "jpg": True,
                "conditions": [],
            },
        ],
        "out": [
            {
                "YYYY-MM-DD_HH-MM-SS": "2021-11-04_09-28-50",
                "YYYY-MM-DD_HH-MM-SS.fff": "2021-11-04_09-28-50.000",
                "YYYYMMDD_HHMMSS": "20211104_092850",
                "IMG_YYYYMMDD_HHMMSS": "IMG_20211104_092850",
                "Day Month DD HH-MM-SS YYYY": "Thu Nov 04 09-28-50 2021",
                "Foldername_Number": "ERROR",
            },
            {
                "YYYY-MM-DD_HH-MM-SS": "IMG_20211104_092850 (2)",
                "YYYY-MM-DD_HH-MM-SS.fff": "IMG_20211104_092850 (2)",
                "YYYYMMDD_HHMMSS": "IMG_20211104_092850 (2)",
                "IMG_YYYYMMDD_HHMMSS": "IMG_20211104_092850 (2)",
                "Day Month DD HH-MM-SS YYYY": "IMG_20211104_092850 (2)",
                "Foldername_Number": "IMG_20211104_092850 (2)",
            },
        ],
    },
    ###############################################################################################
    # IMG_0030 (2)
    ###############################################################################################
    join("(2)", "IMG_0030 (2)"): {
        "cases": [
            {  # Misc
                "folder": "misc",
                "name": 1,
                "jpg": False,
                "conditions": [
                    ("process_unmatched", True),
                    ("process_samename", False),
                ],
            },
            {  # Misc
                "folder": "misc",
                "name": 1,
                "jpg": True,
                "conditions": [
                    ("in_signature", "Filename only"),
                    ("process_unmatched", True),
                ],
            },
            {  # None
                "folder": None,
                "name": None,
                "jpg": False,
                "conditions": [
                    ("process_unmatched", False),
                    ("process_samename", False),
                ],
            },
            {  # None
                "folder": None,
                "name": None,
                "jpg": True,
                "conditions": [
                    ("in_signature", "Filename only"),
                    ("process_unmatched", False),
                ],
            },
            {
                "folder": join("2021", "2021_[11_01-11_30]_November"),
                "name": 0,
                "jpg": True,
                "conditions": [
                    ("require_artist", False),
                ],
            },
            {
                "folder": join("2021", join("2021_[11_01-11_30]_November", "no_artist")),
                "name": 0,
                "jpg": True,
                "conditions": [],
            },
        ],
        "out": [
            {
                "YYYY-MM-DD_HH-MM-SS": "2021-11-11_09-28-50",
                "YYYY-MM-DD_HH-MM-SS.fff": "2021-11-11_09-28-50.000",
                "YYYYMMDD_HHMMSS": "20211111_092850",
                "IMG_YYYYMMDD_HHMMSS": "IMG_20211111_092850",
                "Day Month DD HH-MM-SS YYYY": "Thu Nov 11 09-28-50 2021",
                "Foldername_Number": "ERROR",
            },
            {
                "YYYY-MM-DD_HH-MM-SS": "IMG_0030 (2)",
                "YYYY-MM-DD_HH-MM-SS.fff": "IMG_0030 (2)",
                "YYYYMMDD_HHMMSS": "IMG_0030 (2)",
                "IMG_YYYYMMDD_HHMMSS": "IMG_0030 (2)",
                "Day Month DD HH-MM-SS YYYY": "IMG_0030 (2)",
                "Foldername_Number": "IMG_0030 (2)",
            },
        ],
    },
    ###############################################################################################
    # MVI_20211105_092850 (2)
    ###############################################################################################
    join("(2)", "MVI_20211105_092850 (2)"): {
        "cases": [
            {  # Misc
                "folder": "misc",
                "name": 1,
                "jpg": False,
                "conditions": [
                    ("in_signature", "Metadata only"),
                    ("process_unmatched", True),
                    ("process_samename", False),
                ],
            },
            {  # None
                "folder": None,
                "name": None,
                "jpg": False,
                "conditions": [
                    ("in_signature", "Metadata only"),
                    ("process_samename", False),
                ],
            },
            {
                "folder": join("2021", "2021_[11_01-11_30]_November"),
                "name": 0,
                "jpg": True,
                "conditions": [
                    ("require_artist", False),
                ],
            },
            {
                "folder": join("2021", join("2021_[11_01-11_30]_November", "no_artist")),
                "name": 0,
                "jpg": True,
                "conditions": [],
            },
        ],
        "out": [
            {
                "YYYY-MM-DD_HH-MM-SS": "2021-11-05_09-28-50",
                "YYYY-MM-DD_HH-MM-SS.fff": "2021-11-05_09-28-50.000",
                "YYYYMMDD_HHMMSS": "20211105_092850",
                "IMG_YYYYMMDD_HHMMSS": "IMG_20211105_092850",
                "Day Month DD HH-MM-SS YYYY": "Fri Nov 05 09-28-50 2021",
                "Foldername_Number": "ERROR",
            },
            {
                "YYYY-MM-DD_HH-MM-SS": "MVI_20211105_092850 (2)",
                "YYYY-MM-DD_HH-MM-SS.fff": "MVI_20211105_092850 (2)",
                "YYYYMMDD_HHMMSS": "MVI_20211105_092850 (2)",
                "IMG_YYYYMMDD_HHMMSS": "MVI_20211105_092850 (2)",
                "Day Month DD HH-MM-SS YYYY": "MVI_20211105_092850 (2)",
                "Foldername_Number": "MVI_20211105_092850 (2)",
            },
        ],
    },
    ###############################################################################################
    # Sun Nov 07 09-28-50 2021 (2)
    ###############################################################################################
    join("(2)", "Sun Nov 07 09-28-50 2021 (2)"): {
        "cases": [
            {  # Misc
                "folder": "misc",
                "name": 1,
                "jpg": True,
                "conditions": [
                    ("in_signature", "Metadata only"),
                    ("process_unmatched", True),
                ],
            },
            {  # None
                "folder": None,
                "name": None,
                "jpg": True,
                "conditions": [
                    ("in_signature", "Metadata only"),
                ],
            },
            {
                "folder": join("2021", "2021_[11_01-11_30]_November"),
                "name": 0,
                "jpg": True,
                "conditions": [
                    ("require_artist", False),
                ],
            },
            {
                "folder": join("2021", join("2021_[11_01-11_30]_November", "no_artist")),
                "name": 0,
                "jpg": True,
                "conditions": [],
            },
        ],
        "out": [
            {
                "YYYY-MM-DD_HH-MM-SS": "2021-11-07_09-28-50",
                "YYYY-MM-DD_HH-MM-SS.fff": "2021-11-07_09-28-50.000",
                "YYYYMMDD_HHMMSS": "20211107_092850",
                "IMG_YYYYMMDD_HHMMSS": "IMG_20211107_092850",
                "Day Month DD HH-MM-SS YYYY": "Sun Nov 07 09-28-50 2021",
                "Foldername_Number": "ERROR",
            },
            {
                "YYYY-MM-DD_HH-MM-SS": "Sun Nov 07 09-28-50 2021 (2)",
                "YYYY-MM-DD_HH-MM-SS.fff": "Sun Nov 07 09-28-50 2021 (2)",
                "YYYYMMDD_HHMMSS": "Sun Nov 07 09-28-50 2021 (2)",
                "IMG_YYYYMMDD_HHMMSS": "Sun Nov 07 09-28-50 2021 (2)",
                "Day Month DD HH-MM-SS YYYY": "Sun Nov 07 09-28-50 2021 (2)",
                "Foldername_Number": "Sun Nov 07 09-28-50 2021 (2)",
            },
        ],
    },
    ###############################################################################################
    # VID_20211106_092850 (2)
    ###############################################################################################
    join("(2)", "VID_20211106_092850 (2)"): {
        "cases": [
            {  # Misc
                "folder": "misc",
                "name": 1,
                "jpg": True,
                "conditions": [
                    ("in_signature", "Metadata only"),
                    ("process_unmatched", True),
                ],
            },
            {  # None
                "folder": None,
                "name": None,
                "jpg": True,
                "conditions": [
                    ("in_signature", "Metadata only"),
                ],
            },
            {
                "folder": join("2021", "2021_[11_01-11_30]_November"),
                "name": 0,
                "jpg": True,
                "conditions": [
                    ("require_artist", False),
                ],
            },
            {
                "folder": join("2021", join("2021_[11_01-11_30]_November", "no_artist")),
                "name": 0,
                "jpg": True,
                "conditions": [],
            },
        ],
        "out": [
            {
                "YYYY-MM-DD_HH-MM-SS": "2021-11-06_09-28-50",
                "YYYY-MM-DD_HH-MM-SS.fff": "2021-11-06_09-28-50.000",
                "YYYYMMDD_HHMMSS": "20211106_092850",
                "IMG_YYYYMMDD_HHMMSS": "IMG_20211106_092850",
                "Day Month DD HH-MM-SS YYYY": "Sat Nov 06 09-28-50 2021",
                "Foldername_Number": "ERROR",
            },
            {
                "YYYY-MM-DD_HH-MM-SS": "VID_20211106_092850 (2)",
                "YYYY-MM-DD_HH-MM-SS.fff": "VID_20211106_092850 (2)",
                "YYYYMMDD_HHMMSS": "VID_20211106_092850 (2)",
                "IMG_YYYYMMDD_HHMMSS": "VID_20211106_092850 (2)",
                "Day Month DD HH-MM-SS YYYY": "VID_20211106_092850 (2)",
                "Foldername_Number": "VID_20211106_092850 (2)",
            },
        ],
    },
}
