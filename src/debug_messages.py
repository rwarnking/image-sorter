from enum import IntEnum


class WarningCodes(IntEnum):
    NO_WARNING = 0
    WARNING_MISSING_DATA = 1
    WARNING_DATE_OVERLAP_START = 2
    WARNING_DATE_OVERLAP_END = 3
    WARNING_DATE_OVERLAP_BOTH = 4
    WARNING_DATE_SWAP = 5
    WARNING_PERSON_EXISTS = 6
    WARNING_DATE_OUTSIDE_START = 7
    WARNING_DATE_OUTSIDE_END = 8
    WARNING_DATE_OUTSIDE_BOTH = 9


WarningArray = [
    "",
    "Some cells are not filled.",
    "Adjust start date (overlap)!",
    "Adjust end date (overlap)!",
    "Adjust time frame (overlap)!",
    "Adjust time frame (end > start)!",
    "Person already exists.",
    "Non matching startdate of subevent or participant found.",
    "Non matching enddate of subevent or participant found.",
    "Non matching timeframe of subevent or participant found.",
]


class InfoCodes(IntEnum):
    NO_INFO = 0
    ADD_SUCCESS = 1
    ADD_SUCCESS_AFTER_SHIFT = 2
    MOD_SUCCESS = 3
    DEL_SUCCESS = 4
    CLEAN_SUCCESS = 5
    CLEAN_ALL_SUCCESS = 6
    LOAD_SUCCESS = 7
    LOAD_SUCCESS_PARTIAL = 8
    SAVE_SUCCESS = 9
    ADD_ERROR = 10
    MOD_ERROR = 11
    DEL_ERROR = 12
    VAL_SUCCESS = 13
    VAL_ERROR = 14
    REORDER_SUCCESS = 15
    REORDER_SUCCESS_PARTIAL = 16


InfoArray = [
    "",
    "Item sucessfully added.",
    "Item sucessfully added after shifting to the new id.",
    "Item sucessfully modified.",
    "Item successfully deleted.",
    "All entrys of the selected table (and linked entrys) were deleted.",
    "All tables were deleted.",
    "Successfully loaded database from file.",
    "Warning: Loaded incomplete database from file.",
    "Successfully saved database to file.",
    "Item already present.",
    "Item not found - could not be modified.",
    "Item not found - could not be deleted.",
    "Item validation was sucessfull.",
    "Item validation was not sucessfull.",
    "Successfully reordered database.",
    "Warning: Reordering was only partial successfull.",
]
