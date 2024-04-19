import argparse
import pandas as pd


def parse_date(date_str: str) -> pd.Timestamp:
    return pd.Timestamp(date_str, tz="UTC").normalize()


def today() -> pd.Timestamp:
    return parse_date(pd.Timestamp.today())


def tomorrow() -> pd.Timestamp:
    return parse_date(pd.Timestamp.today() + pd.Timedelta(days=1))


def yesterday() -> pd.Timestamp:
    return parse_date(pd.Timestamp.today() - pd.Timedelta(days=1))


def check_start(check_date: str = "2024-04-01") -> pd.Timestamp:
    return parse_date(check_date)


def repsol_start_date(start_date: str = "2024-03-16") -> pd.Timestamp:
    if start_date is None or start_date == "":
        start_date = "2024-03-16"
    return parse_date(start_date)


def parser_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--no-history", action="store_true", help="Do not update consumption history"
    )
    parser.add_argument("--no-prices", action="store_true", help="Do not update prices")
    parser.add_argument(
        "--no-shelly", action="store_true", help="Do not update Shelly PM data"
    )
    parser.add_argument("--losses", action="store_true", help="Update losses profiles")
    parser.add_argument("--override", action="store_true", help="Override images")
    parser.add_argument(
        "--start-date", type=str, help="Start date in YYYY-MM-DD format"
    )
    parser.add_argument("--debug", action="store_true", help="Turn on debug mode")
    return parser.parse_args()
