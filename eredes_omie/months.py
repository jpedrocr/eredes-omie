# Import the datetime module
from datetime import datetime

# Define month constants with names in English and strings in Portuguese
MONTHS = {
    1: "jan.",
    2: "fev.",
    3: "mar.",
    4: "abr.",
    5: "mai.",
    6: "jun.",
    7: "jul.",
    8: "ago.",
    9: "set.",
    10: "out.",
    11: "nov.",
    12: "dez.",
}


def last_month() -> str:
    """
    Returns the Portuguese abbreviation of the last month.

    The function gets the current month number and uses it to return the corresponding Portuguese abbreviation from the MONTHS dictionary.
    """
    # Get the current month number
    current_month = datetime.now().month

    # Calculate the last month number
    last_month = current_month - 1 if current_month > 1 else 12

    # Return the Portuguese abbreviation of the last month
    return MONTHS[last_month]
