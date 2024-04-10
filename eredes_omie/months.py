from datetime import date


def get_last_month() -> dict:
    """
    This function returns the last month as an integer.
    If the current month is January (1), it returns December (12).
    For all other months, it simply returns the previous month.
    """

    # Get the current month as an integer (1-12)
    current_month = date.today().month

    # Get the current year
    current_year = date.today().year

    # If the current month is not January, subtract 1 to get the last month.
    # If the current month is January, the last month is December.
    last_month = current_month - 1 if current_month > 1 else 12
    year = current_year if last_month != 12 else current_year - 1

    return {"month": last_month, "year": year}
