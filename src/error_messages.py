class WarningCodes:
    NO_WARNING = 0
    WARNING_MISSING_DATA = 1
    WARNING_DATE_OVERLAP_START = 2
    WARNING_DATE_OVERLAP_END = 3
    WARNING_DATE_OVERLAP_BOTH = 4
    WARNING_DATE_SWAP = 5
    WARNING_PERSON_EXISTS = 6

WarningArray = [
    "",
    "Some cells are not filled.",
    "Adjust start date (overlap)!",
    "Adjust end date (overlap)!",
    "Adjust time frame (overlap)!",
    "Adjust time frame (end > start)!",
    "Person already exists.",
]