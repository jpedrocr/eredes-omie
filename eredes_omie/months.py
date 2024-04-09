from datetime import datetime


def get_last_month() -> int:
    """
    This function returns the last month as an integer.
    If the current month is January (1), it returns December (12).
    For all other months, it simply returns the previous month.
    """

    # Get the current month as an integer (1-12)
    current_month = datetime.now().month

    # If the current month is not January, subtract 1 to get the last month.
    # If the current month is January, the last month is December.
    last_month = current_month - 1 if current_month > 1 else 12

    return last_month
